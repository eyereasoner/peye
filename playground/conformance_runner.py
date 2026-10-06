"""The conformance page's side: read the suite's cases and run them one by one,
with the suite's own runner, conformance/run.py, against peye in this process."""
import json
import os
import sys
import time

sys.path.insert(0, '/peye/conformance')
import run as suite  # noqa: E402  conformance/run.py

from peye import __version__  # noqa: E402

sys.setrecursionlimit(5000)
CASES = []


def load(files):
    """Parse the case files, given as [{'file': name, 'text': text}], and
    describe every case."""
    os.makedirs('/cases', exist_ok=True)
    CASES.clear()
    described = []
    for entry in json.loads(files):
        path = f"/cases/{entry['file']}"
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(entry['text'])
        for case in suite.parse(path):
            CASES.append(case)
            described.append({
                'file': entry['file'], 'line': case.line, 'name': case.name, 'spec': case.spec,
                'args': case.args, 'files': case.files, 'stdin': case.stdin, 'stdout': case.stdout,
                'stdoutMode': case.stdout_mode, 'exit': case.exit, 'stderr': case.stderr,
            })
    return json.dumps({'version': __version__, 'cases': described})


def run(index):
    """Run one case: its outcome, what the implementation printed, and what
    differed from the specification."""
    case = CASES[index]
    started = time.perf_counter()
    try:
        code, stdout, stderr = suite.execute(case)
        problems = suite.check(case, code, stdout, stderr)
    except Exception as error:  # a case must never stop the suite
        code, stdout, stderr = None, '', f'{type(error).__name__}: {error}'
        problems = [f'the case could not run: {stderr}']
    return json.dumps({'code': code, 'stdout': stdout, 'stderr': stderr, 'problems': problems,
                       'milliseconds': (time.perf_counter() - started) * 1000})
