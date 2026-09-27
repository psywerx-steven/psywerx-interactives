"""WP-PSG-002 Stage E non-production reference implementation gates."""
import copy, hashlib, importlib.util, json, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; PROTO=ROOT/'prototypes/cross-level-exposure-v1'; DATA=ROOT/'data/governance/post-scale-up/cross-level'
sys.path.insert(0,str(PROTO)); import stage_e as xle
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
class StageETest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.registry=read(PROTO/'registry/prototype-registry.json'); cls.dry=read(DATA/'cross-level-migration-dry-run.json'); cls.handoffs=read(DATA/'cross-level-stage-e-handoffs.json'); cls.delta=read(DATA/'cross-level-production-delta-preview.json'); cls.protected=read(DATA/'cross-level-stage-e-protected-hashes.json'); cls.rels={r['id']:r for r in read(ROOT/'data/relationships.json')['relationships']}; cls.maps={m['mappingId']:m for m in cls.registry['mappings']}; cls.binds={b['relationshipId']:b for b in cls.registry['bindings']}
 def test_isolated_prototype_and_model(self):
  self.assertEqual(self.registry['mappingModelFinding'],'REUSABLE_MAPPING_PLUS_IMMUTABLE_RELATIONSHIP_BINDING'); self.assertFalse(self.registry['productionMaterializationAuthorized'])
  decision=read(DATA/'cross-level-production-implementation-decision-001.json'); self.assertTrue(decision['phase0Authorized']); self.assertTrue((ROOT/'schemas/cross-level-exposure-mapping.schema.json').exists()); self.assertTrue((ROOT/'data/cross-level-exposure-v1').exists())
 def test_all_38_exactly_once_and_counts(self):
  self.assertEqual(len(self.dry['records']),38); self.assertEqual(len({r['relationshipId'] for r in self.dry['records']}),38); self.assertEqual(self.dry['stageECounts'],{'BLOCKED_NETWORK_STATE_DEPENDENCY':3,'MAPPING_PREVIEW_REQUIRED':13,'NOT_APPLICABLE':13,'NO_CROSS_LEVEL_EXPOSURE_MAPPING_REQUIRED':2,'NO_MAPPING_REQUIRED_EXISTING_SUBSTANTIVE_BRIDGE':5,'RESEARCH_NEEDED_BEFORE_MAPPING':2}); self.assertEqual(sum(self.dry['stageCBaselineCounts'].values()),38)
 def test_every_dry_run_row_preserves_authority(self):
  for r in self.dry['records']:
   self.assertFalse(r['productionMutationAuthorized']); self.assertFalse(r['relationshipMutationAuthorized']); self.assertFalse(r['executionAuthorized']); self.assertFalse(r['activationAuthorized']); self.assertEqual(r['rollbackState'],'CURRENT_PRODUCTION_RELATIONSHIP_UNCHANGED')
 def test_positive_controls_and_receipts(self):
  self.assertEqual({r['relationshipId'] for r in self.registry['eligibilityReceipts']},{'REL-INS-040','REL-INS-046','REL-SOC-067'}); self.assertTrue(all(r['evaluationResult']=='CROSS_LEVEL_READY_FOR_REVIEW' for r in self.registry['eligibilityReceipts'])); self.assertTrue(all(not r['mappingCausalEvidence'] and not r['mappingExecutionAuthority'] for r in self.registry['eligibilityReceipts']))
 def test_mapping_has_no_causal_lifecycle_or_graph_semantics(self):
  for m in self.registry['mappings']:
   xle.validate_mapping(m); self.assertFalse(m['causalEvidence']); self.assertFalse(m['executionAuthority']); self.assertFalse(m['hasWeight']); self.assertFalse(m['hasLifecycle']); self.assertFalse(m['hasPropagationState']); self.assertFalse(xle.FORBIDDEN_MAPPING_FIELDS & set(m))
 def test_exact_version_and_immutability(self):
  reg=xle.PrototypeRegistry(); m=self.registry['mappings'][0]; reg.add_mapping(m)
  with self.assertRaises(xle.PrototypeValidationError): reg.mapping(m['mappingId'],'LATEST')
  with self.assertRaises(xle.PrototypeValidationError): reg.add_mapping(m)
  changed=copy.deepcopy(m); changed['exposureDefinition']='drift'
  with self.assertRaises(xle.PrototypeValidationError): xle.validate_mapping_identity(m,changed)
 def test_reusable_mapping_plus_exact_bindings(self):
  ambient=[b for b in self.registry['bindings'] if b['mappingId']=='XLEM-PROTOTYPE-GROUP-AMBIENT-PERSON-001']; self.assertEqual(len(ambient),2); self.assertEqual(len({b['relationshipId'] for b in ambient}),2); self.assertEqual(len({b['mappingVersion'] for b in ambient}),1)
 def test_wrong_attachment_entities_levels_and_hash_rejected(self):
  b=copy.deepcopy(self.binds['REL-INS-040']); m=self.maps[b['mappingId']]; rel=self.rels['REL-INS-040']
  for field,value in [('sourceEntityId','WRONG'),('targetEntityId','WRONG'),('sourceLevel','GROUP'),('relationshipHash','bad')]:
   bad=copy.deepcopy(b); bad[field]=value
   with self.subTest(field), self.assertRaises(xle.PrototypeValidationError): xle.validate_relationship_attachment(bad,m,rel)
 def eval040(self,**overrides):
  b=self.binds['REL-INS-040']; m=self.maps[b['mappingId']]; c={'sourceLevel':'INSTITUTION','targetLevel':'PERSON','implementationSatisfied':True,'actualExposureSatisfied':True,'perceptionSatisfied':True,'coverage':'FULL','coverageRuleSatisfied':True,'observedTemporalOrder':b['temporalAlignment'],'mappingEvidenceSufficient':True}; c.update(overrides); return xle.resolve_cross_level_eligibility(m,b,self.rels['REL-INS-040'],c)
 def test_membership_eligibility_implementation_insufficient_without_exposure(self): self.assertEqual(self.eval040(actualExposureSatisfied=False)['evaluationResult'],'BLOCKED_NO_EXPOSURE_ROUTE')
 def test_missing_implementation(self): self.assertEqual(self.eval040(implementationSatisfied=False)['evaluationResult'],'BLOCKED_NO_IMPLEMENTATION_ROUTE')
 def test_perception_semantics(self): self.assertEqual(self.eval040(perceptionSatisfied=False)['evaluationResult'],'BLOCKED_PERCEPTION_ROUTE_REQUIRED'); self.assertFalse(self.binds['REL-INS-046']['perceptionRequired']); self.assertTrue(self.binds['REL-SOC-067']['perceptionRequired'])
 def test_partial_coverage(self): self.assertEqual(self.eval040(coverage='PARTIAL',coverageRuleSatisfied=False)['evaluationResult'],'BLOCKED_PARTIAL_COVERAGE_UNBOUND'); self.assertEqual(self.eval040(coverage='PARTIAL',coverageRuleSatisfied=True)['evaluationResult'],'CROSS_LEVEL_READY_FOR_REVIEW')
 def test_temporal_reversal(self): self.assertEqual(self.eval040(observedTemporalOrder=list(reversed(self.binds['REL-INS-040']['temporalAlignment'])))['evaluationResult'],'BLOCKED_TEMPORAL_MISMATCH')
 def test_ambient_and_happeningtype_conditional(self):
  a=self.maps['XLEM-PROTOTYPE-GROUP-AMBIENT-PERSON-001']; self.assertTrue(a['ambientContextAllowed']); self.assertFalse(self.binds['REL-SOC-067']['happeningTypeIds']); d=next(b for b in self.registry['bindings'] if b['relationshipId']=='SYN-REL-DISCRETE-ASSIGNMENT-001'); self.assertEqual(d['happeningTypeIds'],['HT-V1-SOC-F07-002'])
 def test_network_state_fail_closed_and_handoff(self):
  self.assertEqual({r['relationshipId'] for r in self.handoffs['wpPsg003']},{'REL-SOC-017','REL-SOC-035','REL-TEC-050'}); self.assertEqual(sum(r['networkStateDependency'] for r in self.dry['records']),3)
 def test_rds_causal_firewall(self):
  self.assertFalse(self.handoffs['wpPsg005']['causalSourceEligible']); ps=read(ROOT/'data/rds-computation-v1/profiles.json')['profiles']; self.assertTrue(all(not p['causalSourceEligible'] for p in ps))
 def test_no_ontology_dependency_or_new_construct(self): self.assertEqual(self.handoffs['wpPsg007']['constructGapsFound'],0); self.assertEqual(self.handoffs['wpPsg007']['newConstructsCreated'],0)
 def test_phase_plan_is_narrow_and_shadow_only(self): self.assertEqual(self.delta['phase0Preview']['relationshipMigrations'],0); self.assertEqual(self.delta['phase1Preview']['recommendedControls'],['REL-INS-040']); self.assertEqual(self.delta['phase1Preview']['mode'],'SHADOW_VALIDATION_ONLY'); self.assertEqual(self.delta['phase1Preview']['graphInclusionChanges'],0); self.assertEqual(self.delta['phase1Preview']['simulationChanges'],0)
 def test_production_implementation_decision_is_bounded_and_complete(self):
  d=read(DATA/'cross-level-production-implementation-decision-001.json'); self.assertEqual(d['decisionId'],'GOV-CROSS-LEVEL-IMPLEMENTATION-001-2026-09-26'); self.assertEqual(d['implementationStatus'],'PHASE_1_REL_INS_040_COMPLETE_SHADOW_ONLY'); self.assertEqual(d['phase1RelationshipIds'],['REL-INS-040']); self.assertEqual(d['remainingRelationshipIdsAuthorized'],0); self.assertFalse(d['phase1Requirements']['productionRelationshipMutation']); self.assertTrue(d['productionState']['schemasInstalled']); self.assertEqual(d['productionState']['mappingsMaterialized'],1); self.assertEqual(d['productionState']['bindingsMaterialized'],1); self.assertEqual(d['productionState']['relationshipsMutated'],0)
 def test_fingerprint_determinism(self):
  a={'b':2,'a':1}; self.assertEqual(xle.canonical_fingerprint(a),xle.canonical_fingerprint({'a':1,'b':2})); self.assertNotEqual(xle.canonical_fingerprint(a),xle.canonical_fingerprint({'a':1,'b':3}))
 def test_protected_files_unchanged(self):
  for p,e in self.protected['files'].items():
   with self.subTest(p): self.assertEqual(hashlib.sha256((ROOT/p).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),e)
  self.assertEqual(len(read(ROOT/'data/drivers.json')),770); entities=read(ROOT/'data/entities.json'); self.assertEqual(sum(e.get('entityType')=='RELATIONAL_DERIVED_STATE' for e in entities),41)
if __name__=='__main__': unittest.main()
