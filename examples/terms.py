# IRIs, datatypes, language tags, lists, formulas and triple terms need
# representations, not additional language syntax or engine state.

from peye import *

fact(
    quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])),
)
fact(member_of(X, [X, *_]))
backward(member_of(X, [_, *Xs]), member_of(X, Xs))
backward(includes(graph(Triples), Triple), member_of(Triple, Triples))
forward(found(T), quoted(G), includes(G, T))
forward(witness(X, W), quoted(X))
