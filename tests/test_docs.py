"""Runnable documentation and published coverage stay tied to the repository."""
import ast
import contextlib
import io
import json
import os
import re
import unittest

from peye import check_report, load_text, run

from helpers import ROOT


def document(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as handle:
        return handle.read()


def python_blocks(path, heading):
    section = re.split(r'\n#{2,6} ', document(path).split(heading + '\n', 1)[1], maxsplit=1)[0]
    return re.findall(r'^```python\n(.*?)^```', section, re.MULTILINE | re.DOTALL)


class Documentation(unittest.TestCase):
    def test_readme_intro_proof_and_report_match_the_program(self):
        source, proof = python_blocks('README.md', '## The idea in a few lines')
        result = run(load_text(source), proof=True)
        self.assertEqual(result.proof, proof)
        report, = python_blocks('README.md', '## Proofs, and what checking one means')
        self.assertEqual(check_report(result.proof_report), report)

    def test_readme_library_example_runs_with_the_documented_results(self):
        source, = python_blocks('README.md', '## From Python')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(source, 'README.md', 'exec'), {})
        self.assertEqual([ast.literal_eval(line) for line in output.getvalue().splitlines()],
                         [["mortal('socrates')"], [{'X': "'socrates'"}], True])

    def test_spec_appendix_output_proof_and_report_match_the_program(self):
        source, output, proof, report = python_blocks('SPEC.md', '## Appendix B. Example')
        program = load_text(source)
        self.assertEqual(run(program).stdout, output)
        result = run(program, proof=True)
        self.assertEqual(result.proof, proof)
        self.assertEqual(check_report(result.proof_report), report)

    def test_documented_example_count_matches_the_manifest(self):
        count = re.search(r'example collection.*?is (\d+)\s+complete programs',
                          document('README.md'), re.DOTALL)
        self.assertIsNotNone(count)
        self.assertEqual(int(count.group(1)), len(json.loads(document('examples/manifest.json'))))

    def test_conformance_coverage_table_matches_every_case_file(self):
        rows = re.findall(r'^\| \[([^]]+\.txt)\]\([^)]*\) \| [^|]+ \| (\d+) \|',
                          document('conformance/README.md'), re.MULTILINE)
        manifest = json.loads(document('conformance/manifest.json'))
        self.assertEqual([name for name, _ in rows], [entry['file'] for entry in manifest])
        for name, count in rows:
            with self.subTest(file=name):
                cases = re.findall(r'^=== ', document('conformance/' + name), re.MULTILINE)
                self.assertEqual(int(count), len(cases))


if __name__ == '__main__':
    unittest.main()
