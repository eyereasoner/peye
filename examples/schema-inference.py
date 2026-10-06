# Subclass and subproperty closure propagates types and relationships.

from peye import *

fact(subclass('cat', 'mammal'))
fact(subclass('mammal', 'animal'))
fact(subproperty('parent_of', 'related_to'))
fact(domain('parent_of', 'person'))
fact(codomain('parent_of', 'person'))
fact(type('koko', 'cat'))
fact(triple('alice', 'parent_of', 'bob'))
forward(subclass(A, C), subclass(A, B), subclass(B, C))
forward(type(X, B), type(X, A), subclass(A, B))
forward(triple(S, Q, O), triple(S, P, O), subproperty(P, Q))
forward(type(S, Class), triple(S, P, _), domain(P, Class))
forward(type(O, Class), triple(_, P, O), codomain(P, Class))
