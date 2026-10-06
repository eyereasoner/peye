# base/3 represents immutable external data. t/3 is the union view.

from peye import *

fact(base('alice', 'parent_of', 'bob'))
fact(base('alice', 'parent_of', 'carol'))
fact(base('bob', 'blocked', 'true'))
backward(t(S, P, O), base(S, P, O))
forward(t(C, 'child_of', P), t(P, 'parent_of', C))
forward(allowed(C), t(C, 'child_of', 'alice'), ~t(C, 'blocked', 'true'))
forward(children(P, Children), base(P, 'parent_of', _), findall(C, t(C, 'child_of', P), Children))
