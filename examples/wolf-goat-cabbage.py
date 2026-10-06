# A farmer must ferry a wolf, a goat and a cabbage across a river in a boat
# that holds him and one passenger. Left alone, the wolf eats the goat and the
# goat eats the cabbage. A state lists which bank (w or e) the farmer, wolf,
# goat and cabbage are on. The program shows a safe plan with seven crossings
# exists, and that no plan with fewer does.

from peye import *

fact(solution(['e', 'e', 'e', 'e'], []))
backward(solution(State, [Move, *Rest]), move(State, Move, Next), safe(Next), solution(Next, Rest))

backward(move([X, X, Goat, Cabbage], 'wolf', [Y, Y, Goat, Cabbage]), change(X, Y))
backward(move([X, Wolf, X, Cabbage], 'goat', [Y, Wolf, Y, Cabbage]), change(X, Y))
backward(move([X, Wolf, Goat, X], 'cabbage', [Y, Wolf, Goat, Y]), change(X, Y))
backward(move([X, Wolf, Goat, Cabbage], 'nothing', [Y, Wolf, Goat, Cabbage]), change(X, Y))

fact(change('e', 'w'))
fact(change('w', 'e'))

# Safe when the goat is with the farmer, or with neither the wolf nor the cabbage.
backward(
    safe([Farmer, Wolf, Goat, Cabbage]),
    one_eq(Farmer, Goat, Wolf),
    one_eq(Farmer, Goat, Cabbage),
)
fact(one_eq(X, X, _))
fact(one_eq(X, _, X))

# A plan of a given length is a list of that many moves still to be chosen.
fact(moves(0, []))
backward(moves(N, [_, *Rest]), N > 0, is_(M, N - 1), moves(M, Rest))
backward(in_range(Low, High, Low), Low <= High)
backward(in_range(Low, High, N), Low < High, is_(Next, Low + 1), in_range(Next, High, N))

backward(
    'shorter_solution',
    in_range(0, 6, N),
    moves(N, Plan),
    solution(['w', 'w', 'w', 'w'], Plan),
)

backward(
    wolf_goat_cabbage_verified(7),
    not_('shorter_solution'),
    moves(7, Plan),
    once(solution(['w', 'w', 'w', 'w'], Plan)),
)
backward(
    shortest_crossing(Plan),
    not_('shorter_solution'),
    moves(7, Plan),
    solution(['w', 'w', 'w', 'w'], Plan),
)

query(wolf_goat_cabbage_verified(7))
query(shortest_crossing(_))
