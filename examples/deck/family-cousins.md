# Family cousins

*Work out who belongs to which generation, and who counts as a cousin.*

[family-cousins.py](https://github.com/eyereasoner/peye/blob/main/examples/family-cousins.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/family-cousins.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/family-cousins.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/family-cousins.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=family-cousins)

---

## The question

A small family tree: Adam has two children, Bob and Carol. They have
children, and some of those have children of their own.

**Which people are cousins?** Here the program defines a cousin as someone
in the *same generation* but a *different branch* of the family.

---

## What we tell peye

Who is whose parent, where generation 0 starts, and which branch four of
the grandchildren belong to:

```python
fact(parent('adam', 'bob'))
fact(parent('adam', 'carol'))
fact(parent('bob', 'dave'))
# … 6 more parent facts …
fact(generation('adam', 0))
fact(branch('dave', 'b'))
fact(branch('frank', 'c'))
# … 2 more branch facts …
```

Branch `'b'` is Bob's side of the family; branch `'c'` is Carol's.

---

## The three rules

```python
implies(parent(Parent, Child) & generation(Parent, N) & is_(Next, N + 1), generation(Child, Next))
implies(parent(Parent, Child) & branch(Parent, Branch), branch(Child, Branch))
implies(
    generation(X, N)
    & generation(Y, N)
    & branch(X, A)
    & branch(Y, B)
    & not_unify(A, B),
    cousin(X, Y),
)
```

- A child is one generation below its parent.
- A child belongs to its parent's branch.
- X and Y are cousins if they share a generation but their branches differ
  (`not_unify` means "is not the same as").

---

## What peye concludes

24 new facts. An excerpt:

```python
generation('dave', 2)
generation('frank', 2)
branch('judy', 'c')
cousin('dave', 'frank')
cousin('eve', 'grace')
cousin('heidi', 'judy')
# … and 18 more
```

Each cousin pair appears both ways round, such as `cousin('dave', 'frank')`
and `cousin('frank', 'dave')`. That makes 12 cousin facts across two
generations.

---

## A rule says exactly what it says

Heidi and Ivan are not listed as cousins, even though their parents (Dave
and Eve) are siblings. Both sit in branch `'b'`, so this program's rule does
not count them.

A genealogist would disagree. The program is not wrong about itself: it
answers by *its* definition, and the proof shows exactly which definition
that was.

---

## Why: the proof in plain words

Why are Dave and Frank cousins?

1. Adam is generation 0 — *a fact*.
2. Bob is Adam's child, so generation 1 — *rule 15*, with 0 + 1 = 1.
3. Dave is Bob's child, so generation 2 — *rule 15*, with 1 + 1 = 2.
4. Frank is generation 2 the same way, through Carol.
5. Dave is in branch `'b'`, Frank in branch `'c'` — *facts*.
6. `'b'` is not `'c'`, so they are cousins — *rule 17*.

---

## Checked, not just claimed

The whole proof has 43 steps behind the 24 conclusions. The checker found:

- 38 steps that are exact instances of the program lines they cite;
- 5 built-in steps (the additions and the "not the same" tests) that it
  recomputed and that agree;
- no circular reasoning, and every step serves an answer.

Verdict: **checked**. All 43 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/family-cousins.py
python -m peye --proof examples/family-cousins.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=family-cousins).
Add `fact(parent('grace', 'kim'))` and run again: Kim joins generation 3 and
branch `'c'`, and becomes a cousin of Heidi and Ivan.

---

## Takeaway

Small, plain rules about parents add up to a whole family picture. And when
a result surprises you, the proof shows which rule produced it, so you can
tell a bug in the data from a choice in the definition.
