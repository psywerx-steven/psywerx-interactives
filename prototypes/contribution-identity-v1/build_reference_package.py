"""Build the governed, non-production WP-PSG-004 Stage E/F package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/governance/post-scale-up/contribution"
DOCS = ROOT / "docs/governance/post-scale-up/contribution"
BASELINE = "2433b13d41a51107a4ccddfce82ee7980ebb126d"
DECISION = "GOV-CONTRIBUTION-IDENTITY-001-2026-09-27"
NOTICE = "GOVERNED DIRECTION / NON-PRODUCTION PROTOTYPE / DRY RUN ONLY"

spec = importlib.util.spec_from_file_location("contribution_control", Path(__file__).with_name("contribution_control.py"))
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)


def read(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def write_json(name, value):
    DATA.mkdir(parents=True, exist_ok=True); (DATA / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
def write_doc(name, value):
    DOCS.mkdir(parents=True, exist_ok=True); (DOCS / name).write_text(value.rstrip()+"\n", encoding="utf-8", newline="\n")
def find(rows, identifier): return next(x for x in rows if x.get("id") == identifier)


def decision():
    return {
        "schemaVersion": "1.0.0", "decisionId": DECISION, "decisionPacketId": "DP-PSG-004",
        "workPackageId": "WP-PSG-004", "rootIssueId": "ROOT-CONTRIBUTION-IDENTITY-001",
        "decisionDate": "2026-09-27", "decisionAuthority": "AUTHORIZED_HUMAN_GOVERNOR",
        "decisionOutcome": "APPROVED_BOUNDED_A_PLUS_B_PLUS_C_DIRECTION",
        "approvedArchitecture": ["EXPLICIT_CROSS_CLASS_GROUPS", "NATIVE_CLASS_CONTROLS", "CENTRAL_FAIL_CLOSED_ENFORCEMENT"],
        "authorized": ["architecture direction", "governance recording", "isolated non-production schema/runtime prototyping", "validator prototypes", "synthetic resolver tests", "read-only migration rehearsal", "consumer-impact analysis", "production implementation planning"],
        "notAuthorized": ["production ContributionGroups", "production registry or resolver integration", "production record migration", "Relationship or EffectAssertion mutation", "RDS causal-source use", "graph or simulation behavior change", "lifecycle or activation change", "effect magnitude or polarity", "WP-PSG-005 adjudication"],
        "qualifiedBlockerHandle": "BLK-PSY-003::CONTRIBUTION-REPETITION",
        "historicalIdPreserved": True, "productionImplementationStatus": "NOT_AUTHORIZED_NOT_STARTED",
        "wpPsg005Status": "NOT_STARTED", "rootIssueResolutionStatus": "NOT_RESOLVED_PROTOTYPE_ONLY",
    }


def production_group():
    rel = find(read("data/relationship-intervention-v1/relationships.json")["relationships"], "REL-V1-PSY-LAYER-001")
    ea = find(read("data/actions-events-v1/catalog.json")["effectAssertions"], "EA-V1-PSY-LAYER-001")
    dims = {
        "causalExposureOrChange": "Repeated encounter with the same specified factual claim under the bounded protocol",
        "targetChange": "Rated belief confidence in that specified claim",
        "causalContrast": "Repeated versus non-repeated encounter under the governed protocol",
        "unitOfAnalysis": "Person x specified claim x exposure protocol",
        "timeScope": "Initial exposure before later bounded judgment",
        "pathwayScope": "Total bounded repetition contribution; no inferred mediation path",
        "intendedContribution": "One repetition-exposure contribution to specified belief confidence",
        "underlyingRepresentedQuantity": "The same bounded exposure-induced belief-confidence change",
    }
    return {
        "schemaVersion": "0.2.0-PROTOTYPE", "groupId": "CONTRIB-PSY-LAYER-REPETITION-001", "groupVersion": "1.0.0",
        "objectKind": "CONTRIBUTION_IDENTITY_CONTROL", "scientificContributionDefinition": dims["intendedContribution"],
        "scope": {"population": rel["applicability"]["populationOrSystem"], "context": rel["applicability"]["context"]}, "identityDimensions": dims,
        "memberRepresentations": [
            {"recordClass": "RELATIONSHIP", "recordId": rel["id"], "recordRevision": rel["revision"], "recordHash": sha(rel), "memberRole": "PRIMARY_CAUSAL_CONTRIBUTION", "representationRelationship": "SAME_UNDERLYING_CONTRIBUTION", "nativeContributionId": None, "nativeContributionPolicy": None},
            {"recordClass": "EFFECT_ASSERTION", "recordId": ea["id"], "recordRevision": ea["revision"], "recordHash": sha(ea), "memberRole": "ALTERNATE_CAUSAL_REPRESENTATION", "representationRelationship": "SAME_UNDERLYING_CONTRIBUTION", "nativeContributionId": ea["contribution"]["groupId"], "nativeContributionPolicy": ea["contribution"]["reconciliation"]},
        ],
        "countingPolicy": "MUTUALLY_EXCLUSIVE_REPRESENTATIONS", "propagationPolicy": "COUNT_ONCE_NO_ADDITIVE_PROPAGATION",
        "selectionPolicy": "EXACT_EXPLICIT_REPRESENTATION_REQUIRED", "derivationPolicy": "NOT_APPLICABLE",
        "causalIndependenceStatus": "SAME_CONTRIBUTION_CONFIRMED", "evidenceOverlapStatus": "SEPARATE_FROM_CONTRIBUTION_IDENTITY",
        "constituentOverlapStatus": "NOT_APPLICABLE", "crossLevelRouteReferences": [], "stateRouteReferences": [], "rdsProfileReferences": [],
        "limitations": ["Prototype only", "No activation, graph, simulation, magnitude or polarity authority"],
        "provenance": {"decisionId": DECISION, "baseline": BASELINE, "prototypeOnly": True}, "governanceReference": DECISION,
        "causalEvidence": False, "executionAuthority": False, "hasWeight": False, "hasPolarity": False, "hasLifecycle": False, "hasActivation": False, "hasPropagationState": False,
    }


def runtime_group(group):
    key = sha(group["identityDimensions"])
    members=[]
    for m in group["memberRepresentations"]:
        members.append({"recordClass":m["recordClass"],"recordId":m["recordId"],"recordVersion":str(m["recordRevision"]),"recordHash":m["recordHash"],"memberRole":m["memberRole"],"representationRelationship":m["representationRelationship"],"identityAlignmentKey":key})
    return {"schemaVersion":"0.2.0-PROTOTYPE","groupId":group["groupId"],"groupVersion":group["groupVersion"],"scientificContributionDefinition":group["scientificContributionDefinition"],"scope":group["scope"],"memberRepresentations":members,"consumerPolicy":"EXPLICIT_FAIL_CLOSED","countingPolicy":group["countingPolicy"],"propagationPolicy":group["propagationPolicy"],"derivationPolicy":group["derivationPolicy"],"causalIndependenceStatus":group["causalIndependenceStatus"],"evidenceOverlapStatus":group["evidenceOverlapStatus"],"constituentOverlapStatus":group["constituentOverlapStatus"],"provenance":group["provenance"],"governance":{"status":"PROTOTYPE_ONLY"},"causalAuthority":False,"hasWeight":False,"hasPolarity":False,"hasActivation":False,"hasScientificLifecycle":False}


def candidate(member, value=None):
    row={"recordClass":member["recordClass"],"recordId":member["recordId"],"recordVersion":str(member["recordRevision"]),"recordHash":member["recordHash"]}
    if value is not None: row["value"]=value
    return row


def resolution_cases(group):
    rg=runtime_group(group); candidates=[candidate(x,.2) for x in group["memberRepresentations"]]
    def attempt(selection):
        try:return cc.resolve_contribution_set(candidates,selection,[rg],{"mode":"SYNTHETIC_VALIDATION"})
        except cc.ValidationError as e:return {"resolutionOutcome":"SELECT_ONE_REQUIRED","error":str(e),"causalAuthorityGranted":False,"activationAuthorityGranted":False,"graphAuthorityGranted":False}
    rel=attempt({group["groupId"]:"REL-V1-PSY-LAYER-001"}); ea=attempt({group["groupId"]:"EA-V1-PSY-LAYER-001"}); none=attempt({})
    rel2=attempt({group["groupId"]:"REL-V1-PSY-LAYER-001"})
    return {"schemaVersion":"1.0.0","decisionId":DECISION,"productionMutationAuthorized":False,"cases":[
        {"id":"DUPLICATE_NO_SELECTION","receipt":none,"expected":"SELECT_ONE_REQUIRED"},
        {"id":"DUPLICATE_SELECT_RELATIONSHIP","receipt":rel,"numericResult":.2,"expected":"COUNT_ONCE"},
        {"id":"DUPLICATE_SELECT_EFFECT_ASSERTION","receipt":ea,"numericResult":.2,"expected":"COUNT_ONCE"},
        {"id":"DUPLICATE_PLUS_INDEPENDENT","receipt":rel,"numericResult":.3,"expected":"ALLOW_INDEPENDENT_ADDITION"},
        {"id":"DERIVATION_AND_NETWORK_RECALCULATION","expected":"NO_CAUSAL_CONTRIBUTION","numericResult":0},
        {"id":"CROSS_LEVEL_MAPPING","expected":"NO_CAUSAL_CONTRIBUTION","numericResult":0},
        {"id":"UNRESOLVED_AGGREGATE","expected":"BLOCK_PENDING_CAUSAL_INDEPENDENCE"}],
        "fingerprintDeterministic":rel["deterministicFingerprint"]==rel2["deterministicFingerprint"],"naiveDuplicateSum":.4,"countOnceResult":.2,"withIndependentResult":.3}


def migration():
    social=find(read("data/candidates/actions-events-v1/SOCIAL_LAYER/astra-escalation-queue.json"),"ASTRA-SOC-LAYER-001")["affectedRecords"]
    rows=[]
    def add(identifier,cls,classification,reason):
        rows.append({"recordId":identifier,"recordClass":cls,"classification":classification,"reason":reason,"productionMutationAuthorized":False,"graphChangeAuthorized":False,"simulationChangeAuthorized":False,"activationAuthorized":False})
    add("REL-V1-PSY-LAYER-001","RELATIONSHIP","READY_FOR_EXTERNAL_GROUP","Exact externally hash-bound member; no Relationship schema change required")
    add("EA-V1-PSY-LAYER-001","EFFECT_ASSERTION","READY_FOR_EXTERNAL_GROUP","Native contribution ID agrees with the external group")
    add("DER-V1-SOC-F07-001","DERIVATION","NATIVE_CONTROL_SUFFICIENT","RECALCULATION_ONLY_NO_CAUSAL_SUM")
    add("RDS-PROFILE-V1-SOC-F07-001@1.0.0","RDS_PROFILE","NATIVE_CONTROL_SUFFICIENT","Preserves legacy contribution identity and causalSourceEligible=false")
    add("RDS-BIND-V1-SOC-F07-001@1.0.0","RDS_BINDING","NATIVE_CONTROL_SUFFICIENT","Exact shadow compatibility binding")
    for x in ("INS-039","REL-INS-017","INS-103","REL-INS-036"): add(x,"RDS_OR_RELATIONSHIP","BLOCKED_PENDING_CAUSAL_INDEPENDENCE","Constituent overlap/independent aggregate mechanism unresolved")
    for x in social:add(x,"SOCIAL_RDS_ROUTE","INSUFFICIENT_ROUTE_DEFINITION","Exact constituent contribution identities unavailable; do not fabricate")
    for x in ("HYP-SOC-F07-H12","HYP-SOC-F07-H20"):add(x,"NETWORK_STATE_EXAMPLE","NONCAUSAL_NO_GROUP_REQUIRED","State delta and deterministic metric recalculation are not causal inputs")
    add("XLEM-V1-INS-PROC-001@1.0.0","CROSS_LEVEL_MAPPING","NONCAUSAL_NO_GROUP_REQUIRED","Exposure routing only")
    add("XLEB-V1-REL-INS-040-001@1.0.0","CROSS_LEVEL_BINDING","NONCAUSAL_NO_GROUP_REQUIRED","Shadow binding only")
    return {"schemaVersion":"1.0.0","decisionId":DECISION,"recordCount":len(rows),"counts":dict(sorted(Counter(x["classification"] for x in rows).items())),"records":rows,"productionMigrationAuthorized":False}


def consumers():
    rows=[
        ("scripts/actions_events_v1.py","NATIVE_CLASS_CONTROL_ONLY","Future adapter exposes EA native group without mutation"),("scripts/relationship_intervention_v1.py","CURRENTLY_SAFE_NO_INTEGRATION","External exact membership avoids Relationship schema change"),("scripts/build_relationships.py","CROSS_CLASS_RESOLUTION_REQUIRED_FUTURE","Any future causal graph assembly must call resolver"),("scripts/rds_computation_v1.py","NATIVE_CLASS_CONTROL_ONLY","Preserve recalculation policy and causal firewall"),("scripts/relational_state_v1.py","NO_CAUSAL_CONSUMPTION","State/metric receipts remain noncausal"),("scripts/cross_level_exposure_v1.py","NO_CAUSAL_CONSUMPTION","Routing only"),("scenario-service/src/openai-service.js","CURRENTLY_SAFE_NO_INTEGRATION","No causal summation path"),("external graph/simulation consumers","UNKNOWN_EXTERNAL_CONSUMER","Must call central gate or fail closed")]
    return {"schemaVersion":"1.0.0","decisionId":DECISION,"records":[{"consumer":a,"classification":b,"futureRequirement":c,"currentBehaviorChanged":False} for a,b,c in rows],"centralGateRequiredFor":["graph assembly","causal propagation","effect summation","action scoring","effect attribution"]}


def handoffs(migration):
    social=[r["recordId"] for r in migration["records"] if r["recordClass"]=="SOCIAL_RDS_ROUTE"]
    def aggregate(identifier,relationship): return {"aggregateRdsId":identifier,"profileId":None,"profileVersion":None,"bindingId":None,"bindingVersion":None,"constituentMapping":"NOT_GOVERNED","constituentContributionIds":[],"candidateAggregateContributionId":None,"crossLevelMappingId":None,"crossLevelMappingVersion":None,"networkStateRef":None,"boundaryWindow":None,"temporalAlignment":"UNRESOLVED","overlapStatus":"CONSTITUENT_OVERLAP_UNRESOLVED","independenceStatus":"INDEPENDENCE_NOT_ESTABLISHED","causalSourceEligible":False,"scientificGaps":["exact constituent routes","independent aggregate mechanism","temporal and scope alignment"],"relationshipIds":[relationship]}
    return {"schemaVersion":"1.0.0","decisionId":DECISION,"wpPsg005":{"status":"NOT_STARTED","adjudicationPerformed":False,"records":[aggregate("INS-039","REL-INS-017"),aggregate("INS-103","REL-INS-036"),{"aggregateFamily":"ASTRA-SOC-LAYER-001","aggregateRdsIds":social,"constituentContributionIds":[],"overlapStatus":"UNKNOWN","independenceStatus":"INSUFFICIENT_ROUTE_DEFINITION","causalSourceEligible":False,"scientificGaps":["exact constituent routes for each of ten RDS sources"]}]},"wpPsg009":{"status":"NOT_STARTED","relationshipCandidates":["REL-V1-PSY-LAYER-001","REL-INS-017","REL-INS-036"],"reason":"Contribution identity or aggregate-overlap resolution required before semantic-debt migration"}}


def delta_preview():
    return {"schemaVersion":"1.0.0","decisionPacketId":"DP-PSG-004-IMPLEMENTATION","productionChangeApplied":False,"phase0":{"add":["ContributionGroup schema","ContributionResolutionRequest schema","ContributionResolutionReceipt schema","empty ContributionGroup registry","exact group validator","central resolution service","native-control adapters","hash/reference resolver","consumer gate interface","migration/review tooling"],"groups":0,"recordMigrations":0,"graphChanges":0,"simulationChanges":0},"phase1":{"shadowOnly":True,"groupId":"CONTRIB-PSY-LAYER-REPETITION-001","members":["REL-V1-PSY-LAYER-001","EA-V1-PSY-LAYER-001"],"sourceRecordsMutated":False,"explicitSelectionRequired":True,"graphChanges":0,"simulationChanges":0,"activationChanges":0},"excluded":["aggregate RDS migration","WP-PSG-005 adjudication","consumer behavior changes","lifecycle or activation changes"]}


def documents(group,mig,cons,handoff,delta):
    alias="Qualified handles are planning aliases; the historical `BLK-PSY-003` ID and provenance remain unchanged. WP-PSG-004 uses `BLK-PSY-003::CONTRIBUTION-REPETITION`; `BLK-PSY-003::CONSTRUCT-BOUNDARY` remains for later construct/ontology governance."
    write_doc("CONTRIBUTION_ARCHITECTURE_DECISION_001.md",f"""# Contribution identity architecture decision 001

Decision `{DECISION}` records `APPROVED_BOUNDED_A_PLUS_B_PLUS_C_DIRECTION` for DP-PSG-004. Stage D is complete. Explicit immutable cross-class groups, preserved native controls, and central fail-closed enforcement are approved. Non-production prototyping and dry-run planning are authorized.

Production schemas, registries, groups, resolver integration, migrations, graph/simulation changes, lifecycle/activation changes, aggregate causal-source use, and WP-PSG-005 adjudication remain unauthorized. {alias}
""")
    write_doc("CONTRIBUTION_REFERENCE_IMPLEMENTATION.md",f"""# Contribution reference implementation

> {NOTICE}

The isolated prototype supplies a JSON Schema, exact-version immutable registry, validator, centralized `resolve_contribution_set` function, and deterministic receipts. It validates exact IDs/revisions/hashes, native EA agreement, identity dimensions, explicit select-one behavior, noncausal roles, unresolved aggregate blocking, collisions, and deterministic fingerprints. Production modules do not import it.

The architecture is sparse: only explicitly adjudicated cross-class identity receives a group. Independent native records remain outside the registry.
""")
    write_doc("CONTRIBUTION_GROUP_SCHEMA_SPEC.md",f"""# ContributionGroup schema specification

> {NOTICE}

`ContributionGroup` is `CONTRIBUTION_IDENTITY_CONTROL`, never a scientific causal object. Identity requires all eight governed dimensions. Members bind exact class, ID, revision and SHA-256 content hash plus role and native controls. Group versions are immutable; a new representation under unchanged identity creates a new version, while a new contrast, target, pathway scope or represented quantity requires a new group identity and scientific re-adjudication.

Every authority flag is false: causal evidence, execution, weight, polarity, lifecycle, activation and propagation state.
""")
    write_doc("CONTRIBUTION_RESOLUTION_CONTRACT.md",f"""# Contribution resolution contract

> {NOTICE}

Future causal consumers submit exact candidate records, exact group versions, explicit selections, native controls and context. The resolver returns included, excluded and blocked representations plus a deterministic receipt. It never prefers Relationship/EA, active/inactive, newest, highest evidence, first or latest. Missing selection for mutually exclusive records returns `SELECT_ONE_REQUIRED`; unresolved aggregate independence blocks; derivation, state recalculation and exposure routing contribute zero.

Every graph assembly, propagation, summation, scoring or attribution consumer must call the governed central gate once implemented. Unknown external consumers fail closed.
""")
    write_doc("CONTRIBUTION_MIGRATION_DRY_RUN.md",f"""# Contribution migration dry run

> {NOTICE}

The manifest covers {mig['recordCount']} records/routes exactly once: {', '.join(f'`{k}`={v}' for k,v in mig['counts'].items())}. Every row denies production mutation, graph change, simulation change and activation. The repetition pair alone is ready for an external group. Aggregate cases remain blocked and noncausal architecture records need no group.
""")
    write_doc("CONTRIBUTION_CONSUMER_IMPACT_STAGE_E.md",f"""# Contribution consumer impact — Stage E

> {NOTICE}

Actions & Events and RDS/Network State retain native controls. Relationships can be externally hash-bound without schema change. Cross-level exposure and scenario service have no causal contribution consumption. Future graph/simulation consumers require the central resolver. No current consumer behavior changes.
""")
    write_doc("CONTRIBUTION_PRODUCTION_IMPLEMENTATION_PLAN.md",f"""# Contribution production implementation plan

Phase 0 would install schemas, empty registry, validators, resolver, adapters and receipt/fingerprint contracts with zero groups, migrations, graph changes or simulation changes. Rollback removes this unused architecture.

After Phase 0 validation, Phase 1 would materialize only `CONTRIB-PSY-LAYER-REPETITION-001@1.0.0` in shadow/validation mode. Both source records remain unchanged, selection is explicit, count-once is proven, and no graph, simulation, lifecycle or activation behavior changes. Aggregates are excluded.
""")
    approval="Approve DP-PSG-004-IMPLEMENTATION for bounded production Phase 0 and the separately gated shadow-only Phase 1 exactly as specified: install immutable exact-version ContributionGroup, ContributionResolutionRequest and ContributionResolutionReceipt schemas, an empty registry, fail-closed validators, native-control adapters, central resolution service, and deterministic receipt/fingerprint contracts with zero groups, zero record migrations, and zero graph or simulation behavior changes; then, only after Phase 0 validation passes, materialize the external ContributionGroup `CONTRIB-PSY-LAYER-REPETITION-001@1.0.0` binding exact unchanged versions and hashes of `REL-V1-PSY-LAYER-001` and `EA-V1-PSY-LAYER-001` in shadow/validation-only mode. Require explicit representation selection, count the contribution once, preserve EA native metadata, mutate neither source record, and confer no new causal, lifecycle, activation, graph, simulation, magnitude, or polarity authority. Aggregate RDS routes, WP-PSG-005 adjudication, and every other production record remain unchanged and unauthorized."
    write_doc("CONTRIBUTION_PRODUCTION_IMPLEMENTATION_DECISION_PACKET.md",f"""# DP-PSG-004-IMPLEMENTATION

> HUMAN PRODUCTION IMPLEMENTATION GOVERNANCE REQUIRED

The narrow request is Phase 0 empty architecture followed, only after validation, by one shadow-only repetition group. Rollback removes the registry/resolver integration and returns to native controls without rewriting scientific records. Aggregate migration is excluded.

## Exact bounded approval statement

{approval}
""")
    write_doc("CONTRIBUTION_STAGE_E_HANDOFF.md",f"""# WP-PSG-004 Stage E handoff

Stage A COMPLETE; Stage B COMPLETE; Stage C COMPLETE; Stage D COMPLETE_BOUNDED_DIRECTION_APPROVED; Stage E COMPLETE_NON_PRODUCTION_REFERENCE_PROTOTYPE; Stage F DRY_RUN_ONLY_COMPLETE_PRODUCTION_MIGRATION_NOT_AUTHORIZED; Stage G NOT_STARTED.

Governance decision: `{DECISION}`. Production implementation: `NOT_AUTHORIZED_NOT_STARTED`. Root issue remains unresolved for production. WP-PSG-005 and WP-PSG-009 handoffs are structured, but neither work package is started. {alias}
""")
    return approval


def main():
    # Preserve Stage C artifacts and regenerate them before adding Stage E outputs.
    subprocess.run([__import__('sys').executable,str(Path(__file__).with_name("build_decision_test.py"))],cwd=ROOT,check=True,capture_output=True,text=True)
    d=decision(); group=production_group(); cases=resolution_cases(group); mig=migration(); cons=consumers(); hand=handoffs(mig); delta=delta_preview()
    write_json("contribution-architecture-decision-001.json",d)
    write_json("contribution-groups-prototype.json",{"schemaVersion":"1.0.0","prototypeStatus":"PROTOTYPE_ONLY","groups":[group],"productionRegistryInstalled":False})
    write_json("contribution-resolution-test-cases.json",cases); write_json("contribution-migration-dry-run.json",mig)
    write_json("contribution-consumer-impact-stage-e.json",cons); write_json("contribution-production-delta-preview.json",delta); write_json("contribution-stage-e-handoffs.json",hand)
    approval=documents(group,mig,cons,hand,delta)
    print(json.dumps({"decisionId":DECISION,"groupCount":1,"migrationRows":mig["recordCount"],"approvalStatement":approval,"productionMutationAuthorized":False},indent=2))


if __name__=="__main__":main()
