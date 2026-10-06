# The monkey and bananas: a monkey, a box and some bananas hanging out of reach
# are in a room with three locations. Find every plan of up to five moves that
# ends with the monkey holding the bananas. A state is
# [Bananas, Monkey, Box, OnBox, HasBananas].
# See https://www.cs.toronto.edu/~hector/PublicTCSlides.pdf

from peye import *

backward(reaches_goal(Moves), initial_state(I), goal_state(G), reachable(I, Moves, G))

fact(reachable(S, [], S))
backward(reachable(S1, [M, *Rest], S3), legal_move(S1, M, S2), reachable(S2, Rest, S3))

fact(initial_state(['loc1', 'loc2', 'loc3', 'n', 'n']))
fact(goal_state([_, _, _, _, 'y']))

fact(legal_move([B, M, M, 'n', H], 'climb_on', [B, M, M, 'y', H]))
fact(legal_move([B, M, M, 'y', H], 'climb_off', [B, M, M, 'n', H]))
fact(legal_move([B, B, B, 'y', 'n'], 'grab', [B, B, B, 'y', 'y']))
backward(legal_move([B, M, M, 'n', H], push(X), [B, X, X, 'n', H]), location(X), not_unify(X, M))
backward(legal_move([B, M, L, 'n', H], go(X), [B, X, L, 'n', H]), location(X), not_unify(X, M))

fact(location('loc1'))
fact(location('loc2'))
fact(location('loc3'))

# Plans are tried shortest first: a plan of a given length is a list of that
# many moves still to be chosen.
fact(moves(0, []))
backward(moves(N, [_, *Rest]), N > 0, is_(M, N - 1), moves(M, Rest))
backward(in_range(Low, High, Low), Low <= High)
backward(in_range(Low, High, N), Low < High, is_(Next, Low + 1), in_range(Next, High, N))

forward(plan(Moves), in_range(1, 5, N), moves(N, Moves), reaches_goal(Moves))
