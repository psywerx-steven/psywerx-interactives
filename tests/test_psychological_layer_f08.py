"""Habit/automaticity measurement and comparator safeguards."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class HabitAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F08'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')

    def test_exact_five_drivers_and_full_fields(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n:03d}' for n in range(70,75)})
        self.assertTrue(all(e['entityType']=='DRIVER' for e in p.read(self.root/'BASELINE.json')['entities']))
        self.assertTrue(p.read(self.root/'coverage-review.json')['allCanonicalFieldsReviewed'])

    def test_three_existing_reviewed_once(self):
        rows=[r for r in p.read(p.STORE/'relationship-review-registry.json').values() if 'PSY-F08' in r['psychologicalFamilyIds']]
        self.assertEqual(len(rows),3)
        self.assertEqual({r['id'] for r in self.r['existingReviews']},{'REL-PSY-034','REL-PSY-035','REL-PSY-036'})
        self.assertEqual(next(r for r in rows if r['id']=='REL-PSY-036')['ownerFamilyId'],'PSY-F09')
        self.assertEqual(next(r for r in rows if r['id']=='REL-PSY-034')['primaryDisposition'],'RETYPE_CANDIDATE')
        self.assertFalse(any(r['implementationAuthorized'] for r in p.read(self.root/'revision-proposals.json')))

    def test_two_effects_remain_unknown(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertEqual({e['targetId'] for e in self.w['passB']['effectAssertions']},{'PSY-070','PSY-072'})
        for ea in self.w['passB']['effectAssertions']:
            self.assertEqual((ea['change'],ea['knowledgeStatus'],ea['governance']['lifecycleStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE','RESEARCH_NEEDED'))
        for ev in self.w['passB']['evidenceAssessments']:
            self.assertEqual(ev['synthesis']['disposition'],'INSUFFICIENT')

    def test_prepost_not_causal_and_comparator_null(self):
        f=self.w['passB']['evidenceAssessments'][0]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['MIXED','NULL_FINDING','MIXED','MIXED','NULL_FINDING'])
        for n in [0,2,3]: self.assertEqual(f[n]['supportedSemantics'],['ASSOCIATION'])
        self.assertEqual(f[1]['datasetIds'],f[2]['datasetIds'])
        self.assertIn('both conditions',f[1]['limitations'][0])
        self.assertIn('OUTSIDE',f[4]['limitations'][0])
        self.assertEqual(f[1]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')

    def test_priming_not_pathway(self):
        ev=self.w['passB']['evidenceAssessments'][1]
        self.assertIn('not identified transmitted pathway',ev['sourceFindings'][0]['limitations'][0])
        self.assertIn('OUTSIDE',ev['sourceFindings'][1]['limitations'][0])
        self.assertEqual(next(h for h in self.r['hypotheses'] if h['id']=='H-PSY-F08-06')['status'],'RESEARCH_NEEDED')

    def test_rejections_feature_scope_and_no_universal_duration(self):
        hs={h['id']:h for h in self.r['hypotheses']}
        for n in [2,3,7,8,9,11,14,16,18,22,25,27]:
            self.assertEqual(hs[f'H-PSY-F08-{n:02d}']['status'],'REJECTED_HYPOTHESIS')
        for n in [4,19]:
            self.assertEqual(hs[f'H-PSY-F08-{n:02d}']['status'],'BLOCKED_NEEDS_GOVERNANCE_INPUT')
        self.assertTrue({'PSY-071','PSY-073'} <= set(p.read(p.STORE/'architecture-escalations.json')[0]['entityIds']))
        self.assertFalse(any(e['targetId'] in {'PSY-071','PSY-073'} for e in self.w['passB']['effectAssertions']))

    def test_source_identity_and_provenance(self):
        x=next(s for s in self.r['canonicalSourceReviews'] if s['id']=='SRC120')
        self.assertEqual(x['status'],'STORED_TITLE_AUTHORS_YEAR_MISMATCH')
        self.assertIn('2008',x['finding'])
        self.assertIn('Luszczynska',x['finding'])
        for row in self.r['entityReviews']+self.r['existingReviews']+self.r['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids,row['id'])
        b.validate_sources()

    def test_five_driver_three_edge_coverage(self):
        a=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(a['drivers']),len(a['relationships'])),(5,3))
        for d in a['drivers']:
            self.assertEqual((len(d['originLayerSearch']),len(d['domainSearch']),len(d['effectProperties'])),(8,9,11))
            self.assertFalse(d['scientificUseEligibility'] or d['modelEligibility'] or d['practitionerActionEligibility'])

    def test_no_governance_no_rds_targets_or_practitioner_permission(self):
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
        self.assertTrue(p.check_protected()['passed'])

    def test_determinism_links(self):
        roots=[self.root,p.DOCS/'PSY-F08']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F08')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__': unittest.main()
