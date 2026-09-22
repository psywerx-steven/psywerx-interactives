"""Materialize the exact human-approved Physical / Environmental bundle."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import actions_events_v1 as ae
import physical_environmental_layer_v2 as env
import relationship_intervention_v1 as ri

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/PHYSICAL_ENVIRONMENTAL_LAYER"
CATALOG = ROOT / "data/actions-events-v1/catalog.json"
SOURCES = ROOT / "data/relationship-intervention-v1/source-register.json"
DECISION_PATH = "docs/governance/scale-up/PHYSICAL_ENVIRONMENTAL_LAYER/PHYSICAL_ENVIRONMENTAL_LAYER_GOVERNANCE_DECISION_001.md"
DECISION_ID = "GOV-PHYSICAL-ENVIRONMENTAL-LAYER-001-2026-09-21"
RECOMMENDATION_HEAD = "ffc733b4811ff76b2228eedd955779719f3a13af"
DATE = "2026-09-21"
STAMP = "2026-09-21T18:00:00Z"
HT_ID = "HT-V1-ENV-LAYER-001"
EA_ID = "EA-V1-ENV-LAYER-001"
EVA_ID = "EVA-AE-V1-ENV-LAYER-001"
SOURCE_MAP = {
    "SRC-CAND-ENV-LAYER-014": "SRC-609",
    "SRC-CAND-ENV-LAYER-015": "SRC-610",
    "SRC-CAND-ENV-LAYER-016": "SRC-611",
    "SRC-CAND-ENV-LAYER-017": "SRC-612",
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
        "originReferences": [env.PROGRAM_ID, candidate_id, RECOMMENDATION_HEAD, DECISION_ID],
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
            "provenance": f"{env.PROGRAM_ID}:{RECOMMENDATION_HEAD}:{candidate_id}:transition-{number}",
            "governanceDecisionRecord": DECISION_PATH if number == 4 else None,
            "exactDecisionMaterialization": number == 4,
        })
    return {
        "lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE", "blockStatus": "NONE",
        "decisionOutcome": "APPROVED", "authorityBasis": "V1_NATIVE", "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor", "decisionDate": DATE,
        "effectiveVersion": "PHYSICAL-ENVIRONMENTAL-LAYER-GOVERNANCE-001",
        "decisionRationale": rationale, "supersedesIds": [], "transitionProvenance": transitions,
    }


def source_records() -> list[dict]:
    fields = [
        ("SRC-609", "SRC-CAND-ENV-LAYER-014", "The influence of a walk in nature on human resting brain activity: a randomized controlled trial.", ["McDonnell AS", "Strayer DL"], 2024, "Scientific Reports", "10.1038/s41598-024-78508-x", "39516236"),
        ("SRC-610", "SRC-CAND-ENV-LAYER-015", "Walking in nature may improve affect but not cognition.", ["Trammell JP", "Harriger JA", "Krumrei-Mancuso EJ"], 2023, "Frontiers in Psychology", "10.3389/fpsyg.2023.1258378", "38250104"),
        ("SRC-611", "SRC-CAND-ENV-LAYER-016", "Effects of Outdoor Walking on Positive and Negative Affect: Nature Contact Makes a Big Difference.", ["Legrand FD", "Jeandet P", "Beaumont F", "Polidori G"], 2022, "Frontiers in Behavioral Neuroscience", "10.3389/fnbeh.2022.901491", "35726335"),
        ("SRC-612", "SRC-CAND-ENV-LAYER-017", "Impact of Exposure to Natural and Built Environments on Positive and Negative Affect: A Systematic Review and Meta-Analysis.", ["Yao W", "Chen F", "Wang S", "Zhang X"], 2021, "Frontiers in Public Health", "10.3389/fpubh.2021.758457", "34900906"),
    ]
    candidates = read(DATA / "candidate-source-registry.json")
    records = []
    for identifier, candidate_id, title, authors, year, publication, doi, pmid in fields:
        candidate = candidates[candidate_id]
        if candidate["pmid"] != pmid or candidate["doi"].lower() != doi or candidate["title"] != title:
            raise ValueError(f"Candidate-source identity conflict: {candidate_id}")
        records.append({
            "schemaVersion": "1.0.0", "id": identifier,
            "citationText": f"{'; '.join(authors)}. {title} {publication}. {year}. doi:{doi}. PMID:{pmid}.",
            "title": title, "authors": authors, "year": year, "publication": publication,
            "doi": doi, "pmid": pmid, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "sourceType": "JOURNAL_ARTICLE",
            "verification": {"status": "VERIFIED", "system": "PUBMED_NCBI_EUTILITIES", "verifiedDate": DATE,
                             "identifierChecked": f"PMID:{pmid}; DOI:{doi}"},
            "governanceDecisionRecord": DECISION_PATH, "auditId": env.PROGRAM_ID,
        })
    return records


def make_identity(catalog: dict) -> dict:
    candidate = read(DATA / "actions-events-identity-registry.json")["HT-CAND-ENV-LAYER-0001"]
    if candidate["status"] != "REVIEW_READY" or candidate["activationStatus"] != "NOT_ELIGIBLE":
        raise ValueError("ENV identity candidate is no longer review-ready")
    template = next(row for row in catalog["happeningTypes"] if row["id"] == "HT-V1-BIO-LAYER-001")
    record = copy.deepcopy(template)
    record.update({
        "id": HT_ID, "name": candidate["name"], "description": candidate["identity"],
        "identityKey": "specified-low-intensity-natural-outdoor-walk",
        "identitySourceIds": ["SRC-609", "SRC-610", "SRC-611"], "originLayers": ["ENV"],
        "aliases": [], "actorOrSourceSystem": "ROLE-CONSENTED-RESEARCH-TASK-OPERATOR",
        "controlProfiles": [{
            "actorId": "ROLE-CONSENTED-RESEARCH-TASK-OPERATOR", "capabilities": [], "extent": "UNKNOWN",
            "conditions": "Identity only; route, duration, distance, pace and relevant physical conditions must be specified. Independent consent, safety, ethics, feasibility and practitioner authority remain required.",
            "context": "A bounded low-intensity walk through a defined natural outdoor setting.",
            "population": "Specified research participants",
            "provenance": provenance("HT-CAND-ENV-LAYER-0001", ["No mood, cognition, stress, health, feasibility, recommendation, generalization or activation inference"]),
        }],
        "governance": governance(HT_ID, "HT-CAND-ENV-LAYER-0001", "Approved reusable natural-setting walk operation identity only; no effect or activation authorized."),
        "provenance": provenance("HT-CAND-ENV-LAYER-0001", ["Operation identity only; efficacy, feasibility, recommendation and activation are not established"]),
    })
    return record


def finding(candidate: dict, number: int, source_id: str, disposition: str, basis: list[str], comparator: str, measurement: str, overlap: str) -> dict:
    return {
        "id": f"FND-EA-V1-ENV-LAYER-001-{number:03d}", "sourceId": source_id,
        "locator": candidate["locator"], "accessDepth": "ABSTRACT", "population": candidate["population"],
        "context": "Specified natural versus built or urban walking/exposure comparison",
        "basis": basis, "supportedSemantics": ["CAUSAL"], "inputRole": "DIRECT_FINDING",
        "design": candidate["design"], "exposure": candidate["exposure"], "comparator": comparator,
        "measurement": measurement, "timing": "Immediate post-exposure or post-walk assessment in the studied session",
        "result": candidate["result"], "disposition": disposition, "quantitativeEstimate": None,
        "uncertainty": ["No common causal coefficient or portable effect magnitude extracted"],
        "limitations": [candidate["limitations"]], "datasetIds": [candidate["datasetGroup"]],
        "overlapNotes": overlap, "nullInterpretation": None,
        "provenance": provenance(candidate["id"], ["Governance does not authorize activation, quantitative execution or practitioner actionability"]),
    }


def make_effect_and_assessment() -> tuple[dict, dict]:
    candidate = read(DATA / "candidate-proposition-registry.json")["EA-CAND-ENV-LAYER-0001"]
    assessment_candidate = read(DATA / "evidence-assessments.json")[0]
    candidate_findings = {row["id"]: row for row in read(DATA / "source-findings.json")}
    template = next(row for row in read(CATALOG)["effectAssertions"] if row["id"] == "EA-V1-PSY-LAYER-001")
    effect = copy.deepcopy(template)
    exclusions = "No enduring mood, cognition, attention, memory, stress physiology, clinical benefit, behavior, dose-response, general nature-exposure, universal setting transfer, component mechanism or practitioner recommendation claim."
    effect.update({
        "id": EA_ID, "typeId": HT_ID, "targetKind": "DRIVER", "targetId": "PSY-050", "targetLayers": ["PSY"],
        "claimSemantics": "CAUSAL", "productionMethod": "SYNTHESIS", "property": "LEVEL", "change": "INCREASE",
        "otherSpecified": None, "intendedChange": None, "observedChange": "INCREASE", "knowledgeStatus": "SUPPORTED_EFFECT",
        "scope": {
            "population": "Healthy adult and predominantly young-adult or student samples in specified field settings",
            "context": "Specified low-intensity natural outdoor walk compared with a time/distance-matched urban or built-setting walk; the natural route is a multisensory package.",
            "timing": "Immediate post-walk self-report in the studied session",
            "measurement": "Immediate self-reported positive affect or mood-valence component; not cognition, attention, memory, stress physiology or behavior",
            "boundaryConditions": exclusions,
        },
        "mechanism": "No component mechanism is identified; route vegetation, water, traffic, surfaces and other multisensory conditions may jointly differ.",
        "mechanismStatus": "UNKNOWN", "mechanisticDriverIds": [],
        "grounding": {"causalIdentificationRationale": "Randomized and controlled natural-versus-built walking comparisons support only the bounded immediate affect contrast; heterogeneity and package differences remain explicit.", "derivationEntailed": "NO", "duplicatePropagationControl": None, "representedDriverId": None},
        "contribution": {"groupId": "CONTRIB-ENV-LAYER-NATURE-WALK-001", "role": "PRIMARY", "relatedAssertionIds": [], "reconciliation": "One bounded operation-to-mood contribution; no component or downstream propagation may be inferred."},
        "moderatorLinks": [], "interaction": {"mode": "NONE", "otherEffectIds": [], "evidenceAssessmentIds": []},
        "qualifiers": {"distribution": None, "evaluation": {"criterion": None, "stakeholder": None, "valence": "NOT_EVALUATED"},
                       "prerequisites": ["Consent, safety, feasibility, accessibility, legality, ethics and context applicability NOT_ASSESSED"],
                       "reach": None, "risks": ["Do not infer health treatment or practitioner actionability"], "subgroups": [],
                       "unintendedConsequences": ["Setting and walking packages may not transfer across populations or environments"]},
        "outcomes": [], "evidenceAssessmentIds": [EVA_ID],
        "uncertainty": ["MIXED evidence", "High setting heterogeneity", "Young-adult/student sampling", "Exercise contribution", "Review/primary-study overlap"],
        "inferenceProvenance": None,
        "governance": governance(EA_ID, "EA-CAND-ENV-LAYER-0001", "Approved exact bounded immediate positive mood-valence contrast; MIXED evidence and all exclusions preserved; activation withheld."),
        "provenance": provenance("EA-CAND-ENV-LAYER-0001", [exclusions, "No numerical effect magnitude or practitioner eligibility"]),
    })
    ids = candidate["sourceFindingIds"]
    findings = [
        finding(candidate_findings[ids[0]], 1, "SRC-609", "SUPPORTS", ["EXPERIMENTAL"], "Time/distance-matched urban walk", "Immediate self-reported affect; neural measure is not the target", "Primary randomized trial; not independent of later reviews if included"),
        finding(candidate_findings[ids[1]], 2, "SRC-610", "SUPPORTS", ["EXPERIMENTAL"], "Urban outdoor and indoor treadmill walks", "Positive/negative affect; the cognition null is retained as an explicit boundary", "Primary experiment; cognition null is not a null mood finding"),
        finding(candidate_findings[ids[2]], 3, "SRC-611", "MIXED", ["EXPERIMENTAL"], "Urban walk and no-exercise control", "Positive and negative affect", "Both walking groups improved negative affect; exercise contribution remains"),
        finding(candidate_findings[ids[3]], 4, "SRC-612", "MIXED", ["EVIDENCE_SYNTHESIS"], "Built-environment exposure", "Positive and negative affect", "Review overlaps primary paradigms and is not independent replication"),
    ]
    assessment = {
        "schemaVersion": "1.0.0", "id": EVA_ID, "revision": 1, "recordClass": "SCIENTIFIC_RECORD",
        "provenance": provenance("EVA-AE-CAND-ENV-LAYER-0001", ["MIXED_SUPPORTS_BOUNDED is preserved; governance does not upgrade certainty"]),
        "governance": governance(EVA_ID, "EVA-AE-CAND-ENV-LAYER-0001", "Approved MIXED/MODERATE bounded synthesis; nulls, comparator improvements, heterogeneity and overlap preserved; activation withheld."),
        "assertion": {"objectType": "EFFECT_ASSERTION", "objectId": EA_ID}, "sourceFindings": findings,
        "synthesis": {
            "sourceFindingIds": [row["id"] for row in findings], "disposition": "MIXED", "evidenceStrength": "MODERATE", "confidence": "MODERATE",
            "rationale": "MIXED_SUPPORTS_BOUNDED: immediate positive-affect signal under specified natural-versus-built walking comparisons, without cognition, durability, health, behavior or component-mechanism transfer.",
            "confidenceRationale": "Randomized primary studies support the bounded contrast, while comparator improvement, exercise contribution, young samples, high heterogeneity and overlapping synthesis limit confidence.",
            "conflicts": [
                {"findingId": findings[2]["id"], "dispositionRationale": "Both walking groups improved some affect outcomes, so no universal nature-only benefit is inferred."},
                {"findingId": findings[3]["id"], "dispositionRationale": "Extreme heterogeneity and high risk of bias prevent upgrading MIXED to SUPPORTS."},
            ],
            "contraryEvidenceSearch": "ASSESSED",
            "generalizationLimits": ["Studied adult settings", "Immediate self-report", "Natural route as multisensory package", exclusions],
            "datasetOverlap": "PMID 34900906 synthesizes overlapping experimental paradigms and is not counted as independent replication.",
        },
        "completeness": {key: "SPECIFIED" for key in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")},
    }
    if assessment_candidate["disposition"] != "MIXED_SUPPORTS_BOUNDED":
        raise ValueError("Candidate evidence disposition changed")
    return effect, assessment


def main() -> None:
    env.validate_protection()
    catalog, source_store = read(CATALOG), read(SOURCES)
    for identifier, collection in ((HT_ID, "happeningTypes"), (EA_ID, "effectAssertions"), (EVA_ID, "evidenceAssessments")):
        if identifier in {row["id"] for row in catalog[collection]}:
            raise ValueError(f"Canonical record already exists: {identifier}")
    sources = source_records()
    existing = read(ROOT / "data/sources.json")["sources"] + source_store["sources"]
    for source in sources:
        if any(old["id"] == source["id"] or old.get("pmid") == source["pmid"] or (old.get("doi") or "").lower() == source["doi"] for old in existing):
            raise ValueError(f"Canonical source duplicate: {source['id']}")
        ri.SchemaSet().validate("source", source)
    identity = make_identity(catalog)
    effect, assessment = make_effect_and_assessment()
    catalog["happeningTypes"].append(identity)
    catalog["effectAssertions"].append(effect)
    catalog["evidenceAssessments"].append(assessment)
    authorized = [identity, effect, assessment]
    catalog["authorizations"].append({
        "decisionId": DECISION_ID, "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "effectiveDate": DATE, "recordClass": "SCIENTIFIC_RECORD",
        "authorizedObjects": [{"id": row["id"], "revision": 1, "recordHash": ae.digest(row)} for row in authorized],
    })
    # Lifecycle validation requires the exact decision path to resolve before
    # any production store is written. The complete durable record replaces
    # this staging marker after all in-memory schema checks pass.
    (ROOT / DECISION_PATH).write_text(
        "# Physical / Environmental Layer governance decision 001\n\nStaged for atomic schema validation.\n",
        encoding="utf-8", newline="\n",
    )
    context = ae.Context.repository()
    context.source_ids.update(row["id"] for row in sources)
    ae.validate_catalog(catalog, context)
    source_store["sources"].extend(sources)

    decision = f"""# Physical / Environmental Layer governance decision 001

Decision ID: `{DECISION_ID}`  
Program ID: `{env.PROGRAM_ID}`  
Frozen baseline: `{env.BASE_COMMIT}`  
Governance recommendation commit: `{RECOMMENDATION_HEAD}`  
Decision date: `{DATE}`  
Authority: explicit human governor instruction.

The candidate package is the historical **RECOMMENDATION**. This record is **HUMAN APPROVED** authority. The manifests identify the exact **MATERIALIZED** records. **ACTIVATION IS NOT AUTHORIZED.**

Approved existing-Relationship dispositions are 1 retain as-is, 31 retain V1-incomplete, 2 prior revision-review-only, 4 retype-review-only and 9 research-needed. `REL-ENV-001`, `014`, `023` and `035` remain unimplemented proposals. No production Relationship changes and no new Relationship is created.

`HT-CAND-ENV-LAYER-0001` becomes `{HT_ID}`, a bounded low-intensity walk of specified duration and route through a defined natural outdoor setting, with relevant physical conditions recorded. Identity governance establishes no effect, feasibility, recommendation, generalization or activation.

`EA-CAND-ENV-LAYER-0001` becomes `{EA_ID}`. A specified low-intensity natural outdoor walk, compared with a time/distance-matched urban or built-setting walk, may increase immediate self-reported positive affect or mood valence (`PSY-050`, `LEVEL`, context-dependent positive) in studied adult settings. The natural route is a multisensory package. No enduring mood, cognition, attention, memory, stress physiology, clinical benefit, behavior, dose response, general nature-exposure, universal setting transfer, component mechanism or practitioner recommendation claim is authorized.

`EVA-AE-CAND-ENV-LAYER-0001` becomes `{EVA_ID}`, **MIXED_SUPPORTS_BOUNDED**, strength **MODERATE_FOR_IMMEDIATE_POSITIVE_AFFECT**, confidence **MODERATE_WITH_SETTING_HETEROGENEITY**. The cognition null in PMID 38250104, urban-comparator improvement, exercise contribution, young/student samples, high heterogeneity and review/primary-study overlap remain explicit. Governance does not upgrade MIXED to SUPPORTS.

Sources `SRC-609` through `SRC-612` register exact PubMed/DOI identities only for this bundle. PMID 34900906 is an overlapping synthesis, not independent replication. The other 14 ENV candidate sources remain unregistered.

**MATERIALIZED:** 0 Relationships, 1 governed/inactive HappeningType, 1 governed/inactive EffectAssertion, 1 governed/inactive EvidenceAssessment and 0 ACTIVE records. No ontology, RDS, architecture or Network State change is authorized.
"""
    (ROOT / DECISION_PATH).write_text(decision, encoding="utf-8", newline="\n")
    write(SOURCES, source_store)
    write(CATALOG, catalog)
    write(DOCS / "PHYSICAL_ENVIRONMENTAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID, "registeredCount": 4,
        "registrations": [{"candidateSourceId": c, "canonicalSourceId": s, "pmid": next(x["pmid"] for x in sources if x["id"] == s),
                           "doi": next(x["doi"] for x in sources if x["id"] == s), "approvedDependencies": [HT_ID, EA_ID, EVA_ID],
                           "accessDepth": "PUBMED_ABSTRACT", "registrationAddsEvidence": False} for c, s in SOURCE_MAP.items()],
        "overlap": "SRC-612 / PMID 34900906 is an overlapping review and is not independent replication.",
        "excludedCandidateSourceCount": 14,
    })
    write(ROOT / "data/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER-materialization-manifest.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID, "programId": env.PROGRAM_ID,
        "candidateBaseline": env.BASE_COMMIT, "recommendationCommit": RECOMMENDATION_HEAD,
        "canonicalIds": {"HT-CAND-ENV-LAYER-0001": HT_ID, "EA-CAND-ENV-LAYER-0001": EA_ID,
                         "EVA-AE-CAND-ENV-LAYER-0001": EVA_ID, **SOURCE_MAP},
        "newGoverned": {"relationships": 0, "happeningTypes": 1, "effectAssertions": 1, "evidenceAssessments": 1},
        "newActive": 0, "existingRelationshipsChanged": 0, "ontologyChanges": 0, "architectureChanges": 0,
        "materializationStatus": "COMPLETE_INACTIVE", "activationAuthorized": False,
        "deferredEffects": ["HYP-ENV-LAYER-AE-002", "HYP-ENV-LAYER-AE-003", "HYP-ENV-LAYER-AE-004"],
    })
    print("Physical / Environmental: 3 GOVERNED/INACTIVE records, 4 sources, zero ACTIVE.")


if __name__ == "__main__":
    main()
