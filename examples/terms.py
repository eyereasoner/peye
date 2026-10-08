# IRIs, datatypes, language tags, lists, formulas and triple terms need
# representations, not additional language syntax or engine state.

from peye import *

fact(
    quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])),
)
fact(member_of(X, [X, *_]))
implied_by(member_of(X, [_, *Xs]), member_of(X, Xs))
implied_by(includes(graph(Triples), Triple), member_of(Triple, Triples))
implies(quoted(G) & includes(G, T), found(T))
implies(quoted(X), witness(X, W))
