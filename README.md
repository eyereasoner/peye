# peye

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.17-blue.svg)](https://pypi.org/project/peye/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23191223-blue.svg)](https://doi.org/10.5281/zenodo.23191223)

<img src="https://josd.github.io/images/eye.png" alt="EYE" width="100">

*peye — reasoning you can see.*

A standalone, dependency-free **Python rule language** with forward and backward
reasoning and checkable proofs.

**[Playground](https://eyereasoner.github.io/peye/playground/)** ·
**[Examples](https://eyereasoner.github.io/peye/examples/)** ·
**[Example decks](https://eyereasoner.github.io/peye/examples/deck/)** ·
**[Specification](https://eyereasoner.github.io/peye/SPEC)** ·
**[Conformance suite](conformance/)** ([run it in your browser](https://eyereasoner.github.io/peye/playground/conformance.html)) ·
**[PyPI](https://pypi.org/project/peye/)**

Most software computes an answer and the reasoning evaporates. peye makes a
different bargain: **an answer can arrive together with the reasoning that
supports it, in a form another program can check.** You write facts and rules;
peye draws conclusions, and every conclusion can come with a proof that a
separate checker verifies against your program.

- [The idea in a few lines](#the-idea-in-a-few-lines)
- [Run it](#run-it)
- [Writing programs](#writing-programs)
- [Proofs, and what checking one means](#proofs-and-what-checking-one-means)
- [Checking the translation](#checking-the-translation)
- [From Python](#from-python)
- [The examples](#the-examples)
- [What is deliberately absent](#what-is-deliberately-absent)
- [The name](#the-name)

## The idea in a few lines

```python
from peye import *

fact(human('socrates'))
forward(mortal(X), human(X))
```

A fact and a rule. peye concludes `mortal('socrates')`. Ask for the reasoning
and you get a document that names the fact it used, the rule it applied, and
the substitution that connects them:

```python
mortal('socrates')

clause(1, fact(human('socrates')))
clause(2, forward(mortal(X), human(X)))

step(mortal('socrates'), rule(2), {'X': 'socrates'}, [human('socrates')])
step(human('socrates'), fact(1), {}, [])
```

That proof is itself Python, one expression per line, and a checker that never
consults the reasoner re-establishes every step against the program. Save the
two lines above, with their import, as `socrates.py` and try it:

```sh
python -m peye --proof socrates.py | python -m peye --check-proof - socrates.py
```

The checker prints a report ending in `verdict('checked')`. The certificate for
a ten-thousand-step derivation works exactly the same way.

What a checked derivation adds is a place for disagreement to land. When a
conclusion is wrong, there are only three possibilities, and a proof tells you
which: the inference was invalid, the rule did not say what you meant, or the
input fact was wrong. A checked proof settles the first, so you can spend your
attention on the other two.

## Run it

Python 3.9 or newer. No dependencies, no build step. From the root of a
checkout:

```sh
python -m peye examples/socrates.py
python -m peye --proof examples/socrates.py
python -m peye --proof examples/socrates.py | python -m peye --check-proof - examples/socrates.py
python -m unittest discover -s tests
```

To use peye from anywhere, install it; an editable install keeps using the
checkout, so your edits take effect at once:

```sh
pip install -e .
peye --proof examples/socrates.py
python examples/socrates.py --proof
```

Once peye is installed, a program is also a script: `python program.py` runs
it with the same options as `peye program.py`. Run `peye --help` for the full
command line, which [SPEC §14](SPEC.md#14-command-line) describes.

Or in the browser: the [playground](https://eyereasoner.github.io/peye/playground/)
edits, runs and checks any example, with peye running in the page through
Pyodide. To run it from a checkout, serve it (`python -m http.server`) and open
`/playground/`.

## Writing programs

A program is a Python module that starts with `from peye import *` and states
one clause per call:

| Call | Meaning |
| --- | --- |
| `fact(Head)` | `Head` holds. |
| `forward(Head, *Body)` | Whenever `Body` holds, conclude `Head`, until nothing new follows. Several conclusions join with `&`. |
| `backward(Head, *Body)` | `Head` holds when `Body` does, decided when a goal asks for it. |
| `query(*Body)` | Publish every instance of `Body` that holds. |
| `contradiction(*Body)` | Stop with exit code 65 when `Body` holds: an integrity constraint. |
| `facts_from(path)` | State every expression of a saved document as a fact. |

The two kinds of rule compose. A forward rule's body may call backward
definitions, and a backward goal may use facts that forward reasoning
established, so you let knowledge accumulate and then ask a focused question:

```python
from peye import *

fact(parent('alice', 'bob'))
fact(parent('bob', 'carol'))

forward(ancestor(X, Y), parent(X, Y))
forward(ancestor(X, Z), ancestor(X, Y), parent(Y, Z))

backward(related(X, Y), ancestor(X, Y))
backward(related(X, Y), ancestor(Y, X))

query(related('alice', 'carol'))
```

With nothing asked, a run prints the facts it derived; `query(...)` asks the
program's own questions, and `--goal "Goal"` asks from outside instead.

**Nothing to declare.** A name the program uses without defining it is a
variable when it starts with a capital or an underscore, like `X` or `_Rest`,
and a predicate otherwise, like `parent`. Python's builtins keep their meaning
in ordinary Python code, so a program can compute with `int`, `getattr` or
`sorted`; inside a statement such as `fact(type('socrates', 'human'))` a
builtin name is a predicate, except for the few a program computes with there:
`print`, `range`, `len`, `list`, `dict`, `set`, `tuple`, `str`, `enumerate`,
`zip`, `sorted`, `reversed`, `isinstance`, `open`, `repr`, `chr`, `ord`,
`iter`, `any`, `all`, `map` and `filter`. A program that wants one of those as
a predicate says so, `range = preds('range')`. A call of
an undeclared predicate on its own, such as a misspelled `fcat(p(1))`, states
nothing, so peye stops with an error instead of ignoring it.

**Terms are Python values.** An atom is a string, `'socrates'`; a number is an
`int` of any size or a `float`; a list is a list, and `[H, *T]` has head `H`
and tail `T`; a compound term is a call, `parent('alice', 'bob')`; and `_` is a
fresh variable at every occurrence. Goals join with `&` (and), `|` (or) and `~`
(not), alongside `call`, `once` and `findall`. Python reads `&` and `|` before
comparisons, so write `(X > 1) & (Y < 2)`; a chained comparison such as
`X > 1 & Y < 2` stops the program with an explanation instead of meaning
something else.

**Numbers are Python's.** Integers are exact and unbounded, so the Fibonacci
example computes F(10000), a 2,090-digit integer, exactly. An expression means
what it means in Python: `4 / 2` is `2.0`, `//` and `%` are floor division and
modulo, `round` rounds half to even. `1` and `1.0` do not unify, yet compare
exactly. A result that is not a finite real number stops the run rather than
becoming a value.

The primitives (`unify`, `is_`, `eq`, comparisons, type tests, `functor`,
`univ`, `atom_concat` and the rest) are listed in [SPEC §5](SPEC.md#5-goals-controls-and-primitives),
and the arithmetic functions in [SPEC §6](SPEC.md#6-arithmetic). Everything
else, such as membership, mapping or graph traversal, is written as ordinary
clauses.

**Domains get representations, not syntax.** peye has no built-in notion of
RDF or of anything else: IRIs, typed literals, triples and quoted graphs are
just terms, such as `literal(V, lang(L))` or `triple(S, P, O)`. A forward head
may contain variables its body never binds; they become `'sk_0'`, `'sk_1'`, ...
within each conclusion, which keeps conclusions deduplicated and stable.

## Proofs, and what checking one means

A proof holds claims, the source clauses it displays, and one inference record
per step. The checker establishes seven conditions:

| | Condition | What it establishes |
| --- | --- | --- |
| **C1** | resolution | Every step is an instance of a clause of the program, with conclusion and premises agreeing under one substitution |
| **C2** | well-foundedness | The derivation has no cycles |
| **C3** | justification | Every step's justification is known, well-formed and unique |
| **C4** | coverage | Every claim and every premise is accounted for |
| **C5** | re-decision | Built-in calculations are recomputed rather than trusted |
| **C6** | boundary consistency | No trusted absence or collection is contradicted by the evidence at hand |
| **C7** | relevance | Every claim answers the question asked, and every step serves a claim |

Two properties make this worth more than a log. **The checker follows the
certificate:** it never calls the reasoner to fill a gap, so a missing step
fails the check rather than being quietly re-derived. **The source is the
authority:** the clauses a proof displays cannot override the program, so you
cannot smuggle a rule into a proof, nor pad it with steps no claim needs.

The report is Python data too, so one program's evidence is material another
program can reason over, with `facts_from('report.py')`:

```python
condition('C1', 'resolution', 'ok', 2)
condition('C2', 'well_founded', 'ok', 2)
condition('C3', 'justification', 'ok', 2)
condition('C4', 'coverage', 'ok', 2)
condition('C5', 're_decision', 'ok', 0)
condition('C6', 'boundary_consistency', 'ok', 0)
condition('C7', 'relevance', 'ok', 3)
steps(2)
verified(2)
recomputed(0)
composed(0)
trusted(0)
claims(1)
verdict('checked')
```

Failures appear as `failed(N)` outcomes with `failure(Condition, Conclusion,
Detail)` facts, an invalid proof gives `verdict(failed(N))` and exit code 1,
and `--json` gives the same report as JSON. Proofs are read with Python's `ast`
module and never executed, so checking a proof from someone else runs none of
their code. Every proof peye generates is checked before it is returned.

**Honesty about absence.** A negation (`~`) says a search found nothing, and a
collection (`findall`) that it found exactly these answers. Neither can be
proved the way a derivation can, so each becomes an explicit `'absent'` or
`'collected'` obligation in the report, and `--strict-proof` rejects any proof
that leans on one. What the checker can do is refute one: an absence fails C6
when a fact of the program, a step of the proof or a recomputed primitive is a
solution after all, and a collection fails when such a solution is missing
from its list. A valid proof with obligations is valid *conditional on* them,
and the report says where.

## Checking the translation

A checked proof shows that the conclusions follow from the program. It cannot
show that the program says what the law, the policy or the textbook says; the
person who knows the source has to judge that. What peye can do is point at the
parts of a program that make no difference to its conclusions, because those
are where a translation is most likely to be decorative, incomplete or untested:

```python
from peye import *

fact(p('a'))
fact(q('b'))
backward(s(X), q(X))
fact(z('c'))
forward('ok', p('a'), ~s('a'))
```

```text
$ peye --unused program.py
unused(line(4), fact(q('b')))
unused(line(5), backward(s(X), q(X)))
unused(line(6), fact(z('c')))
```

A clause is listed when no conclusion's proof uses it. A negation or a
collection may consult a clause without its proof recording that search, as
`~s('a')` consults `q('b')` and the rule for `s`; for each such clause peye
leaves it out, runs the program again, and lists it only when the conclusions
stay the same. The example programs `research-portal.py` and
`package-holiday.py` list no clauses.

## From Python

```python
from peye import check_proof, load_text, run

socrates = load_text("""
from peye import *
fact(human('socrates'))
forward(mortal(X), human(X))
""")
result = run(socrates, goal='mortal(X)', proof=True)
print(result.answers)                                  # ["mortal('socrates')"]
print(result.bindings)                                 # [{'X': "'socrates'"}]
print(check_proof(socrates, result.proof)['valid'])    # True
```

`load('program.py', ...)` loads program files and `load_text(source)` source
text. `run()` returns a `Result` with `answers`, `bindings`, `inferred`,
`stdout`, `proof`, `proof_report`, `stats` and `halt_code`; options are `goal`,
`goals`, `proof`, `max_depth` (1000000), `max_iterations` (1000 per stratum)
and `max_inferences` (1000000), and exceeding a bound raises `PeyeError` rather
than return a partial result. `check_report(report)` formats a report and
`read_term(text)` reads a term back. A goal given as text reads a bare name as
a variable, so a goal with no arguments is written `p()` or `'p'`.

## The examples

The [example collection](https://eyereasoner.github.io/peye/examples/) is 61
complete programs, each with its conclusions, proof and C1-C7 report saved
beside it (`examples/output/`, `examples/proof/`, `examples/check/`), and a
[card deck](https://eyereasoner.github.io/peye/examples/deck/) that explains it
for a wide audience.

These are meant to be edited: change a fact, run it, look at what changed.
Because the artifacts are saved, you can see exactly what your change did:

```sh
python -m unittest discover -s tests -v                      # everything, one line per test as it runs
python tools/update_examples.py                              # regenerate artifacts after an intended change
python tools/timings.py --sort                               # load, run, prove and check times, slowest first
python conformance/run.py                                    # the conformance suite of SPEC.md
```

## What is deliberately absent

Cut, conditional commitment, mutable databases, attributed variables,
constraint libraries, tabling, and filesystem or network built-ins. Several of
these omissions are load-bearing: without cut and without a mutable database, a
derivation is a function of the program and its input, which is what makes a
certificate meaningful. A program is free to use Python to *compute* its
clauses (read a CSV, loop over a range), but once stated a clause is a term,
and reasoning over it calls no Python code of yours. Undefined predicates fail,
under the closed-world convention. How the engine itself works is described in
[SPEC Appendix C](SPEC.md#appendix-c-implementation-notes).

Begin with one question and a few facts. Give the relationships names, write
the rules you already believe, and let the program show you what they imply.
The first *unexpected* answer is often worth the most, because it points at a
specific rule or assumption to revisit.

## The name

**peye** joins a *p*, from the Prolog its reasoning comes from, to *eye*, after
the [EYE](https://github.com/eyereasoner/eye) family of reasoners it belongs
to. And said aloud it sounds like *py*: in peye everything, from the rules and
the data to the proofs and the check reports, is done in Python.

## License

[MIT](LICENSE.md)
