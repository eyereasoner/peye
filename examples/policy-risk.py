# Rank clause findings by score, retaining reasons and suggested mitigations.
# This is a small illustrative policy model; scores are model parameters.

from peye import *

fact(permission('c1', 'remove_account'))
fact(permission('c2', 'change_terms'))
fact(permission('c3', 'share_data'))
fact(prohibition('c4', 'export_data'))
fact(notice_days('c2', 3))
fact(permission('c5', 'share_data'))
fact(safeguard('c5', 'consent'))
fact(permission('c6', 'change_terms'))
fact(notice_days('c6', 14))
fact(importance('retention', 20))
fact(importance('prior_notice', 15))
fact(importance('consent', 12))
fact(importance('portability', 10))
fact(required_notice(14))
implied_by(has_notice(Clause), notice_days(Clause, Days) & (Days >= 0))
implies(
    permission(Clause, 'remove_account')
    & importance('retention', Weight)
    & ~has_notice(Clause)
    & ~safeguard(Clause, 'inform')
    & is_(Raw, 90 + Weight),
    finding(Clause, Raw, 'no_removal_safeguards', 'add_notice_and_inform'),
)
implies(
    permission(Clause, 'change_terms')
    & notice_days(Clause, Days)
    & required_notice(Required)
    & (Days < Required)
    & importance('prior_notice', Weight)
    & is_(Raw, 70 + Weight),
    finding(Clause, Raw, short_notice(Days, Required), increase_notice(Required)),
)
implies(
    permission(Clause, 'share_data')
    & ~safeguard(Clause, 'consent')
    & importance('consent', Weight)
    & is_(Raw, 85 + Weight),
    finding(Clause, Raw, 'sharing_without_consent', 'require_consent'),
)
implies(
    prohibition(Clause, 'export_data')
    & importance('portability', Weight)
    & is_(Raw, 60 + Weight),
    finding(Clause, Raw, 'export_prohibited', 'permit_export'),
)
implies(finding(Clause, Raw, Why, Fix) & (Raw > 100), score(Clause, 100))
implies(finding(Clause, Raw, Why, Fix) & (Raw <= 100), score(Clause, Raw))
implied_by(severity(Score, 'high'), Score >= 80)
implied_by(severity(Score, 'moderate'), (Score >= 50) & (Score < 80))
implied_by(severity(Score, 'low'), Score < 50)
implied_by(higher(Score, Other), score(Clause, Other) & (Other > Score))
fact(count([], 0))
implied_by(count([_, *Rest], N), count(Rest, Before) & is_(N, Before + 1))
implies(
    score(Clause, Score)
    & finding(Clause, Raw, Why, Fix)
    & severity(Score, Severity)
    & findall(Other, higher(Score, Other), Higher)
    & count(Higher, Count)
    & is_(Rank, Count + 1),
    report(Rank, Clause, Score, Severity, Why, Fix),
)
query(report(Rank, Clause, Score, Severity, Why, Fix))
