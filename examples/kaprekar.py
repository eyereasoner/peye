# Kaprekar's routine: take a four-digit number whose digits are not all equal,
# subtract its digits in ascending order from its digits in descending order,
# and repeat. Every such number reaches 6174 within seven steps. The first step
# depends only on which digits occur, so it is enough to check each of the 705
# nontrivial multisets of four digits once rather than all 10,000 numbers.

from peye import *

implied_by(
    kaprekar_step(A, B),
    digits(A, Ds)
    & sort4(Ds, Asc)
    & reverse(Asc, Desc)
    & number_of(Asc, Low)
    & number_of(Desc, High)
    & is_(B, High - Low),
)

implied_by(
    digits(A, [B, C, D, E]),
    is_(B, A // 1000)
    & is_(F, A % 1000)
    & is_(C, F // 100)
    & is_(G, F % 100)
    & is_(D, G // 10)
    & is_(E, G % 10),
)
implied_by(number_of([A, B, C, D], N), is_(N, A * 1000 + B * 100 + C * 10 + D))

# Insertion sort, ascending.
implied_by(sort4(Xs, Ys), insertion(Xs, [], Ys))
fact(insertion([], Ys, Ys))
implied_by(insertion([X, *Xs], Acc, Ys), insert(X, Acc, Next) & insertion(Xs, Next, Ys))
fact(insert(X, [], [X]))
implied_by(insert(X, [Y, *Ys], [X, Y, *Ys]), X <= Y)
implied_by(insert(X, [Y, *Ys], [Y, *Zs]), (X > Y) & insert(X, Ys, Zs))
implied_by(reverse(Xs, Ys), reverse(Xs, [], Ys))
fact(reverse([], Ys, Ys))
implied_by(reverse([X, *Xs], Acc, Ys), reverse(Xs, [X, *Acc], Ys))

implied_by(in_range(Low, High, Low), Low <= High)
implied_by(in_range(Low, High, N), (Low < High) & is_(Next, Low + 1) & in_range(Next, High, N))

# One representative for every multiset of four decimal digits, nondecreasing.
implied_by(
    digit_multiset(N),
    in_range(0, 9, A)
    & in_range(A, 9, B)
    & in_range(B, 9, C)
    & in_range(C, 9, D)
    & ~(eq(A, B) & eq(B, C) & eq(C, D))
    & is_(N, A * 1000 + B * 100 + C * 10 + D),
)

fact(reaches_6174(6174, _))
implied_by(
    reaches_6174(A, Steps),
    ne(A, 6174)
    & (Steps < 7)
    & kaprekar_step(A, B)
    & is_(Next, Steps + 1)
    & reaches_6174(B, Next),
)

implied_by('counterexample', digit_multiset(A) & ~reaches_6174(A, 0))
implied_by(kaprekar_verified(6174, 7), not_('counterexample'))

query(kaprekar_verified(6174, 7))
