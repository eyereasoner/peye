# Enumerate paths in an acyclic weighted graph, then select minimum costs.

from peye import *

fact(edge('a', 'b', 4))
fact(edge('a', 'c', 2))
fact(edge('c', 'b', 1))
fact(edge('b', 'd', 3))
fact(edge('c', 'd', 8))
forward(path(X, Y, Cost), edge(X, Y, Cost))
forward(path(X, Z, Cost), path(X, Y, Before), edge(Y, Z, Weight), is_(Cost, Before + Weight))
backward(cheaper(X, Y, Cost), path(X, Y, Other), Other < Cost)
forward(shortest(X, Y, Cost), path(X, Y, Cost), ~cheaper(X, Y, Cost))
query(shortest('a', 'd', Cost))
