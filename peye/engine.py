"""Backward resolution, forward fixpoints and proof recording."""
import json

from .builtins import PRIMITIVE_KEYS, primitive
from .common import fresh_clause, text, variant
from .program import CONTROL_KEYS, Program
from .terms import (
    Env, PeyeError, Struct, Var, conjunction, copy_resolved, deref, flatten_conjunction,
    fresh_term, is_callable, is_ground, is_term, key, list_from_items, unify, variables,
)

BUILTIN = 'builtin'
CONTROL = 'control'
ABSENT = 'absent'
COLLECTED = 'collected'


class Node:
    """One proof step: a goal, how it was justified, and the steps it used."""
    __slots__ = ('goal', 'by', 'bindings', 'children', 'collected_uses')

    def __init__(self, goal, by, bindings=(), children=(), collected_uses=None):
        self.goal = goal
        self.by = by
        self.bindings = bindings
        self.children = children
        # A collection has no children in a proof, so its node keeps the
        # clauses its answers used.
        self.collected_uses = collected_uses


class Pending:
    """The step a frame's body will justify once it is finished."""
    __slots__ = ('goal', 'by', 'bindings', 'cut')

    def __init__(self, goal, by, bindings, cut):
        self.goal = goal
        self.by = by
        self.bindings = bindings
        self.cut = cut


class Frame:
    """One body being worked through. Frames never change once made."""
    __slots__ = ('goals', 'index', 'nodes', 'parent', 'pending', 'depth')

    def __init__(self, goals, index, nodes, parent, pending, depth):
        self.goals = goals
        self.index = index
        self.nodes = nodes
        self.parent = parent
        self.pending = pending
        self.depth = depth


class Point:
    """A choice point: the frame it was made in and its untried alternatives."""
    __slots__ = ('kind', 'frame', 'mark', 'goal', 'alternatives', 'facts', 'clauses',
                 'position', 'iterator')

    def __init__(self, kind, frame, mark, goal, alternatives=(), facts=(), clauses=(), iterator=None):
        self.kind = kind
        self.frame = frame
        self.mark = mark
        self.goal = goal
        self.alternatives = alternatives
        self.facts = facts
        self.clauses = clauses
        self.position = 0
        self.iterator = iterator

    def count(self):
        if self.kind == 'branch':
            return len(self.alternatives)
        return len(self.facts) + len(self.clauses)


NO_NODES = ()
QUIET = Pending(None, None, NO_NODES, None)
SPLICE = 'splice'


def _resolve_one(node, env):
    return Node(copy_resolved(node.goal, env), node.by,
                [(name, copy_resolved(value, env)) for name, value in node.bindings],
                [None] * len(node.children), node.collected_uses)


def resolve_node(node, env):
    """Resolve a proof forest with an explicit stack: a derivation chain is as
    deep as the search that produced it."""
    root = _resolve_one(node, env)
    pending = [(node, root)]
    while pending:
        source, target = pending.pop()
        for index, child in enumerate(source.children):
            copy = _resolve_one(child, env)
            target.children[index] = copy
            if child.children:
                pending.append((child, copy))
    return root


def _primitive_node(goal, by=BUILTIN):
    return Node(goal, by)


def clauses_used(nodes, used=None):
    """The source clauses a set of proof nodes rests on."""
    if used is None:
        used = set()
    pending = list(nodes)
    while pending:
        node = pending.pop()
        if type(node.by) is Struct:
            used.add(node.by.args[0])
        if node.collected_uses:
            used.update(node.collected_uses)
        pending.extend(node.children)
    return used


def clauses_behind_boundaries(program, roots):
    """The source clauses that searches behind a trusted boundary could consult.

    A negation or a collection records no derivation in a proof, so follow its
    goal through the program instead: every clause whose head could answer a
    goal it reaches, and the goals in that clause's body, transitively.
    """
    by_key = {}
    for clause in program.clauses:
        for head in clause.heads or [clause.head]:
            if is_callable(head):
                by_key.setdefault(key(head), []).append(clause)
    pending = []

    def visit(goal):
        if not is_callable(goal):
            return
        if is_term(goal, ',', 2) or is_term(goal, ';', 2):
            visit(goal.args[0])
            visit(goal.args[1])
        elif is_term(goal, '~', 1) or is_term(goal, 'call', 1) or is_term(goal, 'once', 1):
            visit(goal.args[0])
        elif is_term(goal, 'findall', 3):
            visit(goal.args[1])
        elif key(goal) not in PRIMITIVE_KEYS:
            pending.append(key(goal))

    nodes = list(roots)
    while nodes:
        node = nodes.pop()
        if node.by == ABSENT or node.by == COLLECTED:
            visit(node.goal)
        nodes.extend(node.children)
    seen = set()
    reached = set()
    while pending:
        goal_key = pending.pop()
        if goal_key in seen:
            continue
        seen.add(goal_key)
        for clause in by_key.get(goal_key, ()):
            reached.add(clause.id)
            for goal in clause.body:
                visit(goal)
    return reached


class Solver:
    def __init__(self, program, options):
        self.program = program
        self.options = options
        self.recording = bool(options.get('proof'))
        self.serial = 0
        self.facts = {}
        self.fact_keys = set(program.ground_fact_keys)
        self.derived = []
        self.reported = {}
        self.stats = {'inferences': 0, 'rounds': 0, 'derived': 0}
        self.halt_code = None
        self.max_depth = options.get('max_depth') or 1000000
        self.max_inferences = options.get('max_inferences') or 1000000

    # Proof nodes are recorded only when a proof is asked for. Without one,
    # frames share an empty tuple and a finished body has nothing to hand back.
    def advance(self, frame, node):
        return Frame(frame.goals, frame.index + 1,
                     frame.nodes + (node,) if self.recording else NO_NODES,
                     frame.parent, frame.pending, frame.depth)

    def child_frame(self, parent, goals, pending, depth):
        return Frame(goals, 0, () if self.recording else NO_NODES, parent, pending, depth)

    def control_pending(self, goal, cut):
        if self.recording or cut is not None:
            return Pending(goal, CONTROL, NO_NODES, cut)
        return QUIET

    def close_frame(self, frame):
        """A finished body hands its nodes to the frame that started it: a
        conjunction splices them in place, anything else wraps them as one
        step's children."""
        parent = frame.parent
        if not self.recording:
            return Frame(parent.goals, parent.index + 1, NO_NODES, parent.parent, parent.pending, parent.depth)
        if frame.pending is SPLICE:
            nodes = parent.nodes + frame.nodes
        else:
            pending = frame.pending
            nodes = parent.nodes + (Node(pending.goal, pending.by, pending.bindings, list(frame.nodes)),)
        return Frame(parent.goals, parent.index + 1, nodes, parent.parent, parent.pending, parent.depth)

    def solve(self, goals, env=None, depth=0):
        """Backward search as an explicit machine rather than nested generators.

        A frame is one body being worked through; frames are immutable, so a
        choice point only has to remember the frame it was made in and
        backtracking is a pointer assignment rather than an undo log. One
        substitution is threaded through the whole search and restored by the
        trail, so an answer's bindings are only valid until the next one is
        requested: every consumer copies what it needs first.
        """
        if env is None:
            env = Env()
        frame = Frame(goals, 0, () if self.recording else NO_NODES, None, None, depth)
        choices = []
        entry = env.mark()
        failed = False
        stats = self.stats
        try:
            while True:
                if failed:
                    if not choices:
                        return
                    point = choices[-1]
                    env.undo(point.mark)
                    resumed = self.retry(point, env)
                    if resumed is None:
                        choices.pop()
                        continue
                    frame = resumed
                    failed = False
                    continue
                if frame.index >= len(frame.goals):
                    if frame.parent is None:
                        yield env, frame.nodes
                        failed = True
                        continue
                    # once/1 commits to its first solution by discarding the
                    # choice points its own goal created.
                    cut = frame.pending.cut if frame.pending is not SPLICE else None
                    if cut is not None and len(choices) > cut:
                        del choices[cut:]
                    frame = self.close_frame(frame)
                    continue
                if frame.depth > self.max_depth:
                    raise PeyeError('backward reasoning exceeded max_depth')
                stats['inferences'] += 1
                if stats['inferences'] > self.max_inferences:
                    raise PeyeError('reasoning exceeded max_inferences')
                goal = deref(frame.goals[frame.index], env)
                if not is_callable(goal):
                    raise PeyeError(f'expected a callable goal, got {text(goal)}')
                step = self.step(goal, frame, env, choices)
                if step is None:
                    failed = True
                    continue
                frame = step
        finally:
            env.undo(entry)

    def step(self, goal, frame, env, choices):
        """Start one goal: the frame to continue from, or None when it has no solution."""
        recording = self.recording
        goal_key = key(goal)
        if goal_key == (',', 2):
            return self.child_frame(frame, flatten_conjunction(goal), SPLICE, frame.depth)
        if goal_key == ('~', 1):
            # Negation is a test, not a way to bind its variables.
            if not is_ground(goal.args[0], env):
                raise PeyeError(f'negation requires a ground goal: {text(goal, env)}')
            mark = env.mark()
            iterator = self.solve([goal.args[0]], env, frame.depth + 1)
            try:
                absent = next(iterator, None) is None
            finally:
                iterator.close()
                env.undo(mark)
            if not absent:
                return None
            return self.advance(frame, _primitive_node(goal, ABSENT) if recording else None)
        if goal_key == ('findall', 3):
            items = []
            uses = set() if recording else None
            mark = env.mark()
            for answer_env, nodes in self.solve([goal.args[1]], env, frame.depth + 1):
                self.serial += 1
                items.append(fresh_term(copy_resolved(goal.args[0], answer_env), f'collection{self.serial}'))
                if recording:
                    clauses_used(nodes, uses)
            env.undo(mark)
            if not unify(goal.args[2], list_from_items(items), env):
                env.undo(mark)
                return None
            if not recording:
                return self.advance(frame, None)
            return self.advance(frame, Node(goal, COLLECTED, collected_uses=uses))
        if goal_key == (';', 2):
            point = Point('branch', frame, env.mark(), goal, alternatives=goal.args)
        elif goal_key == ('call', 1) or goal_key == ('once', 1):
            cut = len(choices) if goal_key[0] == 'once' else None
            return self.child_frame(frame, [goal.args[0]], self.control_pending(goal, cut), frame.depth + 1)
        elif goal_key in PRIMITIVE_KEYS:
            point = Point('primitive', frame, env.mark(), goal, iterator=primitive(goal, env))
        else:
            # Derived facts are tried before source clauses. Neither list
            # changes while a search runs.
            point = Point('resolve', frame, env.mark(), goal,
                          facts=self.facts.get(goal_key, NO_NODES),
                          clauses=self.program.candidates(goal, env, goal_key))
        step = self.retry(point, env)
        if step is None:
            return None
        if point.kind == 'primitive' or point.position < point.count():
            choices.append(point)
        return step

    def retry(self, point, env):
        """Take the next untried alternative of a choice point, or None. The
        caller has already undone the bindings of the previous one."""
        recording = self.recording
        if point.kind == 'primitive':
            if next(point.iterator, None) is None:
                return None
            return self.advance(point.frame, _primitive_node(point.goal) if recording else None)
        count = point.count()
        while point.position < count:
            position = point.position
            point.position += 1
            if point.kind == 'branch':
                return self.child_frame(point.frame, [point.alternatives[position]],
                                        self.control_pending(point.goal, None), point.frame.depth + 1)
            facts = point.facts
            if position < len(facts):
                fact = facts[position]
                if unify(point.goal, fact.goal, env):
                    return self.advance(point.frame, fact)
                env.undo(point.mark)
                continue
            clause = point.clauses[position - len(facts)]
            self.serial += 1
            head, body, names = fresh_clause(clause, self.serial)
            if not unify(point.goal, head, env):
                env.undo(point.mark)
                continue
            if recording:
                pending = Pending(point.goal, Struct('rule' if body else 'fact', (clause.id,)),
                                  list(names.items()), None)
            else:
                pending = QUIET
            return self.child_frame(point.frame, body, pending, point.frame.depth + 1)
        return None

    def forward(self, reporting=True):
        """Run the forward rules to a fixpoint, one stratum after another.

        A rule whose heads are all 'true' only publishes output; when the
        caller asks its own question that output is discarded, so the rule is
        skipped.
        """
        layers = {}
        for clause in self.program.forward:
            layers.setdefault(self.program.strata.get(clause.id, 0), []).append(clause)
        max_iterations = self.options.get('max_iterations') or 1000
        for _, rules in sorted(layers.items()):
            changed = True
            rounds = 0
            while changed:
                rounds += 1
                if rounds > max_iterations:
                    raise PeyeError('forward reasoning exceeded max_iterations')
                self.stats['rounds'] += 1
                changed = False
                for clause in rules:
                    if not reporting and all(item == 'true' for item in clause.heads):
                        continue
                    self.serial += 1
                    head, body, names = fresh_clause(clause, self.serial)
                    # Bindings last only until the next answer is requested,
                    # and adding facts mid-scan would extend a live search, so
                    # copy each activation out first and conclude afterwards.
                    activations = []
                    for answer_env, nodes in self.solve(body):
                        mark = answer_env.mark()
                        # Residual head variables become sk_0, sk_1, ... within
                        # each conclusion, with sharing preserved.
                        unresolved = variables(copy_resolved(head, answer_env))
                        for skolem, value in enumerate(unresolved.values()):
                            unify(value, f'sk_{skolem}', answer_env)
                        conclusions = [copy_resolved(item, answer_env) for item in flatten_conjunction(head)]
                        if self.recording:
                            children = [resolve_node(node, answer_env) for node in nodes]
                            bindings = [(name, copy_resolved(value, answer_env)) for name, value in names.items()]
                        else:
                            children = bindings = NO_NODES
                        claim = (copy_resolved(conjunction(body), answer_env)
                                 if any(item == 'true' for item in conclusions) else None)
                        activations.append((conclusions, children, bindings, claim))
                        answer_env.undo(mark)
                    for conclusions, children, bindings, claim in activations:
                        for conclusion in conclusions:
                            if type(conclusion) is str and conclusion == 'true':
                                claim_id = text(claim)
                                if claim_id not in self.reported:
                                    self.reported[claim_id] = (claim, children, clause.id)
                                continue
                            node = Node(conclusion, Struct('rule', (clause.id,)), bindings, children)
                            if type(conclusion) is str and conclusion == 'false':
                                self.derived.append(node)
                                self.halt_code = 65
                                return
                            conclusion_id = text(conclusion)
                            if conclusion_id in self.fact_keys:
                                continue
                            self.fact_keys.add(conclusion_id)
                            self.facts.setdefault(key(conclusion), []).append(node)
                            self.derived.append(node)
                            self.stats['derived'] += 1
                            changed = True


class Result:
    """What a run concluded.

    answers are the conclusions as printable text and bindings one dict per
    answer of the goal's variables; with a proof, proof is the document and
    proof_report its check, clauses_used the ids of the source clauses the
    conclusions rest on, and clauses_behind_boundaries the ids of clauses only
    searches behind a trusted boundary could consult.
    """

    def __init__(self, **fields):
        self.__dict__.update(fields)

    def __repr__(self):
        return f'Result(answers={self.answers!r}, halt_code={self.halt_code!r})'


def run(program, goal=None, goals=None, proof=False, max_depth=None, max_iterations=None,
        max_inferences=None):
    """Reason over a program: forward to a fixpoint, then answer any goals.

    program is a Program, or a source accepted by load(). goal or goals are
    terms or goal text; without one, the program's own query() rules answer,
    and without those every newly derived fact is a conclusion.
    """
    from .dsl import load
    if not isinstance(program, Program):
        program = load(program)
    options = {'proof': proof, 'max_depth': max_depth, 'max_iterations': max_iterations,
               'max_inferences': max_inferences}
    if goals is None:
        goals = [] if goal is None else [goal]
    try:
        return _reason(program, list(goals), options)
    except RecursionError:
        # Search itself is iterative, but a few term walks are recursive, so
        # a term nested deeply enough can exhaust the host stack.
        raise PeyeError('reasoning exhausted the host stack on a deeply nested term') from None


def _goal_term(goal):
    if isinstance(goal, str):
        from .reader import read_term
        return read_term(goal)
    from .terms import _term
    return _term(goal)


def _reason(program, goals, options):
    from .proof import check_proof, render_proof
    solver = Solver(program, options)
    goals = [_goal_term(goal) for goal in goals]
    solver.forward(not goals)
    roots = []
    bindings = []
    claims = []
    seen = set()
    if goals and solver.halt_code is None:
        for goal in goals:
            for answer_env, nodes in solver.solve([goal]):
                conclusion = copy_resolved(goal, answer_env)
                conclusion_id = variant(conclusion)
                if conclusion_id in seen:
                    continue
                seen.add(conclusion_id)
                if options['proof']:
                    roots.extend(resolve_node(node, answer_env) for node in nodes)
                claims.append(conclusion)
                bindings.append({name: text(value, answer_env) for name, value in variables(goal).items()
                                 if not name.startswith('_')})
    elif solver.halt_code is None and solver.reported:
        for claim, children, _ in solver.reported.values():
            claims.append(claim)
            roots.extend(children)
    else:
        for node in solver.derived:
            roots.append(node)
            claims.append(node.goal)
    answers = [text(claim) for claim in claims]
    document = render_proof(program, claims, roots) if options['proof'] else None
    # A rule that reports a claim is used by it, though a proof records only
    # the claim's support.
    used = clauses_used(roots) if options['proof'] else None
    if used is not None and solver.halt_code is None and not goals:
        for _, _, clause_id in solver.reported.values():
            used.add(clause_id)
    report = None
    if document is not None and claims:
        # The generated proof is checked before it is returned.
        report = check_proof(program, document, goals=goals)
        if not report['valid']:
            raise PeyeError(f"cannot certify this result: {report['failures'][0]['detail']}")
    return Result(
        answers=answers,
        bindings=bindings,
        inferred=[text(node.goal) for node in solver.derived],
        clauses_used=sorted(used) if used is not None else None,
        clauses_behind_boundaries=(sorted(set(clauses_behind_boundaries(program, roots)) - used)
                                   if used is not None else None),
        stdout=document if document is not None else ''.join(f'{answer}\n' for answer in answers),
        proof=document,
        proof_report=report,
        stats=solver.stats,
        halt_code=solver.halt_code,
    )


def unused_clauses(program, **options):
    """The clauses that make no difference to the conclusions, as text.

    One unused(line(N), Clause) per clause no conclusion's proof rests on,
    unless leaving it out changes what the program concludes: a clause only a
    negation or a collection consults may still decide a conclusion.
    """
    from .dsl import load
    from .proof import clause_display
    from .writer import write
    if not isinstance(program, Program):
        program = load(program)
    options.pop('proof', None)
    result = run(program, proof=True, **options)
    used = set(result.clauses_used)
    behind = set(result.clauses_behind_boundaries)

    def conclusions(outcome):
        return json.dumps([sorted(outcome.answers), outcome.halt_code])
    baseline = conclusions(result)

    def matters(clause):
        try:
            return conclusions(run(Program(program.sources, without=clause.id), **options)) != baseline
        except PeyeError:
            return True
    lines = []
    for clause in program.clauses:
        if clause.id in used or (clause.id in behind and matters(clause)):
            continue
        written = Struct('unused', (Struct('line', (clause.line,)), clause_display(clause)))
        lines.append(f'{write(written)}\n')
    return ''.join(lines)
