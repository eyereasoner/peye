# A trajectory ends at 1; parity chooses the next recursive step.

from peye import *

fact(trajectory(1, [1]))
implied_by(trajectory(N, [N, *Rest]), (N > 1) & eq(0, N % 2) & is_(Next, N // 2) & trajectory(Next, Rest))
implied_by(
    trajectory(N, [N, *Rest]),
    (N > 1)
    & eq(1, N % 2)
    & is_(Next, 3 * N + 1)
    & trajectory(Next, Rest),
)
# A range of starting values, enumerated by ordinary clauses.
implied_by(in_range(Low, High, Low), Low <= High)
implied_by(in_range(Low, High, N), (Low < High) & is_(Next, Low + 1) & in_range(Next, High, N))
query(in_range(1, 20, N), trajectory(N, Values))
