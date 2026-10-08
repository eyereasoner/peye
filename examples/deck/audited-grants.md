# Audited grants

*A program that reasons about its own reasoning, because there is only one language to speak.*

[audited-grants.py](https://github.com/eyereasoner/peye/blob/main/examples/audited-grants.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/audited-grants.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/audited-grants.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/audited-grants.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=audited-grants)

---

## The question

A town hands out energy grants. Five people applied. Deciding who gets one is
the easy part. The hard questions come afterwards, from an auditor:

- **On which data does each decision rest?**
- **What did each decision take on trust?**
- **Which decisions would collapse if someone's self-declared income were
  wrong?**

Usually that means exporting a decision log, writing a script to parse it,
and hoping both agree with what the decision engine actually did.

---

## One language, all the way down

In peye the rules, the data, the conclusions, the proof and the check report
are all written the same way: as Python terms. So one program can:

1. state the grant policy,
2. have peye decide and **prove** every decision,
3. read that proof and its check report back **as facts**,
4. and answer the auditor with ordinary rules over them.

No export format, no parser, no second tool. The audit reasons over the very
certificate that was checked.

---

## The policy

The applications are plain Python data, and the policy is a program of its
own, stated by a function:

```python
APPLICATIONS = [
    ('ann', 2100, 4, 'payslip'),
    ('bob', 2900, 2, 'payslip'),
    ('cara', 1800, 1, 'self_declared'),
    ('dan', 2400, 3, 'self_declared'),
    ('eve', 2000, 2, 'payslip'),
]

def policy():
    for name, money, size, evidence in APPLICATIONS:
        fact(applicant(name), income(name, money), household(name, size))
    fact(already_received('eve'))
    implies(applicant(P) & income(P, I) & (I < 2500) & ~already_received(P), grant(P))
    implies(grant(P) & household(P, N) & (N >= 3), top_up(P))
    implies(applicant(P) & income(P, I) & (I >= 2500), refused(P, 'income above 2500'))
```

A grant needs an income below 2500 and no earlier grant; a household of
three or more gets a top-up.

---

## Reading the proof back

```python
decided = run(build(policy), proof=True)

facts_from(text=check_report(decided.proof_report))
for term, line in read_terms(decided.proof):
    kind = getattr(term, 'name', None)
    if kind == 'step':
        goal, by, bindings, uses = term.args
        fact(step_of(goal, by, uses))
    elif kind != 'clause':
        fact(decision(term))
```

Every step of the policy's proof becomes a fact `step_of(Goal, How, Uses)`,
and every decision a fact `decision(D)`. The check report needs no work at
all: it already *is* a list of facts.

---

## The audit rules

```python
implies(step_of(G, By, Uses) & member(U, Uses), depends(G, U))
implies(depends(G, U) & depends(U, W), depends(G, W))

implies(decision(D) & depends(D, F) & step_of(F, clause(_), []), rests_on(D, F))
implies(decision(D) & depends(D, A) & step_of(A, 'absent', []), assumes(D, A))
implies(rests_on(D, F) & evidence_of(F, 'self_declared'), at_risk(D, F))
```

A decision depends on everything its proof used, all the way down. The data
it rests on are the policy's facts in that support; its assumptions are the
"nobody has had a grant yet" checks the proof could only take on trust.

---

## What peye concludes

```python
verdict('checked_with_obligations')
at_risk(grant('cara'), income('cara', 1800))
at_risk(grant('dan'), income('dan', 2400))
at_risk(top_up('dan'), income('dan', 2400))
explanation(refused('bob', 'income above 2500'), [applicant('bob'), income('bob', 2900)], [])
explanation(grant('ann'), [applicant('ann'), income('ann', 2100)], [~already_received('ann')])
explanation(top_up('dan'), [household('dan', 3), applicant('dan'), income('dan', 2400)], [~already_received('dan')])
```

(Three more explanations, for Cara, Dan and Ann, follow the same pattern.)

The policy's own proof was **checked**, on the condition of three
"no earlier grant" assumptions. Three decisions are **at risk**, because they
rest on incomes only the applicants themselves declared. And each decision
comes with exactly the data it rests on and what it assumed: Dan's top-up
rests on his household size, his application and his income, and assumes
he had no earlier grant.

---

## Checked, not just claimed

The audit is a peye program too, so its own conclusions come with a proof.
The checker verified 35 of its 47 steps against the program; the other 12
are the lists `findall` collected, listed as obligations. Verdict:
**checked with obligations**.

So the auditor gets an answer about the reasoning that is itself reasoned,
and checked.

---

## Try it

```sh
python -m peye examples/audited-grants.py            # the audit
python -m peye --proof examples/audited-grants.py    # the audit, with its own proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=audited-grants).
Change Cara's evidence to `'payslip'` and run again: her grant is no longer
at risk. Lower the threshold in the grant rule to `I < 2000` and watch the
explanations, and the risks, change with it.

---

## Takeaway

When rules, data, conclusions, proofs and reports share one language, a
program can audit its own decisions with the same tools it used to make
them, and every answer it gives about its reasoning can be checked too.
