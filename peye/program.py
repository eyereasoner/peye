"""A program: its clauses, validated, indexed and stratified."""
from .builtins import PRIMITIVE_KEYS
from .terms import (
    Env, PeyeError, Struct, Var, deref, flatten_conjunction, fresh_term, is_callable,
    is_ground, is_term, key, unify,
)

CONTROL_KEYS = frozenset({(',', 2), (';', 2), ('~', 1), ('call', 1), ('once', 1), ('findall', 3)})
RESERVED_KEYS = frozenset({('step', 4), ('clause', 2)})


# The statements that state a forward rule, and how an error names them.
FORWARD_KINDS = {'forward': 'a forward rule', 'query': 'query()', 'contradiction': 'contradiction()'}


class Clause:
    __slots__ = ('id', 'head', 'heads', 'body', 'forward', 'line', 'renaming')

    def __init__(self, id, head, heads, body, forward, line):
        self.id = id
        self.head = head
        # Only a forward rule can have several heads, so only it stores them.
        self.heads = heads
        self.body = body
        self.forward = forward
        self.line = line
        self.renaming = None  # how to rename it apart, worked out when first needed


class Source:
    """One clause as a program states it, before validation.

    kind is 'fact', 'backward', 'forward', 'query' or 'contradiction'; body is
    a list of goals.
    """
    __slots__ = ('kind', 'head', 'body', 'line', 'file')

    def __init__(self, kind, head, body, line=None, file=None):
        self.kind = kind
        self.head = head
        self.body = body
        self.line = line
        self.file = file


def _push_goals(goal, out):
    if type(goal) is Struct and goal.name == ',' and len(goal.args) == 2:
        out.extend(flatten_conjunction(goal))
    else:
        out.append(goal)


class Program:
    """options: without leaves out the clause with that number, counting from 1."""

    def __init__(self, sources, without=None):
        self.sources = list(sources)
        self.clauses = []
        self.groups = {}
        self.forward = []
        stratifying = False
        for ordinal, source in enumerate(self.sources, 1):
            if ordinal == without:
                continue
            forward = source.kind in FORWARD_KINDS
            body = []
            for goal in source.body:
                _push_goals(goal, body)
            if forward and not body:
                raise PeyeError(f'line {source.line}: {FORWARD_KINDS[source.kind]} needs at least one goal')
            if source.kind == 'fact' and body:
                raise PeyeError(f'line {source.line}: a fact has no body')
            heads = flatten_conjunction(source.head) if forward else [source.head]
            if source.kind == 'forward' and any(item in ('true', 'false') for item in heads):
                # query() and contradiction() state these, and say so.
                raise PeyeError(f"line {source.line}: implies() cannot conclude 'true' or 'false'; "
                                f"write query(Premise) or contradiction(Premise)")
            for goal in body:
                if not stratifying and _may_need_stratifying(goal):
                    stratifying = True
            for item in heads:
                if not is_callable(item):
                    raise PeyeError(f'line {source.line}: a head must be an atom or a compound term')
                item_key = key(item)
                if (item_key in RESERVED_KEYS or
                        ((item_key in PRIMITIVE_KEYS or item_key in CONTROL_KEYS) and
                         not (forward and item in ('true', 'false')))):
                    raise PeyeError(f'line {source.line}: unsupported or reserved head {item_key[0]}/{item_key[1]}')
            clause = Clause(len(self.clauses) + 1, source.head, heads if forward else None,
                            body, forward, source.line)
            self.clauses.append(clause)
            if forward:
                self.forward.append(clause)
            else:
                self.groups.setdefault(key(source.head), []).append(clause)
        self.indexes = {}
        for group_key, clauses in self.groups.items():
            self.indexes[group_key] = _position_indexes(clauses, lambda clause: clause.head, group_key[1])
        # Ground source facts are compared against forward conclusions by text,
        # so render them once here rather than on every run.
        from .common import text
        self.ground_fact_keys = set()
        for clause in self.clauses:
            if not clause.forward and not clause.body and is_ground(clause.head):
                self.ground_fact_keys.add(text(clause.head))
        self.strata = _stratify(self.clauses, stratifying)

    def candidates(self, goal, env, goal_key):
        clauses = self.groups.get(goal_key)
        if clauses is None:
            return ()
        positions = self.indexes.get(goal_key)
        if not positions:
            return clauses
        chosen = None
        matches = None
        count = len(clauses)
        args = goal.args
        for position, index in enumerate(positions):
            if index is None:
                continue
            argument = args[position]
            if type(argument) is Var:
                argument = deref(argument, env)
            if type(argument) is not str:
                continue
            bucket = index[0].get(argument, ())
            size = len(bucket) + len(index[1])
            if size < count:
                chosen = index
                matches = bucket
                count = size
        if chosen is None:
            return clauses
        if not chosen[1]:
            return matches
        # Retain source order, including clauses with variable or structured heads.
        return sorted([*matches, *chosen[1]], key=lambda clause: clause.id)


def _position_indexes(entries, head_of, arity):
    """An index per argument position where enough entries carry an atom.

    Each index is (atoms, other): a map from atom to entries, and the entries
    with anything else there. Indexing a position where nearly every head has
    a variable rules out nothing, so such a position gets None.
    """
    counts = [0] * arity
    for entry in entries:
        head = head_of(entry)
        if arity:
            for position, arg in enumerate(head.args):
                if type(arg) is str:
                    counts[position] += 1
    positions = [None if count * 2 < len(entries) else ({}, []) for count in counts]
    for entry in entries:
        head = head_of(entry)
        for position in range(arity):
            index = positions[position]
            if index is None:
                continue
            argument = head.args[position]
            if type(argument) is not str:
                index[1].append(entry)
            else:
                index[0].setdefault(argument, []).append(entry)
    return positions


CONTROL_NAMES = frozenset({',', ';', '~', 'call', 'once', 'findall'})


def _dependencies(goal, closed=False, out=None):
    """Closed dependencies arise from absence and collection."""
    if out is None:
        out = []
    if is_term(goal, ',', 2) or is_term(goal, ';', 2):
        _dependencies(goal.args[0], closed, out)
        _dependencies(goal.args[1], closed, out)
    elif is_term(goal, '~', 1):
        _dependencies(goal.args[0], True, out)
    elif is_term(goal, 'findall', 3):
        _dependencies(goal.args[1], True, out)
    elif is_term(goal, 'once', 1) or is_term(goal, 'call', 1):
        _dependencies(goal.args[0], closed, out)
    elif type(goal) is Var or (is_callable(goal) and key(goal) not in PRIMITIVE_KEYS):
        out.append((goal, closed))
    return out


def _may_need_stratifying(goal):
    """Whether a goal could contribute a closed dependency or a dynamic call."""
    if type(goal) is Var:
        return True
    if type(goal) is not Struct or goal.name not in CONTROL_NAMES:
        return False
    if is_term(goal, ',', 2) or is_term(goal, ';', 2):
        return _may_need_stratifying(goal.args[0]) or _may_need_stratifying(goal.args[1])
    if is_term(goal, '~', 1) or is_term(goal, 'findall', 3):
        return True
    if is_term(goal, 'once', 1) or is_term(goal, 'call', 1):
        return _may_need_stratifying(goal.args[0])
    return False


def _head_index(clauses):
    index = {}
    for clause in clauses:
        for head in clause.heads or [clause.head]:
            entry = index.get(key(head))
            if entry is None:
                entry = index[key(head)] = {'pairs': [], 'arity': key(head)[1], 'positions': None}
            entry['pairs'].append((clause, head))
    for entry in index.values():
        entry['positions'] = _position_indexes(entry['pairs'], lambda pair: pair[1], entry['arity'])
    return index


def _head_candidates(entry, goal):
    if entry is None:
        return []
    chosen = entry['pairs']
    for position, bucket in enumerate(entry['positions']):
        if bucket is None or type(goal) is not Struct or type(goal.args[position]) is not str:
            continue
        matched = bucket[0].get(goal.args[position], [])
        if len(matched) + len(bucket[1]) < len(chosen):
            chosen = [*matched, *bucket[1]]
    return chosen


def _stratify(clauses, stratifying):
    """Ranks per clause id; an absent rank is stratum 0.

    Stratification matches whole terms, not just predicate names, so two
    relations sharing a name can sit in different strata. Closed dependency
    cycles are rejected, as are dynamic calls reachable from forward rules.
    """
    if not stratifying:
        return {}
    ranks = {clause.id: 0 for clause in clauses}
    edges = []
    outgoing = {}
    dynamic = set()
    index = _head_index(clauses)
    every_head = [(clause, head) for clause in clauses for head in (clause.heads or [clause.head])]
    for clause in clauses:
        for goal in clause.body:
            for dep_goal, closed in _dependencies(goal):
                named = type(dep_goal) is not Var
                if not named:
                    dynamic.add(clause.id)
                candidates = _head_candidates(index.get(key(dep_goal)), dep_goal) if named else every_head
                for candidate_clause, head in candidates:
                    if unify(fresh_term(dep_goal, 'dependency'), fresh_term(head, 'head'), Env()):
                        edge = (clause.id, candidate_clause.id, closed)
                        edges.append(edge)
                        outgoing.setdefault(clause.id, []).append(edge)
    reachable = set()
    pending = [clause.id for clause in clauses if clause.forward]
    while pending:
        clause_id = pending.pop()
        if clause_id in reachable:
            continue
        reachable.add(clause_id)
        if clause_id in dynamic:
            raise PeyeError('forward dependencies require statically named calls')
        for edge in outgoing.get(clause_id, ()):
            pending.append(edge[1])
    for _ in range(len(ranks) + 1):
        changed = False
        for head_id, target_id, closed in edges:
            rank = ranks.get(target_id, 0) + int(closed)
            if rank > ranks[head_id]:
                ranks[head_id] = rank
                changed = True
        if not changed:
            return ranks
    raise PeyeError('unstratified negation or collection dependency')
