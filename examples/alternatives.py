# Alternative clauses, disjunction and once provide goal-directed choices.

from peye import *

fact(train('paris', 'brussels'))
fact(bus('paris', 'lille'))
backward(route(From, To), train(From, To))
backward(route(From, To), bus(From, To))
query(route('paris', To))
query(train('paris', 'brussels') | bus('paris', 'lille'))
query(once(route('paris', To)))
