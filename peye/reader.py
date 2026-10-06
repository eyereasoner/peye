"""Reading terms back from Python source, without executing it.

Conclusions, proofs and check reports are written as Python expressions, one
statement each (writer.py). This module parses such text with ``ast`` and
builds the terms it spells, so a proof document is data for the checker and
never code that runs: only literals, names, calls of a plain name, list
displays, dictionary displays of bindings and the operators of writer.py are
accepted.
"""
import ast
import keyword
import re

from .terms import EMPTY, PeyeError, Struct, Var

BINARY = {
    ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.FloorDiv: '//',
    ast.Mod: '%', ast.Pow: '**', ast.LShift: '<<', ast.RShift: '>>', ast.BitXor: '^',
    ast.BitAnd: ',', ast.BitOr: ';',
}
UNARY = {ast.USub: '-', ast.UAdd: '+', ast.Invert: '~'}
COMPARE = {ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>='}


class Reader:
    def __init__(self):
        self.anonymous = 0

    def term(self, node):
        # Long lists and deep expressions are read without host recursion.
        return _Build(self).run(node)


class _Build:
    def __init__(self, reader):
        self.reader = reader

    def run(self, root):
        # Post-order over the syntax tree: each node is visited once to push
        # its children and once to combine their terms.
        values = []
        stack = [(root, None)]
        while stack:
            node, count = stack.pop()
            if count is None:
                children = self.children(node)
                stack.append((node, len(children)))
                for child in reversed(children):
                    stack.append((child, None))
            else:
                args = values[len(values) - count:] if count else []
                if count:
                    del values[len(values) - count:]
                values.append(self.combine(node, args))
        return values[0]

    def children(self, node):
        kind = type(node)
        if kind is ast.Constant or kind is ast.Name:
            return []
        if kind is ast.UnaryOp:
            if type(node.op) is ast.USub and _numeric(node.operand):
                return []
            return [node.operand]
        if kind is ast.BinOp:
            return [node.left, node.right]
        if kind is ast.Compare:
            if len(node.ops) != 1:
                raise PeyeError(f'line {node.lineno}: chained comparison; parenthesize each comparison')
            return [node.left, node.comparators[0]]
        if kind is ast.Call:
            if type(node.func) is not ast.Name or node.keywords:
                raise PeyeError(f'line {node.lineno}: only calls of a plain name build terms')
            if any(type(arg) is ast.Starred for arg in node.args):
                raise PeyeError(f'line {node.lineno}: starred call arguments are not terms')
            return list(node.args)
        if kind is ast.List:
            return [item.value if type(item) is ast.Starred else item for item in node.elts]
        if kind is ast.Dict:
            if any(k is None for k in node.keys):
                raise PeyeError(f'line {node.lineno}: ** in a dictionary is not a binding')
            return [item for pair in zip(node.keys, node.values) for item in pair]
        raise PeyeError(f'line {getattr(node, "lineno", "?")}: {type(node).__name__} is not a term')

    def combine(self, node, args):
        kind = type(node)
        if kind is ast.Constant:
            value = node.value
            if type(value) in (str, int, float):
                return value
            raise PeyeError(f'line {node.lineno}: {value!r} is not a term')
        if kind is ast.Name:
            if node.id == '_':
                self.reader.anonymous += 1
                return Var(f'__anon{self.reader.anonymous - 1}')
            return Var(node.id)
        if kind is ast.UnaryOp:
            if not args:
                return -node.operand.value
            return Struct(UNARY[type(node.op)], (args[0],)) if type(node.op) in UNARY else _bad(node)
        if kind is ast.BinOp:
            name = BINARY.get(type(node.op))
            return Struct(name, (args[0], args[1])) if name else _bad(node)
        if kind is ast.Compare:
            name = COMPARE.get(type(node.ops[0]))
            if name is None:
                raise PeyeError(f'line {node.lineno}: only <, <=, > and >= compare; '
                                'write eq(X, Y) or unify(X, Y) for equality')
            return Struct(name, (args[0], args[1]))
        if kind is ast.Call:
            name = node.func.id
            if name == 'struct':
                if not args or type(args[0]) is not str:
                    raise PeyeError(f'line {node.lineno}: struct() needs a name string first')
                return Struct(args[0], tuple(args[1:])) if len(args) > 1 else args[0]
            return Struct(name, tuple(args)) if args else name
        if kind is ast.List:
            tail = EMPTY
            items = args
            starred = [i for i, item in enumerate(node.elts) if type(item) is ast.Starred]
            if starred:
                if starred != [len(node.elts) - 1]:
                    raise PeyeError(f'line {node.lineno}: only the last list item can be starred')
                tail = args[-1]
                items = args[:-1]
            result = tail
            for item in reversed(items):
                result = Struct('.', (item, result))
            return result
        if kind is ast.Dict:
            # Bindings: {'X': Value, ...} reads as a list of '='(Name, Value).
            pairs = [Struct('=', (args[i], args[i + 1])) for i in range(0, len(args), 2)]
            result = EMPTY
            for pair in reversed(pairs):
                result = Struct('.', (pair, result))
            return result
        return _bad(node)


def _numeric(node):
    return type(node) is ast.Constant and type(node.value) in (int, float)


def _bad(node):
    raise PeyeError(f'line {getattr(node, "lineno", "?")}: {type(node).__name__} is not a term')


def _parse(text, mode):
    try:
        return ast.parse(text, mode=mode)
    except SyntaxError as error:
        raise PeyeError(f'syntax error on line {error.lineno}: {error.msg}') from None


def read_term(text):
    """One term, such as a goal given on the command line."""
    return Reader().term(_parse(text.strip(), 'eval').body)


def read_terms(text):
    """The terms of a document, one expression statement each, with their lines."""
    fast = _read_lines(text)
    if fast is not None:
        return fast
    module = _parse(text, 'exec')
    reader = Reader()
    out = []
    for statement in module.body:
        if type(statement) is not ast.Expr:
            raise PeyeError(f'line {statement.lineno}: a document holds expressions only, '
                            f'not {type(statement).__name__}')
        out.append((reader.term(statement.value), statement.lineno))
    return out


# Documents peye writes put one expression on each line. Such a line is read
# directly, with Python's grammar for the expressions peye writes: names,
# calls, plain string literals, numbers, lists, binding dictionaries and the
# operators of writer.py, with Python's precedence. That is several times
# faster than building Python syntax trees. A document with anything else on
# any line, an escape, a comment, a tuple, a statement over several lines, is
# read with ast as a whole, so both readings give the same terms.
_TOKEN = re.compile(r"""
    [ \t]*(?:
      (?P<string>'[^'\\\n]*'|"[^"\\\n]*")
    | (?P<float>[0-9]+\.[0-9]+(?:e[+-][0-9]+)?|[0-9]e[+-][0-9]+)
    | (?P<int>0|[1-9][0-9]*)
    | (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    | (?P<op>\*\*|//|<<|>>|<=|>=|[-+*/%&|^~<>])
    | (?P<punct>[()\[\]{},:])
    )""", re.VERBOSE)
_KEYWORDS = frozenset(keyword.kwlist)
# Binary operators: their precedence, tighter higher, and the term they build.
# All are left associative.
_BINARY = {
    '|': (1, ';'), '^': (2, '^'), '&': (3, ','), '<<': (4, '<<'), '>>': (4, '>>'),
    '+': (5, '+'), '-': (5, '-'), '*': (6, '*'), '/': (6, '/'), '//': (6, '//'), '%': (6, '%'),
}
_COMPARE = frozenset({'<', '<=', '>', '>='})
_UNARY = {'-': '-', '+': '+', '~': '~'}


class _NotSimple(Exception):
    """The line needs the full reader."""


def _read_lines(text):
    reader = Reader()
    out = []
    try:
        for number, line in enumerate(text.split('\n'), 1):
            if not line.strip():
                continue
            if line[0] in ' \t':
                raise _NotSimple  # Python reads an indented line as an error
            tokens = []
            position = 0
            end = len(line.rstrip())
            while position < end:
                match = _TOKEN.match(line, position)
                if match is None:
                    raise _NotSimple
                tokens.append(match.group(match.lastgroup))
                tokens.append(match.lastgroup)
                position = match.end()
            parser = _Line(tokens, reader)
            term = parser.expression()
            if parser.index != len(tokens):
                raise _NotSimple
            out.append((term, number))
    except (_NotSimple, RecursionError):
        return None
    return out


class _Line:
    """Recursive descent over one line's tokens, as flat (text, kind) pairs."""

    def __init__(self, tokens, reader):
        self.tokens = tokens
        self.index = 0
        self.reader = reader

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self, value=None):
        if self.index >= len(self.tokens):
            raise _NotSimple
        text = self.tokens[self.index]
        kind = self.tokens[self.index + 1]
        if value is not None and (text != value or kind == 'string'):
            raise _NotSimple
        self.index += 2
        return text, kind

    def operator(self):
        if self.index < len(self.tokens) and self.tokens[self.index + 1] == 'op':
            return self.tokens[self.index]
        return None

    def expression(self):
        left = self.binary(1)
        op = self.operator()
        if op in _COMPARE:
            self.take()
            right = self.binary(1)
            if self.operator() in _COMPARE:
                raise _NotSimple  # a chained comparison
            return Struct(op, (left, right))
        return left

    def binary(self, minimum):
        """Precedence climbing over the binary operators from minimum up."""
        left = self.unary()[0]
        while True:
            op = self.operator()
            entry = _BINARY.get(op)
            if entry is None or entry[0] < minimum:
                return left
            self.take()
            left = Struct(entry[1], (left, self.binary(entry[0] + 1)))

    def unary(self):
        """A term, and whether it is a bare number literal, which a minus
        applied to it turns into a negative number, as the ast reader does."""
        op = self.operator()
        if op in _UNARY:
            self.take()
            operand, literal = self.unary()
            if op == '-' and literal:
                return -operand, False
            return Struct(_UNARY[op], (operand,)), False
        base, literal = self.primary()
        if self.operator() == '**':
            self.take()
            return Struct('**', (base, self.unary()[0])), False
        return base, literal

    def primary(self):
        text, kind = self.take()
        if kind == 'string':
            return text[1:-1], False
        if kind == 'int':
            return int(text), True
        if kind == 'float':
            return float(text), True
        if kind == 'name':
            if text in _KEYWORDS:
                raise _NotSimple
            if self.peek() != '(' or self.tokens[self.index + 1] != 'punct':
                if text == '_':
                    self.reader.anonymous += 1
                    return Var(f'__anon{self.reader.anonymous - 1}'), False
                return Var(text), False
            self.take('(')
            args = self.sequence(')')
            if text == 'struct':
                if not args or type(args[0]) is not str:
                    raise _NotSimple
                return (Struct(args[0], tuple(args[1:])) if len(args) > 1 else args[0]), False
            return (Struct(text, tuple(args)) if args else text), False
        if kind != 'punct':
            raise _NotSimple
        if text == '(':
            start = self.index
            term = self.expression()
            # Parentheses around a number literal, (2) or ((2)), keep it one.
            literal = (type(term) is int or type(term) is float) and self._only_literal(start, self.index)
            self.take(')')
            return term, literal
        if text == '[':
            items = []
            tail = EMPTY
            while self.peek() != ']':
                if self.operator() == '*':
                    self.take()
                    tail = self.binary(1)
                    break
                items.append(self.expression())
                if self.peek() != ']':
                    self.take(',')
                    if self.peek() == ']':
                        raise _NotSimple
            self.take(']')
            result = tail
            for item in reversed(items):
                result = Struct('.', (item, result))
            return result, False
        if text == '{':
            pairs = []
            while self.peek() != '}':
                key = self.expression()
                self.take(':')
                pairs.append(Struct('=', (key, self.expression())))
                if self.peek() != '}':
                    self.take(',')
                    if self.peek() == '}':
                        raise _NotSimple
            self.take('}')
            result = EMPTY
            for pair in reversed(pairs):
                result = Struct('.', (pair, result))
            return result, False
        raise _NotSimple

    def _only_literal(self, start, end):
        """Whether tokens[start:end] are one number literal in parentheses."""
        kinds = [self.tokens[i + 1] for i in range(start, end, 2)]
        texts = [self.tokens[i] for i in range(start, end, 2)]
        numbers = [kind for kind in kinds if kind in ('int', 'float')]
        return len(numbers) == 1 and all(kind in ('int', 'float') or text in '()'
                                         for kind, text in zip(kinds, texts))

    def sequence(self, close):
        args = []
        while self.peek() != close:
            args.append(self.expression())
            if self.peek() != close:
                self.take(',')
                if self.peek() == close:
                    raise _NotSimple
        self.take(close)
        return args
