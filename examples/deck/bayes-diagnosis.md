# Bayes Diagnosis

*A printer shows two symptoms. Which fault is most likely, and by how much?*

[bayes-diagnosis.py](https://github.com/eyereasoner/peye/blob/main/examples/bayes-diagnosis.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/bayes-diagnosis.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/bayes-diagnosis.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/bayes-diagnosis.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=bayes-diagnosis)

---

## The question

A printer reports a **paper jam** and it is also **offline**. Three faults
could be behind it: a real paper jam, a lost network connection, or a power
problem.

**How likely is each fault, given what we see?** And can the computer show
every number it used?

The numbers in this example are made up to illustrate the method. They are
not real fault statistics.

---

## The idea: weigh each explanation

This is *Bayes' rule*, a standard way to update beliefs with evidence:

- Start with how common each fault is (the **prior**).
- Multiply by how likely each symptom is *if* that fault were the cause.
- Divide each result by the sum of all of them, so the chances add up to 1.

The example is *naive* Bayes: it treats the two symptoms as independent
clues, so their chances can simply be multiplied.

---

## What we tell peye

```python
fact(fault('paper_jam', 20, 90, 10))
fact(fault('network_loss', 30, 5, 95))
fact(fault('power_loss', 50, 1, 99))
implies(
    fault(Fault, Prior, Jam, Offline)
    & is_(Weight, Prior * Jam * Offline),
    weight(Fault, Weight),
)
# … sum_weights adds up a list, in two lines
implies(findall(W, weight(Fault, W), Weights) & sum_weights(Weights, Total), total(Total))
implies(
    weight(Fault, Numerator)
    & total(Denominator)
    & (Denominator > 0)
    & is_(Probability, Numerator / Denominator),
    posterior(Fault, Numerator, Denominator, Probability),
)
```

Each fault line reads: name, prior, chance of a jam, chance of being
offline — all whole percentages. `findall` gathers *all* the weights into
one list.

---

## What peye concludes

```python
posterior('paper_jam', 18000, 37200, 0.4838709677419355)
posterior('network_loss', 14250, 37200, 0.38306451612903225)
posterior('power_loss', 4950, 37200, 0.13306451612903225)
```

A paper jam is the best explanation, at about 48%. Power loss was the most
common fault beforehand (50%), but it rarely shows up as a jam, so it drops
to about 13%.

The weights stay exact whole numbers; only the final division gives a
decimal.

---

## Why: the proof in plain words

For the paper jam, the proof records:

1. Its numbers 20, 90 and 10 — *a fact we gave (fact 1)*.
2. 20 × 90 × 10 = 18000 — *a calculation, rule 4*.
3. All three weights are [18000, 14250, 4950] — *collected with `findall`*.
4. 4950 + 0 = 4950, then 14250 + 4950 = 19200, then 18000 + 19200 = 37200 —
   *rule 6, applied three times*.
5. 37200 > 0, and 18000 / 37200 = 0.4838709677419355 — *rule 8*.

The other two faults reuse the same total.

---

## Checked, not just claimed

A separate checker read all 25 steps of the proof against the program:

- 14 steps are verified as exact instances of the program lines they cite;
- 10 calculations (products, sums, the comparison, the divisions) are
  recomputed, and they agree;
- 1 step is taken on trust and listed as an **obligation**.

That obligation is the `findall`: the claim that [18000, 14250, 4950] is
*every* weight there is. A proof can show that each weight exists, but not
that nothing is missing, so the checker records it. It did confirm that no
weight in the proof is missing from that list.

Verdict: **checked_with_obligations**.

---

## Try it

```sh
python -m peye examples/bayes-diagnosis.py            # the answers
python -m peye --proof examples/bayes-diagnosis.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=bayes-diagnosis).
Make paper jams twice as common: change its prior from `20` to `40`. The
total becomes 55200 and the paper jam rises to about 65%
(0.6521739130434783).

---

## Takeaway

A probability is only as trustworthy as the arithmetic behind it. Here every
multiplication, sum and division is on the record and recomputed, and the one
thing taken on trust — that the list of weights is complete — is named
rather than hidden.
