# Cousins occupy the same generation in distinct family branches.

from peye import *

fact(parent('adam', 'bob'))
fact(parent('adam', 'carol'))
fact(parent('bob', 'dave'))
fact(parent('bob', 'eve'))
fact(parent('carol', 'frank'))
fact(parent('carol', 'grace'))
fact(parent('dave', 'heidi'))
fact(parent('eve', 'ivan'))
fact(parent('frank', 'judy'))
fact(generation('adam', 0))
fact(branch('dave', 'b'))
fact(branch('eve', 'b'))
fact(branch('frank', 'c'))
fact(branch('grace', 'c'))
implies(parent(Parent, Child) & generation(Parent, N) & is_(Next, N + 1), generation(Child, Next))
implies(parent(Parent, Child) & branch(Parent, Branch), branch(Child, Branch))
implies(
    generation(X, N)
    & generation(Y, N)
    & branch(X, A)
    & branch(Y, B)
    & not_unify(A, B),
    cousin(X, Y),
)
