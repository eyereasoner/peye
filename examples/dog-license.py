# Count owned dogs before applying a licensing threshold.

from peye import *

fact(owns('alice', 'dog1'))
fact(owns('alice', 'dog2'))
fact(owns('alice', 'dog3'))
fact(owns('alice', 'dog4'))
fact(owns('alice', 'dog5'))
fact(owns('bob', 'dog6'))
fact(owns('bob', 'dog7'))
fact(owner('alice'))
fact(owner('bob'))
fact(length([], 0))
backward(length([_, *Xs], N), length(Xs, Before), is_(N, Before + 1))
forward(dog_count(Owner, N), owner(Owner), findall(Dog, owns(Owner, Dog), Dogs), length(Dogs, N))
forward(requires(Owner, 'dog_license'), dog_count(Owner, N), N > 4)
