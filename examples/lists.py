# Define list operations with ordinary recursive clauses.

from peye import *

fact(append([], Ys, Ys))
backward(append([X, *Xs], Ys, [X, *Zs]), append(Xs, Ys, Zs))
fact(squares([], []))
backward(squares([X, *Xs], [Y, *Ys]), is_(Y, X * X), squares(Xs, Ys))
fact(sum([], 0))
backward(sum([X, *Xs], Total), sum(Xs, Rest), is_(Total, X + Rest))
query(append(['a', 'b'], ['c', 'd'], Joined))
query(squares([1, 2, 3, 4], Squared))
query(sum([1, 2, 3, 4], Total))
