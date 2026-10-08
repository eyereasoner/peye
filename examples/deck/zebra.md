# Zebra

*Einstein's riddle: fifteen clues, five houses, one answer you can check.*

[zebra.py](https://github.com/eyereasoner/peye/blob/main/examples/zebra.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/zebra.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/zebra.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/zebra.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=zebra)

---

## The question

Five houses stand in a row. Each has its own colour, and its owner has a
nationality, a pet, a favourite drink and a brand of cigarettes. Fifteen
clues follow (the first is simply "there are five houses"), such as:

- The Englishman lives in the red house.
- The green house is immediately to the right of the ivory house.
- Milk is drunk in the middle house.

**Who drinks water, and who owns the zebra?**

This puzzle, often called *Einstein's riddle*, was printed in *Life
International* on 17 December 1962.

---

## What we tell peye

The program starts with five houses about which nothing is known, and each
clue fills in a little more:

```python
implied_by(
    zebra(WaterDrinker, ZebraOwner),
    unify(Houses, [_, _, _, _, _])  # 1. There are five houses.
    & member(house('red', 'english', _, _, _), Houses)  # 2. The Englishman lives in the red house.
    & member(house(_, 'spanish', 'dog', _, _), Houses)  # 3. The Spaniard owns the dog.
    & next_to(house('ivory', _, _, _, _), house('green', _, _, _, _), Houses)  # 6. Green is immediately right of ivory.
    & unify(Houses, [_, _, house(_, _, _, 'milk', _), _, _])  # 9. Milk is drunk in the middle house.
    & unify(Houses, [house(_, 'norwegian', _, _, _), *_])  # 10. The Norwegian lives in the first house.
    # … the other clues, in the same style
    & member(house(_, WaterDrinker, _, 'water', _), Houses)
    & member(house(_, ZebraOwner, 'zebra', _, _), Houses),
)
```

`_` means "not known yet". Each house is
`house(Colour, Nationality, Pet, Drink, Cigarettes)`.

---

## How the search works

peye tries to fit each clue into the houses, one at a time. When a clue
doesn't fit the choices made so far, it backs up and tries another place.

This filling-in of blanks by matching patterns is called **unification**:
`house('red', 'english', _, _, _)` matches any house that is red or unknown
in colour, and English or unknown in nationality, and fills in what was
missing.

No arithmetic, no special puzzle solver — just matching.

---

## What peye concludes

```python
zebra('norwegian', 'japanese')
```

**The Norwegian drinks water, and the Japanese owns the zebra.**

The full street, as recorded in the proof:

| House | Colour | Who | Pet | Drink | Smokes |
| --- | --- | --- | --- | --- | --- |
| 1 | yellow | Norwegian | fox | water | Kools |
| 2 | blue | Ukrainian | horse | tea | Chesterfields |
| 3 | red | English | snails | milk | Old Gold |
| 4 | ivory | Spanish | dog | orange juice | Lucky Strike |
| 5 | green | Japanese | zebra | coffee | Parliaments |

---

## Why: the proof in plain words

The proof doesn't replay the search with all its dead ends. It records the
**finished street** and shows that every clue holds in it:

1. The street has five houses — *clue 1, checked by comparing lists*.
2. The red English house is in the street — *it is house 3*.
3. Ivory is immediately left of green — *houses 4 and 5*.
4. Milk is in the middle — *house 3*. The Norwegian is first — *house 1*.
5. …and so on for every clue, then: water is drunk in the Norwegian's house,
   and the zebra lives in the Japanese house.

Anyone can check the answer this way, without redoing the search.

---

## Checked, not just claimed

- **26 steps**: 23 verified as exact instances of the program lines they
  cite, 1 comparison recomputed, and 2 "either side" steps (from the "next
  to" clues) checked by the side that holds.
- No circular reasoning, every clue accounted for, nothing extra.
- **0** steps taken on trust.

Verdict: **checked**.

The proof shows this street satisfies every clue. It does not by itself show
that no *other* street would — that was never claimed.

---

## Try it

```sh
python -m peye examples/zebra.py            # the answer
python -m peye --proof examples/zebra.py    # with the finished street
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=zebra).
Delete the line for clue 15 ("The Norwegian is next to blue") and run again:
the answer is no longer pinned down, and peye prints 15 different
`zebra(...)` answers.

---

## Takeaway

A puzzle can be hard to solve and easy to check. peye does the hard part,
then hands you the easy part: a filled-in street and a clue-by-clue proof
that it fits.
