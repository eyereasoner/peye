# The zebra puzzle (Einstein's riddle), as printed in Life International on
# 17 December 1962. Five houses in a row, each with one colour, nationality,
# pet, drink and brand of cigarette. Who drinks water, and who owns the zebra?
# Each constraint narrows a list of five partially known houses; unification
# does the rest.

from peye import *

implied_by(
    zebra(WaterDrinker, ZebraOwner),
    unify(Houses, [_, _, _, _, _])  # 1. There are five houses.
    & member(house('red', 'english', _, _, _), Houses)  # 2. The Englishman lives in the red house.
    & member(house(_, 'spanish', 'dog', _, _), Houses)  # 3. The Spaniard owns the dog.
    & member(house('green', _, _, 'coffee', _), Houses)  # 4. Coffee is drunk in the green house.
    & member(house(_, 'ukrainian', _, 'tea', _), Houses)  # 5. The Ukrainian drinks tea.
    & next_to(house('ivory', _, _, _, _), house('green', _, _, _, _), Houses)  # 6. Green is immediately right of ivory.
    & member(house(_, _, 'snail', _, 'old_gold'), Houses)  # 7. The Old Gold smoker owns snails.
    & member(house('yellow', _, _, _, 'kools'), Houses)  # 8. Kools are smoked in the yellow house.
    & unify(Houses, [_, _, house(_, _, _, 'milk', _), _, _])  # 9. Milk is drunk in the middle house.
    & unify(Houses, [house(_, 'norwegian', _, _, _), *_])  # 10. The Norwegian lives in the first house.
    & adjacent(house(_, _, _, _, 'chesterfields'), house(_, _, 'fox', _, _), Houses)  # 11. Chesterfields next to the fox.
    & adjacent(house(_, _, _, _, 'kools'), house(_, _, 'horse', _, _), Houses)  # 12. Kools next to the horse.
    & member(house(_, _, _, 'orange_juice', 'lucky_strike'), Houses)  # 13. Lucky Strike with orange juice.
    & member(house(_, 'japanese', _, _, 'parliaments'), Houses)  # 14. The Japanese smokes Parliaments.
    & adjacent(house(_, 'norwegian', _, _, _), house('blue', _, _, _, _), Houses)  # 15. The Norwegian is next to blue.
    & member(house(_, WaterDrinker, _, 'water', _), Houses)
    & member(house(_, ZebraOwner, 'zebra', _, _), Houses),
)

fact(member(X, [X, *_]))
implied_by(member(X, [_, *Rest]), member(X, Rest))
fact(next_to(X, Y, [X, Y, *_]))
implied_by(next_to(X, Y, [_, *Rest]), next_to(X, Y, Rest))
implied_by(adjacent(A, B, Houses), next_to(A, B, Houses) | next_to(B, A, Houses))

query(zebra(_, _))
