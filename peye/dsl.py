"""Writing programs in Python.

A program is a Python module that states facts and rules:

    from peye import *

    fact(type('socrates', 'human'))
    fact(subclass_of('human', 'mortal'))
    implies(type(S, A) & subclass_of(A, B), type(S, B))
    query(type(X, Y))

Atoms are strings, numbers are ints and floats, lists are lists, and
``[H, *T]`` is a list with head H and tail T. Each call states one clause, in
source order; ``load`` runs the module and collects them into a Program.
"""
import keyword
import os
import re
import sys

from .program import CONTROL_KEYS, RESERVED_KEYS, Program, Source
from .builtins import PRIMITIVE_KEYS
from .terms import PeyeError, Struct, Term, Var, _term, unlimited_digits
from .writer import RESERVED_CALLS

_builders = []


class Builder:
    """Collects the clauses a program states, in order."""

    def __init__(self):
        self.sources = []
        # Where each clause was stated, as (code, offset) until finish().
        self.places = []
        # Whether a statement may hold a _ to rename; a program whose source
        # cannot reach _ spares every clause that search.
        self.anonymous = True

    def add(self, kind, head, body, line=None, file=None):
        place = None
        if line is None:
            place = _caller()
        head = _term(head)
        body = [_term(goal) for goal in body]
        if self.anonymous:
            anonymous = _Anonymous([head, *body])
            # In the order the statement writes them: a forward rule, implies(),
            # writes its premise first.
            if kind != 'backward':
                body = [_rename_anonymous(goal, anonymous) for goal in body]
                head = _rename_anonymous(head, anonymous)
            else:
                head = _rename_anonymous(head, anonymous)
                body = [_rename_anonymous(goal, anonymous) for goal in body]
        for goal in body:
            if type(goal) is not Var and type(goal) is not str and type(goal) is not Struct:
                raise PeyeError(f'line {_line_now()}: a goal must be an atom, a compound term or a '
                                f'variable, not {goal!r}')
            if type(goal) is Struct and goal.name == '.' and len(goal.args) == 2:
                raise PeyeError(f'line {_line_now()}: a list is not a goal')
        self.sources.append(Source(kind, head, body, line, file))
        self.places.append(place)

    def finish(self):
        """The sources, with the line each was stated on."""
        # By identity: hashing a code object hashes all of its bytecode.
        lines = {}
        for source, place in zip(self.sources, self.places):
            if place is None:
                continue
            code, offset = place
            table = lines.get(id(code))
            if table is None:
                table = lines[id(code)] = _line_table(code)
            source.line = _line_at(table, offset)
            source.file = code.co_filename
        self.places = [None] * len(self.sources)
        return self.sources


class _Anonymous:
    """Names for the _ of one clause: _0, _1, ..., skipping names the clause
    already uses, which are looked up only once a _ is met."""

    def __init__(self, terms):
        self.terms = terms
        self.used = None
        self.count = 0

    def __next__(self):
        if self.used is None:
            self.used = set()
            pending = list(self.terms)
            while pending:
                term = pending.pop()
                if type(term) is Var:
                    self.used.add(term.name)
                elif type(term) is Struct:
                    pending.extend(term.args)
        while True:
            name = f'_{self.count}'
            self.count += 1
            if name not in self.used:
                return name


def _rename_anonymous(term, counter):
    """Every _ in a clause is a variable of its own. A term without one is
    returned as it is."""
    kind = type(term)
    if kind is Var:
        return Var(next(counter)) if term.name == '_' else term
    if kind is not Struct:
        return term
    args = None
    for index, arg in enumerate(term.args):
        kind = type(arg)
        if kind is Struct or (kind is Var and arg.name == '_'):
            renamed = _rename_anonymous(arg, counter)
            if renamed is not arg:
                if args is None:
                    args = list(term.args)
                args[index] = renamed
    return term if args is None else Struct(term.name, tuple(args))


def _program_frame():
    frame = sys._getframe(2)
    here = __file__
    while frame is not None and frame.f_code.co_filename == here:
        frame = frame.f_back
    return frame


def _caller():
    """Where the program statement that states a clause is: its code and the
    offset of the instruction running in it. Asking a frame for its line
    number scans the code's line table from the start, which makes a long
    program cost quadratic time, so lines are resolved once, by finish()."""
    frame = _program_frame()
    return None if frame is None else (frame.f_code, frame.f_lasti)


def _line_now():
    """The line of the program statement running now, for an error."""
    frame = _program_frame()
    return None if frame is None else frame.f_lineno


def _line_table(code):
    """(offsets, lines): the first instruction offset of each line run."""
    if hasattr(code, 'co_lines'):
        runs = [(start, line) for start, _, line in code.co_lines() if line is not None]
    else:
        import dis
        runs = list(dis.findlinestarts(code))
    return [start for start, _ in runs], [line for _, line in runs]


def _line_at(table, offset):
    import bisect
    offsets, lines = table
    index = bisect.bisect_right(offsets, offset) - 1
    return lines[index] if index >= 0 else None


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


def implies(premise, conclusion):
    """A forward rule: whenever premise holds, conclude conclusion,
    until nothing new follows. Both may join several goals with &."""
    _builder().add('forward', conclusion, [premise])


def implied_by(conclusion, premise):
    """A backward rule: conclusion holds when premise does, decided
    when a goal asks for it. premise may join several goals with &."""
    _builder().add('backward', conclusion, [premise])


def query(*body):
    """Publish every instance of body that holds."""
    _builder().add('query', 'true', list(body))


def contradiction(*body):
    """Stop with exit code 65 when body holds: an integrity constraint."""
    _builder().add('contradiction', 'false', list(body))


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
    # Each fact is stated by this call, so it records the call's line, as
    # every clause records the line of the statement that states it.
    builder = _builder()
    try:
        terms = read_terms(text)
    except PeyeError as error:
        # The document's own line, named so it is not taken for the program's.
        raise PeyeError(f"{path if path is not None else 'the text'}: {error}") from None
    for term, _line in terms:
        builder.add('fact', term, [])


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
    return Program(builder.finish())


def load_text(source, filename='<program>'):
    """A Program from Python source text."""
    builder = Builder()
    _builders.append(builder)
    try:
        _exec(source, filename)
    finally:
        _builders.pop()
    return Program(builder.finish())


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
    any other a predicate. Names peye exports, names starting with __, and
    names the program binds anywhere are left alone. So is the name of a
    Python builtin, unless the program uses it inside a peye statement, as
    in fact(type('socrates', 'human')), where it is a predicate; even there
    the KEPT_BUILTINS and the capitalized builtins keep their meaning.
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
    undefined = sorted(name for name in used - bound if name not in exported and not name.startswith('__'))
    shadowing = {name for name in undefined if hasattr(builtins, name)}
    in_statements = _names_in_statements(source, filename, exported, shadowing) if shadowing else set()
    names = {}
    for name in undefined:
        if hasattr(builtins, name) and (name not in in_statements or name in KEPT_BUILTINS
                                        or name[0].isupper()):
            continue
        names[name] = Var(name) if name[0].isupper() or name[0] == '_' else Pred(name)
    return names


def _names_in_statements(source, filename, exported, wanted):
    """Which of the wanted names are used anywhere inside the arguments of a
    call of a name peye exports, such as fact(...), implies(...) or findall(...).

    A syntax tree of a long program is slow to build, so the source is
    scanned token by token instead; a construct the scan does not model, an
    f-string or a lambda, sends it to the syntax tree after all.
    """
    found = _scan_names_in_statements(source, exported, wanted)
    if found is None:
        found = _ast_names_in_statements(source, filename, exported) & wanted
    return found


_SCAN = re.compile(r'''
    (?P<fstring>(?:[rR][fFtT]|[fFtT][rR]?)['"])
  | (?:[rRbBuU]|[rR][bB]|[bB][rR])?(?:\'\'\'(?:[^\\]|\\.)*?\'\'\'|"""(?:[^\\]|\\.)*?"""
                                      |'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")
  | \#[^\n]*
  | (?P<open>[(\[{]) | (?P<close>[)\]}])
  | (?P<dot>\.\s*)?(?P<name>[^\W\d]\w*)(?P<after>[ \t]*(?:\(|=(?!=)))?
''', re.VERBOSE | re.DOTALL)


def _scan_names_in_statements(source, exported, wanted):
    """_names_in_statements by scanning tokens, or None when the source has a
    construct the scan does not model. Only called on source that compiles."""
    found = set()
    inside = [False]  # per open bracket: whether it lies in a statement's arguments
    for match in _SCAN.finditer(source):
        kind = match.lastgroup
        if kind == 'name' or kind == 'after':
            name = match.group('name')
            if name == 'lambda':
                return None
            if match.group('dot'):
                after = match.group('after')
                if after and after.endswith('('):
                    inside.append(inside[-1])
                continue
            after = match.group('after')
            if after and after.endswith('='):
                continue  # a keyword argument
            if inside[-1] and name in wanted:
                found.add(name)
            if after:
                inside.append(inside[-1] or name in exported)
        elif kind == 'open':
            inside.append(inside[-1])
        elif kind == 'close':
            if len(inside) > 1:
                inside.pop()
        elif kind == 'fstring':
            return None
    return found


def _ast_names_in_statements(source, filename, exported):
    import ast
    found = set()
    for node in ast.walk(ast.parse(source, filename)):
        if type(node) is ast.Call and type(node.func) is ast.Name and node.func.id in exported:
            for argument in [*node.args, *(keyword.value for keyword in node.keywords)]:
                for inner in ast.walk(argument):
                    if type(inner) is ast.Name:
                        found.add(inner.id)
    return found


def _statements_nothing(source, filename, names):
    """A top-level call of an implicit predicate states nothing: a misspelled fact?

    Parsing a long program into a syntax tree is slow, so only a program with
    a line that starts with such a call is parsed to look closer.
    """
    import ast
    suspects = {match.group(1) for match in _LEADING_CALL.finditer(source)}
    renamed = {match.group(1) for match in _RENAMED_CALL.finditer(source)}
    if not any(isinstance(names.get(name), Pred) for name in suspects | renamed):
        return
    tree = ast.parse(source, filename)
    # A statement of an earlier version states nothing wherever it is, as
    # inside a function that states a program's rules.
    for node in ast.walk(tree):
        if (type(node) is ast.Expr and type(node.value) is ast.Call and type(node.value.func) is ast.Name
                and node.value.func.id in _RENAMED and isinstance(names.get(node.value.func.id), Pred)):
            name = node.value.func.id
            raise PeyeError(f'line {node.lineno}: {name}(Head, *Body) is now {_RENAMED[name]}')
    for statement in tree.body:
        value = statement.value if type(statement) is ast.Expr else None
        if (type(value) is ast.Call and type(value.func) is ast.Name and
                isinstance(names.get(value.func.id), Pred)):
            name = value.func.id
            raise PeyeError(f'line {statement.lineno}: {name}(...) on its own states nothing; '
                            f'write fact({name}(...)) to state it, or check the spelling')


# Statements of earlier versions, and what states the same clause now.
_RENAMED = {'forward': 'implies(Premise, Conclusion), premise first',
            'backward': 'implied_by(Conclusion, Premise)'}

_MAY_REACH_ANONYMOUS = re.compile(r'(?<![\w.])_(?!\w)|^[ \t]*import\b|^[ \t]*from\b(?! peye import \*)',
                                  re.MULTILINE)
_RENAMED_CALL = re.compile(r'^[ \t]*(forward|backward)[ \t]*\(', re.MULTILINE)
_LEADING_CALL = re.compile(r'^([^\W\d]\w*)[ \t]*\(', re.MULTILINE)


def _exec(source, filename):
    # A program's source may spell integers longer than Python parses by default.
    with unlimited_digits():
        _exec_program(source, filename)


def _exec_program(source, filename):
    if _PROOF.search(source) and not STAR.search(source):
        raise PeyeError('this is a proof document, not a program: check it with --check-proof PROOF PROGRAM')
    try:
        code = compile(source, filename, 'exec')
        names = implicit_names(source, filename)
    except SyntaxError as error:
        where = f'line {error.lineno}: ' if error.lineno else ''
        raise PeyeError(f'{where}{error.msg}') from None
    except ValueError as error:  # before Python 3.12, a null character
        raise PeyeError(str(error)) from None
    _statements_nothing(source, filename, names)
    builder = _builders[-1] if _builders else None
    if builder is not None:
        # Only a source that names _ or imports other code can state a _.
        builder.anonymous = bool(_MAY_REACH_ANONYMOUS.search(source))
    namespace = {'__name__': '__peye__', '__file__': filename, '__builtins__': __builtins__}
    namespace.update(names)
    try:
        exec(code, namespace)
    except Exception as error:
        if builder is not None:
            builder.anonymous = True
        # An error is reported at the line of the program that raised it,
        # unless it already names one.
        import traceback
        lines = [frame.lineno for frame in traceback.extract_tb(error.__traceback__)
                 if frame.filename == filename]
        where = f'line {lines[-1]}: ' if lines else ''
        if isinstance(error, PeyeError):
            if str(error).startswith('line ') or not where:
                raise
            raise PeyeError(f'{where}{error}') from None
        raise PeyeError(f'{where}{type(error).__name__}: {error}') from None
    if builder is not None:
        builder.anonymous = True


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
    return Program(builder.finish())
