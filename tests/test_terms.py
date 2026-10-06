import unittest

from peye import PeyeError, Struct, Var, read_term, run, write
from peye.terms import Env, compare_terms, copy_resolved, unify

from helpers import program


class Terms(unittest.TestCase):
    def test_fresh_variable_names_cannot_collide_with_source_names(self):
        self.assertNotEqual(write(Var('X#1')), write(Var('X_1')))
        self.assertNotEqual(write(Var('X#1')), write(Var('EYE_X_23_1')))
        self.assertEqual(write(Struct('p', (Var('X#1'), Var('X_1')))), 'p(EYE_X_23_1, X_1)')
        self.assertEqual(write(Var('EYE_X_23_1')), 'EYE_EYE__X__23__1')

    def test_the_trail_restores_bindings_and_occurs_checks_use_aliases(self):
        env = Env()
        x, y = Var('X'), Var('Y')
        self.assertTrue(unify(x, y, env))
        mark = env.mark()
        self.assertTrue(unify(y, 'a', env))
        # Dereferencing X follows the alias and shortens it, which rebinds X.
        self.assertEqual(copy_resolved(x, env), 'a')
        env.undo(mark)
        # Undoing restores the alias rather than dropping the rebound name.
        self.assertIsInstance(copy_resolved(x, env), Var)
        self.assertFalse(unify(y, Struct('f', (x,)), env))
        env.undo(mark)
        self.assertTrue(unify(y, 'b', env))
        self.assertEqual(copy_resolved(x, env), 'b')

    def test_numeric_identity_and_order_keep_exact_large_integers(self):
        self.assertFalse(unify(1.0, 1, Env()))
        self.assertTrue(unify(1, 1, Env()))
        self.assertEqual(compare_terms(9007199254740993, 9007199254740992), 1)

    def test_standard_order_compares_numbers_by_value_before_type(self):
        def order(left, right):
            return run(program(''), goal=f'compare(O, {left}, {right})').bindings[0]['O']
        self.assertEqual(order('1.0', '0'), "'>'")
        self.assertEqual(order('2', '1.5'), "'>'")
        self.assertEqual(order('-1.5', '-2'), "'>'")
        # Equal value, so the float precedes the integer.
        self.assertEqual(order('1.0', '1'), "'<'")
        self.assertEqual(order('1', '1.0'), "'>'")
        self.assertEqual(order('9007199254740993', '9007199254740992.0'), "'>'")
        self.assertEqual(order("'foo'", '1'), "'>'")
        self.assertEqual(order('f(1)', "'foo'"), "'>'")
        self.assertEqual(order('X', '1'), "'<'")

    def test_terms_are_not_truth_values(self):
        X = Var('X')
        with self.assertRaisesRegex(PeyeError, 'parenthesize'):
            bool(X > 1)
        with self.assertRaises(PeyeError):
            if X:
                pass

    def test_python_operators_build_terms(self):
        X, Y = Var('X'), Var('Y')
        self.assertEqual(write(X + 1 < Y * 2), 'X + 1 < Y * 2')
        self.assertEqual(write(1 - X), '1 - X')
        self.assertEqual(write(-(X ** 2)), '-X ** 2')
        self.assertEqual(write((-X) ** 2), '(-X) ** 2')
        self.assertEqual(write([1, 2, *X]), '[1, 2, *X]')
        self.assertEqual(write(read_term('[a, *b]')), '[a, *b]')
        self.assertEqual(write((X > 1) & (Y < 2) | ~X), '(X > 1) & (Y < 2) | ~X')


if __name__ == '__main__':
    unittest.main()
