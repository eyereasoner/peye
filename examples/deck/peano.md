# Peano

*Counting with nothing but zero and "one more" — and getting 5! = 120 out of it.*

[peano.py](https://github.com/eyereasoner/peye/blob/main/examples/peano.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/peano.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/peano.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/peano.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=peano)

---

## The question

Can you do arithmetic without digits? In 1889 Giuseppe Peano showed
that all natural numbers can be built from just two things: **zero**, and
**the next number after** (the *successor*).

- **In how many ways can 3 be split into two numbers that add up to it?**
- **What is (1 × 2) + 3, and what is its factorial?** (The factorial of 5,
  written 5!, is 5 × 4 × 3 × 2 × 1.)

---

## Numbers as nested boxes

Write the successor of N as `s(N)`. Then:

| Number | Written as |
| --- | --- |
| 0 | `'zero'` |
| 1 | `s('zero')` |
| 2 | `s(s('zero'))` |
| 3 | `s(s(s('zero')))` |

A number is simply how many `s(…)` wrappers surround `'zero'`. No built-in
arithmetic is used anywhere in this example.

---

## What we tell peye

```python
fact(add(A, 'zero', A))
implied_by(add(A, s(B), s(C)), add(A, B, C))
fact(multiply(_, 'zero', 'zero'))
implied_by(multiply(A, s(B), C), multiply(A, B, D) & add(A, D, C))
fact(factorial('zero', s('zero')))
implied_by(factorial(s(N), F), factorial(N, Before) & multiply(s(N), Before, F))
query(add(A, B, s(s(s('zero')))))
query(
    multiply(s('zero'), s(s('zero')), Product),
    add(Product, s(s(s('zero'))), Sum),
    factorial(Sum, Factorial),
)
```

Adding is "A + 0 = A, and A + (B+1) = (A+B)+1". Multiplying is repeated
adding; factorial is repeated multiplying.

---

## What peye concludes

The first question runs addition *backward* — the sum is known, the parts
are not — and finds every split of 3:

```python
add(s(s(s('zero'))), 'zero', s(s(s('zero'))))
add(s(s('zero')), s('zero'), s(s(s('zero'))))
add(s('zero'), s(s('zero')), s(s(s('zero'))))
add('zero', s(s(s('zero'))), s(s(s('zero'))))
```

That is 3+0, 2+1, 1+2 and 0+3. The second answer says 1 × 2 = 2,
2 + 3 = 5, and 5! is `s(s(s(…('zero')…)))` with **120** `s` wrappers — a
single line of 510 characters.

---

## Why: the proof in plain words

For the split 2 + 1 = 3:

1. 2 + 0 = 2 — *a fact we gave (fact 1), with A = 2*.
2. So 2 + 1 = 3 — *rule 2, with A = 2, B = 0, C = 2*.

The factorial answer chains the same moves: multiplication steps made of
addition steps, factorial steps made of multiplication steps. Altogether
the proof has 198 steps, each naming the line it used.

---

## Checked, not just claimed

A separate checker read all 198 steps against the program:

- every one of the 198 steps is an exact instance of the line it cites;
- no calculation needed recomputing — there is no built-in arithmetic,
  only rules (0 recomputed);
- no step depends on itself, and every step serves one of the 5 answers.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/peano.py            # the answers
python -m peye --proof examples/peano.py    # answers with their proof
python -m peye --goal "add(A, B, s(s(s('zero'))))" examples/peano.py
```

`--goal` asks your own question instead of the program's. Try
`--goal "multiply(s(s('zero')), s(s(s('zero'))), P)"`: 2 × 3 comes back as
`s(s(s(s(s(s('zero'))))))`, which is 6.
Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=peano).

---

## Takeaway

Arithmetic can be pure reasoning: two ideas, a few rules, and every result
traced back to "zero" and "one more". The same rules even run backward,
answering "what adds up to 3?".
