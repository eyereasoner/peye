# A Turing machine interpreter, and a machine that adds one to a binary number.
# The tape is held as the cells to the left (reversed), the cell under the
# head, and the cells to the right; # is a blank cell.
# See https://en.wikipedia.org/wiki/Universal_Turing_machine

from peye import *

backward(compute([], OutTape), start(_, I), find(I, [], '#', [], OutTape))
backward(compute([Head, *Tail], OutTape), start(_, I), find(I, [], Head, Tail, OutTape))

backward(
    find(State, Left, Cell, Right, OutTape),
    t([State, Cell, Write, Move], Next),
    move(Move, Left, Write, Right, A, B, C),
    struct('continue', Next, A, B, C, OutTape),
)

backward(
    struct('continue', 'halt', Left, Cell, Right, OutTape),
    reverse(Left, R),
    append(R, [Cell, *Right], OutTape),
)
backward(
    struct('continue', State, Left, Cell, Right, OutTape),
    not_unify(State, 'halt'),
    find(State, Left, Cell, Right, OutTape),
)

fact(move('l', [], Cell, Right, [], '#', [Cell, *Right]))
fact(move('l', [Head, *Tail], Cell, Right, Tail, Head, [Cell, *Right]))
fact(move('s', Left, Cell, Right, Left, Cell, Right))
fact(move('r', Left, Cell, [], [Cell, *Left], '#', []))
fact(move('r', Left, Cell, [Head, *Tail], [Cell, *Left], Head, Tail))

fact(append([], Ys, Ys))
backward(append([X, *Xs], Ys, [X, *Zs]), append(Xs, Ys, Zs))
backward(reverse(Xs, Ys), reverse(Xs, [], Ys))
fact(reverse([], Ys, Ys))
backward(reverse([X, *Xs], Acc, Ys), reverse(Xs, [X, *Acc], Ys))

# The machine: scan right to the end, then carry leftwards.
fact(start('add1', 0))
fact(t([0, 0, 0, 'r'], 0))
fact(t([0, 1, 1, 'r'], 0))
fact(t([0, '#', '#', 'l'], 1))
fact(t([1, 0, 1, 's'], 'halt'))
fact(t([1, 1, 0, 'l'], 1))
fact(t([1, '#', 1, 's'], 'halt'))

query(compute([1, 0, 1, 0, 0, 1], _))
query(compute([1, 0, 1, 1, 1, 1], _))
query(compute([1, 1, 1, 1, 1, 1], _))
query(compute([], _))
