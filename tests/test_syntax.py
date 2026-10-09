"""Every term has one Python spelling, and reading it back gives the term."""
import functools
import glob
import os
import re
import unittest

from peye import PeyeError, Struct, Var, load_text, read_term, read_terms, run, write
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


def _shape(line):
    """A line with its atoms, numbers (all but their order of length) and
    repetitions collapsed: lines of one shape exercise a reader in the same way."""
    line = re.sub(r"'[^'\\\n]*'", "'a'", line)
    line = re.sub(r'"[^"\\\n]*"', '"a"', line)
    line = re.sub(r'\d+', lambda number: '0' * len(number.group()).bit_length(), line)
    line = re.sub(r'(\w+\()\1+', r'\1\1', line)
    line = re.sub(r'\)\)+', '))', line)
    # A run of list items becomes the kinds of item in it.
    return re.sub(r"(?:, (?:0+|'a'|\"a\")){2,}", lambda run: ' '.join(sorted(set(run.group().split(', ')))), line)


@functools.lru_cache(maxsize=None)
def saved_lines():
    """One line of the saved documents per shape. Reading all of them, over
    a megabyte of deep proofs, would test the same paths many times over."""
    lines = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'examples', '*', '*.py'))):
        with open(path, encoding='utf-8') as handle:
            for line in handle.read().split('\n'):
                if line:
                    lines.setdefault(_shape(line), line)
    return '\n'.join(lines.values())


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

    def test_nonfinite_numeric_literals_are_rejected(self):
        for text in ['1e999', '-1e999', 'f(1e+999)', '[1e+999]', 'eq(1e+999, 2e+999)']:
            for reader in (read_term, read_terms, ast_terms):
                with self.subTest(text=text, reader=reader.__name__):
                    with self.assertRaisesRegex(PeyeError, 'finite'):
                        reader(text)

    def test_document_reader_rejects_invalid_source_characters(self):
        for text in ["'a\x00b'", "'a\rb'", 'p(1)\u00a0', '\v', '\u00a0']:
            with self.subTest(text=text):
                with self.assertRaises(PeyeError):
                    read_terms(text)
        self.assertEqual([(write(t), n) for t, n in read_terms('p(1)\r\np(2)\r\n')],
                         [('p(1)', 1), ('p(2)', 2)])

    def test_long_integers_need_no_change_to_pythons_digit_limit(self):
        import sys
        if not hasattr(sys, 'set_int_max_str_digits'):
            self.skipTest('the interpreter has no decimal conversion limit')
        previous = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(640)  # the smallest limit Python allows
            digits = '9' * 5000
            for text in (f'p({digits})', f'p({digits})  # read with ast'):
                with self.subTest(text=text[-20:]):
                    (term, _), = read_terms(text)
                    self.assertEqual(term.args[0], 10 ** 5000 - 1)
                    self.assertEqual(write(term), f'p({digits})')
            self.assertEqual(run(load_text(f'from peye import *\nfact(p({digits}))')).stdout, '')
            self.assertEqual(sys.get_int_max_str_digits(), 640)
        finally:
            sys.set_int_max_str_digits(previous)

    def test_nonfinite_literals_are_reported_at_their_line(self):
        for text in ['p(1)\np(1e999)', 'p(1)\np(1e999)  # read with ast', 'p(1)\np(-1e999)  # with ast']:
            with self.subTest(text=text), self.assertRaisesRegex(PeyeError, r'^line 2: a float term must be finite'):
                read_terms(text)

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

    def test_the_direct_reading_agrees_with_ast_on_saved_documents(self):
        from peye.reader import _read_lines
        text = saved_lines()
        direct = _read_lines(text)
        self.assertIsNotNone(direct, 'every saved line can be read directly')
        self.assertEqual([(write(t), n) for t, n in direct], [(write(t), n) for t, n in ast_terms(text)])

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

    def test_saved_documents_read_back_to_their_own_spelling(self):
        lines = saved_lines().split('\n')
        for line, (term, _) in zip(lines, read_terms('\n'.join(lines))):
            if not line.startswith('step('):  # bindings are written as a dictionary
                self.assertEqual(write(term), line)


if __name__ == '__main__':
    unittest.main()
