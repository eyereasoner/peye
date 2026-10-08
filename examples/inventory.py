# Collection runs after line totals have been materialized.

from peye import *

fact(item('apple', 3, 2))
fact(item('pear', 4, 3))
fact(item('plum', 2, 5))
implies(item(Name, Quantity, Price) & is_(Total, Quantity * Price), line_total(Name, Total))
fact(sum([], 0))
implied_by(sum([X, *Xs], Total), sum(Xs, Rest) & is_(Total, X + Rest))
implies(findall(Amount, line_total(_, Amount), Amounts) & sum(Amounts, Total), invoice(Total))
query(invoice(Total))
