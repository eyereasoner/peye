"""Helpers shared by the engine and the proof checker."""
from .terms import Struct, Var, fresh_term, is_ground
from .writer import write


def text(term, env=None):
    """The canonical spelling of a term, which also serves as its identity."""
    return write(term, env)


def fresh_clause(clause, suffix):
    """Rename a clause apart: head and body share one set of fresh variables,
    listed in the order the clause is written (a forward rule's body first)."""
    renamed = renaming(clause)
    if renamed is None:
        names = {}
        if clause.forward:
            body = [fresh_term(goal, suffix, names) for goal in clause.body]
            head = fresh_term(clause.head, suffix, names)
        else:
            head = fresh_term(clause.head, suffix, names)
            body = [fresh_term(goal, suffix, names) for goal in clause.body]
        return head, body, names
    suffix = str(suffix)
    values = [Var(prefix + suffix) for prefix in renamed.prefixes]
    names = dict(zip(renamed.names, values))
    if renamed.written is not None:
        names = {name: names[name] for name in renamed.written}
    return renamed.head(values), renamed.body(values), names


class Renaming:
    """How to rename a clause apart quickly, worked out once per clause.

    The clause's variables are numbered in order of first occurrence, head
    first, and head(values) and body(values) build the renamed head and body
    from a list of fresh variables in that order: the first head_count of
    them suffice for the head. Subterms without variables are shared.
    """
    __slots__ = ('names', 'prefixes', 'head_count', 'head', 'body', 'uses', 'written')


def renaming(clause):
    """How to rename a clause apart quickly, or None while it has been used
    too seldom to be worth working out: most clauses of a large program are
    used once, and renaming those directly is cheaper."""
    renamed = clause.renaming
    if renamed is None:
        clause.uses += 1
        if clause.uses < _WORK_OUT_AFTER:
            return None
        renamed = clause.renaming = _renaming(clause)
    return renamed


_WORK_OUT_AFTER = 3


# A clause renamed this often gets code generated to build its renamed terms;
# compiling one costs about as much as renaming it some tens of times by
# substitution, and many clauses, such as those of a large generated program,
# are used only once or twice.
_COMPILE_AFTER = 8
# Deeper terms are always built by substitution: Python could not compile
# the code that builds them.
_MAX_DEPTH = 40


def _renaming(clause):
    index = {}
    for term in [clause.head, *clause.body]:
        pending = [term]
        while pending:
            item = pending.pop()
            if type(item) is Var:
                index.setdefault(item.name, len(index))
            elif type(item) is Struct:
                pending.extend(reversed(item.args))
        if term is clause.head:
            head_count = len(index)
    renamed = Renaming()
    renamed.names = list(index)
    renamed.prefixes = [name + '#' for name in index]
    renamed.head_count = head_count
    renamed.uses = 0
    # A forward rule is written premise first, implies(Body, Head), and its
    # variables are listed in that order.
    renamed.written = None
    if clause.forward:
        written = {}
        for term in [*clause.body, clause.head]:
            pending = [term]
            while pending:
                item = pending.pop()
                if type(item) is Var:
                    written.setdefault(item.name, None)
                elif type(item) is Struct:
                    pending.extend(reversed(item.args))
        renamed.written = list(written)

    def substituted_head(values):
        return _substitute(clause.head, index, values)

    def substituted_body(values):
        return [_substitute(goal, index, values) for goal in clause.body]

    def counted_head(values):
        renamed.uses += 1
        if renamed.uses >= _COMPILE_AFTER:
            renamed.head, renamed.body = _compiled(clause, index) or (substituted_head, substituted_body)
        return substituted_head(values)

    renamed.head, renamed.body = counted_head, substituted_body
    return renamed


def _compiled(clause, index):
    """Functions building the renamed head and body, or None for a clause too
    deep to generate code for."""
    constants = {'S': Struct}

    def code(term, depth):
        if type(term) is Var:
            return f'v[{index[term.name]}]'
        if type(term) is Struct and not is_ground(term):
            if depth > _MAX_DEPTH:
                raise RecursionError
            name = f'c{len(constants)}'
            constants[name] = term.name
            return f"S({name}, ({''.join(code(arg, depth + 1) + ', ' for arg in term.args)}))"
        name = f'c{len(constants)}'
        constants[name] = term
        return name

    try:
        source = (f'def head(v):\n    return {code(clause.head, 0)}\n'
                  f"def body(v):\n    return [{', '.join(code(goal, 0) for goal in clause.body)}]\n")
        exec(compile(source, '<renaming>', 'exec'), constants)
    except (RecursionError, MemoryError, SyntaxError):
        return None
    return constants['head'], constants['body']


def _substitute(term, index, values):
    kind = type(term)
    if kind is Var:
        return values[index[term.name]]
    if kind is not Struct:
        return term
    args = term.args
    copied = None
    for position, arg in enumerate(args):
        copy = arg if type(arg) is not Var and type(arg) is not Struct else _substitute(arg, index, values)
        if copied is None:
            if copy is arg:
                continue
            copied = list(args[:position])
        copied.append(copy)
    return term if copied is None else Struct(term.name, tuple(copied))


def variant(term):
    """A key that preserves sharing while forgetting variable names."""
    names = {}

    def visit(t):
        if type(t) is Var:
            if t.name not in names:
                names[t.name] = Var(f'V{len(names)}')
            return names[t.name]
        if type(t) is Struct:
            return Struct(t.name, tuple(visit(arg) for arg in t.args))
        return t
    return text(visit(term))
