"""Canonical term output, as Python source.

Every term has one spelling, and that spelling is a Python expression that the
reader in reader.py turns back into the same term: an atom is a string
literal, a number a numeric literal, a variable a name, a compound term a call
such as ``type('socrates', 'mortal')``, a list a list display with ``*T`` for
an open tail, and the operators keep their Python spelling and precedence:
``X + 1``, ``X < Y``, ``p(X) & q(X)``, ``a | b``, ``~g``. A compound whose
name is not a Python identifier is written ``struct('name', Arg, ...)``.
"""
import functools
import keyword

from .terms import Struct, Var, deref

INFIX = {
    ';': ('|', 7), '^': ('^', 8), ',': ('&', 9), '<<': ('<<', 10), '>>': ('>>', 10),
    '+': ('+', 11), '-': ('-', 11), '*': ('*', 12), '/': ('/', 12), '//': ('//', 12),
    '%': ('%', 12), '**': ('**', 14),
    '<': ('<', 6), '<=': ('<=', 6), '>': ('>', 6), '>=': ('>=', 6),
}
PREFIX = {'-': '-', '+': '+', '~': '~'}
COMPARISON = 6
UNARY = 13
POWER = 14
ATOMIC = 100
# Calls to these names have a fixed meaning to the reader.
RESERVED_CALLS = frozenset({'struct'})


@functools.lru_cache(maxsize=4096)
def callable_name(name):
    return name.isidentifier() and not keyword.iskeyword(name) and name not in RESERVED_CALLS


def valid_variable_name(name):
    return (name.isidentifier() and not keyword.iskeyword(name) and name != '_'
            and not name.startswith('EYE_'))


def encode_name(name):
    """An injective identifier for a variable name that is not a valid one.

    X#12, the name a renamed-apart clause variable gets, becomes EYE_X_23_12:
    letters and digits stay, an underscore doubles and any other character
    becomes _hex_. Names already starting with the prefix are encoded too.
    """
    out = ['EYE_']
    for ch in name:
        if ch.isascii() and ch.isalnum():
            out.append(ch)
        elif ch == '_':
            out.append('__')
        else:
            out.append(f'_{ord(ch):x}_')
    return ''.join(out)


@functools.lru_cache(maxsize=4096)
def variable_text(name):
    return name if valid_variable_name(name) else encode_name(name)


def _precedence(term):
    kind = type(term)
    if kind is Struct:
        arity = len(term.args)
        if arity == 2 and term.name in INFIX:
            return INFIX[term.name][1]
        if arity == 1 and term.name in PREFIX and not _ambiguous_prefix(term):
            return UNARY
        return ATOMIC
    if (kind is int or kind is float) and (term < 0 or (kind is float and str(term)[0] == '-')):
        return UNARY
    return ATOMIC


def _ambiguous_prefix(term):
    # -(1) would read back as the number -1.
    arg = term.args[0]
    return term.name == '-' and (type(arg) is int or type(arg) is float)


def write(term, env=None, names=None):
    """The canonical spelling of a term; Python values a program writes, such
    as lists, are taken as the terms they stand for."""
    if type(term) not in (str, int, float, Var, Struct):
        from .terms import _term
        term = _term(term)
    # Without a substitution there is nothing to dereference.
    if env is not None and not env.bindings:
        env = None
    if names is None:
        names = {}
    out = []
    _format(term, env, names, out)
    return ''.join(out)


def _format(term, env, names, out):
    if env is not None:
        term = deref(term, env)
    kind = type(term)
    if kind is str:
        out.append(repr(term) if term != '[]' else '[]')
    elif kind is int:
        out.append(str(term))
    elif kind is float:
        out.append(repr(term))
    elif kind is Var:
        name = names.get(term.name)
        out.append(name if name is not None else variable_text(term.name))
    elif term.name == '.' and len(term.args) == 2:
        out.append('[')
        cursor = term
        first = True
        while type(cursor) is Struct and cursor.name == '.' and len(cursor.args) == 2:
            if not first:
                out.append(', ')
            first = False
            _format(cursor.args[0], env, names, out)
            cursor = cursor.args[1] if env is None else deref(cursor.args[1], env)
        if not (type(cursor) is str and cursor == '[]'):
            out.append(', *')
            _operand(cursor, env, names, out, COMPARISON + 1)
        out.append(']')
    else:
        _format_struct(term, env, names, out)


def _operand(term, env, names, out, minimum):
    if env is not None:
        term = deref(term, env)
    if _precedence(term) < minimum:
        out.append('(')
        _format(term, env, names, out)
        out.append(')')
    else:
        _format(term, env, names, out)


def _format_struct(term, env, names, out):
    name = term.name
    args = term.args
    arity = len(args)
    if arity == 2 and name in INFIX:
        symbol, level = INFIX[name]
        if level == COMPARISON:
            _operand(args[0], env, names, out, level + 1)
            out.append(f' {symbol} ')
            _operand(args[1], env, names, out, level + 1)
        elif level == POWER:
            # Right associative, and binds tighter than a unary minus on its left.
            _operand(args[0], env, names, out, level + 1)
            out.append(' ** ')
            _operand(args[1], env, names, out, level)
        else:
            _operand(args[0], env, names, out, level)
            out.append(f' {symbol} ')
            _operand(args[1], env, names, out, level + 1)
        return
    if arity == 1 and name in PREFIX and not _ambiguous_prefix(term):
        out.append(PREFIX[name])
        _operand(args[0], env, names, out, UNARY)
        return
    if callable_name(name):
        out.append(name)
        out.append('(')
    else:
        out.append('struct(')
        out.append(repr(name))
        if arity:
            out.append(', ')
    for index, arg in enumerate(args):
        if index:
            out.append(', ')
        _format(arg, env, names, out)
    out.append(')')
