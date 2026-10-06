"""The pure primitives.

Only pure primitives belong here. Collections, call and negation are controls
handled by the solver and explicitly distinguished in proof documents.

A test decides a goal at most once: it is handed the goal's arguments, the
same arguments dereferenced, the substitution and a bind function, and says
whether the goal holds. Any bindings it made on the way to failing are undone
for it. A relation can hold several times: it is a generator that yields once
per solution, and the solver undoes the bindings of one solution before asking
for the next.
"""
import itertools

from . import arith
from .terms import (
    PeyeError, Struct, Var, compare_terms, copy_resolved, deref, is_ground,
    key, list_from_items, proper_list_items, unify,
)


def _comparison(holds):
    return lambda args, resolved, env, bind: holds(arith.compare(args[0], args[1], env))


def _same(args, env):
    return compare_terms(copy_resolved(args[0], env), copy_resolved(args[1], env)) == 0


def _not_unify(args, resolved, env, bind):
    mark = env.mark()
    unifies = unify(args[0], args[1], env)
    env.undo(mark)
    return not unifies


def _bounded_integer(term, low, high):
    if type(term) is not int or term < 0:
        raise PeyeError('expected a nonnegative integer')
    if term < low or term > high:
        raise PeyeError(f'integer outside {low}..{high}')
    return term


_functor_serial = itertools.count(1)


def _functor(args, resolved, env, bind):
    term, name, arity = resolved
    if type(term) is not Var:
        if type(term) is Struct:
            return bind(args[1], term.name) and bind(args[2], len(term.args))
        return bind(args[1], term) and bind(args[2], 0)
    count = _bounded_integer(arity, 0, 1024)
    if type(name) is Var:
        raise PeyeError('functor/3 needs a bound name')
    if count > 0 and type(name) is not str:
        raise PeyeError('functor/3 needs an atom name')
    # Unique names across primitive invocations preserve variable isolation.
    serial = next(_functor_serial)
    if count == 0:
        return bind(args[0], name)
    return bind(args[0], Struct(name, tuple(Var(f'_functor{serial}_{i}') for i in range(count))))


def _arg(args, resolved, env, bind):
    position, term = resolved[0], resolved[1]
    index = _bounded_integer(position, 1, 1024)
    return type(term) is Struct and index <= len(term.args) and bind(args[2], term.args[index - 1])


def _univ(args, resolved, env, bind):
    term = resolved[0]
    if type(term) is not Var:
        if type(term) is Struct:
            return bind(args[1], list_from_items([term.name, *term.args]))
        return bind(args[1], list_from_items([term]))
    items = proper_list_items(args[1], env)
    items = None if items is None else [deref(item, env) for item in items]
    if not items or type(items[0]) is Var or (len(items) > 1 and type(items[0]) is not str):
        raise PeyeError('univ/2 needs a nonempty bound term list')
    return bind(args[0], items[0] if len(items) == 1 else Struct(items[0], tuple(items[1:])))


def _atom_text(name, codes):
    def test(args, resolved, env, bind):
        term = resolved[0]
        if type(term) is str:
            items = [ord(ch) for ch in term] if codes else list(term)
            return bind(args[1], list_from_items(items))
        items = proper_list_items(args[1], env)
        if items is None:
            raise PeyeError(f'{name} needs a proper list')
        chars = []
        for item in items:
            item = deref(item, env)
            if codes:
                chars.append(chr(_bounded_integer(item, 0, 0x10FFFF)))
            else:
                if type(item) is not str or len(item) != 1:
                    raise PeyeError('atom_chars/2 needs characters')
                chars.append(item)
        return bind(args[0], ''.join(chars))
    return test


def _atom_length(args, resolved, env, bind):
    if type(resolved[0]) is not str:
        raise PeyeError('atom_length/2 needs a bound atom')
    return bind(args[1], len(resolved[0]))


def _compare(args, resolved, env, bind):
    order = compare_terms(copy_resolved(args[1], env), copy_resolved(args[2], env))
    return bind(args[0], '<' if order < 0 else ('>' if order > 0 else '='))


def _is(args, resolved, env, bind):
    return bind(args[0], arith.evaluate(args[1], env))


TESTS = {
    ('true', 0): lambda args, resolved, env, bind: True,
    ('fail', 0): lambda args, resolved, env, bind: False,
    ('false', 0): lambda args, resolved, env, bind: False,
    ('unify', 2): lambda args, resolved, env, bind: bind(args[0], args[1]),
    ('not_unify', 2): _not_unify,
    ('identical', 2): lambda args, resolved, env, bind: _same(args, env),
    ('not_identical', 2): lambda args, resolved, env, bind: not _same(args, env),
    ('is_', 2): _is,
    ('eq', 2): _comparison(lambda n: n == 0),
    ('ne', 2): _comparison(lambda n: n != 0),
    ('<', 2): _comparison(lambda n: n < 0),
    ('<=', 2): _comparison(lambda n: n <= 0),
    ('>', 2): _comparison(lambda n: n > 0),
    ('>=', 2): _comparison(lambda n: n >= 0),
    ('is_var', 1): lambda args, resolved, env, bind: type(resolved[0]) is Var,
    ('is_nonvar', 1): lambda args, resolved, env, bind: type(resolved[0]) is not Var,
    ('is_ground', 1): lambda args, resolved, env, bind: is_ground(args[0], env),
    ('is_atom', 1): lambda args, resolved, env, bind: type(resolved[0]) is str,
    ('is_number', 1): lambda args, resolved, env, bind: type(resolved[0]) in (int, float),
    ('is_int', 1): lambda args, resolved, env, bind: type(resolved[0]) is int,
    ('is_float', 1): lambda args, resolved, env, bind: type(resolved[0]) is float,
    ('is_compound', 1): lambda args, resolved, env, bind: type(resolved[0]) is Struct,
    ('functor', 3): _functor,
    ('arg', 3): _arg,
    ('univ', 2): _univ,
    ('atom_chars', 2): _atom_text('atom_chars/2', False),
    ('atom_codes', 2): _atom_text('atom_codes/2', True),
    ('atom_length', 2): _atom_length,
    ('compare', 3): _compare,
}


def _atom_concat(args, resolved, env, mark):
    left, right, whole = resolved
    if type(left) is str and type(right) is str:
        if unify(args[2], left + right, env):
            yield env
        else:
            env.undo(mark)
        return
    if type(whole) is not str:
        raise PeyeError('atom_concat/3 needs the result or both operands bound')
    for i in range(len(whole) + 1):
        if unify(args[0], whole[:i], env) and unify(args[1], whole[i:], env):
            yield env
        env.undo(mark)


RELATIONS = {
    ('atom_concat', 3): _atom_concat,
}
PRIMITIVE_KEYS = frozenset(TESTS) | frozenset(RELATIONS)


def primitive(goal, env):
    """Solve a primitive goal: a generator yielding env once per solution."""
    goal_key = key(goal)
    args = goal.args if type(goal) is Struct else ()
    resolved = [deref(arg, env) for arg in args]
    mark = env.mark()
    test = TESTS.get(goal_key)
    if test is None:
        relation = RELATIONS.get(goal_key)
        if relation is None:
            raise PeyeError(f'unsupported primitive {goal_key[0]}/{goal_key[1]}')
        yield from relation(args, resolved, env, mark)
        return
    if test(args, resolved, env, lambda a, b: unify(a, b, env)):
        yield env
    else:
        env.undo(mark)
