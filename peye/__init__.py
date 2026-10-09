"""peye: reasoning you can see, in Python.

Facts and rules are Python. Forward rules materialize conclusions until a
fixpoint, backward rules are decided when a goal asks for them, and every
answer can come with a proof that a separate checker verifies against the
program, condition by condition (C1-C7).
"""

from .dsl import (
    _, arg, atom_chars, atom_codes, atom_concat, atom_length, call, compare,
    contradiction, eq, fact, facts_from, fail, false, findall, functor, identical, implied_by, implies, is_,
    is_atom, is_compound, is_float, is_ground, is_int, is_nonvar, is_number, is_var, load,
    load_text, ne, not_, not_identical, not_unify, once, preds, build, query, struct, true,
    unify, univ, vars,
)
from .engine import Result, run, unused_clauses
from .program import Program
from .proof import check_proof, check_report, public_report, verdict_text
from .reader import read_term, read_terms
from .terms import PeyeError, Struct, Var
from .writer import write

__version__ = '0.4.5'

# What `from peye import *` gives a program: the names it states clauses
# with. The library API (load, run, check_proof, ...) is imported by name.
__all__ = [
    # Stating a program.
    'preds', 'vars', '_', 'fact', 'facts_from', 'implies', 'implied_by', 'query', 'contradiction',
    'struct',
    # Controls.
    'call', 'once', 'not_', 'findall',
    # Primitives.
    'true', 'fail', 'false', 'unify', 'not_unify', 'identical', 'not_identical', 'compare',
    'is_', 'eq', 'ne', 'is_var', 'is_nonvar', 'is_ground', 'is_atom', 'is_number', 'is_int',
    'is_float', 'is_compound', 'functor', 'arg', 'univ', 'atom_chars', 'atom_codes',
    'atom_length', 'atom_concat',
]

from .dsl import run_as_script  # noqa: E402

run_as_script()
