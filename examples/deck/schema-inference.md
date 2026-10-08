# Schema Inference

*A few general statements about categories and relations, and the facts that follow from them.*

[schema-inference.py](https://github.com/eyereasoner/peye/blob/main/examples/schema-inference.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/schema-inference.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/schema-inference.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/schema-inference.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=schema-inference)

---

## The question

Data on the web often comes with a *schema*: general statements about what
the data means. "Every cat is a mammal." "If someone is a parent of
someone, they are related." "Only people can be parents."

Given a schema and a couple of plain facts — Koko is a cat; Alice is
Bob's parent —

**what else can we safely conclude?** And can each conclusion be traced
back to the statements it came from?

---

## Four kinds of schema statement

- **Subclass** — every member of one category is in another: cat ⊂ mammal.
- **Subproperty** — one relation implies a broader one: `parent_of`
  implies `related_to`.
- **Domain** — whoever is *on the left* of a relation is of some kind:
  whoever is a `parent_of` is a person.
- **Range** — whoever is *on the right* is of some kind: whoever has a
  parent is a person.

These are the core ideas of the web's RDF Schema, written here as ordinary
rules.

---

## What we tell peye

```python
fact(subclass('cat', 'mammal'))
fact(subclass('mammal', 'animal'))
fact(subproperty('parent_of', 'related_to'))
fact(domain('parent_of', 'person'))
fact(codomain('parent_of', 'person'))
fact(type('koko', 'cat'))
fact(triple('alice', 'parent_of', 'bob'))

implies(subclass(A, B) & subclass(B, C), subclass(A, C))
implies(type(X, A) & subclass(A, B), type(X, B))
implies(triple(S, P, O) & subproperty(P, Q), triple(S, Q, O))
implies(triple(S, P, _) & domain(P, Class), type(S, Class))
implies(triple(_, P, O) & codomain(P, Class), type(O, Class))
```

`implies` means "keep applying this until nothing new follows". No question is
asked, so peye reports everything new.

---

## What peye concludes

```python
subclass('cat', 'animal')
type('koko', 'animal')
type('koko', 'mammal')
triple('alice', 'related_to', 'bob')
type('alice', 'person')
type('bob', 'person')
```

Six new facts, none of them typed in:

- cats are animals, so Koko is a mammal *and* an animal;
- Alice is related to Bob;
- both Alice and Bob are people — nobody said so directly.

---

## Why: the proof in plain words

Each conclusion cites the rule and facts behind it:

1. Cat ⊂ mammal and mammal ⊂ animal, so cat ⊂ animal — *rule 8*.
2. Koko is a cat, and cat ⊂ animal, so Koko is an animal — *rule 9*.
3. Alice is Bob's parent, and `parent_of` implies `related_to`, so Alice
   is related to Bob — *rule 10*.
4. Alice is a parent, and parents are people — *rule 11* (domain).
5. Bob has a parent, and those are people too — *rule 12* (codomain).

Step 2 builds on step 1: one conclusion feeds the next.

---

## Checked, not just claimed

A separate checker read all 13 proof steps against the program and
confirmed that:

- each step is an exact instance of the rule or fact it cites (13 of 13);
- no conclusion depends on itself in a circle;
- every step serves one of the 6 conclusions, and nothing extra is included.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/schema-inference.py            # the new facts
python -m peye --proof examples/schema-inference.py    # with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=schema-inference).

Add `fact(triple('bob', 'parent_of', 'carol'))` and run again: Bob becomes related to
Carol, and Carol is concluded to be a person.

---

## Takeaway

A schema says a lot in a few lines. peye spells out what it implies, and
every implied fact comes with the exact statements that support it — so a
surprising conclusion can be traced to the schema line that caused it.
