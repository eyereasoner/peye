# Interval Relations

*Thirteen ways two time slots can relate, worked out for a whole schedule.*

[interval-relations.py](https://github.com/eyereasoner/peye/blob/main/examples/interval-relations.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/interval-relations.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/interval-relations.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/interval-relations.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=interval-relations)

---

## The question

Two meetings can sit in time in exactly one of **thirteen** ways: one is
*before* the other, one *meets* the other (ends exactly as it starts), they
*overlap*, one *starts* or *finishes* the other, one is *during* the other,
they are *equal* — plus the reverse of each (*after*, *met by*, …).

This classification is known as **Allen's interval relations**, and it is the
basis of a lot of scheduling and planning software.

**Given a day's worth of time slots, how does every pair relate?**

---

## What we tell peye: the time slots

Times are in minutes after midnight: 600 is 10:00, 720 is 12:00.

```python
fact(interval('a', 600, 720))
fact(interval('b', 780, 900))
# … five more like these
fact(interval('h', 540, 960))
fact(start_duration('i', 960, 120))
fact(end_duration('j', 960, 60))
```

So a runs 10:00–12:00 and h 09:00–16:00. Slot i starts at 16:00 and lasts
120 minutes; slot j ends at 16:00 after 60 minutes.

Each slot is **half-open**: it includes its start minute but not its end, so
a slot ending at 12:00 and one starting at 12:00 touch without overlapping.

---

## What we tell peye: the rules

Missing endpoints are filled in, then each relation gets a rule:

```python
implies(start_duration(I, S, D) & (D > 0) & is_(E, S + D), interval(I, S, E))
implies(end_duration(I, E, D) & (D > 0) & is_(S, E - D), interval(I, S, E))
implied_by(valid_interval(I, S, E), interval(I, S, E) & (S < E))
implies(pair(I, J, SI, EI, SJ, EJ) & (EI < SJ), relation(I, 'before', J))
implies(pair(I, J, SI, EI, SJ, EJ) & eq(EI, SJ), relation(I, 'meets', J))
implies(pair(I, J, SI, EI, SJ, EJ) & (SJ < SI) & (EI < EJ), relation(I, 'during', J))
# … overlaps, starts, finishes, equals
implies(relation(I, 'before', J), relation(J, 'after', I))
# … and the other five reverse relations
```

Only *valid* slots (start before end) are compared, so empty or backwards
slots are left out.

---

## What peye concludes

```python
relation('a', 'before', 'b')
relation('j', 'meets', 'i')
relation('a', 'overlaps', 'd')
relation('f', 'starts', 'a')
relation('a', 'during', 'h')
relation('g', 'finishes', 'a')
relation('a', 'equals', 'e')
relation('h', 'contains', 'a')
# … 100 relations in all
```

Every slot also *equals* itself, so lines like `relation('a', 'equals', 'a')` appear
too.

---

## Why: the proof in plain words

Take `relation('a', 'before', 'i')`:

1. Slot a runs from 600 to 720 — *a fact we gave* — and 600 < 720, so it is
   valid.
2. Slot i starts at 960 and lasts 120 minutes — *a fact we gave* — so it ends
   at 960 + 120 = 1080 — *the endpoint rule*.
3. 960 < 1080, so i is valid too.
4. a ends at 720, before i starts at 960 — *the "before" rule*.

The reverse, `relation('i', 'after', 'a')`, then follows from the "after" rule in
one more step.

---

## Checked, not just claimed

- **214 steps** for 100 answers: 178 verified against the program lines they
  cite, and **36 calculations and comparisons recomputed** by the checker.
- No circular reasoning: the reverse relations rest on the forward ones,
  never the other way round.
- **0** steps taken on trust.

Verdict: **checked**.

---

## Try it

```sh
python -m peye examples/interval-relations.py            # all 100 relations
python -m peye --proof examples/interval-relations.py    # with their proofs
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=interval-relations).
Add `fact(start_duration('k', 600, 60))` (10:00 for one hour) and run again: k gets
its own relations, among them `relation('k', 'equals', 'f')`,
`relation('k', 'starts', 'a')` and `relation('k', 'meets', 'g')`.

---

## Takeaway

Thirteen precise definitions turn a vague "do these clash?" into exact
answers, each one traceable back to the start and end times it came from.
