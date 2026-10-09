# Deep Taxonomy 100000

*A hundred thousand steps of reasoning, every one written down and checked.*

[deep-taxonomy-100000.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-100000.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/deep-taxonomy-100000.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/deep-taxonomy-100000.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/deep-taxonomy-100000.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-100000)

---

## The question

A *taxonomy* is a tree of categories: a robin is a bird, a bird is an
animal, and so on. Here the tree is a hundred thousand levels deep, and at
every level it also splits into two side branches that go nowhere.

We know one thing: an individual, `'ind'`, is in the top category `'n0'`.

**Is `'ind'` in category `'n100000'`, at the very bottom?** And can the
computer show all hundred thousand steps — and have them checked?

---

## A benchmark, at five sizes

This is the *deep-taxonomy benchmark*, a standard stress test for reasoners.
The collection has it at five depths, and this is the largest:

| Example | Levels | Proof steps |
| --- | --- | --- |
| deep-taxonomy-10 | 10 | 11 |
| deep-taxonomy-100 | 100 | 101 |
| deep-taxonomy-1000 | 1000 | 1001 |
| deep-taxonomy-10000 | 10000 | 10001 |
| **deep-taxonomy-100000** | **100000** | **100001** |

Same shape each time; only the length of the chain changes.

---

## What we tell peye

One fact, then three rules per level — 300,000 rules in all. Listed one by
one they would make a 14 MB program, so a loop states them:

```python
fact(type('ind', 'n0'))
for level in range(1, 100001):
    implied_by(type(X, f'n{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'i{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'j{level}'), type(X, f'n{level - 1}'))
query(type(X, 'n100000'))
```

The program is Python, so it can compute its own rules: the loop states
exactly the same clauses the long version would, in the same order. Read
`implied_by(type(X, 'n2'), type(X, 'n1'))` as *anything in n1 is also in n2*.
The `i` and `j` rules are the dead-end side branches.

---

## What peye concludes

```python
type('ind', 'n100000')
```

One answer: yes.

peye works backward from the question: to be in `n100000`, be in `n99999`;
… all the way up to the fact we gave. The search is an explicit machine
inside peye, so a hundred thousand levels deep is no problem.

---

## Why: the proof in plain words

The proof is a chain of 100,001 steps:

1. `'ind'` is in `'n0'` — *a fact we gave (fact 1)*.
2. So `'ind'` is in `'n1'` — *rule 2*.
3. So `'ind'` is in `'n2'` — *rule 5*.
4. … one step per level …
5. So `'ind'` is in `'n100000'` — *rule 299999*.

Each step names the exact rule it used. Every rule the loop states records
the line of the loop, so the proof can still say where each rule came from.
The 200,000 side-branch rules never appear: they do not help answer the
question.

---

## Checked, not just claimed

A separate checker read all 100,001 steps against the program and confirmed
that each is an exact instance of the rule it cites, that the chain never
loops back on itself, and that every step serves the answer.

Verdict: **checked**. All 100,001 steps verified, and nothing taken on trust.

The program is a few lines; its proof is about 14.7 MB, because a proof
records every step it claims.

---

## Try it

```sh
python -m peye examples/deep-taxonomy-100000.py            # the answer
python -m peye --stats examples/deep-taxonomy-100000.py    # and its cost
```

`--stats` reports `"inferences": 100001` — one step per level, plus the fact.
Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-100000).

Change the last line to `query(type(X, 'j50000'))` and run with `--stats`
again: the answer is `type('ind', 'j50000')`, a side branch halfway down,
reached in 50001 steps.

---

## Takeaway

From ten levels to a hundred thousand, only the cost grows, in step with the
depth, and the answer stays just as followable and just as checkable. And
because the program is Python, a rule set this large can be stated in a
few lines.
