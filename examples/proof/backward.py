indeed_more_interesting(5, 3)

clause(1, implied_by(more_interesting(X, Y), X > Y))
clause(2, implies(more_interesting(5, 3), indeed_more_interesting(5, 3)))

step(indeed_more_interesting(5, 3), clause(2), {}, [more_interesting(5, 3)])
step(more_interesting(5, 3), clause(1), {'X': 5, 'Y': 3}, [5 > 3])
step(5 > 3, 'builtin', {}, [])
