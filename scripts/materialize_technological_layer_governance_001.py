"""Materialize the exact human-approved Technological Layer bundle."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import actions_events_v1 as ae
import relationship_intervention_v1 as ri
import source_verification_v1 as sv
import technological_layer_v2 as tech


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/TECHNOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/TECHNOLOGICAL_LAYER"
CATALOG = ROOT / "data/actions-events-v1/catalog.json"
SOURCES = ROOT / "data/relationship-intervention-v1/source-register.json"
DECISION_PATH = "docs/governance/scale-up/TECHNOLOGICAL_LAYER/TECHNOLOGICAL_LAYER_GOVERNANCE_DECISION_001.md"
DECISION_ID = "GOV-TECHNOLOGICAL-LAYER-001-2026-09-22"
RECOMMENDATION_HEAD = "93a98dd8fcb4dc9fa237cbb4ff847fc9bc4c54c5"
RECONCILED_HEAD = "1fdc5c01f7be9003c4a17b23ed3be1e4a19c9761"
DATE = "2026-09-22"
STAMP = "2026-09-22T18:00:00Z"
HT_ID = "HT-V1-TEC-LAYER-001"
EA_ID = "EA-V1-TEC-LAYER-001"
EVA_ID = "EVA-AE-V1-TEC-LAYER-001"
SOURCE_MAP = {
    "SRC-CAND-TEC-LAYER-004": "SRC-613",
    "SRC-CAND-TEC-LAYER-005": "SRC-614",
    "SRC-CAND-TEC-LAYER-013": "SRC-615",
    "SRC-CAND-TEC-LAYER-014": "SRC-616",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def provenance(candidate_id: str, limitations: list[str]) -> dict:
    return {
        "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "method": "Exact mechanical materialization of a human-authorized candidate; no scientific semantic expansion",
        "recordedAt": STAMP,
        "originReferences": [tech.PROGRAM_ID, candidate_id, RECOMMENDATION_HEAD, RECONCILED_HEAD, DECISION_ID],
        "limitations": limitations,
    }


def governance(object_id: str, candidate_id: str, rationale: str) -> dict:
    states = [
        ({"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "CANDIDATE", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "CANDIDATE", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "RESEARCH_NEEDED", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "RESEARCH_NEEDED", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"}),
    ]
    transitions = []
    for number, (before, after) in enumerate(states, 1):
        transitions.append({
            "fromState": before, "toState": after, "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "rationale": "Exact human approval materialized; activation withheld" if number == 4 else "Preserved non-governed candidate workflow",
            "timestamp": STAMP, "objectId": object_id, "revision": 1,
            "provenance": f"{tech.PROGRAM_ID}:{RECOMMENDATION_HEAD}:{candidate_id}:transition-{number}",
            "governanceDecisionRecord": DECISION_PATH if number == 4 else None,
            "exactDecisionMaterialization": number == 4,
        })
    return {
        "lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE", "blockStatus": "NONE",
        "decisionOutcome": "APPROVED", "authorityBasis": "V1_NATIVE", "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor", "decisionDate": DATE,
        "effectiveVersion": "TECHNOLOGICAL-LAYER-GOVERNANCE-001",
        "decisionRationale": rationale, "supersedesIds": [], "transitionProvenance": transitions,
    }


def nonpubmed_verification(source_id: str, doi: str, publisher: str) -> dict:
    path = ROOT / f"docs/governance/source-verification/{source_id}.json"
    snapshot = read(path)
    return {
        "status": "VERIFIED", "system": "AUTHORITATIVE_BIBLIOGRAPHIC", "verificationVersion": "1.0.0",
        "verifiedDate": DATE, "identifierChecked": f"DOI:{doi}", "method": "DOI_REGISTRY_AND_PUBLISHER_ALIGNMENT",
        "authority": "CROSSREF", "registryLocator": snapshot["registryLocator"], "publisherLocator": publisher,
        "verifiedFields": ["title", "authors", "year", "publication", "doi", "sourceType"],
        "accessDepth": "METADATA", "conflicts": [], "verificationConfidence": "HIGH",
        "provenance": {
            "path": path.relative_to(ROOT).as_posix(), "contentHash": sv.digest(snapshot),
            "reviewMethod": snapshot["reviewMethod"], "limitations": snapshot["limitations"],
        },
    }


def source_records() -> list[dict]:
    candidates = read(DATA / "candidate-source-registry.json")
    rows = [
        ("SRC-613", "SRC-CAND-TEC-LAYER-004", ["Wittenberg C", "Epstein Z", "Péloquin-Skulski G", "Berinsky AJ", "Rand DG"], "PNAS Nexus", "40519990", "https://pubmed.ncbi.nlm.nih.gov/40519990/"),
        ("SRC-614", "SRC-CAND-TEC-LAYER-005", ["Gallegos IO", "Shani C", "Shi W", "Bianchi F", "Gainsburg I", "Jurafsky D", "Willer R"], "PNAS Nexus", "41675465", "https://pubmed.ncbi.nlm.nih.gov/41675465/"),
        ("SRC-615", "SRC-CAND-TEC-LAYER-013", ["Tae Hyun Baek", "Jungkeun Kim", "Jeong Hyun Kim"], "International Journal of Advertising", None, "https://www.tandfonline.com/doi/full/10.1080/02650487.2024.2401319"),
        ("SRC-616", "SRC-CAND-TEC-LAYER-014", ["Sue Lim", "Ralf Schmälzle"], "Computers in Human Behavior: Artificial Humans", None, "https://api.elsevier.com/content/article/doi/10.1016%2Fj.chbah.2024.100058"),
    ]
    records = []
    for identifier, candidate_id, authors, publication, pmid, url in rows:
        candidate = candidates[candidate_id]
        verification = (
            {"status": "VERIFIED", "system": "PUBMED_NCBI_EUTILITIES", "verifiedDate": DATE,
             "identifierChecked": f"PMID:{pmid}; DOI:{candidate['doi']}"}
            if pmid else nonpubmed_verification(identifier, candidate["doi"], url)
        )
        citation = f"{'; '.join(authors)}. {candidate['title']}. {publication}. {candidate['year']}. doi:{candidate['doi']}."
        if pmid:
            citation += f" PMID:{pmid}."
        records.append({
            "schemaVersion": "1.0.0", "id": identifier, "citationText": citation,
            "title": candidate["title"], "authors": authors, "year": candidate["year"], "publication": publication,
            "doi": candidate["doi"], "pmid": pmid, "url": url, "sourceType": "JOURNAL_ARTICLE",
            "verification": verification, "governanceDecisionRecord": DECISION_PATH, "auditId": tech.PROGRAM_ID,
        })
    return records


def make_identity(catalog: dict) -> dict:
    candidate = read(DATA / "actions-events-identity-registry.json")["HT-CAND-TEC-LAYER-0001"]
    template = next(row for row in catalog["happeningTypes"] if row["id"] == "HT-V1-ENV-LAYER-001")
    record = copy.deepcopy(template)
    record.update({
        "id": HT_ID, "name": candidate["name"], "description": candidate["definition"],
        "identityKey": "display-ai-generated-process-label-on-specified-synthetic-visual-media",
        "identitySourceIds": ["SRC-613"], "originLayers": ["TEC"], "aliases": [],
        "actorOrSourceSystem": "ROLE-SYSTEM-OR-PLATFORM-OPERATOR",
        "controlProfiles": [{
            "actorId": "ROLE-SYSTEM-OR-PLATFORM-OPERATOR", "capabilities": [], "extent": "UNKNOWN",
            "conditions": "Identity only; exact label text, adjacency, visual item, timing, platform/interface, and recipient exposure must be specified.",
            "context": "A specified synthetic visual media item evaluated with an adjacent AI-generated process label.",
            "population": "Specified recipients",
            "provenance": provenance(candidate["id"], ["No falsity, detection, belief, credibility, behavior, efficacy, recommendation, or activation inference"]),
        }],
        "governance": governance(HT_ID, candidate["id"], "Approved reusable operation identity only; no effect, truth, detection, behavior, efficacy, recommendation, or activation authorized."),
        "provenance": provenance(candidate["id"], ["Operation identity only; synthetic origin is distinct from falsity, belief, credibility, behavior, and efficacy"]),
    })
    return record


def canonical_finding(candidate: dict, number: int, source_id: str) -> dict:
    access = "ABSTRACT" if source_id in {"SRC-613", "SRC-614"} else "METADATA"
    disposition = "NULL_FINDING" if candidate["disposition"] == "NULL" else candidate["disposition"]
    return {
        "id": f"FND-EA-V1-TEC-LAYER-001-{number:03d}", "sourceId": source_id,
        "locator": "Governed candidate sourceFinding; canonical identity independently verified",
        "accessDepth": access, "population": candidate["population"],
        "context": "Specified AI-generated disclosure or authorship-label evaluation",
        "basis": ["EXPERIMENTAL"], "supportedSemantics": ["CAUSAL"], "inputRole": "DIRECT_FINDING",
        "design": candidate["design"], "exposure": candidate["manipulation"], "comparator": "Specified unlabeled or alternate-label condition",
        "measurement": candidate["target"], "timing": candidate["timing"], "result": candidate["result"],
        "disposition": disposition, "quantitativeEstimate": None,
        "uncertainty": ["No portable numerical effect magnitude extracted"],
        "limitations": candidate["limitations"] + ["TIME_SENSITIVE_TECHNOLOGY", "GENERALIZATION_UNCERTAIN"],
        "datasetIds": [candidate["sourceId"]],
        "overlapNotes": "Distinct source identity; medium, label, task, endpoint, and technology-version differences prevent treating findings as interchangeable replication.",
        "nullInterpretation": ({
            "contrast": "AI-model, human-expert, or no authorship label on AI-generated policy text",
            "interpretation": "NO_DETECTED_DIFFERENCE",
            "precisionAssessment": "No equivalence margin or universal-zero precision claim extracted",
            "rationale": "Nonsignificance is retained as a bounded null, not a universal zero.",
        } if candidate["disposition"] == "NULL" else None),
        "provenance": provenance(candidate["id"], ["Candidate extraction preserved; canonical registration does not add evidence or broaden the claim"]),
    }


def make_effect_and_assessment(catalog: dict) -> tuple[dict, dict]:
    candidate = next(x for x in read(DATA / "actions-events-hypotheses.json") if x["id"] == "EA-CAND-TEC-LAYER-0001")
    findings_by_id = {x["id"]: x for x in read(DATA / "source-findings.json")}
    evidence_candidate = read(DATA / "evidence-assessments.json")[0]
    template = next(row for row in catalog["effectAssertions"] if row["id"] == "EA-V1-ENV-LAYER-001")
    effect = copy.deepcopy(template)
    qualifiers = candidate["qualifiers"]
    exclusions = "No truth, detection accuracy, generic correction, text-message, behavior, sharing, durable belief, universal platform, universal AI-label, all-media, or current/future model-version claim."
    effect.update({
        "id": EA_ID, "typeId": HT_ID, "targetKind": "DRIVER", "targetId": "PSY-003", "targetLayers": ["PSY"],
        "claimSemantics": "CAUSAL", "productionMethod": "SYNTHESIS", "property": "LEVEL", "change": "DECREASE",
        "otherSpecified": None, "intendedChange": None, "observedChange": "DECREASE", "knowledgeStatus": "SUPPORTED_EFFECT",
        "scope": {"population": candidate["scope"]["population"], "context": candidate["scope"]["context"],
                  "timing": candidate["scope"]["timing"], "measurement": "Immediate self-reported belief in the specified displayed core claim",
                  "boundaryConditions": candidate["scope"]["boundaries"] + " " + exclusions},
        "mechanism": "No recipient-level mechanism is identified; the operation supplies an explicit production-origin cue adjacent to the evaluated visual item.",
        "mechanismStatus": "UNKNOWN", "mechanisticDriverIds": [],
        "grounding": {"causalIdentificationRationale": "Randomized label contrasts support only the bounded immediate visual-post belief rating; text-policy null and medium/task variation remain explicit.",
                      "derivationEntailed": "NO", "duplicatePropagationControl": None, "representedDriverId": None},
        "contribution": {"groupId": "CONTRIB-TEC-LAYER-AI-LABEL-001", "role": "PRIMARY", "relatedAssertionIds": [],
                         "reconciliation": "One bounded label-to-belief contribution; no credibility, truth-detection, sharing, or downstream propagation may be added."},
        "moderatorLinks": [], "interaction": {"mode": "NONE", "otherEffectIds": [], "evidenceAssessmentIds": []},
        "qualifiers": {"distribution": None, "evaluation": {"criterion": None, "stakeholder": None, "valence": "NOT_EVALUATED"},
                       "prerequisites": ["Exact label, visual item, platform/interface, task, recipient exposure, consent, legality and ethics must be independently specified"],
                       "reach": None, "risks": ["Do not infer falsity, detection accuracy, practitioner actionability, or platform-wide efficacy"],
                       "subgroups": [], "unintendedConsequences": ["Label effects may vary by medium, label, task, platform, population and technology version"]},
        "outcomes": [], "evidenceAssessmentIds": [EVA_ID],
        "uncertainty": ["MIXED evidence", *qualifiers, "Policy-text null", "Medium and label variation"],
        "inferenceProvenance": None,
        "governance": governance(EA_ID, candidate["id"], "Approved exact bounded immediate visual-post belief contrast; MIXED evidence, null boundary, qualifiers and exclusions preserved; activation withheld."),
        "provenance": provenance(candidate["id"], [candidate["claim"], exclusions, *qualifiers, "No numerical magnitude or practitioner eligibility"]),
    })
    candidate_findings = [findings_by_id[x] for x in evidence_candidate["sourceFindingIds"]]
    canonical_sources = ["SRC-613", "SRC-614", "SRC-615", "SRC-616"]
    findings = [canonical_finding(row, i, canonical_sources[i - 1]) for i, row in enumerate(candidate_findings, 1)]
    assessment = {
        "schemaVersion": "1.0.0", "id": EVA_ID, "revision": 1, "recordClass": "SCIENTIFIC_RECORD",
        "provenance": provenance(evidence_candidate["id"], ["MIXED_SUPPORTS_BOUNDED is preserved; governance does not upgrade certainty", *qualifiers]),
        "governance": governance(EVA_ID, evidence_candidate["id"], "Approved MIXED/MODERATE bounded synthesis; policy-text null, medium/task variation and technology sensitivity preserved; activation withheld."),
        "assertion": {"objectType": "EFFECT_ASSERTION", "objectId": EA_ID}, "sourceFindings": findings,
        "synthesis": {
            "sourceFindingIds": [x["id"] for x in findings], "disposition": "MIXED", "evidenceStrength": "MODERATE", "confidence": "MODERATE",
            "rationale": "MIXED_SUPPORTS_BOUNDED: moderate support for an immediate reduction in self-reported belief for specified labeled synthetic visual posts, with no transfer to truth, detection, text messages, behavior, durability, platforms or model versions.",
            "confidenceRationale": "Randomized visual-label findings support the bounded contrast; a policy-text null plus medium, label, task, population, interface and technology-version differences limit confidence.",
            "conflicts": [{"findingId": findings[1]["id"], "dispositionRationale": "The 2026 policy-text experiment found no significant label effect on attitude change or accuracy judgments; this remains a medium/task boundary."},
                          {"findingId": findings[3]["id"], "dispositionRationale": "Source-disclosure effects varied across message evaluations and conditions."}],
            "contraryEvidenceSearch": "ASSESSED",
            "generalizationLimits": ["Adult online survey samples", "Immediate self-report", *qualifiers, exclusions],
            "datasetOverlap": "Distinct studies; media and task differences are not treated as independent same-claim replication.",
        },
        "completeness": {key: "SPECIFIED" for key in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")},
    }
    return effect, assessment


def decision_document() -> str:
    return f"""# Technological Layer governance decision 001

**HUMAN GOVERNANCE DECISION — MATERIALIZED INACTIVE**

- Decision ID: `{DECISION_ID}`
- Audit/program ID: `{tech.PROGRAM_ID}`
- Frozen candidate baseline: `{tech.BASE_COMMIT}`
- Governance recommendation head: `{RECOMMENDATION_HEAD}`
- Reconciled candidate head: `{RECONCILED_HEAD}`
- Decision date: `{DATE}`

The human governor approves 3 retain-as-is, 13 retain V1-incomplete, 31
retype-review-only, 3 revision-review-only, and 22 research-needed existing-edge
dispositions. No production Relationship is changed and no new Relationship is
created.

`HT-CAND-TEC-LAYER-0001` becomes `{HT_ID}`. It identifies display of an explicit
AI-generated process label adjacent to specified synthetic visual media before
or during evaluation. Identity governance establishes no falsity, detection,
belief, credibility, behavior, efficacy, recommendation, or activation.

`EA-CAND-TEC-LAYER-0001` becomes `{EA_ID}`: displaying that label adjacent to a
specified synthetic visual social-media post may reduce immediate self-reported
belief in that post's specified core claim relative to the same unlabeled post
in the represented adult online survey samples. Target is `PSY-003`; property is
`LEVEL`; direction is context-dependent negative. `PLATFORM_SPECIFIC`,
`INTERFACE_SPECIFIC`, `TASK_SPECIFIC`, `TIME_SENSITIVE_TECHNOLOGY`, and
`GENERALIZATION_UNCERTAIN` remain explicit. No truth, accuracy, detection,
behavior, sharing, durability, text-message, universal-platform, universal-label,
all-media, or model-version-general claim is authorized.

`EVA-AE-CAND-TEC-LAYER-0001` becomes `{EVA_ID}` and remains
`MIXED_SUPPORTS_BOUNDED`, strength
`MODERATE_FOR_IMMEDIATE_VISUAL_POST_BELIEF_RATING`, confidence
`MODERATE_WITH_MEDIA_LABEL_AND_TASK_BOUNDARIES`. The 2026 policy-text null and
medium/task variation remain explicit. Governance does not upgrade MIXED.

Sources `SRC-613` through `SRC-616` are registered only for this bundle. The
other ten candidate sources remain unregistered. Registration adds no evidence.

The five A&E routes `HYP-TEC-LAYER-AE-002` through `006` remain research-needed.
`TEC-097`, `TEC-098`, and `TEC-099` remain blocked metadata. Materialization adds
one governed/inactive HappeningType, one governed/inactive EffectAssertion and
one governed/inactive EvidenceAssessment; new ACTIVE = 0. No RDS, Network State,
ontology or architecture change is authorized.
"""


def main() -> None:
    tech.validate_protection()
    catalog, source_store = read(CATALOG), read(SOURCES)
    for identifier, key in ((HT_ID, "happeningTypes"), (EA_ID, "effectAssertions"), (EVA_ID, "evidenceAssessments")):
        if identifier in {x["id"] for x in catalog[key]}:
            raise ValueError(f"Canonical record already exists: {identifier}")
    sources = source_records()
    existing = read(ROOT / "data/sources.json")["sources"] + source_store["sources"]
    for source in sources:
        if any(old["id"] == source["id"] or (source.get("pmid") and old.get("pmid") == source["pmid"]) or (old.get("doi") or "").lower() == source["doi"].lower() for old in existing):
            raise ValueError(f"Canonical source duplicate: {source['id']}")
        ri.SchemaSet().validate("source", source)

    identity = make_identity(catalog)
    effect, assessment = make_effect_and_assessment(catalog)
    catalog["happeningTypes"].append(identity)
    catalog["effectAssertions"].append(effect)
    catalog["evidenceAssessments"].append(assessment)
    authorized = [identity, effect, assessment]
    catalog["authorizations"].append({
        "decisionId": DECISION_ID, "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "effectiveDate": DATE, "recordClass": "SCIENTIFIC_RECORD",
        "authorizedObjects": [{"id": row["id"], "revision": 1, "recordHash": ae.digest(row)} for row in authorized],
    })

    (ROOT / DECISION_PATH).write_text("# Technological Layer governance decision 001\n\nStaged for atomic validation.\n", encoding="utf-8", newline="\n")
    context = ae.Context.repository()
    context.source_ids.update(x["id"] for x in sources)
    ae.validate_catalog(catalog, context)
    for source in sources:
        sv.validate_source(source)
    source_store["sources"].extend(sources)
    (ROOT / DECISION_PATH).write_text(decision_document(), encoding="utf-8", newline="\n")
    write(SOURCES, source_store)
    write(CATALOG, catalog)
    write(DOCS / "TECHNOLOGICAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID, "registeredCount": 4,
        "registrations": [{"candidateSourceId": candidate, "canonicalSourceId": canonical,
                            "approvedDependencies": [HT_ID, EA_ID, EVA_ID], "registrationAddsEvidence": False}
                           for candidate, canonical in SOURCE_MAP.items()],
        "excludedCandidateSourceCount": 10,
        "technologyQualifier": "TIME_SENSITIVE_TECHNOLOGY",
    })
    write(ROOT / "data/actions-events-v1/TECHNOLOGICAL_LAYER-materialization-manifest.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID, "programId": tech.PROGRAM_ID,
        "candidateBaseline": tech.BASE_COMMIT, "recommendationCommit": RECOMMENDATION_HEAD,
        "reconciledCandidateHead": RECONCILED_HEAD,
        "canonicalIds": {"HT-CAND-TEC-LAYER-0001": HT_ID, "EA-CAND-TEC-LAYER-0001": EA_ID,
                         "EVA-AE-CAND-TEC-LAYER-0001": EVA_ID, **SOURCE_MAP},
        "newGoverned": {"relationships": 0, "happeningTypes": 1, "effectAssertions": 1, "evidenceAssessments": 1},
        "newActive": 0, "existingRelationshipsChanged": 0, "ontologyChanges": 0, "architectureChanges": 0,
        "networkStateChanges": 0, "materializationStatus": "COMPLETE_INACTIVE", "activationAuthorized": False,
        "deferredEffects": [f"HYP-TEC-LAYER-AE-{n:03d}" for n in range(2, 7)],
        "preservedBlockedMetadata": ["TEC-097", "TEC-098", "TEC-099"],
    })
    print("Technological Layer: 3 GOVERNED/INACTIVE records, 4 sources, zero ACTIVE.")


if __name__ == "__main__":
    main()
