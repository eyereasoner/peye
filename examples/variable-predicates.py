# A predicate position is data, so a rule can rename several relations at once.

from peye import *

fact(t('alice', 'source_name', 'Alice'))
fact(t('alice', 'source_age', 30))
fact(maps('source_name', 'name'))
fact(maps('source_age', 'age'))
forward(t(S, Target, O), t(S, Source, O), maps(Source, Target))
query(t('alice', 'name', Name))
query(t('alice', 'age', Age))
