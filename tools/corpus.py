"""The example corpus: the manifest, and evaluating an example into the
output, proof and check report saved beside it."""
import json
import os
import re

from peye import check_report, load, run

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples')
KINDS = ('output', 'proof', 'check')
# A run's Skolem atoms have a random genid; the saved artifacts use this one,
# so that they can be reproduced.
SKOLEM_GENID = 'examples'


def read_manifest():
    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, list) or not manifest:
        raise ValueError('the example manifest must be a nonempty list')
    names = set()
    for entry in manifest:
        if (not re.fullmatch(r'[a-z][a-z0-9-]*', entry.get('name', '')) or entry['name'] in names or
                not isinstance(entry.get('description'), str) or not isinstance(entry.get('trusted'), list)):
            raise ValueError(f'invalid example manifest entry: {entry!r}')
        names.add(entry['name'])
    return manifest


def source_path(entry):
    return os.path.join(ROOT, f"{entry['name']}.py")


def artifact_path(kind, entry):
    return os.path.join(ROOT, kind, f"{entry['name']}.py")


def load_example(entry):
    return load(source_path(entry))


def certify(entry, program, output):
    """A certified run holds a valid nonempty proof, agrees with the plain
    run, and relies on exactly the trusted boundaries the manifest declares."""
    name = entry['name']
    proved = run(program, proof=True, skolem_genid=SKOLEM_GENID)
    report = proved.proof_report
    if not report or not report['valid'] or not report['steps'] or not report['claims']:
        raise AssertionError(f'{name}: no valid nonempty proof')
    if output.halt_code != entry.get('halt_code') or proved.halt_code != output.halt_code:
        raise AssertionError(f'{name}: unexpected halt code')
    if output.answers != proved.answers:
        raise AssertionError(f'{name}: proof changed the answers')
    trusted = sorted({item['kind'] for item in report['trusted']})
    if trusted != sorted(entry['trusted']):
        raise AssertionError(f'{name}: unexpected proof obligations {trusted}')
    return proved


def evaluate(entry):
    program = load_example(entry)
    output = run(program, skolem_genid=SKOLEM_GENID)
    proved = certify(entry, program, output)
    return {'output': output.stdout, 'proof': proved.proof, 'check': check_report(proved.proof_report)}
