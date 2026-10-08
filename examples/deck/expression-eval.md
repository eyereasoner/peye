# Expression Evaluation

*Working out (2 × 3) + (10 − 4), and showing every intermediate result.*

[expression-eval.py](https://github.com/eyereasoner/peye/blob/main/examples/expression-eval.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/expression-eval.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/expression-eval.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/expression-eval.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=expression-eval)

---

## The question

A formula like **(2 × 3) + (10 − 4)** is really a little tree: the `+` at the
top, a multiplication and a subtraction below it, and plain numbers at the
bottom. Spreadsheets and calculators work through such trees all the time.

**What is the value of this formula?** And can we see how each part was
computed?

---

## What we tell peye: the formula

Every part of the formula gets a name, called a **node**:

```python
fact(literal('n2', 2))
fact(literal('n3', 3))
fact(literal('n10', 10))
fact(literal('n4', 4))
fact(expression('product', 'mul', 'n2', 'n3'))
fact(expression('difference', 'sub', 'n10', 'n4'))
fact(expression('total', 'add', 'product', 'difference'))
fact(root('example', 'total'))
```

`product` multiplies `n2` and `n3`; `difference` subtracts `n4` from `n10`;
`total` adds those two. The formula called `example` starts at `total`.

---

## What we tell peye: how to evaluate

```python
implied_by(value(Node, Value), literal(Node, Value))
implied_by(
    value(Node, Value),
    expression(Node, Operation, Left, Right)
    & value(Left, L)
    & value(Right, R)
    & calculate(Operation, L, R, Value),
)
implied_by(calculate('add', L, R, Value), is_(Value, L + R))
implied_by(calculate('sub', L, R, Value), is_(Value, L - R))
implied_by(calculate('mul', L, R, Value), is_(Value, L * R))
implies(root(Name, Node) & value(Node, Value), result(Name, Value))
```

A number's value is itself. An expression's value: evaluate both sides, then
apply the operation. This is **recursion**: a rule that uses itself on
smaller pieces until it reaches plain numbers.

---

## What peye concludes

```python
result('example', 12)
```

(2 × 3) + (10 − 4) = 6 + 6 = **12**.

---

## Why: the proof in plain words

The proof follows the tree from the top down, 22 steps in all:

1. `total` is 12, because `product` is 6, `difference` is 6, and 6 + 6 = 12.
2. `product` is 6, because `n2` is 2, `n3` is 3, and 2 × 3 = 6.
3. `difference` is 6, because `n10` is 10, `n4` is 4, and 10 − 4 = 6.
4. Each number's value comes straight from its `literal` fact.

Every step names the program line it used and the values it filled in.

---

## Checked, not just claimed

A separate checker read the proof against the program:

- 19 steps were matched to the exact program line they cite;
- 3 steps are arithmetic (2 × 3, 10 − 4, 6 + 6), and the checker
  **recomputed** each one itself and got the same answer;
- no step depends on itself in a circle, and nothing is extra.

Verdict: **checked**. All 22 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/expression-eval.py
python -m peye --proof examples/expression-eval.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=expression-eval).
Change `fact(literal('n4', 4))` to `fact(literal('n4', 1))` and run again: the
difference becomes 9 and the answer `result('example', 15)`.

---

## Takeaway

Even simple arithmetic is a chain of small steps. When each one is written
down and rechecked, a wrong input is easy to find, and a right answer is
easy to trust.
