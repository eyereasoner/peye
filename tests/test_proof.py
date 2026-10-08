import re
import unittest

from peye import check_proof, run

from helpers import program

SOURCE = program('''
p, q, r = preds('p q r')
X = vars('X')
fact(p('a'))
forward(q(X), p(X))
forward(r(X), q(X))
''')


def proof():
    return run(SOURCE, proof=True).proof


class Proofs(unittest.TestCase):
    def invalid(self, document, condition, source=SOURCE):
        report = check_proof(source, document)
        self.assertFalse(report['valid'])
        self.assertIn(condition, [failure['condition'] for failure in report['failures']], report)

    def test_proofs_are_checked_against_source_rather_than_display_records(self):
        self.invalid(proof().replace("clause(1, fact(p('a')))", "clause(1, fact(p('b')))"), 'C1')
        self.invalid(proof(), 'C1', program("p, q, r = preds('p q r')\nX = vars('X')\nfact(p('b'))\n"
                                            "forward(q(X), p(X))\nforward(r(X), q(X))"))

    def test_altered_conclusion_premise_binding_and_citation_fail_resolution(self):
        self.invalid(proof().replace("step(q('a')", "step(q('b')"), 'C1')
        self.invalid(proof().replace("[p('a')]", "[p('b')]"), 'C1')
        self.invalid(proof().replace("{'X': 'a'}", "{'X': 'b'}"), 'C1')
        self.invalid(proof().replace('clause(2)', 'clause(999)'), 'C1')

    def test_omitted_steps_missing_premises_and_unrelated_claims_fail_coverage(self):
        self.invalid(re.sub(r"^step\(q\('a'\).*\n", '', proof(), flags=re.M), 'C4')
        self.invalid(proof() + "unrelated('a')\n", 'C4')
        self.invalid('', 'C4')

    def test_unknown_duplicate_and_malformed_justifications_are_rejected(self):
        self.invalid(proof().replace('clause(2)', "'magic'"), 'C3')
        self.invalid(proof() + "step(q('a'), clause(2), {}, [])\n", 'C3')
        self.invalid("q('a')\nstep(q('a'), clause(2), 'broken', [])", 'C3')
        self.invalid("q('a')\nx = step(q('a'), clause(2), {}, [])", 'C3')
        self.invalid("unterminated(", 'C3')
        self.invalid("__import__('os').system('true')", 'C3')

    def test_cyclic_certificates_cannot_justify_their_own_conclusions(self):
        self.invalid("p()\nstep(p(), clause(1), {}, [p()])", 'C2', program("p = preds('p')\nbackward(p, p)"))

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
                         "fact(p('a'))\nforward(out(X), p(X), ~missing(X))")
        document = run(source, proof=True).proof
        self.assertEqual(len(check_proof(source, document)['trusted']), 1)
        self.assertFalse(check_proof(source, document, allow_trusted=False)['valid'])

    def test_absences_and_collections_contradicted_by_evidence_fail_boundary_consistency(self):
        text = ("p, out, blocked, all_ = preds('p out blocked all_')\nX, L = vars('X L')\n"
                "fact(p('a'), p('b'))\nforward(out(X), p(X), ~blocked(X))\n"
                "forward(all_(L), findall(X, p(X), L))\n")
        source = program(text)
        document = run(source, proof=True).proof
        self.assertTrue(check_proof(source, document)['valid'])
        self.invalid(document, 'C6', program(text + "fact(blocked('a'))"))
        self.invalid(document.replace("['a', 'b']", "['a']"), 'C6')
        self.invalid("q()\nstep(q(), clause(1), {}, [~(1 < 2)])\nstep(~(1 < 2), 'absent', {}, [])", 'C6',
                     program("q = preds('q')\nforward(q, ~(struct('<', 1, 2)))"))

    def test_claims_must_answer_the_goal_asked_and_every_step_must_serve_a_claim(self):
        asked = run(SOURCE, goal='p(X)', proof=True).proof
        self.assertTrue(check_proof(SOURCE, asked, goals=['p(X)'])['valid'])
        self.invalid(asked, 'C7')
        orphan = check_proof(SOURCE, asked + "step(q('a'), clause(2), {'X': 'a'}, [p('a')])\n", goals=['p(X)'])
        self.assertEqual([failure['condition'] for failure in orphan['failures']], ['C7'])


if __name__ == '__main__':
    unittest.main()
