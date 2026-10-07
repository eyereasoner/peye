# A right to the value of personal data

*How such a right fits existing EU law, and how it could become a right of its own.*

[data-value-right.py](https://github.com/eyereasoner/peye/blob/main/examples/data-value-right.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/data-value-right.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/data-value-right.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/data-value-right.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=data-value-right)

---

## The question

AI systems are trained on, and earn money with, personal data. Do the people
the data is about have a **right to the value** it creates?

A researcher studying this combines two methods:

- **Legal analysis:** how would such a right fit within existing law?
- **Policy evaluation:** how could it be developed into an *autonomous* right
  of data subjects?

This example writes that research design down as a program, so that every
step from the law to the recommendation can be followed and checked.

*It is a model of a research design, with provisions summarized for
illustration, not legal advice.*

---

## Breaking the right down

The program starts from a working hypothesis: a right to the value of
personal data has seven components.

| Component | What it means |
| --- | --- |
| `value_transparency` | knowing that and how one's data creates value, including in AI training |
| `use_control` | deciding on the uses through which one's data creates value |
| `value_mobility` | taking one's data elsewhere, to have value created there |
| `value_recognition` | the law acknowledging that personal data has economic value |
| `collective_exercise` | exercising the right together, through an intermediary |
| `individual_enforcement` | enforcing the right oneself, before a court |
| `value_share` | receiving a share of the value one's data creates |

---

## What existing law already offers

Each provision is recorded with the component it anchors, how far, and why:

```python
('GDPR art. 13-15', 'value_transparency', 'partial',
 'information on purposes and recipients, not on the value created'),
('AI Act art. 53(1)(d)', 'value_transparency', 'partial',
 'a public summary of the content used to train general-purpose AI models, not per data subject'),
('Directive 2019/770 art. 3(1)', 'value_recognition', 'full',
 'personal data recognized as what a consumer may provide in exchange for digital content'),
('GDPR art. 79 and 82', 'individual_enforcement', 'full',
 'a judicial remedy and compensation for the data subject'),
```

There are nine such provisions in all, from the GDPR, the AI Act, the Digital
Markets Act, the Data Governance Act and the directive on digital content.

---

## The legal analysis, as rules

```python
forward(anchored(C), anchor(P, C, D, W))
forward(fully_anchored(C), anchor(P, C, 'full', W))
forward(gap(C), component(C, Description), ~anchored(C))

forward(fit(C, 'in existing law'), fully_anchored(C))
forward(fit(C, 'by interpretation'), anchored(C), ~fully_anchored(C))
forward(fit(C, 'needs an autonomous right'), gap(C))
```

A component anchored fully is already in the law. One anchored only in part
can be developed by interpreting the law. One that no provision anchors at
all is a **gap**: it needs new law.

---

## The policy evaluation, as rules

Five ways of developing the right are weighed against what the analysis
found:

```python
forward(needs_development(C), component(C, Meaning), ~fully_anchored(C))
forward(objection(O, unaddressed(C)), option(O, F), needs_development(C), ~delivers(O, C))
forward(objection(O, 'treats personal data as a commodity'), option(O, F), commodifies(F))
forward(objection(O, 'gives the data subject no claim of their own'), option(O, F), ~own_claim(F))
forward(recommended(O), option(O, F), ~objectionable(O))
```

An option is objected to when it leaves a component that needs developing
undelivered, when it treats personal data as a commodity (in tension with
data protection as a fundamental right, Charter art. 8), or when it gives the
data subject no claim of their own. One option, interpreting existing law,
is not stated at all: it follows from the analysis, because interpretation
can only strengthen what the law already anchors.

---

## What peye concludes

```python
analysis('value_share', "receiving a share of the value one's data creates", 'needs an autonomous right', [])
evaluation('interpret_existing_law', [...], [unaddressed('value_share')])
evaluation('extend_portability', [...], [unaddressed('use_control'), unaddressed('collective_exercise'), unaddressed('value_share')])
evaluation('data_dividend', [...], [unaddressed('value_transparency'), unaddressed('use_control'), unaddressed('value_mobility'), 'gives the data subject no claim of their own'])
evaluation('data_ownership', [...], ['treats personal data as a commodity', unaddressed('value_transparency'), unaddressed('collective_exercise')])
evaluation('autonomous_right', [...], [])
recommended('autonomous_right')
```

Two components are already in the law, four can be developed by
interpretation, and one, **a share of the value**, has no basis at all. Of
the five options only an **autonomous right** delivers every component that
needs developing, without treating data as a commodity and with a claim for
the data subject.

---

## Why: the proof in plain words

1. No provision anchors a share of the value, so it is a gap — *rule 43*,
   relying on the absence `~anchored('value_share')`.
2. A gap needs an autonomous right — *rule 46*.
3. The autonomous right meets no objection — `~objectionable('autonomous_right')`.
4. So it is recommended — *rule 55*.

Every other option fails for a reason the proof names: a component it leaves
undone, a commodity framing, or a missing claim.

---

## Checked, not just claimed

A separate checker re-establishes the proof against the program: 45 of its 68
steps are verified directly. The other 23 rest on what the program could
only find *absent* ("no provision anchors this", "no objection applies") or
*collect* ("these are all the provisions"), and the report lists each of
them as an obligation. Verdict: **checked with obligations**.

And `peye --unused` lists nothing: every provision, component and rule makes
a difference to the conclusions. Nothing in the model is decoration.

---

## Try it

```sh
python -m peye examples/data-value-right.py            # the analysis and the evaluation
python -m peye --proof examples/data-value-right.py    # with the proof
python -m peye --unused examples/data-value-right.py   # nothing is decoration
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=data-value-right).
Add a provision that anchors `value_share`, even only in part, and run
again: the gap closes, and interpreting existing law is recommended next to
an autonomous right. Change `data_ownership`'s framing from `'property'` to
`'inalienable_right'` and see which objection disappears.

---

## Takeaway

Legal analysis and policy evaluation become one chain of reasoning, from
each provision to the recommendation. Change an assumption, a provision or a
criterion, and the whole chain follows, with a proof of every step.
