# Enumerate paths in an acyclic weighted graph, then select minimum costs.

from peye import *

fact(edge('a', 'b', 4))
fact(edge('a', 'c', 2))
fact(edge('c', 'b', 1))
fact(edge('b', 'd', 3))
fact(edge('c', 'd', 8))
implies(edge(X, Y, Cost), path(X, Y, Cost))
implies(path(X, Y, Before) & edge(Y, Z, Weight) & is_(Cost, Before + Weight), path(X, Z, Cost))
implied_by(cheaper(X, Y, Cost), path(X, Y, Other) & (Other < Cost))
implies(path(X, Y, Cost) & ~cheaper(X, Y, Cost), shortest(X, Y, Cost))
query(shortest('a', 'd', Cost))
