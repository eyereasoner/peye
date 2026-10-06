# Research portal: an ODRL/DPV policy meets two digital rulebooks.
# A hospital evaluates each planned research session under the general EU
# baseline and the original Commission Digital Omnibus proposal, COM(2025)
# 837 final (19 November 2025), after the modelled provisions apply.
# Research permission and device consent are independent gates: exempt
# audience measurement never supplies consent to process health records.
# One fixed ODRL/DPV research policy is evaluated alongside each rulebook.
#
# Sources: https://www.w3.org/TR/odrl-model/
# https://www.w3.org/TR/odrl-vocab/
# https://w3id.org/dpv/2.3/dpv/
# https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52025PC0837
# https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
# https://eur-lex.europa.eu/eli/dir/2002/58/2009-12-19
#
# Local profile: each process/10 states its data controller and legal basis;
# operands have at most one value, valid YYYYMMDD dates and an acyclic purpose
# taxonomy. Only odrl:prohibit is supported. Device accesses involve personal
# data on a natural person's device; necessity and measurement aggregation/
# own use are assessed inputs. National exceptions and transition dates are
# outside this model. The portal is not a media service provider. Refusals
# concern the same device purpose, with completed calendar months as input.
# Baseline ask_for_consent is a next-step label, never permission to disregard
# a refusal. A deny_device result blocks this planned session with its stated
# tracker; it does not require denying research if that tracker can be removed.
# Deletion is a planned obligation within 90 days of research use; duty
# fulfilment, actual consent collection and legal compliance are not proved.
# Breach risk is supplied, deadlines run from awareness without undue delay
# and where feasible; no Art. 34(3) exception applies to the high-risk case.
# Every breach must be documented, even when notification is not required.
#
# Reading guide. The program runs top to bottom as one decision process:
#   1. the ODRL/DPV research policy, as triples t(Subject, Predicate, Object);
#   2. the planned research uses, as DPV processes;
#   3. gate 1, the policy: policy_result/2 permits a use or refuses it with
#      the reasons;
#   4. gate 2, the device rules: session/3, then the consent/4 and ask/5
#      tables, one row per regime;
#   5. assessment/4 combines both gates per regime, with the basis cited;
#   6. breaches are planned per regime with breach_plan/5;
#   7. changed/3 lists every outcome the proposal would change.

from peye import *

# A small excerpt of the DPV purpose taxonomy.
fact(t('dpv:AcademicResearch', 'skos:broader', 'dpv:ResearchAndDevelopment'))
fact(t('dpv:CommercialResearch', 'skos:broader', 'dpv:ResearchAndDevelopment'))
fact(t('dpv:Advertising', 'skos:broader', 'dpv:Marketing'))

# Parties and data.
fact(t('ex:partnerBE', 'odrl:partOf', 'ex:consortium'))
fact(t('ex:partnerUS', 'odrl:partOf', 'ex:consortium'))
# The lab results are special-category personal data (dpv:SpecialCategoryPersonalData);
# the policy's conditions, not a type triple, carry what that requires here.

# The policy. The left operands ex:legalBasis, ex:consentStatus and
# ex:technicalMeasure belong to a profile that reads them from the process.
fact(t('ex:policy', 'rdf:type', 'odrl:Agreement'))
fact(t('ex:policy', 'odrl:assigner', 'ex:hospital'))
fact(t('ex:policy', 'odrl:conflict', 'odrl:prohibit'))
fact(t('ex:policy', 'odrl:permission', 'ex:research'))
fact(t('ex:research', 'odrl:assignee', 'ex:consortium'))
fact(t('ex:research', 'odrl:action', 'odrl:use'))
fact(t('ex:research', 'odrl:target', 'ex:labResults'))
fact(t('ex:research', 'odrl:constraint', 'ex:forResearch'))
fact(t('ex:research', 'odrl:constraint', 'ex:underConsent'))
fact(t('ex:research', 'odrl:constraint', 'ex:consentGiven'))
fact(t('ex:research', 'odrl:constraint', 'ex:pseudonymised'))
fact(t('ex:research', 'odrl:constraint', 'ex:before2027'))
fact(t('ex:research', 'odrl:duty', 'ex:deletion'))
fact(t('ex:deletion', 'odrl:action', 'odrl:delete'))
fact(t('ex:deletion', 'ex:withinDays', 90))
fact(t('ex:policy', 'odrl:prohibition', 'ex:noMarketing'))
fact(t('ex:noMarketing', 'odrl:assignee', 'ex:consortium'))
fact(t('ex:noMarketing', 'odrl:action', 'odrl:distribute'))
fact(t('ex:noMarketing', 'odrl:target', 'ex:labResults'))
fact(t('ex:noMarketing', 'odrl:constraint', 'ex:forMarketing'))
fact(t('ex:policy', 'odrl:prohibition', 'ex:noTransferUS'))
fact(t('ex:noTransferUS', 'odrl:assignee', 'ex:partnerUS'))
fact(t('ex:noTransferUS', 'odrl:action', 'odrl:use'))
fact(t('ex:noTransferUS', 'odrl:target', 'ex:labResults'))
fact(constraint('ex:forResearch', 'odrl:purpose', 'odrl:isA', 'dpv:ResearchAndDevelopment'))
fact(constraint('ex:underConsent', 'ex:legalBasis', 'odrl:eq', 'dpv:Consent'))
fact(constraint('ex:consentGiven', 'ex:consentStatus', 'odrl:eq', 'dpv:ConsentGiven'))
fact(constraint('ex:pseudonymised', 'ex:technicalMeasure', 'odrl:eq', 'dpv:Pseudonymisation'))
fact(constraint('ex:before2027', 'odrl:dateTime', 'odrl:lt', 20270101))
fact(constraint('ex:forMarketing', 'odrl:purpose', 'odrl:isA', 'dpv:Marketing'))

# The requests, as DPV processes.
fact(
    process('ex:r1', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r2', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:PersonalisedAdvertising', 'dpv:LegitimateInterest', 'dpv:ConsentUnknown', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r3', 'ex:hospital', 'ex:partnerBE', 'dpv:Share', 'ex:labResults', 'dpv:Advertising', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r4', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:CommercialResearch', 'dpv:Consent', 'dpv:ConsentWithdrawn', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r5', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Encryption', 20270301),
)
fact(
    process('ex:r6', 'ex:hospital', 'ex:partnerUS', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r7', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r8', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r9', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r10', 'ex:hospital', 'ex:partnerBE', 'dpv:Use', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
fact(
    process('ex:r11', 'ex:hospital', 'ex:partnerBE', 'dpv:Share', 'ex:labResults', 'dpv:AcademicResearch', 'dpv:Consent', 'dpv:ConsentGiven', 'dpv:Pseudonymisation', 20261115),
)
backward(t(P, 'rdf:type', 'dpv:Process'), process(P, _, _, _, _, _, _, _, _, _))
backward(t(P, 'dpv:hasDataController', X), process(P, X, _, _, _, _, _, _, _, _))
backward(t(P, 'ex:requestedBy', Who), process(P, _, Who, _, _, _, _, _, _, _))
backward(t(P, 'dpv:hasProcessing', X), process(P, _, _, X, _, _, _, _, _, _))
backward(t(P, 'dpv:hasPersonalData', X), process(P, _, _, _, X, _, _, _, _, _))
backward(t(P, 'dpv:hasPurpose', X), process(P, _, _, _, _, X, _, _, _, _))
backward(t(P, 'dpv:hasLegalBasis', X), process(P, _, _, _, _, _, X, _, _, _))
backward(t(P, 'dpv:hasConsentStatus', X), process(P, _, _, _, _, _, _, X, _, _))
backward(t(P, 'dpv:hasTechnicalMeasure', X), process(P, _, _, _, _, _, _, _, X, _))
backward(t(P, 'ex:requestDate', X), process(P, _, _, _, _, _, _, _, _, X))

# How a DPV processing reads as an ODRL action.
fact(action('dpv:Use', 'odrl:use'))
fact(action('dpv:Share', 'odrl:distribute'))

# What a left operand is for a given process.
backward(value(P, 'odrl:purpose', V), t(P, 'dpv:hasPurpose', V))
backward(value(P, 'ex:legalBasis', V), t(P, 'dpv:hasLegalBasis', V))
backward(value(P, 'ex:consentStatus', V), t(P, 'dpv:hasConsentStatus', V))
backward(value(P, 'ex:technicalMeasure', V), t(P, 'dpv:hasTechnicalMeasure', V))
backward(value(P, 'odrl:dateTime', V), t(P, 'ex:requestDate', V))

backward(holds('odrl:isA', V, Class), within(V, Class))
fact(holds('odrl:eq', V, V))
backward(holds('odrl:lt', V, Limit), is_int(V), is_int(Limit), V < Limit)
fact(within(Class, Class))
backward(within(Class, Super), t(Class, 'skos:broader', Middle), within(Middle, Super))
fact(party(Who, Who))
backward(party(Who, Group), t(Who, 'odrl:partOf', Group))

# A rule addresses a process when its assignee, action and target fit; it then
# applies when every one of its constraints is met.
backward(
    addresses(P, Rule),
    t(P, 'ex:requestedBy', Who),
    t(Rule, 'odrl:assignee', Assignee),
    party(Who, Assignee),
    t(P, 'dpv:hasProcessing', Processing),
    action(Processing, Action),
    t(Rule, 'odrl:action', Action),
    t(P, 'dpv:hasPersonalData', Data),
    t(Rule, 'odrl:target', Data),
)
backward(
    met(P, C),
    constraint(C, Left, Operator, Right),
    value(P, Left, V),
    holds(Operator, V, Right),
)
backward(
    unmet(P, Rule, unmet(C, Left, V, Operator, Right)),
    addresses(P, Rule),
    t(Rule, 'odrl:constraint', C),
    constraint(C, Left, Operator, Right),
    value(P, Left, V),
    ~met(P, C),
)
backward(applies(P, Rule), addresses(P, Rule), findall(Why, unmet(P, Rule, Why), []))
# A policy governs a process when it is an agreement assigned by the
# process's data controller.
backward(
    governs(Policy, P),
    t(Policy, 'rdf:type', 'odrl:Agreement'),
    t(Policy, 'odrl:assigner', Controller),
    t(P, 'dpv:hasDataController', Controller),
)
backward(
    permitted(P, Rule),
    governs(Policy, P),
    t(Policy, 'odrl:permission', Rule),
    applies(P, Rule),
)
backward(
    prohibited(P, Rule),
    governs(Policy, P),
    t(Policy, 'odrl:prohibition', Rule),
    applies(P, Rule),
)
backward(
    candidate(P, Rule),
    governs(Policy, P),
    t(Policy, 'odrl:permission', Rule),
    addresses(P, Rule),
)
backward(
    policy_ready(P),
    governs(Policy, P),
    findall(S, t(Policy, 'odrl:conflict', S), ['odrl:prohibit']),
)

# Policy outcomes are evaluated before considering the device step.
backward(
    policy_result(P, permit(Rule)),
    policy_ready(P),
    permitted(P, Rule),
    findall(R, prohibited(P, R), []),
)
backward(policy_result(P, deny(prohibited_by(Rule))), policy_ready(P), prohibited(P, Rule))
backward(
    policy_result(P, deny(not_permitted(Reasons))),
    t(P, 'rdf:type', 'dpv:Process'),
    policy_ready(P),
    candidate(P, _),
    findall(R, permitted(P, R), []),
    findall(R, prohibited(P, R), []),
    findall(Why, governs(Policy, P) & t(Policy, 'odrl:permission', Rule) & unmet(P, Rule, Why), Reasons),
)
backward(
    policy_result(P, deny('no_matching_permission')),
    t(P, 'rdf:type', 'dpv:Process'),
    policy_ready(P),
    findall(R, candidate(P, R), []),
    findall(R, prohibited(P, R), []),
)

# Each research session specifies its device access and the visitor's choice.
fact(session('ex:r1', 'own_audience_measurement', 'first_visit'))
fact(session('ex:r2', 'own_audience_measurement', 'first_visit'))
fact(session('ex:r3', 'advertising', browser_signal('refuse')))
fact(session('ex:r4', 'own_audience_measurement', 'first_visit'))
fact(session('ex:r5', 'requested_service', 'first_visit'))
fact(session('ex:r6', 'own_audience_measurement', 'first_visit'))
fact(session('ex:r7', 'advertising', browser_signal('refuse')))
fact(session('ex:r8', 'advertising', refused(completed_months(5))))
fact(session('ex:r9', 'advertising', refused(completed_months(6))))
fact(session('ex:r10', 'requested_service', 'first_visit'))
fact(session('ex:r11', 'requested_service', 'first_visit'))

fact(regime('in_force'))
fact(regime('omnibus_proposal'))
fact(refusal_pause(months(6)))

# Whether a kind of access needs consent, and on which provision.
fact(consent('in_force', 'requested_service', 'not_needed', 'ePrivacy Art. 5(3)'))
fact(consent('in_force', 'own_audience_measurement', 'needed', 'ePrivacy Art. 5(3)'))
fact(consent('in_force', 'advertising', 'needed', 'ePrivacy Art. 5(3)'))
fact(consent('omnibus_proposal', 'requested_service', 'not_needed', 'GDPR Art. 88a(3)(b)'))
fact(consent('omnibus_proposal', 'own_audience_measurement', 'not_needed', 'GDPR Art. 88a(3)(c)'))
fact(consent('omnibus_proposal', 'advertising', 'needed', 'GDPR Art. 88a(1)'))

# Where consent is needed: may the site ask, given what the visitor did?
fact(ask('in_force', _, _, 'ask_for_consent', 'ePrivacy Art. 5(3)'))
fact(
    ask('omnibus_proposal', media_service('no'), browser_signal('refuse'), 'refused_by_signal', 'GDPR Art. 88b(1)-(2)'),
)
backward(
    ask('omnibus_proposal', _, refused(completed_months(M)), 'do_not_ask_again', 'GDPR Art. 88a(4)(c)'),
    is_int(M),
    M >= 0,
    refusal_pause(months(Min)),
    M < Min,
)
backward(
    ask('omnibus_proposal', _, refused(completed_months(M)), 'ask_for_consent', 'GDPR Art. 88a(4)(c)'),
    is_int(M),
    M >= 0,
    refusal_pause(months(Min)),
    M >= Min,
)

# Who must be told of a breach, and on which provisions.
fact(authority('in_force', risk('unlikely'), 'none', 'GDPR Art. 33(1)'))
fact(authority('in_force', risk('some'), within_hours(72), 'GDPR Art. 33(1)'))
fact(authority('in_force', risk('high'), within_hours(72), 'GDPR Art. 33(1)'))
fact(authority('omnibus_proposal', risk('unlikely'), 'none', 'GDPR Art. 33(1) as amended'))
fact(authority('omnibus_proposal', risk('some'), 'none', 'GDPR Art. 33(1) as amended'))
fact(
    authority('omnibus_proposal', risk('high'), within_hours_via_single_entry_point(96), 'GDPR Art. 33(1) as amended'),
)
fact(people(_, risk('unlikely'), 'none', 'GDPR Art. 34(1)'))
fact(people(_, risk('some'), 'none', 'GDPR Art. 34(1)'))
fact(people(_, risk('high'), 'without_undue_delay', 'GDPR Art. 34(1)'))

# A policy denial takes precedence. A policy permit proceeds to the device gate.
forward(
    assessment(R, P, deny_policy(Reason), basis(['ex:policy'])),
    regime(R),
    session(P, _, _),
    policy_result(P, deny(Reason)),
)
forward(
    assessment(R, P, permit(Rule), basis(['ex:policy', Provision])),
    regime(R),
    policy_result(P, permit(Rule)),
    session(P, Kind, _),
    consent(R, Kind, 'not_needed', Provision),
)
forward(
    assessment(R, P, await_device_consent(Rule), basis(Basis)),
    regime(R),
    policy_result(P, permit(Rule)),
    session(P, Kind, Before),
    consent(R, Kind, 'needed', Provision),
    ask(R, media_service('no'), Before, 'ask_for_consent', Next),
    device_basis(Provision, Next, Basis),
)
forward(
    assessment(R, P, deny_device(Reason), basis(Basis)),
    regime(R),
    policy_result(P, permit(_)),
    session(P, Kind, Before),
    consent(R, Kind, 'needed', Provision),
    ask(R, media_service('no'), Before, Reason, Next),
    not_identical(Reason, 'ask_for_consent'),
    device_basis(Provision, Next, Basis),
)

fact(device_basis(P, P, ['ex:policy', P]))
backward(device_basis(P, Q, ['ex:policy', P, Q]), not_identical(P, Q))

forward(
    policy_conflict(P, resolved_by('odrl:prohibit', Prohibition, overrides(Permission))),
    session(P, _, _),
    policy_ready(P),
    permitted(P, Permission),
    prohibited(P, Prohibition),
)

# Duties attach to final permits, not to requests waiting for device consent.
forward(
    planned_duty(R, P, Action, within_days(Days)),
    assessment(R, P, permit(Rule), _),
    t(Rule, 'odrl:duty', Duty),
    t(Duty, 'odrl:action', Action),
    t(Duty, 'ex:withinDays', Days),
)

# Incidents concern existing portal data, independently of planned requests.
fact(breach('b1', 'encrypted laptop lost, key safe', risk('unlikely')))
fact(breach('b2', 'researcher contact addresses exposed', risk('some')))
fact(breach('b3', 'patient lab records exposed', risk('high')))
forward(
    breach_plan(R, B, notify(authority(When), people(How)), 'document_breach', basis([P, Q, 'GDPR Art. 33(5)'])),
    regime(R),
    breach(B, _, Risk),
    authority(R, Risk, When, P),
    people(R, Risk, How, Q),
)

# Compare final session decisions and incident plans, rather than provision labels.
forward(
    changed(session(P), struct('from', Old), to(New)),
    assessment('in_force', P, Old, _),
    assessment('omnibus_proposal', P, New, _),
    not_identical(Old, New),
)
forward(
    changed(breach(B), struct('from', Old), to(New)),
    breach_plan('in_force', B, Old, _, _),
    breach_plan('omnibus_proposal', B, New, _, _),
    not_identical(Old, New),
)
