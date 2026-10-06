# Deep taxonomy: one individual, and a chain of 10 levels in which every level
# also branches into two siblings that lead nowhere. Reaching n10 means
# following the single productive branch the whole way down.
# See https://web.archive.org/web/20101025233525/http://www.ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf

from peye import *

fact(type('ind', 'n0'))
backward(type(X, 'n1'), type(X, 'n0'))
backward(type(X, 'i1'), type(X, 'n0'))
backward(type(X, 'j1'), type(X, 'n0'))
backward(type(X, 'n2'), type(X, 'n1'))
backward(type(X, 'i2'), type(X, 'n1'))
backward(type(X, 'j2'), type(X, 'n1'))
backward(type(X, 'n3'), type(X, 'n2'))
backward(type(X, 'i3'), type(X, 'n2'))
backward(type(X, 'j3'), type(X, 'n2'))
backward(type(X, 'n4'), type(X, 'n3'))
backward(type(X, 'i4'), type(X, 'n3'))
backward(type(X, 'j4'), type(X, 'n3'))
backward(type(X, 'n5'), type(X, 'n4'))
backward(type(X, 'i5'), type(X, 'n4'))
backward(type(X, 'j5'), type(X, 'n4'))
backward(type(X, 'n6'), type(X, 'n5'))
backward(type(X, 'i6'), type(X, 'n5'))
backward(type(X, 'j6'), type(X, 'n5'))
backward(type(X, 'n7'), type(X, 'n6'))
backward(type(X, 'i7'), type(X, 'n6'))
backward(type(X, 'j7'), type(X, 'n6'))
backward(type(X, 'n8'), type(X, 'n7'))
backward(type(X, 'i8'), type(X, 'n7'))
backward(type(X, 'j8'), type(X, 'n7'))
backward(type(X, 'n9'), type(X, 'n8'))
backward(type(X, 'i9'), type(X, 'n8'))
backward(type(X, 'j9'), type(X, 'n8'))
backward(type(X, 'n10'), type(X, 'n9'))
backward(type(X, 'i10'), type(X, 'n9'))
backward(type(X, 'j10'), type(X, 'n9'))
query(type(X, 'n10'))
