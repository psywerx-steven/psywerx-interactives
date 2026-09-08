"""Memory/accessibility, temporal reversal and confidence-proxy audit checks."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class MemoryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F07'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')

    def test_exact_membership_fields(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n:03d}' for n in range(63,70)})
        self.assertTrue(all(e['entityType']=='DRIVER' for e in p.read(self.root/'BASELINE.json')['entities']))
        self.assertTrue(p.read(self.root/'coverage-review.json')['allCanonicalFieldsReviewed'])

    def test_four_incident_three_primary_one_reuse(self):
        rows=[r for r in p.read(p.STORE/'relationship-review-registry.json').values() if 'PSY-F07' in r['psychologicalFamilyIds']]
        self.assertEqual((len(rows),len(self.r['existingReviews']),self.r['reusedExistingReviewIds']),(4,3,['REL-PSY-031']))
        self.assertTrue(all(r['primaryDisposition'] for r in rows))
        self.assertEqual({p['existingId'] for p in p.read(self.root/'revision-proposals.json')},{'REL-INF-047'})
        self.assertEqual(next(r for r in rows if r['id']=='REL-INF-047')['ownerFamilyId'],'INF-F12')

    def test_veracity_not_confidence(self):
        r=next(r for r in self.r['existingReviews'] if r['id']=='REL-INF-047')
        self.assertIn('accuracy',r['rationale'])
        self.assertIn('confidence',r['rationale'])
        self.assertFalse(self.w['passA']['relationshipCandidates'])

    def test_delayed_not_immediate_universal_effect(self):
        ea=self.w['passB']['effectAssertions'][0]
        self.assertEqual((ea['targetId'],ea['change'],ea['governance']['lifecycleStatus']),('PSY-066','INCREASE','REVIEW_READY'))
        self.assertIn('Five-minute tests explicitly excluded',ea['scope']['context'])
        self.assertIn('30scored idea units',ea['scope']['measurement'])
        ev=self.w['passB']['evidenceAssessments'][0]
        self.assertEqual([f['disposition'] for f in ev['sourceFindings']],['SUPPORTS','CONTRADICTED','MIXED','NULL_FINDING','MIXED'])
        self.assertEqual((ev['synthesis']['disposition'],ev['synthesis']['evidenceStrength'],ev['synthesis']['confidence']),('MIXED','MODERATE','MODERATE'))
        self.assertEqual(ev['sourceFindings'][0]['datasetIds'],ev['sourceFindings'][1]['datasetIds'])

    def test_unequal_time_and_outside_null_preserved(self):
        f=self.w['passB']['evidenceAssessments'][0]['sourceFindings']
        self.assertIn('not matched total time',f[2]['limitations'][0])
        self.assertIn('OUTSIDE',f[3]['limitations'][0])
        self.assertIn('not PSY-068',f[3]['limitations'][0])
        self.assertEqual(f[3]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')

    def test_feedback_not_calibration_and_fails_closed(self):
        ea=self.w['passB']['effectAssertions'][1]
        self.assertEqual((ea['targetId'],ea['change'],ea['governance']['lifecycleStatus']),('PSY-068','UNKNOWN','RESEARCH_NEEDED'))
        ev=self.w['passB']['evidenceAssessments'][1]
        self.assertEqual(ev['synthesis']['disposition'],'INSUFFICIENT')
        self.assertEqual([f['disposition'] for f in ev['sourceFindings']],['MIXED','NULL_FINDING'])
        self.assertIn('overconfidence',ev['sourceFindings'][1]['result'])
        self.assertIn('correlation and calibration differ',ev['sourceFindings'][1]['limitations'][0])

    def test_knowledge_profile_and_mental_map_boundaries(self):
        hs={h['id']:h for h in self.r['hypotheses']}
        for n in [2,3,4,6,8,11,12,17,18,20,26]:
            self.assertEqual(hs[f'H-PSY-F07-{n:02d}']['status'],'REJECTED_HYPOTHESIS')
        self.assertEqual(hs['H-PSY-F07-10']['status'],'BLOCKED_NEEDS_GOVERNANCE_INPUT')
        self.assertFalse(any(e['targetId'] in {'PSY-064','PSY-065'} for e in self.w['passB']['effectAssertions']))
        self.assertIn('PSY-065',p.read(p.STORE/'architecture-escalations.json')[0]['entityIds'])

    def test_source_mismatch_and_reference_resolution(self):
        source=next(s for s in self.r['canonicalSourceReviews'] if s['id']=='SRC184')
        self.assertEqual(source['status'],'STORED_PMID_IDENTITY_MISMATCH')
        self.assertIn('28395650',source['url'])
        self.assertIn('28373571',source['finding'])
        for row in self.r['entityReviews']+self.r['existingReviews']+self.r['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids,row['id'])
        b.validate_sources()

    def test_seven_driver_four_edge_ledgers(self):
        a=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(a['drivers']),len(a['relationships'])),(7,4))
        for d in a['drivers']:
            self.assertEqual((len(d['originLayerSearch']),len(d['domainSearch']),len(d['effectProperties'])),(8,9,11))
            self.assertFalse(d['scientificUseEligibility'] or d['modelEligibility'] or d['practitionerActionEligibility'])

    def test_candidate_status_rds_protection_and_identity_scope(self):
        for bucket in p.ae.COLLECTIONS:
            for record in self.w['passB'][bucket]:
                self.assertEqual(record['governance']['activationStatus'],'NOT_ELIGIBLE')
                self.assertNotEqual(record['governance']['lifecycleStatus'],'GOVERNED')
        for ht in self.w['passB']['happeningTypes']:
            self.assertIn('permission',ht['description'])
            self.assertEqual(ht['controlProfiles'][0]['extent'],'UNKNOWN')
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(p.ae.ValidationError): p.ae.validate_workspace(bad,b.context())
        self.assertTrue(p.check_protected()['passed'])

    def test_determinism_local_links(self):
        roots=[self.root,p.DOCS/'PSY-F07']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F07')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__': unittest.main()
