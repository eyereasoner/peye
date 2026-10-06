# Who killed Aunt Agatha? Pelletier's problem 55, puzzle PUZ001 in TPTP:
#   1. Someone who lives in Dreadbury Mansion killed Aunt Agatha.
#   2. Agatha, the butler and Charles live in Dreadbury Mansion, and are the
#      only people who live therein.
#   3. A killer always hates their victim, and is never richer than them.
#   4. Charles hates no one that Aunt Agatha hates.
#   5. Agatha hates everyone except the butler.
#   6. The butler hates everyone not richer than Aunt Agatha.
#   7. The butler hates everyone Aunt Agatha hates.
#   8. No one hates everyone.
#   9. Agatha is not the butler.
# Therefore Agatha killed herself.
#
# The conclusion is entailed, not merely possible: it must hold in every
# situation the premises allow. They leave open who hates whom and who is
# richer than whom, so a model assigns yes or no to each hates(X, Y) and to
# each richer(X, agatha); the rest of richer/2 occurs in no premise. Every
# model is enumerated, and in every one of them the killer is Agatha.
#
# A premise narrows the values it constrains and leaves the others unbound;
# labelling gives each remaining value yes and then no, so every model is
# found exactly once. Premise 9 holds because distinct atoms never unify.

from peye import *

backward(
    model(Killer, world(Richer, Hates)),
    unify(Richer, richer(RA, RB, RC)),
    unify(Hates, hates(AA, AB, AC, BA, BB, BC, CA, CB, CC)),
    resident(Killer),  # 1, 2
    hates(Hates, Killer, 'agatha', 'yes'),  # 3
    richer(Richer, Killer, 'no'),
    implies_not(AA, CA),  # 4
    implies_not(AB, CB),
    implies_not(AC, CC),
    unify(AA, 'yes'),  # 5
    unify(AC, 'yes'),
    unless(RA, BA),  # 6
    unless(RB, BB),
    unless(RC, BC),
    implies(AA, BA),  # 7
    implies(AB, BB),
    implies(AC, BC),
    label([RA, RB, RC, AA, AB, AC, BA, BB, BC, CA, CB, CC]),
    some_no(AA, AB, AC),  # 8
    some_no(BA, BB, BC),
    some_no(CA, CB, CC),
)

fact(resident('agatha'))
fact(resident('butler'))
fact(resident('charles'))

# hates(Hates, X, Y, V): V says whether X hates Y.
fact(hates(hates(V, _, _, _, _, _, _, _, _), 'agatha', 'agatha', V))
fact(hates(hates(_, V, _, _, _, _, _, _, _), 'agatha', 'butler', V))
fact(hates(hates(_, _, V, _, _, _, _, _, _), 'agatha', 'charles', V))
fact(hates(hates(_, _, _, V, _, _, _, _, _), 'butler', 'agatha', V))
fact(hates(hates(_, _, _, _, V, _, _, _, _), 'butler', 'butler', V))
fact(hates(hates(_, _, _, _, _, V, _, _, _), 'butler', 'charles', V))
fact(hates(hates(_, _, _, _, _, _, V, _, _), 'charles', 'agatha', V))
fact(hates(hates(_, _, _, _, _, _, _, V, _), 'charles', 'butler', V))
fact(hates(hates(_, _, _, _, _, _, _, _, V), 'charles', 'charles', V))
# richer(Richer, X, V): V says whether X is richer than Agatha.
fact(richer(richer(V, _, _), 'agatha', V))
fact(richer(richer(_, V, _), 'butler', V))
fact(richer(richer(_, _, V), 'charles', V))

fact(truth('yes'))
fact(truth('no'))
fact(label([]))
backward(label([V, *Vs]), truth(V), label(Vs))
# Each connective's clauses are mutually exclusive in their first argument,
# so a value that is still unbound splits the search without duplicates.
fact(implies('no', _))  # A -> B
fact(implies('yes', 'yes'))
fact(implies_not('no', _))  # A -> not B
fact(implies_not('yes', 'no'))
fact(unless('yes', _))  # not A -> B
fact(unless('no', 'yes'))
fact(some_no('no', _, _))  # not (A and B and C)
fact(some_no('yes', 'no', _))
fact(some_no('yes', 'yes', 'no'))

fact(count([], 0))
backward(count([_, *Xs], N), count(Xs, M), is_(N, M + 1))

# How many models make each resident the killer.
forward(models(Suspect, N), resident(Suspect), findall(W, model(Suspect, W), Ws), count(Ws, N))
# Entailment: some model exists, and every model has Agatha as the killer.
forward(
    entailed(killed('agatha', 'agatha')),
    models('agatha', N),
    N > 0,
    models('butler', 0),
    models('charles', 0),
)
# One model in full, with a proof that every premise holds in it.
forward(witness(Killer, W), once(model(Killer, W)))
