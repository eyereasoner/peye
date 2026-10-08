# Witnesses

*When a rule creates something new, give it a name that says where it came from.*

[witnesses.py](https://github.com/eyereasoner/peye/blob/main/examples/witnesses.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/witnesses.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/witnesses.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/witnesses.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=witnesses)

---

## The question

Suppose a rule says: *every person has a record*. For Alice and Bob, that
means two new records exist. But what are they called? And how do we keep
the record and its owner tied together?

A name for something a rule brings into existence is called a *witness*:
it stands as evidence that the thing exists.

**Can we make each witness say exactly which rule made it, and for whom —
and conclude two facts about it at once?**

---

## What we tell peye

Two people, and one rule with two conclusions:

```python
fact(person('alice'))
fact(person('bob'))
implies(
    person(Name),
    has_record(Name, record('person_rule', Name)) & record_owner(record('person_rule', Name), Name),
)
```

The witness is the term `record('person_rule', Name)`: a record labelled
with the rule's name and the person it was made for.

The head holds *two* conclusions joined with `&`. Both share that same
witness, so they always talk about the same record.

---

## What peye concludes

```python
has_record('alice', record('person_rule', 'alice'))
record_owner(record('person_rule', 'alice'), 'alice')
has_record('bob', record('person_rule', 'bob'))
record_owner(record('person_rule', 'bob'), 'bob')
```

Two facts per person. Alice's record is `record('person_rule', 'alice')` —
readable, stable from run to run, and impossible to mix up with Bob's.

---

## Why not let peye invent names?

peye can invent placeholder names for things a rule leaves unnamed. But an
explicit witness is better when you want one per rule and per binding:

- it says *which* rule made it and *for whom*;
- running the program again gives the same names, so results compare
  cleanly;
- firing the rule twice for Alice still gives one record, not two.

---

## Why: the proof in plain words

1. Alice is a person — *a fact we gave (fact 1)*.
2. So Alice has the record `record('person_rule', 'alice')` — *rule 3, with
   Name = 'alice'*.
3. And that record's owner is Alice — *rule 3 again, same binding*.

Bob's two facts follow the same way from fact 2. Both conclusions cite the
same rule and the same value for `Name`: that is how a shared multi-part
conclusion shows up in the proof.

---

## Checked, not just claimed

A separate checker read all 6 steps against the program and confirmed that:

- each step is an exact instance of the line it cites (6 of 6);
- no step depends on itself in a circle;
- every one of the 4 conclusions is justified, and nothing extra is
  included.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/witnesses.py            # the four facts
python -m peye --proof examples/witnesses.py    # with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=witnesses).

Add `fact(person('carol'))` and run again: two more facts appear, with the
witness `record('person_rule', 'carol')`.

---

## Takeaway

A good name carries its own history. By building the witness from the rule
and the binding, every new thing peye concludes can be traced to where it
came from — even before you look at the proof.
