"""Build the read-only Psychological Layer activation-readiness audit."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
READY = "READY_FOR_ACTIVATION_REVIEW"
KEEP = "KEEP_INACTIVE"
BLOCKED = "BLOCKED"
READY_NUMBERS = {2, 3, 5, 7, 12, 23}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def bullets(identifiers):
    return "\n".join(f"- `{identifier}`" for identifier in identifiers)


def build():
    catalog = read(ROOT / "data/actions-events-v1/catalog.json")
    relationships = read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]
    ri_evidence = read(ROOT / "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]
    types = [x for x in catalog["happeningTypes"] if x["id"].startswith("HT-V1-PSY-LAYER-")]
    effects = [x for x in catalog["effectAssertions"] if x["id"].startswith("EA-V1-PSY-LAYER-")]
    assessments = [x for x in catalog["evidenceAssessments"] if x["id"].startswith("EVA-AE-V1-PSY-LAYER-")]
    relationship = next(x for x in relationships if x["id"] == "REL-V1-PSY-LAYER-001")
    relationship_evidence = next(x for x in ri_evidence if x["id"] == "EVA-V1-PSY-LAYER-REL-001")
    effect_by_number = {int(x["id"].rsplit("-", 1)[1]): x for x in effects}
    type_to_effect_number = {x["typeId"]: int(x["id"].rsplit("-", 1)[1]) for x in effects}
    assessment_by_effect = {x["assertion"]["objectId"]: x for x in assessments}
    recommendations = []

    def add(identifier, record_type, recommendation, dependencies, reason, blockers=None):
        recommendations.append({
            "id": identifier,
            "type": record_type,
            "currentStatus": "GOVERNED/INACTIVE",
            "recommendation": recommendation,
            "dependencies": dependencies,
            "blockers": blockers or [],
            "reason": reason,
        })

    add(
        relationship["id"], "RELATIONSHIP", BLOCKED,
        [relationship_evidence["id"], "EA-V1-PSY-LAYER-001"],
        "The exact proposition is governed and source-resolved, but its exposure contribution duplicates EA-001 and current active-consumer semantics do not enforce the one-contribution rule; activation also intersects the unresolved PSY-003/PSY-116 classification boundary.",
        ["BLK-PSY-003", "SHARED-CONTRIBUTION-PSY-001"],
    )
    add(
        relationship_evidence["id"], "EVIDENCE_ASSESSMENT", BLOCKED,
        relationship["sourceIds"] + [relationship["id"]],
        "The MIXED/MODERATE synthesis is scientifically usable, but activation must follow a selected non-duplicative assertion representation.",
        ["SHARED-CONTRIBUTION-PSY-001"],
    )

    for happening_type in sorted(types, key=lambda x: x["id"]):
        if happening_type["id"] in type_to_effect_number:
            number = type_to_effect_number[happening_type["id"]]
            if number == 1:
                add(
                    happening_type["id"], "HAPPENING_TYPE", BLOCKED,
                    ["EA-V1-PSY-LAYER-001"],
                    "This deliberate identity has only the blocked repetition EffectAssertion and must not activate without an active non-duplicative effect.",
                    ["SHARED-CONTRIBUTION-PSY-001"],
                )
            else:
                add(
                    happening_type["id"], "HAPPENING_TYPE", READY,
                    [f"EA-V1-PSY-LAYER-{number:03d}"],
                    "Reusable identity is exact and source-provenanced; active meaning is clear only in the atomic deliberate type/effect bundle. Identity activation implies no efficacy or practitioner permission.",
                )
        else:
            add(
                happening_type["id"], "HAPPENING_TYPE", KEEP, [],
                "Governed identity remains valid, but it has no governed EffectAssertion. Active status would add no supported production effect meaning and deliberate identities fail the active-effect dependency rule.",
            )

    for effect in sorted(effects, key=lambda x: x["id"]):
        number = int(effect["id"].rsplit("-", 1)[1])
        assessment = assessment_by_effect[effect["id"]]
        if number == 1:
            add(
                effect["id"], "EFFECT_ASSERTION", BLOCKED,
                [assessment["id"], effect["typeId"], relationship["id"]],
                "Exact bounded repetition effect remains one contribution with REL-001. Current active-consumer semantics do not structurally prevent additive use of both representations.",
                ["BLK-PSY-003", "SHARED-CONTRIBUTION-PSY-001"],
            )
        else:
            add(
                effect["id"], "EFFECT_ASSERTION", READY,
                [assessment["id"], effect["typeId"]],
                "Exact Driver target, property, direction, timing and population/task scope are machine-readable; evidence and null/contrary boundaries remain explicit; no RDS, quantitative-execution or practitioner-actionability implication.",
            )

    for assessment in sorted(assessments, key=lambda x: x["id"]):
        number = int(assessment["id"].rsplit("-", 1)[1])
        effect_id = assessment["assertion"]["objectId"]
        source_ids = sorted({x["sourceId"] for x in assessment["sourceFindings"]})
        if number == 1:
            add(
                assessment["id"], "EVIDENCE_ASSESSMENT", BLOCKED,
                source_ids + [effect_id],
                "MIXED evidence is source-resolved, but its assertion is blocked by the duplicate-contribution representation decision.",
                ["SHARED-CONTRIBUTION-PSY-001"],
            )
        else:
            add(
                assessment["id"], "EVIDENCE_ASSESSMENT", READY,
                source_ids + [effect_id],
                "Governed synthesis is source-resolved and retains its exact SUPPORTS/MIXED, null, contrary, overlap and access-depth qualifications.",
            )

    all_source_ids = sorted(set(relationship["sourceIds"]) | {
        finding["sourceId"] for assessment in assessments for finding in assessment["sourceFindings"]
    })
    counts = {
        "audited": 45,
        "readyForActivationReview": sum(x["recommendation"] == READY for x in recommendations),
        "keepInactive": sum(x["recommendation"] == KEEP for x in recommendations),
        "blocked": sum(x["recommendation"] == BLOCKED for x in recommendations),
        "newActive": 0,
    }
    audit = {
        "schemaVersion": "1.0.0",
        "auditId": "AUD-PSYCHOLOGICAL-LAYER-ACTIVATION-V1-20260917-001",
        "programId": "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260907-001",
        "governanceDecisionId": "GOV-PSYCHOLOGICAL-LAYER-001-2026-09-17",
        "materializationMerge": "5e9a8ce241d7f4dc29845c50063c95530fd49a14",
        "auditedMain": "5e9a8ce241d7f4dc29845c50063c95530fd49a14",
        "date": "2026-09-17",
        "auditOnly": True,
        "activationAuthorized": False,
        "statusChanges": 0,
        "counts": counts,
        "recommendations": recommendations,
        "activationOrder": [
            {
                "step": 1,
                "ids": [f"EVA-AE-V1-PSY-LAYER-{number:03d}" for number in sorted(READY_NUMBERS)],
                "mode": "BEFORE_OR_SAME_TRANSACTION",
            },
            {
                "step": 2,
                "bundles": [
                    [effect_by_number[number]["typeId"], f"EA-V1-PSY-LAYER-{number:03d}"]
                    for number in sorted(READY_NUMBERS)
                ],
                "mode": "ATOMIC_DELIBERATE_TYPE_EFFECT_BUNDLE_AFTER_EVIDENCE",
            },
        ],
        "blockedActivationChoice": {
            "ids": [
                "EVA-V1-PSY-LAYER-REL-001", "REL-V1-PSY-LAYER-001",
                "EVA-AE-V1-PSY-LAYER-001", "HT-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001",
            ],
            "requiredDecision": "Select a single active representation or add governed runtime contribution-dedup semantics; do not activate both assertions additively.",
        },
        "sourceAudit": {
            "canonicalSourceIds": all_source_ids,
            "sourceCount": len(all_source_ids),
            "unresolvedIdentities": [],
            "metadataVerified": True,
            "overlapPreserved": True,
            "unsupportedQuantitativeEstimates": 0,
        },
        "blockers": [
            {"id": "BLK-PSY-001", "status": "UNRESOLVED", "affectedAuditedRecords": [], "reason": "Approved records do not target the component/profile entities covered by this blocker."},
            {"id": "BLK-PSY-002", "status": "UNRESOLVED", "affectedAuditedRecords": [], "reason": "No approved record targets PSY-130."},
            {"id": "BLK-PSY-003", "status": "UNRESOLVED", "affectedAuditedRecords": ["REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001"], "reason": "Exact referents make governed storage safe, but active duplicate-control semantics remain unresolved for the shared repetition contribution."},
        ],
        "rdsSafety": {"passed": True, "directTargets": [], "relationalStateTargets": [], "newTargetSemantics": False},
        "sharedContribution": {
            "id": "CONTRIB-PSY-LAYER-REPETITION-001",
            "relationshipId": "REL-V1-PSY-LAYER-001",
            "effectAssertionId": "EA-V1-PSY-LAYER-001",
            "doubleCountingDetected": False,
            "activationBlockedUntilExclusiveOrDeduplicated": True,
        },
        "productionCounts": {"activeRelationships": 457, "activeCausalRelationships": 436, "newActive": 0},
    }
    return audit


def render_markdown(audit):
    recommendations = audit["recommendations"]
    ready = [x["id"] for x in recommendations if x["recommendation"] == READY]
    keep = [x["id"] for x in recommendations if x["recommendation"] == KEEP]
    blocked = [x["id"] for x in recommendations if x["recommendation"] == BLOCKED]
    source_count = audit["sourceAudit"]["sourceCount"]
    return f"""# Psychological Layer activation audit 001

**READ-ONLY ACTIVATION AUDIT — HUMAN DECISION REQUIRED**

Audit `AUD-PSYCHOLOGICAL-LAYER-ACTIVATION-V1-20260917-001` reviews only the 45 Psychological records materialized by governance decision `GOV-PSYCHOLOGICAL-LAYER-001-2026-09-17` and merged at `5e9a8ce241d7f4dc29845c50063c95530fd49a14`.

This audit authorizes and performs **no activation**. All 45 records remain `GOVERNED / INACTIVE`; status changes = 0. It does not change science, ontology, classification, target semantics, source identity, or practitioner/model eligibility.

## Result

| Recommendation | Records |
| --- | ---: |
| `READY_FOR_ACTIVATION_REVIEW` | {len(ready)} |
| `KEEP_INACTIVE` | {len(keep)} |
| `BLOCKED` | {len(blocked)} |
| New `ACTIVE` | 0 |

The activation-review subset consists of six evidence/type/effect bundles. No Relationship is recommended for activation review at this checkpoint.

## READY_FOR_ACTIVATION_REVIEW

{bullets(ready)}

Each ready EffectAssertion has an exact Driver target, declared effect property and direction, bounded timing/population/task scope, registered governed evidence, no direct RDS or RelationalState target, and no unresolved source identity. `MIXED` remains `MIXED`; approval does not imply effect size, quantitative execution, or practitioner actionability.

| EvidenceAssessment | HappeningType | EffectAssertion | Exact bounded endpoint |
| --- | --- | --- | --- |
| `EVA-AE-V1-PSY-LAYER-002` | `HT-V1-PSY-LAYER-002` | `EA-V1-PSY-LAYER-002` | Explanatory refutation; later belief in the same specified false proposition; one-week bounded contrast |
| `EVA-AE-V1-PSY-LAYER-003` | `HT-V1-PSY-LAYER-003` | `EA-V1-PSY-LAYER-003` | Response-contingent termination; perceived control over the specified aversive-noise task |
| `EVA-AE-V1-PSY-LAYER-005` | `HT-V1-PSY-LAYER-004` | `EA-V1-PSY-LAYER-005` | Virtual pass withholding; immediate perceived exclusion during the bounded adult task |
| `EVA-AE-V1-PSY-LAYER-007` | `HT-V1-PSY-LAYER-006` | `EA-V1-PSY-LAYER-007` | Two bounded homework choices; interest/enjoyment in that task/unit |
| `EVA-AE-V1-PSY-LAYER-012` | `HT-V1-PSY-LAYER-011` | `EA-V1-PSY-LAYER-012` | Title-cued retrieval practice; delayed same-cue prose idea-unit recall |
| `EVA-AE-V1-PSY-LAYER-023` | `HT-V1-PSY-LAYER-022` | `EA-V1-PSY-LAYER-023` | Specified high-control health message; directly measured freedom threat/reactance |

EA-002 uses the safe current representation for `PSY-003`: the proposition and belief-confidence referent are explicit, and no `PSY-116` calibration, accuracy, truth, behavior, or unrestricted correction claim is made. The unresolved construct classification remains preserved and would govern any broader claim.

## KEEP_INACTIVE

{bullets(keep)}

These 22 identities are coherent governed operation identities, but each lacks a governed EffectAssertion. All are deliberate Intervention-subset records under the current catalog. Active identity status has no independent production meaning here and would fail the active-effect dependency rule. Keeping them inactive does not reject their identity and does not adjudicate efficacy.

## BLOCKED

{bullets(blocked)}

`REL-V1-PSY-LAYER-001` and `EA-V1-PSY-LAYER-001` encode the same repetition exposure contribution, `CONTRIB-PSY-LAYER-REPETITION-001`. Their exact bounded science is governed and their evidence is source-resolved, but the current active Relationship contract does not structurally carry the shared-contribution identity used by the Actions/Events record. Activating both could allow a consumer to count one exposure twice.

The five-record repetition bundle therefore remains blocked until a human chooses one active representation or separately authorizes governed runtime contribution-dedup semantics. This also preserves `BLK-PSY-003`: storage is safe because the proposition/confidence referent is explicit, while active duplicate-control and the `PSY-003`/`PSY-116` classification boundary remain unresolved.

## Skeptical scientific pass

- Repetition: context-dependent direction, extreme-implausibility counterexample, task-instruction boundaries, no universal dose-response, and no truth/calibration/behavior claim remain explicit. Duplicate activation blocks the bundle.
- Explanatory refutation: the supported contrast is the reported one-week same-claim comparison; the one-day null and broader mixed correction literature remain explicit.
- Controllability task: the target is perceived control over that laboratory task, with limited evidence; no chronic agency, safety, or stress-protection claim.
- Ostracism: `SUPPORTS` applies to immediate perceived exclusion in bounded young-adult virtual tasks; the age-six null constrains transport.
- Bounded choice: heterogeneous evidence and null transfer tasks remain; no universal autonomy or long-term trait effect.
- Retrieval practice: delayed same-cue recall only; the immediate reverse and readability null remain explicit.
- High-control recommendation: directly measured freedom threat/reactance only; no mandate, behavior, mediation-chain, or general coercion claim.

No source identity conflict was found across {source_count} canonical sources used by the audited governed records. Review/included-study overlap, shared datasets, preprint/publication identity, theoretical versus experimental roles, and access depth remain as materialized.

## Preserved architecture and construct blockers

- `BLK-PSY-001` / `ARCH-PSY-LAYER-0001` remains unresolved. None of the seven governed effects targets its blocked component/profile entities.
- `BLK-PSY-002` / `ARCH-PSY-LAYER-0002` remains unresolved. No governed record in this audit targets `PSY-130`.
- `BLK-PSY-003` remains unresolved and blocks the repetition Relationship/effect activation bundle as described above.

No ontology or architecture change is implemented or recommended by this audit.

## Exact dependency order

1. Activate a ready bundle's governed EvidenceAssessment before, or in the same transaction as, its assertion.
2. Activate each deliberate HappeningType and its EffectAssertion atomically after its EvidenceAssessment.
3. Continue to fail closed for model and practitioner use: no numeric weight, execution contract, actor feasibility, legal/ethical assessment, or applicability approval exists.
4. Do not activate the repetition bundle without the separate consequential decision described above.

## Explicit exclusions

The other 23 candidate EffectAssertions, all review-only Relationship proposals, 36 existing Relationship research-needed dispositions, 151 rejected hypotheses, 209 research-needed hypotheses, and all three blockers remain outside activation review. Network State V1, prior pilots, existing production propositions, Driver/RDS definitions, aliases, and crosswalks are unchanged.

## Audit conclusion

Exact recommended activation-review subset: {len(ready)} records in six dependency bundles. Exact keep-inactive subset: {len(keep)} identity records. Exact blocked subset: {len(blocked)} repetition records. New `ACTIVE` = 0.

**ACTIVATION REMAINS A CONSEQUENTIAL HUMAN DECISION.**
"""


def main():
    audit = build()
    (DOC / "PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DOC / "PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.md").write_text(
        render_markdown(audit), encoding="utf-8"
    )
    print(json.dumps(audit["counts"], indent=2))


if __name__ == "__main__":
    main()
