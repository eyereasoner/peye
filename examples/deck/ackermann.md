# Ackermann

*A function that grows faster than you can imagine, computed exactly and checked step by step.*

[ackermann.py](https://github.com/eyereasoner/peye/blob/main/examples/ackermann.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/ackermann.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/ackermann.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/ackermann.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=ackermann)

---

## The question

Adding is repeated counting. Multiplying is repeated adding. Raising to a
power is repeated multiplying. Keep going — repeated powers, then repeated
*that* — and numbers explode.

The **Ackermann function** A(X, Y) climbs this ladder: X says which rung,
Y how far to go. A(3, 4) is 125. A(4, 2) has **19,729 digits**.

**Can a computer get such numbers exactly right — and show how?**

---

## The ladder of operations

Mathematicians call the rungs *hyperoperations*. With base 2:

| Level | Operation | Example |
| --- | --- | --- |
| 1 | addition | 7 + 2 |
| 2 | multiplication | 7 × 2 |
| 3 | exponentiation (power) | 2⁷ = 128 |
| 4 | tetration (tower of powers) | 2^2^2^2 = 65,536 |

Each level above 3 is the level below, repeated.

---

## What we tell peye

```python
implied_by(ackermann([X, Y], A), is_(B, Y + 3) & hyper(X, B, 2, C) & is_(A, C - 3))

implied_by(hyper(0, Y, _, A), is_(A, Y + 1))
implied_by(hyper(1, Y, Z, A), is_(A, Y + Z))
implied_by(hyper(2, Y, Z, A), is_(A, Y * Z))
implied_by(hyper(3, Y, Z, A), is_(A, Z ** Y))
implied_by(hyper(X, 0, _, 1), X > 3)
implied_by(
    hyper(X, Y, Z, A),
    (X > 3)
    & (Y > 0)
    & is_(B, Y - 1)
    & hyper(X, B, Z, C)
    & is_(D, X - 1)
    & hyper(D, C, Z, A),
)

query(ackermann([3, 4], _))
# … ten more questions like this
```

The first four levels are plain arithmetic (`is_` means "compute", `**`
is power). The last rule says: level X, Y times, is level X−1 applied to
level X, Y−1 times.

---

## What peye concludes

```python
ackermann([0, 6], 7)
ackermann([2, 9], 21)
ackermann([3, 4], 125)
ackermann([3, 14], 131069)
ackermann([4, 1], 65533)
ackermann([4, 2], 2003529930406846464979072351560255750447825475569751419265016973710894…)
ackermann([5, 0], 65533)
```

7 of the 11 answers. The `[4, 2]` line goes on for 19,729 digits, ending
in `…5587895905719156733`. peye's integers have no size limit, so nothing
is rounded.

---

## Why: the proof in plain words

For A(3, 4) the proof says:

1. 4 + 3 = 7 — *a built-in calculation*.
2. 2⁷ = 128, so level 3 of 7 is 128 — *rule 5*.
3. 128 − 3 = 125 — *a built-in calculation*.
4. So A(3, 4) = 125 — *rule 1, with X = 3, Y = 4*.

A(4, 1) needs the repeating rule: the tower 2^2^2 is 16, and 2¹⁶ is 65,536
— *rule 7*, twice over. Steps already proved for one answer are reused by
the next.

---

## Checked, not just claimed

The checker read all 74 steps against the program:

- **33** steps matched exactly to the rule they cite;
- **41** calculations were **recomputed** by the checker itself and agreed
  — including the 19,729-digit power;
- no circular reasoning, and every step serves one of the 11 answers.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/ackermann.py            # the answers
python -m peye --proof examples/ackermann.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=ackermann).

Add `query(ackermann([3, 5], _))` at the end and run again: a new answer
appears, `ackermann([3, 5], 253)`.

---

## Takeaway

Enormous numbers are no excuse for "trust me". Every rung of the ladder is
an ordinary rule, every sum and power is recomputed by an independent
checker, and the answer is exact down to the last of its 19,729 digits.
