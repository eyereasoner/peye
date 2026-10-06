# A structured witness identifies the rule and the binding that created it.

from peye import *

fact(person('alice'))
fact(person('bob'))
forward(
    has_record(Name, record('person_rule', Name)) & record_owner(record('person_rule', Name), Name),
    person(Name),
)
