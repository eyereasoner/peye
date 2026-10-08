# State transitions

*Replay a bank account's history, one event at a time, to get today's balance.*

[state-transitions.py](https://github.com/eyereasoner/peye/blob/main/examples/state-transitions.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/state-transitions.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/state-transitions.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/state-transitions.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=state-transitions)

---

## The question

An account opens with 100. Then three things happen, in order: a deposit of
25, a withdrawal of 40, a withdrawal of 20.

**What is the balance after event 3?** And can we see how each event
changed it?

---

## What we tell peye: the history

An **event log** is a numbered list of what happened:

```python
fact(opening_balance(100))
fact(event(1, 'deposit', 25))
fact(event(2, 'withdraw', 40))
fact(event(3, 'withdraw', 20))
```

Each balance is a **state**, and each event is a **transition**: a step from
one state to the next.

---

## What we tell peye: the rules

```python
implied_by(balance(0, Amount), opening_balance(Amount))
implied_by(
    balance(N, Amount),
    (N > 0)
    & event(N, 'deposit', Value)
    & is_(Before, N - 1)
    & balance(Before, Previous)
    & is_(Amount, Previous + Value),
)
implied_by(
    balance(N, Amount),
    (N > 0)
    & event(N, 'withdraw', Value)
    & is_(Before, N - 1)
    & balance(Before, Previous)
    & is_(Amount, Previous - Value),
)
query(balance(3, Amount))
```

- Before any event, the balance is the opening balance.
- After a deposit, it is the previous balance plus the amount.
- After a withdrawal, it is the previous balance minus the amount.

`is_(Before, N - 1)` computes a value: `Before` becomes N − 1.

---

## What peye concludes

```python
balance(3, 65)
```

After the three events, the balance is 65.

---

## Why: the proof in plain words

Read from the start of the log:

1. balance 0 is 100 — *the opening balance (rule 5, fact 1)*;
2. event 1 deposits 25, so balance 1 is 100 + 25 = 125 — *rule 6*;
3. event 2 withdraws 40, so balance 2 is 125 − 40 = 85 — *rule 7*;
4. event 3 withdraws 20, so balance 3 is 85 − 20 = 65 — *rule 7*.

The proof also records each small calculation, such as "3 − 1 = 2" for
finding the previous event.

---

## Checked, not just claimed

The proof has 17 steps. The checker found:

- 8 steps that are exact instances of the program lines they cite;
- 9 built-in calculations (the sums, differences and "N > 0" tests) that it
  recomputed and that agree;
- no circular reasoning: each balance rests only on the one before it.

Verdict: **checked**. All 17 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/state-transitions.py            # the answers
python -m peye --proof examples/state-transitions.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=state-transitions).
Add `fact(event(4, 'deposit', 10))` and change the last line to
`query(balance(4, Amount))`: the answer becomes `balance(4, 75)`.

---

## Takeaway

An audit trail you can trust: the final number comes with every
intermediate balance and every calculation that led to it, each one
rechecked.
