import re
import unittest

from peye import check_proof, public_report, run

from helpers import program

SOURCE = program('''
p, q, r = preds('p q r')
X = vars('X')
fact(p('a'))
implies(p(X), q(X))
implies(q(X), r(X))
''')


def proof():
    return run(SOURCE, proof=True).proof


class Proofs(unittest.TestCase):
    def test_flat_resolution_agrees_with_the_general_checker(self):
        from unittest.mock import patch
        source = program('''
fact(p('a', 1), p('b', 1.0))
implied_by(q(X, Y, X), p(X, Y))
query(q(X, Y, X))
''')
        document = run(source, proof=True).proof
        documents = [document]
        for original, altered in [("{'X': 'a', 'Y': 1}", '{}'),
                                  ("{'X': 'a', 'Y': 1}", "{'unknown': 'a'}"),
                                  ("{'X': 'a', 'Y': 1}", "{'X': 'b', 'Y': 1}"),
                                  ("{'X': 'a', 'Y': 1}", "{'X': A, 'Y': 1}"),
                                  ("{'X': 'a', 'Y': 1}", "{'X': 'a', 'Y': 1.0}"),
                                  ("[p('a', 1)]", "[p('b', 1)]"),
                                  ("q('a', 1, 'a')", "q('a', 1, 'b')"),
                                  ("q('a', 1, 'a')", "q(A, 1, A)"),
                                  ("q('a', 1, 'a')", "q(f('a'), 1, f('a'))")]:
            self.assertIn(original, document)
            documents.append(document.replace(original, altered))
        for document in documents:
            with self.subTest(document=document):
                fast = check_proof(source, document)
                with patch('peye.proof._flat_resolution', return_value=None):
                    general = check_proof(source, document)
                self.assertEqual(public_report(fast), public_report(general))

    def test_identity_keeps_the_sign_of_zero_in_displays_and_steps(self):
        source = program("fact(p(0.0))\nquery(p(X))")
        document = run(source, proof=True).proof
        self.assertTrue(check_proof(source, document)['valid'])
        self.invalid(document.replace('clause(1, fact(p(0.0)))', 'clause(1, fact(p(-0.0)))'), 'C1', source)
        self.invalid(document.replace('step(p(0.0)', 'step(p(-0.0)'), 'C1', source)

    def invalid(self, document, condition, source=SOURCE):
        report = check_proof(source, document)
        self.assertFalse(report['valid'])
        self.assertIn(condition, [failure['condition'] for failure in report['failures']], report)

    def test_proofs_are_checked_against_source_rather_than_display_records(self):
        self.invalid(proof().replace("clause(1, fact(p('a')))", "clause(1, fact(p('b')))"), 'C1')
        self.invalid(proof(), 'C1', program("p, q, r = preds('p q r')\nX = vars('X')\nfact(p('b'))\n"
                                            "implies(p(X), q(X))\nimplies(q(X), r(X))"))

    def test_altered_conclusion_premise_binding_and_citation_fail_resolution(self):
        self.invalid(proof().replace("step(q('a')", "step(q('b')"), 'C1')
        self.invalid(proof().replace("[p('a')]", "[p('b')]"), 'C1')
        self.invalid(proof().replace("{'X': 'a'}", "{'X': 'b'}"), 'C1')
        self.invalid(proof().replace('clause(2)', 'clause(999)'), 'C1')

    def test_omitted_steps_missing_premises_and_unrelated_claims_fail_coverage(self):
        self.invalid(re.sub(r"^step\(q\('a'\).*\n", '', proof(), flags=re.M), 'C4')
        self.invalid(proof() + "unrelated('a')\n", 'C4')

    def test_a_document_that_claims_nothing_is_valid_and_certifies_nothing(self):
        report = check_proof(SOURCE, '')
        self.assertTrue(report['valid'])
        self.assertEqual((report['claims'], report['steps']), (0, 0))

    def test_unknown_duplicate_and_malformed_justifications_are_rejected(self):
        self.invalid(proof().replace('clause(2)', "'magic'"), 'C3')
        self.invalid(proof() + "step(q('a'), clause(2), {}, [])\n", 'C3')
        self.invalid("q('a')\nstep(q('a'), clause(2), 'broken', [])", 'C3')
        self.invalid("q('a')\nx = step(q('a'), clause(2), {}, [])", 'C3')
        self.invalid("unterminated(", 'C3')
        self.invalid("__import__('os').system('true')", 'C3')

    def test_nonfinite_values_cannot_be_certified_as_numeric_equalities(self):
        self.invalid("eq(1e+999, 2e+999)\nstep(eq(1e+999, 2e+999), 'builtin', {}, [])",
                     'C3', program(''))

    def test_cyclic_certificates_cannot_justify_their_own_conclusions(self):
        self.invalid("p()\nstep(p(), clause(1), {}, [p()])", 'C2', program("p = preds('p')\nimplied_by(p, p)"))

    def test_primitive_results_are_recomputed_with_no_theory_clauses(self):
        self.invalid('is_(7, 2 + 3)\nstep(is_(7, 2 + 3), \'builtin\', {}, [])', 'C5', program(''))
        self.invalid("evil()\nstep(evil(), 'builtin', {}, [])", 'C3', program("fact('evil')"))
        report = check_proof(program(''), "is_(5, 2 + 3)\nstep(is_(5, 2 + 3), 'builtin', {}, [])",
                             goals=['is_(5, 2 + 3)'])
        self.assertTrue(report['valid'])
        self.assertEqual(report['redecided'], 1)

    def test_source_variable_sharing_cannot_be_forged(self):
        self.invalid("same('a', 'b')\nstep(same('a', 'b'), clause(1), {}, [])", 'C1',
                     program("same = preds('same')\nX = vars('X')\nfact(same(X, X))"))

    def test_absence_and_collection_obligations_remain_visible(self):
        source = program("p, out, missing = preds('p out missing')\nX = vars('X')\n"
                         "fact(p('a'))\nimplies(p(X) & ~missing(X), out(X))")
        document = run(source, proof=True).proof
        self.assertEqual(len(check_proof(source, document)['trusted']), 1)
        self.assertFalse(check_proof(source, document, allow_trusted=False)['valid'])

    def test_absences_and_collections_contradicted_by_evidence_fail_boundary_consistency(self):
        text = ("p, out, blocked, all_ = preds('p out blocked all_')\nX, L = vars('X L')\n"
                "fact(p('a'), p('b'))\nimplies(p(X) & ~blocked(X), out(X))\n"
                "implies(findall(X, p(X), L), all_(L))\n")
        source = program(text)
        document = run(source, proof=True).proof
        self.assertTrue(check_proof(source, document)['valid'])
        self.invalid(document, 'C6', program(text + "fact(blocked('a'))"))
        self.invalid(document.replace("['a', 'b']", "['a']"), 'C6')
        self.invalid("q()\nstep(q(), clause(1), {}, [~(1 < 2)])\nstep(~(1 < 2), 'absent', {}, [])", 'C6',
                     program("q = preds('q')\nimplies(~(struct('<', 1, 2)), q)"))

    def test_an_absence_with_anonymous_variables_is_refuted_by_any_instance(self):
        text = "fact(p('a'), p('b'), q('b', 1))\nimplies(p(X) & ~q(X, _), s(X))\n"
        document = run(program(text), proof=True).proof
        self.assertIn("~q('a', A)", document)
        self.assertTrue(check_proof(program(text), document)['valid'])
        self.invalid(document, 'C6', program(text + "fact(q('a', 2))"))

    def test_claims_must_answer_the_goal_asked_and_every_step_must_serve_a_claim(self):
        asked = run(SOURCE, goal='p(X)', proof=True).proof
        self.assertTrue(check_proof(SOURCE, asked, goals=['p(X)'])['valid'])
        self.invalid(asked, 'C7')
        orphan = check_proof(SOURCE, asked + "step(q('a'), clause(2), {'X': 'a'}, [p('a')])\n", goals=['p(X)'])
        self.assertEqual([failure['condition'] for failure in orphan['failures']], ['C7'])


if __name__ == '__main__':
    unittest.main()
