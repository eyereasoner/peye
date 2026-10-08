# Control systems: two actuator commands computed from measurements,
# observations and a target. Actuator 1 combines a proportional part with a
# feedforward compensation for a measured disturbance; actuator 2 is a
# proportional, nonlinear differential (PND) feedback controller. A
# measurement pair whose first value is below the second contributes the
# square root of their difference, otherwise its first value.

from peye import *

# measurements
fact(measurement1('input1', [6, 11]))
fact(measurement1('disturbance2', [45, 39]))
fact(measurement2('input2', 'true'))
fact(measurement3('input3', 56967))
fact(measurement3('disturbance1', 35766))
fact(measurement4('output2', 24))

# observations
fact(observation1('state1', 80))
fact(observation2('state2', 'false'))
fact(observation3('state3', 22))

# targets
fact(target2('output2', 29))

# rules
implied_by(
    control1('actuator1', C),
    measurement10('input1', M1)
    & measurement2('input2', 'true')
    & measurement3('disturbance1', D1)
    & is_(C1, M1 * 19.6)  # proportional part
    & is_(C2, log(D1) / log(10))  # compensation part
    & is_(C, C1 - C2),  # simple feedforward control
)

implied_by(
    control1('actuator2', C),
    observation3('state3', P3)
    & measurement4('output2', M4)
    & target2('output2', T2)
    & is_(E, T2 - M4)  # error
    & is_(D, P3 - M4)  # differential error
    & is_(C1, 5.8 * E)  # proportional part
    & is_(N, 7.3 / E)  # nonlinear factor
    & is_(C2, N * D)  # nonlinear differential part
    & is_(C, C1 + C2),  # PND feedback control
)

implied_by(
    measurement10(I, M),
    measurement1(I, [M1, M2])
    & (M1 < M2)
    & is_(M3, M2 - M1)
    & is_(M, sqrt(M3)),
)

implied_by(measurement10(I, M1), measurement1(I, [M1, M2]) & (M1 >= M2))

# query
query(control1(_, _))
