# Fast doubling computes F(N) and F(N+1) together in logarithmic depth.
# F(2K) = F(K)*(2*F(K+1)-F(K)); F(2K+1) = F(K)^2+F(K+1)^2.
# Integer arithmetic keeps even very large results exact.

from peye import *

implied_by(fib(N, F), (N >= 0) & fib_pair(N, F, _))
fact(fib_pair(0, 0, 1))
implied_by(
    fib_pair(N, A, B),
    (N > 0)
    & is_(Half, N // 2)
    & fib_pair(Half, X, Y)
    & is_(C, X * (2 * Y - X))
    & is_(D, X * X + Y * Y)
    & parity_pair(N, C, D, A, B),
)
implied_by(parity_pair(N, C, D, A, B), eq(0, N % 2) & unify(A, C) & unify(B, D))
implied_by(parity_pair(N, C, D, A, B), eq(1, N % 2) & unify(A, D) & is_(B, C + D))
# The ratio of successive Fibonacci numbers converges on the golden ratio.
implied_by(
    golden_ratio(N, Ratio),
    fib(N, A)
    & (A > 0)
    & is_(Next, N + 1)
    & fib(Next, B)
    & is_(Ratio, B / A),
)
query(fib(0, F))
query(fib(1, F))
query(fib(10, F))
query(fib(100, F))
query(fib(1000, F))
query(fib(10000, F))
query(golden_ratio(1, Ratio))
query(golden_ratio(10, Ratio))
query(golden_ratio(100, Ratio))
query(golden_ratio(1000, Ratio))
