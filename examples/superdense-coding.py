# Superdense coding using discrete quantum computing
#
# See https://arxiv.org/pdf/1101.3764.pdf and https://arxiv.org/pdf/1010.2929.pdf
#
# Discrete quantum theory is obtained by instantiating the mathematical framework
# of Hilbert spaces with a finite field instead of the field of complex numbers.
# This instantiation collapses much the structure of actual quantum mechanics but
# retains several of its distinguishing characteristics including the notions of
# superposition, interference, and entanglement. Furthermore, discrete quantum
# theory excludes local hidden variable models, has a no-cloning theorem, and can
# express natural counterparts of quantum information protocols such as superdense
# coding and teleportation.
#
# Surprisingly discrete quantum computing is identical to conventional logic
# programming except for a small twist that is responsible for all the
# "quantum-ness". The twist occurs when merging sets of answers computed by
# several alternatives: the answers are combined using an exclusive version of
# logical disjunction. In other words, the two branches of a choice junction
# exhibit an interference effect: an answer is produced from the junction if it
# occurs in one or the other branch but not both.
#
# Here that merge is a count: every way Alice's message N can reach Bob as M is
# collected, and the pair survives when the number of ways is odd. The parity
# depends on all the ways, so the certificate names each collection as an
# obligation.

from peye import *

# |R) = |0, 0) + |1, 1)
fact(r('false', 'false'))
fact(r('true', 'true'))

# |S) = |0, 1) + |1, 0)
fact(s('false', 'true'))
fact(s('true', 'false'))

# |U) = |0, 0) + |1, 0) + |1, 1)
fact(u('false', 'false'))
fact(u('true', 'false'))
fact(u('true', 'true'))

# |V ) = |0, 0) + |0, 1) + |1, 0)
fact(v('false', 'false'))
fact(v('false', 'true'))
fact(v('true', 'false'))

# ID |0) = |0)
fact(id('false', 'false'))
# ID |1) = |1)
fact(id('true', 'true'))

# G |0) = |1)
fact(g('false', 'true'))
# G |1) = |0)
fact(g('true', 'false'))

# K |0) = |0)
fact(k('false', 'false'))
# K |1) = |0) + |1)
fact(k('true', 'false'))
fact(k('true', 'true'))

# KG
implied_by(kg(X, Y), g(X, Z) & k(Z, Y))

# GK
implied_by(gk(X, Y), k(X, Z) & g(Z, Y))

# alice
implied_by(alice(0, [X, Y]), id(X, Y))
implied_by(alice(1, [X, Y]), g(X, Y))
implied_by(alice(2, [X, Y]), k(X, Y))
implied_by(alice(3, [X, Y]), kg(X, Y))

# bob
implied_by(bob([X, Y], 0), gk(X, Y))
implied_by(bob([X, Y], 1), k(X, Y))
implied_by(bob([X, Y], 2), g(X, Y))
implied_by(bob([X, Y], 3), id(X, Y))

# One way for Alice's message N to arrive as Bob's M: the shared pair |R), her
# operation on her half, and his measurement of both halves.
implied_by(path(N, M, [X, Y, B]), r(X, Y) & alice(N, [X, B]) & bob([B, Y], M))

fact(message(0))
fact(message(1))
fact(message(2))
fact(message(3))

fact(odd([_]))
implied_by(odd([_, _, *T]), odd(T))

# superdense coding: the pairs reached an odd number of times
implies(message(N) & message(M) & findall(Path, path(N, M, Path), Paths) & odd(Paths), sdcoding(N, M))

# query
query(sdcoding(_, _))
