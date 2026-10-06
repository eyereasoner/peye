# A forward body invokes
# a backward definition that tests an arithmetic primitive.

from peye import *

backward(more_interesting(X, Y), X > Y)
forward(indeed_more_interesting(5, 3), more_interesting(5, 3))
