import unittest

from peye import PeyeError, run

from helpers import program

EMPTY = program('')


def value(expression):
    return run(EMPTY, goal=f'is_(X, {expression})').bindings[0]['X']


def fails(expression):
    try:
        run(EMPTY, goal=f'is_(X, {expression})')
    except PeyeError as error:
        return str(error)
    return None


class Arithmetic(unittest.TestCase):
    def test_integer_results_never_round_through_a_double(self):
        self.assertEqual(value('trunc(10000000000000000001)'), '10000000000000000001')
        self.assertEqual(value('ceil(123456789012345678901234567890)'), '123456789012345678901234567890')
        self.assertEqual(value('floor(-99999999999999999999)'), '-99999999999999999999')
        self.assertEqual(value('round(10000000000000000001)'), '10000000000000000001')
        self.assertEqual(value('abs(-123456789012345678901234567890)'), '123456789012345678901234567890')
        self.assertEqual(value('2 ** 100'), '1267650600228229401496703205376')
        self.assertEqual(value('1 << 200'), '1606938044258990275541962092341162602522202993782792835301376')

    def test_operators_mean_what_they_mean_in_python(self):
        self.assertEqual(value('4 / 2'), '2.0')
        self.assertEqual(value('7 / 2'), '3.5')
        self.assertEqual(value('-7 // 3'), '-3')
        self.assertEqual(value('-7 % 3'), '2')
        self.assertEqual(value('2 ** -1'), '0.5')
        self.assertEqual(value('6 & 3'), '2')
        self.assertEqual(value('6 | 3'), '7')
        self.assertEqual(value('6 ^ 3'), '5')
        self.assertEqual(value('~5'), '-6')
        self.assertEqual(value('round(2.5)'), '2')
        self.assertEqual(value('round(3.5)'), '4')
        self.assertEqual(value('round(2.675, 2)'), '2.67')
        self.assertEqual(value('int(-2.7)'), '-2')
        self.assertEqual(value('floor(-2.5)'), '-3')
        self.assertEqual(value('min(2, 1.5)'), '1.5')
        self.assertEqual(value('max(2, 3, 1)'), '3')
        self.assertEqual(value('gcd(12, 18)'), '6')
        self.assertEqual(value("'pi' * 2"), '6.283185307179586')

    def test_exceptional_conditions_are_errors(self):
        self.assertIn('division by zero', fails('1 / 0'))
        self.assertIn('division by zero', fails('1 % 0'))
        self.assertIn('division by zero', fails('0 ** -1'))
        self.assertIn('log', fails('log(0)'))
        self.assertIn('sqrt', fails('sqrt(-1)'))
        self.assertIn('no real result', fails('(-8) ** 0.5'))
        self.assertIn('not an arithmetic value', fails("'foo' + 1"))
        self.assertIn('unbound', fails('Y + 1'))
        self.assertIn('not an arithmetic function', fails('foo(1)'))
        self.assertIn('too large', fails('2 ** (10 ** 10)'))

    def test_comparison_stays_exact_across_the_integer_float_boundary(self):
        self.assertEqual(run(EMPTY, goal='9007199254740993 > 9007199254740992.0').answers,
                         ['9007199254740993 > 9007199254740992.0'])
        self.assertEqual(run(program('query(eq(1, 1.0))')).answers, ['eq(1, 1.0)'])
        self.assertEqual(run(program('query(ne(1, 1.0))')).answers, [])


if __name__ == '__main__':
    unittest.main()
