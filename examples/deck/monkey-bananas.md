# Monkey and bananas

*A classic planning puzzle: how does the monkey reach the bananas?*

[monkey-bananas.py](https://github.com/eyereasoner/peye/blob/main/examples/monkey-bananas.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/monkey-bananas.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/monkey-bananas.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/monkey-bananas.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=monkey-bananas)

---

## The question

A room has three spots: loc1, loc2 and loc3. Bananas hang from the ceiling
at loc1, too high to reach. The monkey stands at loc2. A box sits at loc3.

The monkey can walk, push the box, climb on and off it, and grab.
**Which sequences of up to five moves end with the monkey holding the
bananas?** This kind of question is called *planning*.

---

## What we tell peye

A situation is a list: `[Bananas, Monkey, Box, OnBox, HasBananas]`, where
`'y'`/`'n'` mean yes/no.

```python
fact(initial_state(['loc1', 'loc2', 'loc3', 'n', 'n']))
fact(goal_state([_, _, _, _, 'y']))

fact(legal_move([B, M, M, 'n', H], 'climb_on', [B, M, M, 'y', H]))
fact(legal_move([B, B, B, 'y', 'n'], 'grab', [B, B, B, 'y', 'y']))
backward(legal_move([B, M, M, 'n', H], push(X), [B, X, X, 'n', H]), location(X), not_unify(X, M))
backward(legal_move([B, M, L, 'n', H], go(X), [B, X, L, 'n', H]), location(X), not_unify(X, M))
# …
```

Repeated letters mean "the same place": you can only grab when monkey, box
and bananas are all at B and the monkey is on the box. `_` means "anything",
and `not_unify(X, M)` means X and M are different places.

---

## Asking for plans

```python
forward(plan(Moves), in_range(1, 5, N), moves(N, Moves), reaches_goal(Moves))
```

For each length N from 1 to 5, make a list of N moves still to be chosen,
and keep it if it leads from the start to the goal. Shorter plans are tried
first.

---

## What peye concludes

```python
plan([go('loc3'), push('loc1'), 'climb_on', 'grab'])
plan([go('loc1'), go('loc3'), push('loc1'), 'climb_on', 'grab'])
plan([go('loc3'), push('loc1'), 'climb_on', 'grab', 'climb_off'])
plan([go('loc3'), push('loc2'), push('loc1'), 'climb_on', 'grab'])
```

One four-move plan, and three five-move variations of it (a detour, an extra
climb down, an extra push).

---

## Why: the proof in plain words

For the shortest plan, the proof walks through each situation:

1. Start: bananas at loc1, monkey at loc2, box at loc3.
2. `go('loc3')`: the monkey walks to the box — allowed, since loc3 ≠ loc2.
3. `push('loc1')`: monkey and box move to loc1, under the bananas.
4. `'climb_on'`: monkey and box are in the same place, so it can climb.
5. `'grab'`: everything at loc1 and on the box, so it gets the bananas.

---

## Checked, not just claimed

The checker reads the proof against the program:

- **61** steps are instances of the program lines they cite: each move is
  a legal move, each situation follows from the last;
- **25** small calculations (counting 1 to 5, "loc3 ≠ loc2") are redone and
  agree;
- every step serves one of the four plans.

Verdict: **checked**. All 86 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/monkey-bananas.py            # the answers
python -m peye --proof examples/monkey-bananas.py    # answers with their proof
```

Change `in_range(1, 5, N)` to `in_range(1, 4, N)` to allow at most four
moves: only the shortest plan remains.

---

## Takeaway

A plan is a chain of small, checkable moves. peye finds the plans and
records why each move was allowed, so you can follow the monkey step by step.
