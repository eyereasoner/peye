import os
import subprocess
import sys

from peye import PeyeError, check_proof, load_text, run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRELUDE = 'from peye import *\n'


def program(source):
    """A Program from the body of a program module; `from peye import *` is implied."""
    return load_text(PRELUDE + source)


def proven(test, source, **options):
    """Run with a proof, check it independently and return the result."""
    prog = source if not isinstance(source, str) else program(source)
    result = run(prog, proof=True, **options)
    goals = options.get('goals') or ([options['goal']] if options.get('goal') is not None else None)
    report = check_proof(prog, result.proof, goals=goals)
    test.assertTrue(report['valid'], report['failures'])
    return result


def cli(args, stdin=None):
    env = dict(os.environ, PYTHONPATH=ROOT + os.pathsep + os.environ.get('PYTHONPATH', ''))
    return subprocess.run([sys.executable, '-m', 'peye', *args], cwd=ROOT, input=stdin,
                          capture_output=True, text=True, env=env)


__all__ = ['ROOT', 'program', 'proven', 'cli', 'PeyeError', 'check_proof', 'run']
