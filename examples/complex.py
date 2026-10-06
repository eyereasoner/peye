# Complex numbers as ordinary terms: complex(Real, Imaginary).
# peye has no complex primitives, so the whole domain is defined by clauses.
# Gaussian integer components stay exact, and the two places that leave the
# integers - an inexact quotient and a modulus - are visible in the output.

from peye import *

backward(complex_add(complex(A, B), complex(C, D), complex(R, I)), is_(R, A + C), is_(I, B + D))
backward(complex_sub(complex(A, B), complex(C, D), complex(R, I)), is_(R, A - C), is_(I, B - D))
backward(
    complex_mul(complex(A, B), complex(C, D), complex(R, I)),
    is_(R, A * C - B * D),
    is_(I, A * D + B * C),
)
backward(complex_conjugate(complex(A, B), complex(A, N)), is_(N, -B))
# Dividing by a nonzero divisor scales by its norm, so an exactly divisible
# quotient stays a Gaussian integer and any other one becomes a float pair.
backward(
    complex_div(complex(A, B), complex(C, D), complex(R, I)),
    is_(Norm, C * C + D * D),
    Norm > 0,
    is_(R, (A * C + B * D) / Norm),
    is_(I, (B * C - A * D) / Norm),
)
# The norm of a Gaussian integer is an exact integer; the modulus is its root.
backward(complex_norm(complex(A, B), Norm), is_(Norm, A * A + B * B))
backward(complex_modulus(Z, Modulus), complex_norm(Z, Norm), is_(Modulus, sqrt(Norm)))
# Integer powers by repeated squaring, with logarithmic depth, as in modular exponentiation.
fact(complex_power(_, 0, complex(1, 0)))
backward(
    complex_power(Base, Exponent, Result),
    Exponent > 0,
    is_(Half, Exponent // 2),
    complex_mul(Base, Base, Squared),
    complex_power(Squared, Half, Partial),
    finish_complex_power(Exponent, Base, Partial, Result),
)
backward(finish_complex_power(Exponent, _, Partial, Partial), eq(0, Exponent % 2))
backward(
    finish_complex_power(Exponent, Base, Partial, Result),
    eq(1, Exponent % 2),
    complex_mul(Base, Partial, Result),
)

fact(point('z', complex(3, 4)))
fact(point('w', complex(1, 2)))
# Multiplying by 1+i rotates by an eighth turn and scales by the square root of 2.
fact(turn(complex(1, 1)))
fact(turns(8))

forward(sum(Sum), point('z', Z), point('w', W), complex_add(Z, W, Sum))
forward(product(Product), point('z', Z), point('w', W), complex_mul(Z, W, Product))
# Dividing the product by w recovers z exactly: the norm divides both parts.
forward(quotient(Quotient), product(Product), point('w', W), complex_div(Product, W, Quotient))
# The same division with an indivisible numerator leaves the integers.
forward(ratio(Ratio), point('z', Z), point('w', W), complex_div(Z, W, Ratio))
# i*i = -1 follows from the multiplication clause rather than being assumed.
forward(unit_square(Square), complex_mul(complex(0, 1), complex(0, 1), Square))
# Multiplying by the conjugate leaves the norm and no imaginary part.
forward(
    conjugate_product(Name, Product),
    point(Name, Z),
    complex_conjugate(Z, Conjugate),
    complex_mul(Z, Conjugate, Product),
)
# The Gaussian norm is multiplicative: N(z) * N(w) = N(z*w).
forward(
    norm_multiplicative(Nz, Nw, Nzw),
    point('z', Z),
    point('w', W),
    product(ZW),
    complex_norm(Z, Nz),
    complex_norm(W, Nw),
    complex_norm(ZW, Nzw),
)
# Eight eighth-turns return to the positive real axis, at 2^4.
forward(
    integer_power(Exponent, Result),
    turn(Base),
    turns(Exponent),
    complex_power(Base, Exponent, Result),
)
forward(modulus(Name, Modulus), point(Name, Z), complex_modulus(Z, Modulus))

# Leaving the Gaussian integers: polar form turns multiplication into addition
# of angles, which is what makes a complex power well defined.
# The quadrant is chosen explicitly, since acos alone only covers half a turn.
fact(pi_value(3.141592653589793))
backward(
    complex_polar(complex(X, Y), polar(R, Angle)),
    is_(R, sqrt(X * X + Y * Y)),
    R > 0,
    is_(Reference, acos(abs(X) / R)),
    quadrant_angle(X, Y, Reference, Angle),
)
backward(quadrant_angle(X, Y, Reference, Reference), X >= 0, Y >= 0)
backward(
    quadrant_angle(X, Y, Reference, Angle),
    X < 0,
    Y >= 0,
    pi_value(Pi),
    is_(Angle, Pi - Reference),
)
backward(
    quadrant_angle(X, Y, Reference, Angle),
    X < 0,
    Y < 0,
    pi_value(Pi),
    is_(Angle, Pi + Reference),
)
backward(
    quadrant_angle(X, Y, Reference, Angle),
    X >= 0,
    Y < 0,
    pi_value(Pi),
    is_(Angle, 2 * Pi - Reference),
)
# z^w = |z|^c * e^(-d*t) * (cos(d*ln|z| + c*t) + i*sin(d*ln|z| + c*t)).
backward(
    complex_exponentiation(Z, complex(C, D), complex(E, F)),
    complex_polar(Z, polar(R, Angle)),
    is_(Magnitude, R ** C * exp(-D * Angle)),
    is_(Phase, D * log(R) + C * Angle),
    is_(E, Magnitude * cos(Phase)),
    is_(F, Magnitude * sin(Phase)),
)
# Inverse sine and cosine of a complex argument, through the same real parts.
backward(
    complex_half_axes(complex(A, B), Minor, Major),
    is_(Outer, sqrt((1 + A) * (1 + A) + B * B)),
    is_(Inner, sqrt((1 - A) * (1 - A) + B * B)),
    is_(Minor, (Outer - Inner) / 2),
    is_(Major, (Outer + Inner) / 2),
)
backward(
    complex_asin(Z, complex(C, D)),
    complex_half_axes(Z, Minor, Major),
    is_(C, asin(Minor)),
    is_(D, log(Major + sqrt(Major * Major - 1))),
)
backward(
    complex_acos(Z, complex(C, D)),
    complex_half_axes(Z, Minor, Major),
    is_(C, acos(Minor)),
    is_(D, -log(Major + sqrt(Major * Major - 1))),
)

# The complex logarithm of Z in a complex base, through their polar forms.
backward(
    complex_log(Base, Z, Result),
    complex_polar(Base, polar(BaseR, BaseAngle)),
    complex_polar(Z, polar(R, Angle)),
    is_(LogBase, log(BaseR)),
    is_(LogR, log(R)),
    complex_div(complex(LogR, Angle), complex(LogBase, BaseAngle), Result),
)
# Sine and cosine of a complex argument, through the real hyperbolic parts.
backward(
    complex_sin(complex(A, B), complex(C, D)),
    is_(C, sin(A) * (exp(B) + exp(-B)) / 2),
    is_(D, cos(A) * (exp(B) - exp(-B)) / 2),
)
backward(
    complex_cos(complex(A, B), complex(C, D)),
    is_(C, cos(A) * (exp(B) + exp(-B)) / 2),
    is_(D, -sin(A) * (exp(B) - exp(-B)) / 2),
)
backward(
    complex_tan(Z, Result),
    complex_sin(Z, Sine),
    complex_cos(Z, Cosine),
    complex_div(Sine, Cosine, Result),
)
backward(
    complex_atan(Z, Result),
    complex_sub(complex(0, 1), Z, Numerator),
    complex_add(complex(0, 1), Z, Denominator),
    complex_div(Numerator, Denominator, Ratio),
    complex_log(complex(2.718281828459045, 0), Ratio, Logarithm),
    complex_div(Logarithm, complex(0, 2), Result),
)

# The square root of -1, Euler's identity, i to the power i, and a real power
# of e, each as an ordinary complex exponentiation.
fact(exponent_case('root', complex(-1, 0), complex(0.5, 0)))
fact(exponent_case('euler', complex(2.718281828459045, 0), complex(0, 3.141592653589793)))
fact(exponent_case('self_power', complex(0, 1), complex(0, 1)))
fact(exponent_case('real_power', complex(2.718281828459045, 0), complex(-1.57079632679, 0)))
fact(inverse_case(complex(2, 0)))

forward(power(Name, Value), exponent_case(Name, Z, W), complex_exponentiation(Z, W, Value))
forward(arcsine(Z, Value), inverse_case(Z), complex_asin(Z, Value))
forward(arccosine(Z, Value), inverse_case(Z), complex_acos(Z, Value))

# A logarithm in base e recovers Euler's identity; one in base i recovers 1.
forward(
    logarithm('natural', Value),
    complex_log(complex(2.718281828459045, 0), complex(-1, 0), Value),
)
forward(logarithm('imaginary', Value), complex_log(complex(0, 1), complex(0, 1), Value))
# Sine and cosine invert the arcsine and arccosine above, back to 2.
forward(sine(Value), arcsine(_, Angle), complex_sin(Angle, Value))
forward(cosine(Value), arccosine(_, Angle), complex_cos(Angle, Value))
# Tangent and arctangent likewise round-trip 1+2i.
forward(arctangent(Value), complex_atan(complex(1, 2), Value))
forward(tangent(Value), arctangent(Angle), complex_tan(Angle, Value))
