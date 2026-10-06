# N queens: list position is the row, list value is the column (both 1-based).

from peye import *

backward(
    queens(N, Columns),
    is_int(N),
    N >= 0,
    columns(1, N, Available),
    place(Available, [], Columns),
)
backward(columns(I, N, []), I > N)
backward(columns(I, N, [I, *Rest]), I <= N, is_(Next, I + 1), columns(Next, N, Rest))
fact(select(X, [X, *Rest], Rest))
backward(select(X, [Y, *Rest], [Y, *Remaining]), select(X, Rest, Remaining))
fact(place([], _, []))
backward(
    place(Available, Placed, [Column, *Rest]),
    select(Column, Available, Remaining),
    safe(Column, Placed, 1),
    place(Remaining, [Column, *Placed], Rest),
)
fact(safe(_, [], _))
backward(
    safe(Column, [Other, *Rest], Distance),
    ne(Column, Other + Distance),
    ne(Column, Other - Distance),
    is_(Next, Distance + 1),
    safe(Column, Rest, Next),
)
query(once(queens(8, Columns)))
