import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import relational_state_v1 as ns
import relational_state_contracts as contracts
import relational_state_fixtures as f
import materialize_soc_f07_completion as completion
import actions_events_v1 as ae


class NetworkStateV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding=completion.binding(); cls.auth=[completion.authorization([cls.binding])]

    def setUp(self): self.s=f.state()
    def apply(self,ops): return ns.apply_delta(self.s,f.delta(self.s,ops))
    def calc(self,variant='DEGREE_RAW_UNDIRECTED',state=None):
        state=state or self.s; b=self.binding if variant=='FREEMAN_DEGREE_CENTRALIZATION' else None
        return ns.calculate(f.request(state,variant,b),state,b,self.auth)

    def test_all_contracts_meta_validate(self):
        self.assertEqual(len(ns.schemas()),8)
        for name,value in contracts.SCHEMAS.items():
            self.assertEqual(ae.read(contracts.DIRECTORY/(name+'-v1.schema.json')),value)

    def test_optional_state_unaware_catalog_unchanged(self):
        self.assertTrue(ns.validate_state(self.s)); self.assertTrue(ae.validate_catalog(ae.read(ae.DATA)) is not False)
        self.assertNotIn('relationalState',ae.empty_catalog())

    def test_no_scientific_lifecycle_on_state(self):
        for key,value in [('activationStatus','ACTIVE'),('governance',self.binding['governance']),('lifecycleStatus','GOVERNED')]:
            bad=copy.deepcopy(self.s); bad[key]=value
            with self.subTest(key=key),self.assertRaises(ns.ValidationError): ns.validate_state(ns.seal(bad))

    def test_state_hash_and_parent(self):
        bad=copy.deepcopy(self.s); bad['revision']=2
        with self.assertRaises(ns.ValidationError): ns.validate_state(bad)
        with self.assertRaises(ns.ValidationError): ns.validate_state(ns.seal(bad))

    def test_order_invariant_state_hash(self):
        bad=copy.deepcopy(self.s); bad['nodes'].reverse(); bad['ties'].reverse(); bad['groups'].reverse()
        self.assertEqual(ns.content_hash(bad),self.s['contentHash'])

    def test_duplicate_node(self):
        bad=copy.deepcopy(self.s); bad['nodes'].append(copy.deepcopy(bad['nodes'][0]))
        with self.assertRaises(ns.ValidationError): ns.validate_state(ns.seal(bad))

    def test_duplicate_tie_and_reverse_undirected(self):
        for pair in ('AB','BA'):
            with self.subTest(pair=pair),self.assertRaises(ns.ValidationError): self.apply([{'operation':'ADD_TIE','tie':f.tie(pair)}])

    def test_social_tie_not_scientific_relationship(self):
        for key,value in [('id','REL-SOC-001'),('objectKind','RELATIONSHIP')]:
            bad=copy.deepcopy(self.s); bad['ties'][0][key]=value
            with self.assertRaises(ns.ValidationError): ns.validate_state(ns.seal(bad))

    def test_missing_endpoint(self):
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'ADD_TIE','tie':f.tie('AZ')}])

    def test_atomic_failure(self):
        before=copy.deepcopy(self.s)
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}, {'operation':'REMOVE_TIE','tieId':'SYN-TIE-NONE'}])
        self.assertEqual(before,self.s)

    def test_stale_preconditions(self):
        d=f.delta(self.s,[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]); d['expectedState']['contentHash']='f'*64
        with self.assertRaises(ns.ValidationError): ns.apply_delta(self.s,d)

    def test_no_cross_scenario(self):
        d=f.delta(self.s,[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]); d['scenarioId']='SYN-OTHER-SCENARIO'
        with self.assertRaises(ns.ValidationError): ns.apply_delta(self.s,d)

    def test_no_arbitrary_patch(self):
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'replace','path':'/ties','value':[]}])

    def test_added_tie_no_ontology_edge(self):
        after,receipt=self.apply([{'operation':'ADD_TIE','tie':f.tie('AD')}])
        self.assertEqual(len(after['ties']),len(self.s['ties'])+1); self.assertEqual(receipt['ontologyRelationshipsEdited'],0)
        self.assertFalse(receipt['empiricalEvidenceProduced']); self.assertFalse(receipt['causalContribution'])

    def test_deactivate_node_explicit_incident_removal(self):
        after,receipt=self.apply([{'operation':'DEACTIVATE_NODE','nodeId':'SYN-NODE-C','incidentPolicy':'REMOVE_AND_RECORD'}])
        self.assertEqual(receipt['removedTieIds'],['SYN-TIE-AC','SYN-TIE-BC','SYN-TIE-CD'])
        self.assertFalse(next(n for n in after['nodes'] if n['id']=='SYN-NODE-C')['active'])

    def test_node_identity_not_recycled(self):
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'DEACTIVATE_NODE','nodeId':'SYN-NODE-A','incidentPolicy':'REMOVE_AND_RECORD'},
                {'operation':'ADD_NODE','node':f.node('A'),'includeInBoundary':True}])

    def test_tie_identity_not_recycled(self):
        after,_=self.apply([{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}])
        with self.assertRaises(ns.ValidationError): ns.apply_delta(after,f.delta(after,[{'operation':'ADD_TIE','tie':f.tie('AB')}],'SYN-DELTA-NEXT'))

    def test_membership_not_friendship(self):
        after,_=self.apply([{'operation':'CHANGE_MEMBERSHIP','nodeId':'SYN-NODE-A','groupIds':['SYN-GROUP-B']}])
        self.assertEqual(after['ties'],self.s['ties'])

    def test_seating_not_friendship(self):
        after,_=self.apply([{'operation':'CHANGE_CONTACT_OPPORTUNITY','opportunity':f.opportunity()}])
        self.assertEqual(after['ties'],self.s['ties']); self.assertEqual(len(after['opportunities']),2)

    def test_access_not_friendship_deletion(self):
        after,_=self.apply([{'operation':'CHANGE_ACCESS','opportunityId':'SYN-OPP-ACCESS','enabled':False}])
        self.assertEqual(after['ties'],self.s['ties']); self.assertFalse(after['opportunities'][0]['enabled'])

    def test_boundary_not_real_tie_formation(self):
        b=copy.deepcopy(self.s['boundary']); b['revision']+=1; b['includedNodeIds'].append('SYN-NODE-E')
        after,receipt=self.apply([{'operation':'CHANGE_BOUNDARY','boundary':b}])
        self.assertEqual(after['ties'],self.s['ties']); self.assertEqual(receipt['changeClass'],'ANALYTIC_BOUNDARY_ONLY')
        self.assertNotEqual(self.calc('DENSITY_SIMPLE_UNDIRECTED')['value'],self.calc('DENSITY_SIMPLE_UNDIRECTED',after)['value'])

    def test_boundary_exclusion_not_node_death(self):
        b=copy.deepcopy(self.s['boundary']); b['revision']+=1; b['includedNodeIds'].remove('SYN-NODE-A')
        after,_=self.apply([{'operation':'CHANGE_BOUNDARY','boundary':b}])
        self.assertEqual(after['nodes'],self.s['nodes']); self.assertEqual(after['ties'],self.s['ties'])

    def test_boundary_mutation_bundle_rejected(self):
        b=copy.deepcopy(self.s['boundary']); b['revision']+=1
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'CHANGE_BOUNDARY','boundary':b},{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}])

    def test_weight_requires_meaning(self):
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'UPDATE_TIE_WEIGHT','tieId':'SYN-TIE-AB','weight':2,'weightMeaning':None,'weightUnit':None}])

    def test_intensity_and_unknown_not_implicitly_binary(self):
        for weight,meaning,unit in [(2,'INTENSITY','fictional-unit'),(None,None,None)]:
            after,_=self.apply([{'operation':'UPDATE_TIE_WEIGHT','tieId':'SYN-TIE-AB','weight':weight,'weightMeaning':meaning,'weightUnit':unit}])
            self.assertEqual(self.calc(state=after)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_static_snapshot_no_dynamic_prediction(self):
        bad=copy.deepcopy(self.s); bad['window']['end']='2026-02-01T00:00:00Z'
        with self.assertRaises(ns.ValidationError): ns.validate_state(ns.seal(bad))
        d=f.delta(self.s,[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]); d['effectiveAt']='2026-02-01T00:00:00Z'
        with self.assertRaises(ns.ValidationError): ns.apply_delta(self.s,d)

    def test_interval_half_open_selection(self):
        s=copy.deepcopy(self.s); s['window'].update(mode='INTERVAL',end='2026-02-01T00:00:00Z',aggregation='PERSISTENT_THROUGH_WINDOW')
        s['ties'][0]['validUntil']=s['window']['end']; s=ns.seal(s)
        self.assertEqual(self.calc(state=s)['value']['SYN-NODE-A'],2)

    def test_directed_metric_explicitly_unsupported(self):
        s=copy.deepcopy(self.s); s['ties'][0]['directed']=True; s=ns.seal(s); ns.validate_state(s)
        self.assertEqual(self.calc(state=s)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_multiplex_no_collapse(self):
        s=copy.deepcopy(self.s); s['layerIds'].append('SYN-LAYER-OTHER'); t=f.tie('AD'); t['layerId']='SYN-LAYER-OTHER'; s['ties'].append(t); s=ns.seal(s)
        self.assertEqual(self.calc(state=s)['value'],self.calc()['value'])

    def test_five_metric_hand_checks(self):
        self.assertEqual(self.calc()['value'],{'SYN-NODE-A':2,'SYN-NODE-B':2,'SYN-NODE-C':3,'SYN-NODE-D':1})
        self.assertAlmostEqual(self.calc('DENSITY_SIMPLE_UNDIRECTED')['value'],2/3)
        self.assertAlmostEqual(self.calc('CLUSTERING_LOCAL_UNDIRECTED')['value']['SYN-NODE-C'],1/3)
        self.assertEqual(self.calc('FRAGMENTATION_UNREACHABLE_PAIRS')['value'],0)
        self.assertAlmostEqual(self.calc('FREEMAN_DEGREE_CENTRALIZATION')['value'],2/3)

    def test_collection_one_ego_and_missing_node_fail(self):
        for length in (1,3):
            r=f.request(self.s,'FREEMAN_DEGREE_CENTRALIZATION',self.binding); r['collection']['values']=r['collection']['values'][:length]
            self.assertEqual(ns.calculate(r,self.s,self.binding,self.auth)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_collection_duplicate_or_wrong_degree_fail(self):
        for change in ('duplicate','wrong'):
            r=f.request(self.s,'FREEMAN_DEGREE_CENTRALIZATION',self.binding)
            if change=='duplicate': r['collection']['values'][1]=copy.deepcopy(r['collection']['values'][0])
            else: r['collection']['values'][0]['value']=3
            self.assertEqual(ns.calculate(r,self.s,self.binding,self.auth)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_collection_other_centrality_fails(self):
        for variant in ('BETWEENNESS_CENTRALIZATION','EIGENVECTOR_CENTRALIZATION','CLOSENESS_CENTRALIZATION'):
            b=copy.deepcopy(self.binding); b['metricVariant']=variant
            with self.assertRaises(ns.ValidationError): ns.validate_binding(b,self.auth)

    def test_collection_benchmark_missing_wrong(self):
        for value in (None,{'kind':'SAME_SIZE_SIMPLE_UNDIRECTED_STAR','nodeCount':4,'maximum':1}):
            r=f.request(self.s,'FREEMAN_DEGREE_CENTRALIZATION',self.binding); r['externalBenchmark']=value
            self.assertEqual(ns.calculate(r,self.s,self.binding,self.auth)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_collection_state_boundary_window_alignment(self):
        for key in ('stateRef','boundary','window'):
            r=f.request(self.s,'FREEMAN_DEGREE_CENTRALIZATION',self.binding)
            if key=='window': r['collection'][key]['start']='2025-01-01T00:00:00Z'
            else: r['collection'][key]['revision']+=1
            self.assertEqual(ns.calculate(r,self.s,self.binding,self.auth)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_scientific_use_fails_closed(self):
        r=f.request(self.s,'FREEMAN_DEGREE_CENTRALIZATION',self.binding); r['useMode']='SCIENTIFIC_USE'
        result=ns.calculate(r,self.s,self.binding,self.auth); self.assertEqual(result['status'],'NOT_AUTHORIZED')
        self.assertTrue(all(result[k] is False for k in ('scientificUseEligible','modelEligibility','practitionerActionEligibility','causalContribution')))

    def test_no_double_propagation(self):
        r=f.request(self.s,'DEGREE_RAW_UNDIRECTED'); r['propagationRoutes'].append('DIRECT_RDS_CAUSAL_EFFECT')
        with self.assertRaises(ns.ValidationError): ns.calculate(r,self.s)
        r=f.request(self.s,'FREEMAN_DEGREE_CENTRALIZATION',self.binding); r['contributionIdentity']='SYN-OTHER-CONTRIBUTION'
        self.assertEqual(ns.calculate(r,self.s,self.binding,self.auth)['status'],'UNSUPPORTED_OR_INCOMPLETE')

    def test_metric_reachability_not_mediation(self):
        r=f.request(self.s,'FRAGMENTATION_UNREACHABLE_PAIRS'); r['mediatedEffect']=True
        with self.assertRaises(ns.ValidationError): ns.calculate(r,self.s)

    def test_delta_not_empirical_or_effect(self):
        for key,value in [('empiricalEvidenceProduced',True),('realWorldSuccessClaim',True),('objectKind','EFFECT_ASSERTION')]:
            d=f.delta(self.s,[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]); d[key]=value
            with self.assertRaises(ns.ValidationError): ns.apply_delta(self.s,d)

    def test_observation_not_truth(self):
        o=f.observation('SYN-OBS-1','SYN-TIE-AB'); o['missingness']['realNetworkTruthClaim']=True
        with self.assertRaises(ns.ValidationError): ns.validate_observation(ns.seal(o))

    def test_stipulated_weight_change_cannot_inherit_observed_result(self):
        o=f.observation('SYN-OBS-1','SYN-TIE-AB')
        state=ns.construct_from_observation(f.empty_state('SYN-STATE-OBS'),o,'Explicit incomplete assumption',
            [n['id'] for n in o['nodes']],[t['id'] for t in o['ties']])
        identifier=state['ties'][0]['id']
        delta=f.delta(state,[{'operation':'UPDATE_TIE_WEIGHT','tieId':identifier,'weight':2,'weightMeaning':'INTENSITY','weightUnit':'fictional-unit'}])
        result,_=ns.apply_delta(state,delta)
        changed=next(t for t in result['ties'] if t['id']==identifier)
        self.assertEqual(changed['basis'],'ASSUMED'); self.assertIsNone(changed['observationRef'])
        self.assertEqual(changed['provenanceId'],delta['provenance']['id'])
        self.assertEqual(state['ties'][0]['basis'],'OBSERVED')
        self.assertTrue(ns.validate_observation(o))

    def test_delta_cannot_create_observed_tie(self):
        tie=f.tie('AD'); tie['basis']='OBSERVED'
        with self.assertRaises(ns.ValidationError): self.apply([{'operation':'ADD_TIE','tie':tie}])

    def test_observation_inference_method_required(self):
        o=f.observation('SYN-OBS-1','SYN-TIE-AB'); o['ties'][0]['basis']='INFERRED'
        with self.assertRaises(ns.ValidationError): ns.validate_observation(ns.seal(o))

    def test_observation_missingness_explicit(self):
        o=f.observation('SYN-OBS-1','SYN-TIE-AB'); del o['missingness']['missingNodes']
        with self.assertRaises(ns.ValidationError): ns.validate_observation(ns.seal(o))

    def test_observation_cannot_overwrite(self):
        o=f.observation('SYN-OBS-1','SYN-TIE-AB')
        with self.assertRaises(ns.ValidationError): ns.construct_from_observation(self.s,o,'Assume report',[],[])

    def test_two_observations_different_assumptions(self):
        results=[]
        for n,pair in [(1,'AB'),(2,'AC')]:
            o=f.observation(f'SYN-OBS-{n}','SYN-TIE-'+pair)
            s=ns.construct_from_observation(f.empty_state(f'SYN-STATE-{n}'),o,'Treat selected report as incomplete assumption',
                [v['id'] for v in o['nodes']],[v['id'] for v in o['ties']])
            results.append(s); self.assertEqual(s['assumptions']['coverage'],'INCOMPLETE')
            self.assertFalse(s['assumptions']['realNetworkTruthClaim']); ns.validate_state(s,{o['id']:o})
        self.assertNotEqual(results[0]['ties'],results[1]['ties'])

    def test_replay_and_rollback_by_retained_parent(self):
        d=f.delta(self.s,[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]); after,receipt=ns.apply_delta(self.s,d)
        self.assertEqual(ns.replay(self.s,d,receipt),after); self.assertEqual(self.s,f.state())
        receipt['causalContribution']=True
        with self.assertRaises(ns.ValidationError): ns.replay(self.s,d,receipt)

    def test_delta_reference_is_not_execution_or_evidence(self):
        d=f.delta(self.s,[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}])
        link={'schemaVersion':'1.0.0','objectKind':'SCENARIO_OPERATION_REFERENCE','occurrenceRef':None,'happeningTypeRef':None,
            'deltaRef':{'id':d['id'],'revision':1,'contentHash':ns.digest(d)},'relation':'REFERENCES_STIPULATED_OPERATION_NOT_EFFECT',
            'automaticExecution':False,'empiricalConsequenceClaim':False}
        ns.validate_operation_reference(link,d); link['automaticExecution']=True
        with self.assertRaises(ns.ValidationError): ns.validate_operation_reference(link,d)

    def test_all_rds_ae_direct_targets_rejected(self):
        w=ae.read(ROOT/'data/candidates/actions-events-v1/SOC-F07/workspace.json'); context=ae.Context.repository()
        context.source_ids|={s['id'] for s in ae.read(ROOT/'data/candidates/actions-events-v1/SOC-F07/source-registry.json')}
        rds=[k for k,v in context.entities.items() if v['entityType']=='RELATIONAL_DERIVED_STATE']
        self.assertEqual(len(rds),41)
        for target in rds:
            bad=copy.deepcopy(w); bad['passB']['effectAssertions'][0]['targetId']=target
            with self.subTest(target=target),self.assertRaises(ae.ValidationError): ae.validate_workspace(bad,context)

    def test_no_ae_target_vocabulary_expansion(self):
        schema=ae.read(ROOT/'schemas/actions-events/v1/effect-assertion-v1.schema.json')
        self.assertEqual(set(schema['properties']['targetKind']['enum']),{'DRIVER','RELATIONSHIP'})

    def test_synthetic_privacy_and_output_isolation(self):
        bad=copy.deepcopy(self.s); bad['privacy']['externalIdentityReference']='PERSON-123'
        with self.assertRaises(ns.ValidationError): ns.validate_state(ns.seal(bad))
        for path in (ROOT/'data',ROOT/'schemas',ROOT/'scenario-service',ROOT):
            with self.assertRaises(ns.ValidationError): f.safe_output(path)

    def test_twelve_cases_deterministic(self):
        d=f.demonstration(); self.assertEqual(d,f.demonstration()); self.assertEqual(len(d['examples']),12)
        self.assertFalse(d['realPersonData']); self.assertEqual(d['newActive'],0)


if __name__=='__main__': unittest.main()
