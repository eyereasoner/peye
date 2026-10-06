# Kaprekar's 6174

*A number trick that always lands on 6174 — checked for every case, with one honest caveat.*

[kaprekar.py](https://github.com/eyereasoner/peye/blob/main/examples/kaprekar.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/kaprekar.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/kaprekar.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/kaprekar.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=kaprekar)

---

## The question

Take a four-digit number whose digits are not all the same. Sort its digits
from high to low and from low to high, and subtract. Repeat.

```text
3524  ->  5432 - 2345 = 3087
3087  ->  8730 - 0378 = 8352
8352  ->  8532 - 2358 = 6174
```

The mathematician D. R. Kaprekar noticed that you always reach **6174**.
**Does every such number get there within seven steps?**

---

## A shortcut that makes it checkable

There are 10,000 four-digit strings, but the first step only cares about
*which* digits occur, not their order: 3524 and 2453 give the same result.

So it is enough to check each **multiset** of four digits (a bag of digits,
order ignored) once. Leaving out the ten where all digits are equal, there
are 705 of them.

---

## What we tell peye

One step of the routine, written as a backward definition:

```python
backward(
    kaprekar_step(A, B),
    digits(A, Ds),
    sort4(Ds, Asc),
    reverse(Asc, Desc),
    number_of(Asc, Low),
    number_of(Desc, High),
    is_(B, High - Low),
)
```

And the claim to test:

```python
fact(reaches_6174(6174, _))
backward(
    reaches_6174(A, Steps),
    ne(A, 6174),
    Steps < 7,
    kaprekar_step(A, B),
    is_(Next, Steps + 1),
    reaches_6174(B, Next),
)

backward('counterexample', digit_multiset(A), ~reaches_6174(A, 0))
backward(kaprekar_verified(6174, 7), not_('counterexample'))
```

`~` and `not_` mean "cannot be shown". A **counterexample** is a multiset that does
*not* reach 6174 within seven steps.

---

## What peye concludes

```python
kaprekar_verified(6174, 7)
```

peye searched all 705 multisets and found no counterexample, so the claim
holds. `--stats` reports 152,940 inferences for that search.

---

## Why: the proof in plain words

The saved proof is tiny — two steps:

1. Kaprekar is verified — *rule 19*, because there is no counterexample.
2. There is no counterexample — *absent*: peye looked everywhere it could
   and found none.

The whole exhaustive search sits inside that second step. A proof can show
how something *was* found; it cannot list the absence of something in the
same way.

---

## Checked, with one obligation

The checker verified the one rule step, and that the proof is well founded,
covered and relevant. It also tried to refute the "absent" claim using
everything in the proof, and could not.

```python
obligation('absent', 'theory_scoped', ~'counterexample')
verdict('checked_with_obligations')
```

An **obligation** is a step taken on trust and listed openly. Here it says:
"there is no counterexample" rests on peye's completed search, not on a
step-by-step proof. 2 steps: 1 verified, 1 trusted.

---

## Why the caveat is honest, not a flaw

The claim *is* a claim about absence: no number fails. Any checker would have
to either redo the whole search or take it on trust.

peye chooses to say so in writing. If you need a proof with no trusted
steps, `--strict-proof` rejects this one; for most uses, knowing exactly
where the trust sits is what matters.

---

## Try it

```sh
python -m peye examples/kaprekar.py            # the answers
python -m peye --proof examples/kaprekar.py    # answers with their proof
python -m peye --goal "kaprekar_step(3524, B)" examples/kaprekar.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=kaprekar).
Change `Steps < 7` to `Steps < 6`: the conclusion disappears, because some
numbers really do need all seven steps.

---

## Takeaway

peye checked a famous number fact case by case, and its certificate says
plainly which part rests on "we searched and found nothing" — so you know
exactly what you are trusting.
