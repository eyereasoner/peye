"""How long each example takes: loading the program, reasoning, reasoning
with a proof, and checking that proof on its own, as --check-proof does.
Every generated proof is checked before it is returned, so the prove time
includes one check as well.

    python tools/timings.py                    every example, by name
    python tools/timings.py --sort             slowest first
    python tools/timings.py socrates zebra     just these
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import read_manifest, source_path  # noqa: E402
from peye import check_proof, load, run  # noqa: E402
from peye.cli import with_deep_stack  # noqa: E402


def timed(function, *args, **kwargs):
    start = time.perf_counter()
    value = function(*args, **kwargs)
    return value, time.perf_counter() - start


def main():
    parser = argparse.ArgumentParser(description='Time every example.')
    parser.add_argument('names', nargs='*', help='examples to time (default: all)')
    parser.add_argument('--sort', action='store_true', help='slowest first')
    options = parser.parse_args()
    entries = sorted(read_manifest(), key=lambda entry: entry['name'])
    if options.names:
        known = {entry['name'] for entry in entries}
        unknown = sorted(set(options.names) - known)
        if unknown:
            parser.error(f"unknown example {', '.join(unknown)}")
        entries = [entry for entry in entries if entry['name'] in options.names]
    rows = []
    for entry in entries:
        program, loading = timed(load, source_path(entry))
        _, reasoning = timed(run, program)
        proved, proving = timed(run, program, proof=True)
        _, checking = timed(check_proof, program, proved.proof)
        rows.append((entry['name'], loading, reasoning, proving, checking))
        if not options.sort:
            print_row(*rows[-1])
    if options.sort:
        for row in sorted(rows, key=lambda row: -(row[1] + row[3])):
            print_row(*row)
    total = [sum(row[i] for row in rows) for i in (1, 2, 3, 4)]
    print(f"{'':24} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8}")
    print_row(f'{len(rows)} examples', *total)


def print_row(name, loading, reasoning, proving, checking):
    if not hasattr(print_row, 'header'):
        print_row.header = True
        print(f"{'example':24} {'load':>8} {'run':>8} {'prove':>8} {'check':>8}")
    print(f'{name:24} {loading:7.2f}s {reasoning:7.2f}s {proving:7.2f}s {checking:7.2f}s')


if __name__ == '__main__':
    with_deep_stack(main)
