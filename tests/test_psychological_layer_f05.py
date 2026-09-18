"""PSY-F05: discrete emotion, comparator, source identity and proxy safeguards."""
import copy
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class AffectEmotionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = p.STORE / 'PSY-F05'
        cls.r = p.read(cls.root / 'research.json')
        cls.w = p.read(cls.root / 'workspace.json')
        cls.registry = p.read(p.STORE / 'relationship-review-registry.json')

    def test_all_fourteen_actual_drivers(self):
        expected = {f'PSY-{i:03d}' for i in range(41, 55)}
        self.assertEqual({e['id'] for e in self.r['entityReviews']}, expected)
        frozen = p.read(self.root / 'BASELINE.json')['entities']
        self.assertEqual({e['id'] for e in frozen}, expected)
        self.assertEqual({e['entityType'] for e in frozen}, {'DRIVER'})

    def test_exact_existing_coverage_reuse(self):
        own = {r['id'] for r in self.r['existingReviews']}
        reused = set(self.r['reusedExistingReviewIds'])
        incident = {r['id'] for r in self.registry.values() if 'PSY-F05' in r['psychologicalFamilyIds']}
        self.assertEqual((len(own),len(reused),len(incident)), (14,3,17))
        self.assertFalse(own & reused)
        self.assertEqual(own | reused, incident)
        for rid in own:
            self.assertEqual(self.registry[rid]['processingFamilyId'], 'PSY-F05')
        self.assertEqual(reused, {'REL-PSY-008','REL-PSY-009','REL-PSY-017'})

    def test_external_ownership_not_reassigned(self):
        for rid,fam in [('REL-CUL-047','CUL-F10'),('REL-SOC-063','SOC-F04'),('REL-SOC-068','SOC-F11'),('REL-PSY-038','PSY-F09')]:
            self.assertEqual(self.registry[rid]['ownerFamilyId'],fam)
        self.assertEqual(self.registry['REL-PSY-026']['review']['disposition'],'RETAIN_V1_INCOMPLETE')
        self.assertEqual(self.registry['REL-PSY-027']['review']['disposition'],'RETAIN_V1_INCOMPLETE')

    def test_scientific_yield_not_forced(self):
        self.assertFalse(self.w['passA']['relationshipCandidates'])
        self.assertEqual(len(self.w['passB']['happeningTypes']),2)
        self.assertEqual(len(self.w['passB']['effectAssertions']),2)
        for ea in self.w['passB']['effectAssertions']:
            self.assertEqual(ea['governance']['lifecycleStatus'],'RESEARCH_NEEDED')
            self.assertEqual((ea['change'],ea['knowledgeStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE'))
        for ev in self.w['passB']['evidenceAssessments']:
            self.assertEqual((ev['synthesis']['disposition'],ev['synthesis']['evidenceStrength'],ev['synthesis']['confidence']),('INSUFFICIENT','LIMITED','LOW'))

    def test_within_group_improvement_not_causal_contrast(self):
        ev=self.w['passB']['evidenceAssessments'][0]
        self.assertEqual([f['disposition'] for f in ev['sourceFindings']],['MIXED','NULL_FINDING','NULL_FINDING'])
        self.assertEqual(ev['sourceFindings'][0]['supportedSemantics'],['ASSOCIATION'])
        self.assertIn('WITHIN-ARM',ev['sourceFindings'][0]['design'])
        bad=copy.deepcopy(self.w)
        ea=bad['passB']['effectAssertions'][0]
        ea.update(change='DECREASE',observedChange='DECREASE',knowledgeStatus='SUPPORTED_EFFECT')
        with self.assertRaises(p.ae.ValidationError):
            p.ae.validate_workspace(bad,b.context())

    def test_state_trait_and_null_preserved(self):
        fs=self.w['passB']['evidenceAssessments'][0]['sourceFindings']
        self.assertEqual(len({tuple(f['datasetIds']) for f in fs}),1)
        self.assertIn('OUTSIDE',fs[2]['limitations'][0])
        self.assertIn('STAI-trait',fs[2]['measurement'])
        for f in fs[1:]:
            self.assertEqual(f['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')

    def test_film_same_item_contrast_not_profile_difference(self):
        ea=self.w['passB']['effectAssertions'][1]
        self.assertEqual(ea['targetId'],'PSY-047')
        self.assertIn('same-item',ea['scope']['boundaryConditions'])
        f=self.w['passB']['evidenceAssessments'][1]['sourceFindings'][0]
        self.assertIn('Pseudo-random',f['design'])
        self.assertIn('NOT the same-item',f['result'])
        self.assertIn('DURING',ea['scope']['timing'])

    def test_arousal_valence_composite_distinctions(self):
        entities={e['id']:e for e in self.r['entityReviews']}
        self.assertIn('not automatically',entities['PSY-050']['measurementReview'])
        self.assertIn('not equivalent',entities['PSY-051']['measurementReview'])
        self.assertIn('DASS',entities['PSY-054']['measurementReview'])
        hypotheses={h['id']:h for h in self.r['hypotheses']}
        for n in (3,4,6,11,17,19,22,25,28):
            self.assertEqual(hypotheses[f'H-PSY-F05-{n:02d}']['status'],'REJECTED_HYPOTHESIS')

    def test_source_identity_mismatches_are_not_silent_repairs(self):
        sources={s['id']:s for s in self.r['canonicalSourceReviews']}
        for sid,pmid in [('SRC145','15537986'),('SRC177','23458435'),('SRC178','16953797'),('SRC180','17352606')]:
            self.assertEqual(sources[sid]['status'],'STORED_PMID_MISMATCH')
            self.assertIn(pmid,sources[sid]['url'])
        self.assertEqual(sources['SRC207']['status'],'STORED_DOI_UNRESOLVED')
        self.assertIn('NIMH RDoC',sources['SRC-494']['finding'])
        self.assertIn('rdoc/definitions-',sources['SRC-494']['url'])
        self.assertIn('40323862',sources['SRC-506']['url'])
        self.assertTrue(p.check_protected()['passed'])

    def test_shared_sources_resolve_and_deduplicate(self):
        b.validate_sources()
        for row in self.r['entityReviews']+self.r['existingReviews']+self.r['hypotheses']:
            self.assertTrue(set(row['sources']) <= b.context().source_ids,row['id'])
        sources=p.read(p.STORE/'candidate-source-registry.json')
        local=[s for s in sources if 'PSY-F05' in s['families']]
        self.assertEqual(len(local),17)
        self.assertFalse(any(s['registrationAuthorized'] for s in local))
        version=next(s for s in local if s['id'].endswith('0057'))
        self.assertIn('17749.2',version['doi'])
        self.assertIn('2024',version['limitations'])

    def test_all_domains_origins_properties_honest(self):
        ledgers=p.read(self.root/'actions-events-search-ledger.json')
        self.assertEqual((len(ledgers['drivers']),len(ledgers['relationships'])),(14,17))
        queries={q['id'] for q in self.r['searchLog']}
        for d in ledgers['drivers']:
            self.assertEqual((len(d['originLayerSearch']),len(d['domainSearch']),len(d['effectProperties'])),(8,9,11))
            self.assertTrue(set(d['queries']) <= queries)
            self.assertEqual(d['effectProperties']['LEVEL'],'INSUFFICIENT_EVIDENCE')
            for field in ['scientificUseEligibility','modelEligibility','practitionerActionEligibility']:
                self.assertFalse(d[field])

    def test_no_causal_pathway_moderation_or_occurrence_inferred(self):
        self.assertFalse(self.w['passB']['occurrences'])
        for ea in self.w['passB']['effectAssertions']:
            self.assertFalse(ea['moderatorLinks'])
            self.assertFalse(ea['mechanisticDriverIds'])
            self.assertEqual(ea['interaction']['mode'],'NONE')
        for rid in ['REL-PSY-058','REL-PSY-059','REL-SOC-063']:
            self.assertEqual(self.registry[rid]['review']['disposition'],'RESEARCH_NEEDED')

    def test_identity_not_eligibility_or_duplicate_sleep(self):
        for ht in self.w['passB']['happeningTypes']:
            self.assertEqual(ht['controlProfiles'][0]['extent'],'UNKNOWN')
            self.assertIn('permission',ht['description'])
        self.assertNotIn('sleep',p.encode(self.w['passB']['happeningTypes']).lower())
        for bucket in p.ae.COLLECTIONS:
            for row in self.w['passB'][bucket]:
                self.assertEqual(row['governance']['activationStatus'],'NOT_ELIGIBLE')
                self.assertNotEqual(row['governance']['lifecycleStatus'],'GOVERNED')

    def test_direct_rds_target_rejected(self):
        bad=copy.deepcopy(self.w)
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(p.ae.ValidationError):
            p.ae.validate_workspace(bad,b.context())

    def test_deterministic_and_local_links(self):
        roots=[self.root,p.DOCS/'PSY-F05']
        before={f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()}
        b.render('PSY-F05')
        self.assertEqual(before,{f:p.digest(f) for root in roots for f in root.rglob('*') if f.is_file()})
        for path in roots[1].glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/unquote(target.split('#')[0])).exists())


if __name__=='__main__':
    unittest.main()
