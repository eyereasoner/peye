"""The version of peye, wherever it is written.

    python tools/version.py                 print the version
    python tools/version.py check           list every place that disagrees with it
    python tools/version.py bump patch      raise it everywhere (also minor, major)

peye/__init__.py holds the version. pyproject.toml, the README's PyPI badge,
and every "peye X.Y.Z" in the Markdown documentation state it too, so a
release changes them all at once, and a test fails when one of them, or a new
mention, has fallen behind.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = r'(\d+\.\d+\.\d+)'
# Each fixed place, as a file and a pattern whose group is the version.
PLACES = [
    ('peye/__init__.py', re.compile(r"^__version__ = '" + VERSION + "'$", re.MULTILINE)),
    ('pyproject.toml', re.compile(r'^version = "' + VERSION + '"$', re.MULTILINE)),
    ('README.md', re.compile(r'img\.shields\.io/badge/pypi-v' + VERSION + r'-blue\.svg')),
]
# In the Markdown documentation, every mention of a peye version.
MENTION = re.compile(r'\bpeye v?' + VERSION + r'\b')
SKIPPED = {'.git', '__pycache__', 'build', 'dist', '.venv', 'node_modules'}


def read(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as handle:
        return handle.read()


def current():
    return PLACES[0][1].search(read(PLACES[0][0])).group(1)


def documents():
    """Every Markdown file of the repository, relative to its root."""
    found = []
    for directory, subdirectories, files in os.walk(ROOT):
        subdirectories[:] = sorted(d for d in subdirectories if d not in SKIPPED)
        for name in sorted(files):
            if name.endswith('.md'):
                found.append(os.path.relpath(os.path.join(directory, name), ROOT))
    return found


def occurrences():
    """(path, line, version) for every place a version is written."""
    found = []
    for path, pattern in PLACES:
        text = read(path)
        matches = list(pattern.finditer(text))
        if not matches:
            found.append((path, 0, None))
        for match in matches:
            found.append((path, text.count('\n', 0, match.start()) + 1, match.group(1)))
    for path in documents():
        text = read(path)
        for match in MENTION.finditer(text):
            found.append((path, text.count('\n', 0, match.start()) + 1, match.group(1)))
    return found


def check():
    """Every place whose version is not the current one, as text."""
    version = current()
    return [f'{path}:{line}: ' + (f'states {found}, not {version}' if found else 'states no version')
            for path, line, found in occurrences() if found != version]


def set_version(new):
    old = current()
    paths = [path for path, _ in PLACES] + documents()
    for path in dict.fromkeys(paths):
        text = read(path)
        updated = text
        for place, pattern in PLACES:
            if place == path:
                updated = pattern.sub(lambda m: m.group(0).replace(m.group(1), new), updated)
        if path.endswith('.md'):
            updated = MENTION.sub(lambda m: m.group(0).replace(m.group(1), new), updated)
        if updated != text:
            with open(os.path.join(ROOT, path), 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(updated)
    return old


def bumped(version, kind):
    major, minor, patch = map(int, version.split('.'))
    return {'major': f'{major + 1}.0.0', 'minor': f'{major}.{minor + 1}.0',
            'patch': f'{major}.{minor}.{patch + 1}'}[kind]


def main(argv):
    if not argv:
        print(current())
        return 0
    if argv[0] == 'check':
        problems = check()
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    if argv[0] == 'bump' and len(argv) == 2 and argv[1] in ('major', 'minor', 'patch'):
        problems = check()
        if problems:
            print('the version disagrees with itself; fix these first:', *problems, sep='\n  ', file=sys.stderr)
            return 1
        new = bumped(current(), argv[1])
        set_version(new)
        print(new)
        return 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
