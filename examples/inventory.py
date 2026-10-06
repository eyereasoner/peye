# Collection runs after line totals have been materialized.

from peye import *

fact(item('apple', 3, 2))
fact(item('pear', 4, 3))
fact(item('plum', 2, 5))
forward(line_total(Name, Total), item(Name, Quantity, Price), is_(Total, Quantity * Price))
fact(sum([], 0))
backward(sum([X, *Xs], Total), sum(Xs, Rest), is_(Total, X + Rest))
forward(invoice(Total), findall(Amount, line_total(_, Amount), Amounts), sum(Amounts, Total))
query(invoice(Total))
