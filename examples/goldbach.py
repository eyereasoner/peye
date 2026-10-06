# Goldbach's conjecture: every even number greater than 2 is the sum of two
# primes. For each power of two from 4 to 2^25, find the split whose smaller
# prime is the least, testing primality by trial division.
# See https://en.wikipedia.org/wiki/Goldbach%27s_conjecture

from peye import *

fact(split(4, [2, 2]))
backward(split(N, Pair), eq(0, N % 2), N > 4, once(split_from(N, Pair, 3)))

backward(split_from(N, [P, Q], P), is_(Q, N - P), is_prime(Q))
backward(split_from(N, Pair, P), P < N, once(next_prime(P, Next)), split_from(N, Pair, Next))

backward(next_prime(P, Next), is_(Next, P + 2), is_prime(Next))
backward(next_prime(P, Next), is_(Q, P + 2), next_prime(Q, Next))

fact(is_prime(2))
fact(is_prime(3))
backward(is_prime(P), P > 3, eq(1, P % 2), ~has_factor(P, 3))

backward(has_factor(N, L), eq(0, N % L))
backward(has_factor(N, L), L * L < N, is_(M, L + 2), has_factor(N, M))

backward(in_range(Low, High, Low), Low <= High)
backward(in_range(Low, High, N), Low < High, is_(Next, Low + 1), in_range(Next, High, N))

forward(goldbach(N, Pair), in_range(2, 25, I), is_(N, 2 ** I), split(N, Pair))
