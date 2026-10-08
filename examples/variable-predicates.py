# A predicate position is data, so a rule can rename several relations at once.

from peye import *

fact(t('alice', 'source_name', 'Alice'))
fact(t('alice', 'source_age', 30))
fact(maps('source_name', 'name'))
fact(maps('source_age', 'age'))
implies(t(S, Source, O) & maps(Source, Target), t(S, Target, O))
query(t('alice', 'name', Name))
query(t('alice', 'age', Age))
