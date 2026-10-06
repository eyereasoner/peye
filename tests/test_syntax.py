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
