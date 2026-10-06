"""Writing programs in Python.

A program is a Python module that states facts and rules:

    from peye import *

    type, subclass_of = preds('type subclass_of')
    S, A, B, X, Y = vars('S A B X Y')

    fact(type('socrates', 'human'))
    fact(subclass_of('human', 'mortal'))
    forward(type(S, B), type(S, A), subclass_of(A, B))
    query(type(X, Y))

Atoms are strings, numbers are ints and floats, lists are lists, and
``[H, *T]`` is a list with head H and tail T. Each call states one clause, in
source order; ``load`` runs the module and collects them into a Program.
"""
import itertools
import keyword
import os
import re
import sys

from .program import CONTROL_KEYS, RESERVED_KEYS, Program, Source
from .builtins import PRIMITIVE_KEYS
from .terms import PeyeError, Struct, Term, Var, _term
from .writer import RESERVED_CALLS

_builders = []


class Builder:
    """Collects the clauses a program states, in order."""

    def __init__(self):
        self.sources = []
        self.anonymous = itertools.count()

    def add(self, kind, head, body, line=None, file=None):
        if line is None:
            line, file = _caller()
        anonymous = self.anonymous

        def convert(value):
            return _rename_anonymous(_term(value), anonymous)
        head = convert(head)
        body = [convert(goal) for goal in body]
        for goal in body:
            if type(goal) is not Var and type(goal) is not str and type(goal) is not Struct:
                raise PeyeError(f'line {line}: a goal must be an atom, a compound term or a variable, '
                                f'not {goal!r}')
            if type(goal) is Struct and goal.name == '.' and len(goal.args) == 2:
                raise PeyeError(f'line {line}: a list is not a goal')
        self.sources.append(Source(kind, head, body, line, file))


def _rename_anonymous(term, counter):
    """Every _ in a clause is a variable of its own."""
    kind = type(term)
    if kind is Var:
        return Var(f'__anon{next(counter)}') if term.name == '_' else term
    if kind is not Struct:
        return term
    args = tuple(_rename_anonymous(arg, counter) for arg in term.args)
    return term if all(a is b for a, b in zip(args, term.args)) else Struct(term.name, args)


def _caller():
    """The line and file of the program statement that states a clause."""
    frame = sys._getframe(1)
    here = __file__
    while frame is not None and frame.f_code.co_filename == here:
        frame = frame.f_back
    if frame is None:
        return None, None
    return frame.f_lineno, frame.f_code.co_filename


def _builder():
    if _builders:
        return _builders[-1]
    # Outside load(), clauses collect into one builder of their own.
    _builders.append(Builder())
    return _builders[-1]


def _names(spec):
    return spec.replace(',', ' ').split()


def vars(spec):
    """Variables named by a space-separated string: one, or a tuple of several."""
    names = _names(spec)
    for name in names:
        if not name.isidentifier() or keyword.iskeyword(name):
            raise PeyeError(f'{name!r} is not a valid variable name')
    made = tuple(Var(name) for name in names)
    return made[0] if len(made) == 1 else made


_RESERVED_NAMES = frozenset(name for name, _ in PRIMITIVE_KEYS | CONTROL_KEYS | RESERVED_KEYS) | RESERVED_CALLS


class Pred(Term):
    """A predicate name. Calling it builds a goal or a fact; uncalled, it is the atom."""
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __call__(self, *args):
        if not args:
            return self.name
        return Struct(self.name, tuple(_term(arg) for arg in args))

    def __peye_term__(self):
        return self.name

    def __repr__(self):
        return f'Pred({self.name!r})'

    __str__ = __repr__
    __hash__ = object.__hash__


def preds(spec):
    """Predicates named by a space-separated string: one, or a tuple of several."""
    made = []
    for name in _names(spec):
        if not name.isidentifier() or keyword.iskeyword(name):
            raise PeyeError(f'{name!r} is not a valid predicate name')
        if name in _RESERVED_NAMES:
            raise PeyeError(f'{name!r} is a reserved name')
        made.append(Pred(name))
    return made[0] if len(made) == 1 else tuple(made)


def fact(*terms):
    """State facts, one clause each."""
    builder = _builder()
    for term in terms:
        builder.add('fact', term, [])


def forward(head, *body):
    """head is concluded whenever body holds, until nothing new follows.

    head can join several conclusions with &.
    """
    _builder().add('forward', head, list(body))


def backward(head, *body):
    """head holds when body does, decided when a goal asks for it."""
    _builder().add('backward', head, list(body))


def query(*body):
    """Publish every instance of body that holds."""
    _builder().add('forward', 'true', list(body))


def contradiction(*body):
    """Stop with exit code 65 when body holds: an integrity constraint."""
    _builder().add('forward', 'false', list(body))


def _goal(*goals):
    from .terms import conjunction
    return conjunction([_term(goal) for goal in goals])


def _builtin(name, arity):
    def make(*args):
        if len(args) != arity:
            raise PeyeError(f'{name} takes {arity} arguments, got {len(args)}')
        return Struct(name, tuple(_term(arg) for arg in args))
    make.__name__ = name
    return make


# The controls. Conjunction, disjunction and negation are also & | ~.
def call(*goals):
    """Solve the goals as one conjunction."""
    return Struct('call', (_goal(*goals),))


def once(*goals):
    """Solve the goals, committing to their first solution."""
    return Struct('once', (_goal(*goals),))


def not_(*goals):
    """Succeed when the goals have no solution: the same as ~goal."""
    return Struct('~', (_goal(*goals),))


def findall(template, goal, result):
    """result is the list of template for every solution of goal."""
    return Struct('findall', (_term(template), _goal(goal) if not isinstance(goal, list) else _goal(*goal),
                              _term(result)))


unify = _builtin('unify', 2)
not_unify = _builtin('not_unify', 2)
identical = _builtin('identical', 2)
not_identical = _builtin('not_identical', 2)
compare = _builtin('compare', 3)
is_ = _builtin('is_', 2)
eq = _builtin('eq', 2)
ne = _builtin('ne', 2)
is_var = _builtin('is_var', 1)
is_nonvar = _builtin('is_nonvar', 1)
is_ground = _builtin('is_ground', 1)
is_atom = _builtin('is_atom', 1)
is_number = _builtin('is_number', 1)
is_int = _builtin('is_int', 1)
is_float = _builtin('is_float', 1)
is_compound = _builtin('is_compound', 1)
functor = _builtin('functor', 3)
arg = _builtin('arg', 3)
univ = _builtin('univ', 2)
atom_chars = _builtin('atom_chars', 2)
atom_codes = _builtin('atom_codes', 2)
atom_length = _builtin('atom_length', 2)
atom_concat = _builtin('atom_concat', 3)
true = 'true'
fail = 'fail'
false = 'false'
_ = Var('_')


def struct(name, *args):
    """A compound term with any name, written struct('name', Arg, ...)."""
    if not args:
        return name
    return Struct(name, tuple(_term(arg) for arg in args))


def facts_from(path=None, text=None):
    """State every expression of a document as a fact: saved conclusions, a
    proof's claims or a check report become data a program can reason over."""
    from .reader import read_terms
    if text is None:
        with open(path, encoding='utf-8') as handle:
            text = handle.read()
    builder = _builder()
    for term, line in read_terms(text):
        builder.add('fact', term, [], line=line, file=path)


def load(*paths):
    """Run program files, or a Program's sources, into one Program."""
    if len(paths) == 1 and isinstance(paths[0], Program):
        return paths[0]
    if len(paths) == 1 and isinstance(paths[0], (list, tuple)):
        paths = tuple(paths[0])
    builder = Builder()
    _builders.append(builder)
    try:
        for path in paths:
            if path == '-':
                _exec(sys.stdin.read(), '<stdin>')
            else:
                with open(path, encoding='utf-8') as handle:
                    _exec(handle.read(), os.fspath(path))
    finally:
        _builders.pop()
    return Program(builder.sources)


def load_text(source, filename='<program>'):
    """A Program from Python source text."""
    builder = Builder()
    _builders.append(builder)
    try:
        _exec(source, filename)
    finally:
        _builders.pop()
    return Program(builder.sources)


_PROOF = re.compile(r'^step\(', re.MULTILINE)
STAR = re.compile(r'^from peye import \*', re.MULTILINE)
# Python builtins a program can use to compute its clauses. Any other builtin
# name a program uses without defining it, such as type or sum, is taken as a
# predicate; a program can still bind such a name itself.
KEPT_BUILTINS = frozenset({
    'print', 'range', 'len', 'list', 'dict', 'set', 'tuple', 'str', 'enumerate', 'zip', 'sorted',
    'reversed', 'isinstance', 'open', 'repr', 'chr', 'ord', 'iter', 'any', 'all', 'map', 'filter',
})


def implicit_names(source, filename='<program>'):
    """The names a program uses but never defines, which load() supplies.

    A name starting with an uppercase letter or an underscore is a variable,
    any other a predicate. Names peye exports, the KEPT_BUILTINS, the
    capitalized builtins such as ValueError, and names the program binds
    anywhere are left alone.
    """
    import builtins
    import symtable
    from . import __all__ as exported
    table = symtable.symtable(source, filename, 'exec')
    bound = {symbol.get_name() for symbol in table.get_symbols()
             if symbol.is_assigned() or symbol.is_imported() or symbol.is_parameter()}
    used = set()
    pending = [table]
    while pending:
        scope = pending.pop()
        for symbol in scope.get_symbols():
            if symbol.is_referenced() and (scope is table or symbol.is_global()):
                used.add(symbol.get_name())
        pending.extend(scope.get_children())
    names = {}
    for name in sorted(used - bound):
        if name in exported or name in KEPT_BUILTINS or name.startswith('__'):
            continue
        if name[0].isupper() and hasattr(builtins, name):
            continue
        names[name] = Var(name) if name[0].isupper() or name[0] == '_' else Pred(name)
    return names


def _statements_nothing(module, names):
    """A top-level call of an implicit predicate states nothing: a misspelled fact?"""
    import ast
    for statement in module.body:
        value = statement.value if type(statement) is ast.Expr else None
        if (type(value) is ast.Call and type(value.func) is ast.Name and
                isinstance(names.get(value.func.id), Pred)):
            name = value.func.id
            raise PeyeError(f'line {statement.lineno}: {name}(...) on its own states nothing; '
                            f'write fact({name}(...)) to state it, or check the spelling')


def _exec(source, filename):
    import ast
    if _PROOF.search(source) and not STAR.search(source):
        raise PeyeError('this is a proof document, not a program: check it with --check-proof PROOF PROGRAM')
    try:
        module = ast.parse(source, filename)
        names = implicit_names(source, filename)
        code = compile(module, filename, 'exec')
    except SyntaxError as error:
        raise PeyeError(f'line {error.lineno}: {error.msg}') from None
    _statements_nothing(module, names)
    namespace = {'__name__': '__peye__', '__file__': filename, '__builtins__': __builtins__}
    namespace.update(names)
    exec(code, namespace)


def _imports_everything(source, filename):
    """Whether a module states `from peye import *` at its top level."""
    import ast
    return any(type(statement) is ast.ImportFrom and statement.module == 'peye' and
               any(alias.name == '*' for alias in statement.names)
               for statement in ast.parse(source, filename).body)


def run_as_script():
    """Run the __main__ program when it is a peye program being started.

    `python program.py --proof` imports peye from the program's first line;
    the program is then run by peye, with the command line's options, and
    the script ends there.
    """
    main = sys.modules.get('__main__')
    path = getattr(main, '__file__', None)
    spec = getattr(main, '__spec__', None)
    if path is None or (spec is not None and spec.name.startswith('peye')):
        return
    frame = sys._getframe(1)
    while frame is not None and frame.f_globals is not main.__dict__:
        frame = frame.f_back
    if frame is None:
        return
    try:
        with open(path, encoding='utf-8') as handle:
            if not _imports_everything(handle.read(), path):
                return
    except (OSError, SyntaxError, ValueError):
        return
    from .cli import main as cli_main, with_deep_stack
    # This runs while the program's own `import peye` is still in progress,
    # and the program runs again on another thread, whose `from peye import *`
    # would wait for that import to finish. Everything it exports is defined
    # by now, so let it through.
    package = sys.modules[__package__]
    if getattr(package.__spec__, '_initializing', False):
        package.__spec__._initializing = False
    code = with_deep_stack(cli_main, [path, *sys.argv[1:]])
    sys.stdout.flush()
    sys.exit(code)


def build(statements):
    """A Program from a function that states clauses when called."""
    builder = Builder()
    _builders.append(builder)
    try:
        statements()
    finally:
        _builders.pop()
    return Program(builder.sources)
