# Package holidays under two rulebooks. A tour operator's cancellation terms,
# written as an ODRL offer, meet the EU Package Travel Directive in two
# versions: Directive (EU) 2015/2302 as in force, and its revision, approved
# by the European Parliament on 12 March 2026 and then adopted by the Council.
# The revision applies after transposition: Member States have 28 months to
# transpose it and 6 more months to apply it. Each planned cancellation is
# decided under both versions, every outcome cites its basis, and the
# program lists what the revision would change.
#
# In force: a traveller may cancel before departure, paying the organiser's
# termination fee (Art. 12(1)); without a fee when unavoidable and
# extraordinary circumstances at the destination or its immediate vicinity
# significantly affect the package (Art. 12(2)); refunds are due within 14
# days (Art. 12(4)). The 2015 Directive has no rules on vouchers.
# Revision: such circumstances at the point of departure count too; vouchers
# are optional for the traveller, worth at least the refund, valid for at
# most 12 months, and refunded when unused; complaints are acknowledged within
# 7 days and answered with reasons within 60 days.
#
# Sources: https://eur-lex.europa.eu/eli/dir/2015/2302/oj/eng
# https://www.europarl.europa.eu/news/en/press-room/20260306IPR37536/package-travel-parliament-greenlights-new-rules-to-protect-holidaymakers
# https://www.w3.org/TR/odrl-model/
#
# Scope: whether circumstances are unavoidable and extraordinary and
# significantly affect the package is assessed in advance and given as input.
# Whether the operator's fee scale is reasonable and justifiable, as Art. 12(1)
# requires, is not assessed. National rules, the 2015 Directive's other
# articles and the revision's further changes are outside this model.
#
# Reading guide:
#   1. the operator's terms, as triples t(Subject, Predicate, Object);
#   2. the bookings and the cancellation requests;
#   3. gate 1, the terms: policy_result/2 evaluates the ODRL triples and
#      permits a cancellation or refuses it, with every unmet condition;
#   4. gate 2, the directive: free_cancellation/4 and settle/7, one row per
#      version;
#   5. assessment/4 combines both gates per version, with the basis cited;
#   6. complaints are planned per version with complaint_plan/4;
#   7. changed/3 lists every outcome the revision would change.

from peye import *

fact(regime('directive_2015'))
fact(regime('revised_2026'))

# The operator's terms, as an ODRL offer. Gate 1 reads these triples: the
# offer, its assigner, its permission and action, the conditions as one
# odrl:and constraint, and the fee scale of the compensation duty. The local
# profile adds the action ex:cancel, the left operands ex:requesterRole and
# ex:daysBeforeDeparture, and the duty property ex:feeScale, whose bands give
# the fee as a share of the price by the number of days left.
fact(t('ex:terms', 'rdf:type', 'odrl:Offer'))
fact(t('ex:terms', 'odrl:assigner', 'ex:sunTrips'))
fact(t('ex:terms', 'odrl:permission', 'ex:cancellation'))
fact(t('ex:cancellation', 'odrl:action', 'ex:cancel'))
fact(t('ex:cancellation', 'odrl:constraint', 'ex:conditions'))
fact(t('ex:conditions', 'odrl:and', ['ex:byLeadTraveller', 'ex:beforeDeparture']))
fact(t('ex:byLeadTraveller', 'odrl:leftOperand', 'ex:requesterRole'))
fact(t('ex:byLeadTraveller', 'odrl:operator', 'odrl:eq'))
fact(t('ex:byLeadTraveller', 'odrl:rightOperand', 'ex:leadTraveller'))
fact(t('ex:beforeDeparture', 'odrl:leftOperand', 'ex:daysBeforeDeparture'))
fact(t('ex:beforeDeparture', 'odrl:operator', 'odrl:gt'))
fact(t('ex:beforeDeparture', 'odrl:rightOperand', 0))
fact(t('ex:cancellation', 'odrl:duty', 'ex:fee'))
fact(t('ex:fee', 'odrl:action', 'odrl:compensate'))
fact(t('ex:fee', 'ex:feeScale', [band(60, 999, 25), band(30, 59, 50), band(1, 29, 100)]))

# Bookings: the operator, the lead traveller and the price in euro.
fact(booking('bk1', operator('ex:sunTrips'), lead('anna'), price(2400)))
fact(booking('bk2', operator('ex:sunTrips'), lead('ben'), price(1800)))
fact(booking('bk3', operator('ex:sunTrips'), lead('chloe'), price(1500)))
fact(booking('bk4', operator('ex:sunTrips'), lead('david'), price(2100)))
fact(booking('bk5', operator('ex:sunTrips'), lead('emma'), price(1200)))
fact(booking('bk6', operator('ex:sunTrips'), lead('farid'), price(1600)))
fact(booking('bk7', operator('ex:sunTrips'), lead('gina'), price(900)))
fact(booking('bk8', operator('ex:sunTrips'), lead('ivy'), price(1300)))

# Cancellation requests: booking, who asks, the action, days before
# departure, what happened, and whether a voucher is offered and how the
# traveller answers.
fact(
    request('r1', 'bk1', by('anna'), 'ex:cancel', days(90), circumstances('none'), voucher('not_offered')),
)
fact(
    request('r2', 'bk2', by('ben'), 'ex:cancel', days(20), circumstances('none'), voucher('not_offered')),
)
fact(
    request('r3', 'bk3', by('chloe'), 'ex:cancel', days(10), circumstances(at('destination', 'hurricane')), voucher('not_offered')),
)
fact(
    request('r4', 'bk4', by('david'), 'ex:cancel', days(5), circumstances(at('departure', 'airport_closed_by_floods')), voucher('not_offered')),
)
fact(
    request('r5', 'bk5', by('emma'), 'ex:cancel', days(12), circumstances(at('destination', 'hurricane')), voucher(offered('refused'))),
)
fact(
    request('r6', 'bk6', by('farid'), 'ex:cancel', days(12), circumstances(at('destination', 'hurricane')), voucher(offered('accepted'))),
)
fact(
    request('r7', 'bk7', by('gina'), 'ex:cancel', days(-2), circumstances('none'), voucher('not_offered')),
)
fact(
    request('r8', 'bk8', by('hugo'), 'ex:cancel', days(40), circumstances('none'), voucher('not_offered')),
)

# What a left operand is for a request.
implied_by(
    value(C, 'ex:requesterRole', 'ex:leadTraveller'),
    request(C, B, by(X), _, _, _, _)
    & booking(B, _, lead(X), _),
)
implied_by(
    value(C, 'ex:requesterRole', 'ex:otherPerson'),
    request(C, B, by(X), _, _, _, _)
    & booking(B, _, lead(L), _)
    & not_identical(X, L),
)
implied_by(value(C, 'ex:daysBeforeDeparture', D), request(C, _, _, _, days(D), _, _))
# Each operator decides its comparison either way, so no step rests on
# the absence of an answer.
implied_by(compare_('odrl:eq', V, R, 'true'), identical(V, R))
implied_by(compare_('odrl:eq', V, R, 'false'), not_identical(V, R))
implied_by(compare_('odrl:gt', V, R, 'true'), V > R)
implied_by(compare_('odrl:gt', V, R, 'false'), V <= R)

# Gate 1. A permission of an offer addresses a request when the booking is
# with the offer's assigner and the actions match. Each operand of its
# odrl:and constraint is then met or unmet, in the order the policy lists them.
implied_by(
    addresses(C, Rule),
    t(Offer, 'rdf:type', 'odrl:Offer')
    & t(Offer, 'odrl:assigner', Operator)
    & t(Offer, 'odrl:permission', Rule)
    & t(Rule, 'odrl:action', Action)
    & request(C, B, _, Action, _, _, _)
    & booking(B, operator(Operator), _, _),
)
implied_by(
    condition(C, K, Result),
    t(K, 'odrl:leftOperand', Left)
    & t(K, 'odrl:operator', Op)
    & t(K, 'odrl:rightOperand', Right)
    & value(C, Left, V)
    & compare_(Op, V, Right, Holds)
    & result(Holds, K, Left, V, Op, Right, Result),
)
fact(result('true', _, _, _, _, _, 'met'))
fact(result('false', K, Left, V, Op, Right, unmet(K, Left, V, Op, Right)))
fact(unmet(_, [], []))
implied_by(unmet(C, [K, *Ks], Reasons), condition(C, K, 'met') & unmet(C, Ks, Reasons))
implied_by(
    unmet(C, [K, *Ks], [Why, *Reasons]),
    condition(C, K, Why)
    & not_identical(Why, 'met')
    & unmet(C, Ks, Reasons),
)
implied_by(
    policy_result(C, permit(Rule)),
    addresses(C, Rule)
    & t(Rule, 'odrl:constraint', X)
    & t(X, 'odrl:and', Ks)
    & unmet(C, Ks, []),
)
implied_by(
    policy_result(C, refuse(Reasons)),
    addresses(C, Rule)
    & t(Rule, 'odrl:constraint', X)
    & t(X, 'odrl:and', Ks)
    & unmet(C, Ks, Reasons)
    & not_identical(Reasons, []),
)

# The fee band for the days left, from the compensation duty of the permission.
implied_by(
    fee_percent(Rule, D, Pct),
    t(Rule, 'odrl:duty', Duty)
    & t(Duty, 'odrl:action', 'odrl:compensate')
    & t(Duty, 'ex:feeScale', Bands)
    & band(D, Bands, Pct),
)
implied_by(band(D, [band(Min, Max, Pct), *_], Pct), (Min <= D) & (D <= Max))
implied_by(band(D, [band(Min, _, _), *Bands], Pct), (D < Min) & band(D, Bands, Pct))

# Gate 2: whether the circumstances make the cancellation free of charge.
fact(free_cancellation('directive_2015', 'none', 'no', 'PTD Art. 12(1)'))
fact(free_cancellation('directive_2015', at('destination', _), 'yes', 'PTD Art. 12(2)'))
fact(free_cancellation('directive_2015', at('departure', _), 'no', 'PTD Art. 12(1)'))
fact(free_cancellation('revised_2026', 'none', 'no', 'PTD Art. 12(1)'))
fact(free_cancellation('revised_2026', at('destination', _), 'yes', 'revised PTD: destination'))
fact(
    free_cancellation('revised_2026', at('departure', _), 'yes', 'revised PTD: point of departure'),
)

# How the money is settled: the operator's fee, or a refund or voucher.
implied_by(
    settle(_, 'no', Rule, P, D, _, pay_fee(percent(Pct), fee(F), refund(Back), within_days(14))),
    fee_percent(Rule, D, Pct)
    & is_(F, P * Pct // 100)
    & is_(Back, P - F),
)
fact(settle(_, 'yes', _, P, _, 'not_offered', refund(P, within_days(14))))
fact(settle(_, 'yes', _, P, _, offered('refused'), refund(P, within_days(14))))
fact(
    settle('directive_2015', 'yes', _, P, _, offered('accepted'), voucher(value(P), terms('as_agreed'))),
)
fact(
    settle('revised_2026', 'yes', _, P, _, offered('accepted'), voucher(value(P), valid_months(12), 'unused_value_refunded')),
)
# The provision behind the way the money is settled.
fact(money_basis(_, 'no', _, 'PTD Art. 12(4)'))
fact(money_basis(_, 'yes', 'not_offered', 'PTD Art. 12(4)'))
fact(money_basis('directive_2015', 'yes', offered('refused'), 'PTD Art. 12(4)'))
fact(money_basis('directive_2015', 'yes', offered('accepted'), 'PTD 2015: no voucher rules'))
fact(money_basis('revised_2026', 'yes', offered(_), 'revised PTD: vouchers'))

# A refusal by the terms takes precedence; a permitted cancellation is settled
# under the directive.
implies(
    regime(R)
    & policy_result(C, refuse(Reasons)),
    assessment(R, C, refused_by_terms(Reasons), basis(['ex:terms'])),
)
implies(
    regime(R)
    & policy_result(C, permit(Rule))
    & request(C, B, _, _, days(D), circumstances(What), voucher(V))
    & booking(B, _, _, price(P))
    & free_cancellation(R, What, F, Free)
    & settle(R, F, Rule, P, D, V, Outcome)
    & money_basis(R, F, V, Money),
    assessment(R, C, Outcome, basis(['ex:terms', Free, Money])),
)

# Complaints are a separate duty, whatever happens to a booking.
fact(complaint('k1', 'pool closed for the whole stay'))
fact(complaint('k2', 'refund not received'))
implies(
    complaint(K, _),
    complaint_plan('directive_2015', K, deadlines('set_by_national_law'), basis(['PTD 2015: no complaint deadlines'])),
)
implies(
    complaint(K, _),
    complaint_plan('revised_2026', K, deadlines(acknowledge(within_days(7)), reasoned_reply(within_days(60))), basis(['revised PTD: complaints'])),
)

# Compare final outcomes, rather than provision labels.
implies(
    assessment('directive_2015', C, Old, _)
    & assessment('revised_2026', C, New, _)
    & not_identical(Old, New),
    changed(cancellation(C), struct('from', Old), to(New)),
)
implies(
    complaint_plan('directive_2015', K, Old, _)
    & complaint_plan('revised_2026', K, New, _)
    & not_identical(Old, New),
    changed(complaint(K), struct('from', Old), to(New)),
)
