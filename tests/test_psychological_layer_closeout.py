"""Layer-wide conservation, coverage, deduplication and skeptical-closeout gates."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import closeout_psychological_layer_v1 as c


class LayerCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=c.load()
        cls.summary=c.collect()

    def test_full_layer_gate(self):
        s=c.validate()
        self.assertEqual((s['familiesCompleted'],s['driversReviewed'],s['rdsReviewed'],s['entitiesReviewed']),(14,134,1,135))

    def test_exact_entity_union(self):
        ids=[x['id'] for d in self.data.values() for x in d['research']['entityReviews']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(set(ids),set(c.p.read(c.p.STORE/'baseline.json')['entityIds']))

    def test_every_driver_has_one_complete_recall_ledger(self):
        rows=[r for d in self.data.values() for r in d['ledger']['drivers']]
        self.assertEqual(len(rows),134)
        self.assertEqual(len({r['driverId'] for r in rows}),134)
        self.assertNotIn('PSY-078',{r['driverId'] for r in rows})
        for r in rows:
            self.assertEqual((len(r['originLayerSearch']),len(r['domainSearch']),len(r['effectProperties'])),(8,9,11))
            self.assertFalse(any(r[k] for k in ('modelEligibility','practitionerActionEligibility','scientificUseEligibility')))

    def test_shared_existing_propositions_not_incident_sum(self):
        reg=c.p.read(c.p.STORE/'relationship-review-registry.json')
        ids=[r['id'] for d in self.data.values() for r in d['research']['existingReviews']]
        self.assertEqual(len(ids),111)
        self.assertEqual(set(ids),set(reg))
        self.assertGreater(sum(d['manifest']['existingIncidentReviewed'] for d in self.data.values()),111)
        self.assertEqual(self.summary['baseline']['projectionAdditionalPropositions'],0)

    def test_exact_disposition_counts(self):
        self.assertEqual(self.summary['existingDispositions'],dict(zip(c.DISPOSITIONS,[1,10,57,5,2,0,0,36,0])))

    def test_no_candidate_proposition_duplicates(self):
        records=c.p.read(c.p.STORE/'candidate-proposition-registry.json')
        self.assertEqual(len(records),31)
        self.assertEqual(len({tuple(x['semanticKey']) for x in records}),31)
        self.assertTrue(all(x['activationStatus']=='NOT_ELIGIBLE' for x in records))

    def test_identity_and_effect_are_not_synonyms(self):
        records=c.p.read(c.p.STORE/'actions-events-identity-registry.json')
        self.assertEqual(len(records),29)
        self.assertEqual(len({x['identityKey'] for x in records}),29)
        self.assertTrue(all(x['comparedProductionIdentityIds'] for x in records))
        self.assertEqual(self.summary['effectAssertions'],30)

    def test_source_registration_unauthorized_and_exact_ids_dedup(self):
        sources=c.p.read(c.p.STORE/'candidate-source-registry.json')
        self.assertEqual(c.b.validate_sources(),194)
        self.assertEqual(sum(x['id'].startswith('SRC-CAND-') for x in sources),184)
        self.assertTrue(all(not x.get('registrationAuthorized',False) for x in sources))
        self.assertEqual(len({x['id'] for x in sources}),len(sources))

    def test_null_counterexample_preserved_not_universal_boundary(self):
        inp=self.data['PSY-F01']['inputs']
        fs={x['key']:x for x in inp['findings']}
        self.assertEqual(fs['IMPLAUSIBILITY_NULL']['disposition'],'NULL_FINDING')
        self.assertEqual(fs['IMPLAUSIBILITY_COUNTEREXAMPLE']['disposition'],'MIXED')
        for a in inp['assertions'][:2]:
            self.assertIn('IMPLAUSIBILITY_COUNTEREXAMPLE',a['findingKeys'])
            self.assertIn('not a universal exclusion',a['scope'])
            self.assertEqual(a['disposition'],'MIXED')

    def test_metadata_only_access_not_fulltext(self):
        src={s['id']:s for s in c.p.read(c.p.STORE/'candidate-source-registry.json')}
        self.assertEqual(src['SRC-CAND-PSY-LAYER-0150']['accessDepth'],'METADATA')
        self.assertFalse(any(f['sourceId']=='SRC-CAND-PSY-LAYER-0150' for d in self.data.values() for f in d['inputs']['findings']))

    def test_source_results_not_replication_counts(self):
        self.assertEqual((self.summary['sourceFindingsAttached'],self.summary['uniqueSourceResultExtractions']),(105,100))
        self.assertEqual(self.summary['sourceOverlapIssues'],64)
        self.assertEqual(sum(self.summary['sourceFindingDispositionAttached'].values()),105)
        self.assertEqual(self.summary['assessmentDispositions'],{'INSUFFICIENT':23,'MIXED':7,'SUPPORTS':1})

    def test_direct_rds_effect_rejected(self):
        bad=copy.deepcopy(self.data['PSY-F14']['workspace'])
        bad['passB']['effectAssertions'][0]['targetId']='PSY-078'
        with self.assertRaises(c.p.ae.ValidationError):c.p.ae.validate_workspace(bad,c.b.context())

    def test_no_formal_moderation_or_pathway_from_reachability(self):
        self.assertEqual(self.summary['newRelationshipSemantics'],{'CAUSAL':1,'ASSOCIATION':0,'DERIVATIONAL':0,'SEMANTIC':0,'TEMPORAL':0,'MODERATION':0,'CAUSAL_PATHWAY':0})
        self.assertIn('not mediation',c.graph_flags()['interpretation'])

    def test_human_index_does_not_double_vote_discovery(self):
        rr=c.rows()
        self.assertEqual(len(rr),595)
        self.assertEqual(len({r['id'] for r in rr}),595)
        self.assertNotIn('H-PSY-F01-01',{r['id'] for r in rr})
        self.assertTrue(all(r['humanDecision']==c.DECISION for r in rr))

    def test_samples_frozen_before_correction(self):
        samples=c.sample_records()
        self.assertEqual(len(samples),14)
        self.assertEqual(samples[0]['finding']['key'],'IMPLAUSIBILITY_NULL')
        self.assertNotIn('IMPLAUSIBILITY_COUNTEREXAMPLE',samples[0]['assertion']['findingKeys'])
        review=c.p.read(c.p.STORE/'layer-reconciliation.json')
        self.assertEqual(review['sampleSelectionCommit'],c.SAMPLE_COMMIT)
        self.assertEqual(review['randomSampleReviews'][0]['outcome'],'SCOPED_EVIDENCE_CORRECTION')

    def test_duplicate_family_sample_rejected(self):
        original=c.p.read
        review=copy.deepcopy(original(c.p.STORE/'layer-reconciliation.json'))
        review['randomSampleReviews'][-1]=review['randomSampleReviews'][0]
        def reader(path):
            return review if Path(path).name=='layer-reconciliation.json' else original(path)
        with patch.object(c.p,'read',side_effect=reader), self.assertRaises(AssertionError):c.validate()

    def test_new_science_lifecycle_and_prior_protection(self):
        self.assertEqual(self.summary['formalScientificLifecycle'],{'RESEARCH_NEEDED':46,'REVIEW_READY':45})
        self.assertEqual((self.summary['newGoverned'],self.summary['newActive']),(0,0))
        self.assertEqual(self.summary['productionCounts'],{'drivers':770,'rds':41,'entities':811,'combinedActiveRelationships':457,'combinedActiveCausal':436})
        self.assertEqual(c.p.check_protected(),{'filesCompared':191,'changed':[],'passed':True})

    def test_escalations_remain_unimplemented(self):
        records=c.p.read(c.p.STORE/'architecture-escalations.json')
        self.assertEqual(len(records),2)
        self.assertTrue(all(r['status']=='BLOCKED_NEEDS_GOVERNANCE_INPUT' and not r['productionChangeAuthorized'] for r in records))

    def test_deterministic_layer_reports_and_links(self):
        paths=[c.p.STORE/'layer-summary.json',c.p.STORE/'governance-index.json',*c.p.DOCS.glob('PSYCHOLOGICAL_LAYER_*.md'),c.p.DOCS/'PSYCHOLOGICAL_LAYER_AUDIT_MANIFEST.json',c.p.DOCS/'README.md']
        before={f:c.p.digest(f) for f in paths}
        c.render()
        self.assertEqual(before,{f:c.p.digest(f) for f in paths})
        self.assertFalse(c.link_check()['errors'])


if __name__=='__main__':unittest.main()
