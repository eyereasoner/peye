# Audit each quoted graph separately: a fact in one scope does not fill another.

from peye import *

fact(
    context('approved', graph([triple('alice', 'role', 'editor'), triple('alice', 'consent', 'yes')])),
)
fact(context('incomplete', graph([triple('bob', 'role', 'editor')])))
fact(member(X, [X, *_]))
implied_by(member(X, [_, *Xs]), member(X, Xs))
implied_by(includes(graph(Triples), Triple), member(Triple, Triples))
implies(
    context(Context, Graph)
    & includes(Graph, triple(Person, 'consent', 'yes')),
    consented(Context, Person),
)
implies(
    context(Context, Graph)
    & includes(Graph, triple(Person, 'role', 'editor'))
    & ~includes(Graph, triple(Person, 'consent', 'yes')),
    needs_review(Context, Person),
)
