# Deep taxonomy: one individual, and a chain of 10 levels in which every level
# also branches into two siblings that lead nowhere. Reaching n10 means
# following the single productive branch the whole way down.
# See https://web.archive.org/web/20101025233525/http://www.ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf

from peye import *

fact(type('ind', 'n0'))
implied_by(type(X, 'n1'), type(X, 'n0'))
implied_by(type(X, 'i1'), type(X, 'n0'))
implied_by(type(X, 'j1'), type(X, 'n0'))
implied_by(type(X, 'n2'), type(X, 'n1'))
implied_by(type(X, 'i2'), type(X, 'n1'))
implied_by(type(X, 'j2'), type(X, 'n1'))
implied_by(type(X, 'n3'), type(X, 'n2'))
implied_by(type(X, 'i3'), type(X, 'n2'))
implied_by(type(X, 'j3'), type(X, 'n2'))
implied_by(type(X, 'n4'), type(X, 'n3'))
implied_by(type(X, 'i4'), type(X, 'n3'))
implied_by(type(X, 'j4'), type(X, 'n3'))
implied_by(type(X, 'n5'), type(X, 'n4'))
implied_by(type(X, 'i5'), type(X, 'n4'))
implied_by(type(X, 'j5'), type(X, 'n4'))
implied_by(type(X, 'n6'), type(X, 'n5'))
implied_by(type(X, 'i6'), type(X, 'n5'))
implied_by(type(X, 'j6'), type(X, 'n5'))
implied_by(type(X, 'n7'), type(X, 'n6'))
implied_by(type(X, 'i7'), type(X, 'n6'))
implied_by(type(X, 'j7'), type(X, 'n6'))
implied_by(type(X, 'n8'), type(X, 'n7'))
implied_by(type(X, 'i8'), type(X, 'n7'))
implied_by(type(X, 'j8'), type(X, 'n7'))
implied_by(type(X, 'n9'), type(X, 'n8'))
implied_by(type(X, 'i9'), type(X, 'n8'))
implied_by(type(X, 'j9'), type(X, 'n8'))
implied_by(type(X, 'n10'), type(X, 'n9'))
implied_by(type(X, 'i10'), type(X, 'n9'))
implied_by(type(X, 'j10'), type(X, 'n9'))
query(type(X, 'n10'))
