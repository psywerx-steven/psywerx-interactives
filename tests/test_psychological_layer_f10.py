"""Valuation, cue dependence and preference-versus-choice safeguards."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class ValuationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F10'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')

    def test_exact_ten_driver_ledgers(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n:03d}' for n in range(84,94)})
        led=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(led['drivers']),len(led['relationships'])),(10,4))
        for x in led['drivers']:
            self.assertEqual((len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties'])),(8,9,11))
            self.assertFalse(x['scientificUseEligibility'] or x['modelEligibility'] or x['practitionerActionEligibility'])

    def test_review_once_source_ownership(self):
        reg=p.read(p.STORE/'relationship-review-registry.json')
        incident={x['id'] for x in reg.values() if 'PSY-F10' in x['psychologicalFamilyIds']}
        own={x['id'] for x in self.r['existingReviews']}
        reused=set(self.r['reusedExistingReviewIds'])
        self.assertEqual((len(own),len(reused)),(2,2))
        self.assertFalse(own & reused)
        self.assertEqual(own|reused,incident)
        self.assertEqual(reg['REL-PSY-040']['ownerFamilyId'],'PSY-F14')
        self.assertEqual(reg['REL-INF-044']['ownerFamilyId'],'INF-F04')
        self.assertTrue(all(not x['implementationAuthorized'] for x in p.read(self.root/'revision-proposals.json')))

    def test_effects_not_forced_ready(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertEqual({x['targetId'] for x in self.w['passB']['effectAssertions']},{'PSY-089','PSY-093'})
        for x in self.w['passB']['effectAssertions']:
            self.assertEqual((x['change'],x['knowledgeStatus'],x['governance']['lifecycleStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE','RESEARCH_NEEDED'))
        self.assertTrue(all(x['synthesis']['disposition']=='INSUFFICIENT' for x in self.w['passB']['evidenceAssessments']))

    def test_eft_cue_null_and_horizon_not_mediation(self):
        f=self.w['passB']['evidenceAssessments'][0]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['SUPPORTS','NULL_FINDING','NULL_FINDING','MIXED','MIXED'])
        self.assertEqual(f[0]['datasetIds'],f[1]['datasetIds'])
        self.assertIn('OUTSIDE',f[1]['limitations'][0])
        self.assertIn('control',f[2]['result'])
        self.assertEqual(f[1]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')
        self.assertIn('indifference',self.w['passB']['effectAssertions'][0]['scope']['measurement'])

    def test_default_mixed_null_reverse_not_preference(self):
        f=self.w['passB']['evidenceAssessments'][1]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['SUPPORTS','NULL_FINDING','CONTRADICTED'])
        self.assertTrue(all(x['datasetIds']==f[0]['datasetIds'] for x in f))
        self.assertIn('subjective preference',f[0]['limitations'][0])
        self.assertIn('preference',self.w['passB']['effectAssertions'][1]['scope']['measurement'])

    def test_rate_beta_and_shared_measure_distinctions(self):
        rows={x['id']:x for x in self.r['entityReviews']}
        self.assertIn('beta parameter falls',rows['PSY-090']['measurementReview'])
        self.assertIn('LEVEL',rows['PSY-089']['unresolved'])
        self.assertIn('curves can cross',rows['PSY-087']['unresolved'].lower()+' '+rows['PSY-087']['measurementReview'].lower())
        self.assertTrue(all(x['property']=='LEVEL' for x in self.w['passB']['effectAssertions']))

    def test_source_identity_reuse_and_rejections(self):
        x=next(x for x in self.r['canonicalSourceReviews'] if x['id']=='SRC205')
        self.assertEqual(x['status'],'STORED_DOI_MISMATCH')
        self.assertIn('a0034418',x['finding'])
        self.assertIn('a0037917',x['finding'])
        src=p.read(p.STORE/'candidate-source-registry.json')
        self.assertEqual([s['id'] for s in src if s.get('pmid')=='9719656'],['SRC-408'])
        hs={h['id']:h for h in self.r['hypotheses']}
        for n in [2,4,6,8,9,11,13,14,16,18,20,22,28]:
            self.assertEqual(hs[f'H-PSY-F10-{n:02d}']['status'],'REJECTED_HYPOTHESIS')

    def test_references_isolation_and_rds(self):
        for row in self.r['entityReviews']+self.r['existingReviews']+self.r['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids,row['id'])
        b.validate_sources()
        self.assertFalse(p.ae.validate_workspace(self.w,b.context())['productionEligible'])
        for bucket in p.ae.COLLECTIONS:
            for x in self.w['passB'][bucket]:
                self.assertEqual(x['governance']['activationStatus'],'NOT_ELIGIBLE')
                self.assertNotEqual(x['governance']['lifecycleStatus'],'GOVERNED')
        for target in ['PSY-078','SOC-049']:
            bad=copy.deepcopy(self.w)
            bad['passB']['effectAssertions'][0]['targetId']=target
            with self.assertRaises(p.ae.ValidationError):p.ae.validate_workspace(bad,b.context())
        self.assertTrue(p.check_protected()['passed'])

    def test_determinism_and_local_links(self):
        roots=[self.root,p.DOCS/'PSY-F10']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F10')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__':unittest.main()
