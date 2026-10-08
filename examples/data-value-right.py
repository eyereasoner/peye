# A right to the value of personal data, in the age of AI.
#
# A model of a research design in two parts. The legal analysis asks how such
# a right would fit existing EU law: it breaks the right into components and
# finds, for each, the provisions that already anchor it, fully or only in
# part, and the components no provision anchors at all. The policy evaluation
# then weighs ways of developing the right, from interpreting existing law to
# an autonomous right of data subjects, against what the analysis found: does
# an option close the gaps, does it treat personal data as a commodity, in
# tension with data protection as a fundamental right (Charter art. 8), and
# does the data subject get a claim of their own?
#
# The provisions are summarized for illustration, and the decomposition is
# one working hypothesis among others: this models a research design, it is
# not legal advice.

from peye import *

# What a right to the value of personal data would involve.
COMPONENTS = [
    ('value_transparency', 'knowing that and how one\'s data creates value, including in AI training'),
    ('use_control', 'deciding on the uses through which one\'s data creates value'),
    ('value_mobility', 'taking one\'s data elsewhere, to have value created there'),
    ('value_recognition', 'the law acknowledging that personal data has economic value'),
    ('collective_exercise', 'exercising the right together, through an intermediary'),
    ('individual_enforcement', 'enforcing the right oneself, before a court'),
    ('value_share', 'receiving a share of the value one\'s data creates'),
]

# Existing provisions, the component each anchors, how far, and why.
ANCHORS = [
    ('GDPR art. 13-15', 'value_transparency', 'partial',
     'information on purposes and recipients, not on the value created'),
    ('AI Act art. 53(1)(d)', 'value_transparency', 'partial',
     'a public summary of the content used to train general-purpose AI models, not per data subject'),
    ('GDPR art. 7(3)', 'use_control', 'partial',
     'consent can be withdrawn at any time, where processing rests on consent'),
    ('GDPR art. 21', 'use_control', 'partial',
     'a right to object, weighed against the controller\'s legitimate interests'),
    ('GDPR art. 20', 'value_mobility', 'partial',
     'portability of data the data subject provided, on consent or contract'),
    ('DMA art. 6(9)', 'value_mobility', 'partial',
     'continuous, real-time portability, but only from gatekeepers'),
    ('Directive 2019/770 art. 3(1)', 'value_recognition', 'full',
     'personal data recognized as what a consumer may provide in exchange for digital content'),
    ('DGA ch. III', 'collective_exercise', 'partial',
     'data intermediation services, without bargaining over value'),
    ('GDPR art. 79 and 82', 'individual_enforcement', 'full',
     'a judicial remedy and compensation for the data subject'),
]

# Ways of developing the right: the components an option delivers, and how it
# frames the right. Interpreting existing law can only strengthen what is
# already anchored, so its components follow from the analysis below.
OPTIONS = [
    ('interpret_existing_law', [], 'right'),
    ('extend_portability', ['value_mobility', 'value_transparency'], 'right'),
    ('data_dividend', ['value_share', 'collective_exercise'], 'levy'),
    ('data_ownership', ['value_share', 'use_control', 'value_mobility', 'individual_enforcement'], 'property'),
    ('autonomous_right', [name for name, _ in COMPONENTS], 'inalienable_right'),
]

for name, description in COMPONENTS:
    fact(component(name, description))
for provision, name, degree, reason in ANCHORS:
    fact(anchor(provision, name, degree, reason))
for option_name, delivered, framing in OPTIONS:
    fact(option(option_name, framing))
    for name in delivered:
        fact(delivers(option_name, name))

# A framing gives the data subject a claim of their own, or treats personal
# data as a commodity that can be traded away.
fact(own_claim('right'), own_claim('inalienable_right'), own_claim('property'))
fact(commodifies('property'))

# ----- Legal analysis: how a right would fit existing law ----------------

implies(anchor(P, C, D, W), anchored(C))
implies(anchor(P, C, 'full', W), fully_anchored(C))
implies(component(C, Description) & ~anchored(C), gap(C))

implies(fully_anchored(C), fit(C, 'in existing law'))
implies(anchored(C) & ~fully_anchored(C), fit(C, 'by interpretation'))
implies(gap(C), fit(C, 'needs an autonomous right'))

# Each component, what it means, how it fits, and the provisions it rests on.
implies(
    component(C, Meaning)
    & fit(C, How)
    & findall(P, anchor(P, C, D, W), Provisions),
    analysis(C, Meaning, How, Provisions),
)
query(analysis(C, Meaning, How, Provisions))

# ----- Policy evaluation: how to develop the right -----------------------

implies(anchored(C), delivers('interpret_existing_law', C))

# A component needs developing unless existing law anchors it fully, and an
# option that leaves such a component undelivered leaves the right incomplete.
implies(component(C, Meaning) & ~fully_anchored(C), needs_development(C))
implies(option(O, F) & needs_development(C) & ~delivers(O, C), objection(O, unaddressed(C)))
implies(option(O, F) & commodifies(F), objection(O, 'treats personal data as a commodity'))
implies(option(O, F) & ~own_claim(F), objection(O, 'gives the data subject no claim of their own'))

implies(objection(O, Why), objectionable(O))
implies(option(O, F) & ~objectionable(O), recommended(O))

implies(
    option(O, F)
    & findall(C, delivers(O, C), Delivered)
    & findall(Why, objection(O, Why), Objections),
    evaluation(O, Delivered, Objections),
)
query(evaluation(O, Delivered, Objections))
query(recommended(O))
