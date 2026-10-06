# Complex numbers

*Teaching a reasoner a kind of number it has never heard of.*

[complex.py](https://github.com/eyereasoner/peye/blob/main/examples/complex.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/complex.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/complex.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/complex.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=complex)

---

## The question

A *complex number* is a pair of ordinary numbers, a real part and an
imaginary part, written here as `complex(3, 4)` for 3 + 4i. The special
number i has the property that i × i = −1. Engineers use these for waves,
circuits and rotations.

peye has no complex numbers built in. **Can we define them with a few
rules, and get answers that are both right and explained?**

---

## What we tell peye

How to add and multiply pairs, as ordinary rules:

```python
backward(complex_add(complex(A, B), complex(C, D), complex(R, I)), is_(R, A + C), is_(I, B + D))
backward(
    complex_mul(complex(A, B), complex(C, D), complex(R, I)),
    is_(R, A * C - B * D),
    is_(I, A * D + B * C),
)

fact(point('z', complex(3, 4)))
fact(point('w', complex(1, 2)))

forward(sum(Sum), point('z', Z), point('w', W), complex_add(Z, W, Sum))
forward(product(Product), point('z', Z), point('w', W), complex_mul(Z, W, Product))
forward(unit_square(Square), complex_mul(complex(0, 1), complex(0, 1), Square))
# …
```

Division, powers, polar form, logarithms, sine and cosine follow the same way.

---

## What peye concludes

A few of its 23 answers:

```python
sum(complex(4, 6))
product(complex(-5, 10))
quotient(complex(3.0, 4.0))
ratio(complex(2.2, -0.4))
unit_square(complex(-1, 0))
integer_power(8, complex(16, 0))
power('self_power', complex(0.20787957635076193, 0.0))
sine(complex(1.9999999999999998, 1.0605752387249067e-16))
```

…and 15 more.

---

## Reading the answers

- **i × i = −1** (`unit_square`) is *derived* from the multiplication rule,
  not assumed.
- Dividing the product by w gives back z: 3 + 4i, exactly. Division `/`
  always gives decimals, so it reads `complex(3.0, 4.0)`; dividing z by w
  does not divide evenly, so it becomes 2.2 and −0.4.
- Multiplying by 1 + i eight times lands on 16, back on the real line.
- i to the power i is the ordinary number 0.2078…
- The sine of the arcsine of 2 comes back as 1.9999999999999998: decimal
  arithmetic on a computer is very close, but not perfectly exact.

---

## Why: the proof in plain words

Take `product(complex(-5, 10))`:

1. z is 3 + 4i and w is 1 + 2i — *facts we gave*.
2. The multiplication rule, with A = 3, B = 4, C = 1, D = 2, says the result
   is (3·1 − 4·2) + (3·2 + 4·1)i.
3. 3·1 − 4·2 = −5 and 3·2 + 4·1 = 10 — *each a calculation, recorded*.

Every one of the 23 answers has a trail like this.

---

## Checked, not just claimed

The checker reads the proof against the program:

- **93** steps are instances of the program lines they cite;
- **122** calculations are redone by the checker itself, every part of every
  number, and agree;
- no circular reasoning, nothing extra, every answer accounted for.

Verdict: **checked**. All 215 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/complex.py
python -m peye --goal "complex_power(complex(1, 1), 16, Result)" examples/complex.py
python -m peye --goal "complex_div(complex(1, 0), complex(0, 1), Inverse)" examples/complex.py
```

These give `complex(256, 0)` and `complex(0.0, -1.0)` (so 1 / i = −i).
Change `fact(turns(8))` to `fact(turns(4))`: the answer becomes
`integer_power(4, complex(-4, 0))`, half-way round.

---

## Takeaway

A new kind of number is just a handful of rules. Because every calculation is
recorded and redone by the checker, you can see exactly where results stay
exact and where decimals creep in.
