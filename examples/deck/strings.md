# Strings

*Building and taking apart text — accents and emoji included.*

[strings.py](https://github.com/eyereasoner/peye/blob/main/examples/strings.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/strings.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/strings.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/strings.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=strings)

---

## The question

Programs handle text all the time: making a label, counting letters,
looking up the code behind a symbol. Three small jobs:

- **Make a label** by putting `hello_` in front of a name.
- **Split `café` into its letters**, and count them.
- **Find the number** a computer uses for the emoji 😀.

The catch: é and 😀 are not plain English letters. Will they be handled
correctly?

---

## A word on Unicode

Computers store every character as a number. **Unicode** is the worldwide
list that gives each character — Latin, Greek, Chinese, emoji — its own
number, called a *code point*.

Some characters take several bytes to store, which is why naive programs
sometimes count `café` as 5 letters instead of 4.

---

## What we tell peye

```python
implied_by(label(Name, Label), atom_concat('hello_', Name, Label))
implied_by(characters(Text, Chars, Length), atom_chars(Text, Chars) & atom_length(Text, Length))
implied_by(unicode_codes(Text, Codes), atom_codes(Text, Codes))
query(label('alice', Label))
query(characters('café', Chars, Length))
query(unicode_codes('😀', Codes))
```

A piece of text like `'alice'` is called an *atom*. The built-in tools
join atoms (`atom_concat`), split them into characters (`atom_chars`),
measure them (`atom_length`) and give their code points (`atom_codes`).

---

## What peye concludes

```python
label('alice', 'hello_alice')
characters('café', ['c', 'a', 'f', 'é'], 4)
unicode_codes('😀', [128512])
```

- The label is `hello_alice`.
- `café` is four characters, with `é` as one of them.
- 😀 is a single character, code point 128512.

---

## Why: the proof in plain words

1. Joining `hello_` and `alice` gives `hello_alice` — *a built-in
   calculation*.
2. So the label of alice is `hello_alice` — *rule 1*.
3. `café` splits into c, a, f, é, and its length is 4 — *two built-in
   calculations*.
4. So those are its characters and length — *rule 2*.
5. The code of 😀 is 128512 — *a built-in calculation*, so *rule 3* gives
   the answer.

---

## Checked, not just claimed

A separate checker read all 7 steps of the proof against the program:

- 3 steps are verified as exact instances of the rules they cite;
- 4 built-in text calculations are **recomputed** by the checker itself,
  and they agree — so `café` really is 4 characters, independently;
- every step serves one of the 3 answers.

Verdict: **checked**. Nothing taken on trust.

---

## Try it

```sh
python -m peye examples/strings.py            # the answers
python -m peye --proof examples/strings.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=strings).
Add `query(characters('Zoë', Chars, Length))` and run again: you get
`characters('Zoë', ['Z', 'o', 'ë'], 3)`.

---

## Takeaway

Text is data like any other: it can be built, split and measured with
plain rules — and the checker recounts the letters rather than taking the
program's word for it.
