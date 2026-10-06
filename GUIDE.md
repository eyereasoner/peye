# Make reasoning something you can see

![EYE](https://josd.github.io/images/eye.png)

*peye — reasoning you can see.*

There is a particular satisfaction in understanding *why* something is true.
You can follow the steps. You can point at the assumptions. You can change one
fact and watch what follows. The conclusion stops being something you have to
take on trust and becomes something you can work with: explain to a colleague,
challenge, correct, build on.

Most software does not work that way. A program computes an answer and the
reasoning evaporates. If you want to know why the answer came out as it did,
you read the code, or you add logging, or you ask the person who wrote it.

peye is a small rule language, written in and for Python, built on a different
bargain: **an answer can arrive together with the reasoning that supports it,
in a form another program can check.**

---

## Contents

- [The idea in a few lines](#the-idea-in-a-few-lines)
- [Why this matters](#why-this-matters)
- [Two directions of reasoning](#two-directions-of-reasoning)
- [What you can say](#what-you-can-say)
- [Proofs, and what checking one means](#proofs-and-what-checking-one-means)
- [Where it is honest about not knowing](#where-it-is-honest-about-not-knowing)
- [Checking the translation, not just the reasoning](#checking-the-translation-not-just-the-reasoning)
- [The examples](#the-examples)
- [Using it from Python](#using-it-from-python)
- [How it works inside](#how-it-works-inside)
- [What is deliberately absent](#what-is-deliberately-absent)
- [Start with a question](#start-with-a-question)

---

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

That document is itself Python, one expression per line, and every line reads
back as the same term. You can read it, store it, send it to someone else, and
— this is the part that matters — hand it to a checker that re-establishes
every step against the program it came from. It is data for that checker, not
a program to run: the checker parses it with Python's `ast` module and never
executes it, and `clause` and `step` are reserved for its records, so a
program can never conclude something that reads as one. Save the program from
above as `socrates.py` and try it:

```sh
python -m peye --proof socrates.py | python -m peye --check-proof - socrates.py
```

The checker prints a report ending in `verdict('checked')`.

You can understand the whole language before you finish a cup of coffee, and
the certificate for a ten-thousand-step derivation works exactly the same way
as the one above.

## Why this matters

Writing rules down is already valuable before anything is derived. Writing a
rule forces you to decide what you mean. Writing a fact forces you to say what
you actually know. Writing a query forces you to state what you want to learn.
A program becomes a place where a team's understanding takes a precise,
inspectable form instead of living in prose, spreadsheets and habit.

The questions that suit this are the ordinary ones. Which records satisfy a
policy? Which concepts roll up into a reporting category? Which events produced
this balance? Which route connects two airports within a stopover budget? Has
this person passed a given age on a given date?

What a checkable derivation adds is a place for disagreement to land. When a
conclusion is wrong, there are only three possibilities, and a proof tells you
which: the inference was invalid, the rule did not say what you meant, or the
input fact was wrong. Without the derivation those three failures look
identical from the outside, and the argument goes in circles.

A checked derivation establishes what follows **from the source you supplied**.
It does not make your model right. That boundary is a feature: it separates
"did the machine reason correctly" from "is this the right model", and lets you
settle the first question so you can spend your attention on the second.

## Two directions of reasoning

peye has two kinds of rule, and they compose.

**Forward rules** use `forward(Head, *Body)`. They materialize consequences
until nothing new appears — a fixpoint. This is how you build a closure:
everything that follows from what you know.

**Backward rules** use `backward(Head, *Body)`. They define a relation that is
explored when a question asks for it: goal-directed search, as in Prolog.

A forward rule's body may call backward definitions. A backward goal may use
facts that forward reasoning established. You let knowledge accumulate, then
ask a focused question about it:

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

The closure establishes ancestry once. The query expresses the relationship
you want to inspect. Each part has one job.

Output follows from how you ask. With nothing asked, the newly materialized
facts are printed. `query(Goal)` asks a question: it publishes each instance
of `Goal` it can establish. A program contains clauses, and a query is one of
them. `--goal "Goal"` asks from outside instead, and then the program's own
queries stay quiet. `contradiction(Body)` declares a contradiction: when its
body holds, the run stops with exit code 65 — an integrity constraint that
fails loudly.

## What you can say

A program is a Python module that begins with `from peye import *` and then
states one clause per call, in order. There is nothing to declare: a name the
program uses without defining it is a variable when it starts with an
uppercase letter or an underscore, like `X` or `_Rest`, and a predicate
otherwise, like `parent`. That holds for names Python itself would know, such
as `type` or `sum`, except for the few builtins a program uses to compute
clauses — `print`, `range`, `len`, `list`, `dict`, `set`, `tuple`, `str`,
`enumerate`, `zip`, `sorted`, `reversed`, `isinstance`, `open`, `repr`, `chr`,
`ord`, `iter`, `any`, `all`, `map` and `filter` — and the capitalized ones such
as `ValueError`. A program that wants a predicate with one of those names says
so, `range = preds('range')`, and `vars('...')` names variables explicitly
the same way. A call of an undeclared predicate on its own, such as a
misspelled `fcat(p(1))`, states nothing, so peye stops with an error instead of
ignoring it.

| Call | Meaning |
| --- | --- |
| `fact(Head)` | `Head` holds. |
| `forward(Head, *Body)` | Whenever `Body` holds, conclude `Head`; several conclusions join with `&`. |
| `backward(Head, *Body)` | `Head` holds when `Body` does, decided when a goal asks. |
| `query(*Body)` | Publish every instance of `Body` that holds. |
| `contradiction(*Body)` | Stop with exit code 65 when `Body` holds. |
| `facts_from(path)` | State every expression of a saved document as a fact. |

Terms are Python values. An atom is a string, `'socrates'`; a number is an
`int` of any size or a `float`; a list is a list, and `[H, *T]` is a list with
head `H` and tail `T`; a compound term is a call of a predicate,
`parent('alice', 'bob')`; `_` is an anonymous variable, a new one at every
occurrence. A compound term whose name is not a Python identifier is written
`struct('name', Arg, ...)`. `list('abc')` is a list of one-character atoms,
because that is what Python makes of it.

The controls are conjunction `A & B`, disjunction `A | B`, negation `~A` (or
`not_(A, B, ...)`), `call(G)`, `once(G)` and `findall(Template, Goal, List)`.
Python reads `&` and `|` before comparisons, so parenthesize a comparison
inside them: `(X > 1) & (Y < 2)`. Without them Python reads
`X > 1 & Y < 2` as a chained comparison, and since peye refuses to treat a
term as a truth value, that stops the program with an explanation instead of
meaning something else.

The native predicates are the ones below. In a flow pattern, `+` marks an
argument that must be bound when the goal runs, `-` one that must be unbound,
`?` one that may be either, and `@` one that is only inspected. A predicate
with two patterns works in both directions. Calling a predicate outside its
patterns usually stops the run with an error rather than failing quietly.

| Predicate | Flow pattern | What it does |
| --- | --- | --- |
| `true`, `fail`, `false` | | Succeeds, fails, fails. |
| `unify(?X, ?Y)` | | Unifies `X` and `Y`. |
| `not_unify(@X, @Y)` | | Succeeds when `X` and `Y` do not unify; binds nothing. |
| `identical(@X, @Y)` | | Succeeds when `X` and `Y` are identical, variables included. |
| `not_identical(@X, @Y)` | | Succeeds when `X` and `Y` are not identical. |
| `compare(?Order, @X, @Y)` | | Unifies `Order` with `'<'`, `'='` or `'>'` in the standard order of terms. |
| `is_(?Value, +Expr)` | | Evaluates `Expr` and unifies the result with `Value`. |
| `eq(+E1, +E2)`, `ne(+E1, +E2)` | | Compares two evaluated expressions for equal and unequal. |
| `E1 < E2`, `E1 <= E2`, `E1 > E2`, `E1 >= E2` | `+E1 < +E2` | Compares two evaluated expressions by order. |
| `is_var(@X)`, `is_nonvar(@X)` | | Tests whether `X` is an unbound variable, or is not. |
| `is_ground(@X)` | | Tests that `X` contains no unbound variables. |
| `is_atom(@X)`, `is_number(@X)` | | Tests that `X` is an atom, or a number. |
| `is_int(@X)`, `is_float(@X)` | | Tests that `X` is an integer, or a float. |
| `is_compound(@X)` | | Tests that `X` is a compound term; a nonempty list is one. |
| `functor/3` | `functor(+Term, ?Name, ?Arity)`<br>`functor(-Term, +Name, +Arity)` | Takes a term apart into name and arity, or builds a term with fresh arguments. |
| `arg/3` | `arg(+N, +Term, ?Arg)` | Unifies `Arg` with the `N`th argument of `Term`, counting from 1. |
| `univ/2` | `univ(+Term, ?List)`<br>`univ(-Term, +List)` | Converts between a term and the list of its name and arguments. |
| `atom_chars/2` | `atom_chars(+Atom, ?Chars)`<br>`atom_chars(-Atom, +Chars)` | Converts between an atom and its list of one-character atoms. |
| `atom_codes/2` | `atom_codes(+Atom, ?Codes)`<br>`atom_codes(-Atom, +Codes)` | Converts between an atom and its list of character codes. |
| `atom_length/2` | `atom_length(+Atom, ?Length)` | Unifies `Length` with the number of characters in `Atom`. |
| `atom_concat/3` | `atom_concat(+A, +B, ?AB)`<br>`atom_concat(?A, ?B, +AB)` | Joins two atoms, or enumerates every way to split `AB` in two. |

An arithmetic expression means what the same expression means in Python:
`+`, `-`, `*`, `/`, `//`, `%`, `**`, the bitwise `&`, `|`, `^`, `~`, `<<` and
`>>`, Python's `abs`, `min`, `max`, `round`, `int` and `float`, and from
`math` the functions `floor`, `ceil`, `trunc`, `sqrt`, `isqrt`, `exp`, `log`,
`log2`, `log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sinh`,
`cosh`, `tanh`, `hypot`, `degrees`, `radians`, `fmod`, `copysign`, `gcd`,
`lcm` and `pow`, and the constants `pi`, `e` and `tau`. Like any undefined
name, `sqrt` in `is_(R, sqrt(X))` is supplied by peye, and the expression is
evaluated when the goal runs. A program that also wants these as Python
functions, computing at once on numbers, imports them from `peye.functions`. The definitions are in
[peye/arith.py](https://github.com/eyereasoner/peye/blob/main/peye/arith.py) and
[peye/builtins.py](https://github.com/eyereasoner/peye/blob/main/peye/builtins.py).

Everything else — membership, mapping, sorting, graph traversal, formula
inspection — is written as ordinary clauses rather than added to the engine. A
new native operation has to be justified by an example that genuinely cannot be
a clause.

That restraint is what keeps the language learnable, and it reaches further
than it looks. These are the patterns the examples are built from:

| Reasoning pattern | How you write it |
| --- | --- |
| Structured facts, variable predicates | `t(S, P, O)` |
| Forward implication | `forward(Head, *Body)` |
| Backward definition | `backward(Head, *Body)` |
| Several conclusions at once | `forward(H1 & H2, *Body)` |
| Recursion over a graph | Recursive forward rules |
| Numeric tests and expressions | Comparisons and `is_` |
| Alternatives | Several clauses, or `A \| B` |
| Closed absence checks | Ground `~Goal` in a higher stratum |
| Collection and aggregates | `findall`, then list clauses |
| Existence with local variables | Collect matches, test for a nonempty list |
| External data | A separate predicate such as `base/3` |
| Inference plus union views | Derived predicates with backward view definitions |
| Quoted triples and graphs | `triple(S, P, O)` and `graph(Triples)` |
| Typed or language-tagged values | Structured `literal(V, ...)` terms |
| Per-binding witnesses | Explicit `record(Rule, Binding)` terms |
| Ordered events and state changes | Indexed facts, recursive transition relations |
| Asking a goal | `query(Goal)`, or `--goal` from outside |
| Integrity constraints | `contradiction(*Body)` |

### Numbers are Python's

Integers are unbounded and never pass through a floating-point value, so the
Fibonacci example computes F(10000) — a 2,090-digit integer — exactly, and the
Ackermann example A(4, 2), with 19,729 digits. Floats are IEEE-754 doubles.
`/` is true division, so `4 / 2` is `2.0`; `//` and `%` are floor division
and modulo; `**` is exact on integers with a nonnegative exponent; `round`
rounds half to even. Integers and floats are distinct terms — `1` and `1.0` do
not unify — yet comparison between them is exact, and so is the standard order
of terms, which orders numbers by value and places a float before an integer of
equal value. A result that is not a finite real number, such as `1 / 0`,
`sqrt(-1)` or a power too large to hold, stops the run with an error rather
than becoming a value.

### Output you can read back

Every term is written in one canonical spelling, and that spelling is a
Python expression: an atom is a string literal, a number a numeric literal, a
variable a name, a compound term a call, a list a list display with `*T` for
an open tail. Operators keep their Python spelling and precedence, so
`is_(X, Y + 1)` and `(X > 1) & (Y < 2)` read as you would write them, with
parentheses only where Python needs them. Conclusions, proofs and check reports
are all written this way, one expression per line, and the reader in
[peye/reader.py](https://github.com/eyereasoner/peye/blob/main/peye/reader.py)
turns each line back into the same term.

### Representing a domain

peye has no built-in notion of RDF, or of anything else. Domains get
representations rather than syntax:

```python
from peye import *

fact(base('alice', 'parent_of', 'bob'))
backward(t(S, P, O), base(S, P, O))
forward(t(C, 'child_of', P), t(P, 'parent_of', C))
forward(allowed(C), t(C, 'child_of', 'alice'), ~t(C, 'blocked', 'true'))
```

`base/3` is external data; `t/3` is the union view. The engine attaches no
special meaning to either name — the separation is yours, and it is what keeps
the base graph isolated from inference. IRIs, typed literals, language tags,
triple terms and quoted formulas are just terms: `iri(I)`,
`literal(V, datatype(D))`, `literal(V, lang(L))`, `triple(S, P, O)`,
`graph(Triples)`.

A forward head may contain variables the body never binds. Those become
`'sk_0'`, `'sk_1'` and so on within each conclusion, with sharing preserved. If
you want a distinct witness per rule and binding, say so explicitly —
`blank('rule_name', X)` in the head. This is deliberately not the same as
minting a fresh blank node on every firing: it keeps conclusions deduplicated
and stable across runs.

## Proofs, and what checking one means

A proof document holds claims, the source clauses it displays, and one
inference record per step. `check_proof(program, document)` establishes seven
conditions:

| | Condition | What it establishes |
| --- | --- | --- |
| **C1** | resolution | Every step is an instance of a clause in the supplied source, with conclusion and premises agreeing under one substitution |
| **C2** | well-foundedness | The derivation has no cycles |
| **C3** | justification | Every step's justification is known, well-formed and unique |
| **C4** | coverage | Every claim and every premise is accounted for |
| **C5** | re-decision | Pure primitive results are recomputed independently |
| **C6** | boundary consistency | No trusted absence or collection is contradicted by the source or the certificate |
| **C7** | relevance | Every claim answers a goal that was asked, and every step serves a claim |

Two properties make this worth more than a log.

**The checker follows the certificate.** It never calls the solver to fill a
gap. If a step is missing, the check fails; it does not quietly re-derive the
answer. Checking is a genuinely separate activity from reasoning, and
[peye/proof.py](https://github.com/eyereasoner/peye/blob/main/peye/proof.py) has no dependency on the solver.

**The source is the authority.** A certificate displays the clauses it used,
but those display records cannot override the program. If they disagree with
the source you check against, C1 fails. You cannot smuggle in a rule by writing
it into the proof, and you cannot pad it either: C7 rejects a step that no
claim uses and a claim that answers no goal.

The report is itself Python data:

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

So one program's evidence is material another program can reason over:
`facts_from('report.py')` states each line as a fact. A workflow can accept
only certain verdicts, collect unresolved obligations, or attach a verified
derivation to a generated report. Failures appear as `failed(N)` outcomes with
`failure(Condition, Conclusion, Detail)` facts; an invalid certificate gives
`verdict(failed(N))` and CLI exit code 1. A coverage count of zero means that
condition had nothing to check. `--json` gives the same report as JSON.

Clause numbers refer to the supplied program's clauses in source order, so
check a saved proof against the program that produced it. A proof made with
`--goal` answers that goal rather than the program's own, so pass the same
`--goal` with `--check-proof`, or `goals` to `check_proof`, or C7 rejects its
claims.

## Where it is honest about not knowing

Two things in the language cannot be certified the way a resolution step can.

**Negation** (`~`) says a search finished without finding anything.
**Collection** (`findall`) says a search found exactly these answers. Both are
claims about the *absence* of further results, and a certificate cannot
demonstrate an absence the way it demonstrates a derivation.

peye does not paper over this. Each one is recorded as an explicit `'absent'`
or `'collected'` boundary, listed in the report as an obligation, and
`--strict-proof` rejects any proof that leans on one. What the checker can do
is refute a boundary, and that is C6. An absence fails when a source fact, a
step of the same certificate or a recomputed primitive is a solution after all;
a collection fails when such a solution is missing from its list. A boundary C6
cannot decide, such as an absence over a conjunction with shared variables,
simply stays an obligation. A valid proof carrying obligations is exactly that:
valid *conditional on* those obligations, and the report tells you where. You
get to decide whether that is good enough for the task in front of you.

The same honesty applies elsewhere. A mode test such as `is_var(X)` followed by
`unify(X, 'a')` cannot be represented faithfully by recording only the final
substitution, so proof generation refuses rather than emitting something
misleading. And every generated proof is checked before it is returned — the
language does not hand you a certificate it has not verified.

## Checking the translation, not just the reasoning

A checked proof shows that the conclusions follow from the program. It cannot
show that the program says what the law, the policy or the textbook says.
Someone turned that text into facts and rules, and that translation can be
wrong while every proof checks. No tool can certify it; the person who knows
the source has to judge. What peye can do is point at the parts of a program
that make no difference to its conclusions, because those are where a
translation is most likely to be decorative, incomplete or untested.

`--unused` lists those clauses. Take this program:

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

A clause is listed when no conclusion's proof uses it. Here `'ok'` rests on
`p('a')` and on the rule that concludes it, so those two are not listed;
nothing reads `z('c')`. One case needs more: a negation (`~`) or a collection
(`findall`) may consult a clause without its proof recording that search.
`q('b')` and the rule for `s/1` are consulted by `~s('a')`, so for each of
them peye leaves the clause out, runs the program again, and lists it only
because the conclusions stay the same.

A listed clause deserves a look against its source: no fact in the program
exercises it, or it encodes something no conclusion depends on. The check needs
nothing but the program, and its answer is about the program's own facts; with
other facts, a listed clause may matter. The example programs
`research-portal.py` and `package-holiday.py` list no clauses.

## The examples

The [example collection](https://eyereasoner.github.io/peye/examples/) is 59 complete programs. Each one
ships with its conclusions, its proof and its C1–C7 check report, all saved to
disk:

```text
examples/socrates.py           Source program
examples/output/socrates.py    Conclusions
examples/proof/socrates.py     Conclusions with proof records
examples/check/socrates.py     C1-C7 proof-check report
```

| Examples | What they demonstrate |
| --- | --- |
| `socrates`, `backward` | Basic inference and mixed chaining |
| `deep-taxonomy-10` through `deep-taxonomy-10000` | A subclass chain whose branches lead nowhere, at four sizes |
| `reachability`, `shortest-path`, `path-discovery` | Cyclic graph closure, weighted paths and airport routes with bounded stopovers |
| `fibonacci`, `lists` | Recursive computation with exact integers, and list operations |
| `strings`, `unification`, `alternatives` | Unicode, structural matching and goal-directed choices |
| `graphs`, `terms`, `witnesses` | Separate graph views, quoted data and structured witnesses |
| `inventory`, `dog-license`, `permissions`, `state-transitions`, `integrity` | Aggregation, counted policies, policy checks, event logs and constraints |
| `schema-inference`, `family-cousins`, `paraconsistent-animals` | Schema rules, family branches and conflicting observations |
| `flat-map`, `scoped-audit`, `variable-predicates` | Mapping, scoped checks and relation renaming |
| `hanoi`, `collatz`, `control-system`, `lldm`, `age` | Recursive puzzles, actuator control, a leg length measurement and calendar age checks |
| `good-cobbler`, `peano`, `expression-eval`, `complex`, `polynomial` | Structured descriptions, symbolic arithmetic, expression graphs, a complex-number domain and polynomial roots |
| `queens`, `interval-relations` | Constraint search and all thirteen interval relations |
| `bayes-diagnosis`, `policy-risk` | Normalized fault scores and ranked policy findings |
| `research-portal` | ODRL/DPV research policy, device consent and breach plans compared under two EU rulebooks |
| `package-holiday` | A tour operator's ODRL terms and the 2015 and revised Package Travel Directive, compared |
| `ackermann`, `peasant`, `sieve`, `goldbach`, `kaprekar` | Exact hyperoperations, ancient arithmetic and number-theory checks |
| `easter`, `turing`, `superdense-coding`, `teleportation` | Calendar arithmetic, a Turing machine interpreter and discrete quantum protocols |
| `zebra`, `four-color`, `wolf-goat-cabbage`, `monkey-bananas`, `gps` | Classic constraint puzzles and planning problems |
| `aunt-agatha` | Entailment: a conclusion that holds in every model of the premises |

A few are worth singling out. [Ackermann](https://github.com/eyereasoner/peye/blob/main/examples/ackermann.py) computes
A(4, 2), a number with 19,729 digits, exactly. The [zebra puzzle](https://github.com/eyereasoner/peye/blob/main/examples/zebra.py)
is Einstein's riddle solved by unification alone. [Who killed Aunt Agatha?](https://github.com/eyereasoner/peye/blob/main/examples/aunt-agatha.py)
goes a step further: rather than find one solution, it enumerates every model
of nine premises and shows that the killer is Agatha in all of them. The
[research portal](https://github.com/eyereasoner/peye/blob/main/examples/research-portal.py) combines ODRL/DPV policy
decisions with device-consent and breach plans under the EU baseline and the
original Commission Digital Omnibus proposal. It lists changes while preserving
policy refusals, planned duties and the provisions behind each assessment.
The [package holiday](https://github.com/eyereasoner/peye/blob/main/examples/package-holiday.py) applies the same pattern to
leisure: holiday cancellations under a tour operator's terms and the Package
Travel Directive before and after its 2026 revision, checked with no trusted
steps. The [airport search](https://github.com/eyereasoner/peye/blob/main/examples/path-discovery.py)
works over 7,698 airports and 37,505 connections; change the endpoints and the
stopover budget and ask again. The [interval example](https://github.com/eyereasoner/peye/blob/main/examples/interval-relations.py)
distinguishes all thirteen basic relations between two intervals. The
[policy example](https://github.com/eyereasoner/peye/blob/main/examples/policy-risk.py) carries scores, ranks, reasons and
suggested mitigations into its conclusions. The
[deep-taxonomy benchmark](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-10000.py) follows a
ten-thousand-step chain and produces a certificate in which every one of
those 10,001 steps is independently verified.

These are meant to be edited. Read one, change a fact, run it, look at what
changed. The [playground](https://eyereasoner.github.io/peye/playground/) does that in a browser: load any
example, edit it, run it, check its proof, and copy a link that reopens exactly
what you see. Add a clause. Ask a narrower question. Each example is a small
repeatable experiment, and because the artifacts are saved, you can see exactly
what your change did:

```sh
python -m unittest discover -s tests                         # everything
python -m unittest discover -s tests -p test_examples.py     # just the corpus
python tools/update_examples.py                              # regenerate artifacts after an intended change
python tools/timings.py --sort                               # load, run and prove times, slowest first
```

Tests never overwrite the saved artifacts. When you intend a change, you
regenerate and review the artifact diff alongside the source diff.
`examples/manifest.json` lists every program with its expected halt code and
permitted obligations, and the suite requires every source and every artifact
to be listed, so nothing can quietly fall out of coverage.

## Using it from Python

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

`load(path, ...)` runs program files into one `Program` and `load_text(source)`
does the same for source text; both supply the names a program leaves
undefined. `build(function)` collects the clauses a function states, with
predicates and variables named by `preds` and `vars`, since ordinary Python
code has no undefined names to fill in. A script that itself starts with
`from peye import *` is a program: with peye installed (`pip install -e .`
in a checkout), running `python program.py --proof` hands it, with its
options, to peye. The library API is imported by name, as above.

`run()` returns a `Result` with `answers`, `bindings`,
`inferred`, `stdout`, `proof`, `proof_report`, `stats` and `halt_code`.
Answers and binding values are printable Python text, which `read_term` turns
back into terms. Because a generated proof is always checked before it is
returned, `proof_report` hands you that report rather than making you check
the same document twice. A `Program` can be run many times; each run has its
own inference state.

Options are `goal`, `goals`, `proof`, `max_depth` (1000000), `max_iterations`
(1000 per stratum) and `max_inferences` (1000000). Exceeding a bound raises
`PeyeError` — a partial closure is never returned as though it were complete.
A goal is a term, or Python text such as `"mortal(X)"`; in text, a bare name is
a variable, so a goal with no arguments is written `p()` or `'p'`.

`check_report(report)` formats a full report, `verdict_text(report)` just its
verdict, and `public_report(report)` gives it as JSON-ready data.

## How it works inside

None of this needs a large implementation. The runtime has no dependencies
beyond the Python standard library and there is no build step.

| File | Responsibility |
| --- | --- |
| [peye/terms.py](https://github.com/eyereasoner/peye/blob/main/peye/terms.py) | Terms, unification, renaming, the standard order |
| [peye/writer.py](https://github.com/eyereasoner/peye/blob/main/peye/writer.py), [peye/reader.py](https://github.com/eyereasoner/peye/blob/main/peye/reader.py) | Canonical Python spelling, and reading it back without executing it |
| [peye/dsl.py](https://github.com/eyereasoner/peye/blob/main/peye/dsl.py), [peye/functions.py](https://github.com/eyereasoner/peye/blob/main/peye/functions.py) | Stating programs in Python |
| [peye/program.py](https://github.com/eyereasoner/peye/blob/main/peye/program.py) | Profile validation, clause indexing and dependency stratification |
| [peye/builtins.py](https://github.com/eyereasoner/peye/blob/main/peye/builtins.py), [peye/arith.py](https://github.com/eyereasoner/peye/blob/main/peye/arith.py) | The pure primitive profile and arithmetic |
| [peye/engine.py](https://github.com/eyereasoner/peye/blob/main/peye/engine.py) | Backward resolution, forward fixpoints, proof recording |
| [peye/proof.py](https://github.com/eyereasoner/peye/blob/main/peye/proof.py) | Certificate rendering and checking, with no solver dependency |
| [peye/cli.py](https://github.com/eyereasoner/peye/blob/main/peye/cli.py) | The command line |
| [playground/](https://github.com/eyereasoner/peye/tree/main/playground) | The browser playground, which runs the same package through Pyodide |
| [tools/](https://github.com/eyereasoner/peye/tree/main/tools) | Regenerating the saved example output, proofs and check reports |

**Search is an explicit machine, not nested host calls.** A frame is one body
being worked through; frames are immutable, so a choice point only has to
remember the frame it was created in and backtracking is a pointer assignment.
Depth is therefore bounded by `max_depth` and by memory rather than by
Python's recursion limit.

**One substitution is threaded through a search**, restored by an undo trail
when a branch fails, so an alternative costs the bindings it actually made
instead of a copy of the whole map. The trail records each name's previous
value, which also makes it safe for a dereference to shorten a chain of
variable-to-variable bindings as it walks one. Together these make an N-step
derivation cost O(N); without either it costs O(N²). One consequence worth
knowing: an answer's bindings are valid only until the next answer is
requested.

**Unification is on finite trees.** An occurs check rejects a binding that
would create a cycle. Fresh variable names are rendered injectively, so an
internal `X#1` can never be confused with a source variable named `X_1`.

**A program is Python, a document is data.** A program file is Python code
you wrote, and running it states its clauses. A conclusion file, a proof or a
check report is only ever parsed: the reader accepts literals, names, calls of
a plain name, list displays, binding dictionaries and the operators peye
writes, and nothing else, so a document cannot run code or change how another
is read.

**Stratification matches whole terms, not just predicate names.** Forward rules
that use negation or collection run only after everything they inspect has
reached its fixpoint. Because the analysis compares complete head and body
terms, two relations sharing a predicate name can occupy different strata when
their argument patterns do not overlap — which is exactly what you need when
everything is `t/3`. Positive cycles stay in one stratum; closed dependency
cycles are rejected, as are dynamic calls reachable from forward rules.

**Proof steps record the first derivation found** for each conclusion, and are
recorded only when a proof is asked for: without one, the search keeps just what
it needs to find answers. Nodes carry the terms they were built from and are
resolved once, by whoever consumes a complete answer, so a conjunction does not
re-copy the proof forest for each of its goals. Renaming a clause apart shares
every subterm that holds no variable, since terms never change once built.

## What is deliberately absent

Modules of rules, cut, conditional commitment, mutable databases, attributed
variables, constraint libraries, tabling, filesystem and network built-ins,
RDF parsers and streaming adapters.

Some of these are omissions of convenience; several are load-bearing. No cut
and no mutable database means a derivation is a function of the program and its
input, which is what makes a certificate meaningful. A program is free to use
Python to *compute its clauses* — read a CSV, loop over a range, build facts —
but once stated, a clause is a term, and reasoning over it calls no Python code
of yours.

Applications supply external data as facts. Undefined user predicates fail,
under the closed-world convention.

Minimality here means a narrow language profile and a runtime without
dependencies. It is not a claim about source size.

## Start with a question

Perhaps you have a policy spread across several documents. Perhaps there is a
graph whose relationships you keep tracing by hand. Perhaps a calculation needs
an explanation that can travel with its result.

Begin with one question and a few facts. Give the relationships names. Write
the rules you already believe. Then let the program show you what they imply.

The first answer may be small. The first *unexpected* answer is often worth
more, because it points at a specific rule or assumption to revisit. As the
model grows you accumulate a body of executable knowledge you can inspect,
test and explain.

That is the whole promise, and it is a practical one: programs whose
conclusions arrive with a story precise enough to check.
