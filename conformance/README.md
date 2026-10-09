# peye conformance suite

These cases test an implementation against [SPEC.md](../SPEC.md). They are
black-box: each case creates some files, runs the implementation's command
line (SPEC Section 14) and compares what it prints and its exit code with what
the specification requires. Any implementation with that command line can be
tested, not only peye.

```sh
python conformance/run.py                              # against python -m peye
python conformance/run.py --command "path/to/my-peye"  # against another implementation
python conformance/run.py -k skolem                    # cases whose name contains "skolem"
python conformance/run.py 11-checking.txt -v           # one file, listing every case
python conformance/run.py --in-process                 # peye from this checkout, without a process per case
```

The suite also runs with peye's own tests, as `tests/test_conformance.py`,
and in the browser, against the playground's peye, at
[eyereasoner.github.io/peye/playground/conformance](https://eyereasoner.github.io/peye/playground/conformance),
where each case's files, expected output and peye's output can be inspected.
`manifest.json` lists the case files in order, with the SPEC sections and
the topic of each.

## Coverage

| File | SPEC | Cases | What it tests |
| --- | --- | --- | --- |
| [03-terms.txt](03-terms.txt) | 3 | 22 | Unification, the occurs check, integers and finite floats, lists, the standard order |
| [04-programs.txt](04-programs.txt) | 4 | 40 | Statements, clause numbering, names a program leaves undefined, rejected clauses, stratification |
| [05-controls-and-primitives.txt](05-controls-and-primitives.txt) | 5 | 47 | Every control and primitive, and the errors of their flow patterns |
| [06-arithmetic.txt](06-arithmetic.txt) | 6 | 28 | Python's meaning of every operator and function, exact integers, and each error |
| [07-reasoning.txt](07-reasoning.txt) | 7 | 29 | Search order, forward rounds, Skolem terms, conclusions, halting, bounds |
| [08-canonical-text.txt](08-canonical-text.txt) | 8 | 21 | The one spelling of atoms, numbers, variables, lists, compounds and operators |
| [09-reading.txt](09-reading.txt) | 9 | 41 | What a document reader accepts, and what it must reject without running anything |
| [10-proofs.txt](10-proofs.txt) | 10 | 16 | Proof documents for every kind of justification, step order and sharing |
| [11-checking.txt](11-checking.txt) | 11, 12 | 46 | Valid proofs and proofs tampered with to break each of C1-C7, with their exact reports |
| [13-unused.txt](13-unused.txt) | 13 | 9 | Unused clauses, including those a negation or collection consults |
| [14-command-line.txt](14-command-line.txt) | 14 | 23 | Options, their combinations, standard input, errors and exit codes |

## Case format

A case file holds cases, each starting with a line `=== name`. Lines starting
with `#` before a case's blocks are comments. A case has settings, one per
line as `key: value`, followed by blocks, each starting with a line
`--- name` and running to the next `---` or `===` line:

```text
=== a fact with variables binds them
spec: 10.3
args: --proof --goal "same(1, 1)" program.py
--- program.py
from peye import *
fact(same(X, X))
--- stdout
same(1, 1)

clause(1, fact(same(X, X)))

step(same(1, 1), clause(1), {'X': 1}, [])
```

| Setting | Meaning | Default |
| --- | --- | --- |
| `spec` | The SPEC sections the case tests. | |
| `args` | The command-line arguments, split as a POSIX shell would. | `program.py` |
| `exit` | The expected exit code. | `0` |
| `stderr` | `empty`, `nonempty`, `json` (standard error is JSON), or `prefix TEXT` (it starts with `TEXT`). | not checked |
| `stdout` | `nonempty`: standard output is not empty, whatever it says. | |
| `stdout-literal` | The exact standard output as a Python string literal, for output a block cannot show. | |

| Block | Meaning |
| --- | --- |
| `--- stdin` | Standard input. Without it, standard input is empty. |
| `--- stdout` | The exact standard output. Without it, standard output is not checked. |
| `--- stdout json` | Standard output, compared as JSON data rather than as text. |
| `--- NAME` | Any other block is a file of that name, created in an empty directory where the command runs. |

Trailing empty lines of a block are not part of it; every block that is not
empty ends with one line break. In an expected output line, `…` matches any
text: the specification leaves some text to the implementation, such as the
wording of a failure's detail.

## Writing cases

Expected outputs come from the specification, not from running an
implementation. When a case and peye disagree, the specification decides
which one is wrong. While this suite was written, that found two places where
SPEC.md had to say more precisely what peye does (that `not_`, and `call` and
`once` with several goals, are notations of programs, and that answers are
reported once across all goals of a run), and one where peye did not do what
SPEC.md says (`2 ** -1` was written `2 ** (-1)`).
