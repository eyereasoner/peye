# Goldbach

*A famous unsolved question, tested on numbers up to 33 million.*

[goldbach.py](https://github.com/eyereasoner/peye/blob/main/examples/goldbach.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/goldbach.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/goldbach.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/goldbach.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=goldbach)

---

## The question

A **prime** is a whole number greater than 1 that only 1 and itself divide:
2, 3, 5, 7, 11, …

In 1742 Christian Goldbach guessed that **every even number greater than 2 is
the sum of two primes**: 8 = 3 + 5, 16 = 3 + 13. Nobody has proved it yet,
but nobody has found an exception either.

This example tests it on every power of two from 4 to 2²⁵ = 33,554,432,
and for each one finds the split whose smaller prime is as small as possible.

---

## What we tell peye: finding a split

```python
fact(split(4, [2, 2]))
backward(split(N, Pair), eq(0, N % 2), N > 4, once(split_from(N, Pair, 3)))

backward(split_from(N, [P, Q], P), is_(Q, N - P), is_prime(Q))
backward(split_from(N, Pair, P), P < N, once(next_prime(P, Next)), split_from(N, Pair, Next))
```

In words: start with the prime P = 3. If N − P is prime, that is the split.
If not, move on to the next prime and try again. `once` means: take the
first split found and stop.

---

## What we tell peye: testing for primes

```python
fact(is_prime(2))
fact(is_prime(3))
backward(is_prime(P), P > 3, eq(1, P % 2), ~has_factor(P, 3))

backward(has_factor(N, L), eq(0, N % L))
backward(has_factor(N, L), L * L < N, is_(M, L + 2), has_factor(N, M))
```

This is **trial division**: an odd number is prime if none of 3, 5, 7, …
(up to its square root) divides it. `~` means **"not"**: it succeeds when
the search for a factor finds nothing.

---

## What peye concludes

```python
goldbach(4, [2, 2])
goldbach(8, [3, 5])
goldbach(16, [3, 13])
goldbach(128, [19, 109])
goldbach(8388608, [37, 8388571])
goldbach(33554432, [61, 33554371])
# … 24 lines in all, one per power of two
```

Every power of two in the range splits into two primes, as Goldbach predicted.
(Testing cases is not a proof of the conjecture, of course.)

---

## Why: the proof in plain words

Take 8 = 2³:

1. The exponent 3 is in the range 2 to 25, and 2³ = 8 — *recomputed*.
2. 8 is even and larger than 4, so the general split rule applies.
3. Try P = 3: 8 − 3 = 5.
4. 5 is prime: it is above 3, it is odd, and **no factor was found**
   starting from 3.
5. So 8 = 3 + 5, and that is the answer for 8.

Larger numbers follow the same pattern, sometimes after stepping through
several primes P before N − P turns out to be prime.

---

## Checked, with obligations

- **913 steps** for 24 answers: 506 verified against the program lines they
  cite, 333 calculations recomputed, and 39 `once` steps checked by the step
  they rest on.
- **35 steps are taken on trust**, each an **`absent`** obligation like
  `~has_factor(5, 3)`: "this number has no factor starting from 3".

An absence is peye saying *"I searched everything the program allows and
found nothing"*. A proof can show a factor exists, but it cannot show one
doesn't; so the checker records each of these instead of proving it.

---

## What the checker still does with them

The checker tries to **refute** each trusted absence: it looks for evidence
in the program or the proof that a factor *was* found after all. All 35 hold
up.

Verdict: **checked_with_obligations** — valid, provided those 35 "no factor
found" searches were complete.

Want zero trust? `--strict-proof` rejects any proof that leans on such an
obligation.

---

## Try it

```sh
python -m peye examples/goldbach.py                                          # the splits
python -m peye --check-proof examples/proof/goldbach.py examples/goldbach.py   # the report
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=goldbach).
Change `in_range(2, 25, I)` to `in_range(2, 26, I)` and run again: one more
line appears, `goldbach(67108864, [5, 67108859])`.

---

## Takeaway

Even a search for "no factor" is made visible: the proof shows every split it
found, and the report is honest about the 35 places where it relies on
"searched and found nothing".
