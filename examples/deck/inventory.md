# Inventory Invoice

*Adding up a shopping bill, and being honest about what "all the lines" means.*

[inventory.py](https://github.com/eyereasoner/peye/blob/main/examples/inventory.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/inventory.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/inventory.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/inventory.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=inventory)

---

## The question

You buy three kinds of fruit:

- 3 apples at 2 each,
- 4 pears at 3 each,
- 2 plums at 5 each.

**What is the total on the invoice?** Easy for a person; the interesting
part is how a computer can show its work, including the step "I added up
*all* the lines".

---

## What we tell peye

```python
fact(item('apple', 3, 2))
fact(item('pear', 4, 3))
fact(item('plum', 2, 5))
implies(item(Name, Quantity, Price) & is_(Total, Quantity * Price), line_total(Name, Total))
fact(sum([], 0))
implied_by(sum([X, *Xs], Total), sum(Xs, Rest) & is_(Total, X + Rest))
implies(findall(Amount, line_total(_, Amount), Amounts) & sum(Amounts, Total), invoice(Total))
```

- Each item has a name, a quantity and a price.
- A line total is quantity × price.
- `findall` gathers *every* line total into a list; `sum` adds the list up.

---

## What peye concludes

```python
invoice(28)
```

The line totals are 6, 12 and 10, and 6 + 12 + 10 = **28**.

---

## Why: the proof in plain words

1. The line totals, gathered together, are the list `[6, 12, 10]`.
2. The sum of `[10]` is 10 (10 + 0).
3. The sum of `[12, 10]` is 22 (12 + 10).
4. The sum of `[6, 12, 10]` is 28 (6 + 22).
5. So the invoice is 28 — *the `invoice` rule*.

The adding is done one number at a time, from the end of the list, and
each addition is a step of its own: 9 steps in all.

---

## Checked, not just claimed

The checker matched 5 steps to their program lines and **recomputed** the 3
additions itself. Verdict: **checked_with_obligations**.

The one obligation is of the kind called `collected`: the claim that
`[6, 12, 10]` is the *complete* list of line totals. A proof can show that
each number is a line total, but "there are no others" comes from peye
having searched everything it knows. The checker records that as an
obligation, and confirmed that nothing in the proof contradicts it.

---

## Try it

```sh
python -m peye examples/inventory.py            # the answers
python -m peye --proof examples/inventory.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=inventory).
Add `fact(item('fig', 5, 1))` and run again: the invoice becomes `invoice(33)`.

---

## Takeaway

A total is only right if no line was left out. peye does not hide that
assumption: the report names it, so you know exactly what you are trusting.
