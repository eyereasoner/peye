# Map a predicate over subjects and concatenate all matching objects.

from peye import *

fact(t('s1', 'p1', 'o1'))
fact(t('s2', 'p1', 'o2'))
fact(t('s3', 'p1', 'o3'))
fact(t('s3', 'p1', 'o4'))
fact(append([], Ys, Ys))
backward(append([X, *Xs], Ys, [X, *Zs]), append(Xs, Ys, Zs))
fact(flat_map([], _, []))
backward(
    flat_map([S, *Subjects], P, Objects),
    findall(O, t(S, P, O), Here),
    flat_map(Subjects, P, Rest),
    append(Here, Rest, Objects),
)
query(flat_map(['s1', 's2', 's3'], 'p1', Objects))
query(flat_map(['missing'], 'p1', Objects))
query(flat_map(['s1'], 'p2', Objects))
