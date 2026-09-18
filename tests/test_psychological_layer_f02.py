"""PSY-F02 exact scope, evidence and incremental Family gates."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class RiskAppraisalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = p.STORE / 'PSY-F02'
        cls.research = p.read(cls.root / 'research.json')
        cls.w = p.read(cls.root / 'workspace.json')

    def test_exact_actual_entities(self):
        expected = {f'PSY-{n:03d}' for n in range(8,16)} | {'PSY-132'}
        self.assertEqual({r['id'] for r in self.research['entityReviews']}, expected)
        self.assertEqual({e['id'] for e in p.read(self.root / 'BASELINE.json')['entities']}, expected)

    def test_fourteen_unique_existing_reviews(self):
        records = self.research['existingReviews']
        frozen = p.read(self.root / 'BASELINE.json')['legacyIncidentByBucket']['relationships']
        self.assertEqual(len(records), 14)
        self.assertEqual({r['id'] for r in records}, {r['id'] for r in frozen})
        master = p.read(p.STORE / 'relationship-review-registry.json')
        for row in records:
            self.assertEqual(master[row['id']]['processingFamilyId'], 'PSY-F02')
            self.assertEqual(master[row['id']]['primaryDisposition'], row['disposition'])

    def test_governed_candidate_validators(self):
        p.ae.validate_workspace(self.w, b.context())
        self.assertFalse(self.w['productionEligible'])

    def test_task_control_scope_not_stressor_or_life_agency(self):
        effect = self.w['passB']['effectAssertions'][0]
        self.assertEqual((effect['targetId'], effect['change']), ('PSY-013','INCREASE'))
        self.assertIn('OVER THAT TASK', effect['scope']['population'])
        self.assertIn('not specifically', effect['scope']['population'])
        self.assertEqual(self.w['passB']['evidenceAssessments'][0]['synthesis']['evidenceStrength'], 'LIMITED')

    def test_helplessness_proxy_remains_unknown(self):
        e = self.w['passB']['effectAssertions'][1]
        self.assertEqual((e['targetId'], e['change'], e['knowledgeStatus']), ('PSY-015','UNKNOWN','INSUFFICIENT_EVIDENCE'))
        self.assertEqual(e['governance']['lifecycleStatus'], 'RESEARCH_NEEDED')
        ev = self.w['passB']['evidenceAssessments'][1]
        self.assertEqual(ev['completeness']['measurement'], 'MISSING')
        self.assertEqual(ev['synthesis']['disposition'], 'INSUFFICIENT')

    def test_one_contribution_not_two_propagating_routes(self):
        e = self.w['passB']['effectAssertions']
        self.assertEqual({r['contribution']['groupId'] for r in e}, {'CONTRIB-PSY-LAYER-CONTINGENCY-001'})
        self.assertEqual([r['contribution']['role'] for r in e], ['PRIMARY','DESCRIPTIVE_ONLY'])
        bad = copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][1]['contribution']['role'] = 'PRIMARY'
        with self.assertRaisesRegex(p.ae.ValidationError, 'Duplicate contribution'):
            p.ae.validate_workspace(bad, b.context())

    def test_nine_ledgers_and_references(self):
        ledgers = p.read(self.root / 'actions-events-search-ledger.json')['drivers']
        self.assertEqual(len(ledgers), 9)
        queries = {q['id'] for q in self.research['searchLog']}
        for row in ledgers:
            self.assertEqual((len(row['originLayerSearch']),len(row['domainSearch']),len(row['effectProperties'])), (8,9,11))
            self.assertTrue(set(row['queries']) <= queries)
            self.assertTrue(set(row['sources']) <= b.context().source_ids)
            self.assertFalse(row['scientificUseEligibility'])
            self.assertFalse(row['modelEligibility'])
            self.assertFalse(row['practitionerActionEligibility'])
        for row in self.research['entityReviews'] + self.research['existingReviews'] + self.research['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids, row['id'])

    def test_source_overlap_and_conflict_remain(self):
        self.assertTrue(any(r['id']=='SRC124' and 'CONFLICT' in r['status'] for r in self.research['canonicalSourceReviews']))
        overlap = p.read(p.STORE / 'source-overlap-registry.json')
        self.assertTrue(any(set(r['sourceIds']) == {'SRC122','SRC-496'} for r in overlap))
        self.assertTrue(any('54%' in r['rule'] for r in overlap))

    def test_no_formal_causal_edge_or_mediation_from_proxy(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertFalse(self.w['passB']['occurrences'])
        for e in self.w['passB']['effectAssertions']:
            self.assertFalse(e['moderatorLinks'])

    def test_no_supported_null_from_nonsignificance(self):
        f = self.w['passB']['evidenceAssessments'][1]['sourceFindings'][1]
        self.assertEqual(f['disposition'], 'NULL_FINDING')
        self.assertEqual(f['nullInterpretation']['interpretation'], 'NO_DETECTED_DIFFERENCE')

    def test_science_and_prior_pilots_untouched(self):
        self.assertTrue(p.check_protected()['passed'])
        for bucket in p.ae.COLLECTIONS:
            for row in self.w['passB'][bucket]:
                self.assertEqual(row['governance']['activationStatus'], 'NOT_ELIGIBLE')
                self.assertNotEqual(row['governance']['lifecycleStatus'], 'GOVERNED')

    def test_deterministic_render_and_local_links(self):
        import re
        from urllib.parse import unquote
        roots=[self.root,p.DOCS / 'PSY-F02']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F02')
        after={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        self.assertEqual(before,after)
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / unquote(target.split('#')[0])).exists())


if __name__ == '__main__':
    unittest.main()
