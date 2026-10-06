"""Arithmetic functions for rule programs.

Each name here is both the Python function and the arithmetic term it stands
for: on numbers it computes at once, as the builtin or math function does,
and on anything else it builds the term that is_(), the comparisons and eq()
evaluate. Import the ones a program uses, by name:

    from peye.functions import sqrt, floor, max
"""
import builtins
import math

from .arith import CONSTANTS, FUNCTIONS
from .terms import Struct, _term

# This module rebinds int and float to their lifted versions below.
_NUMBERS = (builtins.int, builtins.float)


def _lift(name, fn):
    def lifted(*args):
        if all(type(arg) in _NUMBERS for arg in args):
            return fn(*args)
        return Struct(name, tuple(_term(arg) for arg in args))
    lifted.__name__ = name
    lifted.__qualname__ = name
    lifted.__doc__ = f'{name} on numbers, or the arithmetic term {name}(...) on anything else.'
    return lifted


for _name, _fn in FUNCTIONS.items():
    globals()[_name] = _lift(_name, getattr(builtins, _name, None) or _fn)
pi = CONSTANTS['pi']
e = CONSTANTS['e']
tau = CONSTANTS['tau']

__all__ = sorted([*FUNCTIONS, 'pi', 'e', 'tau'])
