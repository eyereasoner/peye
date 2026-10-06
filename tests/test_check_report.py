import unittest

from peye import Struct, build, check_proof, check_report, facts_from, read_terms, run, verdict_text

from helpers import program


def facts(report):
    return [term for term, _ in read_terms(check_report(report))]


def named(records, name):
    return [record for record in records if isinstance(record, Struct) and record.name == name]


class CheckReports(unittest.TestCase):
    def test_reports_expose_coverage_and_source_and_primitive_counts(self):
        source = program("p, q = preds('p q')\nX = vars('X')\nfact(p('a'))\n"
                         "backward(q(X), p(X), unify(X, 'a'))")
        report = check_proof(source, run(source, goal='q(X)', proof=True).proof, goals=['q(X)'])
        self.assertEqual(report['conditions'], [
            {'id': 'C1', 'name': 'resolution', 'covered': 2, 'failed': 0},
            {'id': 'C2', 'name': 'well_founded', 'covered': 3, 'failed': 0},
            {'id': 'C3', 'name': 'justification', 'covered': 3, 'failed': 0},
            {'id': 'C4', 'name': 'coverage', 'covered': 3, 'failed': 0},
            {'id': 'C5', 'name': 're_decision', 'covered': 1, 'failed': 0},
            {'id': 'C6', 'name': 'boundary_consistency', 'covered': 0, 'failed': 0},
            {'id': 'C7', 'name': 'relevance', 'covered': 4, 'failed': 0},
        ])
        self.assertEqual(report['uses'], 2)
        self.assertEqual(verdict_text(report), "verdict('checked')\n")
        self.assertEqual(len(named(facts(report), 'condition')), 7)
        self.assertIn('recomputed(1)\n', check_report(report))

    def test_each_failed_condition_is_represented_with_counts_and_a_failure(self):
        cases = [
            ('C1', "p = preds('p')\nfact(p('a'))", "p('b')\nstep(p('b'), fact(1), {}, [])"),
            ('C2', "p = preds('p')\nbackward(p, p)", "p()\nstep(p(), rule(1), {}, [p()])"),
            ('C3', '', "p()\nstep(p(), 'magic', {}, [])"),
            ('C4', '', "missing()\ntrue()\nstep(true(), 'builtin', {}, [])"),
            ('C5', '', "is_(7, 2 + 3)\nstep(is_(7, 2 + 3), 'builtin', {}, [])"),
            ('C6', "p, q = preds('p q')\nfact(p('a'))\nforward(q, ~p('a'))",
             "q()\nstep(q(), rule(2), {}, [~p('a')])\nstep(~p('a'), 'absent', {}, [])"),
            ('C7', "p = preds('p')\nfact(p('a'))", "p('a')\nstep(p('a'), fact(1), {}, [])"),
        ]
        for condition_id, source, document in cases:
            with self.subTest(condition_id):
                report = check_proof(program(source), document)
                records = facts(report)
                condition = next(r for r in named(records, 'condition') if r.args[0] == condition_id)
                self.assertEqual(condition.args[2].name, 'failed')
                self.assertEqual(condition.args[2].args[0],
                                 sum(1 for f in report['failures'] if f['condition'] == condition_id))
                failure = next(r for r in named(records, 'failure') if r.args[0] == condition_id)
                self.assertNotEqual(failure.args[1], 'proof_document')
                self.assertEqual(records[-1].args[0].name, 'failed')
                self.assertEqual(records[-1].args[0].args[0], len(report['failures']))

    def test_control_composition_is_counted_under_c5(self):
        source = program("p = preds('p')\nfact(p('a'))")
        report = check_proof(source, run(source, goal="call(p('a'))", proof=True).proof, goals=["call(p('a'))"])
        self.assertEqual(report['verified'], 1)
        self.assertEqual(report['composed'], 1)
        self.assertEqual(report['conditions'][0]['covered'], 1)
        self.assertEqual(report['conditions'][4]['covered'], 1)
        self.assertIn('composed(1)\n', check_report(report))
        invalid = check_proof(source, "call(p('b'))\nstep(call(p('b')), 'control', {}, [p('a')])")
        self.assertGreater(invalid['conditions'][4]['failed'], 0)

    def test_obligations_carry_goal_terms_and_strict_checking_fails_c5(self):
        source = program("p, out, missing = preds('p out missing')\nX = vars('X')\n"
                         "fact(p('a'))\nforward(out(X), p(X), ~missing(X))")
        document = run(source, proof=True).proof
        report = check_proof(source, document)
        obligation = named(facts(report), 'obligation')[0]
        self.assertEqual(obligation.args[0], 'absent')
        self.assertEqual(obligation.args[1], 'theory_scoped')
        self.assertEqual(obligation.args[2].name, '~')
        self.assertEqual(verdict_text(report), "verdict('checked_with_obligations')\n")
        strict = check_proof(source, document, allow_trusted=False)
        self.assertEqual(strict['conditions'][4]['failed'], 1)
        self.assertIn("condition('C5', 're_decision', failed(1), 0)\n", check_report(strict))

    def test_a_strict_verdict_follows_from_the_report_on_every_example(self):
        import os
        import sys
        from peye import load
        from peye.proof import public_report, strict
        from helpers import ROOT
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        from corpus import read_manifest, source_path
        for entry in read_manifest():
            if entry['name'] in ('deep-taxonomy-10000', 'path-discovery'):
                continue  # large, and nothing a smaller one does not show
            with self.subTest(entry['name']):
                program = load(source_path(entry))
                proved = run(program, proof=True)
                derived = strict(proved.proof_report)
                checked = check_proof(program, proved.proof, allow_trusted=False)
                self.assertEqual(check_report(derived), check_report(checked))
                self.assertEqual(public_report(derived), public_report(checked))

    def test_reports_can_be_loaded_and_queried_as_ordinary_data(self):
        source = program("p, q = preds('p q')\nX = vars('X')\nfact(p('a'))\nforward(q(X), p(X))")
        data = check_report(check_proof(source, run(source, proof=True).proof))
        facts_program = build(lambda: facts_from(text=data))
        self.assertEqual(run(facts_program, goal="condition('C1', Name, 'ok', Count)").answers,
                         ["condition('C1', 'resolution', 'ok', 2)"])
        self.assertEqual(run(facts_program, goal='verdict(Result)').answers, ["verdict('checked')"])

    def test_malformed_document_diagnostics_stay_readable_data(self):
        report = check_proof(program(''), "p('unterminated")
        records = facts(report)
        self.assertEqual(len(named(records, 'condition')), 7)
        failure = named(records, 'failure')[0]
        self.assertEqual(failure.args[1], 'proof_document')
        self.assertEqual(failure.args[2], report['failures'][0]['detail'])
        self.assertEqual(str(records[-1]), f"verdict(failed({len(report['failures'])}))")


if __name__ == '__main__':
    unittest.main()
