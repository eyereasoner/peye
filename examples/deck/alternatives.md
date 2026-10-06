# Alternatives

*Two ways out of Paris, and three ways of asking about them.*

[alternatives.py](https://github.com/eyereasoner/peye/blob/main/examples/alternatives.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/alternatives.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/alternatives.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/alternatives.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=alternatives)

---

## The question

From Paris you can take a train to Brussels, or a bus to Lille.

Everyday questions about choices come in different shapes:

- **Where can I go?** (every option)
- **Can I go to Brussels *or* Lille?** (is at least one option open?)
- **Just give me one route.** (the first that works, and stop)

This example asks all three, and shows the reasoning behind each answer.

---

## What we tell peye

Two facts, and two rules that both define a `route`:

```python
fact(train('paris', 'brussels'))
fact(bus('paris', 'lille'))
backward(route(From, To), train(From, To))
backward(route(From, To), bus(From, To))
```

Two rules with the same name are **alternatives**: a route is a train
connection, *or* a bus connection. The `backward` means "work this out when
someone asks".

---

## The three questions

```python
query(route('paris', To))
query(train('paris', 'brussels') | bus('paris', 'lille'))
query(once(route('paris', To)))
```

- Line 1 asks for every destination `To` reachable from Paris.
- Line 2 uses `|`, which means **or**: is either connection there?
- Line 3 wraps the question in `once`: find the *first* route and commit to
  it, without looking for more.

A line of the form `query(Question)` tells peye to answer that question.

---

## What peye concludes

```python
route('paris', 'brussels')
route('paris', 'lille')
train('paris', 'brussels') | bus('paris', 'lille')
once(route('paris', 'brussels'))
```

- Both routes, one from each alternative rule.
- The "or" question holds, and is reported just as it was asked.
- `once` picked Brussels, because the train rule comes first, and stopped there.

---

## Why: the proof in plain words

1. Paris to Brussels by train — *fact 1*.
2. So there is a route Paris to Brussels — *rule 3, the train alternative*.
3. Paris to Lille by bus — *fact 2*.
4. So there is a route Paris to Lille — *rule 4, the bus alternative*.
5. "Train to Brussels or bus to Lille" holds — *because the first half does
   (step 1)*. One true side is enough for an "or".
6. "Once, a route" gives Brussels — *because of step 2*.

---

## Checked, not just claimed

A separate checker reads the proof against the program. The report says:

- **6 steps**: 4 verified as exact instances of the program lines they cite,
  and 2 (the "or" and the `once`) checked by confirming the step they rest on.
- No circular reasoning, every claim is justified, and nothing in the proof
  is extra.
- **0** steps taken on trust.

Verdict: **checked**.

---

## Try it

```sh
python -m peye examples/alternatives.py            # the answers
python -m peye --proof examples/alternatives.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=alternatives).

Add `fact(train('paris', 'amsterdam'))` after the bus line and run again: a third
route, `route('paris', 'amsterdam')`, appears, but `once` still answers Brussels,
because that train fact still comes first.

---

## Takeaway

"All of them", "at least one" and "just the first" are different questions.
peye lets you say which one you mean, and its proof shows exactly which
option answered.
