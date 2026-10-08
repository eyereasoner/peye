# Deep Taxonomy (10 levels)

*Ten levels down a family tree of categories, ignoring every dead end on the way.*

[deep-taxonomy-10.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-10.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/deep-taxonomy-10.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/deep-taxonomy-10.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/deep-taxonomy-10.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-10)

---

## The question

A **taxonomy** is a tree of categories: a poodle is a dog, a dog is a mammal,
a mammal is an animal. Knowing something's lowest category tells you all the
higher ones.

Here we have one individual, `ind`, in category `n0`, and a chain of ten
levels above it. At every level the chain also branches into two side
categories that lead nowhere.

**Does `ind` belong to `n10`, the top of the chain?**

---

## What we tell peye

One fact, and three rules per level:

```python
fact(type('ind', 'n0'))
implied_by(type(X, 'n1'), type(X, 'n0'))
implied_by(type(X, 'i1'), type(X, 'n0'))
implied_by(type(X, 'j1'), type(X, 'n0'))
implied_by(type(X, 'n2'), type(X, 'n1'))
# … the same pattern for levels 3 to 9 …
implied_by(type(X, 'n10'), type(X, 'n9'))
implied_by(type(X, 'i10'), type(X, 'n9'))
implied_by(type(X, 'j10'), type(X, 'n9'))
query(type(X, 'n10'))
```

The `n` rules are the real chain; `i` and `j` are the side branches. The last
line is the question: "which X are of type `n10`?"

---

## What peye concludes

```python
type('ind', 'n10')
```

Yes: `ind` is an `n10`. The side categories are never needed, so they never
appear in the answer.

---

## Why: the proof in plain words

The proof is a straight ladder of 11 steps, read from the top down:

1. `ind` is `n10`, because it is `n9` — *the `n10` rule, with X = ind*.
2. `ind` is `n9`, because it is `n8` — *the `n9` rule*.
3. … and so on, one level at a time …
4. `ind` is `n0` — *the fact we gave*.

Ten rule steps plus one fact. None of the 20 side-branch rules shows up,
because none of them helps answer the question.

---

## Checked, not just claimed

The checker read all 11 steps against the program and confirmed that:

- each step is an exact instance of the line it cites;
- the ladder ends in a real fact, with no circular reasoning;
- the proof answers the question and contains nothing extra.

Verdict: **checked**. All 11 steps verified, nothing taken on trust.

---

## One of four sizes

This is the smallest of a well-known benchmark, the deep taxonomy, that
peye ships at four sizes:

- `deep-taxonomy-10` (this one), `-100`, `-1000` and `-10000` levels.

Each costs exactly one step per level, plus one for the fact. The
ten-thousand-level version verifies 10001 steps. Time, proof size and
checking all grow in proportion to the depth, so a longer chain costs
more, but never disproportionately more.

---

## Try it

```sh
python -m peye examples/deep-taxonomy-10.py
python -m peye --stats examples/deep-taxonomy-10.py
```

`--stats` reports 11 inferences, one per step of the ladder.
In the [playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-10),
change the last line to `query(type(X, 'j7'))` and the answer becomes
`type('ind', 'j7')`: a side branch, reached by climbing six levels first.

---

## Takeaway

A long chain of reasoning stays easy to trust when every link is written
down and checked, and the dead ends stay out of the explanation.
