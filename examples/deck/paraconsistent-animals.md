# Paraconsistent Animals

*When the facts disagree, say so, instead of pretending they don't.*

[paraconsistent-animals.py](https://github.com/eyereasoner/peye/blob/main/examples/paraconsistent-animals.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/paraconsistent-animals.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/paraconsistent-animals.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/paraconsistent-animals.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=paraconsistent-animals)

---

## The question

Birds fly. Penguins don't. Tweety is a bird *and* a penguin. Does Tweety fly?

Real data is often like this: two rules, or a rule and an observation,
point in opposite directions. Ordinary logic breaks down here: from a
contradiction it lets you conclude anything at all.

**Paraconsistent** reasoning is reasoning that keeps working when the data
contains contradictions. It keeps the conflict contained and visible.

---

## What we tell peye: animals and rules

```python
fact(bird('tweety'))
fact(penguin('tweety'))
fact(bird('falco'))
fact(penguin('opus'))
fact(mammal('batsy'))
fact(bat('batsy'))
fact(fish('nemo'))
fact(bird('mythic'))
fact(observed('mythic', 'flies', 'false'))
forward(flies(X, 'true'), bird(X))
forward(wings(X, 'true'), bird(X))
forward(flies(X, 'false'), penguin(X))
forward(wings(X, 'false'), mammal(X))
forward(flies(X, 'true') & wings(X, 'true'), bat(X))
# …
```

Conclusions are written as `flies(X, 'true')` or `flies(X, 'false')`, so both
can be recorded side by side without the program falling over.

---

## What we tell peye: summaries

Each property gets a local summary: *true only*, *false only*, or *both*.

```python
forward(flight_status(X, 'both'), flies(X, 'true'), flies(X, 'false'))
forward(flight_status(X, 'true_only'), flies(X, 'true'), ~flies(X, 'false'))
# …
forward(flies_safely(X, 'true'), flight_status(X, 'true_only'))
forward(flies_safely(X, 'undecided'), flight_status(X, 'both'))
```

`~` means "not found": nothing peye knows says otherwise. Decisions read
only the summary, so a conflict leads to *undecided*, never to both answers.

---

## What peye concludes

50 conclusions in all. The interesting ones:

```python
inconsistent('tweety', 'flies')
needs_review('tweety', 'flies')
inconsistent('mythic', 'flies')
inconsistent('batsy', 'wings')
flies_safely('tweety', 'undecided')
flies_safely('falco', 'true')
flies_safely('opus', 'false')
moves_by('opus', 'walking')
```

Tweety (bird and penguin) and Mythic (a bird seen not flying) are flagged
for review. Batsy the bat has wings by one rule and none by the mammal rule.
Falco, Opus and Nemo are clear-cut.

---

## Why: the proof in plain words

For Tweety:

1. Tweety flies — *birds fly*, because `bird('tweety')`.
2. Tweety does not fly — *penguins don't*, because `penguin('tweety')`.
3. So Tweety's flight status is *both*, and Tweety needs review.

For Falco:

1. Falco flies — *birds fly*.
2. Nothing says Falco does not fly (a search that found nothing).
3. So Falco's status is *true only*, and Falco flies safely.

---

## Checked, not just claimed

59 steps were verified against the program. Verdict:
**checked_with_obligations**.

The 7 obligations are all of the kind called `absent`, one for each "not
found" the decisions rely on, such as:

```python
obligation('absent', 'theory_scoped', ~flies('falco', 'false'))
```

peye concluded that nothing says Falco cannot fly because it searched
everything it knows and found nothing. The checker records each such
absence rather than proving it, and confirmed that no step in the proof
contradicts any of them.

---

## Try it

```sh
python -m peye examples/paraconsistent-animals.py            # the answers
python -m peye --proof examples/paraconsistent-animals.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=paraconsistent-animals).
Delete the line `fact(observed('mythic', 'flies', 'false'))` and run again: the
conflict disappears, and you get `flies_safely('mythic', 'true')` and
`moves_by('mythic', 'flying')`.

---

## Takeaway

Contradictions in data are not a reason to give up or to guess. Kept local
and labelled, they become a to-do list for a human, while everything that
is clear-cut still gets decided.
