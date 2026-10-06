# A negative balance triggers the integrity fuse; the CLI exits with code 65.

from peye import *

fact(account('alice', 30))
fact(account('bob', -5))
contradiction(account(Owner, Balance), Balance < 0)
