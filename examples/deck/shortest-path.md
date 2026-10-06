# Shortest Path

*The cheapest way from A to D, and the honest fine print behind "cheapest".*

[shortest-path.py](https://github.com/eyereasoner/peye/blob/main/examples/shortest-path.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/shortest-path.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/shortest-path.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/shortest-path.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=shortest-path)

---

## The question

A small road map: four places, five one-way roads, each with a cost (think
minutes, or kilometres).

```text
a --4--> b --3--> d
a --2--> c --1--> b
         c --8--> d
```

**What is the cheapest way to get from a to d?**

Finding *a* route is easy. Saying a route is the *cheapest* means saying that
**no cheaper route exists** — a claim about everything you didn't pick.

---

## What we tell peye: the map and the routes

```python
fact(edge('a', 'b', 4))
fact(edge('a', 'c', 2))
fact(edge('c', 'b', 1))
fact(edge('b', 'd', 3))
fact(edge('c', 'd', 8))
forward(path(X, Y, Cost), edge(X, Y, Cost))
forward(path(X, Z, Cost), path(X, Y, Before), edge(Y, Z, Weight), is_(Cost, Before + Weight))
```

A road is a path; a path followed by one more road is a longer path, and the
costs add up. `forward` means "keep applying this until nothing new follows".

---

## What we tell peye: "cheapest"

```python
backward(cheaper(X, Y, Cost), path(X, Y, Other), Other < Cost)
forward(shortest(X, Y, Cost), path(X, Y, Cost), ~cheaper(X, Y, Cost))
query(shortest('a', 'd', Cost))
```

`~` means **"not"**. A path is the shortest if there is **no** cheaper path
between the same two places. The last line asks the question.

peye first finishes listing all paths, and only then looks for "no cheaper
one", so the search for something cheaper is over a complete list.

---

## What peye concludes

```python
shortest('a', 'd', 6)
```

There are three ways from a to d, costing 7 (via b), 10 (via c) and 6 (via c,
then b). The cheapest costs **6**.

---

## Why: the proof in plain words

1. Road a → c costs 2 — *fact 2*, so there is a path of cost 2.
2. Road c → b costs 1 — *fact 3*; path a → b now costs 2 + 1 = 3.
3. Road b → d costs 3 — *fact 4*; path a → d now costs 3 + 3 = 6.
4. **No** path from a to d is cheaper than 6 — *searched, none found*.
5. So the shortest a → d costs 6 — *the `shortest` rule*.

Steps 1–3 are shown in full. Step 4 is different: it is a claim that
something does *not* exist.

---

## Checked, with one obligation

- **10 steps**: 7 verified against the program lines they cite, and the
  two additions recomputed by the checker.
- **1 step is taken on trust**: an **`absent`** obligation,
  `~cheaper('a', 'd', 6)`.

An absence means peye looked through everything it knows and found no
cheaper path. A proof can show a path exists; it cannot show one doesn't. So
the checker records this as an obligation, and checks that nothing in the
proof contradicts it — no cheaper path appears there.

Verdict: **checked_with_obligations**.

---

## Strict mode

If you need a proof with nothing taken on trust, ask for it:

```sh
python -m peye --proof examples/shortest-path.py > /tmp/sp-proof.py
python -m peye --strict-proof --check-proof /tmp/sp-proof.py examples/shortest-path.py
```

The strict check refuses this proof — verdict `failed(1)` — because it leans
on the trusted absence. Nothing is wrong with the answer; strict mode just
does not accept "searched and found nothing" as evidence.

---

## Try it

```sh
python -m peye examples/shortest-path.py            # the answer
python -m peye --proof examples/shortest-path.py    # with its proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=shortest-path).
Add a direct road `fact(edge('a', 'd', 5))` and run again: the answer becomes
`shortest('a', 'd', 5)`.

---

## Takeaway

"Best" always hides a "nothing better exists". peye shows the route it
found, and tells you plainly which part of the answer is a search that came
up empty.
