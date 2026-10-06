"""Run the peye conformance suite against an implementation.

    python conformance/run.py                       every case, against python -m peye
    python conformance/run.py --command "my-peye"   against another implementation
    python conformance/run.py -k skolem 07-reasoning.txt
    python conformance/run.py --in-process          peye from this checkout, without a
                                                    process per case

The case format is described in conformance/README.md.
"""
import argparse
import ast
import contextlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WILDCARD = '…'


class Case:
    def __init__(self, name, path, line):
        self.name = name
        self.path = path
        self.line = line
        self.spec = ''
        self.args = 'program.py'
        self.exit = 0
        self.stderr = None      # None: not checked; 'empty', 'nonempty' or 'json'
        self.stdout_mode = 'exact'
        self.files = {}
        self.stdin = None
        self.stdout = None
        self.stdout_literal = False

    @property
    def where(self):
        return f'{os.path.basename(self.path)}:{self.line}'


def parse(path):
    """The cases of one file: '=== name' starts a case, 'key: value' lines set
    its options, and '--- block' starts a block that runs to the next marker."""
    cases = []
    case = None
    block = None
    lines = []

    def close_block():
        if case is None or block is None:
            return
        text = '\n'.join(lines)
        text = text + '\n' if text else ''
        if block == 'stdin':
            case.stdin = text
        elif block in ('stdout', 'stdout json'):
            case.stdout = text
            if block == 'stdout json':
                case.stdout_mode = 'json'
        else:
            case.files[block] = text

    with open(path, encoding='utf-8') as handle:
        source = handle.read().split('\n')
    if source and source[-1] == '':
        source.pop()
    for number, line in enumerate(source, 1):
        if line.startswith('=== '):
            close_block()
            block = None
            lines = []
            case = Case(line[4:].strip(), path, number)
            cases.append(case)
        elif line.startswith('--- '):
            close_block()
            block = line[4:].strip()
            lines = []
        elif block is not None:
            lines.append(line)
        elif case is not None and line.strip() and not line.startswith('#'):
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if key == 'spec':
                case.spec = value
            elif key == 'args':
                case.args = value
            elif key == 'exit':
                case.exit = int(value)
            elif key == 'stderr':
                case.stderr = value
            elif key == 'stdout' and value == 'nonempty':
                case.stdout_mode = 'nonempty'
            elif key == 'stdout-literal':
                # Exact output that a block cannot show, such as empty lines.
                case.stdout = ast.literal_eval(value)
                case.stdout_literal = True
            else:
                raise ValueError(f'{path}:{number}: unknown key {key!r}')
    close_block()
    for case in cases:
        # Trailing empty lines separate cases in the file; they are not content.
        for name, text in list(case.files.items()):
            case.files[name] = text.rstrip('\n') + '\n' if text.strip() else ''
        if case.stdin is not None:
            case.stdin = case.stdin.rstrip('\n') + '\n' if case.stdin.strip() else ''
        if case.stdout is not None and not case.stdout_literal:
            case.stdout = case.stdout.rstrip('\n') + '\n' if case.stdout.strip() else ''
    return cases


def line_matches(expected, actual):
    if WILDCARD not in expected:
        return expected == actual
    pattern = '.*'.join(re.escape(part) for part in expected.split(WILDCARD))
    return re.fullmatch(pattern, actual, re.DOTALL) is not None


def compare_stdout(case, actual):
    """None when the output is as expected, otherwise a description."""
    if case.stdout_mode == 'nonempty':
        return None if actual.strip() else 'expected output on standard output'
    if case.stdout is None:
        return None
    if case.stdout_mode == 'json':
        try:
            if json.loads(actual) == json.loads(case.stdout):
                return None
        except ValueError as error:
            return f'standard output is not JSON: {error}'
        return f'JSON differs:\n  expected {case.stdout.strip()}\n  actual   {actual.strip()}'
    expected_lines = case.stdout.split('\n')
    actual_lines = actual.split('\n')
    if len(expected_lines) == len(actual_lines) and all(
            line_matches(e, a) for e, a in zip(expected_lines, actual_lines)):
        return None
    for index, (e, a) in enumerate(zip(expected_lines, actual_lines)):
        if not line_matches(e, a):
            return f'line {index + 1} differs:\n  expected {e}\n  actual   {a}'
    return (f'expected {len(expected_lines) - 1} lines, got {len(actual_lines) - 1}:\n'
            f'  expected {case.stdout!r}\n  actual   {actual!r}')


def check(case, code, stdout, stderr):
    problems = []
    if code != case.exit:
        problems.append(f'exit code {code}, expected {case.exit}'
                        + (f'; stderr: {stderr.strip()[:300]}' if stderr.strip() else ''))
    difference = compare_stdout(case, stdout)
    if difference:
        problems.append(difference)
    if case.stderr == 'empty' and stderr:
        problems.append(f'expected no standard error, got: {stderr.strip()[:300]}')
    elif case.stderr == 'nonempty' and not stderr.strip():
        problems.append('expected a message on standard error')
    elif case.stderr and case.stderr.startswith('prefix '):
        prefix = case.stderr[len('prefix '):]
        if not stderr.startswith(prefix):
            problems.append(f'expected standard error to start with {prefix!r}, got: {stderr.strip()[:300]}')
    elif case.stderr == 'json':
        try:
            json.loads(stderr)
        except ValueError:
            problems.append(f'standard error is not JSON: {stderr.strip()[:300]}')
    return problems


def run_subprocess(case, command, directory):
    argv = shlex.split(command) + shlex.split(case.args)
    env = dict(os.environ)
    env['PYTHONPATH'] = ROOT + os.pathsep + env.get('PYTHONPATH', '')
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(argv, cwd=directory, input=case.stdin or '', capture_output=True,
                            text=True, encoding='utf-8', env=env, timeout=300)
    return result.returncode, result.stdout, result.stderr


def run_in_process(case, directory):
    sys.path.insert(0, ROOT)
    from peye.cli import main, with_deep_stack
    out = io.StringIO()
    err = io.StringIO()
    previous = os.getcwd()
    stdin = sys.stdin
    os.chdir(directory)
    sys.stdin = io.StringIO(case.stdin or '')
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = with_deep_stack(main, shlex.split(case.args), stdout=out, stderr=err)
    finally:
        os.chdir(previous)
        sys.stdin = stdin
    return code, out.getvalue(), err.getvalue()


def run_case(case, command=None):
    """The problems a case found, empty when it passed."""
    with tempfile.TemporaryDirectory(prefix='peye-conformance-') as directory:
        for name, text in case.files.items():
            path = os.path.join(directory, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(text)
        if command is None:
            code, stdout, stderr = run_in_process(case, directory)
        else:
            code, stdout, stderr = run_subprocess(case, command, directory)
    return check(case, code, stdout, stderr)


def case_files(names=()):
    if names:
        return [name if os.path.isabs(name) or os.path.exists(name) else os.path.join(HERE, name)
                for name in names]
    return sorted(os.path.join(HERE, name) for name in os.listdir(HERE) if name.endswith('.txt'))


def load_cases(names=(), pattern=None):
    cases = [case for path in case_files(names) for case in parse(path)]
    if pattern:
        cases = [case for case in cases if pattern.lower() in case.name.lower()]
    return cases


def main():
    parser = argparse.ArgumentParser(description='Run the peye conformance suite.')
    parser.add_argument('files', nargs='*', help='case files (default: every conformance/*.txt)')
    parser.add_argument('--command', default=f'{shlex.quote(sys.executable)} -m peye',
                        help='the implementation to test (default: python -m peye)')
    parser.add_argument('--in-process', action='store_true',
                        help='run peye from this checkout in this process')
    parser.add_argument('-k', dest='pattern', help='only cases whose name contains this')
    parser.add_argument('-v', '--verbose', action='store_true', help='list passing cases too')
    options = parser.parse_args()
    cases = load_cases(options.files, options.pattern)
    failed = 0
    for case in cases:
        problems = run_case(case, None if options.in_process else options.command)
        if problems:
            failed += 1
            print(f'FAIL {case.where} {case.name} [SPEC {case.spec}]')
            for problem in problems:
                print('     ' + problem.replace('\n', '\n     '))
        elif options.verbose:
            print(f'ok   {case.where} {case.name}')
    print(f'{len(cases) - failed} of {len(cases)} cases passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
