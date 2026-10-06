# A graph of expression nodes evaluated recursively, then used by a forward rule.

from peye import *

fact(literal('n2', 2))
fact(literal('n3', 3))
fact(literal('n10', 10))
fact(literal('n4', 4))
fact(expression('product', 'mul', 'n2', 'n3'))
fact(expression('difference', 'sub', 'n10', 'n4'))
fact(expression('total', 'add', 'product', 'difference'))
fact(root('example', 'total'))
backward(value(Node, Value), literal(Node, Value))
backward(
    value(Node, Value),
    expression(Node, Operation, Left, Right),
    value(Left, L),
    value(Right, R),
    calculate(Operation, L, R, Value),
)
backward(calculate('add', L, R, Value), is_(Value, L + R))
backward(calculate('sub', L, R, Value), is_(Value, L - R))
backward(calculate('mul', L, R, Value), is_(Value, L * R))
forward(result(Name, Value), root(Name, Node), value(Node, Value))
query(result(Name, Value))
