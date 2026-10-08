"""Every test of peye in one run, one numbered line per test: ./test

    ./test                      unit tests, examples, conformance in process
                                and through the command line
    ./test unit examples        only these sections
    ./test -k skolem            only tests whose line contains "skolem"

Sections: unit, examples, conformance, cli. Each test prints OK or FAIL, its
number, what it tests and how long it took; each section and the whole run
end with a total. The exit code is 1 when a test failed.
"""
import argparse
import concurrent.futures
import os
import sys
import time
import traceback
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ROOT, os.path.join(ROOT, 'conformance')]

SECTIONS = ('unit', 'examples', 'conformance', 'cli')
TITLES = {'unit': 'Unit tests', 'examples': 'Examples', 'conformance': 'Conformance',
          'cli': 'Conformance through the command line'}
COUNTED = {'unit': 'unit tests', 'examples': 'example tests', 'conformance': 'conformance cases',
           'cli': 'conformance cases through the command line'}

COLOR = os.environ.get('NO_COLOR') is None and (
    sys.stdout.isatty() or os.environ.get('FORCE_COLOR', '0') != '0')


def paint(code, text):
    return f'\x1b[{code}m{text}\x1b[0m' if COLOR else text


class Reporter:
    def __init__(self, pattern):
        self.pattern = pattern
        self.passed = self.total = 0
        self.failures = []
        self.started = time.perf_counter()
        self.section_start = None
        self.heading = None

    def wanted(self, label):
        return self.pattern is None or self.pattern.lower() in label.lower()

    def section(self, name):
        # The heading waits for the section's first test, so a section -k
        # leaves empty does not show.
        self.heading = name
        self.section_start = (time.perf_counter(), self.passed, self.total)

    def end_section(self, name):
        started, passed, total = self.section_start
        if self.total == total:
            return
        self.summary(self.passed - passed, self.total - total, COUNTED[name], time.perf_counter() - started)

    def summary(self, passed, total, what, seconds):
        word = paint('32', 'OK') if passed == total else paint('31', 'FAIL')
        outcome = 'passed' if passed == total else f'passed, {total - passed} failed'
        print(f'{word} {passed}/{total} {what} {outcome} {paint("2", f"({seconds:.1f} s)")}', flush=True)

    def result(self, label, seconds, problem=None):
        if self.heading is not None:
            print('\n' + paint('33', f'== {TITLES[self.heading]}'), flush=True)
            self.heading = None
        self.total += 1
        number = f'{self.total:03d}'
        timing = paint('2', f'({seconds * 1000:.0f} ms)')
        if problem is None:
            self.passed += 1
            print(f'{paint("32", "OK")} {number} {label} {timing}', flush=True)
        else:
            self.failures.append((number, label))
            print(f'{paint("31", "FAIL")} {number} {label} {timing}', flush=True)
            print(problem.rstrip(), file=sys.stderr, flush=True)

    def finish(self):
        if self.total == 0:
            print(paint('31', 'FAIL') + ' no test matches')
            return 1
        print('\n' + paint('33', '== Total'))
        self.summary(self.passed, self.total, 'tests', time.perf_counter() - self.started)
        for number, label in self.failures:
            print(f'{paint("31", "FAIL")} {number} {label}')
        return 0 if self.passed == self.total else 1


def unittest_cases():
    """Every unittest test method, as (section, label, test)."""
    suite = unittest.defaultTestLoader.discover(HERE, pattern='test_*.py', top_level_dir=HERE)
    pending = [suite]
    while pending:
        item = pending.pop(0)
        if isinstance(item, unittest.TestSuite):
            pending[:0] = list(item)
            continue
        if isinstance(item, unittest.loader._FailedTest):
            yield 'unit', item.id(), item
            continue
        module = type(item).__module__
        method = item._testMethodName
        if module == 'test_conformance' and method.startswith('test_cases_'):
            continue  # the cases are run one by one below
        if module == 'test_examples' and method.startswith('test_example_'):
            yield 'examples', item.shortDescription() or method, item
            continue
        yield 'unit', f"{module.removeprefix('test_')}: {method.removeprefix('test_').replace('_', ' ')}", item


def run_unittest(test):
    result = unittest.TestResult()
    test.run(result)
    problems = result.failures + result.errors
    if problems:
        return ''.join(text for _, text in problems)
    if result.skipped:
        return None
    return None


def run_unittests(reporter, section, cases):
    for _, label, test in cases:
        if not reporter.wanted(label):
            continue
        started = time.perf_counter()
        problem = run_unittest(test)
        reporter.result(label, time.perf_counter() - started, problem)


def conformance_cases(reporter):
    from run import load_cases
    return [case for case in load_cases() if reporter.wanted(f'{case.where} {case.name}')]


def run_conformance(reporter, through_command_line):
    import shlex
    from run import run_case
    cases = conformance_cases(reporter)
    command = f'{shlex.quote(sys.executable)} -m peye' if through_command_line else None

    def one(case):
        started = time.perf_counter()
        try:
            problems = run_case(case, command)
            problem = ('; '.join(problems) + '\n') if problems else None
        except Exception:
            problem = traceback.format_exc()
        return case, time.perf_counter() - started, problem

    if through_command_line:
        # Each case is a process of its own, so they run side by side.
        env_path = os.environ.get('PYTHONPATH')
        os.environ['PYTHONPATH'] = ROOT + (os.pathsep + env_path if env_path else '')
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            outcomes = pool.map(one, cases)
            for case, seconds, problem in outcomes:
                reporter.result(f'{case.where} {case.name}', seconds, problem)
    else:
        for case in cases:
            case, seconds, problem = one(case)
            reporter.result(f'{case.where} {case.name}', seconds, problem)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='./test', description='Run every test of peye.')
    parser.add_argument('sections', nargs='*', choices=[[], *SECTIONS], metavar='SECTION',
                        help=f"any of {', '.join(SECTIONS)} (default: all)")
    parser.add_argument('-k', dest='pattern', help='only tests whose line contains this text')
    options = parser.parse_args(argv)
    sections = options.sections or list(SECTIONS)
    reporter = Reporter(options.pattern)
    from peye import __version__
    from peye.cli import with_deep_stack
    print(paint('2', f'peye {__version__} on Python {sys.version.split()[0]}'), flush=True)

    def run_all():
        cases = list(unittest_cases())
        for section in SECTIONS:
            if section not in sections:
                continue
            reporter.section(section)
            if section in ('unit', 'examples'):
                run_unittests(reporter, section, [case for case in cases if case[0] == section])
            else:
                run_conformance(reporter, through_command_line=section == 'cli')
            reporter.end_section(section)
        return reporter.finish()
    return with_deep_stack(run_all)


if __name__ == '__main__':
    sys.exit(main())
