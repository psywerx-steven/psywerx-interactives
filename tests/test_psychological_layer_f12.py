"""Agency, reactance component and nominal attribution safeguards."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class AgencyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F12'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')

    def test_membership_and_complete_search(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n:03d}' for n in [*range(104,113),135]})
        led=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(led['drivers']),len(led['relationships'])),(10,8))
        for x in led['drivers']:
            self.assertEqual((len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties'])),(8,9,11))

    def test_review_once_and_no_retype_implementation(self):
        reg=p.read(p.STORE/'relationship-review-registry.json')
        incident={x['id'] for x in reg.values() if 'PSY-F12' in x['psychologicalFamilyIds']}
        own={x['id'] for x in self.r['existingReviews']}
        reused=set(self.r['reusedExistingReviewIds'])
        self.assertEqual((len(own),len(reused)),(6,2))
        self.assertFalse(own & reused)
        self.assertEqual(own|reused,incident)
        self.assertEqual(reg['REL-PSY-048']['primaryDisposition'],'RETYPE_CANDIDATE')
        self.assertTrue(all(not x['implementationAuthorized'] for x in p.read(self.root/'revision-proposals.json')))

    def test_scoped_threat_and_unknown_proxy_effects(self):
        effects=self.w['passB']['effectAssertions']
        self.assertEqual([(x['targetId'],x['change']) for x in effects],[('PSY-108','INCREASE'),('PSY-104','UNKNOWN'),('PSY-135','UNKNOWN')])
        self.assertIn('four-item',effects[0]['scope']['measurement'])
        self.assertEqual([x['synthesis']['disposition'] for x in self.w['passB']['evidenceAssessments']],['MIXED','INSUFFICIENT','INSUFFICIENT'])
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertNotIn('PSY-106',{x['targetId'] for x in effects})

    def test_null_scope_and_measure_dissociation(self):
        assessments=self.w['passB']['evidenceAssessments']
        frame=assessments[0]['sourceFindings'][-1]
        self.assertIn('OUTSIDE',frame['limitations'][0])
        self.assertEqual(frame['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')
        agency=assessments[1]['sourceFindings'][1]
        self.assertEqual(agency['basis'],['OBSERVATIONAL_CROSS_SECTIONAL'])
        self.assertEqual(agency['supportedSemantics'],['ASSOCIATION'])
        self.assertIn('OUTSIDE',assessments[2]['sourceFindings'][1]['limitations'][0])

    def test_canonical_mismatch_recorded_not_repaired(self):
        source=next(x for x in self.r['canonicalSourceReviews'] if x['id']=='SRC197')
        self.assertIn('27765344',source['finding'])
        self.assertIn('27621713',source['finding'])
        self.assertTrue(p.check_protected()['passed'])

    def test_same_title_distinct_year_but_doi_duplicates_fail(self):
        self.assertGreaterEqual(b.validate_sources(),160)
        s={'id':'SRC-CAND-TEST','doi':'10.1/new','title':'Same title','year':2021,'pmid':None}
        c={'id':'SRC-OLD','title':'Same title','year':2010,'doi':'10.1/old'}
        original=p.read
        def read(path):
            if path==p.STORE/'candidate-source-registry.json': return [s]
            return {'sources':[c]}
        with patch.object(p,'read',side_effect=read),patch.object(b.ae,'read',return_value={'sources':[c]}):
            self.assertEqual(b.validate_sources(),1)
            c['year']=2021
            with self.assertRaises(ValueError): b.validate_sources()
            c['year']=2010
            c['doi']='10.1/new'
            with self.assertRaises(ValueError): b.validate_sources()

    def test_no_eligibility_or_rds_target(self):
        for bucket in p.ae.COLLECTIONS:
            for x in self.w['passB'][bucket]:
                self.assertEqual(x['governance']['activationStatus'],'NOT_ELIGIBLE')
                self.assertNotEqual(x['governance']['lifecycleStatus'],'GOVERNED')
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(p.ae.ValidationError): p.ae.validate_workspace(bad,b.context())

    def test_determinism(self):
        roots=[self.root,p.DOCS/'PSY-F12']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F12')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})


if __name__=='__main__':unittest.main()
