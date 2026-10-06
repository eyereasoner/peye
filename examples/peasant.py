# Peasant multiplication and exponentiation, as in ancient Egyptian arithmetic:
# halve one operand, double (or square) the other, and add (or multiply) in the
# rows where the halved operand was odd. Only halving, doubling and addition
# are needed, and the integers stay exact however large they grow.

from peye import *

fact(prod([0, _], 0))
backward(prod([X, Y], Z), ne(X, 0), eq(0, X % 2), is_(S, X // 2), is_(T, Y + Y), prod([S, T], Z))
backward(
    prod([X, Y], Z),
    ne(X, 0),
    eq(1, X % 2),
    is_(S, X // 2),
    is_(T, Y + Y),
    prod([S, T], R),
    is_(Z, R + Y),
)

fact(pow([_, 0], 1))
backward(pow([X, Y], Z), ne(Y, 0), eq(0, Y % 2), is_(S, X * X), is_(T, Y // 2), pow([S, T], Z))
backward(
    pow([X, Y], Z),
    ne(Y, 0),
    eq(1, Y % 2),
    is_(S, X * X),
    is_(T, Y // 2),
    pow([S, T], R),
    is_(Z, R * X),
)

query(prod([3, 0], _))
query(prod([5, 6], _))
query(prod([238, 13], _))
query(prod([8367238, 27133], _))
query(prod([62713345408367238, 40836723862713345], _))
query(prod([4083672386271334562713345408367238, 4083672386271334562713345408367238], _))
query(pow([3, 0], _))
query(pow([5, 6], _))
query(pow([238, 13], _))
query(pow([8367238, 2713], _))
