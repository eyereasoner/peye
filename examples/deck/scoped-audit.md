# Scoped audit

*Checking each record on its own, so one file cannot fill gaps in another.*

[scoped-audit.py](https://github.com/eyereasoner/peye/blob/main/examples/scoped-audit.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/scoped-audit.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/scoped-audit.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/scoped-audit.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=scoped-audit)

---

## The question

An auditor has two separate records. The *approved* record says Alice is an
editor and that she gave consent. The *incomplete* record says Bob is an
editor, and nothing else.

**Within each record, which editors gave consent, and which need review?**
A consent written in one record must not count for another.

---

## What we tell peye

Each record is a *graph*: a bundle of simple statements (triples, written
`triple(Subject, Property, Value)`), kept as one piece of data.

```python
fact(
    context('approved', graph([triple('alice', 'role', 'editor'), triple('alice', 'consent', 'yes')])),
)
fact(context('incomplete', graph([triple('bob', 'role', 'editor')])))

implies(
    context(Context, Graph)
    & includes(Graph, triple(Person, 'consent', 'yes')),
    consented(Context, Person),
)
implies(
    context(Context, Graph)
    & includes(Graph, triple(Person, 'role', 'editor'))
    & ~includes(Graph, triple(Person, 'consent', 'yes')),
    needs_review(Context, Person),
)
```

Both rules look *inside one graph*. `~` means "it is not the case that".

---

## What peye concludes

```python
consented('approved', 'alice')
needs_review('incomplete', 'bob')
```

Alice consented in the approved record. Bob is an editor in the incomplete
record with no consent there, so he needs review.

---

## Why: the proof in plain words

For Bob:

1. The incomplete record holds exactly `[triple('bob', 'role', 'editor')]` —
   *fact 2*.
2. That record includes "Bob is an editor" — *found by walking its list*.
3. That record does **not** include "Bob consented" — *searched, nothing
   found*.
4. So Bob needs review in the incomplete record — *rule 7*.

---

## Checked, not just claimed

- **9** steps are confirmed against the program lines they cite.
- **1** step is taken on trust, as an *absent* obligation: that Bob's record
  does not include a consent. peye searched that graph and found none;
  the checker records the claim rather than proving a negative.
- The checker looked for evidence against it and found none.

Verdict: **checked_with_obligations**. 10 steps, 1 on trust.

Note how small the trusted part is: it is scoped to one record, not "nothing
anywhere".

---

## Try it

```sh
python -m peye examples/scoped-audit.py
python -m peye --proof examples/scoped-audit.py
```

Add `triple('bob', 'consent', 'yes')` to Bob's graph, so it reads
`graph([triple('bob', 'role', 'editor'), triple('bob', 'consent', 'yes')])`: the review
disappears and `consented('incomplete', 'bob')` appears instead.

---

## Takeaway

Keeping records separate keeps audits honest. Each conclusion says which
record it came from, and the one "not found" claim is limited to that record.
