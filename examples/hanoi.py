# Move three disks using a spare peg; recursion constructs the move list.

from peye import *

fact(append([], Ys, Ys))
backward(append([X, *Xs], Ys, [X, *Zs]), append(Xs, Ys, Zs))
fact(moves(1, From, To, _, [move(From, To)]))
backward(
    moves(N, From, To, Spare, Moves),
    N > 1,
    is_(Smaller, N - 1),
    moves(Smaller, From, Spare, To, First),
    moves(Smaller, Spare, To, From, Last),
    append(First, [move(From, To), *Last], Moves),
)
query(moves(3, 'left', 'right', 'center', Moves))
