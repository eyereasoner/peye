# GPS: goal-driven routes

*Plan a trip from Gent to Oostende that stays within your time, budget and comfort limits.*

[gps.py](https://github.com/eyereasoner/peye/blob/main/examples/gps.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/gps.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/gps.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/gps.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=gps)

---

## The question

You are in Gent and want to get to Oostende. There are a few roads, and each
drive has a **duration**, a **cost**, a **belief** (how sure we are it will
work out) and a **comfort** score.

**Which sequences of drives reach Oostende without breaking any limit?**

GPS here stands for *Goal-driven Parallel Sequences*, a planning method by
Jos De Roo, not satellite navigation.

---

## What we tell peye: the map

Four possible drives on a partial map of Belgium, each written like this:

```python
fact(
    description('map_be', [location(S, 'gent'), 'true', location(S, 'brugge'), 'drive_gent_brugge', 1500.0, 0.006, 0.96, 0.99]),
)
```

From Gent to Brugge by the action `'drive_gent_brugge'`, with duration
1500.0, cost 0.006, belief 0.96 and comfort 0.99.
The other drives are Gent–Kortrijk, Kortrijk–Brugge and Brugge–Oostende.

---

## What we tell peye: the limits

The question names the goal and five limits:

```python
query(
    findpath('map_be', [location(_SUBJECT, 'oostende'), _PATH, _DURATION, _COST, _BELIEF, _COMFORT, [5000.0, 5.0, 0.2, 0.4, 1]]),
)
```

Duration at most 5000, cost at most 5.0, belief at least 0.2, comfort at
least 0.4, and at most 1 **stage** (a run of steps on the same map). Along a
route, durations and costs add up; beliefs and comforts multiply.

---

## How the search works

The program keeps the current **state** as a list of facts, starting from
`[location('i1', 'gent')]`.

At each step it asks: does the goal already hold? If not, pick a drive that
starts where we are, replace the old location with the new one, update the
running totals, and check every limit before going on.

A route that breaks a limit is dropped right there.

---

## What peye concludes

Two routes qualify (lines wrapped to fit):

```python
findpath('map_be', [location('i1', 'oostende'),
  ['drive_gent_brugge', 'drive_brugge_oostende'],
  2400.0, 0.01, 0.9408, 0.99, [5000.0, 5.0, 0.2, 0.4, 1]])
findpath('map_be', [location('i1', 'oostende'),
  ['drive_gent_kortrijk', 'drive_kortrijk_brugge', 'drive_brugge_oostende'],
  4100.0, 0.018000000000000002, 0.903168, 0.9801, [5000.0, 5.0, 0.2, 0.4, 1]])
```

The direct route via Brugge takes 2400; the detour via Kortrijk takes 4100.
(The long cost figure is how computers store 0.018 in binary.)

---

## Why: the proof in plain words

For the Brugge route, the proof records, among other steps:

1. we start in Gent — *fact 19, the current state*;
2. Oostende is not reached yet, since Gent is not Oostende;
3. the drive Gent→Brugge applies — *fact 15*, and Gent is replaced by Brugge;
4. duration 0 + 1500, belief 1.0 × 0.96, and so on, each within its limit;
5. the drive Brugge→Oostende applies, and now the goal holds.

Every addition, multiplication and comparison is written into the proof.

---

## Checked, not just claimed

The proof has 93 steps behind the 2 routes. The checker found:

- 44 steps that are exact instances of the program lines they cite;
- 44 built-in calculations (sums, products, comparisons) that it recomputed
  and that agree;
- 5 steps that commit to the first way of finishing (`once`), each matching
  the step it wraps.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/gps.py
python -m peye --proof examples/gps.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=gps).
Lower the duration limit from `5000.0` to `3000.0`: the Kortrijk detour
(4100) no longer fits, and only the Brugge route remains.

---

## Takeaway

A planner that explains itself: each route comes with the running totals
and every limit check that let it through, and a checker has redone the
arithmetic.
