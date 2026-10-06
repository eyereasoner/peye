# Conflicting observations are kept as data rather than repaired. Each property
# is summarized locally as true only, false only or both, and only an
# unconflicted summary is allowed to drive a decision.

from peye import *

fact(bird('tweety'))
fact(penguin('tweety'))
fact(bird('falco'))
fact(penguin('opus'))
fact(mammal('batsy'))
fact(bat('batsy'))
fact(fish('nemo'))
fact(bird('mythic'))
# An explicit observation that contradicts the rule for birds.
fact(observed('mythic', 'flies', 'false'))

# Domain rules that may conflict with one another.
forward(flies(X, 'true'), bird(X))
forward(wings(X, 'true'), bird(X))
forward(flies(X, 'false'), penguin(X))
forward(wings(X, 'false'), mammal(X))
forward(flies(X, 'true') & wings(X, 'true'), bat(X))
forward(swims(X, 'true') & wings(X, 'false'), fish(X))
forward(flies(X, Value), observed(X, 'flies', Value))

# Local summaries. These inspect the rule conclusions, so they run only after
# the stratum above has reached its fixpoint.
forward(flight_status(X, 'both'), flies(X, 'true'), flies(X, 'false'))
forward(flight_status(X, 'true_only'), flies(X, 'true'), ~flies(X, 'false'))
forward(flight_status(X, 'false_only'), flies(X, 'false'), ~flies(X, 'true'))
forward(wing_status(X, 'both'), wings(X, 'true'), wings(X, 'false'))
forward(wing_status(X, 'true_only'), wings(X, 'true'), ~wings(X, 'false'))
forward(wing_status(X, 'false_only'), wings(X, 'false'), ~wings(X, 'true'))

# A conflicting summary is reported rather than silently resolved.
forward(inconsistent(X, 'flies') & needs_review(X, 'flies'), flight_status(X, 'both'))
forward(inconsistent(X, 'wings') & needs_review(X, 'wings'), wing_status(X, 'both'))

# Decisions read the summary, so a contradiction yields undecided instead of
# both answers at once.
forward(flies_safely(X, 'true'), flight_status(X, 'true_only'))
forward(flies_safely(X, 'false'), flight_status(X, 'false_only'))
forward(flies_safely(X, 'undecided'), flight_status(X, 'both'))
forward(wings_safely(X, 'true'), wing_status(X, 'true_only'))
forward(wings_safely(X, 'false'), wing_status(X, 'false_only'))
forward(wings_safely(X, 'undecided'), wing_status(X, 'both'))
forward(moves_by(X, 'flying') & migrates(X, 'true'), flight_status(X, 'true_only'))
forward(moves_by(X, 'walking') & migrates(X, 'false'), flight_status(X, 'false_only'))
forward(moves_by(X, 'unknown') & migrates(X, 'undecided'), flight_status(X, 'both'))
