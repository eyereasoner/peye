"""Every term has one Python spelling, and reading it back gives the term."""
import glob
import os
import unittest

from peye import PeyeError, Struct, Var, read_term, read_terms, write
from peye.terms import list_from_items

from helpers import ROOT

CASES = [
    "'socrates'", "[]", "0", "-7", "123456789012345678901234567890", "0.1", "-2.5e-07", "1e+22",
    "X", "_G1", "f(X, 'a', [1, 2.0, *T])", "['a', *'b']", "struct('hello world', 1)",
    "struct('from', X)", "struct('struct', 1)", "struct('-', 1)", "struct('-', -1)", "-X", "+X", "~X",
    "--X", "X - -1", "-1 - X", "(-2) ** 2", "-2 ** 2", "2 ** 3 ** 2", "(2 ** 3) ** 2", "2 ** -1",
    "X + Y * Z", "(X + Y) * Z", "X - (Y - Z)", "X - Y - Z", "X // Y % Z", "X << 1 >> 2", "X ^ Y & Z",
    "(X ^ Y) & Z", "X | Y | Z", "X | (Y | Z)", "X & Y | Z", "X & (Y | Z)", "X < Y", "(X < Y) & (Y <= Z)",
    "(X < Y) < Z", "X + 1 >= Y", "~(X & Y)", "~X & Y", "f(X < Y, [X > Y])", "\"it's\"", "'say \"hi\"'",
    "'\\n\\t\\\\'", "'😀'", "struct('[]')", "struct('{}', X)", "eq(X, 1)", "is_(X, Y + 1)",
    "[*X]" ,
]


def ast_terms(text):
    """read_terms without its direct reading of simple lines."""
    from peye import reader
    saved = reader._read_lines
    reader._read_lines = lambda text: None
    try:
        return read_terms(text)
    finally:
        reader._read_lines = saved


class Syntax(unittest.TestCase):
    def test_edge_cases_round_trip(self):
        for text in CASES:
            with self.subTest(text):
                term = read_term(text)
                written = write(term)
                self.assertEqual(write(read_term(written)), written)

    def test_spellings_are_canonical(self):
        self.assertEqual(write(read_term("'it\\'s'")), '"it\'s"')
        self.assertEqual(write(read_term('(X)')), 'X')
        self.assertEqual(write(read_term('2 ** 3 ** 2')), '2 ** 3 ** 2')
        self.assertEqual(write(read_term('(2 ** 3) ** 2')), '(2 ** 3) ** 2')
        self.assertEqual(write(read_term('X - (Y - Z)')), 'X - (Y - Z)')
        self.assertEqual(write(Struct('-', (1,))), "struct('-', 1)")
        self.assertEqual(write(Struct('-', (Var('X'),))), '-X')
        self.assertEqual(write(read_term('[*X]')), 'X')
        self.assertEqual(write(list_from_items([1, 2], Var('T'))), '[1, 2, *T]')
        self.assertEqual(write(Struct('-', (Struct('**', (2, 2)),))), '-2 ** 2')
        self.assertEqual(write(Struct('**', (-2, 2))), '(-2) ** 2')

    def test_anonymous_variables_are_distinct(self):
        term = read_term('f(_, _)')
        self.assertNotEqual(term.args[0].name, term.args[1].name)

    def test_only_term_syntax_is_read(self):
        for text in ["os.system('x')", "f(x=1)", "f(*X)", "(1, 2)", "{1, 2}", "lambda: 1", "X == Y",
                     "1 < 2 < 3", "[*X, 1]", "None", "True", "f()()", "X @ Y", "not X", "{**X}",
                     "f'{X}'", "b'x'", "1j"]:
            with self.subTest(text), self.assertRaises(PeyeError):
                read_term(text)
        with self.assertRaises(PeyeError):
            read_terms('x = 1\n')
        with self.assertRaises(PeyeError):
            read_terms('import os\n')

    def test_the_direct_reading_agrees_with_ast_on_every_saved_document(self):
        from peye.reader import _read_lines
        for path in sorted(glob.glob(os.path.join(ROOT, 'examples', '*', '*.py'))):
            with self.subTest(os.path.relpath(path, ROOT)), open(path, encoding='utf-8') as handle:
                text = handle.read()
                direct = _read_lines(text)
                expected = ast_terms(text)
                if direct is None:
                    continue  # read with ast as a whole
                self.assertEqual([(write(t), n) for t, n in direct], [(write(t), n) for t, n in expected])

    def test_the_direct_reading_agrees_with_ast_or_steps_aside(self):
        from peye.reader import _read_lines
        cases = CASES + [
            "f('a', \"b\", 1, -2, 0.5, -1.5e-07, 1e+22, [], [X, *Y], {'X': 1, 'Y': g(Z)})",
            "struct('hello world', 1)", "struct('x')", "p()", "_", "f(_, _)", "-0", "-0.0",
            "f('\U0001F600', 'ä')", "f(\"it's\")",
            # Each of these needs the full reader, which accepts it or rejects it.
            "f(a,)", "'a' 'b'", "f(x) # comment", "  f(x)", "f(\n x)", "007", "1_000",
            "f(True)", "b'x'", "f(*X)", "[*X, 1]", "x; y", "struct()", "f(é)", "f(x=1)",
            "f(X) g(Y)", "[1 2]", "{1}", "f('a\\nb')",
            # Operators and literals, where precedence and the folding of a
            # minus into a negative number must come out as Python reads them.
            "-(2)", "-(2) ** 2", "-(2 ** 2)", "+1", "~-1", "-(-1)", "--1", "-+1", "(X)", "(1, 2)",
            "[*X < 1]", "f(-(1))", "- 1", "1 -1", "2**2", "a<b", "1 < 2 < 3", "X == Y", "X @ Y",
            "-X ** -Y ** 2", "(-X) ** 2", "~X ** 2", "X - Y - Z", "X - (Y - Z)", "X | Y & Z ^ W",
            "(X | Y) & Z", "X << 1 + 2", "X * -Y", "-1.5", "-1e+22", "f(*[1])", "[*(X | Y)]",
            "f(X)(Y)", "{X: Y < 1}", "(X)(1)", "((1))", "-((1))",
        ]
        for text in cases:
            with self.subTest(text):
                direct = _read_lines(text)
                try:
                    expected = [(write(t), n) for t, n in ast_terms(text)]
                except PeyeError:
                    expected = None
                if direct is not None:
                    self.assertEqual([(write(t), n) for t, n in direct], expected)

    def test_every_saved_document_reads_back_to_its_own_spelling(self):
        for path in sorted(glob.glob(os.path.join(ROOT, 'examples', '*', '*.py'))):
            with self.subTest(os.path.relpath(path, ROOT)), open(path, encoding='utf-8') as handle:
                lines = [line for line in handle.read().split('\n') if line]
                for line, (term, _) in zip(lines, read_terms('\n'.join(lines))):
                    if line.startswith('step('):
                        continue  # bindings are written as a dictionary
                    self.assertEqual(write(term), line)


if __name__ == '__main__':
    unittest.main()
