"""Epistemic appraisal, confidence/calibration and external omission RDS."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class EpistemicAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F13'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')

    def test_membership_and_search(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n}' for n in range(113,120)})
        led=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(led['drivers']),len(led['relationships'])),(7,18))
        for x in led['drivers']:
            self.assertEqual((len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties'])),(8,9,11))

    def test_unique_reviews_and_prior_pilot_retention(self):
        reg=p.read(p.STORE/'relationship-review-registry.json')
        incident={x['id'] for x in reg.values() if 'PSY-F13' in x['psychologicalFamilyIds']}
        own={x['id'] for x in self.r['existingReviews']}
        reused=set(self.r['reusedExistingReviewIds'])
        self.assertEqual((len(own),len(reused)),(10,8))
        self.assertEqual(own|reused,incident)
        self.assertFalse(own & reused)
        self.assertEqual(reg['REL-V1-INF-F03-001']['primaryDisposition'],'RETAIN_AS_IS')
        self.assertEqual(reg['REL-INF-045']['review']['causalGate'],'HEIGHTENED_CAUSAL')
        self.assertIn('denominator',reg['REL-INF-045']['review']['proposal'])
        self.assertTrue(all(not x['implementationAuthorized'] for x in p.read(self.root/'revision-proposals.json')))

    def test_three_unknown_effects(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertEqual({x['targetId'] for x in self.w['passB']['effectAssertions']},{'PSY-116','PSY-117','PSY-119'})
        for x in self.w['passB']['effectAssertions']:
            self.assertEqual((x['change'],x['knowledgeStatus'],x['governance']['lifecycleStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE','RESEARCH_NEEDED'))

    def test_nulls_are_not_automatic_zero_or_cross_operation_evidence(self):
        ev=self.w['passB']['evidenceAssessments']
        self.assertIn('OUTSIDE',ev[0]['sourceFindings'][2]['limitations'][0])
        self.assertEqual(ev[0]['sourceFindings'][2]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')
        self.assertIn('OUTSIDE',ev[1]['sourceFindings'][1]['limitations'][0])
        self.assertIn('equivalence',ev[2]['sourceFindings'][0]['result'])
        self.assertIn('not pure',ev[2]['sourceFindings'][0]['limitations'][0])
        self.assertEqual(ev[2]['sourceFindings'][2]['supportedSemantics'],['ASSOCIATION'])

    def test_source_mismatches_and_existing_duplicate_reuse(self):
        sr={x['id']:x for x in self.r['canonicalSourceReviews']}
        self.assertIn('Digestion',sr['SRC166']['finding'])
        self.assertIn('Elite Cues',sr['SRC167']['finding'])
        self.assertIn('SRC-412',sr['SRC201']['finding'])
        self.assertGreaterEqual(b.validate_sources(),176)

    def test_canonical_index_can_reuse_one_historical_duplicate(self):
        source={'id':'SRC-ONE','doi':'10.1234/example','title':'Work','year':2004,'pmid':None}
        canonical=[{'id':'SRC-ONE','doi':'10.1234/example'},{'id':'SRC-TWO','doi':'10.1234/example'}]
        with patch.object(p,'read',return_value=[source]),patch.object(b.ae,'read',return_value={'sources':canonical}):
            self.assertEqual(b.validate_sources(),1)
            source['doi']='10.1234/incorrect'
            with self.assertRaises(ValueError): b.validate_sources()

    def test_candidate_isolation_rds_and_protection(self):
        self.assertFalse(p.ae.validate_workspace(self.w,b.context())['productionEligible'])
        for bucket in p.ae.COLLECTIONS:
            for x in self.w['passB'][bucket]:
                self.assertEqual(x['governance']['activationStatus'],'NOT_ELIGIBLE')
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='INF-068'
        with self.assertRaises(p.ae.ValidationError):p.ae.validate_workspace(bad,b.context())
        self.assertTrue(p.check_protected()['passed'])

    def test_determinism(self):
        roots=[self.root,p.DOCS/'PSY-F13']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F13')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})


if __name__=='__main__':unittest.main()
