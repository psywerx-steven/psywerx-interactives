"""Identity, trait timing, profile components and source-design safeguards."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class IdentityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F11'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')

    def test_exact_entities_and_search_dimensions(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n:03d}' for n in range(94,104)})
        led=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(led['drivers']),len(led['relationships'])),(10,6))
        for x in led['drivers']:
            self.assertEqual((len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties'])),(8,9,11))
            self.assertFalse(x['scientificUseEligibility'] or x['modelEligibility'] or x['practitionerActionEligibility'])

    def test_review_once_and_component_retype_not_implemented(self):
        reg=p.read(p.STORE/'relationship-review-registry.json')
        incident={x['id'] for x in reg.values() if 'PSY-F11' in x['psychologicalFamilyIds']}
        own={x['id'] for x in self.r['existingReviews']}
        reused=set(self.r['reusedExistingReviewIds'])
        self.assertEqual((len(own),len(reused)),(5,1))
        self.assertFalse(own & reused)
        self.assertEqual(own|reused,incident)
        self.assertEqual(reg['REL-PSY-065']['primaryDisposition'],'RETYPE_CANDIDATE')
        self.assertEqual(reg['REL-CUL-049']['ownerFamilyId'],'CUL-F13')
        self.assertTrue(all(not x['implementationAuthorized'] for x in p.read(self.root/'revision-proposals.json')))

    def test_three_unknown_effects_no_new_edges(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertEqual({x['targetId'] for x in self.w['passB']['effectAssertions']},{'PSY-100','PSY-102','PSY-098'})
        for x in self.w['passB']['effectAssertions']:
            self.assertEqual((x['change'],x['knowledgeStatus'],x['governance']['lifecycleStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE','RESEARCH_NEEDED'))
        self.assertTrue(all(x['synthesis']['disposition']=='INSUFFICIENT' for x in self.w['passB']['evidenceAssessments']))

    def test_affirmation_proxy_and_distinct_operation_null(self):
        f=self.w['passB']['evidenceAssessments'][0]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['MIXED','SUPPORTS','NULL_FINDING','MIXED'])
        self.assertTrue(all('OUTSIDE' in x['limitations'][0] for x in f))
        self.assertEqual(f[2]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')

    def test_dissonance_artifact_not_all_discomfort_false(self):
        f=self.w['passB']['evidenceAssessments'][1]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['SUPPORTS','INSUFFICIENT'])
        self.assertIn('not empirical proof all dissonance',f[1]['limitations'][0])
        self.assertNotIn('EXPERIMENTAL',f[1]['basis'])

    def test_fusion_source_inconsistency_and_no_trait_transfer(self):
        f=self.w['passB']['evidenceAssessments'][2]['sourceFindings']
        self.assertIn('internally inconsistent',f[0]['result'])
        self.assertIsNone(f[0]['quantitativeEstimate'])
        self.assertIn('enduring',f[0]['limitations'][0])
        self.assertEqual(f[1]['basis'],['OBSERVATIONAL_CROSS_SECTIONAL'])
        self.assertEqual(f[1]['supportedSemantics'],['ASSOCIATION'])
        self.assertNotIn('EXPERIMENTAL',f[2]['basis'])
        self.assertIn('not empirical observation',f[2]['limitations'][0])

    def test_rejections_and_unresolved_profile(self):
        hs={h['id']:h for h in self.r['hypotheses']}
        for n in [2,4,5,8,9,10,12,15,18,21,23,25,30]:
            self.assertEqual(hs[f'H-PSY-F11-{n:02d}']['status'],'REJECTED_HYPOTHESIS')
        ar=p.read(p.STORE/'architecture-escalations.json')[0]
        self.assertIn('PSY-097',ar['entityIds'])
        self.assertFalse(ar['productionChangeAuthorized'])

    def test_source_references_isolation_and_rds(self):
        for row in self.r['entityReviews']+self.r['existingReviews']+self.r['hypotheses']:
            self.assertTrue(set(row['sources'])<=b.context().source_ids,row['id'])
        b.validate_sources()
        self.assertFalse(p.ae.validate_workspace(self.w,b.context())['productionEligible'])
        for bucket in p.ae.COLLECTIONS:
            for x in self.w['passB'][bucket]:
                self.assertEqual(x['governance']['activationStatus'],'NOT_ELIGIBLE')
                self.assertNotEqual(x['governance']['lifecycleStatus'],'GOVERNED')
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(p.ae.ValidationError):p.ae.validate_workspace(bad,b.context())
        self.assertTrue(p.check_protected()['passed'])

    def test_determinism_and_links(self):
        roots=[self.root,p.DOCS/'PSY-F11']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F11')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__':unittest.main()
