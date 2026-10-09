# Terms

*Web data, quoted statements and placeholder names, without any new syntax.*

[terms.py](https://github.com/eyereasoner/peye/blob/main/examples/terms.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/terms.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/terms.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/terms.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=terms)

---

## The question

Data on the web (the **Semantic Web**, RDF) is made of small statements
called **triples**: *subject – predicate – object*, such as "this page – has
title – hello". Names are web addresses (**IRIs**), and text can carry a
language tag ("hello", in English).

Sometimes you also want to talk *about* a group of statements without
claiming they are true — a **quoted graph**, like quoting someone's words.

**Can a small rule language handle all this without special features?**

---

## What we tell peye: the data

Everything is written as ordinary nested terms:

```python
fact(
    quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])),
)
```

Read from the inside out:

- `iri(...)` — a web address used as a name;
- `literal('hello', lang('en'))` — the text "hello", tagged as English;
- `triple(S, P, O)` — one statement;
- `graph([...])` — a list of statements, held as a quotation.

---

## What we tell peye: the rules

```python
fact(member_of(X, [X, *_]))
implied_by(member_of(X, [_, *Xs]), member_of(X, Xs))
implied_by(includes(graph(Triples), Triple), member_of(Triple, Triples))
implies(quoted(G) & includes(G, T), found(T))
implies(quoted(X), witness(X, W))
```

- `member_of` finds an item in a list; `includes` looks inside a graph.
- `found` lists every triple inside the quoted graph.
- `witness` has a `W` that the rule never fills in. More on that below.

---

## What peye concludes

```python
found(triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))))
witness(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), skolem(6, 'W', [graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])]))
```

- The one triple inside the quotation has been found.
- In the `witness`, the unknown `W` became a **Skolem term**,
  `skolem(6, 'W', [the graph])`: a name meaning "the `W` that rule 6 says
  exists for this graph". peye invents such names when a conclusion mentions
  something the rule never pinned down; the same graph always gives the same
  name, and nothing else can.

---

## Why: the proof in plain words

For `found`:

1. The quoted graph is a fact we gave — *fact 1*.
2. The triple is the first item of the graph's list — *the first
   `member_of` line, with the rest of the list empty*.
3. So the graph includes that triple — *the `includes` rule*.
4. So the triple is found — *the `found` rule, with G the graph and T the
   triple*.

For `witness`: the quoted graph exists (fact 1), so the `witness` rule fires
with X the graph and W the Skolem term `skolem(6, 'W', [X])`.

---

## Checked, not just claimed

- **5 steps** for 2 answers, all **5 verified** as exact instances of the
  program lines they cite.
- No calculations to recompute, no circular reasoning, nothing extra.
- **0** steps taken on trust.

Verdict: **checked**.

A quoted graph is just data: its triple is *found*, not *asserted* as true.

---

## Try it

```sh
python -m peye examples/terms.py            # the answers
python -m peye --proof examples/terms.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=terms).
Add a second triple to the list, for example
`triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hallo', lang('nl')))`,
and run again: two `found` lines appear, one for "hello" in English and one
for "hallo" in Dutch.

---

## Takeaway

Web addresses, language-tagged text, statements and quotations all fit into
plain terms, so the same simple, checkable reasoning works on them.
