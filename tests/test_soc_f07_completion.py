"""Conditional approval is exact, additive and inactive; history is not rewritten."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import actions_events_v1 as ae
import audit_family as af
import relational_state_v1 as ns
import materialize_soc_f07_completion as c
import materialize_soc_f07_governance_001 as old


class CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=ae.read(old.AE_PATH)
        cls.derivations=ae.read(ns.CATALOG)
        cls.manifest=ae.read(c.MANIFEST)

    def test_exact_two_inactive_additions(self):
        self.assertEqual(self.manifest['newGoverned'],2)
        self.assertEqual(self.manifest['newInactive'],2)
        self.assertEqual(self.manifest['newActive'],0)
        self.assertEqual({r['id'] for r in self.manifest['records']},{'HT-V1-SOC-F07-008','DER-V1-SOC-F07-001'})
        records=[r for r in self.catalog['happeningTypes'] if 'SOC-F07' in r['id']]
        self.assertEqual({r['id'] for r in records},{f'HT-V1-SOC-F07-{n:03d}' for n in range(1,9)})
        for r in records+self.derivations['bindings']:
            self.assertEqual((r['governance']['lifecycleStatus'],r['governance']['activationStatus']),('GOVERNED','INACTIVE'))

    def test_exact_record_hashes_and_authority(self):
        ae.validate_catalog(self.catalog); ns.validate_repository()
        expected=[c.identity(),c.binding()]
        self.assertEqual(self.manifest['records'],[{'id':r['id'],'revision':1,'contentHash':ae.digest(r)} for r in expected])
        self.assertEqual(self.derivations['bindings'],[c.binding()])
        bad=copy.deepcopy(c.binding()); bad['scopeLimitations'].append('unapproved scope')
        with self.assertRaises((ValueError,ae.ValidationError)): ns.validate_binding(bad,self.derivations['authorizations'])

    def test_every_old_scientific_record_and_envelope_unchanged(self):
        for p in ('data/actions-events-v1/catalog.json','data/relationship-intervention-v1/source-register.json'):
            self.assertEqual(c.strip_additions(p,ae.read(c.ROOT/p)),c.frozen(p))
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',c.BASELINE,'--','data'],cwd=c.ROOT).decode().splitlines()
        mechanical={'data/candidates/actions-events-v1/SOC-F07/protected-science.json'}
        for p in paths:
            if p in mechanical or p in {'data/actions-events-v1/catalog.json','data/relationship-intervention-v1/source-register.json'}: continue
            original=subprocess.check_output(['git','show',c.BASELINE+':'+p],cwd=c.ROOT).replace(b'\r\n',b'\n')
            self.assertEqual((c.ROOT/p).read_bytes().replace(b'\r\n',b'\n'),original,p)

    def test_no_existing_bio_inf_scenario_or_definition_changes(self):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',c.BASELINE,'--','docs/governance/pilots/BIO-F01','docs/governance/pilots/INF-F03','scenario-service','_migration_handoff_v0.3'],cwd=c.ROOT).decode().splitlines()
        for p in paths:
            original=subprocess.check_output(['git','show',c.BASELINE+':'+p],cwd=c.ROOT).replace(b'\r\n',b'\n')
            self.assertEqual((c.ROOT/p).read_bytes().replace(b'\r\n',b'\n'),original,p)

    def test_schema_extension_not_target_expansion(self):
        p='schemas/relationship-intervention/v1/source-record-v1.schema.json'
        self.assertTrue(c.source_schema_extension_only(c.frozen(p),ae.read(c.ROOT/p)))
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',c.BASELINE,'--','schemas'],cwd=c.ROOT).decode().splitlines()
        for path in paths:
            if path==p: continue
            original=subprocess.check_output(['git','show',c.BASELINE+':'+path],cwd=c.ROOT).replace(b'\r\n',b'\n')
            self.assertEqual((c.ROOT/path).read_bytes().replace(b'\r\n',b'\n'),original,path)

    def test_truthful_only_one_canonical_source(self):
        before={r['id'] for r in c.frozen('data/relationship-intervention-v1/source-register.json')['sources']}
        current={r['id']:r for r in ae.read(old.SOURCE_PATH)['sources']}
        self.assertEqual(set(current)-before,{'SRC-559'})
        self.assertEqual(current['SRC-559'],c.source()); self.assertIsNone(current['SRC-559']['pmid'])
        self.assertEqual(c.identity()['identitySourceIds'],['SRC-559'])
        self.assertEqual(self.manifest['sourceMapping']['SRC-CAND-SOC-F07-010'],'SRC-559')

    def test_derivation_not_binary_or_causal(self):
        b=c.binding()
        self.assertFalse(b['causalRelationship'])
        self.assertEqual(b['inputContract']['collectionSubject'],'ALL_NODES_OF_BOUND_STATE_BOUNDARY')
        self.assertEqual(b['inputContract']['completenessRule'],'EXACT_SET_EQUALITY_NO_MISSING_NO_EXTRA')
        self.assertIn('MAXIMUM_BENCHMARK',b['inputContract']['requiredExternalInputs'])
        self.assertEqual(b['lineage']['candidateId'],'REL-CAND-SOC-F07-001')
        self.assertNotIn('sourceEntityId',b)
        self.assertEqual(b['evidenceBasis'],'DEFINITIONAL_CALCULATIONAL')
        self.assertEqual(self.manifest['separateEvidenceAssessmentCount'],0)
        self.assertEqual(self.manifest['sourceFindingCount'],1)
        self.assertFalse(b['sourceFindings'][0]['empiricalCausalEvidence'])

    def test_no_candidate_science_or_target_gaps_promoted(self):
        for p in ('workspace.json','hypotheses.json','ontology-target-gaps.json','revision-proposals.json','source-findings.json'):
            path='data/candidates/actions-events-v1/SOC-F07/'+p
            self.assertEqual(ae.read(c.ROOT/path),c.frozen(path))
        gaps=ae.read(old.STORE/'ontology-target-gaps.json')
        self.assertEqual(len(gaps),12)
        self.assertTrue(all(r['governance']['blockStatus']=='NEEDS_GOVERNANCE_INPUT' for r in gaps))
        self.assertFalse(any('SOC-F07' in r['id'] for r in self.catalog['effectAssertions']))

    def test_historical_decisions_and_source_overlap_preserved(self):
        for path in (old.MARKER,old.MANIFEST,old.AE_PATH.parent/'SOC-F07-materialization-manifest.json'):
            self.assertEqual(ae.read(path),c.frozen(path.relative_to(c.ROOT).as_posix()))
        self.assertIn('SRC-509',ae.read(old.MANIFEST)['preservedOverlap'])

    def test_identity_does_not_authorize_effect_or_practitioner(self):
        r=c.identity()
        for term in ('no efficacy','SOC-102 change','practitioner'):
            self.assertIn(term,r['description'])
        self.assertFalse(ae.state_active(r))
        self.assertFalse(any('SOC-F07' in r['id'] for r in self.catalog['occurrences']))

    def test_mechanical_counts(self):
        s=af.enriched_inventory()['summary']
        self.assertEqual([s[k] for k in ('drivers','rds','entities','combinedActiveRelationships','combinedActiveCausal')],[770,41,811,457,436])
        self.assertEqual(ns.validate_repository()['activeBindings'],0)

    def test_deterministic_materialization_does_not_rewrite(self):
        captured={}
        with patch.object(c,'write',side_effect=lambda path,value:captured.update({path:value})): c.materialize()
        self.assertEqual(set(captured),{old.AE_PATH,old.SOURCE_PATH,ns.CATALOG,c.MANIFEST})
        for path,value in captured.items(): self.assertEqual(ae.read(path),value,str(path))


if __name__=='__main__': unittest.main()
