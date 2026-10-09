"""Proof documents: rendering, and checking C1-C7 against the source program.

A proof document is Python source, one expression per line: first the claims,
then clause(N, Display) for every source clause the proof cites, written as
the program states it (fact(...), implies(...) or implied_by(...)), then one
step(Goal, By, Bindings, Uses) per inference. The document reader parses
simple lines directly and other syntax with ast; it never executes them.

Verification follows recorded uses; it never asks the solver to find a missing
derivation. Only pure primitives are independently recomputed.
"""
from .builtins import PRIMITIVE_KEYS, primitive
from .common import fresh_clause, text
from .program import CONTROL_KEYS, Program
from .reader import read_term, read_terms
from .terms import (
    Env, PeyeError, Struct, Var, conjunction, copy_resolved, deref, flatten_conjunction,
    fresh_term, is_callable, is_ground, is_term, key, proper_list_items, unify,
)
from .writer import Lettering, letter_name, write, write_noting_variables


def clause_display(clause):
    """A clause as the program states it."""
    if clause.forward:
        # A query or a contradiction is displayed as the statement that wrote it.
        if clause.head == 'true':
            return Struct('query', tuple(clause.body))
        if clause.head == 'false':
            return Struct('contradiction', tuple(clause.body))
        return Struct('implies', (conjunction(clause.body), clause.head))
    if clause.body:
        return Struct('implied_by', (clause.head, conjunction(clause.body)))
    return Struct('fact', (clause.head,))


def _resolves_to(term, env, target):
    """Whether term, read through env, is exactly target, variables included."""
    pending = [term, target]
    while pending:
        expected = pending.pop()
        actual = deref(pending.pop(), env)
        kind = type(actual)
        if kind is not type(expected):
            return False
        if kind is Struct:
            if actual.name != expected.name or len(actual.args) != len(expected.args):
                return False
            for i in range(len(actual.args) - 1, -1, -1):
                pending.append(actual.args[i])
                pending.append(expected.args[i])
        elif kind is Var:
            if actual.name != expected.name:
                return False
        elif actual != expected:
            return False
    return True


class _Spellings:
    """The canonical text of terms, written once per term object.

    A proof names most goals several times, as a step and as a use, and the
    checks look each up more than once; the text is the same every time.
    The memo keeps each term alive, so an id is never reused within it.
    """
    __slots__ = ('memo',)

    def __init__(self):
        self.memo = {}

    def __call__(self, term):
        entry = self.memo.get(id(term))
        if entry is None:
            entry = self.memo[id(term)] = (term, *write_noting_variables(term))
        return entry[1]

    def lettered(self, term, lettering):
        """The text of a term with its variables named by the lettering."""
        self(term)
        _, spelling, has_variables = self.memo[id(term)]
        return write(term, names=lettering) if has_variables else spelling


def _bindings_text(bindings, lettering):
    return '{' + ', '.join(f'{name!r}: {write(value, names=lettering)}' for name, value in bindings) + '}'


def render_proof(program, claims, roots, checkable=False):
    """The proof document of a run's claims and their derivations. With
    checkable, also what check_rendered() needs to check it without reading
    the document back: the document and that, as a pair."""
    spell = _Spellings()
    steps = {}
    cited = set()
    pending = list(reversed(roots))
    while pending:
        node = pending.pop()
        node_id = spell(node.goal)
        if node_id in steps:
            continue
        steps[node_id] = node
        if type(node.by) is Struct:
            cited.add(node.by.args[0])
        for child in reversed(node.children):
            pending.append(child)
    # Variables are named A, B, ... in the order the document first shows
    # them, the claims written first, as in the run's conclusions.
    lettering = Lettering()
    lines = [spell.lettered(claim, lettering) for claim in claims]
    lines.append('')
    for clause_id in sorted(cited):
        lines.append(text(Struct('clause', (clause_id, clause_display(program.clauses[clause_id - 1])))))
    lines.append('')
    for node in steps.values():
        uses = '[' + ', '.join(spell.lettered(child.goal, lettering) for child in node.children) + ']'
        lines.append(f'step({spell.lettered(node.goal, lettering)}, {text(node.by)}, '
                     f'{_bindings_text(node.bindings, lettering)}, {uses})')
    document = '\n'.join(lines) + '\n'
    if not checkable:
        return document
    # The steps as reading the document would give them: bindings as '='/2
    # pairs, uses as goals. Their variables keep the run's names, which the
    # document only spells differently, so the checks come out the same; what
    # a report shows of a term is spelled as the document spells it.
    read = {}
    for node_id, node in steps.items():
        read[node_id] = {'goal': node.goal, 'by': node.by,
                         'bindings': [Struct('=', (name, value)) for name, value in node.bindings],
                         'uses': [child.goal for child in node.children]}
    return document, (list(claims), read, spell, lambda term: spell.lettered(term, lettering))


class _Failures:
    def __init__(self, name=text):
        self.items = []
        self.name = name

    def __call__(self, condition, detail, term=None):
        record = {'condition': condition, 'detail': detail}
        if term is not None:
            record['conclusion'] = self.name(term)
        # The term itself stays out of JSON but is kept for the term report.
        self.items.append((record, term))


def check_proof(program, document, goals=None, allow_trusted=True):
    """Check a proof document against the program that produced it.

    goals names the goals the proof answers when they were asked from outside
    the program. allow_trusted=False rejects any trusted boundary.
    """
    from .dsl import load
    if not isinstance(program, Program):
        program = load(program)
    fail = _Failures()
    spell = _Spellings()
    claims, steps = _read_document(program, document, fail, spell)
    return _check(program, claims, steps, goals, allow_trusted, fail, spell, text)


def check_rendered(program, checkable, goals=None, allow_trusted=True):
    """Check a proof as render_proof(..., checkable=True) gave it: the report
    check_proof() gives for its document, without reading the document back.
    A reasoner checks its own proofs this way; their text is covered by the
    tests that what is written reads back as the same terms."""
    claims, steps, spell, name = checkable
    return _check(program, claims, steps, goals, allow_trusted, _Failures(name), spell, name)


def _check(program, claims, steps, goals, allow_trusted, fail, spell, name):
    for claim in claims:
        if not all(spell(part) in steps for part in flatten_conjunction(claim)):
            fail('C4', f'unjustified claim {text(claim)}', claim)
    tally = _check_steps(program, steps, allow_trusted, fail, spell, name)
    confronted = _check_boundaries(program, steps, tally['boundaries'], fail)
    _check_relevance(program, claims, steps, goals or [], fail, spell)
    _check_well_founded(steps, fail, spell)

    uses = sum(len(step['uses']) for step in steps.values())

    def failed(condition):
        return sum(1 for record, _ in fail.items if record['condition'] == condition)
    conditions = [
        {'id': 'C1', 'name': 'resolution', 'covered': tally['verified'], 'failed': failed('C1')},
        {'id': 'C2', 'name': 'well_founded', 'covered': len(steps), 'failed': failed('C2')},
        {'id': 'C3', 'name': 'justification', 'covered': len(steps), 'failed': failed('C3')},
        {'id': 'C4', 'name': 'coverage', 'covered': len(claims) + uses, 'failed': failed('C4')},
        {'id': 'C5', 'name': 're_decision', 'covered': tally['redecided'] + tally['composed'],
         'failed': failed('C5')},
        {'id': 'C6', 'name': 'boundary_consistency', 'covered': confronted, 'failed': failed('C6')},
        {'id': 'C7', 'name': 'relevance', 'covered': len(claims) + len(steps), 'failed': failed('C7')},
    ]
    return {
        'valid': not fail.items, 'steps': len(steps), 'claims': len(claims),
        'verified': tally['verified'], 'redecided': tally['redecided'], 'composed': tally['composed'],
        'uses': uses, 'trusted': [record for record, _ in tally['trusted']],
        'failures': [record for record, _ in fail.items], 'conditions': conditions,
        # Terms behind the records, for the term report.
        '_failure_terms': [term for _, term in fail.items],
        '_trusted_terms': [term for _, term in tally['trusted']],
    }


def strict(report):
    """The verdict allow_trusted=False would give, from a report without it.

    Without failures, a strict check differs only in failing C5 once for
    each trusted boundary, in step order, so it needs no second reading of
    the document. A report with failures returns None: check again instead.
    """
    if report['failures']:
        return None
    failures = [{'condition': 'C5', 'detail': f"trusted boundary forbidden: {record['kind']}",
                 'conclusion': record['conclusion']} for record in report['trusted']]
    conditions = [dict(condition, failed=len(failures)) if condition['id'] == 'C5' else dict(condition)
                  for condition in report['conditions']]
    return dict(report, valid=not failures, failures=failures, conditions=conditions,
                _failure_terms=list(report['_trusted_terms']))


def _read_document(program, document, fail, spell):
    """C3: split a document into claims and steps keyed by the goal's text.
    clause/2 records are compared with the source."""
    claims = []
    steps = {}
    try:
        for term, _ in read_terms(document):
            if is_term(term, 'clause', 2):
                # These display records are not authority: the source program is.
                clause_id = term.args[0]
                clause = (program.clauses[clause_id - 1]
                          if type(clause_id) is int and 1 <= clause_id <= len(program.clauses) else None)
                if clause is None or text(term.args[1]) != text(clause_display(clause)):
                    fail('C1', 'clause display differs from source', term)
                continue
            if not is_term(term, 'step', 4):
                claims.append(term)
                continue
            goal, by, binding_list, use_list = term.args
            bindings = proper_list_items(binding_list, Env())
            uses = proper_list_items(use_list, Env())
            if bindings is None or uses is None:
                fail('C3', 'step bindings must be a dictionary and uses a list', goal)
                continue
            goal_id = spell(goal)
            if goal_id in steps:
                fail('C3', f'duplicate justification for {goal_id}', goal)
                continue
            steps[goal_id] = {'goal': goal, 'by': by, 'bindings': bindings, 'uses': uses}
    except PeyeError as error:
        fail('C3', str(error))
    return claims, steps


def _check_steps(program, steps, allow_trusted, fail, spell, name):
    """C4, C1, C3 and C5 for each step: every use is justified, and the step is
    an instance of the clause it cites, a recomputed primitive, a control
    composed of its uses, or a trusted boundary the later checks confront."""
    tally = {'verified': 0, 'redecided': 0, 'composed': 0, 'boundaries': [], 'trusted': []}

    def covered(goal):
        if is_term(goal, ',', 2):
            return all(covered(part) for part in flatten_conjunction(goal))
        if spell(goal) in steps:
            return True
        # Source facts are available as leaves, including universal facts.
        if not is_callable(goal):
            return False
        for clause in program.groups.get(key(goal), ()):
            if clause.body:
                continue
            head = fresh_term(clause.head, 'given')
            env = Env()
            if unify(head, goal, env) and _resolves_to(head, env, goal):
                return True
        return False

    for step in steps.values():
        goal, by, bindings, uses = step['goal'], step['by'], step['bindings'], step['uses']
        for use in uses:
            if not covered(use):
                fail('C4', f'unjustified use {text(use)}', goal)
        if is_term(by, 'clause', 1):
            if _check_resolution(program, step, fail):
                tally['verified'] += 1
        elif by == BUILTIN_BY:
            if bindings or uses or not is_callable(goal) or key(goal) not in PRIMITIVE_KEYS:
                fail('C3', 'invalid builtin justification', goal)
                continue
            agrees = False
            try:
                for env in primitive(goal, Env()):
                    if _resolves_to(goal, env, goal):
                        agrees = True
                        break
            except PeyeError:
                pass  # A primitive that cannot be recomputed does not pass C5.
            if not agrees:
                fail('C5', f'primitive disagrees: {text(goal)}', goal)
            else:
                tally['redecided'] += 1
        elif by == CONTROL_BY:
            candidates = []
            if is_term(goal, 'call', 1) or is_term(goal, 'once', 1):
                candidates = [goal.args[0]]
            elif is_term(goal, ';', 2):
                candidates = list(goal.args)

            def composes(candidate):
                parts = flatten_conjunction(candidate)
                return len(parts) == len(uses) and all(spell(part) == spell(use) for part, use in zip(parts, uses))
            if bindings or not any(composes(candidate) for candidate in candidates):
                fail('C5', f'control step does not follow from its uses: {text(goal)}', goal)
            else:
                tally['composed'] += 1
        elif (by == 'absent' and is_term(goal, '~', 1)) or (by == 'collected' and is_term(goal, 'findall', 3)):
            if bindings or uses:
                fail('C3', 'trusted boundaries cannot have bindings or uses', goal)
            tally['boundaries'].append(goal)
            tally['trusted'].append(({'kind': by, 'conclusion': name(goal)}, goal))
            if not allow_trusted:
                fail('C5', f'trusted boundary forbidden: {by}', goal)
        else:
            fail('C3', f'unknown justification {text(by)}', goal)
    return tally


BUILTIN_BY = 'builtin'
CONTROL_BY = 'control'


def _check_resolution(program, step, fail):
    """C1: a clause step names a source clause, its bindings name
    distinct variables of that clause, and under them one of the clause's
    heads is the step's goal and its body is exactly the step's uses."""
    goal, by, bindings, uses = step['goal'], step['by'], step['bindings'], step['uses']
    clause_id = by.args[0]
    clause = (program.clauses[clause_id - 1]
              if type(clause_id) is int and 1 <= clause_id <= len(program.clauses) else None)
    if clause is None:
        fail('C1', f'unknown clause {text(by)}', goal)
        return False
    head, body, names = fresh_clause(clause, f'check{clause_id}')
    env = Env()
    seen = set()
    valid = True
    for binding in bindings:
        if (not is_term(binding, '=', 2) or type(binding.args[0]) is not str or
                binding.args[0] not in names or binding.args[0] in seen):
            valid = False
            break
        seen.add(binding.args[0])
        if not unify(names[binding.args[0]], binding.args[1], env):
            valid = False
    heads = flatten_conjunction(head) if clause.forward else [head]
    resolution = False
    for candidate in heads:
        mark = env.mark()
        matches = unify(candidate, goal, env) and len(body) == len(uses)
        i = 0
        while matches and i < len(body):
            if not unify(body[i], uses[i], env):
                matches = False
            i += 1
        if (matches and _resolves_to(candidate, env, goal) and
                all(_resolves_to(item, env, uses[i]) for i, item in enumerate(body))):
            resolution = True
        env.undo(mark)
    if not valid or not resolution:
        fail('C1', f'not an instance of source clause {clause_id}: {text(goal)}', goal)
        return False
    return True


def _check_boundaries(program, steps, boundaries, fail):
    """C6: a trusted boundary cannot be proved, but evidence at hand can refute
    it. An absence fails when a source fact, a step of this certificate or a
    recomputed primitive is a solution; a collection fails when such a
    solution is missing from its list. Returns how many boundaries the
    evidence could speak for."""
    step_goals = {}
    for step in steps.values():
        if is_callable(step['goal']):
            step_goals.setdefault(key(step['goal']), []).append(step['goal'])
    serial = [0]
    confronted = 0

    def next_serial():
        serial[0] += 1
        return serial[0]

    def evidence(goal):
        """Each solution of a simple goal that the evidence shows, or None
        when the evidence cannot speak for the goal."""
        if not is_callable(goal):
            return None
        goal_key = key(goal)
        if goal_key in PRIMITIVE_KEYS:
            if not is_ground(goal):
                return None
            try:
                for _ in primitive(goal, Env()):
                    return [goal]
            except PeyeError:
                return None
            return []
        if goal_key in CONTROL_KEYS:
            return None
        facts = [fresh_term(clause.head, f'evidence{next_serial()}')
                 for clause in program.groups.get(goal_key, ()) if not clause.body and not clause.forward]
        return facts + [fresh_term(item, f'evidence{next_serial()}') for item in step_goals.get(goal_key, ())]

    for boundary in boundaries:
        if is_term(boundary, '~', 1):
            parts = flatten_conjunction(boundary.args[0])
            # Without a join, only a single goal or a ground conjunction is decided.
            if len(parts) > 1 and not is_ground(boundary.args[0]):
                continue
            shown = [evidence(part) for part in parts]
            if any(items is None for items in shown):
                continue
            confronted += 1
            solved = all(any(unify(fresh_term(part, f'absent{next_serial()}'), item, Env()) for item in shown[i])
                         for i, part in enumerate(parts))
            if solved:
                fail('C6', f'absence contradicted by evidence: {text(boundary)}', boundary)
        else:
            items = proper_list_items(boundary.args[2], Env())
            if items is None:
                fail('C6', f'collected result is not a proper list: {text(boundary)}', boundary)
                continue
            parts = flatten_conjunction(boundary.args[1])
            shown = evidence(parts[0]) if len(parts) == 1 else None
            if shown is None:
                continue
            confronted += 1
            for item in shown:
                names = {}
                number = next_serial()
                pattern = fresh_term(boundary.args[0], f'collect{number}', names)
                goal = fresh_term(parts[0], f'collect{number}', names)
                env = Env()
                if not unify(goal, item, env):
                    continue
                answer = copy_resolved(pattern, env)
                listed = any(unify(answer, fresh_term(element, f'listed{next_serial()}'), Env())
                             for element in items)
                if not listed:
                    fail('C6', f'collection misses {text(answer)}: {text(boundary)}', boundary)
                    break
    return confronted


def _check_relevance(program, claims, steps, goals, fail, spell):
    """C7: the certificate answers the question that was asked and carries
    nothing beside it. A claim is an instance of a goal asked from outside, of
    a query() goal or, for printed conclusions, of a forward head."""
    serial = [0]

    def instance_of(claim, question):
        serial[0] += 1
        env = Env()
        pattern = fresh_term(question, f'asked{serial[0]}')
        return unify(pattern, claim, env) and _resolves_to(pattern, env, claim)

    asked = [read_term(goal) if isinstance(goal, str) else goal for goal in goals]
    halted = any(type(claim) is str and claim == 'false' for claim in claims)
    questions = []
    if asked and not halted:
        questions.extend(asked)
    else:
        for clause in program.forward:
            heads = flatten_conjunction(clause.head)
            if any(type(head) is str and head == 'true' for head in heads):
                if not halted and clause.body:
                    questions.append(conjunction(clause.body))
            for head in heads:
                if not (type(head) is str and head == 'true'):
                    questions.append(head)
    for claim in claims:
        if not any(instance_of(claim, question) for question in questions):
            fail('C7', f'claim answers no goal: {text(claim)}', claim)
    reached = set()
    reach = [spell(part) for claim in claims for part in flatten_conjunction(claim)]
    while reach:
        step_id = reach.pop()
        if step_id in reached or step_id not in steps:
            continue
        reached.add(step_id)
        for use in steps[step_id]['uses']:
            for part in flatten_conjunction(use):
                reach.append(spell(part))
    for step_id, step in steps.items():
        if step_id not in reached:
            fail('C7', f'step serves no claim: {step_id}', step['goal'])


def _check_well_founded(steps, fail, spell):
    """C2: no step depends on itself, walked iteratively."""
    visiting = set()
    visited = set()

    def supports(step_id):
        used = []
        step = steps.get(step_id)
        for use in (step['uses'] if step else ()):
            for part in flatten_conjunction(use):
                part_id = spell(part)
                if part_id in steps:
                    used.append(part_id)
        return used

    for start in steps:
        if start in visited:
            continue
        visiting.add(start)
        stack = [[start, supports(start), 0]]
        while stack:
            top = stack[-1]
            if top[2] >= len(top[1]):
                visiting.discard(top[0])
                visited.add(top[0])
                stack.pop()
                continue
            following = top[1][top[2]]
            top[2] += 1
            if following in visiting:
                fail('C2', f'cyclic derivation at {following}', steps[following]['goal'])
                continue
            if following in visited:
                continue
            visiting.add(following)
            stack.append([following, supports(following), 0])


def _verdict(report):
    if not report['valid']:
        return Struct('failed', (len(report['failures']),))
    return 'checked_with_obligations' if report['trusted'] else 'checked'


def _lettered(term):
    """Rename a report fact's variables A, B, C, ... in order of appearance."""
    names = {}

    def visit(t):
        if type(t) is Var:
            if t.name not in names:
                names[t.name] = Var(letter_name(len(names)))
            return names[t.name]
        if type(t) is Struct:
            return Struct(t.name, tuple(visit(arg) for arg in t.args))
        return t
    return visit(term)


def check_report(report):
    """The report as Python source, one fact per line, every condition included."""
    facts = []
    for condition in report['conditions']:
        outcome = Struct('failed', (condition['failed'],)) if condition['failed'] else 'ok'
        facts.append(Struct('condition', (condition['id'], condition['name'], outcome, condition['covered'])))
    for record, term in zip(report['failures'], report['_failure_terms']):
        subject = term if term is not None else record.get('conclusion', 'proof_document')
        facts.append(Struct('failure', (record['condition'], subject, record['detail'])))
    for record, term in zip(report['trusted'], report['_trusted_terms']):
        facts.append(Struct('obligation', (record['kind'], record.get('reason', 'theory_scoped'),
                                           term if term is not None else record['conclusion'])))
    for name, count in [('steps', report['steps']), ('verified', report['verified']),
                        ('recomputed', report['redecided']), ('composed', report['composed']),
                        ('trusted', len(report['trusted'])), ('claims', report['claims'])]:
        facts.append(Struct(name, (count,)))
    facts.append(Struct('verdict', (_verdict(report),)))
    return ''.join(f'{text(_lettered(fact))}\n' for fact in facts)


def verdict_text(report):
    return f"{text(Struct('verdict', (_verdict(report),)))}\n"


def public_report(report):
    """The report without its term-valued internals, ready for JSON."""
    return {name: value for name, value in report.items() if not name.startswith('_')}
