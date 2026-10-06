"""The conformance suite of conformance/, run against peye in this process."""
import os
import sys
import unittest

from helpers import ROOT

sys.path.insert(0, os.path.join(ROOT, 'conformance'))
from run import load_cases, run_case  # noqa: E402


class Conformance(unittest.TestCase):
    def test_every_case(self):
        cases = load_cases()
        self.assertGreater(len(cases), 0)
        for case in cases:
            with self.subTest(f'{case.where} {case.name}'):
                problems = run_case(case)
                self.assertEqual(problems, [], f'SPEC {case.spec}: ' + '; '.join(problems))


if __name__ == '__main__':
    unittest.main()
