# The peye Rule Language and Proof Format

```text
Title:      The peye Rule Language and Proof Format
Version:    peye 0.4.2
Status:     Informational
Author:     Jos De Roo, KNoWS office of IDLab, Ghent University - imec
Repository: https://github.com/eyereasoner/peye
```

## Abstract

peye is a rule language embedded in Python, with forward and backward
reasoning, and a proof format whose documents a separate checker verifies
against the program that produced them. This document specifies the terms
the language reasons over, how a program is stated in Python, what a program
concludes, the canonical text in which terms, conclusions, proofs and check
reports are written and read back, the proof document, the seven conditions
(C1-C7) a proof checker establishes, the check report, and the command line.

## Status of This Memo

This document is not an Internet Standards Track specification. It describes
the language and formats as implemented by peye 0.4.2, for readers who want
to write programs, produce or consume proofs and reports, or implement a
compatible reasoner or checker. Where this document and the implementation
disagree, that is a defect in one of them.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Conventions and Terminology](#2-conventions-and-terminology)
3. [Terms](#3-terms)
4. [Programs](#4-programs)
5. [Goals, Controls and Primitives](#5-goals-controls-and-primitives)
6. [Arithmetic](#6-arithmetic)
7. [Reasoning](#7-reasoning)
8. [Canonical Text](#8-canonical-text)
9. [Reading Documents](#9-reading-documents)
10. [Proof Documents](#10-proof-documents)
11. [Proof Checking](#11-proof-checking)
12. [Check Reports](#12-check-reports)
13. [Unused Clauses](#13-unused-clauses)
14. [Command Line](#14-command-line)
15. [Security Considerations](#15-security-considerations)
16. [Conformance](#16-conformance)
- [Appendix A. Document Grammar](#appendix-a-document-grammar)
- [Appendix B. Example](#appendix-b-example)
- [Appendix C. Implementation Notes](#appendix-c-implementation-notes)

---

## 1. Introduction

A peye program states facts and rules. Forward rules are applied until no
new conclusion follows; backward rules are applied when a goal asks for them.
Every conclusion can be accompanied by a proof: a document that names, for
each step, the program clause or primitive that justifies it. A checker that
never consults the reasoner verifies such a document against the program and
reports, condition by condition, what it established and what it had to take
on trust.

Programs are Python modules. Conclusions, proofs and check reports are Python
expressions, one per line, which a reader turns back into terms without
executing them.

## 2. Conventions and Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY" and "OPTIONAL" in this document
are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and
only when, they appear in all capitals.

- **Term**: a value the language reasons over (Section 3).
- **Clause**: a fact, a forward rule or a backward rule (Section 4).
- **Goal**: a term solved by resolution or by a primitive (Section 5).
- **Substitution**: a mapping from variable names to terms.
- **Instance**: a term obtained from another by applying a substitution.
- **Identical**: two terms are identical when their canonical texts
  (Section 8) are equal; variables are identical only to themselves.
- **Ground**: containing no variable.
- **Conclusion**: a term a run reports (Section 7.6).
- **Document**: text holding a sequence of expressions (Sections 9-12).
- **Reasoner**: an implementation of Sections 3-10, which checks its own
  proofs as Section 11 describes.
- **Checker**: an implementation of Sections 9, 11 and 12.

## 3. Terms

A term is one of:

| Kind | Representation | Example |
| --- | --- | --- |
| Atom | a Python `str` | `'socrates'`, `'[]'` |
| Integer | a Python `int`, of unbounded size | `42`, `-7` |
| Float | a Python `float`, an IEEE-754 binary64 value | `0.5`, `1e+22` |
| Variable | a name | `X`, `_Rest` |
| Compound | a name (an atom) and one or more argument terms | `parent('alice', 'bob')` |

A compound term is identified by its name and its arity, the number of its
arguments, written `name/arity`. An atom used as a goal has arity 0.

**Lists.** The empty list is the atom `'[]'`. A non-empty list is the
compound `'.'(Head, Tail)`. A list whose final tail is not `'[]'` is an open
list. Character text is a list of one-character atoms.

**Numbers.** Integers and floats are distinct: `1` and `1.0` MUST NOT unify.
Floats MUST be finite; no operation produces an infinity or a NaN as a term
(Section 6). Nonfinite Python values and float literals that overflow, such
as `1e999`, MUST be rejected in programs, goals and documents. Booleans and
`None` are not terms.

**Unification** is syntactic unification on finite trees. It MUST apply the
occurs check: binding a variable to a term that contains it fails. Atoms unify
when their texts are equal; numbers when they are of the same kind and equal;
compounds when their names and arities are equal and their arguments unify
pairwise.

**Standard order.** Terms are totally ordered as: variables, then numbers,
then atoms, then compounds. Numbers are ordered by value, compared exactly
across integers and floats; a float precedes an integer of equal value.
Atoms are ordered by the code points of their characters. Compounds are
ordered by arity, then name, then arguments from left to right. Distinct
variables are ordered by the code points of their names, so the order is the
same in every comparison. The names of renamed-apart variables (Section 7.1)
are implementation-specific, so a program SHOULD NOT depend on the relative
order of two distinct unbound variables.

## 4. Programs

### 4.1 Program modules

A program is a Python module whose top level contains `from peye import *`.
Running the module states the program's clauses in the order the calls are
made; `fact` MAY state several clauses in one call (Section 4.2).
Several modules MAY be loaded as one program; their
clauses are then numbered in the order the modules are run.

`from peye import *` provides exactly the names needed to state a program:
the statements of Section 4.2, `preds`, `vars`, `_`, `struct`, the controls
and primitives of Section 5, and the atoms `true`, `fail` and `false`.

### 4.2 Statements

| Statement | Clause stated |
| --- | --- |
| `fact(T1, T2, ...)` | One fact per argument. |
| `implies(Premise, Conclusion)` | A forward rule, N3's `=>`: the premise's goals are its body and the conclusion its head, which MAY join several conclusions with `&`. |
| `implied_by(Conclusion, Premise)` | A backward rule, N3's `<=`: the conclusion is its head and the premise's goals are its body. |
| `query(G1, G2, ...)` | A forward rule with the head `'true'` and the body `G1, G2, ...`: it reports its body's instances (Section 7.2). At least one goal is REQUIRED. |
| `contradiction(G1, G2, ...)` | A forward rule with the head `'false'` and the body `G1, G2, ...`: it halts the run (Section 7.2). At least one goal is REQUIRED. |
| `facts_from(path)` or `facts_from(text=...)` | One fact per expression of a document (Section 9). |

A body goal that is a conjunction (`&`, Section 5.1) is split into its
conjuncts; the clause body is the resulting sequence of goals.

Clauses are numbered from 1 in the order they are stated. Each clause records
the line of the program on which the statement stating it begins; the facts
of `facts_from` record the line of that call.

`facts_from` is how a program takes in data that is not a program: a document
of plain expressions, one per line, such as the conclusions, proof or check
report of another run, or data from a source that is not trusted. The
document is read as Section 9 describes and is never executed, so it can only
ever state facts. A data file written as a program instead (`fact(...)`
statements) would run as Python code.

A clause MUST be rejected when:

- a head is not an atom or a compound;
- a head is `step/4` or `clause/2`, which are reserved for proof documents;
- a head is a primitive (Section 5.2) or a control (Section 5.1), except the
  head `'true'` of a query and `'false'` of a contradiction; in particular a
  conclusion of `implies` is never `'true'` or `'false'`;
- a body goal is not a variable, an atom or a compound, or is a non-empty list.

### 4.3 Names a program does not define

Before a program module runs, its source is analysed. A referenced name with
no module-level binding (by assignment, import or definition) is supplied as
follows. References in nested scopes are considered only when Python resolves
them as global names; local variables and parameters keep their Python scope.

1. a name beginning with an uppercase letter or `_` is the variable of that
   name;
2. any other name is the predicate of that name: calling it with arguments
   builds the compound with that name, and using it uncalled stands for the
   atom of that name.

Names `from peye import *` provides and names beginning with `__` keep their
meaning. So does the name of a Python builtin, such as `getattr` or `int`,
unless the program uses it somewhere inside the arguments of a call of a name
`from peye import *` provides, as `type` in `fact(type('socrates', 'human'))`:
then it is a predicate. Even there, the builtins `print`, `range`, `len`,
`list`, `dict`, `set`, `tuple`, `str`, `enumerate`, `zip`, `sorted`,
`reversed`, `isinstance`, `open`, `repr`, `chr`, `ord`, `iter`, `any`, `all`,
`map` and `filter`, and builtins beginning with an uppercase letter, keep their
meaning.

A program MAY name predicates and variables explicitly:
`p, q = preds('p q')` and `X, Y = vars('X Y')`. A program that wants a
predicate named like a kept builtin MUST do so.

A top-level expression statement that calls a predicate supplied by rule 2,
such as a misspelled `fcat(p(1))`, states nothing; a loader MUST report it as
an error rather than ignore it.

### 4.4 Terms in a program

Within a program, a Python `str` is an atom, an `int` or `float` a number, a
Python list a list, and `[H, *T]` the list with head `H` and tail `T`.
`struct('name', A1, ...)` builds a compound with any name, and
`struct('name')` the atom. Every occurrence of `_` in a clause is a distinct
variable, an **anonymous variable**: the occurrences are named `_0`, `_1`,
... in the order of the clause's text, skipping names the clause already
uses, and clause displays and bindings (Section 10) show these names. A
program SHOULD NOT name its own variables `_` followed by digits, which
Section 5.1 treats as anonymous.

Python operators on variables and compounds build compound terms
(Section 8.2), for example `X + 1` builds `'+'(X, 1)` and `X < Y` builds
`'<'(X, Y)`. A term MUST NOT be used as a Python truth value; an
implementation MUST raise an error when it is, which catches a chained
comparison such as `X > 1 & Y < 2`. An operator applied only to plain Python
values is Python's own: `1 < 2` is the Python `True`, which is not a term,
and stating it is an error.

### 4.5 Stratification

A body goal depends on a clause when the goal, renamed apart, unifies with
one of the clause's heads. The dependency is **closed** when the goal occurs
inside a negation or as the goal of a collection (Section 5.1), and **open**
otherwise. Each clause has a rank: the least assignment such that a clause's
rank is at least the rank of every clause it depends on, plus one for a closed
dependency. Forward rules run in order of rank (Section 7.2).

A program MUST be rejected when:

- no such assignment exists ("unstratified negation or collection
  dependency"), that is, a closed dependency lies on a cycle;
- a forward rule can reach, through dependencies, a clause with a body goal
  that is a variable ("forward dependencies require statically named calls").

Because dependencies compare whole terms, two relations sharing a predicate
name MAY have different ranks.

## 5. Goals, Controls and Primitives

### 5.1 Controls

| Control | Term | Meaning |
| --- | --- | --- |
| `A & B` | `','(A, B)` | Conjunction: solve `A`, then `B`. |
| `A \| B` | `';'(A, B)` | Disjunction: the solutions of `A`, then those of `B`. |
| `~G` | `'~'(G)` | Negation: succeeds once, binding nothing, when `G` has no solution. When the negation is solved, every variable of `G` MUST be bound except anonymous ones, which stand for any value: `~q(X, _)` succeeds when `q(X, Y)` has no solution for any `Y`. A named unbound variable is an error. |
| `call(G)` | `call(G)` | The solutions of `G`. |
| `once(G)` | `once(G)` | The first solution of `G`. |
| `findall(T, G, L)` | `findall(T, G, L)` | Unifies `L` with the list of instances of `T`, one per solution of `G`, in order, each renamed apart. |

A variable is anonymous when its name, up to any `#` a renaming apart
(Section 7.1) adds, is `_` followed by digits (Section 4.4), or is one a
reader made for a `_` (Section 9).

In a program (Section 4), `not_(G1, G2, ...)` builds `~(G1 & G2 & ...)`, and
`call` and `once` with several goals build `call(G1 & G2 & ...)` and
`once(G1 & G2 & ...)`. In goal text and documents (Section 9) these are
ordinary compounds: there `not_(...)` is not a negation.

### 5.2 Primitives

In a flow pattern, `+` marks an argument that MUST be bound when the goal
runs, `-` one that MUST be unbound, `?` either, and `@` one only inspected. A
primitive called outside its patterns raises an error.

| Primitive | Pattern | Meaning |
| --- | --- | --- |
| `'true'`, `'fail'`, `'false'` | | Succeeds; fails; fails. |
| `unify(?X, ?Y)` | | Unifies `X` and `Y`. |
| `not_unify(@X, @Y)` | | Succeeds, binding nothing, when `X` and `Y` do not unify. |
| `identical(@X, @Y)` | | `X` and `Y` are identical. |
| `not_identical(@X, @Y)` | | `X` and `Y` are not identical. |
| `compare(?O, @X, @Y)` | | Unifies `O` with `'<'`, `'='` or `'>'`, by the standard order. |
| `is_(?V, +E)` | | Evaluates `E` (Section 6) and unifies `V` with the result. |
| `eq(+E1, +E2)`, `ne(+E1, +E2)` | | The values of `E1` and `E2` are equal, or not. |
| `E1 < E2`, `E1 <= E2`, `E1 > E2`, `E1 >= E2` | | Compares the values of `E1` and `E2`. |
| `is_var(@X)`, `is_nonvar(@X)` | | `X` is an unbound variable, or is not. |
| `is_ground(@X)` | | `X` contains no unbound variable. |
| `is_atom(@X)`, `is_number(@X)` | | `X` is an atom, or a number. |
| `is_int(@X)`, `is_float(@X)` | | `X` is an integer, or a float. |
| `is_compound(@X)` | | `X` is a compound; a non-empty list is one. |
| `functor` | `functor(+T, ?N, ?A)`, `functor(-T, +N, +A)` | Name and arity of `T`, or `T` built with fresh variable arguments. `A` MUST be between 0 and 1024. |
| `arg` | `arg(+N, +T, ?A)` | `A` is the `N`th argument of `T`, counting from 1. |
| `univ` | `univ(+T, ?L)`, `univ(-T, +L)` | `L` is the list of `T`'s name and arguments. |
| `atom_chars` | `atom_chars(+A, ?L)`, `atom_chars(-A, +L)` | `L` is the list of `A`'s characters as atoms. |
| `atom_codes` | `atom_codes(+A, ?L)`, `atom_codes(-A, +L)` | `L` is the list of `A`'s character code points. |
| `atom_length` | `atom_length(+A, ?N)` | `N` is the number of characters of `A`. |
| `atom_concat` | `atom_concat(+A, +B, ?AB)`, `atom_concat(?A, ?B, +AB)` | `AB` is `A` followed by `B`; with `AB` given, every split, shortest `A` first. |

Every primitive except `atom_concat` has at most one solution. Primitives
MUST be pure: their solutions depend only on their arguments. A primitive
given an argument of the wrong kind for its patterns raises an error, as
`atom_length(123, N)` does; one given arguments of the right kinds that has
no solution fails, as `arg(5, f(1), A)` does.

A goal whose name and arity are neither a control, a primitive nor the head
of any clause has no solution.

## 6. Arithmetic

An expression term is evaluated with the meaning the same expression has in
Python:

- a number is its value; the atoms `'pi'`, `'e'` and `'tau'` are the
  constants of Python's `math` module; a variable bound to an expression is
  that expression's value; an unbound variable or any other atom is an error;
- `'+'`, `'-'`, `'*'`, `'/'`, `'//'`, `'%'`, `'**'`, `'<<'`, `'>>'` and `'^'`
  with two arguments are Python's `+`, `-`, `*`, true division `/`, floor
  division `//`, modulo `%`, power `**`, shifts and exclusive or;
- `','` and `';'` with two arguments are bitwise and and or, and `'~'`, `'-'`
  and `'+'` with one argument are bitwise inversion, negation and identity:
  in an expression, `&`, `|` and `~` keep their Python meaning;
- the compounds `abs`, `min`, `max`, `round`, `int` and `float` are Python's
  builtins of those names, and `floor`, `ceil`, `trunc`, `sqrt`, `isqrt`,
  `exp`, `log`, `log2`, `log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`,
  `atan2`, `sinh`, `cosh`, `tanh`, `hypot`, `degrees`, `radians`, `fmod`,
  `copysign`, `gcd` and `lcm` the functions of `math`; `pow` is `**`.

Integers are exact and unbounded. An evaluation MUST raise an error, rather
than produce a value, when the operation raises one in Python (such as a
division by zero or `sqrt(-1)`), when the result is not a finite real number,
or when a power or left shift would need more than 2^26 bits: for a power
of integers `A ** B` with `B > 0` and `abs(A) > 1`, when `B` times the bit
length of `A` exceeds 2^26; for a shift `A << B` of integers, when `B` exceeds
2^26.

Comparisons are primitives (Section 5.2), not arithmetic functions: `'<'` and
the other comparisons in an expression are an error. Comparison primitives
compare values exactly, including across integers and floats.

## 7. Reasoning

### 7.1 Search

Goals are solved depth-first, left to right. A goal is solved, in order:

1. by a control or primitive (Section 5), when it is one;
2. otherwise against the facts derived so far by forward rules with the same
   name and arity, in the order they were derived;
3. then against the program's facts and backward rules with the same name and
   arity, in clause order, each renamed apart before it is unified with the
   goal; a rule's body is then solved in its place.

Renaming a clause apart gives each of its variables a fresh variable whose
name is the variable's name followed by `#` and an implementation-specific
suffix. Such names never appear in the documents a run writes (Section 8.3).

An implementation MAY index clauses, provided the order above is kept.

### 7.2 Forward reasoning

Forward rules run stratum by stratum, in increasing rank (Section 4.5). Within
a stratum, rounds are repeated until a round adds no new fact. In a round,
each rule in clause order is renamed apart and its body solved against the
current state; all solutions of the body are collected first, then each is
concluded:

- a head variable the solution leaves unbound is bound to a **Skolem term**
  `skolem(Rule, Variable, Arguments)`: `Rule` is the clause number of the
  rule, `Variable` the variable's name as the program writes it (an
  anonymous one as `_0`, `_1`, ..., Section 4.4), and `Arguments` the list of
  the ground values the solution gives the heads' other variables, in order
  of their first occurrence in the heads. A Skolem term is thus a function of
  the activation: the rule and the instance of its heads. The same activation
  gives the same terms, in any round and in any run, and different
  activations give different terms; variables shared between heads stay
  shared. A variable that a value of the solution brought in, rather than a
  head variable, is named after its own variable, followed by `1`, `2`, ...
  when that name is taken. A rule that keeps meeting new activations does
  not terminate (Section 7.3). Derived facts are therefore ground;
- a head `'true'` reports the instance of the rule's body, as a conjunction,
  once per distinct instance (by identity of canonical text);
- a head `'false'` records the conclusion `'false'` and stops all reasoning
  with halt code 65;
- any other head is added as a derived fact unless an identical fact is
  already derived or is a ground fact of the program.

When the run asks its own goals (Section 7.4), rules whose heads are all
`'true'` are not run.

### 7.3 Bounds

A run is bounded by `max_depth`, the depth of nested rule bodies (default
1000000), by `max_inferences`, the number of goals started (default
1000000), and by `max_iterations`, the rounds per stratum (default 1000).
Exceeding a bound MUST raise an error; a partial result MUST NOT be returned
as complete.

### 7.4 Goals

A run MAY be given goals. After forward reasoning, each goal is solved in
turn, and each solution is reported as the instance of its goal, unless an
instance identical up to renaming of its variables was already reported for
this goal or an earlier one of the same run.

### 7.5 Halting

A run that concluded `'false'` has halt code 65; otherwise it has none.

### 7.6 Conclusions

The conclusions of a run are, in order:

1. when it halted: every derived fact, in the order derived, ending with
   `'false'`;
2. otherwise, when it was given goals: the reported instances of its goals;
3. otherwise, when the program has a forward rule with a head `'true'`: the
   reported instances, in order of first report, which MAY be none;
4. otherwise: every derived fact, in the order derived.

The output of a run is the canonical text (Section 8) of each conclusion,
one per line.

### 7.7 Proof recording

When a proof is requested, each solution records how each of its goals was
justified: by a fact or rule of the program, by a derived fact (whose own
record is kept), by a primitive, by a control, by an absence (a negation) or
by a collection (`findall`). For each conclusion the first derivation found
is recorded. A reasoner MUST check every proof it generates (Section 11)
before returning it, and MUST fail with an error rather than return a proof
that does not pass. A run without conclusions has a proof without claims,
which is valid and certifies nothing.

A goal such as `is_var(X)` followed by `unify(X, 'a')`
cannot be recorded faithfully by its final substitution, so such a run
cannot produce a proof.

## 8. Canonical Text

Every term has exactly one canonical text, which is a Python expression.

### 8.1 Atoms, numbers, variables and lists

- An atom is written as Python's `repr` of the string, except that `'[]'` is
  written `[]`.
- An integer is written in decimal; a float as Python's `repr` (for example
  `0.1`, `1e+22`, `2.0`).
- A variable is written as its name when the name is a Python identifier,
  not a keyword, not `_` and does not begin with `VAR_`. Any other name is
  written `VAR_` followed by the name with every ASCII letter and digit kept,
  every `_` doubled and every other character `c` replaced by `_hex_` where
  `hex` is the lowercase hexadecimal code point of `c`. The variable `X#12`
  is thus written `VAR_X_23_12`. A reader decodes such a name back
  (Section 9).
- A list is written `[I1, I2, ...]`; an open list ends with `, *Tail`.

### 8.2 Compounds

A compound whose name and arity appear below is written with the operator,
with Python's precedence; operands are parenthesized exactly where Python
needs it:

| Term | Text | Precedence |
| --- | --- | --- |
| `'<'(A, B)`, `'<='(A, B)`, `'>'(A, B)`, `'>='(A, B)` | `A < B`, ... | 6, not associative |
| `';'(A, B)` | `A \| B` | 7, left |
| `'^'(A, B)` | `A ^ B` | 8, left |
| `','(A, B)` | `A & B` | 9, left |
| `'<<'(A, B)`, `'>>'(A, B)` | `A << B`, `A >> B` | 10, left |
| `'+'(A, B)`, `'-'(A, B)` | `A + B`, `A - B` | 11, left |
| `'*'(A, B)`, `'/'(A, B)`, `'//'(A, B)`, `'%'(A, B)` | `A * B`, ... | 12, left |
| `'-'(A)`, `'+'(A)`, `'~'(A)` | `-A`, `+A`, `~A` | 13 |
| `'**'(A, B)` | `A ** B` | 14, right |

A negative number has precedence 13. `'-'(N)` with a number `N` is not
written `-N`, which would read back as a number; it is written `struct('-', N)`.

Any other compound is written `name(A1, A2, ...)` when its name is a Python
identifier, not a keyword and not `struct`, and `struct('name', A1, ...)`
otherwise. Arguments are separated by `, `.

A conjunction built left to right, `','(','(A, B), C)`, is written `A & B & C`.

### 8.3 Variables in written documents

The conclusions a run writes, its proof documents (Section 10) and check
reports (Section 12) do not show the names variables have inside a run. In
the conclusions of a run and in a proof document, the variables are named
`A`, `B`, ..., `Z`, `A1`, ..., `Z1`, `A2`, ... in the order the document
first shows them, across the whole document, the conclusions written first;
the clause displays of a proof keep the program's names. A check report
names the variables of each fact anew (Section 12). The bindings an
implementation reports for each answer to a goal SHOULD name its variables as
the answer does.

## 9. Reading Documents

A document is UTF-8 text holding a sequence of Python expression
statements. As in Python, a statement MAY span lines inside brackets,
statements on one line MAY be separated by `;`, and comments and blank lines
are ignored; each term records the line on which its statement begins. The
documents peye writes hold one statement per line. A reader MUST build terms
from the syntax tree of the text and MUST NOT execute it. It accepts
exactly:

- a string literal, or adjacent string literals: the atom; an integer or
  finite float literal: the number;
- a name: the variable of that name, where each `_` is a new anonymous
  variable (Section 5.1) and a name starting with `VAR_` is decoded
  (Section 8.1), or rejected when it encodes no name;
- a call of a plain name with positional arguments only: the compound, or
  the atom when there are no arguments; `struct('name', ...)` as in
  Section 8.2;
- a list display: the list, where only the last item MAY be starred and then
  is the tail;
- a dictionary display `{K: V, ...}`: the list of compounds `'='(K, V)`, in
  order;
- a unary minus applied directly to a numeric literal: the negative number;
- the operators of Section 8.2, with Python's precedence; a comparison MUST
  NOT be chained.

Anything else, such as an attribute, a subscript, a keyword argument, a
tuple, a set, `True`, `False`, `None`, a bytes or formatted string, an
imaginary number, `==`, `in`,
`is`, `not`, `and`, `or`, `@` or a non-expression statement, MUST be
rejected. Reading the canonical text of a term MUST give the term back.

A reader MAY read simple lines by other means than a syntax tree, provided it
gives exactly the terms Python's syntax tree would.

## 10. Proof Documents

### 10.1 Structure

A proof document is a document (Section 9) holding, in this order:

1. the conclusions of the run (Section 7.6), one per line;
2. an empty line;
3. one `clause(N, Display)` per program clause the proof cites, by
   increasing `N`;
4. an empty line;
5. one `step(Goal, By, Bindings, Uses)` per justified goal.

A checker MUST treat every statement that is neither `clause/2` nor `step/4`
as a claim, whatever its position.

### 10.2 Clause displays

`Display` shows clause `N` as the program states it: `fact(Head)`,
`implies(Body, Head)`, `implied_by(Head, Body)`, `query(G1, ...)` or
`contradiction(G1, ...)`, where `Body` is the clause's body goals joined left
to right with `&` and `G1, ...` are those goals themselves. Displays are not
authority: a checker MUST compare each with the program it checks against.

### 10.3 Steps

`Goal` is the justified goal as it stands once the whole solution is found:
the goal with every variable the solution bound replaced by its value. The
program's goal `unify(Y, 6)`, solved with `Y` unbound, thus has the step
`step(unify(6, 6), 'builtin', {}, [])`; the value `Y` received is recorded in
the bindings of the step that cites the clause, as `{'Y': 6}`. Steps appear
in the order a depth-first walk
from the claims first meets each goal, and each distinct goal (by canonical
text) has one step. `Uses` is the list of the goals that justify `Goal`, in
order. `By` is one of:

| `By` | Meaning | `Bindings` | `Uses` |
| --- | --- | --- | --- |
| `clause(N)` | `Goal` is an instance of a head of clause `N`, a fact or a rule, whose body instance is `Uses`. | the clause's variables | the body instance, empty for a fact |
| `'builtin'` | `Goal` is a primitive that holds. | empty | empty |
| `'control'` | `Goal` is `call`, `once` or a disjunction, solved by `Uses`. | empty | the solved goals |
| `'absent'` | `Goal` is a negation taken on trust. | empty | empty |
| `'collected'` | `Goal` is a `findall` taken on trust. | empty | empty |

`Bindings` is a dictionary from each variable name of the cited clause, as
the program wrote it, to its value in this step: `{'X': 'socrates'}`. A
reasoner writes every variable of the clause, in the order the clause display
first shows them (for `implies`, the premise first);
a checker MUST accept any subset, since the goal and uses determine the
rest. A primitive has no variables of its own, so `'builtin'` steps have
empty bindings.

## 11. Proof Checking

A checker is given a program, a proof document and, when the proof answers
goals asked from outside the program, those goals. It MUST NOT call a
reasoner to supply a missing step; it MAY recompute primitives. It
establishes seven conditions and records each failure with its condition, a
detail and, where there is one, the term concerned.

### 11.1 Reading the document

The document MUST read (Section 9); otherwise C3 fails and the document has
no claims and no steps. Each `clause(N, Display)` MUST name a clause of the
program whose display (Section 10.2) is identical to `Display`; otherwise C1
fails. Each `step` MUST have bindings that read as a list of `'='/2` pairs,
as a dictionary display does, and a list of uses, and no two steps may have
identical goals; otherwise C3 fails and the step is set aside. Every other
statement is a claim (Section 10.1).

### 11.2 C1 Resolution

For a `clause(N)` step, `N` MUST be a clause of the program. The clause,
renamed apart, MUST satisfy: each binding names a distinct variable of the
clause and unifies it with its value; and for one of the clause's heads
(each conjunct of a forward rule's head), the head unifies with `Goal` and
the body, of the same length as `Uses`, unifies with `Uses` pairwise, such
that afterwards the head is identical to `Goal` and each body goal to its
use. A step's own terms MUST NOT need further instantiation to match: a
source clause `same(X, X)` cannot justify `same('a', 'b')`.

### 11.3 C2 Well-foundedness

No step MAY depend on itself through the uses of steps.

### 11.4 C3 Justification

`By` MUST be one of the forms of Section 10.3. A `'builtin'` step MUST have
no bindings and no uses and a goal that is a primitive; an `'absent'` or
`'collected'` step MUST have no bindings and no uses and a goal that is a
negation or a `findall`, respectively.

### 11.5 C4 Coverage

Each conjunct of each claim MUST have a step. Each use, and each conjunct of
a use, MUST have a step or be identical to an instance of a fact of the
program. A document without claims is valid and certifies nothing.

### 11.6 C5 Re-decision

A `'builtin'` step's goal, solved as a primitive with no prior bindings, MUST
succeed without binding anything. A `'control'` step MUST have no bindings,
and its uses MUST be identical, in order, to the conjuncts of the argument of
`call` or `once`, or of one side of a disjunction. When trusted boundaries are
forbidden ("strict"), each `'absent'` or `'collected'` step fails C5.

### 11.7 C6 Boundary consistency

A trusted boundary cannot be proved, but the evidence at hand can refute it.
The evidence for a goal is: when the goal is a ground primitive, the goal
itself if it holds; when it is a control, none, and the boundary is left
undecided; otherwise the program's facts and the goals of the document's
steps with the same name and arity.

- An absence `~G` is decided when `G` is a single goal, or a ground
  conjunction, whose every goal has evidence. It fails C6 when every goal of
  `G` unifies with some of its evidence; the anonymous variables of `G`
  unify with anything.
- A collection `findall(T, G, L)` fails C6 when `L` is not a list, and is
  decided when `G` is a single goal with evidence. It fails C6 when an
  instance of `T` for some evidence of `G` unifies with no element of `L`.

A boundary that is not refuted remains an obligation (Section 12).

### 11.8 C7 Relevance

When goals were given and no claim is `'false'`, the questions are the goals.
Otherwise the questions are, for each forward rule, each head other than
`'true'`, and the rule's body as a conjunction when one of its heads is
`'true'` and no claim is `'false'`. Each claim MUST be an instance of a
question. Each step MUST be reachable from a conjunct of a claim through the
conjuncts of uses.

### 11.9 Counts and validity

| Condition | Covered |
| --- | --- |
| C1 resolution | `clause` steps that passed C1 |
| C2 well_founded | steps |
| C3 justification | steps |
| C4 coverage | claims plus uses |
| C5 re_decision | `'builtin'` and `'control'` steps that passed C5 |
| C6 boundary_consistency | boundaries decided |
| C7 relevance | claims plus steps |

A check also counts the **steps** it read, the **claims**, the `clause` steps
**verified** by C1, the `'builtin'` steps **recomputed** by C5, the
`'control'` steps **composed** by C5, and the `'absent'` and `'collected'`
steps **trusted**.

A proof is **valid** when no condition failed. A valid proof with trusted
boundaries is valid *conditional on* them.

### 11.10 What a valid proof establishes

A valid proof establishes that each of its claims follows from the program
by the recorded steps, given its trusted boundaries. It does not establish
that the claims are all the conclusions of the program, that the program
derives no `'false'`, or that the program is the one intended: a proof MAY
leave conclusions out, and a run's own proof holds exactly its conclusions.

## 12. Check Reports

A check report is a document (Section 9) holding, in this order, one fact per
line:

1. `condition(Id, Name, Outcome, Covered)` for C1 to C7, where `Outcome` is
   `'ok'` or `failed(N)`, `N` the number of that condition's failures;
2. `failure(Condition, Subject, Detail)` per failure, where `Subject` is the
   term concerned or `'proof_document'`, and `Detail` an atom;
3. `obligation(Kind, 'theory_scoped', Goal)` per trusted boundary, in step
   order, where `Kind` is `'absent'` or `'collected'`;
4. `steps(N)`, `verified(N)`, `recomputed(N)`, `composed(N)`, `trusted(N)`,
   `claims(N)`, the counts of Section 11.9;
5. `verdict(V)`, where `V` is `failed(N)` when `N` failures were recorded,
   otherwise `'checked_with_obligations'` when there are obligations,
   otherwise `'checked'`.

Failures are listed in the order they are found: those of reading the
document (Section 11.1), in document order; C4 for each claim, in claim
order; then for each step, in document order, C4 for its uses and the C1, C3
or C5 failure of its justification; C6 for each boundary, in step order; C7
for each claim, then for each step; and C2.

`Detail` is a short human-readable text that names what failed, often with
the canonical text of a term; it is informative, and implementations MAY word
it differently. peye's details are, by condition:

| Condition | Details |
| --- | --- |
| C1 | `clause display differs from source`, `unknown clause ...`, `not an instance of source clause N: ...` |
| C2 | `cyclic derivation at ...` |
| C3 | the reader's error, `step bindings must be a dictionary and uses a list`, `duplicate justification for ...`, `invalid builtin justification`, `trusted boundaries cannot have bindings or uses`, `unknown justification ...` |
| C4 | `unjustified claim ...`, `unjustified use ...` |
| C5 | `primitive disagrees: ...`, `control step does not follow from its uses: ...`, `trusted boundary forbidden: absent` or `collected` |
| C6 | `absence contradicted by evidence: ...`, `collected result is not a proper list: ...`, `collection misses ...: ...` |
| C7 | `claim answers no goal: ...`, `step serves no claim: ...` |

The variables of each fact are renamed `A`, `B`, ..., `Z`, `A1`, ... in order
of first occurrence. A report is ordinary data: `facts_from` (Section 4.2)
states it as facts.

The JSON form of a report is an object with `valid` (boolean), `steps`,
`claims`, `verified`, `redecided` (the count `recomputed`), `composed`,
`uses` (the number of uses of all steps, integers), `trusted`
(a list of `{kind, conclusion}`), `failures` (a list of
`{condition, detail, conclusion?}`) and `conditions` (a list of
`{id, name, covered, failed}`), where `conclusion` is a canonical text.

## 13. Unused Clauses

A clause is **unused** when no conclusion's recorded derivation cites it,
unless a negation or collection in the proof could consult it and running the
program without it changes the conclusions or the halt code, or fails. The clauses a
negation or collection could consult are those whose heads have the name and
arity of a goal it reaches through the program's bodies.

Unused clauses are reported one per line, in clause order, as
`unused(line(L), Display)`, where `L` is the clause's line (Section 4.2) and
`Display` as in Section 10.2.

"Unused" is relative to the recorded derivations, which are the first ones
found (Section 7.7). A clause that only offers a second derivation of a
conclusion, such as a duplicate rule, is unused, though leaving out the
clause that offers the first one would make it used; leaving out several
unused clauses together can therefore change the conclusions. A
`contradiction` rule that never fires changes no conclusion and is unused,
though it guards the program against data that would make it fire.

## 14. Command Line

```text
peye [OPTION ...] [FILE ...]
```

| Option | Meaning |
| --- | --- |
| (none) | Load the files, or standard input, as one program and print its conclusions. |
| `--proof` | Print the proof document instead. |
| `--check-proof FILE` | Check the proof in `FILE` (`-` for standard input) against the program and print its report. |
| `--json` | With `--check-proof`, print the report as JSON. |
| `--goal GOAL` | Ask `GOAL`, read as in Section 9; MAY be repeated. With `--check-proof`, the goals the proof answers. |
| `--strict-proof` | With `--check-proof`, forbid trusted boundaries. |
| `--unused` | Print the unused clauses (Section 13). |
| `--stats` | Print reasoning statistics as JSON to standard error. |
| `--max-depth N`, `--max-iterations N`, `--max-inferences N` | The bounds of Section 7.3; `N` MUST be a positive integer. |
| `--version`, `--help` | Print the version, or the usage. |

`--check-proof` MUST NOT be combined with `--proof`, nor `--unused` with
either, and `--json` and `--strict-proof` need `--check-proof`. A program
text that has a line starting with `step(` and none starting with
`from peye import *` is a proof document; given one as a program, the command
line MUST say how to check it instead.

| Exit code | Meaning |
| --- | --- |
| 0 | Success, including a check that found the proof valid. |
| 1 | An error, printed to standard error as `peye: message`. |
| 2 | A check that found the proof not valid; the report is printed as usual. |
| 65 | The run halted (Section 7.5). |

A program module whose top level contains `from peye import *` MAY be run as
a Python script: it is then loaded and reasoned over with the command line's
options, as if named as a `FILE`.

## 15. Security Considerations

A **program** is Python code and runs with the privileges of whoever runs it;
only programs from trusted sources should be run. Reasoning itself calls no
code of the program: once stated, clauses are terms.

A **document** (conclusions, proofs, reports, `facts_from` input and goals)
is untrusted data. It MUST NOT be executed. The reader of Section 9 accepts
literals, names, calls of a plain name, list and dictionary displays and a
fixed set of operators, so no document can run code, import modules or
reach attributes. Checking a proof from a third party is therefore safe in
the sense that it runs none of the third party's code.

Reasoning and checking consume time and memory. The bounds of Section 7.3,
the limit on powers and shifts in Section 6 and the limit on `functor`
arities in Section 5.2 bound some of this; a deployment that checks untrusted
proofs SHOULD additionally bound document size, nesting depth and running
time.

A valid proof establishes that its claims follow from the program supplied
to the checker (Section 11.10). It does not establish that the program is
correct or that the claims are all its conclusions, and a proof with
obligations holds only conditional on them.

## 16. Conformance

A conforming **reasoner** implements Sections 3 to 10, produces
conclusions and proof documents in the canonical text, and checks every proof
it produces as Section 11 describes. A conforming **checker** implements
Sections 9, 11 and 12 and does not depend on a reasoner. For the same
program, a conforming reasoner and checker MUST produce the same
conclusions, proof documents and reports as peye 0.4.2, byte for byte,
except for the `Detail` texts of failures (Section 12), the internal names of
variables where Section 3 says so, and where Python's floating-point library
functions differ in the last digit.

The conformance suite in the repository's `conformance/` directory tests an
implementation against this document through its command line, case by case,
each case naming the sections it tests; `conformance/README.md` describes how
to run it against any implementation. The repository's examples, with their
saved conclusions (`examples/output/`), proofs (`examples/proof/`) and reports
(`examples/check/`), test the same on larger programs.

---

## Appendix A. Document Grammar

The documents of Sections 9 to 12 use this subset of Python's grammar, in the
ABNF style of RFC 5234, with whitespace between tokens allowed as in Python;
as in Python, an expression MAY continue onto following lines inside
brackets.

```abnf
document    = *( line LF ) [ line ]
line        = [ expression *( ";" expression ) [ ";" ] ] [ comment ]
comment     = "#" *<any character except LF>
expression  = bitor [ compare-op bitor ]
compare-op  = "<" / "<=" / ">" / ">="
bitor       = bitxor *( "|" bitxor )
bitxor      = bitand *( "^" bitand )
bitand      = shift *( "&" shift )
shift       = sum *( ( "<<" / ">>" ) sum )
sum         = product *( ( "+" / "-" ) product )
product     = unary *( ( "*" / "/" / "//" / "%" ) unary )
unary       = ( "-" / "+" / "~" ) unary / power
power       = primary [ "**" unary ]
primary     = string / number / name / call / list / dict / "(" expression ")"
call        = name "(" [ expression *( "," expression ) [ "," ] ] ")"
list        = "[" [ items ] "]"
items       = expression *( "," expression ) [ "," "*" bitor ] [ "," ]
            / "*" bitor [ "," ]
dict        = "{" [ pair *( "," pair ) [ "," ] ] "}"
pair        = expression ":" expression
string      = 1*<a Python string literal, not bytes and not formatted>
number      = <a Python integer or floating-point literal, not imaginary>
name        = <a Python identifier that is not a keyword>
```

## Appendix B. Example

The program `socrates.py`:

```python
from peye import *

fact(type('socrates', 'human'))
fact(subclass_of('human', 'mortal'))
implies(type(S, A) & subclass_of(A, B), type(S, B))
query(type(X, Y))
```

Its conclusions:

```python
type('socrates', 'mortal')
type('socrates', 'human')
```

Its proof document (Section 10):

```python
type('socrates', 'mortal')
type('socrates', 'human')

clause(1, fact(type('socrates', 'human')))
clause(2, fact(subclass_of('human', 'mortal')))
clause(3, implies(type(S, A) & subclass_of(A, B), type(S, B)))

step(type('socrates', 'mortal'), clause(3), {'S': 'socrates', 'A': 'human', 'B': 'mortal'}, [type('socrates', 'human'), subclass_of('human', 'mortal')])
step(type('socrates', 'human'), clause(1), {}, [])
step(subclass_of('human', 'mortal'), clause(2), {}, [])
```

Its check report (Section 12):

```python
condition('C1', 'resolution', 'ok', 3)
condition('C2', 'well_founded', 'ok', 3)
condition('C3', 'justification', 'ok', 3)
condition('C4', 'coverage', 'ok', 4)
condition('C5', 're_decision', 'ok', 0)
condition('C6', 'boundary_consistency', 'ok', 0)
condition('C7', 'relevance', 'ok', 5)
steps(3)
verified(3)
recomputed(0)
composed(0)
trusted(0)
claims(2)
verdict('checked')
```

## Appendix C. Implementation Notes

This appendix is informative: it describes how this version of peye
implements this document, not requirements on other implementations. The
runtime has no dependencies beyond the Python standard library and there is no
build step.

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

**Forward rounds are semi-naive.** After a forward rule's first search, a
rule whose body goals are all answered by facts alone (or are primitives,
negations or collections) is searched only for activations that use a fact
derived since its previous search: once for each body goal that has such
facts, that goal limited to them and the goals before it to the older ones.
The activations found are then sorted into the order a full search would
find them, by the fact or clause each body goal took, so the conclusions,
their order and their proofs are those of Section 7.2. A transitive closure
over a chain of 150 edges needs 11,476 inferences this way instead of
1,136,575.

**Proof steps record the first derivation found** for each conclusion, and are
recorded only when a proof is asked for: without one, the search keeps just what
it needs to find answers. Nodes carry the terms they were built from and are
resolved once, by whoever consumes a complete answer, so a conjunction does not
re-copy the proof forest for each of its goals. Renaming a clause apart shares
every subterm that holds no variable, since terms never change once built.
