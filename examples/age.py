# Age checker with an explicit reference date, so proofs remain reproducible.
# Change as_of/1 or query age_above(Person, years(N), date(Y, M, D)).
# Thresholds are strictly exceeded; a leap-day anniversary falls on February
# 28 in a non-leap year. days(N) instead measures exact elapsed whole days.

from peye import *

fact(birth_date('pat_h', date(1944, 8, 21)))
fact(as_of(date(2026, 10, 1)))

backward(age_above(Person, Duration), as_of(Date), age_above(Person, Duration, Date))
backward(
    age_above(Person, years(Years), Date),
    is_int(Years),
    Years >= 0,
    birth_date(Person, Birth),
    date_day(Birth, Born),
    date_day(Date, Today),
    Today >= Born,
    anniversary(Birth, Years, Anniversary),
    date_day(Anniversary, Threshold),
    Today > Threshold,
)
backward(
    age_above(Person, days(Days), Date),
    is_int(Days),
    Days >= 0,
    age_days(Person, Date, Age),
    Age > Days,
)
backward(
    age_days(Person, Date, Days),
    birth_date(Person, Birth),
    date_day(Birth, Born),
    date_day(Date, Today),
    Today >= Born,
    is_(Days, Today - Born),
)
backward(
    anniversary(date(Y, M, D), Years, date(Year, M, Day)),
    is_(Year, Y + Years),
    month_days(Year, M, Maximum),
    is_(Day, min(D, Maximum)),
)

# Proleptic Gregorian calendar; dates have integer years >= 1.
backward(
    date_day(date(Y, M, D), Ordinal),
    is_int(Y),
    is_int(M),
    is_int(D),
    Y >= 1,
    month_days(Y, M, Maximum),
    D >= 1,
    D <= Maximum,
    month_offset(M, Offset),
    leap_extra(Y, M, Extra),
    is_(Previous, Y - 1),
    is_(Ordinal, 365 * Previous + Previous // 4 - Previous // 100 + Previous // 400 + Offset + Extra + D),
)
backward(month_days(Y, 2, 29), leap_year(Y))
backward(month_days(Y, 2, 28), common_year(Y))
backward(month_days(_, M, Days), ordinary_month(M, Days))
fact(ordinary_month(1, 31))
fact(ordinary_month(3, 31))
fact(ordinary_month(4, 30))
fact(ordinary_month(5, 31))
fact(ordinary_month(6, 30))
fact(ordinary_month(7, 31))
fact(ordinary_month(8, 31))
fact(ordinary_month(9, 30))
fact(ordinary_month(10, 31))
fact(ordinary_month(11, 30))
fact(ordinary_month(12, 31))
backward(leap_year(Y), eq(0, Y % 400))
backward(leap_year(Y), eq(0, Y % 4), ne(0, Y % 100))
backward(common_year(Y), ne(0, Y % 4))
backward(common_year(Y), eq(0, Y % 100), ne(0, Y % 400))
backward(leap_extra(_, M, 0), M <= 2)
backward(leap_extra(Y, M, 1), M > 2, leap_year(Y))
backward(leap_extra(Y, M, 0), M > 2, common_year(Y))
fact(month_offset(1, 0))
fact(month_offset(2, 31))
fact(month_offset(3, 59))
fact(month_offset(4, 90))
fact(month_offset(5, 120))
fact(month_offset(6, 151))
fact(month_offset(7, 181))
fact(month_offset(8, 212))
fact(month_offset(9, 243))
fact(month_offset(10, 273))
fact(month_offset(11, 304))
fact(month_offset(12, 334))

query(age_above(Person, years(80)))
