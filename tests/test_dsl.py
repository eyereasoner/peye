"""Stating programs: names a program uses without defining them are supplied."""
import os
import subprocess
import sys
import unittest

from peye import PeyeError, load_text, run
from peye.dsl import Pred, implicit_names
from peye.terms import Var

from helpers import ROOT


def program(source):
    return load_text('from peye import *\n' + source)


class ImplicitNames(unittest.TestCase):
    def test_undefined_names_are_predicates_and_variables(self):
        names = implicit_names('from peye import *\nfact(type(X, _Y, sum))\nquery(type(X, Y, Z))\n')
        self.assertEqual(sorted(names), ['X', 'Y', 'Z', '_Y', 'sum', 'type'])
        self.assertIsInstance(names['type'], Pred)
        self.assertIsInstance(names['sum'], Pred)
        self.assertIsInstance(names['X'], Var)
        self.assertIsInstance(names['_Y'], Var)

    def test_bound_exported_kept_and_capitalized_builtin_names_are_left_alone(self):
        names = implicit_names('from peye import *\nedge = 1\nimport math\n'
                               'for i in range(3): print(len([i]), math.pi, unify, ValueError)\n')
        self.assertEqual(names, {})

    def test_socrates_without_declarations(self):
        source = program('''
fact(type('socrates', 'human'))
fact(subclass_of('human', 'mortal'))
implies(type(S, A) & subclass_of(A, B), type(S, B))
query(type(X, Y))
''')
        self.assertEqual(run(source).answers, ["type('socrates', 'mortal')", "type('socrates', 'human')"])

    def test_helper_functions_see_the_implicit_names(self):
        source = program('''
def chain(n):
    for i in range(n):
        fact(edge(i, i + 1))

chain(3)
implies(edge(X, Y), path(X, Y))
implies(path(X, Y) & edge(Y, Z), path(X, Z))
query(path(0, W))
''')
        self.assertEqual(run(source).answers, ['path(0, 1)', 'path(0, 2)', 'path(0, 3)'])

    def test_local_parameters_do_not_suppress_implicit_globals(self):
        source = program("def state(X):\n    fact(p(X))\nstate(1)\nquery(p(X))")
        self.assertEqual(run(source).answers, ['p(1)'])

    def test_predicate_names_work_as_atoms_and_in_expressions(self):
        source = program("fact(ready)\nquery(is_(V, 2 * pi + sqrt(4)), ~blocked, ready)")
        self.assertEqual(run(source).answers, ["is_(8.283185307179586, 2 * 'pi' + sqrt(4)) & ~'blocked' & 'ready'"])

    def test_a_variable_named_like_a_library_class_is_a_variable(self):
        source = program("fact(answer(42))\nquery(answer(Result))")
        self.assertEqual(run(source).answers, ['answer(42)'])

    def test_explicit_declarations_still_work(self):
        source = program("range = preds('range')\nN = vars('N')\nfact(range(1, 3))\nquery(range(1, N))")
        self.assertEqual(run(source).answers, ['range(1, 3)'])

    def test_clauses_know_the_line_that_states_them(self):
        lines = ['from peye import *', '', 'def state(n):', '    fact(n_(n))', '']
        lines += [f'fact(p({i}))' for i in range(2000)]
        lines += ['state(1)', 'implied_by(', '    q(X),', '    p(X),', ')']
        clauses = load_text('\n'.join(lines) + '\n').clauses
        self.assertEqual([clause.line for clause in clauses[:2]], [6, 7])
        self.assertEqual(clauses[1999].line, 2005)
        self.assertEqual(clauses[2000].line, 4)  # stated inside state()
        self.assertEqual(clauses[2001].line, 2007)

    def test_the_token_scan_finds_the_names_the_syntax_tree_finds(self):
        import builtins
        import glob
        from peye import __all__ as exported
        from peye.dsl import _ast_names_in_statements, _scan_names_in_statements
        wanted = {name for name in dir(builtins) if not name.startswith('_')}
        # The examples, except the few generated ones too long to say more.
        sources = []
        for path in glob.glob(os.path.join(ROOT, 'examples', '*.py')):
            if os.path.getsize(path) < 100_000:
                with open(path, encoding='utf-8') as handle:
                    sources.append(handle.read())
        sources += [
            "fact(p(type))", "x = type(1)\nfact(p(sum([1])))", "fact(p(x.type))", "fact(p(type=1))",
            "fact(p([type for type in xs]))", "fact(p('type'))", 'fact(p("""type\n"""))', "# fact(type)\n",
            "fact(p(X)) if type(1) else 0", "fact\n(p(type))", "y = x.fact(type(1))", "fact(p(min))\nmax(1)",
            "fact(p(type == 1))", "fact(p(sum != 1))", "fact(p(1 if type else 2))", "fact(p(rb'x', type))",
            "fact(p(r'\\'', type))", "fact(p(\nsum\n))\nzip(1)", "implies(findall(X, p(X), L) & ~abs, q)",
        ]
        for source in sources:
            with self.subTest(source[:60]):
                scanned = _scan_names_in_statements(source, exported, wanted)
                if scanned is None:
                    continue  # an f-string or a lambda: the syntax tree decides instead
                self.assertEqual(scanned, _ast_names_in_statements(source, '<program>', exported) & wanted)
        for source in ["fact(p(f'{sum(1)}'))", "fact(p(lambda type: 1))"]:
            self.assertIsNone(_scan_names_in_statements(source, exported, wanted))

    def test_a_misspelled_statement_is_an_error(self):
        with self.assertRaisesRegex(PeyeError, r'line 3: fcat\(\.\.\.\) on its own states nothing'):
            program("fact(p(1))\nfcat(p(2))")


class Scripts(unittest.TestCase):
    def run_script(self, source, *args):
        path = os.path.join(ROOT, 'tests', '_script_under_test.py')
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(source)
        try:
            return subprocess.run([sys.executable, path, *args], capture_output=True, text=True,
                                  env=dict(os.environ, PYTHONPATH=ROOT))
        finally:
            os.remove(path)

    def test_a_program_runs_as_a_script_with_command_line_options(self):
        result = self.run_script('from peye import *\nfact(p(1))\nquery(p(X))\n', '--goal', 'p(Y)')
        self.assertEqual(result.stdout, 'p(1)\n', result.stderr)

    def test_a_script_using_the_library_is_not_taken_over(self):
        result = self.run_script('from peye import load_text, run\n'
                                 'print(run(load_text("from peye import *\\nfact(p(1))\\nquery(p(X))")).answers)\n')
        self.assertEqual(result.stdout, "['p(1)']\n", result.stderr)
        # The program text names peye too, but only inside a string.
        result = self.run_script('from peye import load_text, run\n'
                                 'source = """\nfrom peye import *\nfact(p(1))\nquery(p(X))\n"""\n'
                                 'print(run(load_text(source)).answers)\n')
        self.assertEqual(result.stdout, "['p(1)']\n", result.stderr)


if __name__ == '__main__':
    unittest.main()
