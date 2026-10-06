# Materialize every reachable pair in a graph containing a cycle.

from peye import *

fact(edge('a', 'b'))
fact(edge('b', 'c'))
fact(edge('c', 'a'))
fact(edge('c', 'd'))
forward(reachable(X, Y), edge(X, Y))
forward(reachable(X, Z), reachable(X, Y), edge(Y, Z))
