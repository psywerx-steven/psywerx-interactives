"""Materialize the one human-approved Informational identity, without effects."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import actions_events_v1 as ae
import relationship_intervention_v1 as ri
import informational_layer_v2 as inf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/INFORMATIONAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/INFORMATIONAL_LAYER"
CATALOG = ROOT / "data/actions-events-v1/catalog.json"
SOURCES = ROOT / "data/relationship-intervention-v1/source-register.json"
DECISION_PATH = "docs/governance/scale-up/INFORMATIONAL_LAYER/INFORMATIONAL_LAYER_GOVERNANCE_DECISION_001.md"
DECISION_ID = "GOV-INFORMATIONAL-LAYER-001-2026-09-20"
PROGRAM_ID = "AUD-INFORMATIONAL-LAYER-AE-V1-20260920-001"
RECOMMENDATION_HEAD = "a86f0449a3f3b817af40c02c2932a696751378e2"
DATE = "2026-09-20"
STAMP = "2026-09-20T12:00:00Z"
HT_ID = "HT-V1-INF-LAYER-001"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def source_records() -> list[dict]:
    # PubMed published-version metadata verified on 2026-09-20. Registration
    # attests to bibliographic identity, not to an effect or evidence depth.
    fields = [
        ("SRC-604", "SRC-CAND-INF-LAYER-013", "Encouraging the resumption of economic activity after COVID-19: Evidence from a large scale-field experiment in China", ["Juan Palacios", "Yichun Fan", "Erez Yoeli", "Jianghao Wang", "Yuchen Chai", "Weizeng Sun", "David G Rand", "Siqi Zheng"], 2022, "Proceedings of the National Academy of Sciences", "10.1073/pnas.2100719119", "35082145"),
        ("SRC-605", "SRC-CAND-INF-LAYER-015", "The impact of descriptive norms on motivation to participate in cancer screening - Evidence from online experiments", ["Christian von Wagner", "Yasemin Hirst", "Jo Waller", "Alex Ghanouni", "Lesley M McGregor", "Robert S Kerrison", "Wouter Verstraete", "Ivo Vlaev", "Monika Sieverding", "Sandro T Stoffel"], 2019, "Patient Education and Counseling", "10.1016/j.pec.2019.04.001", "30975450"),
    ]
    candidate = read(DATA / "candidate-source-registry.json")
    records = []
    for identifier, candidate_id, title, authors, year, publication, doi, pmid in fields:
        row = candidate[candidate_id]
        if row["doi"].lower() != doi or row.get("pmid", pmid) != pmid or row["pmcid"] not in {"PMC8812684", "PMC6686210"}:
            raise ValueError(f"Candidate-source identity conflict: {candidate_id}")
        records.append({
            "schemaVersion": "1.0.0", "id": identifier,
            "citationText": f"{'; '.join(authors)}. {title}. {publication}. {year}. doi:{doi}. PMID:{pmid}.",
            "title": title, "authors": authors, "year": year, "publication": publication,
            "doi": doi, "pmid": pmid, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "sourceType": "JOURNAL_ARTICLE",
            "verification": {"status": "VERIFIED", "system": "PUBMED_NCBI_EUTILITIES", "verifiedDate": DATE,
                             "identifierChecked": f"PMID:{pmid}; DOI:{doi}"},
            "governanceDecisionRecord": DECISION_PATH, "auditId": PROGRAM_ID,
        })
    return records


def make_identity() -> dict:
    candidate = read(DATA / "actions-events-identity-registry.json")["HT-CAND-INF-LAYER-0001"]
    if candidate["lifecycleStatus"] != "REVIEW_READY" or candidate["activationStatus"] != "NOT_ELIGIBLE":
        raise ValueError("Identity candidate is no longer review-ready")
    template = next(row for row in read(CATALOG)["happeningTypes"] if row["id"] == "HT-V1-PSY-LAYER-005")
    record = copy.deepcopy(template)
    record.update({
        "id": HT_ID, "name": candidate["name"], "description": candidate["definition"],
        "identityKey": "single-reference-group-behavior-prevalence-statement",
        "identitySourceIds": ["SRC-604", "SRC-605"], "originLayers": ["INF"],
        "actorOrSourceSystem": "ROLE-MESSAGE-EDITOR", "aliases": [],
        "controlProfiles": [{
            "actorId": "ROLE-MESSAGE-EDITOR", "capabilities": [],
            "conditions": "Identity only; the behavior, referent group, observation window and claimed statistic must be specified. Accuracy, provenance, feasibility, legality and efficacy are not certified.",
            "context": "A single displayed numerical prevalence or frequency statement, without a required comparison to recipient behavior or estimate.",
            "extent": "UNKNOWN", "population": "Specified recipient and reference group",
            "provenance": {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Materialized exact human-approved operation identity", "recordedAt": STAMP,
                           "originReferences": [PROGRAM_ID, candidate["name"], "HT-CAND-INF-LAYER-0001"],
                           "limitations": ["No efficacy, accuracy, practitioner, feasibility or activation inference"]},
        }],
        "provenance": {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Exact materialization of human-approved candidate identity", "recordedAt": STAMP,
                       "originReferences": [PROGRAM_ID, "HT-CAND-INF-LAYER-0001", RECOMMENDATION_HEAD, DECISION_ID],
                       "limitations": ["Operation identity only; no efficacy, truth, behavior, actor feasibility, practitioner use or activation claim"]},
    })
    states = [
        ({"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "CANDIDATE", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "CANDIDATE", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "RESEARCH_NEEDED", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "RESEARCH_NEEDED", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}),
        ({"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}, {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"}),
    ]
    transitions = [{"fromState": before, "toState": after, "actorClass": "AUTOMATED_PROCESS_OR_AI",
                    "rationale": "Exact human approval materialized; activation withheld" if i == 4 else "Preserved non-governed candidate workflow",
                    "timestamp": STAMP, "objectId": HT_ID, "revision": 1,
                    "provenance": f"{PROGRAM_ID}:{RECOMMENDATION_HEAD}:HT-CAND-INF-LAYER-0001:transition-{i}",
                    "governanceDecisionRecord": DECISION_PATH if i == 4 else None,
                    "exactDecisionMaterialization": i == 4} for i, (before, after) in enumerate(states, 1)]
    record["governance"] = {
        "lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE", "blockStatus": "NONE",
        "decisionOutcome": "APPROVED", "authorityBasis": "V1_NATIVE", "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor", "decisionDate": DATE,
        "effectiveVersion": "INFORMATIONAL-LAYER-GOVERNANCE-001",
        "decisionRationale": "Reusable single-statement operation identity only; no effect or activation authorized.",
        "supersedesIds": [], "transitionProvenance": transitions,
    }
    return record


def main() -> None:
    inf.validate_protection()
    catalog = read(CATALOG)
    sources = read(SOURCES)
    if HT_ID in {row["id"] for row in catalog["happeningTypes"]}:
        raise ValueError("Canonical identity already exists; do not rematerialize")
    registered = source_records()
    existing_sources = read(ROOT / "data/sources.json")["sources"] + sources["sources"]
    for row in registered:
        if any(old.get("doi", "").lower() == row["doi"] or old.get("pmid") == row["pmid"] or old["id"] == row["id"] for old in existing_sources):
            raise ValueError(f"Canonical source duplicate: {row['id']}")
        ri.SchemaSet().validate("source", row)
    identity = make_identity()
    decision_text = f"""# Informational Layer governance decision 001

Decision ID: `{DECISION_ID}`
Program ID: `{PROGRAM_ID}`
Candidate baseline: `{inf.BASE_COMMIT}`
Reconciled main: `{inf.BASE_COMMIT}`
Governance recommendation commit: `{RECOMMENDATION_HEAD}`
Decision date: `{DATE}`
Authority: explicit human governor instruction.

The prior governance recommendation is **RECOMMENDED** historical advice. This record is **HUMAN_APPROVED** authority. The source and identity manifests document what was **MATERIALIZED**. No activation is authorized.

Approved existing-Relationship dispositions: 5 retain, 5 retain V1-incomplete, 16 retype-review-only, 12 prior review decisions reused and 12 research-needed. Review-only outcomes do not modify production Relationships. `REL-CAND-INF-LAYER-0001` remains **DEFERRED / KEEP_RESEARCH_NEEDED**, including plans-versus-visits and bundled-feedback limitations; its candidate assessment stays non-governed. Four A&E routes and all five historical INF-F03 candidate effects remain research-needed. Five category-error rejections and five cheap-triage research-needed hypotheses remain durable workflow conclusions.

The one approved identity is `HT-CAND-INF-LAYER-0001` → `{HT_ID}`, a single displayed reference-group prevalence statement. It is distinct from multi-panel `HT-V1-PSY-LAYER-005`. Only reusable identity is approved. No effect, truth, norm change, behavior, feasibility, ethics, practitioner recommendation or activation is established. Sources `SRC-CAND-INF-LAYER-013` and `015` are approved for bibliographic provenance only, registered as `SRC-604` and `SRC-605` after published-version PubMed DOI/PMID verification. `SRC-CAND-INF-LAYER-014` and all eleven INF-F03 candidate-only queue rows remain unregistered and unchanged.

**MATERIALIZED:** 0 Relationships, 1 governed/inactive HappeningType, 0 EffectAssertions, 0 EvidenceAssessments, 0 ACTIVE. The approved record may not be used as evidence of efficacy.

**BLOCKED:** `HYP-INF-F03-H20`, `ARCH-INF-LAYER-0001`, `META-INF-LAYER-0001`; `ASTRA-INF-LAYER-001` remains an escalation question. No INF-013/INF-077 repair, RDS architecture, Network State binding or feature workaround is authorized. The Psychological repetition contribution remains blocked. Production propositions, INF-F03 pilot science, Psychological science and all seven Informational RDS remain unchanged.
"""
    (ROOT / DECISION_PATH).write_text(decision_text, encoding="utf-8", newline="\n")
    catalog["happeningTypes"].append(identity)
    catalog["authorizations"].append({"decisionId": DECISION_ID, "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "effectiveDate": DATE,
        "recordClass": "SCIENTIFIC_RECORD",
        "authorizedObjects": [{"id": HT_ID, "revision": 1, "recordHash": ae.digest(identity)}]})
    context = ae.Context.repository()
    context.source_ids.update(row["id"] for row in registered)
    ae.validate_catalog(catalog, context)
    sources["sources"].extend(registered)
    write(SOURCES, sources)
    write(CATALOG, catalog)
    write(DOCS / "INFORMATIONAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID, "sourceRole": "IDENTITY_PROVENANCE_ONLY_NOT_EFFECT_EVIDENCE",
        "registrations": [{"candidateSourceId": c, "canonicalSourceId": s, "verifiedVia": f"https://pubmed.ncbi.nlm.nih.gov/{p}/",
                            "doi": d, "approvedDependency": HT_ID, "accessDepth": a}
                         for c, s, p, d, a in [
            ("SRC-CAND-INF-LAYER-013", "SRC-604", "35082145", "10.1073/pnas.2100719119", "PUBMED_ABSTRACT_AND_INDEXED_RESULT_EXCERPT"),
            ("SRC-CAND-INF-LAYER-015", "SRC-605", "30975450", "10.1016/j.pec.2019.04.001", "ABSTRACT_AND_SEARCH_EXCERPT")]],
        "excludedCandidateSourceIds": ["SRC-CAND-INF-LAYER-014"],
        "pilotSourceQueuePreserved": 11,
        "caveats": ["Publication verification does not upgrade source access depth or prove efficacy.",
                    "Studies address different populations and outcomes; neither independently verifies the other study's effect.",
                    "Plans and actual visits must not be conflated; comparative feedback is a bundled operation."],
    })
    write(ROOT / "data/actions-events-v1/INFORMATIONAL_LAYER-materialization-manifest.json", {
        "schemaVersion": "1.0.0", "decisionId": DECISION_ID,
        "candidateIdentity": "HT-CAND-INF-LAYER-0001", "canonicalIdentity": HT_ID,
        "newGoverned": {"relationships": 0, "happeningTypes": 1, "effectAssertions": 0, "evidenceAssessments": 0},
        "newActive": 0, "canonicalSources": ["SRC-604", "SRC-605"],
        "recommendationStatus": "HISTORICAL_ADVISORY", "humanDecisionStatus": "APPROVED",
        "materializationStatus": "COMPLETE_INACTIVE", "activationRecommendation": "NONE",
    })


if __name__ == "__main__":
    main()
