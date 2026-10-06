# Who Killed Aunt Agatha?

*A murder mystery where the answer has to hold no matter how the gaps are filled.*

[aunt-agatha.py](https://github.com/eyereasoner/peye/blob/main/examples/aunt-agatha.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/aunt-agatha.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/aunt-agatha.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/aunt-agatha.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=aunt-agatha)

---

## The question

Someone in Dreadbury Mansion killed Aunt Agatha. Three people live there:
Agatha, the butler and Charles. We are told nine things, among them:

- a killer always hates their victim, and is never richer than them;
- Charles hates no one that Agatha hates;
- Agatha hates everyone except the butler;
- no one hates everyone.

**Who did it?** This is a classic test puzzle for theorem provers
(Pelletier's problem 55).

---

## "Follows from" means "true in every case"

The clues leave a lot open: we are not told exactly who hates whom, or who
is richer than whom. Each way of filling in those gaps that obeys all nine
clues is called a **model**: one possible situation the clues allow.

A conclusion is **entailed** (it really follows) only if it is true in
*every* model. Being true in one model only makes it possible.

So the program does the honest thing: it lists every model, and looks at
who the killer is in each one.

---

## What we tell peye

Each clue becomes one line inside the definition of a model:

```python
backward(
    model(Killer, world(Richer, Hates)),
    # …
    resident(Killer),                                    # 1, 2
    hates(Hates, Killer, 'agatha', 'yes'),               # 3
    richer(Richer, Killer, 'no'),
    implies_not(AA, CA),                                 # 4
    implies_not(AB, CB),
    implies_not(AC, CC),
    unify(AA, 'yes'),                                    # 5
    unify(AC, 'yes'),
    # … clues 6 and 7 …
    label([RA, RB, RC, AA, AB, AC, BA, BB, BC, CA, CB, CC]),
    some_no(AA, AB, AC),                                 # 8
    some_no(BA, BB, BC),
    some_no(CA, CB, CC),
)
```

The twelve open questions (`AA` = "does Agatha hate Agatha?", and so on) are
each tried as `'yes'` and as `'no'`; `label` makes sure every model is found
exactly once.

---

## Counting the cases

Three rules then turn "every model" into a verdict:

```python
forward(models(Suspect, N), resident(Suspect), findall(W, model(Suspect, W), Ws), count(Ws, N))
forward(
    entailed(killed('agatha', 'agatha')),
    models('agatha', N),
    N > 0,
    models('butler', 0),
    models('charles', 0),
)
forward(witness(Killer, W), once(model(Killer, W)))
```

`findall` gathers *all* models for a suspect into a list, and `count`
counts them. Agatha's guilt is entailed if she is the killer in at least one
model and the others are killers in none.

---

## What peye concludes

```python
models('agatha', 4)
models('butler', 0)
models('charles', 0)
entailed(killed('agatha', 'agatha'))
```

The clues allow exactly four situations, and in all four Agatha is the
killer. **Agatha killed herself.** It is not a guess: there is no other way
the clues can be true.

---

## Why: one situation, in full

peye also prints one model as a **witness**, an example you can inspect:

```python
witness('agatha', world(richer('no', 'yes', 'yes'), hates('yes', 'no', 'yes', 'yes', 'no', 'yes', 'no', 'yes', 'no')))
```

Read it as: Agatha is not richer than herself; the butler and Charles are
richer than her. Agatha hates herself and Charles, the butler hates Agatha
and Charles, Charles hates only the butler.

The proof walks through this model and shows each clue holding in it, one
program line at a time. Then it counts the lists of models: 4, 0 and 0.

---

## Checked, not just claimed

The checker verified 40 steps directly and recomputed 8 calculations
itself. Verdict: **checked_with_obligations**.

There are 3 obligations, all of the kind called `collected`. They are the
three "all models" lists: four models for Agatha, none for the butler, none
for Charles. That each list is *complete* is the heart of the argument, and
it comes from peye's exhaustive search; the checker records it as an
obligation rather than proving it. It did confirm that nothing in the proof
contradicts those lists, and that no step relies on circular reasoning.

---

## Try it

```sh
python -m peye examples/aunt-agatha.py
python -m peye --proof examples/aunt-agatha.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=aunt-agatha).
Delete clue 4 (the three `implies_not` lines) and run again: now there are 14
models with Agatha as killer and 6 with Charles, so `entailed(...)`
disappears. Without that clue, the mystery has no single answer.

---

## Takeaway

"It follows" is a strong claim: true in every situation the facts allow.
Here you can see all the situations counted, one of them in full, and
exactly which part of the argument rests on the search being complete.
