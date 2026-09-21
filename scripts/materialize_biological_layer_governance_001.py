"""Materialize the one human-approved Biological identity, without effects."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import actions_events_v1 as ae
import biological_layer_v2 as bio
import relationship_intervention_v1 as ri

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/BIOLOGICAL_LAYER"
CATALOG = ROOT / "data/actions-events-v1/catalog.json"
SOURCES = ROOT / "data/relationship-intervention-v1/source-register.json"
DECISION_PATH = "docs/governance/scale-up/BIOLOGICAL_LAYER/BIOLOGICAL_LAYER_GOVERNANCE_DECISION_001.md"
DECISION_ID = "GOV-BIOLOGICAL-LAYER-001-2026-09-21"
PROGRAM_ID = bio.PROGRAM_ID
RECOMMENDATION_HEAD = "2e3c6cf1f2e70ab5570d429d4bf5a259c242b391"
DATE = "2026-09-21"
STAMP = "2026-09-21T12:00:00Z"
HT_ID = "HT-V1-BIO-LAYER-001"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def source_records() -> list[dict]:
    # Published-version identities verified through PubMed/NCBI E-utilities.
    # Registration records identity provenance only and does not govern an effect.
    fields = [
        ("SRC-606", "SRC-CAND-BIO-LAYER-021", "Withdrawal syndrome after the double-blind cessation of caffeine consumption", ["Silverman K", "Evans SM", "Strain EC", "Griffiths RR"], 1992, "The New England Journal of Medicine", "10.1056/nejm199210153271601", "1528206"),
        ("SRC-607", "SRC-CAND-BIO-LAYER-022", "The frequency of caffeine withdrawal in a population-based survey and in a controlled, blinded pilot experiment", ["Dews PB", "Curtis GL", "Hanford KJ", "O'Brien CP"], 1999, "Journal of Clinical Pharmacology", "10.1177/00912709922012024", "10586387"),
        ("SRC-608", "SRC-CAND-BIO-LAYER-023", "Low-dose caffeine physical dependence in humans", ["Griffiths RR", "Evans SM", "Heishman SJ", "Preston KL", "Sannerud CA", "Wolf B", "Woodson PP"], 1990, "The Journal of Pharmacology and Experimental Therapeutics", None, "2262896"),
    ]
    candidates = read(DATA / "candidate-source-registry.json")
    records = []
    for identifier, candidate_id, title, authors, year, publication, doi, pmid in fields:
        candidate = candidates[candidate_id]
        if candidate["pmid"] != pmid or (candidate.get("doi") or "").lower() != (doi or "").lower():
            raise ValueError(f"Candidate-source identity conflict: {candidate_id}")
        citation_doi = f" doi:{doi}." if doi else ""
        record = {
            "schemaVersion": "1.0.0", "id": identifier,
            "citationText": f"{'; '.join(authors)}. {title}. {publication}. {year}.{citation_doi} PMID:{pmid}.",
            "title": title, "authors": authors, "year": year, "publication": publication,
            "doi": doi,
            "pmid": pmid, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "sourceType": "JOURNAL_ARTICLE",
            "verification": {"status": "VERIFIED", "system": "PUBMED_NCBI_EUTILITIES", "verifiedDate": DATE,
                             "identifierChecked": f"PMID:{pmid}" + (f"; DOI:{doi}" if doi else "")},
            "governanceDecisionRecord": DECISION_PATH, "auditId": PROGRAM_ID,
        }
        records.append(record)
    return records


def make_identity() -> dict:
    candidate = read(DATA / "actions-events-identity-registry.json")["HT-CAND-BIO-LAYER-0001"]
    if candidate["status"] != "REVIEW_READY" or candidate["activationStatus"] != "NOT_ELIGIBLE":
        raise ValueError("Identity candidate is no longer review-ready")
    catalog = read(CATALOG)
    template = next(row for row in catalog["happeningTypes"]
                    if row.get("actorOrSourceSystem") == "ROLE-CONSENTED-RESEARCH-TASK-OPERATOR")
    record = copy.deepcopy(template)
    record.update({
        "id": HT_ID, "name": candidate["name"], "description": candidate["identity"],
        "identityKey": "abrupt-cessation-of-habitual-caffeine-intake",
        "identitySourceIds": ["SRC-606", "SRC-607", "SRC-608"], "originLayers": ["BIO"],
        "actorOrSourceSystem": "ROLE-CONSENTED-RESEARCH-TASK-OPERATOR", "aliases": [],
        "domainTags": ["DELIBERATE_INTERVENTION"], "kindTags": ["ACTION"],
        "controlProfiles": [{
            "actorId": "ROLE-CONSENTED-RESEARCH-TASK-OPERATOR", "capabilities": [],
            "conditions": "Identity only; usual caffeine exposure, substitution method, cessation interval, consent, safety and independent clinical or ethical authority must be specified.",
            "context": "A bounded research operation replacing an adult participant's usual daily caffeine intake with caffeine-free matched intake or placebo.",
            "extent": "UNKNOWN", "population": "Adults with specified habitual caffeine intake",
            "provenance": {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Materialized exact human-approved operation identity", "recordedAt": STAMP,
                           "originReferences": [PROGRAM_ID, "HT-CAND-BIO-LAYER-0001"],
                           "limitations": ["No withdrawal severity, fatigue, BIO-066 effect, treatment, feasibility, practitioner use or activation inference"]},
        }],
        "provenance": {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Exact materialization of human-approved candidate identity", "recordedAt": STAMP,
                       "originReferences": [PROGRAM_ID, "HT-CAND-BIO-LAYER-0001", RECOMMENDATION_HEAD, DECISION_ID],
                       "limitations": ["Operation identity only; no efficacy, effect size, treatment, feasibility, practitioner use or activation claim"]},
    })
    states = [
        ({"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "CANDIDATE", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "CANDIDATE", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "RESEARCH_NEEDED", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "RESEARCH_NEEDED", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"}),
    ]
    transitions = [{
        "fromState": before, "toState": after, "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "rationale": "Exact human approval materialized; activation withheld" if i == 4 else "Preserved non-governed candidate workflow",
        "timestamp": STAMP, "objectId": HT_ID, "revision": 1,
        "provenance": f"{PROGRAM_ID}:{RECOMMENDATION_HEAD}:HT-CAND-BIO-LAYER-0001:transition-{i}",
        "governanceDecisionRecord": DECISION_PATH if i == 4 else None,
        "exactDecisionMaterialization": i == 4,
    } for i, (before, after) in enumerate(states, 1)]
    record["governance"] = {
        "lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE", "blockStatus": "NONE",
        "decisionOutcome": "APPROVED", "authorityBasis": "V1_NATIVE", "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor", "decisionDate": DATE,
        "effectiveVersion": "BIOLOGICAL-LAYER-GOVERNANCE-001",
        "decisionRationale": "Reusable caffeine-cessation operation identity only; no effect or activation authorized.",
        "supersedesIds": [], "transitionProvenance": transitions,
    }
    return record


def main() -> None:
    bio.validate_protection()
    catalog, sources = read(CATALOG), read(SOURCES)
    if HT_ID in {row["id"] for row in catalog["happeningTypes"]}:
        raise ValueError("Canonical identity already exists; do not rematerialize")
    registered = source_records()
    existing_sources = read(ROOT / "data/sources.json")["sources"] + sources["sources"]
    for row in registered:
        if any((row.get("doi") and old.get("doi", "").lower() == row["doi"].lower()) or
               old.get("pmid") == row["pmid"] or old["id"] == row["id"] for old in existing_sources):
            raise ValueError(f"Canonical source duplicate: {row['id']}")
        ri.SchemaSet().validate("source", row)
    identity = make_identity()
    decision_text = f"""# Biological Layer governance decision 001

Decision ID: `{DECISION_ID}`
Program ID: `{PROGRAM_ID}`
Frozen baseline: `{bio.BASE_COMMIT}`
Governance recommendation commit: `{RECOMMENDATION_HEAD}`
Decision date: `{DATE}`
Authority: explicit human governor instruction.

The recommendation package is the historical **CANDIDATE RECOMMENDATION**. This record is the **HUMAN APPROVAL**. The source and materialization manifests record what was **MATERIALIZED**. No activation is authorized.

Approved existing-edge dispositions are 11 retain as-is, 9 retain V1-incomplete, 5 revision-review-only and 14 research-needed. The five BIO-F01 B01–B05 revision proposals remain unimplemented; no production Relationship is changed, replaced, deactivated or rewritten. No new Relationship is approved.

`HT-CAND-BIO-LAYER-0001` is approved as `{HT_ID}`, **GOVERNED / INACTIVE**. It is the bounded operation of replacing specified habitual adult caffeine intake with caffeine-free matched intake or placebo for a specified interval. Identity governance establishes no withdrawal severity, fatigue or BIO-066 effect, treatment recommendation, practitioner actionability, feasibility, quantitative execution or activation. Candidate sources 021–023 are registered only as identity provenance after PubMed DOI/PMID verification. Candidate source 020 remains unregistered background.

`EA-CAND-BIO-LAYER-0001` remains **RESEARCH_NEEDED / NOT_ELIGIBLE**. `EVA-AE-CAND-BIO-LAYER-0001` remains candidate-only, **MIXED / NOT_ELIGIBLE**. Endotoxin, iron/fatigue and thyroid/fatigue conclusions remain exactly as recommended. No governed EffectAssertion or EvidenceAssessment is created.

**MATERIALIZED:** 0 Relationships, 1 governed/inactive HappeningType, 0 EffectAssertions, 0 EvidenceAssessments and 0 ACTIVE records.

**BLOCKED:** `ARCH-BIO-LAYER-0001`, `BLK-BIO-RDS-001` and `ASTRA-BIO-LAYER-001` remain unresolved. No RDS definition, derivation, aggregation, causal-source architecture, Network State binding or BIO-003 causal semantics changed. Prior BIO-F01, Psychological and Informational science remains unchanged.
"""
    (ROOT / DECISION_PATH).write_text(decision_text, encoding="utf-8", newline="\n")
    catalog["happeningTypes"].append(identity)
    catalog["authorizations"].append({
        "decisionId": DECISION_ID, "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "effectiveDate": DATE,
        "recordClass": "SCIENTIFIC_RECORD",
        "authorizedObjects": [{"id": HT_ID, "revision": 1, "recordHash": ae.digest(identity)}],
    })
    context = ae.Context.repository()
    context.source_ids.update(row["id"] for row in registered)
    ae.validate_catalog(catalog, context)
    sources["sources"].extend(registered)
    write(SOURCES, sources)
    write(CATALOG, catalog)
    write(DOCS / "BIOLOGICAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID,
        "sourceRole": "IDENTITY_PROVENANCE_ONLY_NOT_EFFECT_EVIDENCE",
        "registrations": [{
            "candidateSourceId": candidate_id, "canonicalSourceId": canonical_id,
            "verifiedVia": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", "doi": doi,
            "approvedDependency": HT_ID, "accessDepth": "PUBMED_METADATA_AND_INDEXED_ABSTRACT",
        } for candidate_id, canonical_id, pmid, doi in [
            ("SRC-CAND-BIO-LAYER-021", "SRC-606", "1528206", "10.1056/nejm199210153271601"),
            ("SRC-CAND-BIO-LAYER-022", "SRC-607", "10586387", "10.1177/00912709922012024"),
            ("SRC-CAND-BIO-LAYER-023", "SRC-608", "2262896", None),
        ]],
        "excludedCandidateSourceIds": ["SRC-CAND-BIO-LAYER-020"],
        "caveats": ["Publication verification does not upgrade access depth or prove efficacy.",
                    "The three sources are not counted as evidence for a governed BIO-066 effect.",
                    "Review/primary-study and symptom-level overlap remain recorded in the candidate package."],
    })
    write(ROOT / "data/actions-events-v1/BIOLOGICAL_LAYER-materialization-manifest.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID,
        "candidateIdentity": "HT-CAND-BIO-LAYER-0001", "canonicalIdentity": HT_ID,
        "newGoverned": {"relationships": 0, "happeningTypes": 1, "effectAssertions": 0, "evidenceAssessments": 0},
        "newActive": 0, "canonicalSources": ["SRC-606", "SRC-607", "SRC-608"],
        "recommendationStatus": "HISTORICAL_ADVISORY", "humanDecisionStatus": "APPROVED",
        "materializationStatus": "COMPLETE_INACTIVE", "activationRecommendation": "NONE",
    })


if __name__ == "__main__":
    main()
