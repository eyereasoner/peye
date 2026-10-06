# Symbolic natural numbers: zero, s(zero), s(s(zero)), ...
# Addition also works backward to enumerate ways of splitting a known sum.

from peye import *

fact(add(A, 'zero', A))
backward(add(A, s(B), s(C)), add(A, B, C))
fact(multiply(_, 'zero', 'zero'))
backward(multiply(A, s(B), C), multiply(A, B, D), add(A, D, C))
fact(factorial('zero', s('zero')))
backward(factorial(s(N), F), factorial(N, Before), multiply(s(N), Before, F))
# Addition run backward enumerates every way of splitting a known sum.
query(add(A, B, s(s(s('zero')))))
# One derivation chains all three relations: (1*2)+3 = 5, then 5! = 120.
query(
    multiply(s('zero'), s(s('zero')), Product),
    add(Product, s(s(s('zero'))), Sum),
    factorial(Sum, Factorial),
)
