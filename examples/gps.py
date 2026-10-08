# Goal driven Parallel Sequences -- Jos De Roo
# See background paper https://www.sciencedirect.com/science/article/pii/S1532046421000794
#
# Find sequences of actions that lead from the current state to a goal state
# within limits on duration, cost, belief, comfort and the number of stages (a
# stage is a run of steps in the same map). Each description is a transition
# from a state fluent to a new one, with the action that makes it and what that
# action costs; belief and comfort multiply along a path, duration and cost add.
#
# The original keeps the current state in the database: it reads transitions
# with clause/2, proves their preconditions as goals, and asserts and retracts
# fluents as it moves. Here the state is a list of fluents passed along the
# search, and a transition replaces its From fluent by its To fluent.

from peye import *

# find paths in the state space from the current state to a goal state within limits
implied_by(
    findpath(_Scope, [Goal, Path, Duration, Cost, Belief, Comfort, Limits]),
    current_state(State)
    & findpaths(State, [], Goal, [], 0.0, 0.0, 1.0, 1.0, Path, Duration, Cost, Belief, Comfort, Limits),
)

# A path ends as soon as the goal holds; otherwise it takes one more step.
implied_by(
    findpaths(State, Maps, Goal, Path_s, Duration_s, Cost_s, Belief_s, Comfort_s, Path, Duration, Cost, Belief, Comfort, Limits),
    holds(Goal, State, Holds)
    & struct('continue', Holds, State, Maps, Goal, Path_s, Duration_s, Cost_s, Belief_s, Comfort_s, Path, Duration, Cost, Belief, Comfort, Limits),
)

fact(
    struct('continue', 'yes', _State, _Maps, _Goal, Path, Duration, Cost, Belief, Comfort, Path, Duration, Cost, Belief, Comfort, _Limits),
)
implied_by(
    struct('continue', 'no', State, Maps_s, Goal, Path_s, Duration_s, Cost_s, Belief_s, Comfort_s, Path, Duration, Cost, Belief, Comfort, Limits),
    unify(Limits, [MaxDuration, MaxCost, MinBelief, MinComfort, MaxStagecount])
    & description(Map, [From, _Transition, To, Action, Duration_n, Cost_n, Belief_n, Comfort_n])
    & becomes(From, To, State, State_t)
    & append(Maps_s, [Map], Maps_t)
    & stagecount(Maps_t, Stagecount)
    & (Stagecount <= MaxStagecount)
    & is_(Duration_t, Duration_s + Duration_n)
    & (Duration_t <= MaxDuration)
    & is_(Cost_t, Cost_s + Cost_n)
    & (Cost_t <= MaxCost)
    & is_(Belief_t, Belief_s * Belief_n)
    & (Belief_t >= MinBelief)
    & is_(Comfort_t, Comfort_s * Comfort_n)
    & (Comfort_t >= MinComfort)
    & append(Path_s, [Action], Path_t)
    # Like the original, each step commits to the first way of finishing from it.
    & once(findpaths(State_t, Maps_t, Goal, Path_t, Duration_t, Cost_t, Belief_t, Comfort_t, Path, Duration, Cost, Belief, Comfort, Limits)),
)

# Whether a fluent of the state matches the goal, binding it to the first that does.
fact(holds(_Goal, [], 'no'))
implied_by(holds(Goal, [Fluent, *_], 'yes'), unify(Fluent, Goal))
implied_by(
    holds(Goal, [Fluent, *Fluents], Holds),
    not_unify(Fluent, Goal)
    & holds(Goal, Fluents, Holds),
)

# A transition applies to a fluent of the state and replaces it.
implied_by(becomes(From, To, [Fluent, *Fluents], [To, *Fluents]), unify(Fluent, From))
implied_by(becomes(From, To, [Fluent, *Fluents], [Fluent, *Rest]), becomes(From, To, Fluents, Rest))

# counting the number of stages (a stage is a sequence of steps in the same map)
fact(stagecount([_], 1))
implied_by(
    stagecount([Map, Next, *Maps], Count),
    identical(Map, Next)
    & stagecount([Next, *Maps], Count),
)
implied_by(
    stagecount([Map, Next, *Maps], Count),
    not_identical(Map, Next)
    & stagecount([Next, *Maps], Rest)
    & is_(Count, Rest + 1),
)

fact(append([], L, L))
implied_by(append([X, *Xs], L, [X, *Ys]), append(Xs, L, Ys))

# test data: partial map of Belgium
fact(
    description('map_be', [location(S, 'gent'), 'true', location(S, 'brugge'), 'drive_gent_brugge', 1500.0, 0.006, 0.96, 0.99]),
)
fact(
    description('map_be', [location(S, 'gent'), 'true', location(S, 'kortrijk'), 'drive_gent_kortrijk', 1600.0, 0.007, 0.96, 0.99]),
)
fact(
    description('map_be', [location(S, 'kortrijk'), 'true', location(S, 'brugge'), 'drive_kortrijk_brugge', 1600.0, 0.007, 0.96, 0.99]),
)
fact(
    description('map_be', [location(S, 'brugge'), 'true', location(S, 'oostende'), 'drive_brugge_oostende', 900.0, 0.004, 0.98, 1.0]),
)

# current state
fact(current_state([location('i1', 'gent')]))

# query
query(
    findpath('map_be', [location(_SUBJECT, 'oostende'), _PATH, _DURATION, _COST, _BELIEF, _COMFORT, [5000.0, 5.0, 0.2, 0.4, 1]]),
)
