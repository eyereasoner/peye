# Variable Predicates

*One rule that renames many fields at once, driven by a small mapping table.*

[variable-predicates.py](https://github.com/eyereasoner/peye/blob/main/examples/variable-predicates.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/variable-predicates.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/variable-predicates.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/variable-predicates.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=variable-predicates)

---

## The question

Data often arrives with someone else's field names. A source system calls
them `source_name` and `source_age`; we want `name` and `age`.

**Can we translate the field names with a lookup table, instead of writing
one rule per field?** And can we see where each translated value came from?

---

## Facts as triples

Here every fact is a *triple*: a subject, a relation, and a value.

```python
fact(t('alice', 'source_name', 'Alice'))
```

reads *alice has source_name 'Alice'*.

The trick is that the relation in the middle is just data — so a rule can
use a variable there and treat the relation name like any other value.

---

## What we tell peye

```python
fact(t('alice', 'source_name', 'Alice'))
fact(t('alice', 'source_age', 30))
fact(maps('source_name', 'name'))
fact(maps('source_age', 'age'))
implies(t(S, Source, O) & maps(Source, Target), t(S, Target, O))
query(t('alice', 'name', Name))
query(t('alice', 'age', Age))
```

The rule reads: *if S has value O under the Source name, and Source maps to
Target, then S has value O under the Target name.* One rule covers every
row of the mapping table.

---

## What peye concludes

```python
t('alice', 'name', 'Alice')
t('alice', 'age', 30)
```

Alice's name and age, now under the field names we wanted. The original
facts are left as they were.

---

## Why: the proof in plain words

For the name:

1. alice has source_name 'Alice' — *a fact we gave (fact 1)*.
2. source_name maps to name — *a fact we gave (fact 3)*.
3. So alice has name 'Alice' — *rule 5, with Source = 'source_name' and
   Target = 'name'*.

The age is the same rule again, with facts 2 and 4. The proof shows which
mapping row produced each value.

---

## Checked, not just claimed

A separate checker read all 6 steps of the proof against the program and
confirmed that:

- every step is an exact instance of the line it cites (6 of 6);
- nothing is assumed beyond the four facts and the one rule;
- every step serves one of the 2 answers.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/variable-predicates.py            # the answers
python -m peye --proof examples/variable-predicates.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=variable-predicates).
Add a new field and a mapping row — `fact(t('alice', 'source_city', 'Gent'))`
and `fact(maps('source_city', 'city'))` — plus the question
`query(t('alice', 'city', _))`. The same rule answers
`t('alice', 'city', 'Gent')`.

---

## Takeaway

When relation names are data, one general rule plus a table can replace a
pile of special cases — and the proof still tells you exactly which table
row was used.
