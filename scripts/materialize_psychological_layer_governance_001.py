"""Materialize the authorized Psychological Layer governance decision.

The materializer is additive and deterministic. It registers only required
sources, creates governed/inactive canonical records, and preserves every
pre-existing production record byte-for-byte at the JSON object level.
"""

from __future__ import annotations

import copy
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

import actions_events_v1 as ae
import relationship_intervention_v1 as ri
import source_verification_v1 as sv


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
AE_CATALOG = ROOT / "data/actions-events-v1/catalog.json"
RI_RELATIONSHIPS = ROOT / "data/relationship-intervention-v1/relationships.json"
RI_EVIDENCE = ROOT / "data/relationship-intervention-v1/evidence-assessments.json"
RI_SOURCES = ROOT / "data/relationship-intervention-v1/source-register.json"
RI_FINDINGS = ROOT / "data/relationship-intervention-v1/relationship-source-findings.json"
MATERIALIZATION_MANIFEST = ROOT / "data/actions-events-v1/PSYCHOLOGICAL_LAYER-materialization-manifest.json"
SOURCE_MANIFEST = DOCS / "PSYCHOLOGICAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json"
DECISION_DATA = CANDIDATE / "governance-decision-001.json"

PROGRAM = "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260907-001"
DECISION = "GOV-PSYCHOLOGICAL-LAYER-001-2026-09-17"
DECISION_PATH = "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_GOVERNANCE_DECISION_001.md"
DECISION_DOC = ROOT / DECISION_PATH
BASELINE = "de38b3948f511602af7aa94a9cd80b78e1a00298"
RECONCILED_MAIN = "fae569f2a281278b896437e10959fdc4937904a7"
RECOMMENDATION_COMMIT = "5675780b7c36c788f222617810bfd07ee64ebfba"
DATE = "2026-09-17"
STAMP = "2026-09-18T02:40:00Z"

APPROVED_EFFECT_NUMBERS = (1, 2, 3, 5, 7, 12, 23)
RELATIONSHIP_ID = "REL-V1-PSY-LAYER-001"
RELATIONSHIP_EVIDENCE_ID = "EVA-V1-PSY-LAYER-REL-001"
SHARED_CONTRIBUTION = "CONTRIB-PSY-LAYER-REPETITION-001"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def ht_id(candidate_id: str) -> str:
    return f"HT-V1-PSY-LAYER-{int(candidate_id.rsplit('-', 1)[1]):03d}"


def effect_id(candidate_id: str) -> str:
    return f"EA-V1-PSY-LAYER-{int(candidate_id.rsplit('-', 1)[1]):03d}"


def effect_evidence_id(candidate_id: str) -> str:
    return f"EVA-AE-V1-PSY-LAYER-{int(candidate_id.rsplit('-', 1)[1]):03d}"


def source_map() -> dict[str, str]:
    required = read(CANDIDATE / "source-registration-recommendations.json")["futureRegistrationManifest"]
    return {row["sourceId"]: f"SRC-{560 + index}" for index, row in enumerate(required)}


SOURCE_MAP = source_map()


def remap_source(identifier: str) -> str:
    return SOURCE_MAP.get(identifier, identifier)


def remap_record(identifier: str) -> str:
    if identifier == "REL-CAND-PSY-LAYER-0001":
        return RELATIONSHIP_ID
    if identifier.startswith("HT-CAND-PSY-LAYER-"):
        return ht_id(identifier)
    if identifier.startswith("EA-CAND-PSY-LAYER-"):
        return effect_id(identifier)
    if identifier == "EVA-REL-CAND-PSY-LAYER-0001":
        return RELATIONSHIP_EVIDENCE_ID
    if identifier.startswith("EVA-EA-CAND-PSY-LAYER-"):
        return effect_evidence_id(identifier)
    return identifier


def governance(candidate: dict, canonical_id: str, rationale: str) -> dict:
    original = candidate["governance"]
    if original["lifecycleStatus"] != "REVIEW_READY" or original["activationStatus"] != "NOT_ELIGIBLE":
        raise ValueError(f"Authorized source record is not REVIEW_READY/NOT_ELIGIBLE: {candidate['id']}")
    transitions = copy.deepcopy(original["transitionProvenance"])
    for transition in transitions:
        transition["objectId"] = canonical_id
        transition["provenance"] += f"; candidate-lineage:{candidate['id']}"
    transitions.append({
        "fromState": {"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"},
        "toState": {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"},
        "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "rationale": "Exact materialization of the authorized Psychological Layer decision; activation explicitly withheld.",
        "timestamp": STAMP,
        "objectId": canonical_id,
        "revision": candidate["revision"],
        "provenance": f"{PROGRAM}:{RECOMMENDATION_COMMIT}:{candidate['id']}",
        "governanceDecisionRecord": DECISION_PATH,
        "exactDecisionMaterialization": True,
    })
    return {
        "lifecycleStatus": "GOVERNED",
        "activationStatus": "INACTIVE",
        "blockStatus": "NONE",
        "decisionOutcome": "APPROVED",
        "authorityBasis": "V1_NATIVE",
        "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor",
        "decisionDate": DATE,
        "effectiveVersion": "PSYCHOLOGICAL-LAYER-GOVERNANCE-001",
        "decisionRationale": rationale,
        "supersedesIds": [],
        "transitionProvenance": transitions,
    }


def provenance(candidate: dict, candidate_id: str) -> dict:
    prior = copy.deepcopy(candidate.get("provenance", {}))
    return {
        "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "method": "Exact mechanical materialization of a human-authorized candidate; no scientific semantic expansion",
        "recordedAt": STAMP,
        "originReferences": sorted(set(prior.get("originReferences", []) + [PROGRAM, BASELINE, RECONCILED_MAIN, RECOMMENDATION_COMMIT, DECISION, candidate_id])),
        "limitations": sorted(set(prior.get("limitations", []) + ["Governance does not authorize activation, numerical execution, or practitioner actionability"])),
    }


def collect_candidates():
    relationships, relationship_evidence, relationship_sidecar = [], [], None
    identities, effects, effect_evidence = [], [], []
    for family in sorted(CANDIDATE.glob("PSY-F*")):
        workspace = read(family / "workspace.json")
        relationships.extend(workspace["passA"].get("relationshipCandidates", []))
        relationship_evidence.extend(workspace["passA"].get("evidence", []))
        identities.extend(workspace["passB"].get("happeningTypes", []))
        effects.extend(workspace["passB"].get("effectAssertions", []))
        effect_evidence.extend(workspace["passB"].get("evidenceAssessments", []))
        sidecars = read(family / "relationship-evidence-sidecars.json")
        for sidecar in sidecars:
            if sidecar["assertionId"] == "REL-CAND-PSY-LAYER-0001":
                relationship_sidecar = sidecar
    return relationships, relationship_evidence, relationship_sidecar, identities, effects, effect_evidence


def make_relationship(candidate: dict, assessment_candidate: dict, sidecar_candidate: dict):
    relationship = copy.deepcopy(candidate)
    relationship["id"] = RELATIONSHIP_ID
    relationship["sourceIds"] = [remap_source(x) for x in relationship["sourceIds"]]
    relationship["evidenceAssessmentIds"] = [RELATIONSHIP_EVIDENCE_ID]
    relationship["governance"] = governance(
        candidate,
        RELATIONSHIP_ID,
        "Approved exact bounded repetition-to-specified-belief-confidence proposition with context-dependent direction, null/counterexample boundaries, and no truth, calibration, behavior, universal-dose, or unrestricted-transfer claim; activation withheld.",
    )
    relationship["compatibility"].update({
        "migrationCompleteness": "COMPLETE",
        "v1Executability": "NOT_EXECUTABLE",
        "blockedFields": ["activationNotAuthorized", "numericalExecutionNotAuthorized", "practitionerActionabilityNotAuthorized"],
    })

    assessment = copy.deepcopy(assessment_candidate)
    assessment["id"] = RELATIONSHIP_EVIDENCE_ID
    assessment["assertion"] = {"objectType": "RELATIONSHIP", "objectId": RELATIONSHIP_ID}
    assessment["sourceIds"] = [remap_source(x) for x in assessment["sourceIds"]]
    assessment["conflictingEvidence"]["sourceIds"] = [remap_source(x) for x in assessment["conflictingEvidence"]["sourceIds"]]
    assessment["governance"] = governance(
        assessment_candidate,
        RELATIONSHIP_EVIDENCE_ID,
        "Approved exact MIXED/MODERATE evidence synthesis for the bounded Relationship; governance does not upgrade evidence certainty and activation is withheld.",
    )
    assessment["reviewProvenance"].update({
        "reviewedAt": STAMP,
        "reviewedBy": "authorized human governor",
        "sourceSchema": f"{PROGRAM}:governance-materialization-001",
    })

    sidecar = copy.deepcopy(sidecar_candidate)
    sidecar["assertionId"] = RELATIONSHIP_ID
    sidecar["evidenceAssessmentId"] = RELATIONSHIP_EVIDENCE_ID
    sidecar["governance"] = copy.deepcopy(assessment["governance"])
    finding_map = {}
    for finding in sidecar["sourceFindings"]:
        old_id = finding["id"]
        finding["id"] = old_id.replace("FND-REL-CAND-PSY-LAYER-0001", "FND-REL-V1-PSY-LAYER-001")
        finding["sourceId"] = remap_source(finding["sourceId"])
        finding["provenance"] = provenance(finding, old_id)
        finding_map[old_id] = finding["id"]
    sidecar["synthesis"]["sourceFindingIds"] = [finding_map[x] for x in sidecar["synthesis"]["sourceFindingIds"]]
    for conflict in sidecar["synthesis"].get("conflicts", []):
        conflict["findingId"] = finding_map[conflict["findingId"]]
    return relationship, assessment, sidecar


def make_identity(candidate: dict) -> dict:
    record = copy.deepcopy(candidate)
    canonical_id = ht_id(candidate["id"])
    record["id"] = canonical_id
    record["identitySourceIds"] = [remap_source(x) for x in record["identitySourceIds"]]
    record["governance"] = governance(candidate, canonical_id, "Approved reusable operation identity only; no efficacy, legality, feasibility, model, practitioner, or activation claim.")
    record["provenance"] = provenance(candidate, candidate["id"])
    return record


def make_effect(candidate: dict, assessment_candidate: dict) -> tuple[dict, dict]:
    canonical_id = effect_id(candidate["id"])
    assessment_id = effect_evidence_id(candidate["id"])
    effect = copy.deepcopy(candidate)
    effect["id"] = canonical_id
    effect["typeId"] = ht_id(effect["typeId"])
    effect["evidenceAssessmentIds"] = [assessment_id]
    effect["governance"] = governance(candidate, canonical_id, "Approved exact reviewed EffectAssertion scope, direction, timing, target, limitations, and contribution identity; no activation or quantitative magnitude.")
    effect["provenance"] = provenance(candidate, candidate["id"])
    if candidate["id"] == "EA-CAND-PSY-LAYER-0001":
        if effect["contribution"]["groupId"] != SHARED_CONTRIBUTION:
            raise ValueError("Repetition contribution identity changed")
        # The V1 EffectAssertion linkage field accepts only EffectAssertion
        # IDs. Preserve the cross-store Relationship link in the reconciliation
        # text and materialization manifest rather than violating that contract.
        effect["contribution"]["relatedAssertionIds"] = []
        effect["contribution"]["reconciliation"] = "Same exposure contribution as REL-V1-PSY-LAYER-001; never sum or propagate as an additional causal input."

    assessment = copy.deepcopy(assessment_candidate)
    assessment["id"] = assessment_id
    assessment["assertion"] = {"objectType": "EFFECT_ASSERTION", "objectId": canonical_id}
    assessment["governance"] = governance(assessment_candidate, assessment_id, "Approved exact evidence synthesis for the governed inactive EffectAssertion; MIXED/SUPPORTS/null/contrary semantics remain unchanged.")
    assessment["provenance"] = provenance(assessment_candidate, assessment_candidate["id"])
    finding_map = {}
    for finding in assessment["sourceFindings"]:
        old_id = finding["id"]
        finding["id"] = old_id.replace("FND-EA-CAND-PSY-LAYER-", "FND-EA-V1-PSY-LAYER-")
        finding["sourceId"] = remap_source(finding["sourceId"])
        finding["provenance"] = provenance(finding, old_id)
        finding_map[old_id] = finding["id"]
    assessment["synthesis"]["sourceFindingIds"] = [finding_map[x] for x in assessment["synthesis"]["sourceFindingIds"]]
    for conflict in assessment["synthesis"].get("conflicts", []):
        conflict["findingId"] = finding_map[conflict["findingId"]]
    return effect, assessment


def normalized_access(value: str) -> str:
    value = value.upper()
    if value == "METADATA":
        return "METADATA"
    if "FULL_TEXT" in value and "SELECTED" not in value:
        return "FULL_TEXT"
    if "SELECTED" in value or "RESULTS" in value or "METHODS" in value or "EXCERPT" in value:
        return "SELECTED_FULL_TEXT"
    return "ABSTRACT_METADATA"


def attestation(source: dict, canonical_id: str) -> dict:
    doi = source["doi"].lower()
    publisher = f"https://doi.org/{doi}"
    metadata = {
        "title": source["title"], "authors": source["authors"], "year": source["year"],
        "publication": source["venue"], "doi": doi, "sourceType": source["sourceType"],
    }
    return {
        "recordKind": "BIBLIOGRAPHIC_VERIFICATION_ATTESTATION",
        "verifiedDate": DATE,
        "authority": "CROSSREF",
        "registryLocator": "https://api.crossref.org/works/" + quote(doi, safe=""),
        "publisherLocator": publisher,
        "accessDepth": normalized_access(source["accessDepth"]),
        "conflicts": [],
        "verificationPurpose": "BIBLIOGRAPHIC_IDENTITY_ONLY_NOT_EFFECT_EVIDENCE",
        "registryMetadata": metadata,
        "publisherMetadata": copy.deepcopy(metadata),
        "registryPublisherLinks": [publisher],
        "locators": {field: f"Crossref work {doi} and DOI resolver/publisher route; normalized against completed candidate verification" for field in sv.FIELDS},
        "versionAlignment": {
            "candidateSourceId": source["id"],
            "relationship": source.get("overlap") or source.get("limitations") or "No separate work version asserted",
            "independentReplication": False if source.get("overlap") else None,
        },
        "reviewMethod": "Completed Layer candidate verification plus live Crossref DOI/title/year check on 2026-09-17; bibliographic identity only.",
        "limitations": [
            f"Scientific access depth remains {source['accessDepth']}; bibliographic verification does not increase it.",
            "Registration adds no scientific evidence, efficacy, activation, model, or practitioner authority.",
            "Overlap, shared-dataset, review/included-study, and version caveats remain attached to the governed records and registration manifest.",
        ],
    }


def make_sources() -> tuple[list[dict], list[dict]]:
    registry = {x["id"]: x for x in read(CANDIDATE / "candidate-source-registry.json")}
    verification = {x["candidateSourceId"]: x for x in read(CANDIDATE / "source-verification-results.json")["records"]}
    recommendation = read(CANDIDATE / "source-registration-recommendations.json")
    dependencies = {x["sourceId"]: x for x in recommendation["futureRegistrationManifest"]}
    if set(SOURCE_MAP) != set(dependencies) or len(SOURCE_MAP) != 44:
        raise ValueError("Authorized source set changed")

    source_records, registrations = [], []
    for candidate_id, canonical_id in SOURCE_MAP.items():
        candidate = registry[candidate_id]
        publisher_url = f"https://doi.org/{candidate['doi'].lower()}"
        check = verification[candidate_id]
        if not check["verified"] or check["doi"] != candidate["doi"].lower():
            raise ValueError(f"Required source not authoritatively verified: {candidate_id}")
        if candidate.get("pmid") and check.get("pubmedOk") is not True:
            raise ValueError(f"PubMed identity mismatch: {candidate_id}")
        if not candidate.get("pmid") and check.get("crossrefOk") is not True:
            raise ValueError(f"Crossref identity mismatch: {candidate_id}")

        if candidate.get("pmid"):
            url = f"https://pubmed.ncbi.nlm.nih.gov/{candidate['pmid']}/"
            verification_record = {
                "status": "VERIFIED", "system": "PUBMED_NCBI_EUTILITIES", "verifiedDate": DATE,
                "identifierChecked": f"PMID:{candidate['pmid']}; DOI:{candidate['doi'].lower()}",
            }
            attestation_path = None
        else:
            snapshot = attestation(candidate, canonical_id)
            attestation_path = f"docs/governance/source-verification/{canonical_id}.json"
            write_json(ROOT / attestation_path, snapshot)
            url = snapshot["publisherLocator"]
            verification_record = {
                "status": "VERIFIED", "system": "AUTHORITATIVE_BIBLIOGRAPHIC", "verificationVersion": "1.0.0",
                "verifiedDate": DATE, "identifierChecked": f"DOI:{candidate['doi'].lower()}",
                "method": "DOI_REGISTRY_AND_PUBLISHER_ALIGNMENT", "authority": "CROSSREF",
                "registryLocator": snapshot["registryLocator"], "publisherLocator": snapshot["publisherLocator"],
                "verifiedFields": sv.FIELDS, "accessDepth": snapshot["accessDepth"], "conflicts": [],
                "verificationConfidence": "HIGH",
                "provenance": {"path": attestation_path, "contentHash": sv.digest(snapshot), "reviewMethod": snapshot["reviewMethod"], "limitations": snapshot["limitations"]},
            }
        record = {
            "schemaVersion": "1.0.0", "id": canonical_id,
            "citationText": f"{'; '.join(candidate['authors'])}. {candidate['title']}. {candidate['venue']}. {candidate['year']}. doi:{candidate['doi'].lower()}." + (f" PMID:{candidate['pmid']}." if candidate.get("pmid") else ""),
            "title": candidate["title"], "authors": candidate["authors"], "year": candidate["year"],
            "publication": candidate["venue"], "doi": candidate["doi"].lower(), "pmid": candidate.get("pmid"),
            "url": url, "sourceType": candidate["sourceType"], "verification": verification_record,
            "governanceDecisionRecord": DECISION_PATH, "auditId": PROGRAM,
        }
        source_records.append(record)
        registrations.append({
            "candidateSourceId": candidate_id, "canonicalSourceId": canonical_id,
            "verificationRoute": check["verificationRoute"],
            "registryLocator": check["crossrefUrl"], "pubmedLocator": check.get("pubmedUrl"),
            "publisherLocator": publisher_url, "accessDepth": candidate["accessDepth"],
            "approvedRecordDependencies": sorted(remap_record(x) for x in dependencies[candidate_id]["requiredForRecommendedRecordIds"]),
            "overlap": candidate.get("overlap"), "limitations": candidate.get("limitations"),
            "deduplicationOutcome": "NEW_CANONICAL_RECORD_NO_DOI_PMID_TITLE_YEAR_DUPLICATE",
            "registrationStatus": "REGISTERED_FOR_HUMAN_APPROVED_GOVERNED_INACTIVE_RECORD",
        })
    return source_records, registrations


def decision_document(canonical: dict) -> str:
    identity_lines = "\n".join(f"- `{candidate}` → `{canonical_id}`" for candidate, canonical_id in canonical["happeningTypes"].items())
    effect_lines = "\n".join(f"- `{candidate}` → `{canonical_id}`; evidence `{canonical['evidenceAssessments']['EVA-EA-CAND-PSY-LAYER-' + candidate.rsplit('-', 1)[1]]}`" for candidate, canonical_id in canonical["effectAssertions"].items())
    return f"""# Psychological Layer governance decision 001

## Authority

- Decision ID: `{DECISION}`
- Layer program: `{PROGRAM}`
- Candidate scientific baseline: `{BASELINE}`
- Reconciled main: `{RECONCILED_MAIN}`
- Governance recommendation commit: `{RECOMMENDATION_COMMIT}`
- Decision date: `{DATE}`
- Actor class: `authorized human governor`
- Activation authorized: **NO**

This record materializes the explicit human authorization following the independent recommendation pass. The recommendation documents remain the historical advisory analysis. This decision is the human approval authority; the materialization manifest records the canonical implementation.

## Existing Relationships and ledgers

Approved without production implementation: 1 retain as-is, 10 retain V1-incomplete, 57 revision-review-only, 5 retype-review-only, 2 split-review-only, and 36 keep-research-needed. The 64 revision/retype/split proposals remain proposals. No existing production Relationship is changed, superseded, deactivated, retyped, split, or replaced.

The 151 rejection dispositions are approved as durable rejected hypotheses. The 209 research-needed hypotheses remain non-governed questions. A materially different future proposition or evidence base may receive a separate review.

## Governed inactive Relationship and evidence

- `REL-CAND-PSY-LAYER-0001` → `{RELATIONSHIP_ID}`
- `EVA-REL-CAND-PSY-LAYER-0001` → `{RELATIONSHIP_EVIDENCE_ID}`

Repeated encounter with the same factual statement/headline may alter subsequently rated confidence or commitment in that specified proposition under bounded controlled adult tasks. Direction is context-dependent. There is no universal positive polarity, universal dose response, truth/objective-accuracy claim, calibration claim, behavior claim, or unrestricted population/content transfer. Implausibility, veracity cues, task instructions, exact referent, timing, population, nulls, and counterexamples remain explicit.

`{RELATIONSHIP_ID}` and `EA-V1-PSY-LAYER-001` share `{SHARED_CONTRIBUTION}`. They are alternate representations of one exposure contribution and may never be summed as two causal inputs.

## Governed inactive HappeningType identities

{identity_lines}

These 29 records govern reusable operation identities only. They establish no efficacy, legality, ethics, feasibility, practitioner recommendation, numerical model eligibility, or activation.

## Governed inactive EffectAssertions and evidence

{effect_lines}

The exact reviewed Driver target, effect property, direction, timing, population, task/manipulation alignment, boundaries, limitations, source findings, and contribution identity are controlling. Evidence confidence is not effect magnitude. MIXED, SUPPORTS, null, and contrary semantics remain unchanged.

The remaining 23 candidate EffectAssertions remain `RESEARCH_NEEDED / NOT_ELIGIBLE`.

## Sources

Exactly 44 supplemental sources required by the governed records are registered as `{min(SOURCE_MAP.values())}` through `{max(SOURCE_MAP.values())}`. Nine already-canonical sources are reused. DOI/PMID/work-version deduplication, access depth, shared datasets, review/included-study dependence, and preprint/publication relationships remain explicit. Background, rejected, and research-needed-only sources are not registered.

## Preserved blockers

- `BLK-PSY-001` / `ARCH-PSY-LAYER-0001`: normalized feature/dimension-specific representation.
- `BLK-PSY-002` / `ARCH-PSY-LAYER-0002`: PSY-130 situational/enduring meaning versus trait-only timing.
- `BLK-PSY-003`: PSY-003 Belief Strength versus PSY-116 Metacognitive Confidence.

No ontology definition, classification, alias, crosswalk, RDS definition, target semantics, or architecture decision is changed.

## Activation boundary

All 45 newly governed records are `INACTIVE`: 1 Relationship, 29 HappeningTypes, 7 EffectAssertions, and 8 EvidenceAssessments. New `ACTIVE` records = 0. Governance does not authorize quantitative causal execution or practitioner actionability. Activation requires a separate human decision after an independent activation audit.
"""


def authorization(records: list[dict]) -> dict:
    return {
        "decisionId": DECISION, "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "effectiveDate": DATE,
        "authorizedObjects": [{"id": x["id"], "revision": x["revision"], "recordHash": ae.digest(x)} for x in sorted(records, key=lambda x: x["id"])],
        "recordClass": "SCIENTIFIC_RECORD",
    }


def merge_exact(existing: list[dict], additions: list[dict], key: str = "id") -> list[dict]:
    by_id = {row[key]: row for row in existing}
    merged = list(existing)
    for addition in additions:
        found = by_id.get(addition[key])
        if found is not None and found != addition:
            raise ValueError(f"Canonical collision: {addition[key]}")
        if found is None:
            by_id[addition[key]] = addition
            merged.append(addition)
    return merged


def assert_no_source_duplicates(new_sources: list[dict]) -> None:
    old = read(ROOT / "data/sources.json")["sources"] + read(RI_SOURCES)["sources"]
    def norm(value):
        return re.sub(r"[^a-z0-9]", "", str(value or "").casefold())
    for source in new_sources:
        for existing in old:
            if source["id"] == existing["id"]:
                if source != existing:
                    raise ValueError(f"Existing canonical source changed: {source['id']}")
                continue
            text = json.dumps(existing, ensure_ascii=False).casefold()
            if source["doi"] in text or (source.get("pmid") and str(source["pmid"]) == str(existing.get("pmid"))):
                raise ValueError(f"Existing DOI/PMID must be reused rather than reminted: {source['id']} / {existing['id']}")
            if norm(source["title"]) == norm(existing.get("title")) and source["year"] == existing.get("year"):
                raise ValueError(f"Existing title/year must be reused rather than reminted: {source['id']} / {existing['id']}")


def update_advisory_status() -> None:
    # Regenerate through the advisory builder so the historical recommendation
    # stays intact while its post-recommendation status is deterministic.
    import build_psychological_layer_governance_recommendations as advisory
    advisory.main()


def materialize() -> None:
    relationship_candidates, relationship_evidence_candidates, sidecar_candidate, identity_candidates, effect_candidates, effect_evidence_candidates = collect_candidates()
    relationship_candidate = next(x for x in relationship_candidates if x["id"] == "REL-CAND-PSY-LAYER-0001")
    relationship_evidence_candidate = next(x for x in relationship_evidence_candidates if x["id"] == "EVA-REL-CAND-PSY-LAYER-0001")
    if sidecar_candidate is None:
        raise ValueError("Relationship source-finding sidecar unavailable")

    identities = [make_identity(x) for x in sorted(identity_candidates, key=lambda x: x["id"])]
    if len(identities) != 29:
        raise ValueError("Identity authorization set changed")
    effects_by_id = {x["id"]: x for x in effect_candidates}
    assessments_by_object = {x["assertion"]["objectId"]: x for x in effect_evidence_candidates}
    effects, effect_assessments = [], []
    for number in APPROVED_EFFECT_NUMBERS:
        candidate_id = f"EA-CAND-PSY-LAYER-{number:04d}"
        effect, assessment = make_effect(effects_by_id[candidate_id], assessments_by_object[candidate_id])
        effects.append(effect); effect_assessments.append(assessment)
    relationship, relationship_assessment, relationship_sidecar = make_relationship(relationship_candidate, relationship_evidence_candidate, sidecar_candidate)

    canonical = {
        "relationship": {relationship_candidate["id"]: relationship["id"]},
        "happeningTypes": {x["id"]: ht_id(x["id"]) for x in sorted(identity_candidates, key=lambda x: x["id"])},
        "effectAssertions": {f"EA-CAND-PSY-LAYER-{n:04d}": f"EA-V1-PSY-LAYER-{n:03d}" for n in APPROVED_EFFECT_NUMBERS},
        "evidenceAssessments": {"EVA-REL-CAND-PSY-LAYER-0001": relationship_assessment["id"], **{f"EVA-EA-CAND-PSY-LAYER-{n:04d}": f"EVA-AE-V1-PSY-LAYER-{n:03d}" for n in APPROVED_EFFECT_NUMBERS}},
        "sources": SOURCE_MAP,
    }
    write_text(DECISION_DOC, decision_document(canonical))
    new_sources, registrations = make_sources()
    assert_no_source_duplicates(new_sources)
    source_context = ae.Context.repository()
    source_context.source_ids |= {x["id"] for x in new_sources}
    for source in new_sources:
        ri.SchemaSet().validate("source", source)
        sv.validate_source(source)

    # Validate all scientific records in memory before production writes.
    catalog = read(AE_CATALOG)
    catalog["happeningTypes"] = merge_exact(catalog["happeningTypes"], identities)
    catalog["effectAssertions"] = merge_exact(catalog["effectAssertions"], effects)
    catalog["evidenceAssessments"] = merge_exact(catalog["evidenceAssessments"], effect_assessments)
    auth = authorization([*identities, *effects, *effect_assessments])
    catalog["authorizations"] = merge_exact(catalog["authorizations"], [auth], key="decisionId")
    ae.validate_catalog(catalog, source_context)

    relationship_store = read(RI_RELATIONSHIPS)
    relationship_store["relationships"] = merge_exact(relationship_store["relationships"], [relationship])
    evidence_store = read(RI_EVIDENCE)
    evidence_store["evidenceAssessments"] = merge_exact(evidence_store["evidenceAssessments"], [relationship_assessment])
    source_store = read(RI_SOURCES)
    source_store["sources"] = merge_exact(source_store["sources"], new_sources)
    findings_store = read(RI_FINDINGS)
    findings_store["records"] = merge_exact(findings_store["records"], [relationship_sidecar], key="assertionId")
    schemas = ri.SchemaSet()
    ri_catalog = ri.Catalog.synthetic(
        read(ROOT / "data/entities.json"),
        read(ROOT / "data/relationships.json")["relationships"],
        source_context.source_ids,
    )
    relationship_map = dict(ri_catalog.legacy_relationships)
    relationship_map.update({x["id"]: x for x in relationship_store["relationships"]})
    ri.validate_relationship(relationship, ri_catalog, schemas, relationship_map)
    ri.validate_evidence_assessment(relationship_assessment, ri_catalog, schemas)

    write_json(RI_SOURCES, source_store)
    write_json(RI_RELATIONSHIPS, relationship_store)
    write_json(RI_EVIDENCE, evidence_store)
    write_json(RI_FINDINGS, findings_store)
    write_json(AE_CATALOG, catalog)

    source_manifest = {
        "schemaVersion": "1.0.0", "programId": PROGRAM, "governanceDecisionId": DECISION,
        "verificationDate": DATE, "registrationPerformed": True, "registeredCount": 44,
        "canonicalReused": ["SRC-433", "SRC-450", "SRC114", "SRC139", "SRC155", "SRC186", "SRC193", "SRC200", "SRC221"],
        "registrations": registrations,
        "notRegisteredCounts": {"researchNeededOrBackground": 132, "rejectionBackground": 6, "duplicateOverlapping": 2},
        "alignmentRules": [
            "Reviews and included primary studies are not independent replications.",
            "Shared datasets and publication components remain one evidence contribution.",
            "Preprint and published versions remain one work unless explicitly demonstrated otherwise.",
            "Scientific access depth is preserved and bibliographic verification does not upgrade evidence depth.",
            "Source registration adds no scientific evidence, effect magnitude, activation, model, or practitioner authority.",
        ],
        "recordsBlockedBySourceVerification": [],
    }
    write_json(SOURCE_MANIFEST, source_manifest)

    recommendations = read(CANDIDATE / "governance-recommendations.json")
    decision_data = {
        "schemaVersion": "1.0.0", "decisionId": DECISION, "decisionRecord": DECISION_PATH,
        "programId": PROGRAM, "candidateBaseline": BASELINE, "reconciledMain": RECONCILED_MAIN,
        "recommendationCommit": RECOMMENDATION_COMMIT, "effectiveDate": DATE,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "activationAuthorized": False,
        "advisoryCompression": recommendations["compression"],
        "approvedExistingRelationshipCounts": recommendations["existingRelationshipCounts"],
        "approvedLedgerCounts": {"rejectedHypotheses": 151, "researchNeededHypotheses": 209},
        "canonicalIds": canonical,
        "preservedBlockers": ["BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"],
        "sourceRegistration": {"authorizedRequiredOnly": 44, "registered": 44, "blockedRecords": []},
        "materialized": {"relationships": 1, "happeningTypes": 29, "effectAssertions": 7, "evidenceAssessments": 8, "newGoverned": 45, "newInactive": 45, "newActive": 0},
        "productionChangesAuthorized": {"existingRelationships": False, "ontology": False, "architecture": False, "activation": False},
    }
    write_json(DECISION_DATA, decision_data)

    lineage = []
    candidate_lookup = {x["id"]: x for x in [relationship_candidate, relationship_evidence_candidate, *identity_candidates, *[effects_by_id[f"EA-CAND-PSY-LAYER-{n:04d}"] for n in APPROVED_EFFECT_NUMBERS], *[assessments_by_object[f"EA-CAND-PSY-LAYER-{n:04d}"] for n in APPROVED_EFFECT_NUMBERS]]}
    canonical_records = {x["id"]: x for x in [relationship, relationship_assessment, *identities, *effects, *effect_assessments]}
    for candidate_id, candidate_record in sorted(candidate_lookup.items()):
        canonical_id = remap_record(candidate_id)
        lineage.append({
            "candidateId": candidate_id, "candidateRevision": candidate_record["revision"], "candidateHash": ae.digest(candidate_record),
            "canonicalId": canonical_id, "canonicalRevision": canonical_records[canonical_id]["revision"], "canonicalHash": ae.digest(canonical_records[canonical_id]),
            "governanceDecisionId": DECISION, "scientificSemanticsBroadened": False, "activationStatus": "INACTIVE",
        })
    materialization_manifest = {
        "schemaVersion": "1.0.0", "materializationId": "PSYCHOLOGICAL-LAYER-GOVERNANCE-MATERIALIZATION-001",
        "programId": PROGRAM, "candidateBaseline": BASELINE, "reconciledMain": RECONCILED_MAIN,
        "recommendationCommit": RECOMMENDATION_COMMIT, "governanceDecisionId": DECISION, "governanceDecisionRecord": DECISION_PATH,
        "activationAuthorized": False, "productionGraphEligible": False,
        "counts": {"relationships": 1, "happeningTypes": 29, "effectAssertions": 7, "evidenceAssessments": 8, "sources": 44, "newGoverned": 45, "newInactive": 45, "newActive": 0},
        "canonicalIds": canonical, "candidateLineage": lineage,
        "sharedContributions": [{"id": SHARED_CONTRIBUTION, "relationshipId": RELATIONSHIP_ID, "effectAssertionId": "EA-V1-PSY-LAYER-001", "policy": "ONE_CONTRIBUTION_NO_ADDITIVE_COUNT"}],
        "remainingNonGoverned": {"effectAssertions": [f"EA-CAND-PSY-LAYER-{n:04d}" for n in range(1, 31) if n not in APPROVED_EFFECT_NUMBERS], "existingRelationshipResearchNeeded": 36, "revisionProposals": 57, "retypeProposals": 5, "splitProposals": 2, "researchNeededHypotheses": 209},
        "rejectedHypotheses": 151, "preservedBlockers": ["BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"],
        "existingScientificRecordsChanged": 0, "ontologyChanges": 0, "architectureChanges": 0,
        "activeProductionCountsUnchanged": {"drivers": 770, "rds": 41, "entities": 811, "relationships": 457, "causalRelationships": 436},
    }
    write_json(MATERIALIZATION_MANIFEST, materialization_manifest)
    update_advisory_status()
    print("Psychological Layer: 45 GOVERNED/INACTIVE scientific records, 44 sources, zero ACTIVE.")


if __name__ == "__main__":
    materialize()
