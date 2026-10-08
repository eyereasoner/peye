# Subclass and subproperty closure propagates types and relationships.

from peye import *

fact(subclass('cat', 'mammal'))
fact(subclass('mammal', 'animal'))
fact(subproperty('parent_of', 'related_to'))
fact(domain('parent_of', 'person'))
fact(codomain('parent_of', 'person'))
fact(type('koko', 'cat'))
fact(triple('alice', 'parent_of', 'bob'))
implies(subclass(A, B) & subclass(B, C), subclass(A, C))
implies(type(X, A) & subclass(A, B), type(X, B))
implies(triple(S, P, O) & subproperty(P, Q), triple(S, Q, O))
implies(triple(S, P, _) & domain(P, Class), type(S, Class))
implies(triple(_, P, O) & codomain(P, Class), type(O, Class))
