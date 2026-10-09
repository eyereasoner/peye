"""Finite-tree terms, substitutions, unification and the standard order.

A term is one of
  - a Python ``str``: an atom ('socrates', '[]' is the empty list),
  - a Python ``int`` (unbounded) or ``float`` (IEEE-754 double): a number,
  - a ``Var``: a logical variable, identified by its name,
  - a ``Struct``: a compound term, a name with a tuple of argument terms.
A list is built from ``Struct('.', (Head, Tail))`` cells ending in '[]'.

Terms never change once built. Var and Struct carry Python operators, so rule
programs can write ``X + 1``, ``X < Y``, ``p(X) & q(X)``, ``a | b`` and ``~g``;
the operators only build terms, they never compute anything.
"""

import contextlib
import math
import sys

EMPTY = '[]'


class PeyeError(Exception):
    """An error in a peye program, a goal or a proof document."""


# Python refuses to convert integers longer than a set number of digits
# (4300 by default, never less than 640) between text and int. Exact integers
# can be far longer, so peye converts them in pieces below that limit, and
# lifts it only while Python itself parses source text; it never changes the
# limit for the rest of the process.
_PIECE = 600


def decimal_int(digits):
    """The integer a string of decimal digits spells, however long."""
    if len(digits) <= _PIECE:
        return int(digits)
    low = len(digits) // 2
    return decimal_int(digits[:-low]) * 10 ** low + decimal_int(digits[-low:])


def decimal_text(number):
    """The decimal text of an integer, however long."""
    if number < 0:
        return '-' + decimal_text(-number)
    if number.bit_length() <= 1990:  # fewer than 600 digits
        return str(number)
    low = int(number.bit_length() * 0.30103) // 2
    high, rest = divmod(number, 10 ** low)
    return decimal_text(high) + decimal_text(rest).zfill(low)


@contextlib.contextmanager
def unlimited_digits():
    """Lift Python's limit on integer digits while source text is parsed."""
    get = getattr(sys, 'get_int_max_str_digits', None)
    if get is None:
        yield
        return
    previous = get()
    sys.set_int_max_str_digits(0)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(previous)


def nonfinite(value, where=''):
    """The error for a float that is not a term: an infinity or a NaN."""
    return PeyeError(f'{where}a float term must be finite, not {value!r}')


def _term(value):
    """Turn a Python value written in a rule program into a term."""
    kind = type(value)
    if kind is float and not math.isfinite(value):
        raise nonfinite(value)
    if kind is str or kind is int or kind is float or kind is Var or kind is Struct:
        return value
    if kind is list:
        return _from_python_list(value)
    if kind is bool:
        # A comparison of two numbers, such as 1 < 2, is decided by Python
        # before peye sees it.
        raise PeyeError(f'{value!r} is not a term: a comparison or test of plain Python values is '
                        f'decided by Python before peye sees it; compare terms or variables, or '
                        f'write an atom such as \'true\'')
    if value is None:
        raise PeyeError(f'{value!r} is not a term; write an atom such as \'true\' instead')
    to_term = getattr(value, '__peye_term__', None)
    if to_term is not None:
        return to_term()
    raise PeyeError(f'{value!r} of type {kind.__name__} is not a term')


class Tail:
    """The rest of an open list: ``[H, *T]`` stars T, which yields one Tail."""
    __slots__ = ('term',)

    def __init__(self, term):
        self.term = term


def _from_python_list(items):
    tail = EMPTY
    if items and type(items[-1]) is Tail:
        tail = _term(items[-1].term)
        items = items[:-1]
    result = tail
    for item in reversed(items):
        if type(item) is Tail:
            raise PeyeError('a starred tail can only end a list')
        result = Struct('.', (_term(item), result))
    return result


class Term:
    """Operators shared by variables, compound terms and predicate names.
    Each builds a term."""
    __slots__ = ()

    def __add__(self, other): return Struct('+', (_term(self), _term(other)))
    def __radd__(self, other): return Struct('+', (_term(other), _term(self)))
    def __sub__(self, other): return Struct('-', (_term(self), _term(other)))
    def __rsub__(self, other): return Struct('-', (_term(other), _term(self)))
    def __mul__(self, other): return Struct('*', (_term(self), _term(other)))
    def __rmul__(self, other): return Struct('*', (_term(other), _term(self)))
    def __truediv__(self, other): return Struct('/', (_term(self), _term(other)))
    def __rtruediv__(self, other): return Struct('/', (_term(other), _term(self)))
    def __floordiv__(self, other): return Struct('//', (_term(self), _term(other)))
    def __rfloordiv__(self, other): return Struct('//', (_term(other), _term(self)))
    def __mod__(self, other): return Struct('%', (_term(self), _term(other)))
    def __rmod__(self, other): return Struct('%', (_term(other), _term(self)))
    def __pow__(self, other): return Struct('**', (_term(self), _term(other)))
    def __rpow__(self, other): return Struct('**', (_term(other), _term(self)))
    def __lshift__(self, other): return Struct('<<', (_term(self), _term(other)))
    def __rlshift__(self, other): return Struct('<<', (_term(other), _term(self)))
    def __rshift__(self, other): return Struct('>>', (_term(self), _term(other)))
    def __rrshift__(self, other): return Struct('>>', (_term(other), _term(self)))
    def __xor__(self, other): return Struct('^', (_term(self), _term(other)))
    def __rxor__(self, other): return Struct('^', (_term(other), _term(self)))
    # & | ~ are conjunction, disjunction and negation of goals; inside an
    # arithmetic expression they are bitwise and, or and invert, as in Python.
    def __and__(self, other): return Struct(',', (_term(self), _term(other)))
    def __rand__(self, other): return Struct(',', (_term(other), _term(self)))
    def __or__(self, other): return Struct(';', (_term(self), _term(other)))
    def __ror__(self, other): return Struct(';', (_term(other), _term(self)))
    def __invert__(self): return Struct('~', (_term(self),))
    def __neg__(self): return Struct('-', (_term(self),))
    def __pos__(self): return Struct('+', (_term(self),))
    def __abs__(self): return Struct('abs', (_term(self),))
    def __lt__(self, other): return Struct('<', (_term(self), _term(other)))
    def __le__(self, other): return Struct('<=', (_term(self), _term(other)))
    def __gt__(self, other): return Struct('>', (_term(self), _term(other)))
    def __ge__(self, other): return Struct('>=', (_term(self), _term(other)))

    def __bool__(self):
        raise PeyeError(
            'a term has no truth value in Python; parenthesize comparisons joined '
            'by & or |, as in (X > 1) & (Y < 2), and write eq(X, Y) for numeric equality')

    def __iter__(self):
        # Lets [H, *T] write an open list.
        yield Tail(_term(self))

    def __str__(self):
        from .writer import write
        return write(self)

    __repr__ = __str__


class Var(Term):
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    # Variables are identified by name, so they can be dictionary keys.
    __hash__ = object.__hash__


class Struct(Term):
    __slots__ = ('name', 'args')

    def __init__(self, name, args):
        self.name = name
        self.args = args

    __hash__ = object.__hash__


def cons(head, tail):
    return Struct('.', (head, tail))


def list_from_items(items, tail=EMPTY):
    result = tail
    for item in reversed(items):
        result = Struct('.', (item, result))
    return result


def is_cons(term):
    return type(term) is Struct and term.name == '.' and len(term.args) == 2


def proper_list_items(term, env):
    items = []
    cursor = deref(term, env)
    while type(cursor) is Struct and cursor.name == '.' and len(cursor.args) == 2:
        items.append(cursor.args[0])
        cursor = deref(cursor.args[1], env)
    return items if type(cursor) is str and cursor == EMPTY else None


def is_callable(term):
    return type(term) is str or type(term) is Struct


def key(term):
    """The name/arity of a callable term, as a hashable pair."""
    return (term, 0) if type(term) is str else (term.name, len(term.args))


def is_term(term, name, arity):
    if type(term) is str:
        return arity == 0 and term == name
    return type(term) is Struct and term.name == name and len(term.args) == arity


def flatten_conjunction(goal):
    out = []
    stack = [goal]
    while stack:
        current = stack.pop()
        if type(current) is Struct and current.name == ',' and len(current.args) == 2:
            stack.append(current.args[1])
            stack.append(current.args[0])
        else:
            out.append(current)
    return out


def conjunction(items):
    """Goals joined left to right, as Python reads g1 & g2 & g3."""
    if not items:
        return 'true'
    result = items[0]
    for item in items[1:]:
        result = Struct(',', (result, item))
    return result


class Env:
    """One substitution per search, with an undo trail.

    Backtracking restores the bindings a failed branch made instead of copying
    the whole map for every alternative. The trail records each name with the
    value it had, so rebinding a name, which path compression in deref does,
    undoes correctly too.
    """
    __slots__ = ('bindings', 'trail')

    def __init__(self):
        self.bindings = {}
        self.trail = []

    def mark(self):
        return len(self.trail)

    def undo(self, mark):
        trail = self.trail
        bindings = self.bindings
        while len(trail) > mark:
            previous = trail.pop()
            name = trail.pop()
            if previous is None:
                del bindings[name]
            else:
                bindings[name] = previous

    def bind(self, name, value):
        self.trail.append(name)
        self.trail.append(self.bindings.get(name))
        self.bindings[name] = value


def deref(term, env):
    if type(term) is not Var:
        return term
    bindings = env.bindings
    value = bindings.get(term.name)
    if value is None:
        return term
    if type(value) is not Var:
        return value
    # Resolving a chain of variable-to-variable bindings records where the
    # whole chain ended, so a variable threaded through N resolution steps is
    # not re-walked on every dereference.
    chain = [term.name]
    while type(value) is Var:
        following = bindings.get(value.name)
        if following is None:
            break
        chain.append(value.name)
        value = following
    for name in chain:
        env.bind(name, value)
    return value


def _occurs(name, term, env):
    pending = [term]
    while pending:
        item = deref(pending.pop(), env)
        kind = type(item)
        if kind is Var:
            if item.name == name:
                return True
        elif kind is Struct:
            pending.extend(item.args)
    return False


def unify(left, right, env):
    """Unify on finite trees: the occurs check always applies."""
    pending = [left, right]
    while pending:
        b = deref(pending.pop(), env)
        a = deref(pending.pop(), env)
        if a is b:
            continue
        ta = type(a)
        tb = type(b)
        if ta is Var:
            if tb is Var and a.name == b.name:
                continue
            if tb is Struct and _occurs(a.name, b, env):
                return False
            env.bind(a.name, b)
        elif tb is Var:
            if ta is Struct and _occurs(b.name, a, env):
                return False
            env.bind(b.name, a)
        elif ta is not tb:
            # Integers and floats stay distinct: 7 and 7.0 do not unify.
            return False
        elif ta is Struct:
            if a.name != b.name or len(a.args) != len(b.args):
                return False
            args_a = a.args
            args_b = b.args
            for i in range(len(args_a) - 1, -1, -1):
                pending.append(args_a[i])
                pending.append(args_b[i])
        elif a != b:
            return False
    return True


def fresh_term(term, suffix, names=None):
    """Rename a term's variables apart. A subterm without variables is shared."""
    if names is None:
        names = {}
    kind = type(term)
    if kind is Var:
        fresh = names.get(term.name)
        if fresh is None:
            fresh = Var(f'{term.name}#{suffix}')
            names[term.name] = fresh
        return fresh
    if kind is not Struct:
        return term
    args = term.args
    copied = None
    for index, arg in enumerate(args):
        kind = type(arg)
        copy = arg if (kind is not Var and kind is not Struct) else fresh_term(arg, suffix, names)
        if copied is None:
            if copy is arg:
                continue
            copied = list(args[:index])
        copied.append(copy)
    return term if copied is None else Struct(term.name, tuple(copied))


def copy_resolved(term, env):
    """The term with every bound variable replaced by its value.

    Deeply nested terms are copied iteratively, and shared subterms stay
    shared in the copy; a subterm that resolves to itself is not copied.
    """
    root = deref(term, env)
    if type(root) is not Struct:
        return root
    done = {}
    stack = [root]
    while stack:
        node = stack[-1]
        if id(node) in done:
            stack.pop()
            continue
        missing = False
        for arg in node.args:
            arg = deref(arg, env)
            if type(arg) is Struct and id(arg) not in done:
                stack.append(arg)
                missing = True
        if missing:
            continue
        stack.pop()
        args = []
        same = True
        for arg in node.args:
            value = deref(arg, env)
            if type(value) is Struct:
                value = done[id(value)]
            if value is not arg:
                same = False
            args.append(value)
        done[id(node)] = node if same else Struct(node.name, tuple(args))
    return done[id(root)]


def is_anonymous(var):
    """Whether a variable stands for a _ of a program or a document: _0, _1,
    ... in a clause, renamed apart or not, or one a reader made."""
    base = var.name.partition('#')[0]
    return base == '_' or (len(base) > 1 and base[0] == '_' and base[1:].isdigit())


def is_ground_but_anonymous(term, env):
    """Whether every variable left in term, read through env, is anonymous."""
    pending = [term]
    while pending:
        item = deref(pending.pop(), env)
        if type(item) is Var:
            if not is_anonymous(item):
                return False
        elif type(item) is Struct:
            pending.extend(item.args)
    return True


def is_ground(term, env=None):
    pending = [term]
    seen = None
    while pending:
        item = pending.pop()
        if env is not None:
            item = deref(item, env)
        kind = type(item)
        if kind is Var:
            return False
        if kind is Struct:
            if seen is None:
                seen = set()
            if id(item) in seen:
                continue
            seen.add(id(item))
            pending.extend(item.args)
    return True


def variables(term, result=None):
    """The variables of a term by name, in order of first appearance."""
    if result is None:
        result = {}
    pending = [term]
    while pending:
        item = pending.pop()
        kind = type(item)
        if kind is Var:
            result.setdefault(item.name, item)
        elif kind is Struct:
            pending.extend(reversed(item.args))
    return result


# Standard order: variables < numbers < atoms < compound terms. Numbers are
# ordered by value, and a float precedes an integer of equal value. Distinct
# variables are ordered by name, so the order is the same in every comparison.
_ORDER = {Var: 0, int: 1, float: 1, str: 2, Struct: 3}


def compare_terms(left, right):
    pending = [left, right]
    while pending:
        right = pending.pop()
        left = pending.pop()
        lt = type(left)
        rt = type(right)
        lr = _ORDER[lt]
        rr = _ORDER[rt]
        if lr != rr:
            return -1 if lr < rr else 1
        if lr == 1:
            if left != right:
                return -1 if left < right else 1
            if lt is not rt:
                return 1 if lt is int else -1
        elif lt is Var:
            if left.name != right.name:
                return -1 if left.name < right.name else 1
        elif lt is str:
            if left != right:
                return -1 if left < right else 1
        else:
            if len(left.args) != len(right.args):
                return -1 if len(left.args) < len(right.args) else 1
            if left.name != right.name:
                return -1 if left.name < right.name else 1
            for i in range(len(left.args) - 1, -1, -1):
                pending.append(left.args[i])
                pending.append(right.args[i])
    return 0
