# Wolf, goat and cabbage

*The river crossing puzzle, with the shortest answer shown to be shortest.*

[wolf-goat-cabbage.py](https://github.com/eyereasoner/peye/blob/main/examples/wolf-goat-cabbage.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/wolf-goat-cabbage.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/wolf-goat-cabbage.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/wolf-goat-cabbage.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=wolf-goat-cabbage)

---

## The question

A farmer must get a wolf, a goat and a cabbage across a river. The boat
holds the farmer and at most one passenger. Left alone, the wolf eats the
goat, and the goat eats the cabbage.

**How can he do it, and what is the fewest number of crossings?** Finding a
plan is one thing; showing no shorter plan exists is another.

---

## What we tell peye

A situation lists which bank, west (`'w'`) or east (`'e'`), the farmer,
wolf, goat and cabbage are on. Everyone starts west.

```python
fact(solution(['e', 'e', 'e', 'e'], []))
implied_by(solution(State, [Move, *Rest]), move(State, Move, Next) & safe(Next) & solution(Next, Rest))

implied_by(move([X, X, Goat, Cabbage], 'wolf', [Y, Y, Goat, Cabbage]), change(X, Y))
implied_by(move([X, Wolf, Goat, Cabbage], 'nothing', [Y, Wolf, Goat, Cabbage]), change(X, Y))
# … same for goat and cabbage

# Safe when the goat is with the farmer, or with neither the wolf nor the cabbage.
implied_by(
    safe([Farmer, Wolf, Goat, Cabbage]),
    one_eq(Farmer, Goat, Wolf)
    & one_eq(Farmer, Goat, Cabbage),
)
```

---

## Asking for the shortest plan

```python
implied_by(
    'shorter_solution',
    in_range(0, 6, N)
    & moves(N, Plan)
    & solution(['w', 'w', 'w', 'w'], Plan),
)

implied_by(
    wolf_goat_cabbage_verified(7),
    not_('shorter_solution')
    & moves(7, Plan)
    & once(solution(['w', 'w', 'w', 'w'], Plan)),
)
implied_by(
    shortest_crossing(Plan),
    not_('shorter_solution')
    & moves(7, Plan)
    & solution(['w', 'w', 'w', 'w'], Plan),
)
```

In words: *there is no safe plan with 0 to 6 crossings* (`not_` means "it
is not the case that"), *and there is one with 7*.

---

## What peye concludes

```python
wolf_goat_cabbage_verified(7)
shortest_crossing(['goat', 'nothing', 'wolf', 'goat', 'cabbage', 'nothing', 'goat'])
shortest_crossing(['goat', 'nothing', 'cabbage', 'goat', 'wolf', 'nothing', 'goat'])
```

Seven crossings, and exactly two seven-crossing plans: they differ only in
whether the wolf or the cabbage goes over first.

---

## Why: the proof in plain words

The first plan, crossing by crossing:

1. Take the goat over. (Wolf and cabbage are safe together.)
2. Come back alone.
3. Take the wolf over.
4. Bring the goat back — otherwise the wolf would eat it.
5. Take the cabbage over.
6. Come back alone.
7. Take the goat over. Everyone is east.

The proof checks that every in-between situation is safe.

---

## Checked, not just claimed

- **56** steps are confirmed against the program lines they cite, and 15
  calculations and choices are rechecked.
- **1** step is taken on trust, as an *absent* obligation: "there is no
  shorter solution". peye searched every plan of 0 to 6 crossings and
  found none; the checker records that rather than proving a negative.

Verdict: **checked_with_obligations**. 72 steps, 1 on trust. So the plans
are fully checked; the claim *"7 is the minimum"* is the obligation.

---

## Try it

```sh
python -m peye examples/wolf-goat-cabbage.py            # the answers
python -m peye --proof examples/wolf-goat-cabbage.py    # answers with their proof
```

Change `in_range(0, 6, N)` to `in_range(0, 7, N)`. Now "a shorter solution"
includes 7-crossing plans, which exist, so the claim fails and peye prints
nothing at all.

---

## Takeaway

"Here is a plan" and "no better plan exists" are different kinds of claim.
peye proves the first step by step, and labels the second clearly as the
part that rests on an exhaustive search.
