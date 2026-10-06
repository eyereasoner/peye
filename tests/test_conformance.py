"""The conformance suite of conformance/, run against peye in this process."""
import os
import sys
import unittest

from helpers import ROOT

sys.path.insert(0, os.path.join(ROOT, 'conformance'))
from run import load_cases, read_manifest, run_case  # noqa: E402


class Conformance(unittest.TestCase):
    def test_the_manifest_lists_every_case_file(self):
        from run import HERE
        listed = [entry['file'] for entry in read_manifest()]
        self.assertEqual(listed, sorted(name for name in os.listdir(HERE) if name.endswith('.txt')))
        for entry in read_manifest():
            self.assertTrue(entry['spec'] and entry['topic'], entry)



def case_file_test(entry):
    def test(self):
        cases = load_cases([entry['file']])
        self.assertGreater(len(cases), 0)
        for case in cases:
            with self.subTest(f'{case.where} {case.name}'):
                problems = run_case(case)
                self.assertEqual(problems, [], f'SPEC {case.spec}: ' + '; '.join(problems))
    test.__doc__ = f"conformance/{entry['file']}: SPEC {entry['spec']}"
    return test


# One test per case file, so a verbose run shows each SPEC section as it goes.
for entry in read_manifest():
    name = os.path.splitext(entry['file'])[0].replace('-', '_')
    setattr(Conformance, f'test_cases_{name}', case_file_test(entry))


if __name__ == '__main__':
    unittest.main()
