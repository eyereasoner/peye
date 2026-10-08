# Match a structured description without treating "good" as a global property.

from peye import *

fact(description('joe', ['good', 'cobbler']))
fact(description('jane', ['good', 'carpenter']))
fact(description('sam', ['novice', 'cobbler']))
implies(description(Person, ['good', Trade]), good_at(Person, Trade))
implies(description(Person, ['good', Trade]), classified_as(Person, Trade))
query(good_at(Person, Trade))
query(classified_as(Person, Trade))
