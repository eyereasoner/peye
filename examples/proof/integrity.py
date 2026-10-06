'false'

clause(2, fact(account('bob', -5)))
clause(3, forward('false', account(Owner, Balance), Balance < 0))

step('false', rule(3), {'Owner': 'bob', 'Balance': -5}, [account('bob', -5), -5 < 0])
step(account('bob', -5), fact(2), {}, [])
step(-5 < 0, 'builtin', {}, [])
