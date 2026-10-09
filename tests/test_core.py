import os
import unittest

from peye import Program, PeyeError, check_proof, load, run

from helpers import ROOT, program, proven


def example(name):
    return load(os.path.join(ROOT, 'examples', f'{name}.py'))


class Core(unittest.TestCase):
    def test_deep_branching_taxonomy_answers_proves_and_checks(self):
        source = program('''
fact(type('a', 'n0'), type('b', 'n0'))
for level in range(1, 2049):
    implied_by(type(X, f'n{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'i{level}'), type(X, f'n{level - 1}'))
    implied_by(type(X, f'j{level}'), type(X, f'n{level - 1}'))
query(type(X, 'n2048'))
''')
        plain = run(source)
        certified = proven(self, source)
        self.assertEqual(plain.answers, ["type('a', 'n2048')", "type('b', 'n2048')"])
        self.assertEqual(plain.answers, certified.answers)
        self.assertEqual(plain.stats, certified.stats)

    def test_tail_calls_preserve_alternatives_and_once_cuts(self):
        source = program('''
fact(p('a'), p('b'))
implied_by(inner(X), p(X))
implied_by(outer(X), inner(X))
''')
        for goal, count in [('outer(X)', 2), ('once(outer(X)) & p(Y)', 2),
                            ('outer(X) & once(p(Y))', 2),
                            ("once(outer(X) & unify(X, 'b'))", 1),
                            ('once(outer(X)) | outer(X)', 2)]:
            with self.subTest(goal=goal):
                plain = run(source, goal=goal)
                certified = proven(self, source, goal=goal)
                self.assertEqual(plain.answers, certified.answers)
                self.assertEqual(len(plain.answers), count)

    def test_standalone_forward_inference_and_proof(self):
        self.assertEqual(proven(self, example('socrates')).answers,
                         ["type('socrates', 'mortal')", "type('socrates', 'human')"])

    def test_mixed_forward_and_backward_reasoning(self):
        source = example('backward')
        self.assertEqual(proven(self, source).answers, ['indeed_more_interesting(5, 3)'])
        self.assertEqual(proven(self, source, goal='more_interesting(9, 2)').answers, ['more_interesting(9, 2)'])

    def test_recursive_closure_terminates_on_cycles_and_suppresses_duplicates(self):
        source = program('''
edge, path = preds('edge path')
X, Y, Z = vars('X Y Z')
fact(edge('a', 'b'), edge('b', 'a'))
implies(edge(X, Y), path(X, Y))
implies(path(X, Y) & edge(Y, Z), path(X, Z))
''')
        self.assertEqual(set(proven(self, source).answers),
                         {"path('a', 'b')", "path('b', 'a')", "path('a', 'a')", "path('b', 'b')"})

    def test_lists_quoted_formulas_triples_and_existential_sharing(self):
        result = proven(self, example('terms'))
        self.assertEqual(len(result.answers), 2)
        self.assertTrue(result.answers[0].startswith('found(triple'))
        self.assertIn("skolem(6, 'W', [graph(", result.answers[1])
        source = program('''
in_, pair = preds('in_ pair')
X, Y = vars('X Y')
fact(in_('a'))
implies(in_(X), pair(X, Y, Y))
''')
        sk = "skolem(2, 'Y', ['a'])"
        self.assertEqual(proven(self, source).answers, [f"pair('a', {sk}, {sk})"])

    def test_each_activation_gets_skolem_terms_of_its_own(self):
        source = program('''
fact(person('a'), person('b'))
implies(person(X), has_parent(X, P))
implies(has_parent(X, P) & has_parent(Y, P) & not_identical(X, Y), siblings(X, Y))
implies(has_parent(X, P), known(X))
''')
        result = run(source, proof=True)
        self.assertTrue(result.proof_report['valid'])
        self.assertEqual(result.answers, ["has_parent('a', skolem(3, 'P', ['a']))",
                                          "has_parent('b', skolem(3, 'P', ['b']))", "known('a')", "known('b')"])
        # A Skolem term is a function of the activation, the same in every run.
        self.assertEqual(run(source).answers, result.answers)

    def test_semi_naive_forward_reasoning_concludes_and_proves_as_a_full_search_does(self):
        import random
        from peye import engine
        rng = random.Random(7)
        full = lambda solver, clause: None  # noqa: E731
        for trial in range(12):
            nodes = rng.randint(3, 8)
            edges = sorted({(rng.randrange(nodes), rng.randrange(nodes)) for _ in range(rng.randint(2, 12))})
            source = program(''.join(f'fact(edge({a}, {b}))\n' for a, b in edges) + '''
fact(node(0))
implies(node(X) & edge(X, Y), node(Y))
implies(edge(X, Y), path(X, Y))
implies(path(X, Y) & path(Y, Z), path(X, Z))
implies(path(X, X) & is_(M, X * 2), loop(X) & mark(X, M))
implies(node(X) & (X > 1), witness(X, W))
implies(witness(X, W), tagged(W, X))
implies(node(X) & findall(Y, edge(X, Y), L), hub(X, L))
implies(node(X) & ~edge(X, _), isolated(X))
''')
            semi = run(source, proof=True)
            saved = engine.Solver.direct_keys
            engine.Solver.direct_keys = full
            try:
                naive = run(source, proof=True)
            finally:
                engine.Solver.direct_keys = saved
            with self.subTest(trial):
                self.assertEqual((semi.stdout, semi.proof), (naive.stdout, naive.proof))
                self.assertLessEqual(semi.stats['inferences'], naive.stats['inferences'])

    def test_answers_name_their_variables_as_their_bindings_do(self):
        result = run(program("implied_by(r(Y, Z), unify(Y, f(_, Z)))"), goal='r(P, Q)')
        self.assertEqual(result.answers, ['r(f(A, B), B)'])
        self.assertEqual(result.bindings, [{'P': 'f(A, B)', 'Q': 'B'}])

    def test_a_query_without_answers_concludes_nothing(self):
        self.assertEqual(run(program("fact(p(1))\nimplies(p(X), q(X))\nquery(r(X))")).answers, [])

    def test_recursive_arithmetic_and_goal(self):
        self.assertEqual(proven(self, example('fibonacci'), goal='fib(10, F)').answers, ['fib(10, 55)'])

    def test_large_fibonacci_indices_are_exact_within_small_budgets(self):
        fibonacci = example('fibonacci')
        current, following = 0, 1
        indices = {0, 1, 2, 3, 10, 100, 1000, 10000}
        for n in range(10001):
            if n in indices:
                result = proven(self, fibonacci, goal=f'fib({n}, F)', max_depth=32, max_inferences=1000)
                self.assertEqual(result.answers, [f'fib({n}, {current})'])
            current, following = following, current + following
        self.assertEqual(run(fibonacci, goal='fib(-1, F)').answers, [])

    def test_graph_isolation_stratified_absence_and_completed_collection(self):
        graphs = example('graphs')
        result = proven(self, graphs)
        self.assertIn("allowed('carol')", result.answers)
        self.assertNotIn("allowed('bob')", result.answers)
        self.assertTrue(any(answer.startswith("children('alice',") for answer in result.answers))
        self.assertEqual(run(graphs, goal="base('bob', 'child_of', 'alice')").answers, [])
        report = check_proof(graphs, result.proof)
        self.assertEqual({item['kind'] for item in report['trusted']}, {'absent', 'collected'})
        self.assertFalse(check_proof(graphs, result.proof, allow_trusted=False)['valid'])

    def test_negative_dependencies_through_backward_definitions_run_after_closure(self):
        source = program('''
seed, clear, blocked, derived = preds('seed clear blocked derived')
X = vars('X')
fact(seed('a'))
implies(~blocked('a'), clear('a'))
implied_by(blocked(X), derived(X))
implies(seed(X), derived(X))
''')
        self.assertEqual(proven(self, source).answers, ["derived('a')"])

    def test_closed_dependency_cycles_are_rejected(self):
        with self.assertRaisesRegex(PeyeError, 'unstratified'):
            program("p, q = preds('p q')\nimplies(not_(q), p)\nimplies(p, q)")
        with self.assertRaisesRegex(PeyeError, 'unstratified'):
            program("p = preds('p')\nX, Y = vars('X Y')\nimplies(findall(Y, p(Y), X), p(X))")

    def test_predicate_positions_distinguish_open_and_closed_dependencies(self):
        source = program('''
t = preds('t')
X = vars('X')
fact(t('a', 'seed', 'true'))
implies(t(X, 'seed', 'true') & ~t(X, 'blocked', 'true'), t(X, 'allowed', 'true'))
implies(t(X, 'seed', 'true'), t(X, 'blocked', 'true'))
''')
        self.assertEqual(proven(self, source).answers, ["t('a', 'blocked', 'true')"])

    def test_conjunction_disjunction_call_and_once_preserve_proof_uses(self):
        facts = "p, q = preds('p q')\nX = vars('X')\nfact(p('a'), p('b'))\n"
        proven(self, program(facts + "implied_by(q(X), p(X) & unify(X, 'a'))"), goal='q(X)')
        proven(self, program(facts), goal="p('a') | p('b')")
        proven(self, program(facts), goal="call(p('a') & p('b'))")
        self.assertEqual(len(proven(self, program(facts), goal='once(p(X))').answers), 1)
        proven(self, program(facts), goal="p('a') & p('b')")

    def test_query_selects_output_and_contradiction_trips_the_fuse(self):
        source = program("p, q = preds('p q')\nX = vars('X')\nfact(p('a'))\nimplies(p(X), q(X))\nquery(q(X))")
        self.assertEqual(proven(self, source).answers, ["q('a')"])
        result = proven(self, program("p = preds('p')\nfact(p('a'))\ncontradiction(p('a'))"))
        self.assertEqual(result.halt_code, 65)
        self.assertEqual(result.answers, ["'false'"])

    def test_nonground_answers_retain_shared_variables(self):
        result = proven(self, program("same = preds('same')\nX = vars('X')\nfact(same(X, X))"), goal='same(A, B)')
        self.assertEqual(len(result.answers), 1)
        self.assertEqual(result.bindings[0]['A'], result.bindings[0]['B'])

    def test_unsupported_constructs_and_resource_exhaustion_fail_explicitly(self):
        with self.assertRaisesRegex(PeyeError, 'max_depth'):
            run(program("p = preds('p')\nimplied_by(p, p)"), goal='p()', max_depth=10)
        with self.assertRaisesRegex(PeyeError, 'max_iterations'):
            run(program("p = preds('p')\nN, M = vars('N M')\nfact(p(0))\nimplies(p(M) & is_(N, M + 1), p(N))"),
                max_iterations=3)
        with self.assertRaisesRegex(PeyeError, 'max_inferences'):
            run(program("p, q = preds('p q')\nX = vars('X')\nfact(p('a'))\nimplies(p(X) & p(X), q(X))"), max_inferences=1)
        with self.assertRaisesRegex(PeyeError, 'negation requires a goal whose variables are bound'):
            run(program(''), goal='~p(X)')
        with self.assertRaisesRegex(PeyeError, 'reserved'):
            program("fact(struct('step', 1, 2, 3, 4))")
        with self.assertRaisesRegex(PeyeError, 'a list is not a goal'):
            program("p = preds('p')\nimplied_by(p, ['a'])")

    def test_pure_term_and_text_operations(self):
        source = program('''
out, term, chars, codes = preds('out term chars codes')
C, N, T = vars('C N T')
implied_by(out(C, N), atom_concat('ab', 'cd', C) & atom_length(C, N))
implied_by(term(T), univ(T, ['pair', 'a', 'b']) & functor(T, 'pair', 2) & arg(2, T, 'b'))
implied_by(chars(C), atom_chars('\U0001F600a', C))
implied_by(codes(C), atom_codes('\U0001F600a', C))
''')
        self.assertEqual(proven(self, source, goal='out(C, N)').answers, ["out('abcd', 4)"])
        self.assertEqual(proven(self, source, goal='term(T)').answers, ["term(pair('a', 'b'))"])
        self.assertEqual(proven(self, source, goal='chars(C)').answers, ["chars(['\U0001F600', 'a'])"])
        self.assertEqual(proven(self, source, goal='codes(C)').answers, ['codes([128512, 97])'])

    def test_arithmetic_preserves_unbounded_integers_and_numeric_types(self):
        source = program("out = preds('out')\nN, M = vars('N M')\n"
                         "implied_by(out(N), unify(M, 9007199254740993) & is_(N, M + 1))")
        self.assertEqual(proven(self, source, goal='out(N)').answers, ['out(9007199254740994)'])
        self.assertEqual(run(program("p = preds('p')\nfact(p(1))"), goal='p(1.0)').answers, [])

    def test_finite_tree_unification_and_nested_identity(self):
        self.assertEqual(run(program(''), goal='unify(X, f(X))').answers, [])
        proven(self, program("p = preds('p')\nX = vars('X')\n"
                             "implied_by(p, unify(X, 'a') & identical(struct('f', X), struct('f', 'a')))"), goal='p()')
        proven(self, program("p = preds('p')\nT, X = vars('T X')\n"
                             "implied_by(p(T), unify(X, 'pair') & univ(T, [X, 'a', 'b']))"), goal='p(T)')
        proven(self, program("p = preds('p')\nA, C = vars('A C')\n"
                             "implied_by(p(C), unify(C, 'a') & atom_chars(A, [C]) & unify(A, 'a'))"), goal='p(C)')

    def test_computed_calls_work_backward_and_forward_analysis_rejects_hidden_calls(self):
        source = "p, apply = preds('p apply')\nG = vars('G')\nfact(p('a'))\nimplied_by(apply(G), call(G))\n"
        self.assertEqual(proven(self, program(source), goal="apply(p('a'))").answers, ["apply(p('a'))"])
        with self.assertRaisesRegex(PeyeError, 'statically named'):
            program(source + "q = preds('q')\nimplies(apply(p('a')), q)")

    def test_programs_can_be_reused_without_sharing_derived_state(self):
        source = program("p, q = preds('p q')\nX = vars('X')\nfact(p('a'))\nimplies(p(X), q(X))")
        self.assertEqual(run(source).answers, ["q('a')"])
        self.assertEqual(run(source).answers, ["q('a')"])

    def test_clause_indexing_preserves_source_order_and_generic_clauses(self):
        source = program('''
p, f = preds('p f')
X = vars('X')
fact(p('a', 'first'), p(X, 'generic_before'), p('b', 'other'))
fact(p('a', 'second'), p(X, 'generic_after'), p(f('a'), 'structured'), p(1, 'numeric'))
''')
        self.assertEqual(proven(self, source, goal="p('a', Y)").answers, [
            "p('a', 'first')", "p('a', 'generic_before')", "p('a', 'second')", "p('a', 'generic_after')"])
        self.assertEqual(proven(self, source, goal="p('missing', Y)").answers, [
            "p('missing', 'generic_before')", "p('missing', 'generic_after')"])
        self.assertEqual(len(proven(self, source, goal='p(X, Y)').answers), 7)
        self.assertEqual(len(proven(self, source, goal="p(f('a'), Y)").answers), 3)
        self.assertEqual(len(proven(self, source, goal='p(1, Y)').answers), 3)
        self.assertEqual(proven(self, source, goal="p(X, 'structured')").answers, ["p(f('a'), 'structured')"])
        self.assertEqual(len(proven(self, source, goal="unify(X, 'a') & p(X, Y)").answers), 4)

    def test_proofs_fail_explicitly_when_mode_tests_lose_their_state(self):
        source = program("p = preds('p')\nX = vars('X')\nimplied_by(p(X), is_var(X) & unify(X, 'a'))")
        self.assertEqual(run(source, goal='p(X)').answers, ["p('a')"])
        with self.assertRaisesRegex(PeyeError, 'cannot certify'):
            run(source, goal='p(X)', proof=True)

    def test_program_from_sources(self):
        prog = program("p = preds('p')\nfact(p('a'))")
        self.assertIsInstance(prog, Program)
        self.assertEqual(run(Program(prog.sources), goal='p(X)').answers, ["p('a')"])


if __name__ == '__main__':
    unittest.main()
