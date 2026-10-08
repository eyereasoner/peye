# Materialize every reachable pair in a graph containing a cycle.

from peye import *

fact(edge('a', 'b'))
fact(edge('b', 'c'))
fact(edge('c', 'a'))
fact(edge('c', 'd'))
implies(edge(X, Y), reachable(X, Y))
implies(reachable(X, Y) & edge(Y, Z), reachable(X, Z))
