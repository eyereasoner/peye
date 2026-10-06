"""Regenerate the saved output, proof and check report of every example.

Every example is evaluated before any file is written, so a reasoning failure
does not leave a partially refreshed corpus.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import KINDS, artifact_path, evaluate, read_manifest  # noqa: E402
from peye.cli import with_deep_stack  # noqa: E402


def main():
    results = [(entry, evaluate(entry)) for entry in read_manifest()]
    for kind in KINDS:
        os.makedirs(os.path.dirname(artifact_path(kind, results[0][0])), exist_ok=True)
    for entry, artifacts in results:
        for kind in KINDS:
            with open(artifact_path(kind, entry), 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(artifacts[kind])
        print(f"updated {entry['name']}: output, proof, check")


if __name__ == '__main__':
    with_deep_stack(main)
