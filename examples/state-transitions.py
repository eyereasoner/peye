# An ordered event log defines a relation between successive account states.

from peye import *

fact(opening_balance(100))
fact(event(1, 'deposit', 25))
fact(event(2, 'withdraw', 40))
fact(event(3, 'withdraw', 20))
implied_by(balance(0, Amount), opening_balance(Amount))
implied_by(
    balance(N, Amount),
    (N > 0)
    & event(N, 'deposit', Value)
    & is_(Before, N - 1)
    & balance(Before, Previous)
    & is_(Amount, Previous + Value),
)
implied_by(
    balance(N, Amount),
    (N > 0)
    & event(N, 'withdraw', Value)
    & is_(Before, N - 1)
    & balance(Before, Previous)
    & is_(Amount, Previous - Value),
)
query(balance(3, Amount))
