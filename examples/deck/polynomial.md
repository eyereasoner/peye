# Polynomial Roots

*Solving equations up to x⁴ with formulas from the 1500s and 1700s.*

[polynomial.py](https://github.com/eyereasoner/peye/blob/main/examples/polynomial.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/polynomial.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/polynomial.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/polynomial.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=polynomial)

---

## The question

For x² there is the school formula. For x³ and x⁴ there are formulas too:
Cardano published the cubic one in 1545, and Lagrange later explained the
quartic one by reducing it to a cubic.

**For which x is x⁴ − 10x³ + 35x² − 50x + 24 equal to zero?** These x are
called the **roots** of the polynomial. Here they are 1, 2, 3 and 4.

The program is the solver of Alain Colmerauer, one of the creators of
Prolog, adapted for peye. His comments are kept in French.

---

## What we tell peye: the numbers

A polynomial is the list of its **coefficients**, the numbers in front of
each power of x, highest power first. Each number is a **complex number**: an
ordinary part plus a multiple of *i*, the square root of −1. It is written
`[Real, Imaginary]`; for ordinary numbers the second part is 0.

```python
query(roots([[1, 0], [-10, 0], [35, 0], [-50, 0], [24, 0]], _))
query(roots([[1, 0], [-9, -5], [14, 33], [24, -44], [-26, 0]], _))
```

The second polynomial has complex coefficients; its roots are 3+2i, 5+i,
i and 1+i.

---

## What we tell peye: the method

```python
implied_by(roots(P, L), findall(Z, racine(P, Z), L))
# …
implied_by(racine([A, B, C, D], Z), racine_cubique([A, B, C, D], Z))
implied_by(
    racine([A, B, C, D, E], Zp),
    est(T, B // fois([-4, 0], A))
    # …
    & solutionLagrange(P, Q, R, Z)
    & est(Zp, add(Z, T)),
)
```

`racine` ("root") finds one root at a time, with one clause per degree.
`findall` gathers *all* of them into a list. `est`, `fois`, `add` and `//`
(division) are complex arithmetic written out as ordinary rules.

---

## What peye concludes

```python
roots([[1, 0], [-10, 0], [35, 0], [-50, 0], [24, 0]], [[4.000000007450581, 0.0], [2.9999999925494194, 0.0], [1.9999999925494194, 0.0], [1.0000000074505806, 0.0]])
roots([[1, 0], [-9, -5], [14, 33], [24, -44], [-26, 0]], [[3.0000000000000036, 2.000000000000001], [5.000000000000005, 0.9999999999999927], [-5.773159728050814e-15, 1.0000000000000027], [0.9999999999999962, 1.0000000000000036]])
```

The roots 4, 3, 2, 1 and 3+2i, 5+i, i, 1+i, each **up to rounding**: the
formulas use square and cube roots, which a computer can only approximate.

---

## Why: the proof in plain words

The default proof is short: 4 steps.

1. The roots of the first polynomial are this list — *the `roots` rule*.
2. That list is everything `racine` finds for it — *a collected answer*.
3. and 4. The same for the second polynomial.

All the arithmetic happens *inside* the collection, so it is not spelled
out here. To see it, ask for one root at a time (see "Try it").

---

## Checked, not just claimed

Verdict: **checked_with_obligations**. 2 steps verified, and 2 obligations.

Both obligations are of the kind called `collected`: the claim that each
list contains *all* the roots `racine` can find. That comes from peye's
complete search, and the checker records it rather than proving it; it
confirmed that nothing in the proof contradicts either list.

For a cubic, asking for one root at a time gives a much bigger proof with
every calculation in it, and no obligations at all.

---

## Try it

```sh
python -m peye examples/polynomial.py
python -m peye --proof --goal "racine([[1, 0], [-6, 0], [11, 0], [-6, 0]], Z)" examples/polynomial.py
```

The second command solves the cubic x³ − 6x² + 11x − 6 one root at a time:
about 1, 2 and 3. Its proof has 263 steps, and the checker recomputes 124
calculations itself. Verdict: **checked**, with nothing taken on trust, even
under `--strict-proof`, which rejects any obligation.

---

## Takeaway

You can choose the shape of the explanation: a compact one that trusts a
complete search, or a long one where every multiplication is rechecked.
Either way, the report says exactly which one you got.
