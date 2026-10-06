# Solving polynomial equations of degree 4
# original code from http://alain.colmerauer.free.fr/alcol/ArchivesPublications/Equation4/Equation4.pdf
#
# A polynomial is the list of its complex coefficients, highest degree first,
# and a complex number is a pair [Re, Im]. Degrees 1 and 2 are solved
# directly, degree 3 by Cardan's formula and degree 4 by Lagrange's method,
# which reduces it to a cubic. The roots are floating-point approximations.
# Colmerauer's comments are kept in their original French.

from peye import *

# Liste des racines dun polynome
backward(roots(P, L), findall(Z, racine(P, Z), L))

# Racine dun polynome
backward(racine([A, B], Z), est(Z, moins(B // A)))
backward(
    racine([A, B, C], Z),
    est(P, B // fois([2, 0], A)),
    est(Q, C // A),
    est(Z, add(moins(P), fois('racarreeun', racine(2, moins(carre(P), Q))))),
)
backward(racine([A, B, C, D], Z), racine_cubique([A, B, C, D], Z))
backward(
    racine([A, B, C, D, E], Zp),
    est(T, B // fois([-4, 0], A)),
    est(P, add(fois([6, 0], fois(A, carre(T))), add(fois([3, 0], fois(B, T)), C)) // A),
    est(Q, add(fois(fois([4, 0], A), cube(T)), add(fois(fois([3, 0], B), carre(T)), add(fois(fois([2, 0], C), T), D))) // A),
    est(R, add(fois(A, pquatre(T)), add(fois(B, cube(T)), add(fois(C, carre(T)), add(fois(D, T), E)))) // A),
    solutionLagrange(P, Q, R, Z),
    est(Zp, add(Z, T)),
)

# Racine dun polynome du troisieme degre. Lagrange's method collects these
# roots, so they get a predicate of their own: the collection then depends only
# on lower degrees, never on itself.
backward(
    racine_cubique([A, B, C, D], Zp),
    est(T, B // fois([-3, 0], A)),
    est(P, add(fois([3, 0], fois(A, carre(T))), add(fois([2, 0], fois(B, T)), C)) // A),
    est(Q, add(fois(A, cube(T)), add(fois(B, carre(T)), add(fois(C, T), D))) // A),
    solutionCardan(P, Q, Z),
    est(Zp, add(Z, T)),
)

# Polynome a partir de ses racines
backward(polynome(L, P), polynome(L, [[1, 0]], P))

fact(polynome([], P0, P0))
backward(
    polynome([X, *L], P0, P4),
    conc(P0, [[0, 0]], P1),
    est(Xp, moins(X)),
    foisl(Xp, P0, P2),
    addll(P1, [[0, 0], *P2], P3),
    polynome(L, P3, P4),
)

fact(conc([], L, L))
backward(conc([E, *L], Lp, [E, *Lpp]), conc(L, Lp, Lpp))

fact(foisl(_, [], []))
backward(foisl(X, [Y, *L], [Z, *Lp]), est(Z, fois(X, Y)), foisl(X, L, Lp))

fact(addll([], [], []))
backward(addll([X, *L], [Y, *Lp], [Z, *Lpp]), est(Z, add(X, Y)), addll(L, Lp, Lpp))

# Solution de lequation du troisieme degre selon Cardan
backward(solutionCardan(P, Q, Z), nul(P), est(Z, fois('racubiqueun', racine(3, moins(Q)))))
backward(
    solutionCardan(Pp, Qp, Z),
    nonnul(Pp),
    est(P, Pp // [3, 0]),
    est(Q, Qp // [2, 0]),
    est(Raccubique, fois('racubiqueun', racine(3, moins(racine(2, add(carre(Q), cube(P))), Q)))),
    est(Z, moins(Raccubique, P // Raccubique)),
)

# Solutions de lequation du quatrieme degre selon Lagrange
backward(
    solutionLagrange(P, Q, R, Z),
    est(A, [1, 0]),
    est(B, fois([2, 0], P)),
    est(C, moins(carre(P), fois([4, 0], R))),
    est(D, moins(carre(Q))),
    findall(Y, racine_cubique([A, B, C, D], Y), [Y1, Y2, Y3]),
    est(Y1p, racine(2, Y1)),
    est(Y2p, racine(2, Y2)),
    est(Y3p, racine(2, Y3)),
    est(U1, add(Y1p, add(Y2p, Y3p)) // [2, 0]),
    est(U2, moins(Y1p, add(Y2p, Y3p)) // [2, 0]),
    est(U3, moins(Y3p, add(Y1p, Y2p)) // [2, 0]),
    est(U4, moins(Y2p, add(Y1p, Y3p)) // [2, 0]),
    est(V1, fois(U1, fois(U2, U3))),
    est(V2, fois(U1, fois(U2, U4))),
    est(V3, fois(U1, fois(U3, U4))),
    est(V4, fois(U2, fois(U3, U4))),
    epsilon(E, moins(add(V1, add(V2, add(V3, V4)))), Q),
    dans(U, [U1, U2, U3, U4]),
    est(Z, fois(E, U)),
)

backward(epsilon([1, 0], _, Q), nul(Q))
backward(epsilon(E, S, Q), nonnul(Q), est(E, S // Q))

fact(dans(U, [U, *_]))
backward(dans(U, [_, *L]), dans(U, L))

# Valeurs de lenchainement des operations sur les complexes
# The original builds each call with =.. and runs it; one clause per operation
# says the same thing directly.
backward(est(Z, Z), unify(Z, [_, _]))
backward(est(Z, 'racarreeun'), racarreeun(Z))
backward(est(Z, 'racubiqueun'), racubiqueun(Z))
backward(est(Z, moins(X)), est(Xp, X), moins(Xp, Z))
backward(est(Z, carre(X)), est(Xp, X), carre(Xp, Z))
backward(est(Z, cube(X)), est(Xp, X), cube(Xp, Z))
backward(est(Z, pquatre(X)), est(Xp, X), pquatre(Xp, Z))
backward(est(Z, moins(X, Y)), est(Xp, X), est(Yp, Y), moins(Xp, Yp, Z))
backward(est(Z, add(X, Y)), est(Xp, X), est(Yp, Y), add(Xp, Yp, Z))
backward(est(Z, fois(X, Y)), est(Xp, X), est(Yp, Y), fois(Xp, Yp, Z))
backward(est(Z, X // Y), est(Xp, X), est(Yp, Y), div(Xp, Yp, Z))
backward(est(Z, racine(N, X)), est(Xp, X), racine(N, Xp, Z))

# Operations sur les complexes
backward(moins([X1, X2], [Y1, Y2]), is_(Y1, -X1), is_(Y2, -X2))

backward(moins([X1, X2], [Y1, Y2], [Z1, Z2]), is_(Z1, X1 - Y1), is_(Z2, X2 - Y2))

backward(add([X1, X2], [Y1, Y2], [Z1, Z2]), is_(Z1, X1 + Y1), is_(Z2, X2 + Y2))

backward(fois([X1, X2], [Y1, Y2], [Z1, Z2]), is_(Z1, X1 * Y1 - X2 * Y2), is_(Z2, X1 * Y2 + X2 * Y1))

backward(
    invers([X1, X2], [Y1, Y2]),
    is_(Y1, X1 / (X1 ** 2 + X2 ** 2)),
    is_(Y2, -X2 / (X1 ** 2 + X2 ** 2)),
)

backward(div(X, Y, Z), invers(Y, Yp), fois(X, Yp, Z))

backward(carre(X, Y), fois(X, X, Y))

backward(cube(X, Y), carre(X, Xp), fois(X, Xp, Y))

backward(pquatre(X, Y), carre(X, Xp), carre(Xp, Y))

fact(racarreeun([1, 0]))
fact(racarreeun([-1, 0]))

fact(racubiqueun([1, 0]))
backward(racubiqueun([X, Y]), is_(X, -1 / 2), is_(Y, sqrt(3) / 2))
backward(racubiqueun([X, Y]), is_(X, -1 / 2), is_(Y, -sqrt(3) / 2))

backward(racine(_, X, [0, 0]), nul(X))
backward(
    racine(N, X, Y),
    nonnul(X),
    polaire(X, [R, T]),
    root(N, R, Rp),
    is_(Tp, T / N),
    cartesien([Rp, Tp], Y),
)

backward(root(N, X, Y), is_(Y, exp(log(X) / N)))

backward(
    polaire([X, Y], [R, Tp]),
    is_(R, sqrt(X ** 2 + Y ** 2)),
    is_(T, acos(abs(X) / R)),
    cadran(X, Y, T, Tp),
)

backward(cadran(X, Y, T, Tp), X >= 0, Y >= 0, unify(Tp, T))
backward(cadran(X, Y, T, Tp), X < 0, Y >= 0, is_(Tp, pi - T))
backward(cadran(X, Y, T, Tp), X < 0, Y < 0, is_(Tp, T + pi))
backward(cadran(X, Y, T, Tp), X >= 0, Y < 0, is_(Tp, 2 * pi - T))

backward(cartesien([R, T], [X1, X2]), is_(X1, R * cos(T)), is_(X2, R * sin(T)))

# Problemes de zero
# A complex number is zero when both parts compare equal to 0, which covers 0,
# 0.0 and -0.0; the two tests exclude each other without a cut.
backward(nul([X, Y]), eq(X, 0), eq(Y, 0))

backward(nonnul([X, _]), ne(X, 0))
backward(nonnul([X, Y]), eq(X, 0), ne(Y, 0))

# query
query(roots([[1, 0], [-10, 0], [35, 0], [-50, 0], [24, 0]], _))
query(roots([[1, 0], [-9, -5], [14, 33], [24, -44], [-26, 0]], _))
