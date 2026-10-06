# Path discovery

*Find flight routes from Ostend to Prague in a network of 7,698 airports.*

[path-discovery.py](https://github.com/eyereasoner/peye/blob/main/examples/path-discovery.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/path-discovery.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/path-discovery.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/path-discovery.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=path-discovery)

---

## The question

You want to fly from **Ostend-Bruges** to **Prague**, changing planes at
most twice. A **stopover** is an airport where you change planes on the way.

**Which routes are there?** No airport may be visited twice.

The data is a historical snapshot of airport connections, not today's
timetable.

---

## What we tell peye: the data

The file holds 7,698 airports and 37,505 one-way connections:

```python
fact(airport('AIRPORT_1', 'Goroka Airport'))
fact(airport('AIRPORT_10', 'Thule Air Base'))
# … 7,696 more airports …
fact(flight('AIRPORT_1', 'AIRPORT_2'))
fact(flight('AIRPORT_1', 'AIRPORT_3'))
# … 37,503 more connections …
```

`flight(A, B)` means there is a connection from A to B. That is about
2.1 MB of facts, followed by a few rules.

---

## What we tell peye: the rules

```python
backward(route_airports(From, To, _, Visited, [From, To]), flight(From, To), unvisited(To, Visited))
backward(
    route_airports(From, To, Remaining, Visited, [From, *Rest]),
    Remaining > 0,
    flight(From, Via),
    not_unify(Via, To),
    unvisited(Via, Visited),
    is_(Next, Remaining - 1),
    route_airports(Via, To, Next, [Via, *Visited], Rest),
)
```

- Either fly straight there, to an airport not yet visited;
- or, if stopovers remain, fly to a new airport `Via` and continue from
  there with one stopover fewer.

`path_discovery` wraps this, turning names into ids and back.

---

## What peye concludes

Three routes, all through Liège:

```text
Ostend-Bruges → Liège → Heraklion International Nikos Kazantzakis → Prague
Ostend-Bruges → Liège → Diagoras Airport → Prague
Ostend-Bruges → Liège → Palma De Mallorca → Prague
```

The real output lists the full names, for example:
`['Ostend-Bruges International Airport', 'Liège Airport', 'Diagoras Airport', 'Václav Havel Airport Prague']`.

---

## Why: the proof in plain words

For the Heraklion route, the proof records:

1. Ostend-Bruges is airport 310 and Prague is airport 1587 — *facts*;
2. 2 is a whole number, at least 0, and 310 is not 1587 — *built-ins*;
3. there is a flight 310 → 309 (Liège), and Liège is not yet visited;
4. there is a flight 309 → 1452 (Heraklion), and Heraklion is new too;
5. there is a flight 1452 → 1587, and Prague is new — route complete.

"Not yet visited" is shown by comparing against each earlier airport, one by
one, so even that part is spelled out.

---

## Checked, not just claimed

Out of 37,505 connections, the proof cites only the handful each route uses.
It has 76 steps behind the 3 routes:

- 53 steps are exact instances of the program lines they cite;
- 23 built-in comparisons and subtractions are recomputed and agree;
- nothing is circular or extra.

Verdict: **checked**. Nothing taken on trust: the "no repeats" rule uses
explicit "is not the same as" tests rather than "cannot be shown", so it
leaves no obligations.

---

## Try it

```sh
python -m peye examples/path-discovery.py            # the answers
python -m peye --proof examples/path-discovery.py    # answers with their proof
python -m peye --goal "path_discovery('Liège Airport', 'Václav Havel Airport Prague', 1, Path)" examples/path-discovery.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=path-discovery).
With 0 stopovers only direct flights count:
`--goal "path_discovery('Ostend-Bruges International Airport', 'Liège Airport', 0, Path)"`
gives the single route Ostend-Bruges → Liège.

---

## Takeaway

Even in a large dataset, an answer's proof stays small: it names only the
flights that route uses, and every one of them can be checked against the
data.
