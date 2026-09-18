"""Norm/perception, external-RDS and shared-review safeguards for PSY-F03."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class NormPerceptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = p.STORE / 'PSY-F03'
        cls.research = p.read(cls.root / 'research.json')
        cls.w = p.read(cls.root / 'workspace.json')
        cls.master = p.read(p.STORE / 'relationship-review-registry.json')

    def test_actual_twelve_driver_membership(self):
        ids = {f'PSY-{n:03d}' for n in range(16,26)} | {'PSY-133','PSY-134'}
        self.assertEqual({r['id'] for r in self.research['entityReviews']}, ids)
        frozen = p.read(self.root / 'BASELINE.json')['entities']
        self.assertEqual({e['id'] for e in frozen}, ids)
        self.assertEqual({e['entityType'] for e in frozen}, {'DRIVER'})

    def test_twenty_new_reviews_one_prior_reused(self):
        records = self.research['existingReviews']
        self.assertEqual(len(records), 20)
        self.assertNotIn('REL-PSY-016', {r['id'] for r in records})
        self.assertEqual(self.research['reusedExistingReviewIds'], ['REL-PSY-016'])
        incident = [r for r in self.master.values() if 'PSY-F03' in r['psychologicalFamilyIds']]
        self.assertEqual(len(incident), 21)
        self.assertTrue(all(r['primaryDisposition'] for r in incident))
        self.assertEqual(self.master['REL-PSY-016']['processingFamilyId'], 'PSY-F02')
        for r in records:
            self.assertEqual(self.master[r['id']]['processingFamilyId'], 'PSY-F03')

    def test_external_rds_not_overlooked(self):
        rec = self.master['REL-SOC-067']['frozenRecord']
        self.assertEqual(rec['subjectEntityType'], 'RELATIONAL_DERIVED_STATE')
        self.assertEqual(rec['subjectEntityId'], 'SOC-096')
        review = self.master['REL-SOC-067']['review']
        self.assertIn('HEIGHTENED_CAUSAL', review['nullContrary'])
        self.assertEqual(review['disposition'], 'RESEARCH_NEEDED')
        self.assertIn('GROUP_A_STATUS', p.read(self.root / 'coverage-review.json')['rdsReview'])

    def test_production_validators_and_source_resolution(self):
        p.ae.validate_workspace(self.w, b.context())
        self.assertFalse(self.w['productionEligible'])
        b.validate_sources()
        for row in self.research['entityReviews'] + self.research['existingReviews'] + self.research['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids, row['id'])

    def test_exclusion_target_is_exact_young_adult_perception(self):
        e = self.w['passB']['effectAssertions'][0]
        self.assertEqual((e['targetId'], e['property'], e['change']), ('PSY-024','LEVEL','INCREASE'))
        self.assertIn('DURING THAT GAME', e['scope']['population'])
        self.assertIn('young-adult', e['scope']['population'])
        self.assertIn('not treated as an independently randomized mediator', e['mechanism'])
        self.assertIn('REL-SOC-062', e['contribution']['reconciliation'])
        self.assertFalse(self.w['passA']['relationshipCandidates'])

    def test_child_null_preserved_without_equivalence(self):
        f = self.w['passB']['evidenceAssessments'][0]['sourceFindings'][2]
        self.assertEqual(f['disposition'], 'NULL_FINDING')
        self.assertEqual(f['nullInterpretation']['interpretation'], 'NO_DETECTED_DIFFERENCE')
        self.assertIn('OUTSIDE', f['limitations'][0])
        self.assertIn('40 children', f['design'])

    def test_norm_effect_remains_unknown(self):
        e = self.w['passB']['effectAssertions'][1]
        self.assertEqual((e['targetId'],e['change'],e['knowledgeStatus']), ('PSY-016','UNKNOWN','INSUFFICIENT_EVIDENCE'))
        self.assertEqual(e['governance']['lifecycleStatus'], 'RESEARCH_NEEDED')
        ev = self.w['passB']['evidenceAssessments'][1]
        self.assertEqual(ev['completeness']['measurement'], 'MISSING')
        f = ev['sourceFindings'][2]
        self.assertIn('NOT direct perceived-norm', f['measurement'])
        self.assertEqual(f['disposition'], 'NULL_FINDING')

    def test_no_direct_rds_target_or_ontology_tie_edit(self):
        bad = copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId'] = 'SOC-096'
        with self.assertRaises(p.ae.ValidationError):
            p.ae.validate_workspace(bad, b.context())
        self.assertTrue(all(not e['moderatorLinks'] for e in self.w['passB']['effectAssertions']))
        self.assertFalse(self.w['passB']['occurrences'])
        self.assertIn('PSYWERX Relationship edit', self.w['passB']['happeningTypes'][0]['description'])

    def test_twelve_ledgers_full_dimensions_honest_no_findings(self):
        ledger = p.read(self.root / 'actions-events-search-ledger.json')
        self.assertEqual(len(ledger['drivers']),12)
        self.assertEqual(len(ledger['relationships']),21)
        queries = {q['id'] for q in self.research['searchLog']}
        for r in ledger['drivers']:
            self.assertEqual((len(r['originLayerSearch']),len(r['domainSearch']),len(r['effectProperties'])), (8,9,11))
            self.assertTrue(set(r['queries']) <= queries)
            self.assertFalse(r['scientificUseEligibility'])
            self.assertFalse(r['modelEligibility'])
            self.assertFalse(r['practitionerActionEligibility'])

    def test_feature_scope_block_and_sources_unrepaired(self):
        issues = p.read(p.STORE / 'architecture-escalations.json')
        self.assertTrue(any('PSY-022' in i['entityIds'] and not i['productionChangeAuthorized'] for i in issues))
        c = {r['id']:r for r in self.research['canonicalSourceReviews']}
        self.assertEqual(c['SRC172']['status'], 'IDENTIFIER_UNRESOLVED')
        self.assertEqual(c['SRC-503']['status'], 'CAUSAL_LIMIT_EXPLICIT')
        self.assertTrue(p.check_protected()['passed'])

    def test_all_candidate_science_not_eligible(self):
        for bucket in p.ae.COLLECTIONS:
            for r in self.w['passB'][bucket]:
                self.assertEqual(r['governance']['activationStatus'], 'NOT_ELIGIBLE')
                self.assertNotEqual(r['governance']['lifecycleStatus'], 'GOVERNED')

    def test_deterministic_output_and_links(self):
        roots=[self.root,p.DOCS / 'PSY-F03']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F03')
        after={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        self.assertEqual(before,after)
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / unquote(target.split('#')[0])).exists())


if __name__ == '__main__':
    unittest.main()
