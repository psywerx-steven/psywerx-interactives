"""Materialize the human-authorized Psychological Layer activation checkpoint.

Only six evidence-first atomic bundles are activated. Scientific content,
sources, Relationships, ontology, architecture, and the historical read-only
activation audit are not modified.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import actions_events_v1 as ae


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/actions-events-v1/catalog.json"
MANIFEST_PATH = ROOT / "data/actions-events-v1/PSYCHOLOGICAL_LAYER-activation-manifest.json"
CANDIDATE_DIR = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"
DECISION_DATA_PATH = CANDIDATE_DIR / "activation-decision-001.json"
DOC_DIR = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
DECISION_PATH = "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_ACTIVATION_DECISION_001.md"
DECISION_DOC = ROOT / DECISION_PATH

DECISION_ID = "GOV-PSYCHOLOGICAL-LAYER-ACTIVATION-001-2026-09-18"
GOVERNANCE_DECISION_ID = "GOV-PSYCHOLOGICAL-LAYER-001-2026-09-17"
AUDIT_ID = "AUD-PSYCHOLOGICAL-LAYER-ACTIVATION-V1-20260917-001"
PRE_ACTIVATION_HEAD = "d7bb61b0e139e93b874c6aa9844dbfffb94bc97a"
DATE = "2026-09-18"
STAMP = "2026-09-18T18:00:00Z"

BUNDLES = (
    ("EXPLANATORY_REFUTATION", "EVA-AE-V1-PSY-LAYER-002", "HT-V1-PSY-LAYER-002", "EA-V1-PSY-LAYER-002"),
    ("RESPONSE_CONTINGENT_CONTROL", "EVA-AE-V1-PSY-LAYER-003", "HT-V1-PSY-LAYER-003", "EA-V1-PSY-LAYER-003"),
    ("VIRTUAL_OSTRACISM", "EVA-AE-V1-PSY-LAYER-005", "HT-V1-PSY-LAYER-004", "EA-V1-PSY-LAYER-005"),
    ("BOUNDED_CHOICE", "EVA-AE-V1-PSY-LAYER-007", "HT-V1-PSY-LAYER-006", "EA-V1-PSY-LAYER-007"),
    ("RETRIEVAL_PRACTICE", "EVA-AE-V1-PSY-LAYER-012", "HT-V1-PSY-LAYER-011", "EA-V1-PSY-LAYER-012"),
    ("HIGH_CONTROL_HEALTH_MESSAGE", "EVA-AE-V1-PSY-LAYER-023", "HT-V1-PSY-LAYER-022", "EA-V1-PSY-LAYER-023"),
)
ACTIVE_IDS = frozenset(identifier for bundle in BUNDLES for identifier in bundle[1:])
ACTIVE_EVIDENCE_IDS = frozenset(bundle[1] for bundle in BUNDLES)
ACTIVE_TYPE_IDS = frozenset(bundle[2] for bundle in BUNDLES)
ACTIVE_EFFECT_IDS = frozenset(bundle[3] for bundle in BUNDLES)
KEEP_INACTIVE_TYPE_IDS = frozenset(
    f"HT-V1-PSY-LAYER-{number:03d}"
    for number in (5, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29)
)
BLOCKED_REPETITION_IDS = frozenset({
    "REL-V1-PSY-LAYER-001",
    "EVA-V1-PSY-LAYER-REL-001",
    "HT-V1-PSY-LAYER-001",
    "EA-V1-PSY-LAYER-001",
    "EVA-AE-V1-PSY-LAYER-001",
})


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def activate(record: dict) -> None:
    """Apply the one authorized transition, idempotently."""
    identifier = record["id"]
    if identifier not in ACTIVE_IDS:
        raise ValueError(f"Record is outside the authorized activation set: {identifier}")
    governance = record["governance"]
    if governance["lifecycleStatus"] != "GOVERNED":
        raise ValueError(f"Activation source lifecycle is not GOVERNED: {identifier}")
    if governance["activationStatus"] == "ACTIVE":
        if governance.get("decisionRecord") != DECISION_PATH:
            raise ValueError(f"Record is ACTIVE under a different decision: {identifier}")
        return
    if governance["activationStatus"] != "INACTIVE":
        raise ValueError(f"Activation source state is not GOVERNED/INACTIVE: {identifier}")
    governance["activationStatus"] = "ACTIVE"
    governance["decisionRecord"] = DECISION_PATH
    governance["authorizedBy"] = "authorized human governor"
    governance["decisionDate"] = DATE
    governance["effectiveVersion"] = "PSYCHOLOGICAL-LAYER-ACTIVATION-001"
    governance["decisionRationale"] = (
        "Exact activation of one audited evidence-first Psychological bundle; "
        "scientific identity, proposition, scope, evidence synthesis, limitations, "
        "and non-quantitative boundary remain unchanged."
    )
    governance["transitionProvenance"].append({
        "fromState": {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"},
        "toState": {"lifecycleStatus": "GOVERNED", "activationStatus": "ACTIVE"},
        "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "rationale": (
            "Mechanical materialization of the exact six-bundle activation explicitly "
            "authorized by the human governor after the independent activation audit."
        ),
        "timestamp": STAMP,
        "objectId": identifier,
        "revision": record["revision"],
        "provenance": f"{AUDIT_ID}:{PRE_ACTIVATION_HEAD}:activation-001",
        "governanceDecisionRecord": DECISION_PATH,
        "exactDecisionMaterialization": True,
    })


def decision_document(records: list[dict]) -> str:
    by_id = {record["id"]: record for record in records}
    hashes = "\n".join(f"- `{identifier}` — `{ae.digest(by_id[identifier])}`" for identifier in sorted(ACTIVE_IDS))
    bundles = "\n".join(
        f"{index}. **{name.replace('_', ' ').title()}** — `{evidence}`, `{happening_type}`, `{effect}`"
        for index, (name, evidence, happening_type, effect) in enumerate(BUNDLES, 1)
    )
    inactive = "\n".join(f"- `{identifier}`" for identifier in sorted(KEEP_INACTIVE_TYPE_IDS))
    blocked = "\n".join(f"- `{identifier}`" for identifier in sorted(BLOCKED_REPETITION_IDS))
    return f"""# Psychological Layer activation decision 001

**HUMAN GOVERNANCE DECISION — EXACT PARTIAL ACTIVATION**

- Decision ID: `{DECISION_ID}`
- Layer governance decision: `{GOVERNANCE_DECISION_ID}`
- Activation-readiness audit: `{AUDIT_ID}`
- Audited pre-activation head: `{PRE_ACTIVATION_HEAD}`
- Effective date: `{DATE}`
- Authority: authorized human governor

## Human authorization

APPROVE activation of exactly six audited evidence-first atomic bundles / 18
records. Governance remains `GOVERNED`; activation changes from `INACTIVE` to
`ACTIVE`. EvidenceAssessment activation precedes or is committed atomically with
its assertion, and each HappeningType activates with its EffectAssertion.

{bundles}

## Exact bundle boundaries retained

- **Explanatory refutation:** a concise explanatory refutation of one specified
  false claim affects later belief/confidence in that same proposition in the
  bounded one-week contrast. Evidence remains `MIXED`; the one-day null remains
  explicit. No universal correction, truth, calibration, or behavior claim.
- **Response-contingent control:** a response-contingent termination rule in the
  specified aversive-noise task affects perceived control over that task.
  Evidence remains limited/mixed. No chronic agency, stress-protection, or
  general learned-helplessness inference.
- **Virtual ostracism:** withholding later virtual ball passes after initial
  participation affects immediate perceived exclusion in the bounded task.
  Adult/young-adult limits and the age-six null/transport limit remain. No
  friendship-loss or real-network structural claim.
- **Bounded choice:** specified bounded task alternatives affect
  interest/enjoyment in that task/unit. Evidence remains `MIXED`, including null
  transfer findings. No universal autonomy benefit or stable motivation trait.
- **Retrieval practice:** title-cued free recall without feedback affects delayed
  same-cue prose idea-unit recall. The immediate reverse remains explicit. No
  generic knowledge, universal memory, confidence, or calibration claim.
- **High-control health message:** the specified high-control recommendation
  affects directly measured freedom threat/reactance for the governed message
  and population. Evidence remains `MIXED`. No general coercion, actual behavior,
  mediation-chain, or universal institutional-policy claim.

## Exact active record hashes

{hashes}

## Scientific boundary

Activation permits these records to participate in the production knowledge
catalog under their already governed exact scope. It adds no numeric causal
weight, effect size, success probability, practitioner recommendation,
legal/ethical authorization, actor feasibility, universal applicability,
quantitative execution, or downstream causal propagation.

All `MIXED`, `SUPPORTS`, null, contrary, population, timing, task, referent,
transfer, and contribution semantics remain byte-for-byte unchanged outside the
lifecycle governance object.

## Governed identities explicitly kept inactive

These 22 identity-only records remain `GOVERNED / INACTIVE`; inactivity is not a
scientific rejection.

{inactive}

## Repetition bundle remains blocked

{blocked}

`CONTRIB-PSY-LAYER-REPETITION-001` remains one shared causal contribution. No
representation is selected, no runtime contribution deduplication is added, and
`BLK-PSY-003` remains unresolved.

## Other exclusions

- No Psychological Relationship activates.
- `BLK-PSY-001`, `BLK-PSY-002`, and `BLK-PSY-003` remain unresolved.
- No ontology definition, classification, target schema, or architecture changes.
- No source content or source registration changes.
- No production Relationship proposition changes.
- The 57 revision, 5 retype, and 2 split proposals remain unimplemented.
- The 36 existing-Relationship and 23 EffectAssertion research-needed items remain deferred.
- The 151 rejection and 209 research-needed ledger dispositions remain preserved.
"""


def materialize() -> None:
    original = read(CATALOG_PATH)
    catalog = copy.deepcopy(original)
    collections = {
        record["id"]: record
        for key in ("happeningTypes", "effectAssertions", "evidenceAssessments")
        for record in catalog[key]
    }
    missing = ACTIVE_IDS - collections.keys()
    if missing:
        raise ValueError(f"Authorized records missing from catalog: {sorted(missing)}")

    # Evidence first, followed by the atomic identity/assertion pair. One final
    # catalog write ensures no externally visible partial bundle state.
    for _, evidence_id, type_id, effect_id in BUNDLES:
        activate(collections[evidence_id])
        activate(collections[type_id])
        activate(collections[effect_id])

    active_records = [collections[identifier] for identifier in sorted(ACTIVE_IDS)]
    authorization = {
        "decisionId": DECISION_ID,
        "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR",
        "effectiveDate": DATE,
        "authorizedObjects": [
            {"id": record["id"], "revision": record["revision"], "recordHash": ae.digest(record)}
            for record in active_records
        ],
        "recordClass": "SCIENTIFIC_RECORD",
    }
    by_decision = {row["decisionId"]: row for row in catalog["authorizations"]}
    prior = by_decision.get(DECISION_ID)
    if prior is not None and prior != authorization:
        raise ValueError("Activation authorization differs from deterministic output")
    by_decision[DECISION_ID] = authorization
    catalog["authorizations"] = [
        by_decision.pop(row["decisionId"], row) for row in catalog["authorizations"]
    ]
    catalog["authorizations"].extend(by_decision.values())

    write_text(DECISION_DOC, decision_document(active_records))
    ae.validate_catalog(catalog, ae.Context.repository())

    psychological = {
        record["id"]: record
        for key in ("happeningTypes", "effectAssertions", "evidenceAssessments")
        for record in catalog[key]
        if "-PSY-LAYER-" in record["id"]
    }
    actual_active = {identifier for identifier, record in psychological.items() if record["governance"]["activationStatus"] == "ACTIVE"}
    if actual_active != ACTIVE_IDS:
        raise ValueError(f"Psychological active set differs from authorization: {sorted(actual_active ^ ACTIVE_IDS)}")
    if any(psychological[identifier]["governance"]["activationStatus"] != "INACTIVE" for identifier in KEEP_INACTIVE_TYPE_IDS):
        raise ValueError("An identity-only Psychological record did not remain inactive")
    for identifier in BLOCKED_REPETITION_IDS & psychological.keys():
        if psychological[identifier]["governance"]["activationStatus"] != "INACTIVE":
            raise ValueError(f"Blocked repetition record activated: {identifier}")

    write_json(CATALOG_PATH, catalog)
    manifest = {
        "schemaVersion": "1.0.0",
        "materializationId": "PSYCHOLOGICAL-LAYER-ACTIVATION-MATERIALIZATION-001",
        "decisionId": DECISION_ID,
        "decisionRecord": DECISION_PATH,
        "governanceDecisionId": GOVERNANCE_DECISION_ID,
        "activationAuditId": AUDIT_ID,
        "preActivationHead": PRE_ACTIVATION_HEAD,
        "effectiveDate": DATE,
        "atomicBundles": [
            {"name": name, "evidenceAssessmentId": evidence, "happeningTypeId": happening_type, "effectAssertionId": effect}
            for name, evidence, happening_type, effect in BUNDLES
        ],
        "activatedIds": sorted(ACTIVE_IDS),
        "activatedCounts": {"relationships": 0, "evidenceAssessments": 6, "happeningTypes": 6, "effectAssertions": 6, "total": 18},
        "keptInactiveIdentityIds": sorted(KEEP_INACTIVE_TYPE_IDS),
        "blockedRepetitionIds": sorted(BLOCKED_REPETITION_IDS),
        "preservedBlockers": ["BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"],
        "deferred": {"revisionReview": 57, "retypeReview": 5, "splitReview": 2, "existingRelationshipResearchNeeded": 36, "effectAssertionsResearchNeeded": 23, "rejectedHypotheses": 151, "researchNeededHypotheses": 209},
        "scientificSemanticsChanged": False,
        "sourceContentChanged": False,
        "relationshipContentChanged": False,
        "ontologyChanged": False,
        "architectureChanged": False,
    }
    decision_data = {
        "schemaVersion": "1.0.0",
        "decisionId": DECISION_ID,
        "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR",
        "effectiveDate": DATE,
        "humanAuthorization": "APPROVE activation of exactly six audited bundles / 18 records",
        "referenceDecisions": [GOVERNANCE_DECISION_ID, AUDIT_ID],
        "activatedIds": sorted(ACTIVE_IDS),
        "explicitlyKeptInactive": sorted(KEEP_INACTIVE_TYPE_IDS),
        "blockedRepetitionIds": sorted(BLOCKED_REPETITION_IDS),
        "unresolvedBlockers": ["BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"],
        "authorizationLimits": [
            "No Psychological Relationship activation",
            "No scientific semantic change",
            "No source change",
            "No ontology, classification, target-schema, or architecture change",
            "No numerical execution or practitioner recommendation authority",
        ],
    }
    write_json(MANIFEST_PATH, manifest)
    write_json(DECISION_DATA_PATH, decision_data)
    print("Psychological Layer activation: six atomic bundles / 18 records ACTIVE; zero Relationships ACTIVE.")


if __name__ == "__main__":
    materialize()
