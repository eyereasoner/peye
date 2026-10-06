"""Arithmetic evaluation with Python semantics.

An expression term means what the same expression means in Python: integers
are unbounded and exact, floats are IEEE-754 doubles, ``/`` is true division,
``//`` and ``%`` are floor division and modulo, ``**`` is exact on integers
with a nonnegative exponent, and ``&``, ``|``, ``^``, ``~``, ``<<`` and ``>>``
are the bitwise operators. The functions are Python's builtins ``abs``,
``min``, ``max``, ``round``, ``int`` and ``float``, and from ``math`` the
functions listed in FUNCTIONS. A result that is not a finite real number is an
error, never a value.
"""
import math

from .terms import PeyeError, Var, deref

# A power whose result would need more bits than this is refused rather than
# allowed to exhaust memory.
MAX_POWER_BITS = 1 << 26


def _power(a, b):
    if type(a) is int and type(b) is int and b > 0 and abs(a) > 1:
        if b * a.bit_length() > MAX_POWER_BITS:
            raise PeyeError(f'arithmetic resource: {a} ** {b} is too large')
    return a ** b


def _shift(a, b):
    if type(a) is int and type(b) is int and b > MAX_POWER_BITS:
        raise PeyeError(f'arithmetic resource: {a} << {b} is too large')
    return a << b


BINARY = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
    '//': lambda a, b: a // b,
    '%': lambda a, b: a % b,
    '**': _power,
    '<<': _shift,
    '>>': lambda a, b: a >> b,
    '^': lambda a, b: a ^ b,
    ',': lambda a, b: a & b,
    ';': lambda a, b: a | b,
}
UNARY = {
    '-': lambda a: -a,
    '+': lambda a: +a,
    '~': lambda a: ~a,
}
FUNCTIONS = {
    'abs': abs, 'min': min, 'max': max, 'round': round, 'int': int, 'float': float,
    'pow': _power, 'gcd': math.gcd, 'lcm': getattr(math, 'lcm', None),
    'floor': math.floor, 'ceil': math.ceil, 'trunc': math.trunc,
    'sqrt': math.sqrt, 'isqrt': math.isqrt, 'exp': math.exp, 'log': math.log,
    'log2': math.log2, 'log10': math.log10,
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'atan2': math.atan2,
    'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
    'hypot': math.hypot, 'degrees': math.degrees, 'radians': math.radians,
    'fmod': math.fmod, 'copysign': math.copysign,
}
FUNCTIONS = {name: fn for name, fn in FUNCTIONS.items() if fn is not None}
CONSTANTS = {'pi': math.pi, 'e': math.e, 'tau': math.tau}


def evaluate(term, env):
    term = deref(term, env)
    kind = type(term)
    if kind is int or kind is float:
        return term
    if kind is Var:
        raise PeyeError('arithmetic needs a bound expression, found an unbound variable')
    if kind is str:
        if term in CONSTANTS:
            return CONSTANTS[term]
        raise PeyeError(f'{term!r} is not an arithmetic value')
    values = [evaluate(arg, env) for arg in term.args]
    return apply(term.name, values)


def apply(name, values):
    arity = len(values)
    if arity == 2 and name in BINARY:
        fn = BINARY[name]
    elif arity == 1 and name in UNARY:
        fn = UNARY[name]
    elif name in FUNCTIONS:
        fn = FUNCTIONS[name]
    else:
        raise PeyeError(f'{name}/{arity} is not an arithmetic function')
    try:
        result = fn(*values)
    except ZeroDivisionError:
        raise PeyeError(f'arithmetic: division by zero in {name}') from None
    except OverflowError:
        raise PeyeError(f'arithmetic: overflow in {name}') from None
    except (ValueError, TypeError) as error:
        raise PeyeError(f'arithmetic: {name} {error}') from None
    kind = type(result)
    if kind is int:
        return result
    if kind is float:
        if not math.isfinite(result):
            raise PeyeError(f'arithmetic: {name} has no finite result')
        return result
    if kind is bool:
        return int(result)
    raise PeyeError(f'arithmetic: {name} has no real result')


def compare(left, right, env):
    """-1, 0 or 1. Python compares integers and floats exactly."""
    a = evaluate(left, env)
    b = evaluate(right, env)
    return -1 if a < b else (1 if a > b else 0)
