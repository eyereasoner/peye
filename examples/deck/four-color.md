# Four colours

*Colouring the map of the European Union so that no neighbours match.*

[four-color.py](https://github.com/eyereasoner/peye/blob/main/examples/four-color.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/four-color.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/four-color.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/four-color.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=four-color)

---

## The question

Mapmakers like neighbouring countries to have different colours. A famous
result, the *four colour theorem*, says four colours are always enough for
any flat map.

**Can peye colour the 27 countries of the European Union with red, green,
blue and yellow, so that no two neighbours share a colour?**

---

## What we tell peye

The map, as a list of neighbours for each country:

```python
fact(neighbours('Belgium', ['France', 'Netherlands', 'Luxemburg', 'Germany']))
fact(neighbours('Netherlands', ['Belgium', 'Germany']))
# … 24 more countries
fact(neighbours('Croatia', ['Slovenia', 'Hungary']))

query(colors('mapEU', _))
```

Islands such as Ireland, Cyprus and Malta have an empty list `[]`.

---

## How it colours

```python
implied_by(
    places([[Place, Color], *Tail]),
    places(Tail)
    & neighbours(Place, Neighbours)
    & member(Color, ['red', 'green', 'blue', 'yellow'])
    & ~conflict(Color, Tail, Neighbours),
)
```

Countries are coloured one at a time, starting from the end of the list.
Each takes the first colour from red, green, blue, yellow that *no*
already-coloured neighbour has. `~` means "it is not the case that": here,
there is no conflict.

---

## What peye concludes

One colouring of all 27 countries (excerpt):

```python
colors('mapEU', [['Belgium', 'yellow'], ['Netherlands', 'green'],
  ['Luxemburg', 'green'], ['France', 'blue'], ['Germany', 'red'],
  ['Italy', 'red'], ['Denmark', 'green'], ['Ireland', 'red'],  # …
  ['Bulgaria', 'green'], ['Romania', 'red'], ['Croatia', 'red']])
```

Only red, green, blue and yellow are used; yellow is needed just twice,
for Austria and Belgium.

---

## Why: the proof in plain words

1. Gather all countries on the map into a list (27 of them).
2. Croatia goes first: red, since nothing is coloured yet.
3. Romania: red is fine, Croatia is not its neighbour.
4. Bulgaria: its neighbour Romania is red, so it takes green.
5. …and so on until Belgium, whose neighbours already use red, green and
   blue, so it gets yellow.

Each "no conflict" is a step in the proof.

---

## Checked, not just claimed

The checker verifies 66 steps against the program. 28 steps are taken on
trust and listed as **obligations**:

- **1 collected**: the list of countries gathered with `findall` ("find
  all") is assumed to be the complete map;
- **27 absent**: one per country, "this colour clashes with no coloured
  neighbour". peye searched and found no clash; the checker records that
  rather than proving a negative.

The checker did look for evidence against all 28 and found none.

Verdict: **checked_with_obligations**. 95 steps, 28 on trust.

---

## Try it

```sh
python -m peye examples/four-color.py
```

Swap the colour order to `['yellow', 'blue', 'green', 'red']`: you get a
different, equally valid map, starting with Belgium red. Or give Ireland a
neighbour: change its line to `fact(neighbours('Ireland', ['United Kingdom']))`
and add `fact(neighbours('United Kingdom', ['Ireland']))` — the UK becomes red
and Ireland turns green.

---

## Takeaway

A search that says "no clash here" is making a claim about what is *not*
there. peye finds the colouring, shows each choice, and lists exactly which
of those "nothing found" claims you are trusting.
