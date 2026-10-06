"""Helpers shared by the engine and the proof checker."""
from .terms import Struct, Var, fresh_term
from .writer import write


def text(term, env=None):
    """The canonical spelling of a term, which also serves as its identity."""
    return write(term, env)


def fresh_clause(clause, suffix):
    """Rename a clause apart: head and body share one set of fresh variables."""
    names = {}
    head = fresh_term(clause.head, suffix, names)
    body = [fresh_term(goal, suffix, names) for goal in clause.body]
    return head, body, names


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
