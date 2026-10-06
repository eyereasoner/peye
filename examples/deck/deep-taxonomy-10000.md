# Deep Taxonomy 10000

*Ten thousand steps of reasoning, every one written down and checked.*

[deep-taxonomy-10000.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-10000.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/deep-taxonomy-10000.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/deep-taxonomy-10000.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/deep-taxonomy-10000.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-10000)

---

## The question

A *taxonomy* is a tree of categories: a robin is a bird, a bird is an
animal, and so on. Here the tree is ten thousand levels deep, and at every
level it also splits into two side branches that go nowhere.

We know one thing: an individual, `'ind'`, is in the top category `'n0'`.

**Is `'ind'` in category `'n10000'`, at the very bottom?** And can the computer
show all ten thousand steps — and have them checked?

---

## A benchmark, at four sizes

This is the *deep-taxonomy benchmark*, a standard stress test for reasoners.
The collection has it at four depths, and this is the largest:

| Example | Levels | Proof steps |
| --- | --- | --- |
| deep-taxonomy-10 | 10 | 11 |
| deep-taxonomy-100 | 100 | 101 |
| deep-taxonomy-1000 | 1000 | 1001 |
| **deep-taxonomy-10000** | **10000** | **10001** |

Same shape each time; only the length of the chain changes.

---

## What we tell peye

One fact, then three rules per level — 30,000 rules in all:

```python
fact(type('ind', 'n0'))
backward(type(X, 'n1'), type(X, 'n0'))
backward(type(X, 'i1'), type(X, 'n0'))
backward(type(X, 'j1'), type(X, 'n0'))
backward(type(X, 'n2'), type(X, 'n1'))
# … and so on, down to
backward(type(X, 'n10000'), type(X, 'n9999'))
backward(type(X, 'i10000'), type(X, 'n9999'))
backward(type(X, 'j10000'), type(X, 'n9999'))
query(type(X, 'n10000'))
```

Read `backward(type(X, 'n2'), type(X, 'n1'))` as *anything in n1 is also in
n2*. The `i` and `j` rules are the dead-end side branches. The last line asks
the question.

---

## What peye concludes

```python
type('ind', 'n10000')
```

One answer: yes.

peye works backward from the question (`backward` rules are explored only
when a question needs them): to be in `n10000`, be in `n9999`; to be in
`n9999`, be in `n9998`; … all the way up to the fact we gave. The search is an
explicit machine inside peye, so ten thousand levels deep is no problem.

---

## Why: the proof in plain words

The proof is a chain of 10,001 steps:

1. `'ind'` is in `'n0'` — *a fact we gave (fact 1)*.
2. So `'ind'` is in `'n1'` — *rule 2*.
3. So `'ind'` is in `'n2'` — *rule 5*.
4. … one step per level …
5. So `'ind'` is in `'n10000'` — *rule 29999*.

Each step names the exact program line it used. The 20,000 side-branch
rules never appear: they do not help answer the question.

---

## Checked, not just claimed

A separate checker read all 10,001 steps against the program and confirmed
that:

- each step is an exact instance of the rule it cites (10,001 of 10,001);
- the chain never loops back on itself — no circular reasoning;
- every step serves the answer, and nothing extra is included.

Verdict: **checked**. All 10,001 steps verified, and nothing taken on trust.

The source is about 1.3 MB and its proof about 1.4 MB: a proof records every
step it claims.

---

## Try it

```sh
python -m peye examples/deep-taxonomy-10000.py            # the answer
python -m peye --stats examples/deep-taxonomy-10000.py    # and its cost
```

`--stats` reports `"inferences": 10001` — one step per level, plus the fact.
Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-10000).

Change the last line to `query(type(X, 'j5000'))` and run with `--stats`
again: the answer is `type('ind', 'j5000')`, a side branch halfway down,
reached in 5001 steps.

---

## Takeaway

Going from ten levels to ten thousand changes the cost, not the kind of
answer. Time, proof size and checking all grow in step with the depth, so a
ten-thousand-step argument is just as followable — and just as checkable —
as a ten-step one.
