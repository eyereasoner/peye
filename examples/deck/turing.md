# A Turing Machine

*The simplest model of a computer, adding one to a binary number, step by step.*

[turing.py](https://github.com/eyereasoner/peye/blob/main/examples/turing.py) · [output](https://github.com/eyereasoner/peye/blob/main/examples/output/turing.py) · [proof](https://github.com/eyereasoner/peye/blob/main/examples/proof/turing.py) · [check](https://github.com/eyereasoner/peye/blob/main/examples/check/turing.py) · [try it in the playground](https://eyereasoner.github.io/peye/playground/#example=turing)

---

## The question

In 1936 Alan Turing described an imaginary machine: a long tape of cells, a
head that reads and writes one cell at a time and moves left or right, and
a small table of instructions. Anything a modern computer can calculate,
such a machine can calculate too.

Here the machine adds one to a **binary** number (written with only 0 and 1).

**What is 101001 + 1?** And can we watch every move of the machine?

---

## What we tell peye: the machine

```python
fact(start('add1', 0))
fact(t([0, 0, 0, 'r'], 0))
fact(t([0, 1, 1, 'r'], 0))
fact(t([0, '#', '#', 'l'], 1))
fact(t([1, 0, 1, 's'], 'halt'))
fact(t([1, 1, 0, 'l'], 1))
fact(t([1, '#', 1, 's'], 'halt'))
```

Each line reads: *in state S, seeing symbol X, write Y, move (l)eft,
(r)ight or (s)tay, and go to the next state.* `'#'` is a blank cell.

State 0 runs right to the end of the number. State 1 walks back, turning
1s into 0s until it can turn a 0 (or a blank) into a 1: the carry.

---

## What we tell peye: the interpreter

```python
implied_by(
    find(State, Left, Cell, Right, OutTape),
    t([State, Cell, Write, Move], Next)
    & move(Move, Left, Write, Right, A, B, C)
    & struct('continue', Next, A, B, C, OutTape),
)

implied_by(
    struct('continue', 'halt', Left, Cell, Right, OutTape),
    reverse(Left, R)
    & append(R, [Cell, *Right], OutTape),
)
implied_by(
    struct('continue', State, Left, Cell, Right, OutTape),
    not_unify(State, 'halt')
    & find(State, Left, Cell, Right, OutTape),
)
```

An **interpreter** is a program that runs another program. This one looks
up the instruction, moves the head, and repeats until the state is
`'halt'`. (`continue` is a reserved word in Python, so that step is
written as `struct('continue', ...)`.)

---

## What peye concludes

```python
compute([1, 0, 1, 0, 0, 1], [1, 0, 1, 0, 1, 0, '#'])
compute([1, 0, 1, 1, 1, 1], [1, 1, 0, 0, 0, 0, '#'])
compute([1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, '#'])
compute([], [1, '#'])
```

In everyday numbers: 41 + 1 = 42, 47 + 1 = 48, 63 + 1 = 64 (the number
grows a digit), and an empty tape becomes 1. The trailing `'#'` is the blank
cell the head stopped next to.

---

## Why: the proof in plain words

For 101001, the proof records every move:

1. Start in state 0, reading the first 1. Rule `t([0, 1, 1, 'r'], 0)`:
   keep the 1, move right.
2. Read 0: keep it, move right. … and so on to the blank at the end.
3. At the blank, switch to state 1 and step left.
4. Read 1: write 0, step left (the carry).
5. Read 0: write 1, halt.

Each move names the instruction it used and the tape before and after.

---

## Checked, not just claimed

The checker went through all four runs: 144 steps.

- 142 were matched to the exact instruction or program line they cite;
- the 2 built-in tests ("state 0 is not `'halt'`", "state 1 is not
  `'halt'`") were **recomputed** by the checker itself;
- no step depends on itself in a circle, and nothing is extra.

Verdict: **checked**. All 144 steps verified, nothing taken on trust.

---

## Try it

```sh
python -m peye examples/turing.py            # the answers
python -m peye --proof examples/turing.py    # answers with their proof
```

Or open it in the [playground](https://eyereasoner.github.io/peye/playground/#example=turing).
Add `query(compute([1, 0, 1, 1], _))` and run again: you get
`compute([1, 0, 1, 1], [1, 1, 0, 0, '#'])`, that is 11 + 1 = 12.

---

## Takeaway

A Turing machine is computation at its barest. With a proof, every tick of
it becomes something you can read, replay and check.
