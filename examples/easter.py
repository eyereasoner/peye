# The date of Easter Sunday, by the anonymous Gregorian algorithm (Meeus/Jones/
# Butcher). Every step is integer arithmetic on the year; the result is a
# [Month, Day] pair.

from peye import *

implied_by(
    computus(Year, [Month, Day]),
    is_(A, Year % 19)
    & is_(B, Year // 100)
    & is_(C, Year % 100)
    & is_(D, (19 * A + B - B // 4 - (B - (B + 8) // 25 + 1) // 3 + 15) % 30)
    & is_(E, (32 + 2 * (B % 4) + 2 * (C // 4) - D - C % 4) % 7)
    & is_(F, D + E - 7 * ((A + 11 * D + 22 * E) // 451) + 114)
    & is_(Month, F // 31)
    & is_(Day, F % 31 + 1),
)

implied_by(in_range(Low, High, Low), Low <= High)
implied_by(in_range(Low, High, N), (Low < High) & is_(Next, Low + 1) & in_range(Next, High, N))

implies(in_range(2021, 2050, Year) & computus(Year, Date), easter(Year, Date))
