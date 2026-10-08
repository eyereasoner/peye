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
has_parent('ann', '…/genid/examples#sk_0')
has_parent('bob', '…/genid/examples#sk_1')
sibling('dan', 'fay')
sibling('fay', 'dan')
invoice_for('carl', '…/genid/examples#sk_2')
invoice_for('dora', '…/genid/examples#sk_3')
sent('…/genid/examples#sk_2')
sent('…/genid/examples#sk_3')
meeting('…/genid/examples#sk_4')
attends('…/genid/examples#sk_4', 'ann')
attends('…/genid/examples#sk_4', 'dora')
```

Each unknown became a **Skolem atom**, here shortened: a name that stands for
"the one that exists here". The full name starts with
`https://eyereasoner.github.io/.well-known/genid/`.

---

## One witness per activation

- **Ann and Bob each get a parent of their own**, `sk_0` and `sk_1`. Had they
  shared one, the sibling rule would have made them siblings by accident.
  Only Dan and Fay, whose parent the data names, are siblings.
- **Carl ordered twice, and gets one invoice.** Both orders lead to the same
  conclusion, an invoice for Carl, so one witness serves both.
- **The meeting is one meeting.** The three conclusions of one activation
  share their witness `sk_4`.
- **Invented values are values.** The `sent` rule uses the invoices like any
  other value. Whenever a rule meets the same activation again, it gives back
  the same witness, so reasoning comes to an end.

---

## Never a clash

The witnesses live in a namespace of their own, with a **genid** that is a
random identifier for each run, as EYE does. So a witness never clashes:

- with a name in your data, even one that happens to be called `'sk_0'`;
- with the witnesses of another run, even when a program reads that run's
  output back in.

The saved files use the genid `examples`, so they can be reproduced:
`--skolem-genid examples` does the same on the command line.

---

## Why: the proof in plain words

For Bob's parent:

1. Bob is a person — *clause 2, a fact*.
2. So Bob has a parent, the witness `sk_1` — *clause 3, with X = bob and P =
   that witness*.

For Carl's invoice: Carl ordered a lamp (*clause 7*), so he has the invoice
`sk_2` (*clause 10*). The desk is not needed: it would only give the same
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
python -m peye examples/existential-rules.py                             # a fresh genid each run
python -m peye --skolem-genid examples examples/existential-rules.py     # the saved output
python -m peye --proof examples/existential-rules.py                     # with the proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=existential-rules).
Add `fact(person('dan'))` and run again: Dan gets a parent witness of his own
as well, beside Eve, because the rule says only that some parent exists.

---

## Takeaway

An existential rule says that something exists. peye gives each such
something a name of its own, keeps it when the same activation returns, and
makes sure it can never be mistaken for anything else.
