"""Reading terms back from Python source, without executing it.

Conclusions, proofs and check reports are written as Python expressions, one
statement each (writer.py). This module parses such text with ``ast`` and
builds the terms it spells, so a proof document is data for the checker and
never code that runs: only literals, names, calls of a plain name, list
displays, dictionary displays of bindings and the operators of writer.py are
accepted.
"""
import ast

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
        stack = [(root, False)]
        while stack:
            node, ready = stack.pop()
            if not ready:
                children = self.children(node)
                stack.append((node, True))
                for child in reversed(children):
                    stack.append((child, False))
            else:
                count = len(self.children(node))
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
    module = _parse(text, 'exec')
    reader = Reader()
    out = []
    for statement in module.body:
        if type(statement) is not ast.Expr:
            raise PeyeError(f'line {statement.lineno}: a document holds expressions only, '
                            f'not {type(statement).__name__}')
        out.append((reader.term(statement.value), statement.lineno))
    return out
