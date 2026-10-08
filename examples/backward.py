# A forward body invokes
# a backward definition that tests an arithmetic primitive.

from peye import *

implied_by(more_interesting(X, Y), X > Y)
implies(more_interesting(5, 3), indeed_more_interesting(5, 3))
