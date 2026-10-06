# Illustrative naive Bayes diagnosis of a printer: jam and offline observations.
# Weights are whole percentages; products stay exact until normalization.

from peye import *

fact(fault('paper_jam', 20, 90, 10))
fact(fault('network_loss', 30, 5, 95))
fact(fault('power_loss', 50, 1, 99))
forward(
    weight(Fault, Weight),
    fault(Fault, Prior, Jam, Offline),
    is_(Weight, Prior * Jam * Offline),
)
fact(sum_weights([], 0))
backward(sum_weights([W, *Ws], Sum), sum_weights(Ws, Rest), is_(Sum, W + Rest))
forward(total(Total), findall(W, weight(Fault, W), Weights), sum_weights(Weights, Total))
forward(
    posterior(Fault, Numerator, Denominator, Probability),
    weight(Fault, Numerator),
    total(Denominator),
    Denominator > 0,
    is_(Probability, Numerator / Denominator),
)
query(posterior(Fault, Numerator, Denominator, Probability))
