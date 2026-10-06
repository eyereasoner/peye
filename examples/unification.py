# Open lists and repeated variables enforce structural relationships.

from peye import *

fact(append([], Ys, Ys))
backward(append([X, *Xs], Ys, [X, *Zs]), append(Xs, Ys, Zs))
fact(matching_pair(pair(X, X)))
fact(head_tail([Head, *Tail], Head, Tail))
query(append(Prefix, Suffix, ['a', 'b']))
query(matching_pair(pair('same', 'same')))
query(head_tail(['a', 'b', 'c'], Head, Tail))
