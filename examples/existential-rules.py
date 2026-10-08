# Existential rules: a rule whose conclusion mentions something its body never
# names says that such a thing exists. peye names each such unknown with a
# Skolem atom: one per activation of the rule, the same one when the same
# activation comes back, and never one that could stand for anything else.

from peye import *

# Every person has a parent, even when nobody knows who. Ann and Bob each get
# a parent of their own, so they do not become siblings by accident.
fact(person('ann'), person('bob'))
forward(has_parent(X, P), person(X))

# Dan and Fay share a parent the data names, so they are siblings.
fact(has_parent('dan', 'eve'), has_parent('fay', 'eve'))
forward(sibling(X, Y), has_parent(X, P), has_parent(Y, P), not_identical(X, Y))

# A customer who ordered something has an invoice. Carl ordered twice, but
# the conclusion is the same both times, so one invoice is enough.
fact(ordered('carl', 'lamp'), ordered('carl', 'desk'), ordered('dora', 'chair'))
forward(invoice_for(C, I), ordered(C, Item))

# Every invoice is sent. A rule can use an invented invoice like any other
# value; whenever the invoice rule meets Carl's orders again, it gives back
# the same invoice, so reasoning comes to an end.
forward(sent(I), invoice_for(C, I))

# Colleagues meet: one meeting, shared by the three conclusions about it.
fact(colleagues('ann', 'dora'))
forward(meeting(M) & attends(M, X) & attends(M, Y), colleagues(X, Y))
