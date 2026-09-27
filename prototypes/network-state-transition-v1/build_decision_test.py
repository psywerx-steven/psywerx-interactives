"""Build the read-only WP-PSG-003 decision test from production Network State V1.

All executed states are fictional SYN-* fixtures.  The script writes only planning
artifacts and never changes a production state, scientific catalog, or validator.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae  # noqa: E402
import materialize_soc_f07_completion as completion  # noqa: E402
import relational_state_fixtures as fx  # noqa: E402
import relational_state_v1 as ns  # noqa: E402

BASELINE = "18be50222d75fea3f27ecfd27aed3eee05409ecd"
NOTICE = "READ-ONLY ARCHITECTURE DECISION TEST — NO PRODUCTION SCIENCE, SCHEMA, LIFECYCLE OR ACTIVATION CHANGE"
DOCS = ROOT / "docs/governance/post-scale-up/network-state"
DATA = ROOT / "data/governance/post-scale-up/network-state"

PROTECTED = [
    "data/drivers.json", "data/entities.json", "data/relationships.json", "data/sources.json",
    "data/actions-events-v1/catalog.json", "data/relational-state-v1/catalog.json",
    "data/rds-computation-v1/profiles.json", "data/rds-computation-v1/bindings.json",
    "data/cross-level-exposure-v1/mappings.json", "data/cross-level-exposure-v1/bindings.json",
    "schemas/relational-state/v1/*.schema.json", "scripts/relational_state_v1.py",
    "scripts/actions_events_v1.py", "scripts/relationship_intervention_v1.py",
    "scripts/rds_computation_v1.py", "scripts/cross_level_exposure_v1.py",
    "scripts/build_relationships.py", "scenario-service/src/openai-service.js",
]


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_hashes():
    values = {}
    for spec in PROTECTED:
        for path in sorted(ROOT.glob(spec)):
            values[path.relative_to(ROOT).as_posix()] = sha(path)
    return values


def rejected(callable_):
    try:
        callable_()
    except ns.ValidationError as error:
        return str(error)
    raise AssertionError("Expected Network State validation rejection")


def calc(state, variant, binding=None, authorizations=()):
    return ns.calculate(fx.request(state, variant, binding), state, binding, authorizations)


def apply(state, operations, identifier):
    delta = fx.delta(state, operations, identifier)
    after, receipt = ns.apply_delta(state, delta)
    assert receipt["causalContribution"] is False
    assert receipt["empiricalEvidenceProduced"] is False
    assert receipt["ontologyRelationshipsEdited"] == 0
    return delta, after, receipt


def synthetic_results():
    s0 = fx.state()
    binding = completion.binding()
    auth = [completion.authorization([binding])]

    before_degree = calc(s0, "DEGREE_RAW_UNDIRECTED")
    before_frag = calc(s0, "FRAGMENTATION_UNREACHABLE_PAIRS")
    before_cent = calc(s0, "FREEMAN_DEGREE_CENTRALIZATION", binding, auth)

    rewiring_ops = [
        {"operation": "REMOVE_TIE", "tieId": "SYN-TIE-AB"},
        {"operation": "ADD_TIE", "tie": fx.tie("AD")},
    ]
    rewiring_delta, rewired, rewiring_receipt = apply(s0, rewiring_ops, "SYN-DELTA-WP003-REWIRE")
    after_degree = calc(rewired, "DEGREE_RAW_UNDIRECTED")

    node_delta, node_state, node_receipt = apply(
        s0,
        [{"operation": "DEACTIVATE_NODE", "nodeId": "SYN-NODE-C", "incidentPolicy": "REMOVE_AND_RECORD"}],
        "SYN-DELTA-WP003-NODE",
    )
    after_frag = calc(node_state, "FRAGMENTATION_UNREACHABLE_PAIRS")

    boundary = copy.deepcopy(s0["boundary"])
    boundary["revision"] += 1
    boundary["includedNodeIds"].append("SYN-NODE-E")
    boundary_delta, boundary_state, boundary_receipt = apply(
        s0, [{"operation": "CHANGE_BOUNDARY", "boundary": boundary}], "SYN-DELTA-WP003-BOUNDARY"
    )
    boundary_density = calc(boundary_state, "DENSITY_SIMPLE_UNDIRECTED")

    membership_delta, membership_state, membership_receipt = apply(
        s0,
        [{"operation": "CHANGE_MEMBERSHIP", "nodeId": "SYN-NODE-A", "groupIds": ["SYN-GROUP-B"]}],
        "SYN-DELTA-WP003-MEMBERSHIP",
    )
    membership_degree = calc(membership_state, "DEGREE_RAW_UNDIRECTED")

    opportunity_delta, opportunity_state, opportunity_receipt = apply(
        s0,
        [{"operation": "CHANGE_CONTACT_OPPORTUNITY", "opportunity": fx.opportunity("SYN-OPP-SEAT", "ASSIGNED_SEATING")}],
        "SYN-DELTA-WP003-OPPORTUNITY",
    )
    access_delta, access_state, access_receipt = apply(
        s0,
        [{"operation": "CHANGE_ACCESS", "opportunityId": "SYN-OPP-ACCESS", "enabled": False}],
        "SYN-DELTA-WP003-ACCESS",
    )

    weight_delta, weight_state, weight_receipt = apply(
        s0,
        [{"operation": "UPDATE_TIE_WEIGHT", "tieId": "SYN-TIE-AB", "weight": 2,
          "weightMeaning": "FICTIONAL_CONTACT_INTENSITY", "weightUnit": "fictional-unit"}],
        "SYN-DELTA-WP003-WEIGHT",
    )
    weight_calc = calc(weight_state, "DEGREE_RAW_UNDIRECTED")

    observation = fx.observation("SYN-OBS-WP003", "SYN-TIE-AB")
    observed_state = ns.construct_from_observation(
        fx.empty_state("SYN-STATE-WP003-OBS"), observation,
        "Incomplete fictional selection retained as a modeled assumption, not observed truth.",
        [node["id"] for node in observation["nodes"]], [tie["id"] for tie in observation["ties"]],
    )

    branch_a_delta, branch_a, branch_a_receipt = apply(
        s0, [{"operation": "REMOVE_TIE", "tieId": "SYN-TIE-AB"}], "SYN-DELTA-WP003-BRANCH-A"
    )
    branch_b_delta, branch_b, branch_b_receipt = apply(
        s0, [{"operation": "REMOVE_TIE", "tieId": "SYN-TIE-AC"}], "SYN-DELTA-WP003-BRANCH-B"
    )
    replayed = ns.replay(s0, rewiring_delta, rewiring_receipt)

    events = read(ROOT / "data/actions-events-v1/catalog.json")
    ht = events["happeningTypes"][0]
    ht_ref = ns.ref(ht)
    referenced_delta = copy.deepcopy(access_delta)
    referenced_delta["id"] = "SYN-DELTA-WP003-OPREF"
    referenced_delta["happeningTypeRef"] = ht_ref
    link = {
        "schemaVersion": "1.0.0", "objectKind": "SCENARIO_OPERATION_REFERENCE",
        "deltaRef": {"id": referenced_delta["id"], "revision": 1, "contentHash": ns.digest(referenced_delta)},
        "occurrenceRef": None, "happeningTypeRef": ht_ref,
        "relation": "REFERENCES_STIPULATED_OPERATION_NOT_EFFECT",
        "automaticExecution": False, "empiricalConsequenceClaim": False,
    }
    assert ns.validate_operation_reference(link, referenced_delta, {}, {ht["id"]: ht})

    stale = copy.deepcopy(branch_a_delta)
    stale["id"] = "SYN-DELTA-WP003-STALE"
    stale_error = rejected(lambda: ns.apply_delta(branch_a, stale))
    cross = copy.deepcopy(branch_a_delta)
    cross["id"] = "SYN-DELTA-WP003-CROSS"
    cross["scenarioId"] = "SYN-SCENARIO-OTHER"
    cross_error = rejected(lambda: ns.apply_delta(s0, cross))
    recycled = fx.tie("AB")
    recycle_delta = fx.delta(branch_a, [{"operation": "ADD_TIE", "tie": recycled}], "SYN-DELTA-WP003-RECYCLE")
    recycle_error = rejected(lambda: ns.apply_delta(branch_a, recycle_delta))

    return {
        "schemaVersion": "1.0.0", "workPackageId": "WP-PSG-003", "recordClass": ns.SYNTHETIC,
        "notice": NOTICE, "productionStateWritten": False,
        "operationsVerified": ["ADD_NODE", "DEACTIVATE_NODE", "ADD_TIE", "REMOVE_TIE", "UPDATE_TIE_WEIGHT",
                               "CHANGE_MEMBERSHIP", "CHANGE_BOUNDARY", "CHANGE_CONTACT_OPPORTUNITY", "CHANGE_ACCESS"],
        "rewiring": {
            "deltaId": rewiring_delta["id"], "operationOrder": rewiring_receipt["operationOrder"],
            "beforeState": ns.ref(s0), "afterState": ns.ref(rewired),
            "beforeDegree": before_degree["value"], "afterDegree": after_degree["value"],
            "stateChanged": s0["contentHash"] != rewired["contentHash"], "receipt": rewiring_receipt,
            "h12Advisory": "ARCHITECTURALLY_REPRESENTABLE_RECALCULATION_NOT_EMPIRICAL_CAUSAL_EFFECT",
        },
        "nodeDeactivation": {
            "deltaId": node_delta["id"], "beforeFragmentation": before_frag["value"],
            "afterFragmentation": after_frag["value"], "removedTieIds": node_receipt["removedTieIds"],
            "removedOpportunityIds": node_receipt["removedOpportunityIds"], "afterState": ns.ref(node_state),
            "h20Advisory": "ARCHITECTURALLY_REPRESENTABLE_RECALCULATION_NOT_EMPIRICAL_CAUSAL_EFFECT",
        },
        "boundary": {"deltaId": boundary_delta["id"], "changeClass": boundary_receipt["changeClass"],
                     "tieCorpusUnchanged": boundary_state["ties"] == s0["ties"], "density": boundary_density["value"]},
        "membership": {"deltaId": membership_delta["id"], "tiesUnchanged": membership_state["ties"] == s0["ties"],
                       "degreeUnchanged": membership_degree["value"] == before_degree["value"], "receipt": membership_receipt},
        "opportunityAndAccess": {"opportunityDeltaId": opportunity_delta["id"], "accessDeltaId": access_delta["id"],
                                  "tiesUnchanged": opportunity_state["ties"] == s0["ties"] == access_state["ties"],
                                  "receipts": [opportunity_receipt, access_receipt]},
        "weight": {"deltaId": weight_delta["id"], "receipt": weight_receipt,
                   "binaryMetricStatus": weight_calc["status"], "binaryMetricReason": weight_calc["reason"]},
        "observation": {"observationRef": ns.ref(observation), "constructedState": ns.ref(observed_state),
                        "construction": observed_state["construction"], "assumptions": observed_state["assumptions"]},
        "replay": {"exactState": replayed == rewired, "exactReceipt": True},
        "branching": {"parent": ns.ref(s0), "branchA": ns.ref(branch_a), "branchB": ns.ref(branch_b),
                      "distinct": branch_a["contentHash"] != branch_b["contentHash"],
                      "receipts": [branch_a_receipt, branch_b_receipt]},
        "operationReference": {"happeningTypeId": ht["id"], "relation": link["relation"],
                               "automaticExecution": False, "empiricalConsequenceClaim": False, "valid": True},
        "rejections": {"staleState": stale_error, "crossScenario": cross_error, "retiredTieReuse": recycle_error},
        "centralizationPositiveControl": {"bindingId": binding["id"], "before": before_cent,
                                          "governance": binding["governance"],
                                          "causalSourceAuthorized": False, "effectAssertionCreated": False},
        "firewalls": {"causalContribution": False, "empiricalEvidenceProduced": False,
                      "ontologyRelationshipsEdited": 0, "effectAssertionsCreated": 0,
                      "directRdsEffectAssertionCreated": False, "causalSourceEligible": False},
    }


def relationship_handoffs():
    relationships = {r["id"]: r for r in read(ROOT / "data/relationships.json")["relationships"]}
    stage_e = read(ROOT / "data/governance/post-scale-up/cross-level/cross-level-migration-dry-run.json")
    reviews = {r["relationshipId"]: r for r in stage_e["records"]}
    specifications = {
        "REL-SOC-017": {
            "dependency": "Exact network state and exact Active Personal Network Size computation profile/binding; provider eligibility/opportunity remains distinct from received or perceived support.",
            "networkStateRequirements": ["stateId/revision/contentHash", "boundaryId/revision", "window", "active node set", "tie definition", "exact SOC-024 profile/binding"],
            "metricRole": "Network-derived RDS is a potential-provider-pool summary, not actual support exposure.",
            "downstream": ["WP-PSG-002", "WP-PSG-005"], "primaryClassification": "BLOCKED_BY_WP_PSG_005",
        },
        "REL-SOC-035": {
            "dependency": "Exact network state and clustering computation plus actor-specific reinforcing-neighbor behavior/exposure; clustering alone does not establish reinforcement.",
            "networkStateRequirements": ["stateId/revision/contentHash", "boundaryId/revision", "window", "ego node", "neighbor tie definition", "exact SOC-053 profile/binding"],
            "metricRole": "Local clustering describes neighbor connectivity; actual reinforcing exposures are separate.",
            "downstream": ["WP-PSG-002", "WP-PSG-005"], "primaryClassification": "BLOCKED_BY_WP_PSG_005",
        },
        "REL-TEC-050": {
            "dependency": "Filtering restrictiveness may alter recommendations or opportunity before any observed/stipulated adjacency change; exact segregation profile and state transition/observation are absent.",
            "networkStateRequirements": ["stateId/revision/contentHash", "boundaryId/revision", "window", "group labels", "tie/opportunity definition", "exact SOC-057 profile/binding", "transition or observation reference"],
            "metricRole": "A technological affordance does not itself establish a changed network or segregation metric.",
            "downstream": ["WP-PSG-001", "WP-PSG-002", "WP-PSG-005"], "primaryClassification": "BLOCKED_BY_SCIENCE_NOT_ARCHITECTURE",
        },
    }
    rows = []
    for identifier, extra in specifications.items():
        relationship, review = relationships[identifier], reviews[identifier]
        rows.append({
            "relationshipId": identifier, "sourceEntityId": relationship["subjectEntityId"],
            "targetEntityId": relationship["objectEntityId"], "sourceLevel": relationship["subjectLevel"],
            "targetLevel": relationship["objectLevel"], "relationFamily": relationship["relationFamily"],
            "currentGovernanceStatus": relationship["governanceStatus"],
            "currentReviewDisposition": review["currentReviewDisposition"],
            "productionRelationshipChanged": False, **extra,
        })
    return rows


def migration(handoffs):
    rows = [
        {"id": "HYP-SOC-F07-H12", "classification": "ALREADY_REPRESENTABLE_BY_CURRENT_NETWORK_STATE", "reason": "Explicit REMOVE_TIE plus ADD_TIE rewiring yields a new immutable state and deterministic degree recalculation."},
        {"id": "HYP-SOC-F07-H20", "classification": "ALREADY_REPRESENTABLE_BY_CURRENT_NETWORK_STATE", "reason": "DEACTIVATE_NODE retires incident ties and yields a new immutable state from which fragmentation is recalculated."},
        {"id": "ASTRA-SOC-LAYER-003", "classification": "REPRESENTABLE_WITH_DOCUMENTED_CONTRACT_ONLY", "reason": "ScenarioStateDelta already supplies transition identity, ordered operations, before-state reference, after-state receipt, lineage, provenance and replay."},
    ]
    rows.extend({"id": row["relationshipId"], "classification": row["primaryClassification"], "reason": row["dependency"]} for row in handoffs)
    counts = Counter(row["classification"] for row in rows)
    all_classes = ["ALREADY_REPRESENTABLE_BY_CURRENT_NETWORK_STATE", "REPRESENTABLE_WITH_DOCUMENTED_CONTRACT_ONLY",
                   "REPRESENTABLE_WITH_MINOR_ADDITIVE_METADATA", "NEEDS_NEW_TYPED_OPERATION", "NEEDS_NEW_ARCHITECTURE_OBJECT",
                   "BLOCKED_BY_SCIENCE_NOT_ARCHITECTURE", "BLOCKED_BY_WP_PSG_004", "BLOCKED_BY_WP_PSG_005"]
    return {"schemaVersion": "1.0.0", "workPackageId": "WP-PSG-003", "recordCount": len(rows),
            "counts": {key: counts[key] for key in all_classes}, "records": rows,
            "productionMutationAuthorized": False}


def consumers():
    return {
        "schemaVersion": "1.0.0", "workPackageId": "WP-PSG-003",
        "consumers": [
            {"path": "scripts/relational_state_v1.py", "impact": "NO_CHANGE", "finding": "Current typed state, receipt, replay, observation and metric runtime is sufficient for tested cases."},
            {"path": "scripts/rds_computation_v1.py", "impact": "CALCULATION_PROFILE_AWARE_FUTURE", "finding": "Future unified execution may bind exact state references to governed RDS profiles; legacy DER-V1 compatibility remains."},
            {"path": "scripts/cross_level_exposure_v1.py", "impact": "STATE_REFERENCE_AWARE_FUTURE", "finding": "Network-dependent mappings must fail closed until exact state, boundary, window and profile references exist."},
            {"path": "scripts/relationship_intervention_v1.py", "impact": "NO_CHANGE", "finding": "State deltas do not edit or approve ontology Relationships."},
            {"path": "scripts/actions_events_v1.py", "impact": "NO_CHANGE", "finding": "ScenarioOperationReference can link identity without asserting an empirical consequence; direct RDS effects remain prohibited."},
            {"path": "scenario-service/src/openai-service.js", "impact": "NO_CURRENT_NETWORK_STATE_CONSUMER_FOUND", "finding": "Repository search found no RelationalState or ScenarioStateDelta ingestion path."},
            {"path": "repository FCM/model construction", "impact": "NO_INTERNAL_ACTIVE_NETWORK_STATE_CONSUMER_FOUND", "finding": "No production graph builder consumes state deltas or calculation receipts as causal edges."},
        ], "productionConsumerBehaviorChanged": False,
    }


def option_results():
    return {
        "schemaVersion": "1.0.0", "decisionPacketId": "DP-PSG-003",
        "recommendation": "BOUNDED_A_PLUS_C_USE_EXISTING_TYPED_SCENARIO_STATE_DELTA_AND_BLOCK_UNSUPPORTED_TRANSITIONS",
        "options": {
            "A": {"result": "PASS_CURRENT_CAPABILITY", "finding": "Existing typed ScenarioStateDelta already represents every tested node, tie, weight, membership, boundary, opportunity and access operation with immutable state lineage and replay. No schema extension is presently required."},
            "B": {"result": "REJECT_AS_REDUNDANT_FOR_CURRENT_SCOPE", "finding": "A NetworkStateTransition repeating delta identity, before/after state, ordered operations, provenance, time and receipt adds no distinct scientific meaning and risks a duplicate quasi-causal class."},
            "C": {"result": "PASS_AS_FAIL_CLOSED_POLICY", "finding": "Unsupported or empirically estimated transitions should remain blocked, but C alone would obscure that supported modeled transitions already work."},
            "A_PLUS_C": {"result": "RECOMMENDED_ADVISORY", "finding": "Use current typed ScenarioStateDelta for supported stipulated changes, ScenarioOperationReference for non-effect identity linkage, RelationalState as scenario truth, and exact RDS calculation for recalculation; leave everything else unsupported."},
        },
        "networkStateTransitionUniqueConceptFound": False,
        "missingTypedOperationsForCurrentCases": [],
        "unsupportedByDesign": ["EMPIRICALLY_ESTIMATED_TRANSITION", "implicit continuous-time dynamics", "generic untyped transition", "metric-to-exposure inference"],
        "humanDecisionTaken": False,
    }


def render_docs(results, handoffs, migration_data, consumer_data, options):
    counts = migration_data["counts"]
    before_degree_text = json.dumps(results["rewiring"]["beforeDegree"], sort_keys=True)
    after_degree_text = json.dumps(results["rewiring"]["afterDegree"], sort_keys=True)
    write_text(DOCS / "NETWORK_STATE_DECISION_TEST.md", f"""# Network State transition decision test

**{NOTICE}**

`WP-PSG-003` / `DP-PSG-003` tested production Network State V1 at baseline `{BASELINE}` with fictional `SYN-*` states. The test changed no production state or scientific record.

## Finding

The existing `ScenarioStateDelta` is already the bounded state-transition record for supported modeled operations. It contains an immutable identity, exact before-state reference, ordered typed operations, effective time, provenance, scenario alignment, and deterministic receipt pointing to the resulting `RelationalState`. `ScenarioOperationReference` optionally links a scientific operation identity while stating `REFERENCES_STIPULATED_OPERATION_NOT_EFFECT`.

The advisory recommendation is **A+C**: use the existing typed delta for supported stipulated changes and keep unsupported/empirically estimated transitions blocked. A second `NetworkStateTransition` class would duplicate current semantics.

## H12 — rewiring

The synthetic delta `{results['rewiring']['deltaId']}` removes one tie and adds another. The state hash changes, parent lineage is retained, and node degree changes from `{before_degree_text}` to `{after_degree_text}`. The receipt preserves `causalContribution=false`, `empiricalEvidenceProduced=false`, and `ontologyRelationshipsEdited=0`. H12 is architecturally representable as state change plus recalculation; an empirical causal Driver→RDS claim is unnecessary and unsupported.

## H20 — node deactivation

`DEACTIVATE_NODE` removes the inactive node from the analytic boundary and retires its incident ties. Fragmentation changes from `{results['nodeDeactivation']['beforeFragmentation']}` to `{results['nodeDeactivation']['afterFragmentation']}`. This is deterministic recalculation from a stipulated state, not an EffectAssertion.

## Controls

- `CHANGE_BOUNDARY` is `ANALYTIC_BOUNDARY_ONLY`; it changes selection and metrics without claiming physical tie change.
- `CHANGE_MEMBERSHIP` changes group membership without creating/removing ties.
- contact opportunity and access changes do not create realized ties or exposure.
- an intensity-weight update makes binary-only metric calculation fail closed.
- observation-derived construction preserves observation reference, selection, missingness, assumptions, boundary and window.
- replay is exact and two branches retain the same parent without becoming observed futures.
- stale state, cross-scenario application and retired tie-ID reuse are rejected.

## Scientific firewalls

No Relationship, EffectAssertion, causal contribution, empirical evidence, ontology edit, RDS causal authorization, graph edge, lifecycle state or activation follows from a delta or recalculation.
""")

    write_text(DOCS / "NETWORK_STATE_OPTION_COMPARISON.md", f"""# Network State option comparison

**{NOTICE}**

| Criterion | A — current typed delta | B — new transition object | C — leave unsupported blocked | A+C |
|---|---|---|---|---|
| Scientific fidelity | Strong for stipulated operations | Adds no current scientific distinction | Safe but incomplete description | Strongest bounded separation |
| Determinism/replay | Existing hashes, receipts and replay | Would duplicate them | Preserved | Preserved |
| A&E separation | Explicit optional non-effect reference | Risks quasi-causal interpretation | Safe | Explicit and safe |
| RDS separation | Existing calculation receipts are noncausal | Duplicate linkage surface | Safe | Exact recalculation only |
| Cross-level compatibility | Supplies exact state reference | No added exposure semantics | Leaves dependencies blocked | Exact state input; exposure remains WP-PSG-002 |
| Migration | None | New schema/registry/consumers | None | None for current cases |
| Rollback | Historical immutable branches | New object migration required | Current behavior | Current behavior |

Recommendation: `{options['recommendation']}`. Option B is rejected for current scope because it duplicates delta + receipt + parent state + operation reference. C remains the fail-closed rule for unsupported transitions.
""")

    write_text(DOCS / "NETWORK_STATE_REPRESENTATION_CONTRACT.md", f"""# Network State representation contract

**{NOTICE}**

1. **HappeningType / Occurrence** identifies an asserted or observed operation; it does not prove a state consequence.
2. **ScenarioOperationReference** may link that identity to a delta as a modeled consequence assumption, with no automatic execution or empirical consequence claim.
3. **ScenarioStateDelta** stipulates an ordered, typed modification to one exact scenario state.
4. **RelationalState revision** is the resulting immutable modeled configuration with parent lineage.
5. **RDS computation profile / derivation** recalculates a metric from an exact state/boundary/window.
6. **CrossLevelExposureMapping** may later describe how exact network context reaches a lower-level target.
7. **Relationship / EffectAssertion** remains the governed empirical causal claim.

An exact state reference requires state ID, revision, content hash, scenario ID, boundary ID/revision, window, node set, tie type/layer, tie set, missingness/assumptions and provenance. A future cross-level binding must reference these explicitly; a metric value cannot substitute for state identity.

Supported changes are `STIPULATED_CONFIGURATION_CHANGE` or analytic selection. Observation construction is `CONSTRUCTED_STATE_FROM_OBSERVATION`. `EMPIRICALLY_ESTIMATED_TRANSITION` and continuous-time dynamics are not represented and remain blocked.
""")

    write_text(DOCS / "NETWORK_STATE_OPERATION_TAXONOMY.md", """# Network State operation taxonomy

**READ-ONLY INVENTORY — PRODUCTION SCHEMAS UNCHANGED**

| Operation | State meaning | Does not establish |
|---|---|---|
| ADD_NODE | add a stipulated node, optionally to boundary | empirical entry mechanism |
| DEACTIVATE_NODE | deactivate node; remove boundary membership, incident ties/opportunities | real-world intervention effectiveness |
| ADD_TIE / REMOVE_TIE | stipulate adjacency | observed tie formation/dissolution |
| UPDATE_TIE_WEIGHT | stipulate an explicit weight meaning/unit | observed measurement |
| CHANGE_MEMBERSHIP | change group membership metadata | node existence, boundary inclusion, tie, exposure |
| CHANGE_BOUNDARY | change analytic selection only; must occur alone | physical network change |
| CHANGE_CONTACT_OPPORTUNITY | change potential opportunity | realized tie or encounter |
| CHANGE_ACCESS | enable/disable an opportunity | receipt, contact or exposure |

Operation order is explicit. IDs are immutable; removed tie IDs are retired. No operation advances an implicit clock or produces evidence, causal contribution, ontology edits, or EffectAssertions.
""")

    table = "\n".join(f"| {key} | {value} |" for key, value in counts.items())
    write_text(DOCS / "NETWORK_STATE_MIGRATION_CLASSIFICATION.md", f"""# Network State migration classification

**{NOTICE}**

| Category | Count |
|---|---:|
{table}

H12 and H20 are already representable, while the root architecture question needs only a documented contract. REL-SOC-017 and REL-SOC-035 remain blocked on later aggregate-source governance; REL-TEC-050 lacks science establishing a state transition and an exact segregation computation. No production migration is proposed.
""")

    consumer_lines = "\n".join(f"| `{r['path']}` | {r['impact']} | {r['finding']} |" for r in consumer_data["consumers"])
    write_text(DOCS / "NETWORK_STATE_CONSUMER_IMPACT.md", f"""# Network State consumer impact

**{NOTICE}**

| Consumer | Impact | Finding |
|---|---|---|
{consumer_lines}

No current internal FCM, model-construction or scenario-service path was found that consumes a state delta or metric receipt as a causal edge. Future consumers must preserve exact state/profile references and fail closed; this decision test changes no behavior.
""")

    handoff_lines = "\n".join(f"| `{r['relationshipId']}` | `{r['sourceEntityId']}` → `{r['targetEntityId']}` | {r['metricRole']} | {', '.join(r['networkStateRequirements'])} | {', '.join(r['downstream'])} |" for r in handoffs)
    approval = ("Approve the bounded WP-PSG-003 A+C architecture direction tested in DP-PSG-003: retain the existing immutable typed ScenarioStateDelta, ScenarioOperationReference, state receipt and RelationalState lineage as the sole bounded representation for supported stipulated node, tie, membership, boundary, opportunity and access changes; use exact governed RDS computation profiles or preserved legacy derivations only for deterministic recalculation; and keep unsupported or empirically estimated transitions blocked. Do not create a separate NetworkStateTransition class unless a future governed requirement demonstrates a distinct scientific concept. This authorizes architecture direction and optional non-production prototyping only; it does not authorize production Network State schema or state migration, empirical causal claims, Relationships, EffectAssertions, HappeningTypes, cross-level execution, RDS causal-source eligibility, lifecycle change, activation, or production state mutation.")
    write_text(DOCS / "NETWORK_STATE_ARCHITECTURE_DECISION_PACKET.md", f"""# DP-PSG-003 — Network State architecture decision packet

**HUMAN ARCHITECTURE GOVERNANCE REQUIRED**

## Current problem

State operations, deterministic metric changes and empirical causal effects must remain separate. Current tests show the production V1 delta already supplies the bounded transition representation.

## Recommendation

Choose bounded **A+C**. Use current typed `ScenarioStateDelta`; use `ScenarioOperationReference` only for non-effect scientific-operation identity; recalculate through exact derivation/profile semantics; leave unsupported transitions blocked. Reject B for current scope as duplicate architecture.

## Cross-level handoff

| Relationship | Proposition | Metric/state finding | Exact Network State input | Later work |
|---|---|---|---|---|
{handoff_lines}

## Safeguards

- modeled delta is not an occurrence or empirical effect;
- metric change is not a Relationship, EffectAssertion or causal contribution;
- direct RDS EffectAssertions remain prohibited;
- RDS causal-source eligibility remains false pending WP-PSG-005;
- alternate state-delta/metric/causal representations go to WP-PSG-004;
- historical states remain immutable and rollback means selecting/replaying a branch.

## Exact bounded approval statement

{approval}
""")


def main():
    before = protected_hashes()
    results = synthetic_results()
    handoffs = relationship_handoffs()
    migration_data = migration(handoffs)
    consumer_data = consumers()
    options = option_results()
    after = protected_hashes()
    assert before == after
    write_json(DATA / "network-state-test-cases.json", results)
    write_json(DATA / "network-state-option-results.json", options)
    write_json(DATA / "network-state-migration-classification.json", migration_data)
    write_json(DATA / "network-state-consumer-impact.json", consumer_data)
    write_json(DATA / "network-state-handoffs.json", {"schemaVersion": "1.0.0", "records": handoffs,
                                                        "wpPsg004": ["state-delta route", "metric-recalculation route", "causal Relationship route", "EffectAssertion route"],
                                                        "wpPsg005": ["exact RDS/profile", "state/boundary/window", "constituent mapping", "cross-level route", "causalSourceEligible=false"],
                                                        "productionMutationAuthorized": False})
    write_json(DATA / "protected-production-hashes.json", {"schemaVersion": "1.0.0", "sourceMain": BASELINE,
                                                            "algorithm": "SHA-256", "hashes": before})
    render_docs(results, handoffs, migration_data, consumer_data, options)
    print(json.dumps({"workPackage": "WP-PSG-003", "recommendation": options["recommendation"],
                      "syntheticCases": 10, "migrationRecords": migration_data["recordCount"],
                      "protectedFiles": len(before), "productionMutation": False}, indent=2))


if __name__ == "__main__":
    main()
