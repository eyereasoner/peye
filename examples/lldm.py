# Leg Length Discrepancy Measurement, adapted from Eyeling lldm.n3.
#
# Four landmarks are measured on a radiograph. Landmarks 1 and 2 fix a
# reference line; each leg's length is the distance from landmark 3 or 4 to
# its perpendicular projection, 5 or 6, on that line. An alarm fires when the
# left and right lengths differ by more than a threshold. The measurement and
# intermediate geometry are kept in helper predicates, and the goals at the end
# print the alarm with the small set of relations explaining why it fired.

from peye import *

# val/3 stores raw landmark coordinates, derived deltas, line coefficients,
# projected landmarks, lengths, and alarm values in one measurement namespace.
fact(measurement('meas47'))

# measured landmark coordinates, in centimetres
fact(val('meas47', 'p1xCm', 10.1))
fact(val('meas47', 'p1yCm', 7.8))
fact(val('meas47', 'p2xCm', 45.1))
fact(val('meas47', 'p2yCm', 5.6))
fact(val('meas47', 'p3xCm', 3.6))
fact(val('meas47', 'p3yCm', 29.8))
fact(val('meas47', 'p4xCm', 54.7))
fact(val('meas47', 'p4yCm', 28.5))

# threshold used by the alarm rule, in centimetres
fact(threshold('meas47', 'lld_alarm_threshold_cm', 1.25))

# geometric intermediate values
# The geometry rules build from coordinate differences to projected knee points,
# then compute left/right leg lengths and compare the discrepancy with a threshold.
implied_by(val(M, 'dx12Cm', Z), measurement(M) & val(M, 'p1xCm', X) & val(M, 'p2xCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dx51Cm', Z), measurement(M) & val(M, 'p5xCm', X) & val(M, 'p1xCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dx53Cm', Z), measurement(M) & val(M, 'p5xCm', X) & val(M, 'p3xCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dx62Cm', Z), measurement(M) & val(M, 'p6xCm', X) & val(M, 'p2xCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dx64Cm', Z), measurement(M) & val(M, 'p6xCm', X) & val(M, 'p4xCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dy12Cm', Z), measurement(M) & val(M, 'p1yCm', X) & val(M, 'p2yCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dy13Cm', Z), measurement(M) & val(M, 'p1yCm', X) & val(M, 'p3yCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dy24Cm', Z), measurement(M) & val(M, 'p2yCm', X) & val(M, 'p4yCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dy53Cm', Z), measurement(M) & val(M, 'p5yCm', X) & val(M, 'p3yCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'dy64Cm', Z), measurement(M) & val(M, 'p6yCm', X) & val(M, 'p4yCm', Y) & is_(Z, X - Y))
implied_by(val(M, 'cL1', Z), measurement(M) & val(M, 'dy12Cm', Y) & val(M, 'dx12Cm', X) & is_(Z, Y / X))
implied_by(val(M, 'dL3m', Z), measurement(M) & val(M, 'cL1', X) & is_(Z, 1 / X))
implied_by(val(M, 'cL3', Z), measurement(M) & val(M, 'dL3m', X) & is_(Z, 0 - X))
implied_by(val(M, 'pL1x1Cm', Z), measurement(M) & val(M, 'cL1', X) & val(M, 'p1xCm', Y) & is_(Z, X * Y))
implied_by(val(M, 'pL1x2Cm', Z), measurement(M) & val(M, 'cL1', X) & val(M, 'p2xCm', Y) & is_(Z, X * Y))
implied_by(val(M, 'pL3x3Cm', Z), measurement(M) & val(M, 'cL3', X) & val(M, 'p3xCm', Y) & is_(Z, X * Y))
implied_by(val(M, 'pL3x4Cm', Z), measurement(M) & val(M, 'cL3', X) & val(M, 'p4xCm', Y) & is_(Z, X * Y))
implied_by(
    val(M, 'dd13Cm', Z),
    measurement(M)
    & val(M, 'pL1x1Cm', X)
    & val(M, 'pL3x3Cm', Y)
    & is_(Z, X - Y),
)
implied_by(
    val(M, 'ddy13Cm', Z),
    measurement(M)
    & val(M, 'dd13Cm', X)
    & val(M, 'dy13Cm', Y)
    & is_(Z, X - Y),
)
implied_by(
    val(M, 'dd24Cm', Z),
    measurement(M)
    & val(M, 'pL1x2Cm', X)
    & val(M, 'pL3x4Cm', Y)
    & is_(Z, X - Y),
)
implied_by(
    val(M, 'ddy24Cm', Z),
    measurement(M)
    & val(M, 'dd24Cm', X)
    & val(M, 'dy24Cm', Y)
    & is_(Z, X - Y),
)
implied_by(val(M, 'ddL13', Z), measurement(M) & val(M, 'cL1', X) & val(M, 'cL3', Y) & is_(Z, X - Y))
implied_by(
    val(M, 'pL1dx51Cm', Z),
    measurement(M)
    & val(M, 'cL1', X)
    & val(M, 'dx51Cm', Y)
    & is_(Z, X * Y),
)
implied_by(
    val(M, 'pL1dx62Cm', Z),
    measurement(M)
    & val(M, 'cL1', X)
    & val(M, 'dx62Cm', Y)
    & is_(Z, X * Y),
)
implied_by(
    val(M, 'p5xCm', Z),
    measurement(M)
    & val(M, 'ddy13Cm', X)
    & val(M, 'ddL13', Y)
    & is_(Z, X / Y),
)
implied_by(
    val(M, 'p5yCm', Z),
    measurement(M)
    & val(M, 'pL1dx51Cm', X)
    & val(M, 'p1yCm', Y)
    & is_(Z, X + Y),
)
implied_by(
    val(M, 'p6xCm', Z),
    measurement(M)
    & val(M, 'ddy24Cm', X)
    & val(M, 'ddL13', Y)
    & is_(Z, X / Y),
)
implied_by(
    val(M, 'p6yCm', Z),
    measurement(M)
    & val(M, 'pL1dx62Cm', X)
    & val(M, 'p2yCm', Y)
    & is_(Z, X + Y),
)
implied_by(val(M, 'sdx53Cm2', Z), measurement(M) & val(M, 'dx53Cm', X) & is_(Z, X ** 2))
implied_by(val(M, 'sdx64Cm2', Z), measurement(M) & val(M, 'dx64Cm', X) & is_(Z, X ** 2))
implied_by(val(M, 'sdy53Cm2', Z), measurement(M) & val(M, 'dy53Cm', X) & is_(Z, X ** 2))
implied_by(val(M, 'sdy64Cm2', Z), measurement(M) & val(M, 'dy64Cm', X) & is_(Z, X ** 2))
implied_by(
    val(M, 'ssd53Cm2', Z),
    measurement(M)
    & val(M, 'sdx53Cm2', X)
    & val(M, 'sdy53Cm2', Y)
    & is_(Z, X + Y),
)
implied_by(
    val(M, 'ssd64Cm2', Z),
    measurement(M)
    & val(M, 'sdx64Cm2', X)
    & val(M, 'sdy64Cm2', Y)
    & is_(Z, X + Y),
)
implied_by(val(M, 'd53Cm', Z), measurement(M) & val(M, 'ssd53Cm2', X) & is_(Z, X ** 0.5))
implied_by(val(M, 'd64Cm', Z), measurement(M) & val(M, 'ssd64Cm2', X) & is_(Z, X ** 0.5))
implied_by(val(M, 'dCm', Z), measurement(M) & val(M, 'd53Cm', X) & val(M, 'd64Cm', Y) & is_(Z, X - Y))

# concise output layer
# The alarm fires on either side of the threshold, and the reason says which.
implied_by(
    alarm(M, 'discrepancy below negative threshold'),
    measurement(M)
    & val(M, 'dCm', D)
    & threshold(M, 'lld_alarm_threshold_cm', T)
    & is_(Negt, 0 - T)
    & (D < Negt),
)
implied_by(
    alarm(M, 'discrepancy above threshold'),
    measurement(M)
    & val(M, 'dCm', D)
    & threshold(M, 'lld_alarm_threshold_cm', T)
    & (D > T),
)
implied_by(type(M, 'lld_alarm'), alarm(M, _))
implied_by(lld_left_length_cm(M, L), type(M, 'lld_alarm') & val(M, 'd53Cm', L))
implied_by(lld_right_length_cm(M, R), type(M, 'lld_alarm') & val(M, 'd64Cm', R))
implied_by(lld_discrepancy_cm(M, D), type(M, 'lld_alarm') & val(M, 'dCm', D))
implied_by(lld_threshold_cm(M, T), type(M, 'lld_alarm') & threshold(M, 'lld_alarm_threshold_cm', T))
implied_by(lld_reason(M, Reason), alarm(M, Reason))

query(type(_, _))
query(lld_left_length_cm(_, _))
query(lld_right_length_cm(_, _))
query(lld_discrepancy_cm(_, _))
query(lld_threshold_cm(_, _))
query(lld_reason(_, _))
