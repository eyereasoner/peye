# One language for everything. This program states an energy grant policy,
# has peye prove the policy's decisions, and then reads that proof and its
# check report back as ordinary facts, in the same language, to answer audit
# questions about the reasoning itself: which data each decision rests on,
# which assumptions it takes on trust, and which decisions are at risk if
# self-declared data is wrong. There is no export format, no schema and no
# second tool: rules, data, conclusions, proofs and reports are all terms.

from peye import *
from peye import build, check_report, read_terms, run

# The applications, as Python data: name, monthly income, household size and
# the evidence for the income. Python computes clauses from them; once
# stated, a clause is a term.
APPLICATIONS = [
    ('ann', 2100, 4, 'payslip'),
    ('bob', 2900, 2, 'payslip'),
    ('cara', 1800, 1, 'self_declared'),
    ('dan', 2400, 3, 'self_declared'),
    ('eve', 2000, 2, 'payslip'),
]


def policy():
    """The grant policy, stated as a program of its own."""
    for name, money, size, evidence in APPLICATIONS:
        fact(applicant(name), income(name, money), household(name, size))
    fact(already_received('eve'))
    forward(grant(P), applicant(P), income(P, I), I < 2500, ~already_received(P))
    forward(top_up(P), grant(P), household(P, N), N >= 3)
    forward(refused(P, 'income above 2500'), applicant(P), income(P, I), I >= 2500)


# Prove the policy's decisions; run() checks the proof before returning it.
decided = run(build(policy), proof=True)

# The check report and the proof are documents in the language of this very
# program, so they become facts here without any translation: the report as
# it is, and each step of the proof as step_of(Goal, Justification, Uses).
facts_from(text=check_report(decided.proof_report))
for term, line in read_terms(decided.proof):
    kind = getattr(term, 'name', None)
    if kind == 'step':
        goal, by, bindings, uses = term.args
        fact(step_of(goal, by, uses))
    elif kind != 'clause':
        fact(decision(term))

# Where each income figure came from.
for name, money, size, evidence in APPLICATIONS:
    fact(evidence_of(income(name, money), evidence))

fact(member(X, [X, *_]))
backward(member(X, [_, *T]), member(X, T))

# A goal depends on the goals its step used, and on everything they used.
forward(depends(G, U), step_of(G, By, Uses), member(U, Uses))
forward(depends(G, W), depends(G, U), depends(U, W))

# The data a decision rests on are the policy's facts in its support, and
# its assumptions are the absences the proof could only take on trust.
# (A step justified by fact N is written struct('fact', N) here, because
# fact(...) states a fact of this program.)
forward(rests_on(D, F), decision(D), depends(D, F), step_of(F, struct('fact', _), []))
forward(assumes(D, A), decision(D), depends(D, A), step_of(A, 'absent', []))

# Was the policy's own reasoning certified, and on what conditions?
query(verdict(V))

# A decision is at risk when it rests on an income nobody has verified.
forward(at_risk(D, F), rests_on(D, F), evidence_of(F, 'self_declared'))
query(at_risk(D, F))

# For each decision: the data it rests on and the assumptions it makes.
forward(
    explanation(D, Data, Assumptions),
    decision(D),
    findall(F, rests_on(D, F), Data),
    findall(A, assumes(D, A), Assumptions),
)
query(explanation(D, Data, Assumptions))
