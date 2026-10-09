# Existential rules

*Saying that something exists, without knowing what it is, and without mixing it up with anything else.*

[existential-rules.py](https://github.com/eyereasoner/peye/blob/main/examples/existential-rules.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/existential-rules.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/existential-rules.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/existential-rules.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=existential-rules)

---

## The question

Some rules conclude that something exists without saying what it is:

- every person has a parent, even when nobody knows who;
- every customer who ordered something has an invoice, not yet numbered;
- two colleagues meet, at some meeting.

**How can a reasoner keep track of such unknowns** without confusing one
with another, or with anything it already knows?

---

## What we tell peye

A variable that appears in a rule's conclusion but not in its body is such an
unknown, an *existential*:

```python
implies(person(X), has_parent(X, P))          # P: some parent of X
implies(ordered(C, Item), invoice_for(C, I))  # I: some invoice for C
implies(colleagues(X, Y), meeting(M) & attends(M, X) & attends(M, Y))
```

Around them: Ann and Bob are persons, Dan and Fay have a parent the data
names (Eve), Carl ordered a lamp and a desk, Dora a chair, and Ann and Dora
are colleagues.

---

## What peye concludes

```python
has_parent('ann', skolem(3, 'P', ['ann']))
has_parent('bob', skolem(3, 'P', ['bob']))
sibling('dan', 'fay')
sibling('fay', 'dan')
invoice_for('carl', skolem(10, 'I', ['carl']))
invoice_for('dora', skolem(10, 'I', ['dora']))
sent(skolem(10, 'I', ['carl']))
sent(skolem(10, 'I', ['dora']))
meeting(skolem(13, 'M', ['ann', 'dora']))
attends(skolem(13, 'M', ['ann', 'dora']), 'ann')
attends(skolem(13, 'M', ['ann', 'dora']), 'dora')
```

Each unknown became a **Skolem term**, a name for "the one that exists
here": `skolem(3, 'P', ['ann'])` reads *the `P` of rule 3, for Ann*. It is a
function of what the rule knew when it concluded: the rule, the unknown, and
the values of the conclusion's other variables.

---

## One witness per activation

- **Ann and Bob each get a parent of their own**, the `P` of rule 3 for Ann
  and for Bob. Had they shared one, the sibling rule would have made them
  siblings by accident. Only Dan and Fay, whose parent the data names, are
  siblings.
- **Carl ordered twice, and gets one invoice.** The invoice depends on Carl
  alone, not on what he ordered, so both orders give the same term.
- **The meeting is one meeting.** The three conclusions of one activation
  share their witness, the `M` of rule 13 for Ann and Dora.
- **Invented values are values.** The `sent` rule uses the invoices like any
  other value. Whenever a rule meets the same activation again, it gives back
  the same term, so reasoning comes to an end.

---

## Never a clash

A Skolem term names the rule and the unknown it stands for, and the values it
depends on, so it cannot be mistaken for anything else:

- not for a name in your data, which says nothing of rule 3's `P`;
- not for another unknown, which belongs to another rule, another variable or
  other values.

And it is the same in every run: run the program twice, or read one run's
output into another, and the same unknown has the same name.

---

## Why: the proof in plain words

For Bob's parent:

1. Bob is a person — *clause 2, a fact*.
2. So Bob has a parent, `skolem(3, 'P', ['bob'])` — *clause 3, with X = bob
   and P that term*.

For Carl's invoice: Carl ordered a lamp (*clause 7*), so he has the invoice
`skolem(10, 'I', ['carl'])` (*clause 10*). The desk is not needed: it would only give the same
conclusion again, and `peye --unused` says so.

---

## Checked, not just claimed

The checker confirms every step against the program: 18 steps are instances
of the clauses they cite, and the two `not_identical` tests are recomputed.
Nothing is taken on trust. Verdict: **checked**.

The witnesses need no special treatment in the proof: they are ordinary
values that the rule's variables were bound to.

---

## Try it

```sh
python -m peye examples/existential-rules.py            # the conclusions
python -m peye --proof examples/existential-rules.py    # with the proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=existential-rules).
Add `fact(person('dan'))` and run again: Dan gets a parent witness of his own
as well, beside Eve, because the rule says only that some parent exists.

---

## Takeaway

An existential rule says that something exists. peye names each such
something by a Skolem function of what the rule knew: the same activation
always gives the same name, and the name can never be mistaken for anything
else.
