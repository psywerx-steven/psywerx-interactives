"""PSY-F04: intention, needs, task-choice and goal-measure safeguards."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class MotivationGoalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = p.STORE / 'PSY-F04'
        cls.research = p.read(cls.root / 'research.json')
        cls.w = p.read(cls.root / 'workspace.json')
        cls.master = p.read(p.STORE / 'relationship-review-registry.json')

    def test_actual_fifteen_drivers(self):
        expected = {f'PSY-{n:03d}' for n in range(26, 41)}
        self.assertEqual({r['id'] for r in self.research['entityReviews']}, expected)
        entities = p.read(self.root / 'BASELINE.json')['entities']
        self.assertEqual({r['id'] for r in entities}, expected)
        self.assertEqual({r['entityType'] for r in entities}, {'DRIVER'})

    def test_existing_review_once(self):
        new = {r['id'] for r in self.research['existingReviews']}
        reused = set(self.research['reusedExistingReviewIds'])
        incident = {r['id'] for r in self.master.values() if 'PSY-F04' in r['psychologicalFamilyIds']}
        self.assertEqual((len(new), len(reused), len(incident)), (8, 8, 16))
        self.assertFalse(new & reused)
        self.assertEqual(new | reused, incident)
        for rid in new:
            self.assertEqual(self.master[rid]['processingFamilyId'], 'PSY-F04')
        for rid in reused:
            self.assertNotEqual(self.master[rid]['processingFamilyId'], 'PSY-F04')

    def test_exact_scoped_interest_not_entire_motivation(self):
        ea = self.w['passB']['effectAssertions'][0]
        self.assertEqual((ea['targetId'], ea['property'], ea['change']), ('PSY-032', 'LEVEL', 'INCREASE'))
        self.assertIn('INTEREST/ENJOYMENT OF THAT HOMEWORK', ea['scope']['population'])
        self.assertIn('Seven-item IMI', ea['scope']['measurement'])
        self.assertIn('exclude competence/choice/value/effort/pressure', ea['scope']['measurement'])
        self.assertIn('not treated as independently randomized mediators', ea['mechanism'])
        self.assertEqual(ea['governance']['activationStatus'], 'NOT_ELIGIBLE')

    def test_mixed_nulls_and_measurement_scope(self):
        ev = self.w['passB']['evidenceAssessments'][0]
        self.assertEqual((ev['synthesis']['disposition'], ev['synthesis']['evidenceStrength'], ev['synthesis']['confidence']), ('MIXED', 'MODERATE', 'MODERATE'))
        findings = ev['sourceFindings']
        self.assertEqual(len(findings), 4)
        self.assertEqual([f['disposition'] for f in findings], ['SUPPORTS','MIXED','NULL_FINDING','NULL_FINDING'])
        self.assertIn('OUTSIDE', findings[2]['limitations'][0])
        self.assertIn('12 solvers excluded', findings[2]['design'])
        self.assertIn('not direct PSY-032 nulls', findings[3]['limitations'][0])
        for f in findings[2:]:
            self.assertEqual(f['nullInterpretation']['interpretation'], 'NO_DETECTED_DIFFERENCE')

    def test_review_primary_and_within_study_overlap(self):
        ev = self.w['passB']['evidenceAssessments'][0]
        self.assertEqual(ev['sourceFindings'][0]['datasetIds'], ev['sourceFindings'][3]['datasetIds'])
        overlap = p.read(p.STORE / 'source-overlap-registry.json')
        self.assertTrue(any(set(r['sourceIds']) == {'SRC-CAND-PSY-LAYER-0028','SRC-CAND-PSY-LAYER-0030'} for r in overlap))
        self.assertTrue(any(set(r['sourceIds']) == {'SRC160','SRC-501'} for r in overlap))

    def test_sources_reused_without_canonical_registration(self):
        sources = p.read(p.STORE / 'candidate-source-registry.json')
        self.assertFalse(any(r['id'] == 'SRC-CAND-PSY-LAYER-0040' for r in sources))
        self.assertTrue(any(r['id'] == 'SRC-467' and r['provisionalIdRetired'] == 'SRC-CAND-PSY-LAYER-0040' for r in sources))
        b.validate_sources()
        for row in self.research['entityReviews'] + self.research['existingReviews'] + self.research['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids, row['id'])
        src = {r['id']:r for r in self.research['canonicalSourceReviews']}
        self.assertIn('1748-5908-7-37', src['SRC109']['url'])
        self.assertIn('NOT a goal-conflict', src['SRC109']['finding'])

    def test_regret_inaction_not_universal_positive(self):
        r = self.master['REL-PSY-024']
        self.assertIn('not acting', r['frozenRecord']['mechanism'])
        self.assertIn('already inaction-qualified', r['review']['rationale'])
        self.assertIn('Action regret predicts weaker intention', r['review']['nullContrary'])
        self.assertEqual(r['review']['disposition'], 'REVISION_CANDIDATE')

    def test_goal_difficulty_and_trait_source_not_rewritten(self):
        r = self.master['REL-PSY-022']
        self.assertEqual(r['frozenRecord']['polarity'], 'NON_MONOTONIC')
        self.assertIn('NON_MONOTONIC', r['review']['rationale'])
        self.assertEqual(self.master['REL-PSY-041']['review']['disposition'], 'RESEARCH_NEEDED')
        self.assertFalse(self.w['passA']['relationshipCandidates'])

    def test_no_fake_pathway_or_moderator(self):
        ea = self.w['passB']['effectAssertions'][0]
        self.assertFalse(ea['moderatorLinks'])
        self.assertEqual(ea['interaction']['mode'], 'NONE')
        self.assertIn('no parallel autonomy', ea['contribution']['reconciliation'])
        self.assertFalse(self.w['passB']['occurrences'])

    def test_option_identity_not_partner_link_revision(self):
        ht = self.w['passB']['happeningTypes'][0]
        self.assertIn('not unrestricted action choice, partner-link revision', ht['description'])
        self.assertEqual(ht['controlProfiles'][0]['extent'], 'UNKNOWN')
        self.assertEqual(ht['governance']['activationStatus'], 'NOT_ELIGIBLE')

    def test_complete_honest_ledgers(self):
        ledgers = p.read(self.root / 'actions-events-search-ledger.json')
        self.assertEqual((len(ledgers['drivers']),len(ledgers['relationships'])), (15,16))
        query_ids = {q['id'] for q in self.research['searchLog']}
        for row in ledgers['drivers']:
            self.assertEqual((len(row['originLayerSearch']),len(row['domainSearch']),len(row['effectProperties'])), (8,9,11))
            self.assertTrue(set(row['queries']) <= query_ids)
            self.assertFalse(row['scientificUseEligibility'])
            self.assertFalse(row['modelEligibility'])
            self.assertFalse(row['practitionerActionEligibility'])
        self.assertEqual(sum(r['effectProperties']['LEVEL'] == 'SUPPORTED_EFFECT' for r in ledgers['drivers']), 1)

    def test_rds_rejection_and_protected_science(self):
        p.ae.validate_workspace(self.w, b.context())
        bad = copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId'] = 'PSY-078'
        with self.assertRaises(p.ae.ValidationError):
            p.ae.validate_workspace(bad, b.context())
        self.assertTrue(p.check_protected()['passed'])
        self.assertFalse(self.w['productionEligible'])

    def test_rejections_remain_hypotheses_not_governed_rejections(self):
        hypotheses = {r['id']:r for r in self.research['hypotheses']}
        for n in (1,3,5,8,9,13,14,18,24,27):
            self.assertEqual(hypotheses[f'H-PSY-F04-{n:02d}']['status'], 'REJECTED_HYPOTHESIS')
        for bucket in p.ae.COLLECTIONS:
            for row in self.w['passB'][bucket]:
                self.assertEqual(row['governance']['activationStatus'], 'NOT_ELIGIBLE')
                self.assertNotEqual(row['governance']['lifecycleStatus'], 'GOVERNED')

    def test_deterministic_output_and_local_links(self):
        roots = [self.root, p.DOCS / 'PSY-F04']
        before = {f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F04')
        self.assertEqual(before, {f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / unquote(target.split('#')[0])).exists())


if __name__ == '__main__':
    unittest.main()
