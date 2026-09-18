"""Attention/resource/nominal-frame and prior-pilot noninterference checks."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class CognitiveProcessingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = p.STORE / 'PSY-F06'
        cls.r = p.read(cls.root / 'research.json')
        cls.w = p.read(cls.root / 'workspace.json')
        cls.registry = p.read(p.STORE / 'relationship-review-registry.json')

    def test_eight_actual_drivers_all_fields(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']}, {f'PSY-{n:03d}' for n in range(55,63)})
        self.assertTrue(all(e['entityType']=='DRIVER' for e in p.read(self.root/'BASELINE.json')['entities']))
        self.assertTrue(p.read(self.root/'coverage-review.json')['allCanonicalFieldsReviewed'])

    def test_fifteen_incident_twelve_primary_three_reused(self):
        rows=[r for r in self.registry.values() if 'PSY-F06' in r['psychologicalFamilyIds']]
        self.assertEqual((len(rows),len(self.r['existingReviews']),len(self.r['reusedExistingReviewIds'])),(15,12,3))
        self.assertTrue(all(r['primaryDisposition'] for r in rows))
        self.assertEqual(set(self.r['reusedExistingReviewIds']),{'REL-PSY-007','REL-PSY-025','REL-PSY-059'})

    def test_prior_pilot_proposals_referenced_not_recreated(self):
        proposals=p.read(self.root/'revision-proposals.json')
        self.assertEqual({r['existingId'] for r in proposals},{'REL-ENV-045','REL-PSY-028','REL-PSY-039'})
        refs=self.r['reusedProposalReferences']
        self.assertEqual({r['existingId'] for r in refs},{'REL-BIO-021','REL-INF-041'})
        self.assertTrue(all(not r['newProposalCreated'] and not r['implementationAuthorized'] for r in refs))
        self.assertTrue(p.check_protected()['passed'])

    def test_both_effects_fail_closed_on_exact_construct(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        for ea in self.w['passB']['effectAssertions']:
            self.assertEqual((ea['governance']['lifecycleStatus'],ea['change'],ea['knowledgeStatus']),('RESEARCH_NEEDED','UNKNOWN','INSUFFICIENT_EVIDENCE'))
            self.assertEqual(ea['targetKind'],'DRIVER')
        for ev in self.w['passB']['evidenceAssessments']:
            self.assertEqual((ev['synthesis']['disposition'],ev['synthesis']['evidenceStrength'],ev['synthesis']['confidence']),('INSUFFICIENT','LIMITED','LOW'))

    def test_cue_proxy_and_moderator_null_not_mediation(self):
        ev=self.w['passB']['evidenceAssessments'][0]
        self.assertEqual([f['disposition'] for f in ev['sourceFindings']],['MIXED','MIXED','NULL_FINDING'])
        self.assertIn('perceived difficulty',ev['sourceFindings'][0]['measurement'])
        self.assertIn('mediation',ev['sourceFindings'][0]['limitations'][0])
        self.assertEqual(ev['sourceFindings'][2]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')
        self.assertEqual(ev['sourceFindings'][1]['datasetIds'],ev['sourceFindings'][2]['datasetIds'])

    def test_task_transfer_not_general_resource_increase(self):
        ev=self.w['passB']['evidenceAssessments'][1]
        self.assertEqual([f['disposition'] for f in ev['sourceFindings']],['MIXED','SUPPORTS','NULL_FINDING'])
        self.assertIn('task-specific',ev['sourceFindings'][0]['result'])
        self.assertIn('OUTSIDE',ev['sourceFindings'][2]['limitations'][0])
        self.assertEqual(ev['sourceFindings'][1]['datasetIds'],ev['sourceFindings'][2]['datasetIds'])

    def test_nominal_frame_not_ordinal_effect(self):
        ledger=next(d for d in p.read(self.root/'actions-events-search-ledger.json')['drivers'] if d['driverId']=='PSY-060')
        self.assertEqual(ledger['effectProperties']['LEVEL'],'NOT_APPLICABLE')
        self.assertFalse(ledger['candidateEffectIds'])
        self.assertEqual(next(h for h in self.r['hypotheses'] if h['id']=='H-PSY-F06-16')['status'],'REJECTED_HYPOTHESIS')
        self.assertTrue(all(ea['targetId']!='PSY-060' for ea in self.w['passB']['effectAssertions']))

    def test_hypothesis_same_construct_reference_is_not_duplicate(self):
        for q in self.w['passA']['gapQuestions']:
            self.assertEqual(len(q['recordIds']),len(set(q['recordIds'])))
        q=next(q for q in self.w['passA']['gapQuestions'] if q['id']=='H-PSY-F06-17')
        self.assertEqual(q['recordIds'],['PSY-060'])
        self.assertEqual(q['status'],'RESEARCH_NEEDED')

    def test_source_mismatch_reuse_and_resolution(self):
        sources={s['id']:s for s in self.r['canonicalSourceReviews']}
        self.assertEqual(sources['SRC171']['status'],'STORED_TITLE_YEAR_PMID_MISMATCH')
        self.assertIn('17999571',sources['SRC171']['url'])
        self.assertIn('19638628',sources['SRC125']['url'])
        allsources=p.read(p.STORE/'candidate-source-registry.json')
        self.assertNotIn('SRC-CAND-PSY-LAYER-0065',{s['id'] for s in allsources})
        self.assertIn('SRC340',{s['id'] for s in allsources})
        for row in self.r['entityReviews']+self.r['existingReviews']+self.r['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids,row['id'])
        b.validate_sources()

    def test_all_driver_and_edge_ledgers(self):
        ledgers=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(ledgers['drivers']),len(ledgers['relationships'])),(8,15))
        for row in ledgers['drivers']:
            self.assertEqual((len(row['originLayerSearch']),len(row['domainSearch']),len(row['effectProperties'])),(8,9,11))
            self.assertFalse(row['scientificUseEligibility'] or row['modelEligibility'] or row['practitionerActionEligibility'])

    def test_no_authority_or_rds_target(self):
        for bucket in p.ae.COLLECTIONS:
            for row in self.w['passB'][bucket]:
                self.assertEqual(row['governance']['activationStatus'],'NOT_ELIGIBLE')
                self.assertNotEqual(row['governance']['lifecycleStatus'],'GOVERNED')
        for ht in self.w['passB']['happeningTypes']:
            self.assertIn('permission',ht['description'])
            self.assertEqual(ht['controlProfiles'][0]['extent'],'UNKNOWN')
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(p.ae.ValidationError): p.ae.validate_workspace(bad,b.context())

    def test_determinism_links(self):
        roots=[self.root,p.DOCS/'PSY-F06']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F06')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__': unittest.main()
