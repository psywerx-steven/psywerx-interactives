"""Isolated synthetic-only representation tests, NOT network-science experiments."""
import copy
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('network_state_prototype',ROOT/'experiments/network-state-vnext/prototype.py')
ns=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(ns)
sys.path.insert(0,str(ROOT/'scripts'))
import actions_events_v1 as ae


class NetworkStateTests(unittest.TestCase):
    def setUp(self): self.s=ns.fixture()
    def apply(self, ops): return ns.apply_delta(self.s,ns.delta(self.s,'SYN-DELTA-TEST',ops))

    def test_fixture_schema(self):
        self.assertTrue(ns.validate_state(self.s))
        for schema in (ns.STATE_SCHEMA,ns.DELTA_SCHEMA): ns.Draft202012Validator.check_schema(schema)

    def test_all_nine_demonstrations(self):
        examples=ns.demonstration()['examples']
        self.assertEqual(len(examples),9)
        self.assertEqual({e['delta']['operations'][0]['operation'] for e in examples},
            {'ADD_TIE','REMOVE_TIE','ADD_NODE','REMOVE_NODE','ASSIGN_MEMBERSHIP','SET_BOUNDARY','SET_WEIGHT','SET_ACCESS','ASSIGN_SEATING'})
        for e in examples:
            ns.validate_state(e['afterState'])
            self.assertFalse(e['receipt']['empiricalEvidenceProduced'])
            self.assertEqual(e['receipt']['ontologyRelationshipsEdited'],0)

    def test_deterministic_recomputation_and_version(self):
        a=ns.demonstration(); b=ns.demonstration(); self.assertEqual(a,b)
        for row in a['examples']:
            self.assertEqual(row['afterState']['version'],2)
            self.assertEqual(row['afterState']['parentHash'],self.s['contentHash'])

    def test_json_order_independence(self):
        s=copy.deepcopy(self.s); s['nodeCatalog'].reverse(); s['ties'].reverse(); s['boundary']['includedNodeIds'].reverse()
        self.assertEqual(ns.content_hash(s),self.s['contentHash'])

    def test_tampered_version_or_content_rejected(self):
        for field in ('version','contentHash'):
            bad=copy.deepcopy(self.s); bad[field]=5 if field=='version' else 'a'*64
            with self.assertRaises(ns.Rejected): ns.validate_state(bad)

    def test_stale_precondition(self):
        d=ns.delta(self.s,'SYN-DELTA-STALE',[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]); d['expectedVersion']=2
        with self.assertRaises(ns.Rejected): ns.apply_delta(self.s,d)

    def test_atomic_rollback_no_input_mutation(self):
        before=copy.deepcopy(self.s)
        with self.assertRaises(ns.Rejected): self.apply([{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'},{'operation':'REMOVE_TIE','tieId':'SYN-TIE-MISSING'}])
        self.assertEqual(self.s,before)

    def test_duplicate_tie_id_and_dyad(self):
        for identifier in ('SYN-TIE-AB','SYN-TIE-DUP'):
            with self.assertRaises(ns.Rejected): self.apply([{'operation':'ADD_TIE','tie':ns.tie(identifier,'SYN-NODE-B','SYN-NODE-A')}])

    def test_immutable_node_identity_and_no_recycling(self):
        with self.assertRaises(ns.Rejected): self.apply([{'operation':'ADD_NODE','node':{'id':'SYN-NODE-A','active':True,'memberships':[]},'includeInBoundary':True}])
        after,_=self.apply([{'operation':'REMOVE_NODE','nodeId':'SYN-NODE-A','incidentTiePolicy':'REMOVE_AND_RECORD'}])
        self.assertFalse(next(n for n in after['nodeCatalog'] if n['id']=='SYN-NODE-A')['active'])
        d=ns.delta(after,'SYN-DELTA-RECYCLE',[{'operation':'ADD_NODE','node':{'id':'SYN-NODE-A','active':True,'memberships':[]},'includeInBoundary':True}])
        with self.assertRaises(ns.Rejected): ns.apply_delta(after,d)

    def test_node_exit_removes_incident_ties_with_receipt(self):
        after,receipt=self.apply([{'operation':'REMOVE_NODE','nodeId':'SYN-NODE-C','incidentTiePolicy':'REMOVE_AND_RECORD'}])
        self.assertEqual(receipt['removedTieIds'],['SYN-TIE-AC','SYN-TIE-BC','SYN-TIE-CD'])
        self.assertNotIn('SYN-NODE-C',after['boundary']['includedNodeIds'])

    def test_add_node_does_not_create_ties(self):
        after,_=self.apply([{'operation':'ADD_NODE','node':{'id':'SYN-NODE-F','active':True,'memberships':[]},'includeInBoundary':True}])
        self.assertEqual(after['ties'],self.s['ties']); self.assertEqual(ns.metrics(after)['degree']['SYN-NODE-F'],0)

    def test_rewire_atomic_explicit_old_new_tie(self):
        after,receipt=self.apply([{'operation':'REWIRE_TIE','removedTieId':'SYN-TIE-AB','addedTie':ns.tie('SYN-TIE-AD','SYN-NODE-A','SYN-NODE-D')}])
        self.assertEqual(receipt['removedTieIds'],['SYN-TIE-AB']); self.assertEqual(len(after['ties']),len(self.s['ties']))

    def test_membership_not_friendship(self):
        after,_=self.apply([{'operation':'ASSIGN_MEMBERSHIP','nodeId':'SYN-NODE-A','groupIds':['SYN-GROUP-2']}])
        self.assertEqual(after['ties'],self.s['ties'])
        self.assertEqual(ns.metrics(after)['degree'],ns.metrics(self.s)['degree'])

    def test_boundary_changes_metrics_not_actual_ties(self):
        after,receipt=self.apply([{'operation':'SET_BOUNDARY','includedNodeIds':['SYN-NODE-'+c for c in 'ABCDE'],'selectionReason':'Expand analytic scope only'}])
        self.assertEqual(after['ties'],self.s['ties']); self.assertEqual(receipt['changeClass'],'ANALYTIC_BOUNDARY_ONLY')
        self.assertNotEqual(ns.metrics(after)['density'],ns.metrics(self.s)['density'])

    def test_boundary_missing_node_rejected(self):
        with self.assertRaises(ns.Rejected): self.apply([{'operation':'SET_BOUNDARY','includedNodeIds':['SYN-NODE-ABSENT'],'selectionReason':'Not observed'}])

    def test_boundary_cannot_claim_structural_mutation(self):
        d=ns.delta(self.s,'SYN-DELTA-BAD',[{'operation':'SET_BOUNDARY','includedNodeIds':[],'selectionReason':'Scope'}]); d['basis']='SYNTHETIC_SCENARIO_OPERATION'
        with self.assertRaises(ns.Rejected): ns.apply_delta(self.s,d)

    def test_no_boundary_tie_mutation_bundle(self):
        with self.assertRaises(ns.Rejected): self.apply([{'operation':'SET_BOUNDARY','includedNodeIds':[],'selectionReason':'Scope'}, {'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}])

    def test_weight_storage_not_numeric_causal_weight(self):
        after,_=self.apply([{'operation':'SET_WEIGHT','tieId':'SYN-TIE-AB','weight':5}])
        self.assertEqual(ns.metrics(after)['degree'],ns.metrics(self.s)['degree'])
        self.assertIn('BINARY_POSITIVE_WEIGHT',ns.metrics(after)['scope']['projection'])
        self.assertFalse(after['executionEligibility'])

    def test_access_disable_not_friendship_deletion(self):
        after,_=self.apply([{'operation':'SET_ACCESS','opportunityId':'SYN-OPPORTUNITY-AD','enabled':False}])
        self.assertFalse(after['opportunities'][0]['enabled']); self.assertEqual(after['ties'],self.s['ties'])

    def test_seating_not_automatic_friendship(self):
        after,_=self.apply([{'operation':'ASSIGN_SEATING','opportunity':ns.opportunity('SYN-OPPORTUNITY-SEAT','SYN-NODE-A','SYN-NODE-D','ASSIGNED_SEATING')}])
        self.assertEqual(after['ties'],self.s['ties']); self.assertEqual(len(after['opportunities']),2)

    def test_directed_storage_but_no_silent_undirected_metrics(self):
        s=copy.deepcopy(self.s); s['ties'][0]['directed']=True; s=ns.sealed(s)
        ns.validate_state(s)
        with self.assertRaises(ns.Rejected): ns.metrics(s)

    def test_multiplex_preserved_no_silent_collapse(self):
        s=copy.deepcopy(self.s); s['networkSpecification']['layerIds'].append('SYN-LAYER-OTHER')
        extra=ns.tie('SYN-TIE-OTHER','SYN-NODE-A','SYN-NODE-B'); extra['layerId']='SYN-LAYER-OTHER'; s['ties'].append(extra)
        s=ns.sealed(s); ns.validate_state(s)
        self.assertEqual(ns.metrics(s)['degree'],ns.metrics(self.s)['degree'])

    def test_observation_not_truth(self):
        s=copy.deepcopy(self.s); s['stateNature']='SYNTHETIC_OBSERVATION'; s['observation']['isGroundTruth']=True; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)

    def test_missingness_requires_provenance(self):
        s=copy.deepcopy(self.s); s['observation']['missingNodes']=''; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)
        s=copy.deepcopy(self.s); s['observation']['coverage']='INCOMPLETE'; s['observation']['missingNodes']='Unknown number outside sampling frame'; s=ns.sealed(s)
        self.assertFalse(ns.metrics(s)['realWorldMetricKnown'])

    def test_static_not_dynamic(self):
        s=copy.deepcopy(self.s); s['window']['end']='2026-02-01T00:00:00Z'; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)

    def test_interval_requires_persistence_aggregation(self):
        s=copy.deepcopy(self.s); s['window'].update(mode='INTERVAL',end='2026-02-01T00:00:00Z',aggregation='PERSISTENT_THROUGH_WINDOW'); s=ns.sealed(s)
        ns.validate_state(s); self.assertEqual(ns.metrics(s)['edgeCount'],4)

    def test_temporal_expired_tie_not_carried_forward(self):
        s=copy.deepcopy(self.s); s['ties'][0]['validUntil']='2026-01-01T00:00:00Z'; s=ns.sealed(s)
        self.assertEqual(ns.metrics(s)['edgeCount'],3)

    def test_interval_end_is_exclusive_and_utc_normalized(self):
        s=copy.deepcopy(self.s); s['window'].update(mode='INTERVAL',end='2026-02-01T00:00:00Z',aggregation='PERSISTENT_THROUGH_WINDOW')
        s['ties'][0]['validUntil']=s['window']['end']; s=ns.sealed(s)
        self.assertEqual(ns.metrics(s)['edgeCount'],4)
        s['window']['start']='2026-01-01T01:00:00+01:00'; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)

    def test_known_metrics_by_hand(self):
        m=ns.metrics(self.s)
        self.assertEqual(m['degree'],{'SYN-NODE-A':2,'SYN-NODE-B':2,'SYN-NODE-C':3,'SYN-NODE-D':1})
        self.assertAlmostEqual(m['density'],2/3)
        self.assertAlmostEqual(m['localClustering']['SYN-NODE-C'],1/3)
        self.assertEqual(m['componentFragmentation']['value'],0)
        self.assertAlmostEqual(m['degreeCentralization']['value'],2/3)

    def test_fragmentation_not_generic_cohesion(self):
        after,_=self.apply([{'operation':'REMOVE_NODE','nodeId':'SYN-NODE-C','incidentTiePolicy':'REMOVE_AND_RECORD'}])
        self.assertAlmostEqual(ns.metrics(after)['componentFragmentation']['value'],2/3)
        self.assertEqual(ns.metrics(after)['componentFragmentation']['variant'],'UNREACHABLE_UNORDERED_PAIR_FRACTION')

    def test_centralization_one_actor_rejected(self):
        m=ns.metrics(self.s)
        with self.assertRaises(ns.Rejected): ns.centralization({'SYN-NODE-A':2},m['scope']['nodeIds'],m['externalBenchmark'])

    def test_centralization_wrong_benchmark_rejected(self):
        m=ns.metrics(self.s); bad=copy.deepcopy(m['externalBenchmark']); bad['maximum']=1
        with self.assertRaises(ns.Rejected): ns.centralization(m['degree'],m['scope']['nodeIds'],bad)

    def test_non_graphical_degree_collection_rejected(self):
        m=ns.metrics(self.s); values={n:0 for n in m['scope']['nodeIds']}; values['SYN-NODE-A']=3
        with self.assertRaises(ns.Rejected): ns.centralization(values,m['scope']['nodeIds'],m['externalBenchmark'])

    def test_singleton_normalization_not_invented_zero(self):
        after,_=self.apply([{'operation':'SET_BOUNDARY','includedNodeIds':['SYN-NODE-A'],'selectionReason':'Single-node analytic frame'}])
        m=ns.metrics(after); self.assertIsNone(m['density']); self.assertIsNone(m['degreeCentralization']['value'])

    def test_social_tie_not_psywerx_relationship(self):
        s=copy.deepcopy(self.s); s['ties'][0]['objectKind']='RELATIONSHIP'; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)

    def test_delta_not_effect_assertion_or_empirical_evidence(self):
        d=ns.delta(self.s,'SYN-DELTA-BAD',[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}])
        for field,value in [('objectKind','EFFECT_ASSERTION'),('occurrenceStatus','OBSERVED'),('assertedConsequences',['Trust increases'])]:
            bad=copy.deepcopy(d); bad[field]=value
            with self.subTest(field=field),self.assertRaises(ns.Rejected): ns.apply_delta(self.s,bad)

    def test_forbidden_interpretations(self):
        for use in ('EMPIRICAL_CAUSAL_EVIDENCE','MEDIATION_FROM_REACHABILITY','DYNAMIC_PREDICTION','METRIC_CAUSAL_PROPAGATION','DIRECT_RDS_EFFECT','ONTOLOGY_RELATIONSHIP_EDIT','PRACTITIONER_RECOMMENDATION','REAL_STATE_TRUTH'):
            with self.subTest(use=use),self.assertRaises(ns.Rejected): ns.assert_use(use)
        ns.assert_use('SYNTHETIC_METRIC_RECOMPUTATION')

    def test_ae_production_direct_target_safeguards_unchanged(self):
        w=ae.read(ROOT/'data/candidates/actions-events-v1/SOC-F07/workspace.json'); c=ae.Context.repository()
        c.source_ids|={s['id'] for s in ae.read(ROOT/'data/candidates/actions-events-v1/SOC-F07/source-registry.json')}
        for target in ('SOC-049','SOC-052','SYN-STATE-001'):
            bad=copy.deepcopy(w); bad['passB']['effectAssertions'][0]['targetId']=target
            with self.subTest(target=target),self.assertRaises(ae.ValidationError): ae.validate_workspace(bad,c)
        bad=copy.deepcopy(w); bad['passB']['effectAssertions'][0].update(targetKind='RELATIONSHIP',targetId='SYN-TIE-AB')
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(bad,c)

    def test_synthetic_ids_only(self):
        s=copy.deepcopy(self.s); s['nodeCatalog'][0]['id']='PERSON-REAL'; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)
        s=copy.deepcopy(self.s); s['label']='SCIENTIFIC_RECORD'; s=ns.sealed(s)
        with self.assertRaises(ns.Rejected): ns.validate_state(s)

    def test_production_path_rejected(self):
        for path in (ROOT/'data',ROOT/'schemas',ROOT/'scenario-service',ns.HERE,ns.HERE/'..'/'..'/'data'):
            with self.subTest(path=path),self.assertRaises(ns.Rejected): ns.safe_output(path)
        self.assertEqual(ns.safe_output(ns.HERE/'generated'),ns.HERE/'generated')

    def test_deterministic_generated_artifacts(self):
        for name,payload in [('synthetic-examples.json',ns.demonstration()),('state.schema.json',ns.STATE_SCHEMA),('delta.schema.json',ns.DELTA_SCHEMA)]:
            self.assertEqual((ns.HERE/'generated'/name).read_text(encoding='utf-8'),json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+'\n')

    def test_exact_ns_human_decisions(self):
        decisions=json.loads((ns.HERE/'decisions.json').read_text(encoding='utf-8'))
        self.assertEqual({r['id'] for r in decisions},{f'NS{n:02d}' for n in range(1,13)})
        self.assertEqual({r['id']:r['decision'] for r in decisions},
            {f'NS{n:02d}':('MODIFY/APPROVE-AS-MODIFIED' if n in (6,9) else 'APPROVE') for n in range(1,13)})
        self.assertTrue(all(r['governanceDecisionId']=='GOV-NETWORK-STATE-V1-2026-09-07' for r in decisions))
        decision=(ROOT/'docs/governance/NETWORK_STATE_V1_GOVERNANCE_DECISION.md').read_text(encoding='utf-8')
        self.assertIn('authorized human governor',decision)
        self.assertIn('AE04 and D10/D12 remain unchanged',decision)

    def test_architecture_links(self):
        for doc in ns.HERE.glob('*.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
                link=unquote(link.strip('<>').split('#',1)[0])
                if link and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',link):
                    self.assertTrue((doc.parent/link).exists(),(doc.name,link))


if __name__=='__main__': unittest.main()
