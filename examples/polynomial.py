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
implied_by(roots(P, L), findall(Z, racine(P, Z), L))

# Racine dun polynome
implied_by(racine([A, B], Z), est(Z, moins(B // A)))
implied_by(
    racine([A, B, C], Z),
    est(P, B // fois([2, 0], A))
    & est(Q, C // A)
    & est(Z, add(moins(P), fois('racarreeun', racine(2, moins(carre(P), Q))))),
)
implied_by(racine([A, B, C, D], Z), racine_cubique([A, B, C, D], Z))
implied_by(
    racine([A, B, C, D, E], Zp),
    est(T, B // fois([-4, 0], A))
    & est(P, add(fois([6, 0], fois(A, carre(T))), add(fois([3, 0], fois(B, T)), C)) // A)
    & est(Q, add(fois(fois([4, 0], A), cube(T)), add(fois(fois([3, 0], B), carre(T)), add(fois(fois([2, 0], C), T), D))) // A)
    & est(R, add(fois(A, pquatre(T)), add(fois(B, cube(T)), add(fois(C, carre(T)), add(fois(D, T), E)))) // A)
    & solutionLagrange(P, Q, R, Z)
    & est(Zp, add(Z, T)),
)

# Racine dun polynome du troisieme degre. Lagrange's method collects these
# roots, so they get a predicate of their own: the collection then depends only
# on lower degrees, never on itself.
implied_by(
    racine_cubique([A, B, C, D], Zp),
    est(T, B // fois([-3, 0], A))
    & est(P, add(fois([3, 0], fois(A, carre(T))), add(fois([2, 0], fois(B, T)), C)) // A)
    & est(Q, add(fois(A, cube(T)), add(fois(B, carre(T)), add(fois(C, T), D))) // A)
    & solutionCardan(P, Q, Z)
    & est(Zp, add(Z, T)),
)

# Polynome a partir de ses racines
implied_by(polynome(L, P), polynome(L, [[1, 0]], P))

fact(polynome([], P0, P0))
implied_by(
    polynome([X, *L], P0, P4),
    conc(P0, [[0, 0]], P1)
    & est(Xp, moins(X))
    & foisl(Xp, P0, P2)
    & addll(P1, [[0, 0], *P2], P3)
    & polynome(L, P3, P4),
)

fact(conc([], L, L))
implied_by(conc([E, *L], Lp, [E, *Lpp]), conc(L, Lp, Lpp))

fact(foisl(_, [], []))
implied_by(foisl(X, [Y, *L], [Z, *Lp]), est(Z, fois(X, Y)) & foisl(X, L, Lp))

fact(addll([], [], []))
implied_by(addll([X, *L], [Y, *Lp], [Z, *Lpp]), est(Z, add(X, Y)) & addll(L, Lp, Lpp))

# Solution de lequation du troisieme degre selon Cardan
implied_by(solutionCardan(P, Q, Z), nul(P) & est(Z, fois('racubiqueun', racine(3, moins(Q)))))
implied_by(
    solutionCardan(Pp, Qp, Z),
    nonnul(Pp)
    & est(P, Pp // [3, 0])
    & est(Q, Qp // [2, 0])
    & est(Raccubique, fois('racubiqueun', racine(3, moins(racine(2, add(carre(Q), cube(P))), Q))))
    & est(Z, moins(Raccubique, P // Raccubique)),
)

# Solutions de lequation du quatrieme degre selon Lagrange
implied_by(
    solutionLagrange(P, Q, R, Z),
    est(A, [1, 0])
    & est(B, fois([2, 0], P))
    & est(C, moins(carre(P), fois([4, 0], R)))
    & est(D, moins(carre(Q)))
    & findall(Y, racine_cubique([A, B, C, D], Y), [Y1, Y2, Y3])
    & est(Y1p, racine(2, Y1))
    & est(Y2p, racine(2, Y2))
    & est(Y3p, racine(2, Y3))
    & est(U1, add(Y1p, add(Y2p, Y3p)) // [2, 0])
    & est(U2, moins(Y1p, add(Y2p, Y3p)) // [2, 0])
    & est(U3, moins(Y3p, add(Y1p, Y2p)) // [2, 0])
    & est(U4, moins(Y2p, add(Y1p, Y3p)) // [2, 0])
    & est(V1, fois(U1, fois(U2, U3)))
    & est(V2, fois(U1, fois(U2, U4)))
    & est(V3, fois(U1, fois(U3, U4)))
    & est(V4, fois(U2, fois(U3, U4)))
    & epsilon(E, moins(add(V1, add(V2, add(V3, V4)))), Q)
    & dans(U, [U1, U2, U3, U4])
    & est(Z, fois(E, U)),
)

implied_by(epsilon([1, 0], _, Q), nul(Q))
implied_by(epsilon(E, S, Q), nonnul(Q) & est(E, S // Q))

fact(dans(U, [U, *_]))
implied_by(dans(U, [_, *L]), dans(U, L))

# Valeurs de lenchainement des operations sur les complexes
# The original builds each call with =.. and runs it; one clause per operation
# says the same thing directly.
implied_by(est(Z, Z), unify(Z, [_, _]))
implied_by(est(Z, 'racarreeun'), racarreeun(Z))
implied_by(est(Z, 'racubiqueun'), racubiqueun(Z))
implied_by(est(Z, moins(X)), est(Xp, X) & moins(Xp, Z))
implied_by(est(Z, carre(X)), est(Xp, X) & carre(Xp, Z))
implied_by(est(Z, cube(X)), est(Xp, X) & cube(Xp, Z))
implied_by(est(Z, pquatre(X)), est(Xp, X) & pquatre(Xp, Z))
implied_by(est(Z, moins(X, Y)), est(Xp, X) & est(Yp, Y) & moins(Xp, Yp, Z))
implied_by(est(Z, add(X, Y)), est(Xp, X) & est(Yp, Y) & add(Xp, Yp, Z))
implied_by(est(Z, fois(X, Y)), est(Xp, X) & est(Yp, Y) & fois(Xp, Yp, Z))
implied_by(est(Z, X // Y), est(Xp, X) & est(Yp, Y) & div(Xp, Yp, Z))
implied_by(est(Z, racine(N, X)), est(Xp, X) & racine(N, Xp, Z))

# Operations sur les complexes
implied_by(moins([X1, X2], [Y1, Y2]), is_(Y1, -X1) & is_(Y2, -X2))

implied_by(moins([X1, X2], [Y1, Y2], [Z1, Z2]), is_(Z1, X1 - Y1) & is_(Z2, X2 - Y2))

implied_by(add([X1, X2], [Y1, Y2], [Z1, Z2]), is_(Z1, X1 + Y1) & is_(Z2, X2 + Y2))

implied_by(fois([X1, X2], [Y1, Y2], [Z1, Z2]), is_(Z1, X1 * Y1 - X2 * Y2) & is_(Z2, X1 * Y2 + X2 * Y1))

implied_by(
    invers([X1, X2], [Y1, Y2]),
    is_(Y1, X1 / (X1 ** 2 + X2 ** 2))
    & is_(Y2, -X2 / (X1 ** 2 + X2 ** 2)),
)

implied_by(div(X, Y, Z), invers(Y, Yp) & fois(X, Yp, Z))

implied_by(carre(X, Y), fois(X, X, Y))

implied_by(cube(X, Y), carre(X, Xp) & fois(X, Xp, Y))

implied_by(pquatre(X, Y), carre(X, Xp) & carre(Xp, Y))

fact(racarreeun([1, 0]))
fact(racarreeun([-1, 0]))

fact(racubiqueun([1, 0]))
implied_by(racubiqueun([X, Y]), is_(X, -1 / 2) & is_(Y, sqrt(3) / 2))
implied_by(racubiqueun([X, Y]), is_(X, -1 / 2) & is_(Y, -sqrt(3) / 2))

implied_by(racine(_, X, [0, 0]), nul(X))
implied_by(
    racine(N, X, Y),
    nonnul(X)
    & polaire(X, [R, T])
    & root(N, R, Rp)
    & is_(Tp, T / N)
    & cartesien([Rp, Tp], Y),
)

implied_by(root(N, X, Y), is_(Y, exp(log(X) / N)))

implied_by(
    polaire([X, Y], [R, Tp]),
    is_(R, sqrt(X ** 2 + Y ** 2))
    & is_(T, acos(abs(X) / R))
    & cadran(X, Y, T, Tp),
)

implied_by(cadran(X, Y, T, Tp), (X >= 0) & (Y >= 0) & unify(Tp, T))
implied_by(cadran(X, Y, T, Tp), (X < 0) & (Y >= 0) & is_(Tp, pi - T))
implied_by(cadran(X, Y, T, Tp), (X < 0) & (Y < 0) & is_(Tp, T + pi))
implied_by(cadran(X, Y, T, Tp), (X >= 0) & (Y < 0) & is_(Tp, 2 * pi - T))

implied_by(cartesien([R, T], [X1, X2]), is_(X1, R * cos(T)) & is_(X2, R * sin(T)))

# Problemes de zero
# A complex number is zero when both parts compare equal to 0, which covers 0,
# 0.0 and -0.0; the two tests exclude each other without a cut.
implied_by(nul([X, Y]), eq(X, 0) & eq(Y, 0))

implied_by(nonnul([X, _]), ne(X, 0))
implied_by(nonnul([X, Y]), eq(X, 0) & ne(Y, 0))

# query
query(roots([[1, 0], [-10, 0], [35, 0], [-50, 0], [24, 0]], _))
query(roots([[1, 0], [-9, -5], [14, 33], [24, -44], [-26, 0]], _))
