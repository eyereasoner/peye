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
implies(bird(X), flies(X, 'true'))
implies(bird(X), wings(X, 'true'))
implies(penguin(X), flies(X, 'false'))
implies(mammal(X), wings(X, 'false'))
implies(bat(X), flies(X, 'true') & wings(X, 'true'))
implies(fish(X), swims(X, 'true') & wings(X, 'false'))
implies(observed(X, 'flies', Value), flies(X, Value))

# Local summaries. These inspect the rule conclusions, so they run only after
# the stratum above has reached its fixpoint.
implies(flies(X, 'true') & flies(X, 'false'), flight_status(X, 'both'))
implies(flies(X, 'true') & ~flies(X, 'false'), flight_status(X, 'true_only'))
implies(flies(X, 'false') & ~flies(X, 'true'), flight_status(X, 'false_only'))
implies(wings(X, 'true') & wings(X, 'false'), wing_status(X, 'both'))
implies(wings(X, 'true') & ~wings(X, 'false'), wing_status(X, 'true_only'))
implies(wings(X, 'false') & ~wings(X, 'true'), wing_status(X, 'false_only'))

# A conflicting summary is reported rather than silently resolved.
implies(flight_status(X, 'both'), inconsistent(X, 'flies') & needs_review(X, 'flies'))
implies(wing_status(X, 'both'), inconsistent(X, 'wings') & needs_review(X, 'wings'))

# Decisions read the summary, so a contradiction yields undecided instead of
# both answers at once.
implies(flight_status(X, 'true_only'), flies_safely(X, 'true'))
implies(flight_status(X, 'false_only'), flies_safely(X, 'false'))
implies(flight_status(X, 'both'), flies_safely(X, 'undecided'))
implies(wing_status(X, 'true_only'), wings_safely(X, 'true'))
implies(wing_status(X, 'false_only'), wings_safely(X, 'false'))
implies(wing_status(X, 'both'), wings_safely(X, 'undecided'))
implies(flight_status(X, 'true_only'), moves_by(X, 'flying') & migrates(X, 'true'))
implies(flight_status(X, 'false_only'), moves_by(X, 'walking') & migrates(X, 'false'))
implies(flight_status(X, 'both'), moves_by(X, 'unknown') & migrates(X, 'undecided'))
