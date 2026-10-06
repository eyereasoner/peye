# Flat Map

*Gather every matching value from a list of things — and be honest about what "every" means.*

[flat-map.py](https://github.com/eyereasoner/peye/blob/main/examples/flat-map.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/flat-map.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/flat-map.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/flat-map.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=flat-map)

---

## The question

Imagine a small table of facts, each saying *subject — property — value*:
a book has an author, a person has a phone number. Some subjects have one
value, some have several, some have none.

Now: **for a list of subjects, collect all their values for one property
into a single flat list.** Programmers call this a *flat map*.

What happens with a subject that has two values? One that has none? A
property nobody uses?

---

## What we tell peye

Four facts, and a rule that walks the list:

```python
fact(t('s1', 'p1', 'o1'))
fact(t('s2', 'p1', 'o2'))
fact(t('s3', 'p1', 'o3'))
fact(t('s3', 'p1', 'o4'))
# … two lines defining append
fact(flat_map([], _, []))
backward(
    flat_map([S, *Subjects], P, Objects),
    findall(O, t(S, P, O), Here),
    flat_map(Subjects, P, Rest),
    append(Here, Rest, Objects),
)

query(flat_map(['s1', 's2', 's3'], 'p1', Objects))
query(flat_map(['missing'], 'p1', Objects))
query(flat_map(['s1'], 'p2', Objects))
```

`findall` gathers *all* values of one subject into a list, `Here`;
`append` joins two lists end to end.

---

## What peye concludes

```python
flat_map(['s1', 's2', 's3'], 'p1', ['o1', 'o2', 'o3', 'o4'])
flat_map(['missing'], 'p1', [])
flat_map(['s1'], 'p2', [])
```

- `s3` contributes two values, `o3` and `o4`, in order.
- A subject with no facts gives an empty list `[]`, not an error.
- A property nobody uses gives `[]` too.

---

## Why: the proof in plain words

For the first answer, the proof records:

1. All `p1` values of `s1`: `['o1']` — *collected by searching*.
2. All `p1` values of `s2`: `['o2']` — *collected*.
3. All `p1` values of `s3`: `['o3', 'o4']` — *collected*.
4. An empty subject list gives `[]` — *fact 7*.
5. Joining `['o3', 'o4']`, then `['o2']`, then `['o1']` in front — *rules 5 and 6*.
6. So the flat map is `['o1', 'o2', 'o3', 'o4']` — *rule 8*.

---

## Checked, with obligations

The checker matched **14** steps to their program lines. Verdict:
**checked_with_obligations**.

The 5 obligations are all of the kind called `collected`: each claims a
list is the *complete* set of answers — for example, that `s3` has exactly
`['o3', 'o4']` and `missing` has nothing at all. A proof can show each value
is there; "and there are no others" comes from peye having searched
everything it knows. The checker records that as an obligation instead of
pretending to prove it.

It did confirm that nothing in the program or the proof contradicts any of
the 5 lists.

---

## When "all" is a promise

An obligation is not a flaw; it is a label on the one kind of claim that
depends on *nothing else being known*. If someone later adds a fact, the
lists could change — and the report tells you exactly which lists those are.

If you need proof with no such promises, `--strict-proof` rejects any
certificate that leans on one. This one would fail that stricter test,
on exactly these 5 lists.

---

## Try it

```sh
python -m peye examples/flat-map.py
python -m peye --goal "flat_map(['s3', 's1'], 'p1', Objects)" examples/flat-map.py
```

The second gives `['o3', 'o4', 'o1']`: the order follows the subject list.
Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=flat-map).

Add the fact `fact(t('s2', 'p1', 'o5'))` and run again: the first answer
becomes `['o1', 'o2', 'o5', 'o3', 'o4']`.

---

## Takeaway

"Here are all the matches" is a stronger statement than "here are some
matches". peye gives you the answer and marks precisely where it relied on
having seen everything — so you know what to recheck when the data grows.
