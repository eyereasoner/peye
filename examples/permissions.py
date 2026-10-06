# Establish candidate permissions, then apply closed-world exclusions.

from peye import *

fact(role('alice', 'editor'))
fact(role('bob', 'viewer'))
fact(role('carol', 'editor'))
fact(permits('editor', 'read'))
fact(permits('editor', 'write'))
fact(permits('viewer', 'read'))
fact(suspended('carol'))
forward(candidate(User, Action), role(User, Role), permits(Role, Action))
forward(allowed(User, Action), candidate(User, Action), ~suspended(User))
query(allowed(User, Action))
