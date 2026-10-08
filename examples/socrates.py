# Class membership follows a class hierarchy: Socrates is human, and every
# human is mortal, so the subclass rule concludes that Socrates is mortal.

from peye import *

fact(type('socrates', 'human'))
fact(subclass_of('human', 'mortal'))
implies(type(S, A) & subclass_of(A, B), type(S, B))
# The query reports every class membership, asserted as well as derived.
query(type(X, Y))
