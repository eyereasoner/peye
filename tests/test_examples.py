"""The example corpus: every program reproduces its saved output, proof and
check report, its saved proof checks from disk, and a tampered one does not."""
import os
import sys
import unittest

from peye import check_proof, check_report, run
from peye.cli import with_deep_stack

from helpers import ROOT, cli

sys.path.insert(0, os.path.join(ROOT, 'tools'))
from corpus import KINDS, artifact_path, certify, load_example, read_manifest, source_path  # noqa: E402

MANIFEST = read_manifest()
# PEYE_EXAMPLES=socrates,graphs limits the corpus to those examples.
ONLY = set(filter(None, os.environ.get('PEYE_EXAMPLES', '').split(',')))
CHANGED = '{} changed; review it, then run python tools/update_examples.py'


def read(path):
    with open(path, encoding='utf-8') as handle:
        return handle.read()


class Examples(unittest.TestCase):
    def test_the_manifest_covers_every_source_artifact_and_deck(self):
        names = sorted(f"{entry['name']}.py" for entry in MANIFEST)
        examples = os.path.join(ROOT, 'examples')
        self.assertEqual(sorted(f for f in os.listdir(examples) if f.endswith('.py')), names)
        for kind in KINDS:
            self.assertEqual(sorted(os.listdir(os.path.join(examples, kind))), names)
        decks = sorted([f"{entry['name']}.md" for entry in MANIFEST] + ['README.md'])
        self.assertEqual(sorted(f for f in os.listdir(os.path.join(examples, 'deck')) if f.endswith('.md')), decks)

    def check_example(self, entry):
        program = load_example(entry)
        output = run(program)
        proved = certify(entry, program, output)
        saved = {kind: read(artifact_path(kind, entry)) for kind in KINDS}
        self.assertEqual(output.stdout, saved['output'], CHANGED.format('output'))
        self.assertEqual(proved.proof, saved['proof'], CHANGED.format('proof'))
        self.assertEqual(check_report(proved.proof_report), saved['check'], CHANGED.format('check'))
        # The saved certificate, checked from scratch.
        self.assertEqual(check_report(check_proof(program, saved['proof'])), saved['check'])
        tampered = saved['proof'] + "\nunjustified_example_claim()\n"
        self.assertFalse(check_proof(program, tampered)['valid'])

    def test_the_command_line_on_examples(self):
        for name in ('socrates', 'graphs', 'integrity'):
            entry = next(entry for entry in MANIFEST if entry['name'] == name)
            source = os.path.relpath(source_path(entry), ROOT)
            with self.subTest(name):
                ran = cli([source])
                self.assertEqual(ran.returncode, entry.get('halt_code') or 0, ran.stderr)
                self.assertEqual(ran.stdout, read(artifact_path('output', entry)))
                proof = cli(['--proof', source])
                self.assertEqual(proof.stdout, read(artifact_path('proof', entry)))
                checked = cli(['--check-proof', os.path.relpath(artifact_path('proof', entry), ROOT), source])
                self.assertEqual(checked.returncode, 0, checked.stderr)
                self.assertEqual(checked.stdout, read(artifact_path('check', entry)))


def example_test(entry):
    def test(self):
        if ONLY and entry['name'] not in ONLY:
            self.skipTest('not in PEYE_EXAMPLES')
        with_deep_stack(self.check_example, entry)
    test.__doc__ = f"examples/{entry['name']}.py: {entry['description']}"
    return test


# One test per example, so a verbose run shows each as it goes and a failure
# names the example.
for entry in MANIFEST:
    setattr(Examples, 'test_example_' + entry['name'].replace('-', '_'), example_test(entry))


if __name__ == '__main__':
    unittest.main()
