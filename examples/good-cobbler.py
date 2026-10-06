# Match a structured description without treating "good" as a global property.

from peye import *

fact(description('joe', ['good', 'cobbler']))
fact(description('jane', ['good', 'carpenter']))
fact(description('sam', ['novice', 'cobbler']))
forward(good_at(Person, Trade), description(Person, ['good', Trade]))
forward(classified_as(Person, Trade), description(Person, ['good', Trade]))
query(good_at(Person, Trade))
query(classified_as(Person, Trade))
