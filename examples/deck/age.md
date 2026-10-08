# Age

*Is someone over 80? A calendar question, answered with every day counted.*

[age.py](https://github.com/eyereasoner/peye/blob/main/examples/age.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/age.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/age.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/age.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=age)

---

## The question

Pat was born on 21 August 1944. Some benefits, discounts or rules start
"after your 80th birthday".

**On 1 October 2026, is Pat older than 80?** It sounds easy, but calendars
have leap years, months of different lengths and birthdays on 29 February.
We want an answer that shows its arithmetic.

---

## What we tell peye

Two facts: a birth date, and the date we ask about. Writing the date down
(instead of reading the computer's clock) means the answer is the same
tomorrow.

```python
fact(birth_date('pat_h', date(1944, 8, 21)))
fact(as_of(date(2026, 10, 1)))

query(age_above(Person, years(80)))
```

The last line is the question: *find every Person whose age is above 80
years.* `query` means "work this out and report what follows".

---

## How the program counts

The rule for "older than N years", quoted from the program:

```python
implied_by(
    age_above(Person, years(Years), Date),
    is_int(Years)
    & (Years >= 0)
    & birth_date(Person, Birth)
    & date_day(Birth, Born)
    & date_day(Date, Today)
    & (Today >= Born)
    & anniversary(Birth, Years, Anniversary)
    & date_day(Anniversary, Threshold)
    & (Today > Threshold),
)
```

In words: turn each date into a *day number* (days since the start of the
calendar), find the 80th birthday, and check that today is strictly later.
`date_day` is defined in the same file, leap-year rules included.

---

## What peye concludes

```python
age_above('pat_h', years(80))
```

Yes: Pat is older than 80 on 1 October 2026.

---

## Why: the proof in plain words

The proof records every number it used:

1. Pat's birthday, 21 August 1944, is day **709899**.
2. The reference date, 1 October 2026, is day **739890**.
3. The 80th birthday is 21 August 2024, day **739119**.
4. 739890 is greater than 739119, so the threshold has been passed.

Along the way it shows *why* 1944 and 2024 are leap years (divisible by 4,
not by 100) and why 2026 is not.

---

## Checked, not just claimed

A separate checker reads the proof against the program:

- each of the **21** reasoning steps really is an instance of the program
  line it cites;
- each of the **33** calculations (comparisons, additions, `%`) is
  recomputed by the checker and agrees;
- nothing depends on itself in a circle, and every step serves the answer.

Verdict: **checked**. All 54 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/age.py
python -m peye --goal "age_above('pat_h', years(80), date(2024, 8, 22))" examples/age.py
python -m peye --goal "age_days('pat_h', date(2026, 10, 1), Days)" examples/age.py
```

The last one answers `age_days('pat_h', date(2026, 10, 1), 29991)`. Change `as_of` to `date(2024, 8, 21)`,
the 80th birthday itself: there is no answer, because on that day Pat is
exactly 80, not *above* 80. One day later, the answer comes back.

---

## Takeaway

Date arithmetic is where small mistakes hide. Here each day number, each
leap-year decision and each comparison is written down and rechecked, so a
"yes" can be audited down to the last day.
