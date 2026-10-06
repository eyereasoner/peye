# Graphs

*Who is a child of whom, who is allowed, and how a "no" is handled honestly.*

[graphs.py](https://github.com/eyereasoner/peye/blob/main/examples/graphs.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/graphs.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/graphs.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/graphs.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=graphs)

---

## The question

We have a small family record: Alice is the parent of Bob and of Carol, and
Bob is blocked (say, from some service).

- **Who is a child of Alice?**
- **Which of Alice's children are allowed** — that is, not blocked?
- **What is the full list of Alice's children?**

The last two need something new: saying "not" and saying "all".

---

## What we tell peye

The data is written as *triples*: subject, relation, object.

```python
fact(base('alice', 'parent_of', 'bob'))
fact(base('alice', 'parent_of', 'carol'))
fact(base('bob', 'blocked', 'true'))
backward(t(S, P, O), base(S, P, O))
forward(t(C, 'child_of', P), t(P, 'parent_of', C))
forward(allowed(C), t(C, 'child_of', 'alice'), ~t(C, 'blocked', 'true'))
forward(children(P, Children), base(P, 'parent_of', _), findall(C, t(C, 'child_of', P), Children))
```

`base` is the original data, left untouched; `t` is a combined view of the
data plus what follows from it. `~` means *not*. `findall` gathers *all*
answers into a list.

---

## What peye concludes

```python
t('bob', 'child_of', 'alice')
t('carol', 'child_of', 'alice')
allowed('carol')
children('alice', ['bob', 'carol'])
```

Bob and Carol are Alice's children. Only Carol is allowed, because Bob is
blocked. And the list of Alice's children is `['bob', 'carol']`.

---

## Why: the proof in plain words

1. Alice is the parent of Carol — *a fact we gave (fact 2)*, seen through
   the view `t` — *rule 4*.
2. So Carol is a child of Alice — *rule 5* (the same for Bob, from fact 1).
3. Carol is not blocked — *searched, nothing found* (`absent`).
4. So Carol is allowed — *rule 6*.
5. All children of Alice are Bob and Carol — *collected with `findall`*.
6. So Alice's children are `['bob', 'carol']` — *rule 7*.

---

## Two kinds of honest "trust me"

Steps 3 and 5 are different from the others:

- **"Carol is not blocked"** is concluded because peye searched
  everything it knows and found nothing. That is an *absence*, and a proof
  cannot point at an absence the way it points at a fact.
- **"The children are exactly Bob and Carol"** says the list is
  *complete*. Each name can be proven; that no one is missing cannot.

peye does not hide this. Each one is recorded as an **obligation**: a
step taken on trust, named in the report.

---

## Checked, not just claimed

A separate checker read all 10 steps against the program:

- 8 steps are verified as exact instances of the lines they cite;
- 2 steps are trusted and listed as obligations: one `absent` (Carol is not
  blocked) and one `collected` (the list `['bob', 'carol']` is complete);
- it also tested both of them against the evidence in the proof, and
  neither is contradicted: no fact or step says Carol is blocked, and no
  child of Alice in the proof is missing from the list.

Verdict: **checked_with_obligations**.

---

## Try it

```sh
python -m peye examples/graphs.py            # the answers
python -m peye --proof examples/graphs.py    # with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=graphs).
Change `fact(base('bob', 'blocked', 'true'))` to
`fact(base('carol', 'blocked', 'true'))` and run again: now `allowed('bob')`
appears instead of `allowed('carol')`.

---

## Takeaway

"Not" and "all" are claims about what is *missing*, and a proof cannot
display a missing thing. peye still uses them — and tells you exactly
which conclusions rest on them, so you know what you are trusting.
