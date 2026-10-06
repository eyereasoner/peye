# Policy Risk

*Reviewing a contract's clauses: what is risky, how risky, and what to fix.*

[policy-risk.py](https://github.com/eyereasoner/peye/blob/main/examples/policy-risk.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/policy-risk.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/policy-risk.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/policy-risk.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=policy-risk)

---

## The question

Terms of service are full of clauses: "we may remove your account", "we may
change these terms", "we may share your data". Some come with safeguards
(notice, consent); some don't.

**Which clauses are risky, in what order should we look at them, and what
would fix each one?**

This is a small illustrative model: the scores are made-up parameters, not
legal advice.

---

## What we tell peye: the clauses

```python
fact(permission('c1', 'remove_account'))
fact(permission('c2', 'change_terms'))
fact(notice_days('c2', 3))
fact(permission('c3', 'share_data'))
fact(prohibition('c4', 'export_data'))
fact(permission('c5', 'share_data'))
fact(safeguard('c5', 'consent'))
fact(permission('c6', 'change_terms'))
fact(notice_days('c6', 14))
fact(required_notice(14))
fact(importance('consent', 12))
# … and three more importance weights
```

c3 and c5 both allow sharing data, but only c5 asks for consent.

---

## What we tell peye: one finding rule

Each kind of risk has a rule. This one flags sharing without consent:

```python
forward(
    finding(Clause, Raw, 'sharing_without_consent', 'require_consent'),
    permission(Clause, 'share_data'),
    ~safeguard(Clause, 'consent'),
    importance('consent', Weight),
    is_(Raw, 85 + Weight),
)
```

`~` means **"not"**: the rule fires only if no consent safeguard is known.

Further rules cap scores at 100, label them high (80+), moderate (50–79) or
low, and give each finding a **rank**: 1 plus the number of findings that
score higher.

---

## What peye concludes

```python
report(1, 'c1', 100, 'high', 'no_removal_safeguards', 'add_notice_and_inform')
report(2, 'c3', 97, 'high', 'sharing_without_consent', 'require_consent')
report(3, 'c2', 85, 'high', short_notice(3, 14), increase_notice(14))
report(4, 'c4', 70, 'moderate', 'export_prohibited', 'permit_export')
```

(Sorted by rank here; peye prints them in the order it found them.)

Each line: rank, clause, score, severity, the reason, and a suggested fix.
c5 and c6 do not appear: c5 has consent, and c6 gives the full 14 days'
notice.

---

## Why: the proof in plain words

Take clause c1, which lets the provider remove your account:

1. c1 permits account removal — *a fact we gave*.
2. c1 has **no** notice period, and **no** "inform the user" safeguard —
   *nothing found after searching*.
3. Raw score 90 + 20 = 110 — *recomputed*; above 100, so it is capped at 100.
4. 100 is at least 80: severity **high**.
5. The list of scores higher than 100 is **empty**, so c1 has rank 1.

Steps 2 and 5 rely on "nothing more to find", which the next card is about.

---

## Checked, with obligations

- **57 steps** for 4 answers: 32 verified against the program lines they
  cite, and 18 calculations and comparisons recomputed.
- **7 steps are taken on trust**:
  - 3 **`absent`** obligations — "c1 has no notice", "c1 has no inform
    safeguard", "c3 has no consent safeguard". peye searched and found
    nothing; the checker records this rather than proving it.
  - 4 **`collected`** obligations — the lists of higher scores used for each
    rank, e.g. for 85 the list `[100, 97]`. That each list is complete is
    recorded, not proved.
- The checker tries to refute all 7 against the evidence and finds no
  contradiction.

Verdict: **checked_with_obligations**.

---

## Try it

```sh
python -m peye examples/policy-risk.py                                              # the report
python -m peye --check-proof examples/proof/policy-risk.py examples/policy-risk.py   # the check
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=policy-risk).
Add `fact(safeguard('c3', 'consent'))` and run again: the c3 finding disappears, and
c2 and c4 move up to ranks 2 and 3.

---

## Takeaway

A risk list is only useful if you can see why each item is on it. Here every
finding carries its reason and fix, and the report spells out exactly which
"nothing was found" assumptions the ranking depends on.
