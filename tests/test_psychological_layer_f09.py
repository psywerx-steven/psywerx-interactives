"""Planning, signed RDS, task-transfer and evidence-comparator safeguards."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class RegulationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=p.STORE/'PSY-F09'
        cls.r=p.read(cls.root/'research.json')
        cls.w=p.read(cls.root/'workspace.json')
        cls.d=p.read(cls.root/'rds-review.json')

    def test_exact_nine_entities_eight_driver_ledgers(self):
        self.assertEqual({e['id'] for e in self.r['entityReviews']},{f'PSY-{n:03d}' for n in range(75,84)})
        led=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(led['drivers']),len(led['relationships'])),(8,9))
        self.assertNotIn('PSY-078',{x['driverId'] for x in led['drivers']})
        for x in led['drivers']:
            self.assertEqual((len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties'])),(8,9,11))
            self.assertFalse(x['scientificUseEligibility'] or x['modelEligibility'] or x['practitionerActionEligibility'])

    def test_nine_existing_review_once_and_correct_ownership(self):
        reg=p.read(p.STORE/'relationship-review-registry.json')
        incident={x['id'] for x in reg.values() if 'PSY-F09' in x['psychologicalFamilyIds']}
        own={x['id'] for x in self.r['existingReviews']}
        reused=set(self.r['reusedExistingReviewIds'])
        self.assertEqual((len(own),len(reused)),(5,4))
        self.assertFalse(own & reused)
        self.assertEqual(own|reused,incident)
        self.assertEqual(reg['REL-PSY-044']['ownerFamilyId'],'PSY-F14')
        self.assertEqual(reg['REL-PSY-036']['processingFamilyId'],'PSY-F08')
        self.assertTrue(all(reg[x]['primaryDisposition'] for x in incident))
        self.assertTrue(all(not x['implementationAuthorized'] for x in p.read(self.root/'revision-proposals.json')))

    def test_rds_external_difference_not_invented_driver(self):
        d=self.d
        self.assertEqual(d['derivationType'],'DIFFERENCE')
        self.assertEqual({x['type'] for x in d['requiredInputs']},{'DESIRED_OR_REFERENCE_STATE','PERCEIVED_CURRENT_STATE'})
        self.assertTrue(all(x['required'] and x['entityId'] is None for x in d['requiredInputs']))
        self.assertFalse(d['canonicalDriverConstituents'])
        self.assertEqual(d['incomingCausalIds'],['REL-PSY-037'])
        self.assertFalse(d['outgoingCausalIds'] or d['causalSource'] or d['directEffectTargetPermitted'])
        self.assertFalse(d['formulaTreatedAsCausality'] or d['canonicalMetadataModified'])

    def test_toward_zero_not_universal_negative(self):
        rows=self.d['illustration']['cases']
        self.assertEqual(self.d['illustration']['recordClass'],'SYNTHETIC_NON_PRODUCTION')
        directions=[]
        for x in rows:
            self.assertEqual(x['reference']-x['currentBefore'],x['differenceBefore'])
            self.assertEqual(x['reference']-x['currentAfter'],x['differenceAfter'])
            self.assertLess(abs(x['differenceAfter']),abs(x['differenceBefore']))
            directions.append(x['differenceAfter']-x['differenceBefore'])
        self.assertLess(directions[0],0)
        self.assertGreater(directions[1],0)
        rev=next(x for x in self.r['existingReviews'] if x['id']=='REL-PSY-037')
        self.assertEqual((rev['causalGate'],rev['disposition']),('HEIGHTENED_CAUSAL','SPLIT_CANDIDATE'))

    def test_two_effects_not_forced_ready(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertEqual({x['targetId'] for x in self.w['passB']['effectAssertions']},{'PSY-077','PSY-081'})
        for x in self.w['passB']['effectAssertions']:
            self.assertEqual((x['change'],x['knowledgeStatus'],x['governance']['lifecycleStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE','RESEARCH_NEEDED'))
        self.assertTrue(all(x['synthesis']['disposition']=='INSUFFICIENT' for x in self.w['passB']['evidenceAssessments']))

    def test_monitoring_not_attainment_or_rds_effect(self):
        f=self.w['passB']['evidenceAssessments'][0]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['SUPPORTS','MIXED'])
        self.assertEqual(f[0]['datasetIds'],f[1]['datasetIds'])
        self.assertIn('OUTSIDE',f[1]['limitations'][0])
        self.assertIn('signed PSY-078',f[1]['limitations'][0])

    def test_active_comparator_null_and_review_not_replications(self):
        f=self.w['passB']['evidenceAssessments'][1]['sourceFindings']
        self.assertEqual([x['disposition'] for x in f],['MIXED','NULL_FINDING','NULL_FINDING','MIXED','MIXED'])
        self.assertIn('passive-control',f[0]['result'])
        self.assertIn('active control',f[2]['result'])
        self.assertIn('OUTSIDE',f[2]['limitations'][0])
        self.assertEqual(f[1]['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')
        self.assertEqual(f[0]['datasetIds'],f[1]['datasetIds'])
        self.assertIn('combined subgroup',f[1]['result'])

    def test_source_identity_and_hypothesis_status(self):
        x=next(x for x in self.r['canonicalSourceReviews'] if x['id']=='SRC157')
        self.assertEqual(x['status'],'STORED_PMID_MISMATCH')
        self.assertIn('21643479',x['finding'])
        self.assertIn('21662016',x['finding'])
        hs={h['id']:h for h in self.r['hypotheses']}
        for n in [2,6,9,11,13,15,16,18,20,23,28,29]:
            self.assertEqual(hs[f'H-PSY-F09-{n:02d}']['status'],'REJECTED_HYPOTHESIS')
        self.assertEqual(hs['H-PSY-F09-17']['status'],'RESEARCH_NEEDED')
        self.assertEqual(hs['H-PSY-F09-08']['source'],'PSY-004')

    def test_reuse_ifthen_identity_not_duplicate(self):
        a=p.read(self.root/'actions-events-search-ledger.json')['drivers']
        self.assertIn('HT-CAND-PSY-LAYER-0014',next(x for x in a if x['driverId']=='PSY-075')['candidateIdentityIds'])
        self.assertNotIn('HT-CAND-PSY-LAYER-0014',{h['id'] for h in self.w['passB']['happeningTypes']})
        reg=p.read(p.STORE/'actions-events-identity-registry.json')
        self.assertEqual(sum(h['id']=='HT-CAND-PSY-LAYER-0014' for h in reg),1)

    def test_references_and_candidate_isolation(self):
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

    def test_determinism_and_links(self):
        roots=[self.root,p.DOCS/'PSY-F09']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F09')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__':unittest.main()
