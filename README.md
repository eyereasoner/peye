# peye

![EYE](https://josd.github.io/images/eye.png)

*peye — reasoning you can see.*

A standalone, dependency-free **Python rule language** with forward and backward
reasoning and checkable proofs.

peye turns explicit facts and rules into conclusions whose derivations can be
inspected and checked. An answer can arrive together with a certificate, and
that certificate can be verified against the program that produced it.

Facts and rules are Python:

```python
from peye import *

fact(human('socrates'))
forward(mortal(X), human(X))
```

There is nothing to declare: a name the program uses without defining it is a
variable when it starts with a capital or an underscore, like `X`, and a
predicate otherwise, like `human`. Atoms are strings.

`forward(Head, *Body)` materializes conclusions until a fixpoint.
`backward(Head, *Body)` defines a predicate evaluated when called. The two
compose: a forward body may call backward definitions, and a backward goal may
use facts that forward reasoning established.

## The thread

peye is built around one idea: **reasoning you can see**. You write facts and
rules; peye draws conclusions, forward until nothing new follows and backward
on request, and every answer can come with a proof. A separate checker verifies
that proof against the program, independently of the reasoner, and does more
than a classic proof checker:

- **The derivation:** every step is an instance of a program clause (C1),
  nothing is circular (C2), and every claim and every use is justified (C4).
- **The form (C3):** every step has exactly one justification of an allowed
  kind, in the right shape, so the report shows at once whether a proof fails
  on form or on content.
- **Recomputation (C5):** built-in calculations are redone rather than trusted.
- **Honesty about absence:** "there is nothing that …" and "these are *all* the
  answers" cannot be proved; they become explicit obligations, which the
  checker tries to refute with the evidence at hand (C6).
- **The right question (C7):** the proof answers the question asked and
  contains nothing beside it.

The report is itself Python data, and every generated proof is checked before it
is returned. Proofs are read with Python's `ast` module and never executed, so
checking a proof from someone else runs none of their code. Around that core, [59 examples](https://eyereasoner.github.io/peye/examples/)
grew, from Socrates and the zebra puzzle to a hospital research portal decided
under today's EU rules and under the Commission's Digital Omnibus proposal, and
package holiday cancellations under the 2015 and the revised Package Travel
Directive. Each has a [deck](https://eyereasoner.github.io/peye/examples/deck/)
for a wide audience and can be run in the [playground](https://eyereasoner.github.io/peye/playground/).

A proof guarantees that the conclusions follow from the rules, not that the
rules say what the law or the policy says. So `peye --unused` shows which
parts of a translation make no difference to the conclusions, and an expert
knows [where to look](https://eyereasoner.github.io/peye/GUIDE#checking-the-translation-not-just-the-reasoning).

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

Once peye is installed, a program is also a script: `python program.py`
runs it with the same options as `peye program.py`. Run `peye --help` for the
full command line.

Or in the browser: the [playground](https://eyereasoner.github.io/peye/playground/) edits, runs and checks any
example, with peye running in the page through Pyodide. To run it from a
checkout, serve it (`python -m http.server`) and open `/playground/`.

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
print(check_proof(socrates, result.proof)['valid'])    # True
```

`load('program.py')` reads a program file the same way.

## Read on

- **[Make reasoning something you can see](https://eyereasoner.github.io/peye/GUIDE)** —
  what the language is for, how to write it, what a checked proof does and does
  not establish, and how the engine works.
- **[Examples](https://eyereasoner.github.io/peye/examples/)** — 59 complete programs, each with its saved
  conclusions, proof and C1-C7 check report.
- **[Example decks](https://eyereasoner.github.io/peye/examples/deck/)** — a short card deck for every
  example, explaining it for a wide audience: the question, what peye
  concludes, why, and what the proof checker confirms.
- **[Playground](https://eyereasoner.github.io/peye/playground/)** — write a program in the browser, run it, check
  its proof, and share a link to exactly what you see.

## License

[MIT](https://eyereasoner.github.io/peye/LICENSE.md)
