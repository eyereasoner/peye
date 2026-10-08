'false'

clause(2, fact(account('bob', -5)))
clause(3, implies(account(Owner, Balance) & (Balance < 0), 'false'))

step('false', clause(3), {'Owner': 'bob', 'Balance': -5}, [account('bob', -5), -5 < 0])
step(account('bob', -5), clause(2), {}, [])
step(-5 < 0, 'builtin', {}, [])
