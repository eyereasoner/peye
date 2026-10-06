# Integrity

*A rule that should never fire, and a clear alarm when it does.*

[integrity.py](https://github.com/eyereasoner/peye/blob/main/examples/integrity.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/integrity.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/integrity.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/integrity.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=integrity)

---

## The question

A bank keeps a simple promise: **no account may have a negative balance.**

A rule like that is an *integrity constraint*: not a way to derive new
facts, but a condition the data must never break. If it is broken, we want
to know at once, and know *which* record broke it.

---

## What we tell peye

Two accounts and the constraint:

```python
fact(account('alice', 30))
fact(account('bob', -5))
contradiction(account(Owner, Balance), Balance < 0)
```

The last line reads: *if some Owner has a Balance below 0, then
`false`* — that is, the data contradicts itself.

---

## What peye concludes

```python
'false'
```

And the program stops with **exit code 65**.

An exit code is the number a program hands back to whatever started it;
0 means "all fine". peye uses 65 to say "a `false` was derived: the data
breaks a constraint". A script or pipeline can notice that and stop.

---

## Why: the proof in plain words

The alarm comes with its reason:

1. Bob's balance is −5 — *a fact we gave (fact 2)*.
2. −5 is less than 0 — *a calculation*.
3. So `false` — *rule 3, with Owner = bob, Balance = −5*.

Alice's account does not appear: it played no part in the violation.

---

## Checked, not just claimed

Even an alarm can be checked. The checker confirms that:

- the 2 reasoning steps are true instances of the lines they cite;
- the comparison −5 < 0 is recomputed and holds;
- the proof contains nothing beyond what explains the violation.

Verdict: **checked**. All 3 steps verified, nothing taken on trust. The proof
is valid; it is the *data* that is wrong.

---

## Try it

```sh
python -m peye examples/integrity.py; echo "exit code: $?"
python -m peye --proof examples/integrity.py
```

Change Bob's balance to `fact(account('bob', 5))` and run again: nothing is
printed, and the exit code is 0.

---

## Takeaway

A good constraint fails loudly and explains itself. Here the run stops with a
distinct exit code, and the checked proof points straight at Bob's −5.
