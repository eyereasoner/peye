# Backward

*Two ways of reasoning in one tiny program: pushing facts forward, and asking questions backward.*

[backward.py](https://github.com/eyereasoner/peye/blob/main/examples/backward.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/backward.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/backward.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/backward.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=backward)

---

## The question

Is 5 more interesting than 3? Here "more interesting" just means "bigger".

The real point is *how* peye gets there. It can reason in two directions:

- **forward**: start from what is known and keep adding conclusions;
- **backward**: start from a question and work back to what would answer it.

This example uses both, one inside the other.

---

## What we tell peye

One definition and one rule:

```python
implied_by(more_interesting(X, Y), X > Y)
implies(more_interesting(5, 3), indeed_more_interesting(5, 3))
```

- `implied_by` is a **backward definition**: X is more interesting
  than Y *if* X > Y. peye only uses it when some question needs it.
- `implies` is a **forward rule**: if 5 is more interesting than 3, then
  record that it is *indeed* more interesting.

---

## How the two directions meet

To fire the forward rule, peye needs to know whether
`more_interesting(5, 3)` holds. It does not look that up in a table; it
*asks*, using the backward definition.

That definition in turn asks a built-in question: is `5 > 3`? A **built-in**
is a calculation the language does itself, such as comparing numbers.

---

## What peye concludes

```python
indeed_more_interesting(5, 3)
```

One new fact, produced by the forward rule. The backward definition did its
work behind the scenes, and it shows up in the proof instead.

---

## Why: the proof in plain words

The saved proof has three steps:

1. 5 is indeed more interesting than 3 — *rule 2*, because…
2. 5 is more interesting than 3 — *rule 1, with X = 5 and Y = 3*, because…
3. 5 > 3 — *a built-in comparison*.

The forward step and the backward steps sit in one chain, each naming the
program line it used.

---

## Checked, not just claimed

A separate checker reads the proof against the program:

- the 2 steps that cite a program line really are instances of that line;
- the 1 built-in step, `5 > 3`, is recomputed and agrees;
- there is no circular reasoning, and nothing in the proof is extra.

Verdict: **checked**. All 3 steps verified, 1 claim answered, nothing taken
on trust.

---

## Try it

```sh
python -m peye examples/backward.py
python -m peye --proof examples/backward.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=backward).
In the last line, change both `(5, 3)` to `(3, 5)`: since 3 > 5 is false,
peye concludes nothing and prints nothing.

---

## Takeaway

Forward rules build up what is known; backward definitions answer questions
on demand. peye lets you mix them freely, and the proof stitches both into
one readable chain of reasons.
