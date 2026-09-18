"""Enduring traits, facet invariance, package boundaries and final Family consultation."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class DispositionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = p.STORE / 'PSY-F14'
        cls.r = p.read(cls.root / 'research.json')
        cls.w = p.read(cls.root / 'workspace.json')

    def test_exact_membership_and_all_dimensions(self):
        self.assertEqual({x['id'] for x in self.r['entityReviews']}, {f'PSY-{n}' for n in range(120,132)})
        led = p.read(self.root / 'actions-events-search-ledger.json')
        self.assertEqual((len(led['drivers']),len(led['relationships'])),(12,8))
        for x in led['drivers']:
            self.assertEqual((len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties'])),(8,9,11))

    def test_owner_consultation_reuses_eight_primary_reviews(self):
        reg = p.read(p.STORE / 'relationship-review-registry.json')
        ids = {k for k,v in reg.items() if 'PSY-F14' in v['psychologicalFamilyIds']}
        self.assertEqual(ids, set(self.r['reusedExistingReviewIds']))
        self.assertFalse(self.r['existingReviews'])
        self.assertEqual(sum(reg[k]['primaryDisposition']=='RESEARCH_NEEDED' for k in ids),6)
        self.assertEqual(sum(reg[k]['primaryDisposition']=='REVISION_CANDIDATE' for k in ids),2)
        self.assertTrue(all(reg[k]['ownerFamilyId']=='PSY-F14' for k in ids))

    def test_no_trait_effect_from_state_or_component(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        for x in self.w['passB']['effectAssertions']:
            self.assertEqual((x['change'],x['knowledgeStatus'],x['governance']['lifecycleStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE','RESEARCH_NEEDED'))
        inp=p.read(self.root/'evidence-inputs.json')
        self.assertIn('not the entire twelve-session',inp['happeningTypes'][0]['description'])
        self.assertIn('One-week',inp['assertions'][1]['timing'])

    def test_source_findings_do_not_promote_followup_or_completion(self):
        inp=p.read(self.root/'evidence-inputs.json')
        f={x['key']:x for x in inp['findings']}
        self.assertEqual(f['IU_FOLLOWUP']['supportedSemantics'],['ASSOCIATION'])
        self.assertEqual(f['CHALLENGE_SELECTION']['supportedSemantics'],['ASSOCIATION'])
        self.assertEqual(f['PEACH_TRIAL']['dataset'],f['FACET_HETEROGENEITY']['dataset'])
        self.assertEqual(f['OBSERVER_NULL']['disposition'],'NULL_FINDING')
        ev=self.w['passB']['evidenceAssessments'][1]
        null=next(x for x in ev['sourceFindings'] if x['disposition']=='NULL_FINDING')
        self.assertEqual(null['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')

    def test_not_immutable_not_uniform_and_closure_stays_blocked(self):
        hs={x['id']:x for x in self.r['hypotheses']}
        for n in (1,3,4,7,8,10,12,14,16,18,19,20,23,26,28,29):
            self.assertEqual(hs[f'H-PSY-F14-{n:02}']['status'],'REJECTED_HYPOTHESIS')
        self.assertEqual(hs['H-PSY-F14-22']['status'],'BLOCKED_NEEDS_GOVERNANCE_INPUT')
        self.assertTrue(all(not x['productionChangeAuthorized'] for x in p.read(p.STORE/'architecture-escalations.json')))

    def test_supplemental_source_dedup_and_eligibility(self):
        self.assertGreaterEqual(b.validate_sources(),193)
        for collection in p.ae.COLLECTIONS:
            for x in self.w['passB'][collection]:
                self.assertEqual(x['governance']['activationStatus'],'NOT_ELIGIBLE')
        self.assertFalse(p.ae.validate_workspace(self.w,b.context())['productionEligible'])
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(p.ae.ValidationError): p.ae.validate_workspace(bad,b.context())

    def test_protected_science(self):
        self.assertTrue(p.check_protected()['passed'])

    def test_deterministic(self):
        roots=[self.root,p.DOCS/'PSY-F14']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F14')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})


if __name__=='__main__': unittest.main()
