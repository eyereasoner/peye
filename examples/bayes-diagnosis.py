# Illustrative naive Bayes diagnosis of a printer: jam and offline observations.
# Weights are whole percentages; products stay exact until normalization.

from peye import *

fact(fault('paper_jam', 20, 90, 10))
fact(fault('network_loss', 30, 5, 95))
fact(fault('power_loss', 50, 1, 99))
implies(
    fault(Fault, Prior, Jam, Offline)
    & is_(Weight, Prior * Jam * Offline),
    weight(Fault, Weight),
)
fact(sum_weights([], 0))
implied_by(sum_weights([W, *Ws], Sum), sum_weights(Ws, Rest) & is_(Sum, W + Rest))
implies(findall(W, weight(Fault, W), Weights) & sum_weights(Weights, Total), total(Total))
implies(
    weight(Fault, Numerator)
    & total(Denominator)
    & (Denominator > 0)
    & is_(Probability, Numerator / Denominator),
    posterior(Fault, Numerator, Denominator, Probability),
)
query(posterior(Fault, Numerator, Denominator, Probability))
