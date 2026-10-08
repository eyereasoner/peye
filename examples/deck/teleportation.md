# Teleportation

*Sending a quantum state with two ordinary bits, checked for every case.*

[teleportation.py](https://github.com/eyereasoner/peye/blob/main/examples/teleportation.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/teleportation.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/teleportation.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/teleportation.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=teleportation)

---

## The question

In *quantum teleportation*, Alice wants to give Bob a *qubit* (a quantum
bit) without sending the qubit itself. They share a linked pair of qubits
in advance. Alice makes a measurement, phones Bob two ordinary bits (one of
four outcomes, 0 to 3), and Bob applies a fix that depends on the outcome.

**Does Bob always end up with exactly the state Alice had** — for every
state and every outcome?

---

## A simplified quantum world

The program uses *discrete quantum theory*: a toy version where amplitudes
are just "there or not", and two ways of reaching the same result cancel
each other out. A result survives only if it can be reached an **odd**
number of ways.

It keeps the strange parts — superposition, interference, entanglement —
small enough to check exhaustively. Three states are tested: `zero`, `one`,
and `plus` (both at once).

---

## What we tell peye

```python
# … the shared pair, Alice's measurement and Bob's fixes
implied_by(received(S, M, Z), qubit(Z) & findall(Path, path(S, M, Z, Path), Paths) & odd(Paths))
# …
implies(name(S) & outcome(M) & findall(Z, received(S, M, Z), Received), teleported(S, M, Received))
# …
contradiction(teleported(S, _, Received), sent(S, Sent), not_identical(Received, Sent))
```

`findall` gathers *all* answers. The `contradiction` rule is a safety
alarm: if Bob's state ever differs from Alice's, the run stops with exit
code 65.

---

## What peye concludes

```python
teleported('zero', 0, ['false'])
teleported('one', 0, ['true'])
teleported('plus', 0, ['false', 'true'])
teleported('plus', 3, ['false', 'true'])
```

…12 answers in all: 3 states × 4 outcomes. In every one, Bob holds exactly
what Alice sent (`zero` is `['false']`, `one` is `['true']`, `plus` is
both), and the alarm never fires.

---

## Why: the proof in plain words

For each of the 12 cases, the proof says:

1. S is one of the three states — *a fact we gave*.
2. M is one of the four outcomes — *a fact we gave*.
3. Gathering all the values Bob can receive gives this list — *collected*.
4. So this is what Bob holds — *rule 37*.

Step 3 is where the quantum work happens, and it is a "find all" step.

---

## Checked, not just claimed

- **19** steps are confirmed against the program lines they cite.
- **12** steps are taken on trust as *collected* obligations: for each case,
  that the list of values Bob receives is complete. A proof can show what
  is in a list, not that nothing was left out, so the checker records this.
- The checker looked for evidence against all 12 lists and found none.

Verdict: **checked_with_obligations**. 31 steps, 12 on trust. Honestly put:
the counting of paths sits inside those 12 obligations.

---

## Try it

```sh
python -m peye examples/teleportation.py            # the answers
python -m peye --proof examples/teleportation.py    # answers with their proof
```

Break Bob's fix for outcome 0: in `implied_by(bob(0, Y, Z), kg(Y, Z))` replace
`kg(Y, Z)` with `id(Y, Z)`. Now Bob sometimes gets the wrong state, peye
prints `'false'` and exits with code 65.

---

## Takeaway

Even a quantum protocol can be checked case by case with a few rules. peye
covers all 12 cases, and is upfront that the "all answers" lists are the
part you are trusting.
