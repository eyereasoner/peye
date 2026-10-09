# Deep taxonomy: one individual, and a chain of 10 levels in which every level
# also branches into two siblings that lead nowhere. Reaching n10 means
# following the single productive branch the whole way down. A loop states
# the three rules of every level.
# See https://web.archive.org/web/20101025233525/http://www.ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf

from peye import *

fact(type('ind', 'n0'))
for level in range(1, 11):
    implied_by(type(X, f'n{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'i{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'j{level}'), type(X, f'n{level - 1}'))
query(type(X, 'n10'))
