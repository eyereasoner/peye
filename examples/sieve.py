# The sieve of Eratosthenes: list the integers from 2, then repeatedly keep the
# first and strike out its multiples from the rest. The limit is 100 rather
# than 1000 because a certificate records every intermediate list: its size
# grows far faster than the answer: about 314 KB here, more than memory holds at 1000.

from peye import *

backward(primes(Limit, Primes), integers(2, Limit, Integers), sift(Integers, Primes))

backward(integers(Start, End, []), Start > End)
backward(
    integers(Start, End, [Start, *Rest]),
    Start <= End,
    is_(Next, Start + 1),
    integers(Next, End, Rest),
)

fact(sift([], []))
backward(sift([I, *Is], [I, *Ps]), remove(I, Is, New), sift(New, Ps))

fact(remove(_, [], []))
backward(remove(P, [I, *Is], Rest), eq(0, I % P), remove(P, Is, Rest))
backward(remove(P, [I, *Is], [I, *Rest]), ne(0, I % P), remove(P, Is, Rest))

query(primes(100, _))
