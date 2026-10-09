# Examples

<img src="https://josd.github.io/images/eye.png" alt="EYE" width="100">

*peye — reasoning you can see.*

Every example also has a [card deck](https://eyereasoner.github.io/peye/examples/deck/) that explains it for a
wide audience.

Run a source, generate its proof, or check its saved proof:

```sh
python -m peye examples/socrates.py
python -m peye --proof examples/socrates.py
python -m peye --check-proof examples/proof/socrates.py examples/socrates.py
```

Each program has a matching conclusion file in `output/`, a certificate in
`proof/`, and a C1-C7 verification report in `check/`, each written as Python
expressions, one per line. The names match the source: `lists.py` has
`output/lists.py`, `proof/lists.py` and `check/lists.py`.

| Program | Demonstrates |
| --- | --- |
| [ackermann.py](https://github.com/eyereasoner/peye/blob/main/examples/ackermann.py) | The Ackermann function through the hyperoperation sequence, exactly |
| [age.py](https://github.com/eyereasoner/peye/blob/main/examples/age.py) | Calendar-year and elapsed-day age checks at an explicit reference date |
| [alternatives.py](https://github.com/eyereasoner/peye/blob/main/examples/alternatives.py) | Alternative routes, disjunction and once |
| [audited-grants.py](https://github.com/eyereasoner/peye/blob/main/examples/audited-grants.py) | A grant policy whose own proof and check report are read back as facts and audited, in the same language |
| [aunt-agatha.py](https://github.com/eyereasoner/peye/blob/main/examples/aunt-agatha.py) | Who killed Aunt Agatha? A conclusion entailed by holding in every model of the premises |
| [backward.py](https://github.com/eyereasoner/peye/blob/main/examples/backward.py) | Backward definitions inside forward bodies |
| [bayes-diagnosis.py](https://github.com/eyereasoner/peye/blob/main/examples/bayes-diagnosis.py) | Normalized probabilities for illustrative printer faults |
| [collatz.py](https://github.com/eyereasoner/peye/blob/main/examples/collatz.py) | Parity-based recursive trajectories over a range of starts |
| [complex.py](https://github.com/eyereasoner/peye/blob/main/examples/complex.py) | Complex arithmetic, exact over Gaussian integers and polar beyond them |
| [control-system.py](https://github.com/eyereasoner/peye/blob/main/examples/control-system.py) | Feedforward and nonlinear feedback commands for two actuators |
| [data-value-right.py](https://github.com/eyereasoner/peye/blob/main/examples/data-value-right.py) | A right to the value of personal data in the age of AI: how it fits existing EU law, and how it could become an autonomous right |
| [deep-taxonomy-10.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-10.py) | A ten-level subclass chain with branches that lead nowhere |
| [deep-taxonomy-100.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-100.py) | The same taxonomy benchmark at a hundred levels |
| [deep-taxonomy-1000.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-1000.py) | The same taxonomy benchmark at a thousand levels |
| [deep-taxonomy-10000.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-10000.py) | The same taxonomy benchmark at ten thousand levels |
| [deep-taxonomy-100000.py](https://github.com/eyereasoner/peye/blob/main/examples/deep-taxonomy-100000.py) | The same taxonomy benchmark at a hundred thousand levels |
| [dog-license.py](https://github.com/eyereasoner/peye/blob/main/examples/dog-license.py) | A licensing threshold based on collected dog counts |
| [easter.py](https://github.com/eyereasoner/peye/blob/main/examples/easter.py) | Easter Sunday by the anonymous Gregorian algorithm, 2021 to 2050 |
| [existential-rules.py](https://github.com/eyereasoner/peye/blob/main/examples/existential-rules.py) | Existential rules: a fresh witness per activation, never a clash |
| [expression-eval.py](https://github.com/eyereasoner/peye/blob/main/examples/expression-eval.py) | Recursive expression graphs used in forward inference |
| [family-cousins.py](https://github.com/eyereasoner/peye/blob/main/examples/family-cousins.py) | Generations, family branches and cousin relationships |
| [fibonacci.py](https://github.com/eyereasoner/peye/blob/main/examples/fibonacci.py) | Fast doubling for exact Fibonacci numbers, and the golden ratio |
| [flat-map.py](https://github.com/eyereasoner/peye/blob/main/examples/flat-map.py) | Predicate-based mapping with multiple or missing values |
| [four-color.py](https://github.com/eyereasoner/peye/blob/main/examples/four-color.py) | Four-colouring the map of the European Union |
| [goldbach.py](https://github.com/eyereasoner/peye/blob/main/examples/goldbach.py) | Goldbach splits of every power of two up to 2^25 |
| [good-cobbler.py](https://github.com/eyereasoner/peye/blob/main/examples/good-cobbler.py) | Trade-specific classification from structured descriptions |
| [gps.py](https://github.com/eyereasoner/peye/blob/main/examples/gps.py) | Goal-driven parallel sequences: routes to a goal state within duration, cost, belief and comfort limits |
| [graphs.py](https://github.com/eyereasoner/peye/blob/main/examples/graphs.py) | Base data, negation and collection |
| [hanoi.py](https://github.com/eyereasoner/peye/blob/main/examples/hanoi.py) | Recursive construction of a disk-move sequence |
| [integrity.py](https://github.com/eyereasoner/peye/blob/main/examples/integrity.py) | A provable integrity violation |
| [interval-relations.py](https://github.com/eyereasoner/peye/blob/main/examples/interval-relations.py) | All thirteen interval relations and endpoint completion |
| [inventory.py](https://github.com/eyereasoner/peye/blob/main/examples/inventory.py) | An invoice from collected line totals |
| [kaprekar.py](https://github.com/eyereasoner/peye/blob/main/examples/kaprekar.py) | Every four-digit Kaprekar routine reaches 6174 within seven steps |
| [lists.py](https://github.com/eyereasoner/peye/blob/main/examples/lists.py) | Concatenation, mapping and summation |
| [lldm.py](https://github.com/eyereasoner/peye/blob/main/examples/lldm.py) | Leg length discrepancy measured from radiograph landmarks, with an alarm and its reason |
| [monkey-bananas.py](https://github.com/eyereasoner/peye/blob/main/examples/monkey-bananas.py) | Every plan of up to five moves that gets the monkey the bananas |
| [package-holiday.py](https://github.com/eyereasoner/peye/blob/main/examples/package-holiday.py) | Package holiday cancellations under the tour operator's ODRL terms and the 2015 and revised EU Package Travel Directive |
| [paraconsistent-animals.py](https://github.com/eyereasoner/peye/blob/main/examples/paraconsistent-animals.py) | Local summaries of conflicting observations |
| [path-discovery.py](https://github.com/eyereasoner/peye/blob/main/examples/path-discovery.py) | Full airport network with configurable endpoints and maximum stopovers |
| [peano.py](https://github.com/eyereasoner/peye/blob/main/examples/peano.py) | Symbolic arithmetic, relational addition and a chained derivation |
| [peasant.py](https://github.com/eyereasoner/peye/blob/main/examples/peasant.py) | Peasant multiplication and exponentiation by halving and doubling |
| [permissions.py](https://github.com/eyereasoner/peye/blob/main/examples/permissions.py) | Role permissions with exclusions |
| [policy-risk.py](https://github.com/eyereasoner/peye/blob/main/examples/policy-risk.py) | Ranked findings with explanations and suggested mitigations |
| [polynomial.py](https://github.com/eyereasoner/peye/blob/main/examples/polynomial.py) | Complex roots of polynomials up to degree 4 by Cardan and Lagrange |
| [queens.py](https://github.com/eyereasoner/peye/blob/main/examples/queens.py) | Configurable N-queens search with diagonal constraints |
| [reachability.py](https://github.com/eyereasoner/peye/blob/main/examples/reachability.py) | Finite closure in a graph containing a cycle |
| [research-portal.py](https://github.com/eyereasoner/peye/blob/main/examples/research-portal.py) | A hospital research portal combines ODRL/DPV policy decisions with Digital Omnibus device consent and breach plans |
| [schema-inference.py](https://github.com/eyereasoner/peye/blob/main/examples/schema-inference.py) | Subclasses, subproperties, domains and ranges |
| [scoped-audit.py](https://github.com/eyereasoner/peye/blob/main/examples/scoped-audit.py) | Presence and absence within separate quoted graphs |
| [shortest-path.py](https://github.com/eyereasoner/peye/blob/main/examples/shortest-path.py) | Weighted paths and stratified minimum selection |
| [sieve.py](https://github.com/eyereasoner/peye/blob/main/examples/sieve.py) | The sieve of Eratosthenes over an explicit list of integers |
| [socrates.py](https://github.com/eyereasoner/peye/blob/main/examples/socrates.py) | Class membership derived through a subclass rule |
| [state-transitions.py](https://github.com/eyereasoner/peye/blob/main/examples/state-transitions.py) | Account balances from an ordered event log |
| [strings.py](https://github.com/eyereasoner/peye/blob/main/examples/strings.py) | Text construction and Unicode inspection |
| [superdense-coding.py](https://github.com/eyereasoner/peye/blob/main/examples/superdense-coding.py) | Superdense coding in discrete quantum theory, with interference as odd path counts |
| [teleportation.py](https://github.com/eyereasoner/peye/blob/main/examples/teleportation.py) | Quantum teleportation in discrete quantum theory, checked for every state and outcome |
| [terms.py](https://github.com/eyereasoner/peye/blob/main/examples/terms.py) | Quoted graphs, triple terms and residual witnesses |
| [turing.py](https://github.com/eyereasoner/peye/blob/main/examples/turing.py) | A Turing machine interpreter running a binary incrementer |
| [unification.py](https://github.com/eyereasoner/peye/blob/main/examples/unification.py) | Open lists and repeated-variable constraints |
| [variable-predicates.py](https://github.com/eyereasoner/peye/blob/main/examples/variable-predicates.py) | Relations selected and renamed through data bindings |
| [witnesses.py](https://github.com/eyereasoner/peye/blob/main/examples/witnesses.py) | Structured witnesses and shared multi-head conclusions |
| [wolf-goat-cabbage.py](https://github.com/eyereasoner/peye/blob/main/examples/wolf-goat-cabbage.py) | The river crossing, with seven crossings shown to be minimal |
| [zebra.py](https://github.com/eyereasoner/peye/blob/main/examples/zebra.py) | The zebra puzzle solved by narrowing five partially known houses |

`audited-grants.py` shows what one language makes possible. It states an
energy grant policy as a program of its own, has peye prove the decisions,
and then reads that proof and its check report back as ordinary facts, with
`read_terms` and `facts_from`, to audit the reasoning: the data each decision
rests on, the assumptions it took on trust, and the decisions at risk because
they rest on self-declared income. Rules, data, conclusions, proof and report
are all the same terms, so the audit needs no export format, no parser and no
second tool, and its own conclusions come with a checked proof too.

`integrity.py` intentionally exits with code 65 because it concludes `false`.
Its proof-check report is valid: the certificate explains why the constraint was
violated. Negation and collection examples list their `absent` and `collected`
obligations in the check report; `--strict-proof` rejects those obligations.
Every check file includes `condition(...)` facts for C1-C7, verification counts and
a `verdict(...)` fact. Reports with failures include `failure(...)`; reports with
trusted boundaries include `obligation(...)`. Add `--json` to the check command
for JSON output instead.

`fibonacci.py` answers F(0), F(1), F(10), F(100), F(1000) and F(10000), the
last a 2090-digit integer, then divides successive values to watch the ratio
converge on the golden ratio. It uses fast doubling, which halves the index at
each recursive step and fits within the default reasoning limits. Its saved
proof records the arithmetic and recursive clause instances without trusted
obligations.

The `deep-taxonomy` examples are the deep-taxonomy benchmark: one individual, a
chain of subclass rules, and two sibling branches at every level that lead
nowhere. The goal has to follow the single productive branch the whole way
down, so the chain length is also the backward recursion depth. The five sizes
run from ten to a hundred thousand levels, and each costs exactly one
resolution step per level, which `--stats` reports and the saved check report
confirms: `deep-taxonomy-100000` verifies 100001 steps. Each program states
its rules with a Python loop rather than one by one, which keeps even the
largest a few lines long instead of 14 MB. Backward search is an explicit
machine, so the depth costs heap rather than host stack.

```sh
python -m peye --stats examples/deep-taxonomy-10000.py
```

Time, proof size and checking all grow linearly with the depth, so a longer
chain only costs proportionally more; the ten-thousand-level source is about
1 MB and its certificate about 1.3 MB, since a certificate records every step
it claims.

`path-discovery.py` contains 7,698 airport records and 37,505 directed
connections. Its default goal finds three routes from Ostend to Prague with
at most two stopovers. Use any airport-name atoms and a nonnegative integer
limit with `path_discovery(From, To, MaxStopovers, Path)`:

```sh
python -m peye --goal "path_discovery('Liège Airport', 'Václav Havel Airport Prague', 1, Path)" examples/path-discovery.py
goal="path_discovery('Ostend-Bruges International Airport', 'Liège Airport', 0, Path)"
python -m peye --proof --goal "$goal" examples/path-discovery.py > /tmp/route-proof.py
python -m peye --strict-proof --check-proof /tmp/route-proof.py --goal "$goal" examples/path-discovery.py
```

`--goal` replaces the default goal, so checking that proof names the same goal. Zero stopovers allows only direct flights;
N stopovers allows at most N+1 flights. Routes follow the recorded direction
and never repeat an airport. Equal endpoints and unknown names return no
routes. Negative or noninteger limits also return no routes. You can leave
`From` or `To` as a variable to discover endpoints; keep `MaxStopovers` bound.
List the available names with `--goal "airport(Id, Name)"`. These are historical
network records, rather than current flight schedules. The search uses explicit
disequalities to prevent cycles, so its proofs have no trusted obligations.
Large bounds on a dense network may still reach the configured reasoning limits.

`peano.py` represents natural numbers as `'zero'`, `s('zero')`, and so on. Its
addition goal enumerates every split of a known sum, and a second goal chains
all three relations: `(1*2)+3` is 5, whose factorial is 120 nested successors.
`expression-eval.py` evaluates a graph for `(2*3)+(10-4)` and emits
`result('example', 12)`.

`complex.py` adds a numeric domain the engine knows nothing about. A complex
number is the ordinary term `complex(Real, Imaginary)`, and addition,
multiplication, conjugation, division, norm, modulus and integer powers are all
ordinary clauses over integer arithmetic. Sums, products, conjugates, norms and
integer powers stay exact integers. Division uses Python's `/`, which is true
division: dividing `complex(-5, 10)` by `complex(1, 2)` recovers
`complex(3.0, 4.0)`, and the same division applied to `complex(3, 4)` yields
`complex(2.2, -0.4)`.
The example also derives `i*i = -1` from the multiplication clause rather than
assuming it, confirms that the Gaussian norm is multiplicative, and raises
`complex(1, 1)` to the eighth power by repeated squaring.

Polar form then leaves the integers altogether, so a complex number can be
raised to a complex power. The square root of -1 is `i`, `e` to the power `i*pi`
is -1, `i` to the power `i` is the real number 0.20787957635076193, and the
inverse sine and cosine of 2 are complex. Logarithm, sine, cosine, tangent and
arctangent follow, each applied to the answer of its own inverse so the
round trip is visible: the sine of the arcsine of 2 comes back as 2. The example
passes strict proof checking, so every component of every conclusion is
recomputed by the checker:

```sh
python -m peye --goal "complex_power(complex(1, 1), 16, Result)" examples/complex.py
python -m peye --goal "complex_div(complex(1, 0), complex(0, 1), Inverse)" examples/complex.py
```

`polynomial.py` is Alain Colmerauer's solver for polynomial equations up to
degree 4, with complex coefficients and roots as `[Re, Im]` pairs. Degree 3
follows Cardan's formula and degree 4 Lagrange's method, which solves a cubic
on the way. Its default goals find the roots of (x-1)(x-2)(x-3)(x-4) and of a
quartic with complex coefficients whose roots are 3+2i, 5+i, i and 1+i, each
up to rounding. The original evaluates expressions by building calls with
`=..` (here `univ`); here each operation has its own clause, and the zero tests compare
numbers instead of cutting. Lagrange's step collects the roots of a cubic with
a predicate of its own, so that collection depends only on a lower degree.

A list of all roots is a completed collection, so the default certificate is
small: four steps, with the arithmetic inside two `collected` obligations. Ask
for one root at a time and every arithmetic step is in the certificate
instead. For a cubic it passes strict checking:

```sh
python -m peye --proof --goal "racine([[1, 0], [-6, 0], [11, 0], [-6, 0]], Z)" examples/polynomial.py
```

`queens.py` returns the first solution for an 8x8 board by default; another
goal enumerates other board sizes:

```sh
python -m peye --goal "queens(4, Columns)" examples/queens.py
python -m peye --goal "add(A, B, s(s(s('zero'))))" examples/peano.py
```

`interval-relations.py` uses half-open intervals with integer-minute endpoints.
It completes endpoints from durations and classifies each valid interval pair
into exactly one of thirteen relations. Empty and reversed intervals are
excluded from classification.

`control-system.py` computes two actuator commands. The first is a
proportional part on a conditioned measurement minus a feedforward
compensation, the base-10 logarithm of a measured disturbance. The second is
a proportional, nonlinear differential feedback controller on the error
between a target and an output. The results are ordinary floats, and the proof
recomputes every arithmetic step.

`lldm.py` measures a leg length discrepancy from four landmarks on a
radiograph. Two landmarks fix a reference line, and each leg runs from one of
the other two to its perpendicular projection on that line. With a 1.25 cm
threshold the measured legs, 21.55 cm and 23.46 cm, raise an alarm, printed
with the lengths, the discrepancy, the threshold and the reason. The reason
names the side of the threshold that fired; the version this was adapted from
gave the same reason for both. Every intermediate value is a separate `val/3`
clause, so the strict certificate recomputes each one.

`bayes-diagnosis.py` models printer faults using illustrative priors and two
conditionally independent observations. It keeps exact integer likelihood
weights and their collected total alongside a floating-point probability.
`policy-risk.py` reports a rank, clause, clamped score, severity, reason and
mitigation. Rank 1 has the highest score; equal scores share a rank. Output
follows inference order, with ranks recorded explicitly. Adding the missing
safeguards removes the affected findings. Both examples expose their collection
obligations, and policy findings also expose absence obligations.

`research-portal.py` evaluates a hospital research portal under two rulebooks.
An ODRL/DPV policy decides research access first, then the baseline or
original Digital Omnibus rulebook decides the device-consent step. Eleven
sessions produce permits with planned deletion duties, pending device consent,
or explicit policy and device refusals. Three incidents have notification
plans under both regimes, always retaining internal documentation. Changes
compare final plans; a device exemption never overrides withdrawn research
consent or a prohibition.

`package-holiday.py` is the same pattern in the domain of leisure. A tour
operator's cancellation terms, written as an ODRL offer, decide first who may
cancel and at what fee; then the EU Package Travel Directive, in its 2015
version and as revised in 2026, decides when a cancellation is free and how
the money comes back. Eight cancellations and two complaints are decided
under both versions, with fees and refunds computed in euro. The revision
makes a cancellation free when floods close the departure airport, gives
accepted vouchers statutory guarantees, and sets complaint deadlines. Every
condition of the terms is checked one by one, so the proof passes
`--strict-proof` with no trusted steps.

`age.py` checks whether a person's age strictly exceeds `years(N)` or `days(N)`.
It uses `as_of(date(2026, 10, 1))` for reproducible output and proofs. Edit that
fact to change the default date, or pass a reference date directly:

```sh
python -m peye examples/age.py
python -m peye --goal "age_above('pat_h', years(80), date(2024, 8, 22))" examples/age.py
python -m peye --goal "age_days('pat_h', date(2026, 10, 1), Days)" examples/age.py
```

Exactly on the threshold anniversary, `age_above` fails; it succeeds on the
following day. A February 29 anniversary falls on February 28 in a non-leap
year. Elapsed days follow the Gregorian calendar, including century leap-year
rules. Invalid dates, future births, unknown people, and negative or noninteger
thresholds return no answers. Reference dates are explicit source data rather
than clock readings, and the example passes strict proof checking.

The classics from `ackermann.py` to `teleportation.py` are written without a
library. Relations such as `between`, `member` or `length` are defined in
each program as ordinary clauses, and a search commits with `once`, or with
guards that make its alternatives exclusive.

`ackermann.py` computes A(4, 2), a number with 19,729 digits, through the
hyperoperation sequence: addition, multiplication and exponentiation have closed
forms, and every higher level is the one below it iterated. `peasant.py`
multiplies and raises to powers using only halving, doubling and addition.
`sieve.py` lists the primes below 100 by striking out multiples from an
explicit list; it stops there because its certificate records every
intermediate list, which grows far faster than the answer.

`goldbach.py` splits every power of two from 4 to 2^25 into two primes, taking
the split with the smallest prime. `easter.py` dates Easter Sunday for 2021 to
2050 with the anonymous Gregorian algorithm, every step integer arithmetic on
the year. `turing.py` is a Turing machine interpreter running a machine that
adds one to a binary number.

`zebra.py` solves Einstein's riddle by narrowing a list of five partially known
houses with unification alone. `aunt-agatha.py` is Pelletier's problem 55
(TPTP PUZ001), a classic test for theorem provers: nine premises about the
three residents of Dreadbury Mansion, and the claim that Agatha killed
herself. A puzzle like the zebra asks for one solution; this one asks what
follows, which is what holds in every situation the premises allow. The
premises leave open who hates whom and who is richer than whom, so the program
enumerates every model of them: Agatha is the killer in four, the butler and
Charles in none. A full model is printed as a witness, with a proof that each
premise holds in it. `four-color.py` colours the 27 countries of the
European Union so that no neighbours share a colour. `wolf-goat-cabbage.py`
shows that a safe crossing takes seven trips and that no shorter one exists,
then prints both seven-trip plans. `monkey-bananas.py` lists every plan of up
to five moves that gets the monkey the bananas, shortest first.

`gps.py` is goal-driven parallel sequences: it finds sequences of actions from
the current state to a goal state, here driving from Gent to Oostende on a
partial map of Belgium. Duration and cost add up along a path and belief and
comfort multiply, and each must stay within its limit, as must the number of
stages, runs of steps in the same map. Two routes qualify, directly through
Brugge and the longer one through Kortrijk. The original keeps the current
state in the database, reading transitions with `clause/2` and asserting and
retracting fluents as it moves; here the state is a list of fluents passed
along the search, so every step is an ordinary clause instance and the
certificate passes strict checking. Stages are counted as changes of map plus
one, where the original stops counting at two.

`superdense-coding.py` sends two classical bits through one qubit in discrete
quantum theory, where amplitudes come from a finite field and the merge of
alternative branches is exclusive: an answer survives when it is reached an odd
number of times. The original toggles asserted facts to get that parity; here
each of Alice's messages N and Bob's readings M collects its ways through the
shared entangled pair and keeps the pair when their number is odd. Every
message arrives as itself by exactly one way, and every wrong reading by two
ways that cancel or by none, so Bob reads 0 to 3 exactly as Alice sent them.
The parity depends on all the ways, so the certificate carries the four
collections behind its answers as obligations.

`teleportation.py` runs the companion protocol in the same theory, with the
same relations. Alice measures the qubit to send together with her half of the
entangled pair, in the four-state basis Bob decodes with in superdense coding,
and sends him the outcome. Bob applies the inverse of that basis relation, which
turns out to be one of Alice's four operations from superdense coding, to his
half. For each of the three nonzero states over the two-element field and each
of the four outcomes, Bob ends up holding exactly the state Alice sent, and a
`contradiction(...)` rule would stop the run with exit code 65 if he did not. The
protocol was written for this collection, not taken from a sibling project.

Certificates that lean on a completed search say so. In `kaprekar.py` the whole
verification sits inside one negation, so its certificate is two steps plus an
`absent` obligation: the exhaustive check over 705 digit multisets is exactly
what the obligation names. `four-color.py` collects the countries with
`findall` and rules out conflicts with negation, so it carries both kinds.

Run `./test` for the full suite, or `./test examples` for this corpus;
`./test -k socrates` limits it to the tests that mention socrates. Every example
runs through the API, and a few through all three CLI modes. Tests compare
results with saved artifacts and do not overwrite them.

After an intentional behavior change, run `python tools/update_examples.py` and review
the source and artifact changes together. When adding an example, register its
name, description, expected halt code (if any) and proof obligations in
[manifest.json](https://github.com/eyereasoner/peye/blob/main/examples/manifest.json), then generate its artifacts.
