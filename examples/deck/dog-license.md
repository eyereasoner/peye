# Dog license

*A rule that depends on counting, and an honest note about the count.*

[dog-license.py](https://github.com/eyereasoner/peye/blob/main/examples/dog-license.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/dog-license.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/dog-license.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/dog-license.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=dog-license)

---

## The question

Imagine a town rule: **anyone who owns more than four dogs needs a dog
license.**

Alice owns five dogs, Bob owns two. Who needs a license? To answer, we must
*count*, and counting means being sure we saw every dog.

---

## What we tell peye

Who owns which dog, and the rule:

```python
fact(owns('alice', 'dog1'))
# … dog2 to dog5 also belong to alice
fact(owns('bob', 'dog6'))
fact(owns('bob', 'dog7'))
fact(owner('alice'))
fact(owner('bob'))

forward(dog_count(Owner, N), owner(Owner), findall(Dog, owns(Owner, Dog), Dogs), length(Dogs, N))
forward(requires(Owner, 'dog_license'), dog_count(Owner, N), N > 4)
```

`findall` means "gather *all* the dogs this owner has into a list".
`length` (defined in the same file) counts the list.

---

## What peye concludes

```python
dog_count('alice', 5)
dog_count('bob', 2)
requires('alice', 'dog_license')
```

Alice has 5 dogs and needs a license. Bob has 2 and does not.

---

## Why: the proof in plain words

For Alice:

1. Alice is an owner — *a fact we gave*.
2. All of Alice's dogs, gathered: `['dog1', 'dog2', 'dog3', 'dog4', 'dog5']`.
3. That list has length 5 — counted one dog at a time, 0 + 1 = 1, …, 4 + 1 = 5.
4. 5 is more than 4, so Alice requires a dog license.

Bob's count of 2 is shown the same way; since 2 is not more than 4, no
license conclusion is drawn for him.

---

## Checked, not just claimed

The checker confirms 13 steps against the program and recomputes 6
calculations. But step 2 says "these are *all* of Alice's dogs". A proof can
show a dog is in the list; it cannot show that no dog is missing.

So the checker records it as an **obligation**: a claim taken on trust and
listed openly. There are two, one per owner (a *collected* obligation: the
list from `findall` is assumed complete). The checker did confirm that no dog
known to the program is missing from either list.

Verdict: **checked_with_obligations**. 21 steps, 2 taken on trust.

---

## Try it

```sh
python -m peye examples/dog-license.py
python -m peye --strict-proof --check-proof examples/proof/dog-license.py examples/dog-license.py
```

The second command refuses any proof that leans on trust, so here it reports
`verdict(failed(2))`: the two obligations.
Add `fact(owns('bob', 'dog8'))`, `fact(owns('bob', 'dog9'))` and
`fact(owns('bob', 'dog10'))`, and run again: Bob's count becomes 5 and he
needs a license too.

---

## Takeaway

Counting is a claim about *everything* you know. peye does the count, shows
it, and tells you plainly which part rests on "that was the full list".
