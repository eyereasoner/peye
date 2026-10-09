# Deep taxonomy (100 levels)

*A hundred-step chain of "every A is a B", with dead ends at every turn.*

[deep-taxonomy-100.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-100.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/deep-taxonomy-100.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/deep-taxonomy-100.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/deep-taxonomy-100.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-100)

---

## The question

A **taxonomy** is a classification: a dog is a mammal, a mammal is an
animal, and so on.

Imagine one that is a hundred levels deep. One individual, `ind`, sits at
the top level `n0`. **Is `ind` also of type `n100`, a hundred levels down?**

The catch: at every level the path splits three ways, and only one way
leads further.

---

## What we tell peye

One fact and 300 rules, three per level, which a loop states:

```python
fact(type('ind', 'n0'))
for level in range(1, 101):
    implied_by(type(X, f'n{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'i{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'j{level}'), type(X, f'n{level - 1}'))
query(type(X, 'n100'))
```

Anything of type `n0` is also `n1`, `i1` and `j1`. But only `n1` leads on;
`i1` and `j1` are dead ends. The last line asks the question.

---

## What peye concludes

```python
type('ind', 'n100')
```

Yes: `ind` is of type `n100`.

This is a well-known **benchmark** (a standard test of speed), from the
WellnessRules work cited in the file. It checks that a reasoner can follow a
long chain without getting lost in the side branches.

---

## Why: the proof in plain words

The proof is one long chain, read from the answer back to the fact:

1. `ind` is `n100` — *rule 299*, because `ind` is `n99`;
2. `ind` is `n99` — *rule 296*, because `ind` is `n98`;
3. … and so on, one level at a time …
4. `ind` is `n1` — *rule 2*, because `ind` is `n0`;
5. `ind` is `n0` — *fact 1*.

That is 101 steps: one per level, plus the starting fact. None of the dead
ends appear; the proof contains only what the answer needs.

---

## Checked, not just claimed

The checker walks all 101 steps against the program:

- each step is an exact instance of the rule it cites;
- the chain bottoms out in the fact, with no circular reasoning;
- every step serves the answer, and nothing is extra.

Verdict: **checked**. 101 steps, all verified, nothing taken on trust.

---

## One of a family

The same benchmark comes in five sizes:

| Example | Levels | Proof steps |
| --- | --- | --- |
| deep-taxonomy-10 | 10 | 11 |
| deep-taxonomy-100 | 100 | 101 |
| deep-taxonomy-1000 | 1,000 | 1,001 |
| deep-taxonomy-10000 | 10,000 | 10,001 |
| deep-taxonomy-100000 | 100,000 | 100,001 |

The cost grows in a straight line with the depth: each level costs exactly
one step. `--stats` reports 101 inferences for this one.

---

## Try it

```sh
python -m peye examples/deep-taxonomy-100.py
python -m peye --stats examples/deep-taxonomy-100.py
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=deep-taxonomy-100).
Change the last line to `query(type(X, 'n50'))`: the answer becomes
`type('ind', 'n50')`, and `--stats` drops to 51 inferences.

---

## Takeaway

A long chain of simple reasons is still simple to check. However deep the
taxonomy, the proof is exactly as long as the path, and every link in it can
be verified.
