# Establish candidate permissions, then apply closed-world exclusions.

from peye import *

fact(role('alice', 'editor'))
fact(role('bob', 'viewer'))
fact(role('carol', 'editor'))
fact(permits('editor', 'read'))
fact(permits('editor', 'write'))
fact(permits('viewer', 'read'))
fact(suspended('carol'))
implies(role(User, Role) & permits(Role, Action), candidate(User, Action))
implies(candidate(User, Action) & ~suspended(User), allowed(User, Action))
query(allowed(User, Action))
