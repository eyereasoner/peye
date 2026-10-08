type('socrates', 'mortal')
type('socrates', 'human')

clause(1, fact(type('socrates', 'human')))
clause(2, fact(subclass_of('human', 'mortal')))
clause(3, implies(type(S, A) & subclass_of(A, B), type(S, B)))

step(type('socrates', 'mortal'), clause(3), {'S': 'socrates', 'B': 'mortal', 'A': 'human'}, [type('socrates', 'human'), subclass_of('human', 'mortal')])
step(type('socrates', 'human'), clause(1), {}, [])
step(subclass_of('human', 'mortal'), clause(2), {}, [])
