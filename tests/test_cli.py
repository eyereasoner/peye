import json
import os
import unittest

from peye import __version__

from helpers import ROOT, cli

SOCRATES = "type('socrates', 'mortal')\ntype('socrates', 'human')\n"


class CommandLine(unittest.TestCase):
    def test_runs_files_stdin_multiple_sources_and_goals(self):
        self.assertEqual(cli(['examples/socrates.py']).stdout, SOCRATES)
        self.assertEqual(cli([], "from peye import *\np, q = preds('p q')\nX = vars('X')\n"
                                 "fact(p('a'))\nimplies(p(X), q(X))\n").stdout, "q('a')\n")
        result = cli(['examples/socrates.py', '-', '--goal', "type(X, 'mortal')"],
                     "from peye import *\ntype = preds('type')\nfact(type('plato', 'human'))\n")
        self.assertEqual(result.stdout, "type('socrates', 'mortal')\ntype('plato', 'mortal')\n", result.stderr)

    def test_proof_generation_pipes_into_proof_checking(self):
        generated = cli(['--proof', 'examples/socrates.py'])
        self.assertEqual(generated.returncode, 0, generated.stderr)
        checked = cli(['--check-proof', '-', 'examples/socrates.py'], generated.stdout)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("condition('C1', 'resolution', 'ok', 3)\n", checked.stdout)
        self.assertIn("verdict('checked')\n", checked.stdout)
        as_json = cli(['--json', '--check-proof', '-', 'examples/socrates.py'], generated.stdout)
        self.assertEqual(as_json.returncode, 0)
        self.assertTrue(json.loads(as_json.stdout)['valid'])
        self.assertEqual(len(json.loads(as_json.stdout)['conditions']), 7)
        self.assertEqual(cli(['--check-proof', '-', 'examples/socrates.py'], generated.stdout + "bogus()\n").returncode, 2)

    def test_a_proof_document_given_as_a_program_says_how_to_check_it(self):
        ran = cli(['examples/proof/socrates.py'])
        self.assertEqual(ran.returncode, 1)
        self.assertIn('this is a proof document, not a program: check it with --check-proof PROOF PROGRAM', ran.stderr)
        self.assertIn('reserved head clause/2', cli([], "from peye import *\nfact(struct('clause', 'a', 'b'))\n").stderr)

    def test_prints_the_version(self):
        for flag in ('-v', '--version'):
            result = cli([flag, 'examples/socrates.py'])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, f'peye v{__version__}\n')

    def test_the_version_agrees_everywhere_it_is_written(self):
        # pyproject.toml, the README badge and every "peye X.Y.Z" in the docs.
        import sys
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import version
        self.assertEqual(version.current(), __version__)
        self.assertEqual(version.check(), [])

    def test_lists_the_clauses_that_make_no_difference(self):
        source = ("from peye import *\np, q, s, z = preds('p q s z')\nX = vars('X')\n"
                  "fact(p('a'))\nfact(q('b'))\nimplied_by(s(X), q(X))\nfact(z('c'))\nimplies(p('a') & ~s('a'), 'ok')\n")
        result = cli(['--unused'], source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "unused(line(5), fact(q('b')))\n"
                                        "unused(line(6), implied_by(s(X), q(X)))\n"
                                        "unused(line(7), fact(z('c')))\n")
        self.assertEqual(cli(['--unused', 'examples/socrates.py']).stdout, '')
        self.assertEqual(cli(['--unused', '--proof', 'examples/socrates.py']).returncode, 1)

    def test_help_errors_stats_and_fuse_exit_codes(self):
        self.assertIn('Usage: peye', cli(['--help']).stdout)
        self.assertEqual(cli(['--unknown']).returncode, 1)
        self.assertEqual(cli(['--max-depth', '0']).returncode, 1)
        self.assertEqual(cli(['--check-proof', '-'], '').returncode, 1)
        self.assertEqual(cli([], "from peye import *\nfact('p')\ncontradiction('p')\n").returncode, 65)
        result = cli(['--stats', 'examples/socrates.py'])
        self.assertEqual(json.loads(result.stderr)['derived'], 1)

    def test_failed_and_strict_checks_print_verdicts_and_exit_unsuccessfully(self):
        failed = cli(['--check-proof', '-', '--goal', 'is_(7, 2 + 3)', 'examples/socrates.py'],
                     "is_(7, 2 + 3)\nstep(is_(7, 2 + 3), 'builtin', {}, [])\n")
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stderr, '')
        self.assertIn("condition('C5', 're_decision', failed(1), 0)\n", failed.stdout)
        self.assertIn("failure('C5', is_(7, 2 + 3),", failed.stdout)
        self.assertIn('verdict(failed(1))\n', failed.stdout)
        strict = cli(['--strict-proof', '--check-proof', 'examples/proof/permissions.py', 'examples/permissions.py'])
        self.assertEqual(strict.returncode, 2)
        self.assertIn("obligation('absent', 'theory_scoped',", strict.stdout)
        self.assertIn('verdict(failed(', strict.stdout)
        self.assertEqual(cli(['--json', 'examples/socrates.py']).returncode, 1)

    def test_a_program_runs_as_a_script(self):
        import subprocess
        import sys
        env = dict(os.environ, PYTHONPATH=ROOT)
        result = subprocess.run([sys.executable, 'examples/socrates.py'], cwd=ROOT, env=env,
                                 capture_output=True, text=True)
        self.assertEqual(result.stdout, SOCRATES, result.stderr)
        proof = subprocess.run([sys.executable, 'examples/socrates.py', '--proof'], cwd=ROOT, env=env,
                               capture_output=True, text=True)
        self.assertEqual(cli(['--check-proof', '-', 'examples/socrates.py'], proof.stdout).returncode, 0)
        fused = subprocess.run([sys.executable, 'examples/integrity.py'], cwd=ROOT, env=env,
                               capture_output=True, text=True)
        self.assertEqual(fused.returncode, 65)


if __name__ == '__main__':
    unittest.main()
