import copy, hashlib, importlib.util, json, subprocess, sys, unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/governance/post-scale-up/contribution"
spec=importlib.util.spec_from_file_location("cc_stage_e",ROOT/"prototypes/contribution-identity-v1/contribution_control.py")
cc=importlib.util.module_from_spec(spec);spec.loader.exec_module(cc)
def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def runtime(group):
    key=sha(group["identityDimensions"])
    members=[{"recordClass":m["recordClass"],"recordId":m["recordId"],"recordVersion":str(m["recordRevision"]),"recordHash":m["recordHash"],"memberRole":m["memberRole"],"representationRelationship":m["representationRelationship"],"identityAlignmentKey":key} for m in group["memberRepresentations"]]
    return {"schemaVersion":"x","groupId":group["groupId"],"groupVersion":group["groupVersion"],"scientificContributionDefinition":group["scientificContributionDefinition"],"scope":group["scope"],"memberRepresentations":members,"consumerPolicy":"EXPLICIT_FAIL_CLOSED","countingPolicy":group["countingPolicy"],"propagationPolicy":group["propagationPolicy"],"derivationPolicy":group["derivationPolicy"],"causalIndependenceStatus":group["causalIndependenceStatus"],"evidenceOverlapStatus":group["evidenceOverlapStatus"],"constituentOverlapStatus":group["constituentOverlapStatus"],"provenance":group["provenance"],"governance":{},"causalAuthority":False,"hasWeight":False,"hasPolarity":False,"hasActivation":False,"hasScientificLifecycle":False}
def candidates(group):return [{"recordClass":m["recordClass"],"recordId":m["recordId"],"recordVersion":str(m["recordRevision"]),"recordHash":m["recordHash"]} for m in group["memberRepresentations"]]

class ContributionStageE(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  subprocess.run([sys.executable,"prototypes/contribution-identity-v1/build_reference_package.py"],cwd=ROOT,check=True,capture_output=True,text=True)
  cls.group=read(DATA/"contribution-groups-prototype.json")["groups"][0];cls.rg=runtime(cls.group);cls.cands=candidates(cls.group)

 def test_governance_and_status(self):
  d=read(DATA/"contribution-architecture-decision-001.json")
  self.assertEqual(d["decisionId"],"GOV-CONTRIBUTION-IDENTITY-001-2026-09-27");self.assertEqual(d["decisionOutcome"],"APPROVED_BOUNDED_A_PLUS_B_PLUS_C_DIRECTION");self.assertEqual(d["wpPsg005Status"],"NOT_STARTED")
  wp=next(x for x in read(ROOT/"data/governance/post-scale-up/work-packages.json")["workPackages"] if x["workPackageId"]=="WP-PSG-004")
  self.assertEqual(wp["stages"]["D_humanGovernanceDecision"],"COMPLETE_BOUNDED_DIRECTION_APPROVED")
  registry=read(ROOT/"data/contribution-control-v1/groups.json")
  self.assertEqual(wp["stages"]["E_implementation"],"PRODUCTION_ARCHITECTURE_INSTALLED")
  self.assertEqual(wp["productionImplementationStatus"],"PHASE_1_REPETITION_COMPLETE_SHADOW_ONLY" if registry["groups"] else "PHASE_0_COMPLETE_EMPTY_REGISTRY")
  self.assertEqual(wp["productionImplementationDecisionId"],"GOV-CONTRIBUTION-IMPLEMENTATION-001-2026-09-27")

 def test_schema_and_authority_firewall(self):
  schema=read(ROOT/"prototypes/contribution-identity-v1/schemas/contribution-group.schema.json");Draft202012Validator(schema).validate(self.group)
  for x in ("causalEvidence","executionAuthority","hasWeight","hasPolarity","hasLifecycle","hasActivation","hasPropagationState"):self.assertFalse(self.group[x])
  self.assertEqual(self.group["objectKind"],"CONTRIBUTION_IDENTITY_CONTROL")

 def test_exact_hashes_and_native_compatibility(self):
  rel=next(x for x in read(ROOT/"data/relationship-intervention-v1/relationships.json")["relationships"] if x["id"]=="REL-V1-PSY-LAYER-001")
  ea=next(x for x in read(ROOT/"data/actions-events-v1/catalog.json")["effectAssertions"] if x["id"]=="EA-V1-PSY-LAYER-001")
  native={("RELATIONSHIP",rel["id"]):{"revision":rel["revision"],"recordHash":sha(rel),"nativeContributionId":None},("EFFECT_ASSERTION",ea["id"]):{"revision":ea["revision"],"recordHash":sha(ea),"nativeContributionId":ea["contribution"]["groupId"]}}
  self.assertTrue(cc.validate_native_controls(self.group,native));bad=copy.deepcopy(native);bad[("EFFECT_ASSERTION",ea["id"])]["nativeContributionId"]="WRONG"
  with self.assertRaises(cc.ValidationError):cc.validate_native_controls(self.group,bad)

 def test_registry_zero_one_many_versions_no_implicit(self):
  empty=cc.ContributionRegistry();self.assertEqual(empty.versions("x"),[])
  r=cc.ContributionRegistry([self.rg]);self.assertEqual(r.get(self.rg["groupId"],"1.0.0")["groupId"],self.rg["groupId"])
  with self.assertRaises(cc.ValidationError):r.get(self.rg["groupId"],"LATEST")
  v2=copy.deepcopy(self.rg);v2["groupVersion"]="1.1.0";r.add(v2);self.assertEqual(r.versions(self.rg["groupId"]),["1.0.0","1.1.0"])
  with self.assertRaises(cc.ValidationError):r.add(v2)

 def test_select_relationship_or_ea_count_once(self):
  for selected in ("REL-V1-PSY-LAYER-001","EA-V1-PSY-LAYER-001"):
   receipt=cc.resolve_contribution_set(self.cands,{self.rg["groupId"]:selected},[self.rg],{})
   self.assertEqual(receipt["resolutionOutcome"],"COUNT_ONCE");self.assertEqual(receipt["includedRepresentations"],[selected]);self.assertFalse(receipt["graphAuthorityGranted"])
  with self.assertRaisesRegex(cc.ValidationError,"SELECT_ONE_REQUIRED"):cc.resolve_contribution_set(self.cands,{},[self.rg],{})
  with self.assertRaises(cc.ValidationError):cc.resolve_contribution_set(self.cands,{self.rg["groupId"]:[x["recordId"] for x in self.cands]},[self.rg],{})

 def test_receipt_fingerprint_and_hash_mismatch(self):
  sel={self.rg["groupId"]:"REL-V1-PSY-LAYER-001"};a=cc.resolve_contribution_set(self.cands,sel,[self.rg],{"x":1});b=cc.resolve_contribution_set(self.cands,sel,[self.rg],{"x":1});self.assertEqual(a["deterministicFingerprint"],b["deterministicFingerprint"])
  bad=copy.deepcopy(self.cands);bad[0]["recordHash"]="0"*64
  with self.assertRaises(cc.ValidationError):cc.resolve_contribution_set(bad,sel,[self.rg],{})

 def test_identity_dimensions_and_false_grouping(self):
  dims=self.group["identityDimensions"]
  self.assertTrue(cc.same_identity_dimensions(dims,copy.deepcopy(dims)))
  for key in cc.IDENTITY_DIMENSIONS:
   other=copy.deepcopy(dims);other[key]+=" changed";self.assertFalse(cc.same_identity_dimensions(dims,other),key)
  # Superficial shared metadata cannot override a governed dimension mismatch.
  for label in ("source","EvidenceAssessment","target","intervention","HappeningType","mechanism","occurrence","Layer","Family","cross-level mapping","RDS profile","graph reachability"):
   other=copy.deepcopy(dims);other["causalContrast"]="different";self.assertFalse(cc.same_identity_dimensions(dims,other),label)

 def test_group_versioning_and_collision(self):
  v2=copy.deepcopy(self.group);v2["memberRepresentations"].append(copy.deepcopy(v2["memberRepresentations"][0]));v2["memberRepresentations"][-1]["recordId"]="SYN-ALT"
  self.assertEqual(cc.classify_group_change(self.group,v2),"NEW_IMMUTABLE_GROUP_VERSION")
  new=copy.deepcopy(self.group);new["identityDimensions"]["causalContrast"]="different";self.assertEqual(cc.classify_group_change(self.group,new),"NEW_GROUP_IDENTITY_AND_SCIENTIFIC_READJUDICATION")
  contradictory=copy.deepcopy(self.rg);contradictory["groupId"]="OTHER";contradictory["scientificContributionDefinition"]="different"
  with self.assertRaises(cc.ValidationError):cc.resolve_contribution_set(self.cands,{self.rg["groupId"]:"REL-V1-PSY-LAYER-001"},[self.rg,contradictory],{})

 def test_resolution_cases_and_migration(self):
  cases=read(DATA/"contribution-resolution-test-cases.json");self.assertTrue(cases["fingerprintDeterministic"]);self.assertEqual(cases["countOnceResult"],.2);self.assertEqual(cases["withIndependentResult"],.3)
  mig=read(DATA/"contribution-migration-dry-run.json");self.assertEqual(mig["recordCount"],23);self.assertEqual(sum(mig["counts"].values()),23);self.assertEqual(mig["counts"]["READY_FOR_EXTERNAL_GROUP"],2);self.assertEqual(mig["counts"]["INSUFFICIENT_ROUTE_DEFINITION"],10);self.assertTrue(all(not r["productionMutationAuthorized"] for r in mig["records"]))

 def test_handoffs_and_protected_counts(self):
  h=read(DATA/"contribution-stage-e-handoffs.json");self.assertEqual(h["wpPsg005"]["status"],"NOT_STARTED");self.assertFalse(h["wpPsg005"]["adjudicationPerformed"]);self.assertEqual(len(h["wpPsg005"]["records"][2]["aggregateRdsIds"]),10)
  entities=read(ROOT/"data/entities.json");self.assertEqual(sum(x.get("entityType")=="DRIVER" for x in entities),770);self.assertEqual(len(read(ROOT/"data/relational-derived-states.json")),41)
  self.assertFalse(read(DATA/"contribution-groups-prototype.json")["productionRegistryInstalled"])

if __name__=="__main__":unittest.main()
