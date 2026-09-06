"""Materialize the authorized INF-F03 governance checkpoint as inactive V1 science."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import actions_events_v1 as ae


ROOT = Path(__file__).resolve().parents[1]
RI_DATA = ROOT / "data" / "relationship-intervention-v1"
AE_DATA = ROOT / "data" / "actions-events-v1"
CANDIDATE = ROOT / "data" / "candidates" / "actions-events-v1" / "INF-F03"
DOCS = ROOT / "docs" / "governance" / "pilots" / "INF-F03"
AUDIT_ID = "AUD-INF-F03-AE-V1-20260906-001"
BASELINE = "164d938bcd4bbd7e8c48c8128cacd6e64ff0287a"
PILOT_HEAD = "ec49f49346a051a9dada2cdf97d0c85e7205e018"
DECISION_ID = "GOV-INF-F03-001-2026-09-06"
DECISION_PATH = "docs/governance/pilots/INF-F03/INF_F03_GOVERNANCE_DECISION_001.md"
EFFECTIVE_DATE = "2026-09-06"
EFFECTIVE_TIMESTAMP = "2026-09-06T20:00:00Z"


def read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def merge_records(path: Path, key: str, records: list[dict]) -> list[dict]:
    existing = read(path)[key] if path.exists() else []
    merged = {record["id"]: record for record in existing}
    merged.update({record["id"]: record for record in records})
    return [merged[identifier] for identifier in sorted(merged)]


def transition(
    object_id: str,
    before: str | None,
    after: str,
    number: int,
    human: bool = False,
) -> dict:
    return {
        "fromState": {
            "lifecycleStatus": before,
            "activationStatus": "NOT_ELIGIBLE",
        },
        "toState": {
            "lifecycleStatus": after,
            "activationStatus": "INACTIVE" if human else "NOT_ELIGIBLE",
        },
        "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "rationale": (
            "Exact materialization of the authorized INF-F03 human decision; activation was explicitly withheld."
            if human
            else "Preserved non-governed candidate workflow from the audited pilot lineage."
        ),
        "timestamp": EFFECTIVE_TIMESTAMP,
        "objectId": object_id,
        "revision": 1,
        "provenance": f"{AUDIT_ID}:{PILOT_HEAD}:transition-{number}",
        "governanceDecisionRecord": DECISION_PATH if human else None,
        "exactDecisionMaterialization": human,
    }


def governed(object_id: str, rationale: str) -> dict:
    return {
        "lifecycleStatus": "GOVERNED",
        "activationStatus": "INACTIVE",
        "blockStatus": "NONE",
        "decisionOutcome": "APPROVED",
        "authorityBasis": "V1_NATIVE",
        "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor",
        "decisionDate": EFFECTIVE_DATE,
        "effectiveVersion": "INF-F03-GOVERNANCE-001",
        "decisionRationale": rationale,
        "supersedesIds": [],
        "transitionProvenance": [
            transition(object_id, None, "CANDIDATE", 1),
            transition(object_id, "CANDIDATE", "RESEARCH_NEEDED", 2),
            transition(object_id, "RESEARCH_NEEDED", "REVIEW_READY", 3),
            transition(object_id, "REVIEW_READY", "GOVERNED", 4, human=True),
        ],
    }


def source_record(
    identifier: str,
    candidate_id: str,
    title: str,
    authors: list[str],
    year: int,
    publication: str,
    doi: str,
    pmid: str,
    source_type: str,
) -> dict:
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "citationText": f"{'; '.join(authors)}. {title}. {publication}. {year}. doi:{doi}. PMID:{pmid}.",
        "title": title,
        "authors": authors,
        "year": year,
        "publication": publication,
        "doi": doi,
        "pmid": pmid,
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "sourceType": source_type,
        "verification": {
            "status": "VERIFIED",
            "system": "PUBMED_NCBI_EUTILITIES",
            "verifiedDate": EFFECTIVE_DATE,
            "identifierChecked": f"PMID:{pmid}; DOI:{doi}",
        },
        "governanceDecisionRecord": DECISION_PATH,
        "auditId": AUDIT_ID,
    }


SOURCE_RECORDS = [
    source_record(
        "SRC-550",
        "SRC-CAND-INF-F03-001",
        "Poor writing, not specialized concepts, drives processing difficulty in legal language",
        ["Martínez E", "Mollica F", "Gibson E"],
        2022,
        "Cognition",
        "10.1016/j.cognition.2022.105070",
        "35257980",
        "CORPUS_ANALYSIS_AND_CONTROLLED_EXPERIMENTS",
    ),
    source_record(
        "SRC-551",
        "SRC-CAND-INF-F03-002",
        "The effects of communicating uncertainty on public trust in facts and numbers",
        ["van der Bles AM", "van der Linden S", "Freeman ALJ", "Spiegelhalter DJ"],
        2020,
        "Proceedings of the National Academy of Sciences of the United States of America",
        "10.1073/pnas.1913678117",
        "32205438",
        "CONTROLLED_SURVEY_EXPERIMENTS",
    ),
    source_record(
        "SRC-552",
        "SRC-CAND-INF-F03-003",
        "The effects of communicating uncertainty around statistics, on public trust",
        ["Kerr J", "van der Bles AM", "Dryhurst S", "Schneider CR", "Chopurian V", "Freeman ALJ", "van der Linden S"],
        2023,
        "Royal Society Open Science",
        "10.1098/rsos.230604",
        "38026007",
        "CONTROLLED_SURVEY_EXPERIMENTS",
    ),
]

SOURCE_MAP = {
    "SRC-CAND-INF-F03-001": "SRC-550",
    "SRC-CAND-INF-F03-002": "SRC-551",
    "SRC-CAND-INF-F03-003": "SRC-552",
}


def source_finding(
    identifier: str,
    source_id: str,
    locator: str,
    population: str,
    design: str,
    exposure: str,
    comparator: str,
    measurement: str,
    result: str,
    disposition: str,
    limitations: list[str],
    dataset_id: str,
) -> dict:
    return {
        "id": identifier,
        "sourceId": source_id,
        "locator": locator,
        "accessDepth": "SELECTED_FULL_TEXT" if source_id in {"SRC-550", "SRC-551"} else "ABSTRACT",
        "population": population,
        "context": exposure,
        "basis": ["EXPERIMENTAL"],
        "supportedSemantics": ["CAUSAL"],
        "inputRole": "DIRECT_FINDING",
        "design": design,
        "exposure": exposure,
        "comparator": comparator,
        "measurement": measurement,
        "timing": "Within the reported experimental exposure and assessment window; no numeric lag or persistence inferred",
        "result": result,
        "disposition": disposition,
        "quantitativeEstimate": None,
        "uncertainty": ["No graph weight or transferable quantitative effect estimate inferred"],
        "limitations": limitations,
        "datasetIds": [dataset_id],
        "overlapNotes": "Findings within this paper are one research program, not independent replications; no review-primary independence count inferred.",
        "nullInterpretation": None,
        "provenance": {
            "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "method": "Structured source finding normalized under the exact human governance decision",
            "recordedAt": EFFECTIVE_TIMESTAMP,
            "originReferences": [AUDIT_ID, PILOT_HEAD, DECISION_ID, source_id],
            "limitations": ["Access depth is recorded exactly; no unreported estimate was reconstructed"],
        },
    }


REL_FINDINGS = [
    source_finding(
        "FND-V1-INF-F03-REL-001-SRC-551",
        "SRC-551",
        "Full text: experimental overview, results, and discussion",
        "Five survey experiments using numerical factual messages",
        "Randomized uncertainty-format survey experiments",
        "Numeric ranges or verbal uncertainty accompanying factual numerical claims",
        "Point estimates or alternative uncertainty formats",
        "Perceived uncertainty and trust in the number/source",
        "Disclosure format changed perceived uncertainty; numeric ranges generally had small or null source-trust effects, while verbal uncertainty sometimes reduced trust.",
        "MIXED",
        ["Trust in the source is not confidence calibration", "One multi-experiment paper is not five independent replications"],
        "DATASET-SRC-551-EXPERIMENTS",
    ),
    source_finding(
        "FND-V1-INF-F03-REL-001-SRC-552",
        "SRC-552",
        "Abstract and bibliographic record",
        "Survey experiments concerning present and projected COVID-19 statistics",
        "Randomized uncertainty-format survey experiments",
        "Numeric range or unquantified verbal uncertainty accompanying statistics",
        "No disclosure",
        "Trustworthiness of the number and source",
        "Numeric uncertainty had minimal source-trust impact; unquantified verbal uncertainty reduced number/source trust in some comparisons.",
        "MIXED",
        ["Present and projected statistics differ", "No universal direction or transferable effect size"],
        "DATASET-SRC-552-EXPERIMENTS",
    ),
]


def make_relationship(workspace: dict) -> tuple[dict, dict]:
    candidate = next(row for row in workspace["passA"]["relationshipCandidates"] if row["id"] == "REL-CAND-INF-F03-001")
    evidence_candidate = next(row for row in workspace["passA"]["evidence"] if row["id"] == "EVA-REL-CAND-INF-F03-001")
    relationship = copy.deepcopy(candidate)
    relationship.update({
        "id": "REL-V1-INF-F03-001",
        "polarity": "CONTEXT_DEPENDENT",
        "functionalForm": {
            "kind": "CONTEXT_DEPENDENT_NON_MONOTONIC",
            "specification": "Direction and magnitude vary by uncertainty type, numeric versus unquantified verbal format, message type, population, and context; no universal positive or negative monotonic polarity is asserted.",
        },
        "mechanism": "Recipients may interpret explicit uncertainty as transparency, appropriate epistemic qualification, or unreliability; the response depends on disclosure format and message/recipient context.",
        "boundaryConditions": "Scoped to factual, scientific, and numerical messages represented in surveyed experimental populations. Numeric ranges can have small or null credibility effects; no credibility-calibration or objective-accuracy claim is included.",
        "evidenceAssessmentIds": ["EVA-V1-INF-F03-REL-001"],
        "sourceIds": ["SRC-551", "SRC-552"],
        "governance": governed("REL-V1-INF-F03-001", "The bounded context-dependent uncertainty-disclosure proposition was approved as modified; activation was explicitly withheld."),
    })
    relationship["applicability"] = {
        "analyticUnit": "MESSAGE_RECIPIENT_EVALUATION",
        "populationOrSystem": "Surveyed populations evaluating factual, scientific, or numerical messages within the registered evidence",
        "context": relationship["boundaryConditions"],
    }
    relationship["compatibility"].update({
        "migrationCompleteness": "COMPLETE",
        "v1Executability": "NOT_EXECUTABLE",
        "blockedFields": ["activationNotAuthorized", "quantitativeExecutionNotAuthorized"],
    })

    evidence = copy.deepcopy(evidence_candidate)
    evidence.update({
        "id": "EVA-V1-INF-F03-REL-001",
        "assertion": {"objectType": "RELATIONSHIP", "objectId": relationship["id"]},
        "sourceIds": ["SRC-551", "SRC-552"],
        "evidenceDisposition": "MIXED",
        "evidenceStrength": "MODERATE",
        "confidence": "MODERATE",
        "evidenceRationale": "SRC-551 and SRC-552 directly test uncertainty-format manipulations. They support a bounded causal effect on perceived source credibility, while preserving small/null numeric-format findings and adverse effects for some unquantified verbal formats. No universal sign, accuracy claim, or credibility-calibration claim is inferred.",
        "conflictingEvidence": {
            "sourceIds": ["SRC-551", "SRC-552"],
            "summary": "Direction and magnitude differ by disclosure format and outcome; numeric ranges often showed small or null source-trust differences, whereas some unquantified verbal formats reduced trust.",
        },
        "population": relationship["applicability"]["populationOrSystem"],
        "context": relationship["boundaryConditions"],
        "studyDesignCharacterizations": [
            {"designType": "EXPERIMENTAL", "specification": "SRC-551: five randomized survey experiments on factual numerical messages"},
            {"designType": "EXPERIMENTAL", "specification": "SRC-552: randomized survey experiments on present/projected statistics"},
        ],
        "quantitativeEstimate": None,
        "uncertainty": ["No universal polarity, graph weight, numeric lag, persistence, or transferable effect magnitude inferred"],
        "limitations": [
            "Surveyed and experimental populations and message types limit generalization",
            "Source credibility is not confidence calibration or objective truth",
            "Results within a paper are not counted as independent replications",
        ],
        "governance": governed("EVA-V1-INF-F03-REL-001", "The exact mixed evidence assessment for the approved bounded Relationship was authorized; activation was explicitly withheld."),
    })
    evidence["reviewProvenance"].update({
        "reviewedAt": EFFECTIVE_TIMESTAMP,
        "reviewedBy": "authorized human governor",
        "sourceSchema": f"{AUDIT_ID}:governance-checkpoint-001-with-source-findings",
    })
    return relationship, evidence


HT_MAP = {
    "HT-CAND-INF-F03-001": "HT-V1-INF-F03-001",
    "HT-CAND-INF-F03-002": "HT-V1-INF-F03-002",
    "HT-CAND-INF-F03-004": "HT-V1-INF-F03-004",
    "HT-CAND-INF-F03-005": "HT-V1-INF-F03-005",
    "HT-CAND-INF-F03-006": "HT-V1-INF-F03-006",
    "HT-CAND-INF-F03-007": "HT-V1-INF-F03-007",
}


def make_happening_types(workspace: dict) -> list[dict]:
    candidates = {row["id"]: row for row in workspace["passB"]["happeningTypes"]}
    records = []
    for candidate_id, canonical_id in HT_MAP.items():
        record = copy.deepcopy(candidates[candidate_id])
        record["id"] = canonical_id
        record["identityKey"] = record["identityKey"].replace("INF-F03-", "INF-F03-GOV-")
        record["identitySourceIds"] = [SOURCE_MAP[source_id] for source_id in record["identitySourceIds"] if source_id in SOURCE_MAP]
        record["governance"] = governed(canonical_id, "The reusable identity, without an efficacy claim, was approved; activation was explicitly withheld.")
        record["provenance"] = {
            "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "method": "Materialized exact approved identity from candidate lineage",
            "recordedAt": EFFECTIVE_TIMESTAMP,
            "originReferences": [AUDIT_ID, candidate_id, PILOT_HEAD, DECISION_ID],
            "limitations": ["Identity governance does not establish any effect or practitioner recommendation"],
        }
        if candidate_id == "HT-CAND-INF-F03-001":
            record["description"] = "Deliberately alter explicitly specified lexical or syntactic surface features while preserving the intended substantive propositions. The identity promises no improvement in comprehension, readability, trust, or total multidimensional complexity."
        elif candidate_id == "HT-CAND-INF-F03-002":
            record["description"] = "Attach justified numeric uncertainty bounds or a range and an interpretation appropriate to a specified numerical estimate; invented precision is outside this identity."
        elif candidate_id == "HT-CAND-INF-F03-004":
            record["kindTags"] = ["EVENT", "EXPOSURE"]
            record["description"] = "Exposure of a message-production task to concurrent multi-talker babble. This is not a deliberate Intervention subset or practitioner recommendation."
        elif candidate_id == "HT-CAND-INF-F03-005":
            record["description"] = "Use a specified automatic text-simplification system/version to rewrite selected textual features. The identity itself makes no efficacy or meaning-fidelity claim."
        elif candidate_id == "HT-CAND-INF-F03-006":
            record["description"] = "Replace under-specified instructional timing or referents with explicit wording while preserving the substantive instruction; not every ambiguous instruction can safely be made more specific."
        elif candidate_id == "HT-CAND-INF-F03-007":
            record["description"] = "Overnight sleep-loss exposure preceding message production. It is a biological exposure/process, not a practitioner recommendation, and establishes no BIO-F01 effect."
        records.append(record)
    return records


def remap_finding(finding: dict, canonical_ea: str, source_id: str, suffix: str) -> dict:
    result = copy.deepcopy(finding)
    result["id"] = f"FND-{canonical_ea}-{suffix}"
    result["sourceId"] = source_id
    result["quantitativeEstimate"] = None
    result["provenance"] = {
        "actorClass": "AUTOMATED_PROCESS_OR_AI",
        "method": "Normalized source finding under exact human governance",
        "recordedAt": EFFECTIVE_TIMESTAMP,
        "originReferences": [AUDIT_ID, PILOT_HEAD, DECISION_ID, source_id],
        "limitations": ["No unreported quantitative estimate or effect dimension inferred"],
    }
    return result


def make_effects_and_evidence(workspace: dict) -> tuple[list[dict], list[dict]]:
    effects_by_id = {row["id"]: row for row in workspace["passB"]["effectAssertions"]}
    evidence_by_assertion = {row["assertion"]["objectId"]: row for row in workspace["passB"]["evidenceAssessments"]}
    effects: list[dict] = []
    assessments: list[dict] = []
    for number in (1, 2):
        candidate_id = f"EA-CAND-INF-F03-{number:03d}"
        canonical_id = f"EA-V1-INF-F03-{number:03d}"
        evidence_id = f"EVA-AE-V1-INF-F03-{number:03d}"
        effect = copy.deepcopy(effects_by_id[candidate_id])
        effect.update({
            "id": canonical_id,
            "typeId": HT_MAP[effect["typeId"]],
            "evidenceAssessmentIds": [evidence_id],
            "governance": governed(canonical_id, "The exact scoped EffectAssertion was approved; activation was explicitly withheld."),
        })
        effect["provenance"] = {
            "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "method": "Materialized exact approved EffectAssertion from candidate lineage",
            "recordedAt": EFFECTIVE_TIMESTAMP,
            "originReferences": [AUDIT_ID, candidate_id, PILOT_HEAD, DECISION_ID],
            "limitations": ["No activation, recommendation eligibility, graph weight, or downstream effect is implied"],
        }
        assessment = copy.deepcopy(evidence_by_assertion[candidate_id])
        assessment.update({
            "id": evidence_id,
            "assertion": {"objectType": "EFFECT_ASSERTION", "objectId": canonical_id},
            "governance": governed(evidence_id, "The exact source findings and synthesis for the approved EffectAssertion were authorized; activation was explicitly withheld."),
        })
        assessment["provenance"] = {
            "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "method": "Normalized source findings and synthesis under exact human governance",
            "recordedAt": EFFECTIVE_TIMESTAMP,
            "originReferences": [AUDIT_ID, candidate_id, PILOT_HEAD, DECISION_ID],
            "limitations": ["No graph weight or unreported numerical precision inferred"],
        }
        if number == 1:
            effect["scope"] = {
                "population": "English legal-text evidence involving specified surface features",
                "context": "Content-preserving revision of named surface-language features only",
                "boundaryConditions": "Meaning and legal-obligation fidelity require specialist/human verification; no comprehension, readability, completeness, contradiction, or whole-construct benefit is inferred.",
                "timing": "Comparison of the specified pre-revision and post-revision message versions",
                "measurement": "MANIPULATED_FEATURE_SCOPE_V1: LEXICAL_LOW_FREQUENCY and/or SYNTACTIC_CENTER_EMBEDDED_CLAUSE; DECREASE applies only to each explicitly named manipulated feature dimension, never to all INF-077 dimensions.",
            }
            effect["mechanism"] = "Replacing explicitly named low-frequency lexical items and/or center-embedded clause structures changes only those named surface-feature dimensions while the intended substantive propositions are held fixed and independently checked."
            effect["mechanismStatus"] = "SPECIFIED"
            effect["qualifiers"]["risks"] = ["Meaning drift", "Legal-obligation drift", "False inference from feature reduction to comprehension or audience fit"]
            effect["qualifiers"]["prerequisites"] = ["Named manipulated feature dimensions", "Content-fidelity specification", "Specialist/human fidelity verification"]
            effect["uncertainty"] = ["Evidence does not establish uniform reduction across the multidimensional INF-077 construct"]

            original = assessment["sourceFindings"][0]
            finding = remap_finding(original, canonical_id, "SRC-550", "SRC-550")
            finding.update({
                "locator": "Abstract and selected full-text experimental summary/discussion",
                "measurement": "Named lexical/syntactic features plus recall and comprehension; reader outcomes are not inherited by this feature-level EffectAssertion",
                "result": "The source identifies low-frequency legal terminology and center-embedded structures as separable surface features and reports processing differences; it does not establish a uniform decrease of all INF-077 dimensions or guarantee fidelity for any rewrite.",
                "disposition": "MIXED",
                "limitations": ["Legal-text and English-language scope", "Feature evidence does not guarantee content or legal-obligation fidelity", "Reader performance is not the target Driver"],
                "datasetIds": ["DATASET-SRC-550-CORPUS-AND-EXPERIMENTS"],
            })
            assessment["sourceFindings"] = [finding]
            assessment["synthesis"].update({
                "sourceFindingIds": [finding["id"]],
                "disposition": "MIXED",
                "evidenceStrength": "MODERATE",
                "confidence": "MODERATE",
                "rationale": "SRC-550 supports manipulation of specifically named lexical and syntactic surface features. Governance is limited to those feature dimensions and does not transfer the reported reader outcomes or imply total multidimensional complexity reduction.",
                "confidenceRationale": "Moderate confidence is limited to named-feature change under content-preserving, fidelity-checked revision; construct-wide and audience-response claims are excluded.",
                "conflicts": [{"findingId": finding["id"], "dispositionRationale": "The source supports feature specificity but does not establish whole-construct reduction or guaranteed semantic fidelity."}],
                "generalizationLimits": ["English legal texts", "Named manipulated features only", "Requires separate fidelity and downstream-outcome assessment"],
                "datasetOverlap": "Corpus and experiments within SRC-550 are one publication and are not counted as independent replications.",
            })
        else:
            effect["scope"] = {
                "population": "Numerical factual claims with a scientifically or statistically justified uncertainty range",
                "context": "Addition of explicit numeric bounds/range and an interpretation appropriate to the estimate",
                "boundaryConditions": "No fabricated interval, false precision, accuracy guarantee, automatic trust benefit, or confidence-calibration benefit; downstream outcomes require independent EffectAssertions.",
                "timing": "Comparison of the specified claim before and after justified uncertainty information is attached",
                "measurement": "Amount and explicitness of justified quantified uncertainty disclosure for the same specified numerical claim",
            }
            effect["mechanism"] = "Adding justified numeric bounds or a range and an appropriate interpretation makes uncertainty information explicitly present in the message."
            effect["mechanismStatus"] = "SPECIFIED"
            effect["qualifiers"]["risks"] = ["False precision", "Misleading interval coverage", "Incorrect interpretation", "Improper inference of downstream trust benefit"]
            effect["qualifiers"]["prerequisites"] = ["Scientifically or statistically justified uncertainty information", "Interpretation appropriate to the estimate"]
            effect["uncertainty"] = ["Downstream credibility and calibration effects are separate and mixed"]

            mapped = []
            for original, source_id in zip(assessment["sourceFindings"], ("SRC-551", "SRC-552")):
                finding = remap_finding(original, canonical_id, source_id, source_id)
                finding.update({
                    "measurement": "Presence and explicitness of quantified uncertainty; downstream trust outcomes retained as separate findings",
                    "result": (
                        "The experimental message manipulation attached numeric ranges and increased explicit uncertainty information; downstream source-trust effects were generally small/null for numeric ranges and differed for verbal formats."
                        if source_id == "SRC-551"
                        else "The experimental message manipulation attached numeric uncertainty ranges; downstream trust effects were minimal for numeric ranges and more adverse for some unquantified verbal statements."
                    ),
                    "disposition": "MIXED",
                    "limitations": ["Manipulation verifies disclosure, not interval correctness", "Downstream trust outcomes do not transfer into this exact target effect"],
                    "datasetIds": [f"DATASET-{source_id}-EXPERIMENTS"],
                })
                mapped.append(finding)
            assessment["sourceFindings"] = mapped
            assessment["synthesis"].update({
                "sourceFindingIds": [finding["id"] for finding in mapped],
                "disposition": "SUPPORTS",
                "evidenceStrength": "MODERATE",
                "confidence": "MODERATE",
                "rationale": "SRC-551 and SRC-552 directly operationalize attaching numeric uncertainty ranges, supporting increased explicit disclosure in the specified claim. Their mixed/null credibility findings are retained but do not negate the exact disclosure-target effect or imply a trust benefit.",
                "confidenceRationale": "Moderate confidence applies only to explicit disclosure under justified-range conditions; correctness, trust, and calibration are separate claims.",
                "conflicts": [
                    {"findingId": finding["id"], "dispositionRationale": "Each finding supports the disclosure manipulation while preserving mixed/null downstream trust outcomes outside this exact target."}
                    for finding in mapped
                ],
                "generalizationLimits": ["Numerical factual claims", "Justified uncertainty only", "No downstream credibility or confidence-calibration inference"],
                "datasetOverlap": "SRC-551 and SRC-552 are separate publication-level research programs; experiments within each paper are not counted as independent replications.",
            })
        assessment["completeness"] = {key: "SPECIFIED" for key in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")}
        effects.append(effect)
        assessments.append(assessment)
    return effects, assessments


def governance_documents() -> tuple[str, str]:
    package = """# INF-F03 human governance decision package

Audit: `AUD-INF-F03-AE-V1-20260906-001`

Frozen baseline: `164d938bcd4bbd7e8c48c8128cacd6e64ff0287a`

Decision: `GOV-INF-F03-001-2026-09-06`
Activation: **withheld**

This package records the authorized decisions. It does not modify any existing governed proposition and does not activate any new record.

## Existing Relationships

| IDs | Decision | Materialization |
|---|---|---|
| REL-RDS-0001, REL-RDS-0002, REL-RDS-0003, REL-RDS-0014, REL-RDS-0015, REL-INF-023, REL-INF-029 | APPROVE RETAIN EXACTLY | Review decision only; no V1 duplicate; noncausal/deprecated semantics preserved |
| REL-TEC-060 | APPROVE RETAIN, V1-INCOMPLETE | Existing enabling-affordance proposition unchanged; no content, dose, lag, magnitude, or universal disclosure inference |
| REL-INF-003, REL-INF-008 | APPROVE RETYPE-REVIEW STATUS ONLY | RESEARCH_NEEDED / NOT_ELIGIBLE; no retype or replacement |
| REL-INF-006, REL-INF-041, REL-INF-046, REL-INF-048 | APPROVE REVISION PROPOSAL ONLY | Existing exact proposal retained; no implementation |
| REL-INF-007, REL-INF-009 | APPROVE CURRENT RESEARCH_NEEDED DISPOSITION | No replacement governed or activated |

## New scientific objects

| Candidate | Decision | Canonical outcome |
|---|---|---|
| REL-CAND-INF-F03-001 | MODIFY / APPROVE AS MODIFIED | `REL-V1-INF-F03-001`, context-dependent/no-universal-sign causal proposition, MIXED/MODERATE/MODERATE, GOVERNED + INACTIVE |
| REL-CAND-INF-F03-002/003/004 | APPROVE CURRENT DISPOSITION ONLY | RESEARCH_NEEDED / NOT_ELIGIBLE |
| New association, temporal, derivational, semantic, moderation, pathway records | APPROVE CURRENT NON-CREATION | None created |
| HT-CAND-INF-F03-001/002/004/005/006/007 | APPROVE | Canonical `HT-V1-INF-F03-*` identities, GOVERNED + INACTIVE; identity is not efficacy |
| HT-CAND-INF-F03-003 | APPROVE CURRENT DISPOSITION ONLY | RESEARCH_NEEDED / NOT_ELIGIBLE |
| EA-CAND-INF-F03-001 | MODIFY / APPROVE AS MODIFIED | `EA-V1-INF-F03-001`, DECREASE limited by machine-readable measurement scope to named lexical/syntactic dimensions, GOVERNED + INACTIVE |
| EA-CAND-INF-F03-002 | APPROVE | `EA-V1-INF-F03-002`, justified quantified disclosure → INF-015, GOVERNED + INACTIVE; no trust/calibration inheritance |
| EA-CAND-INF-F03-003/004/005/006/007 | APPROVE CURRENT DISPOSITION ONLY | RESEARCH_NEEDED / NOT_ELIGIBLE |

## Hypotheses

- **REJECTED:** H01, H02, H03, H05, H06, H10, H11, H14, H15, H18, H19.
- **RESEARCH_NEEDED:** H04, H07, H08, H09, H12, H13, H16, H17.
- **BLOCKED_NEEDS_GOVERNANCE_INPUT:** H20. No INF-013/INF-077 definition, classification, metadata, or crosswalk was changed.

## Activation and production boundary

All twelve newly governed scientific records are `INACTIVE`. New `ACTIVE` records = 0. Existing active counts remain 456 Relationships total / 435 causal. No application, model, recommendation, ontology classification, canonical V3 proposition, SRC-429, or SRC-444 changed.
"""
    decision = """# INF-F03 governance decision 001

## Authority and scope

- Decision ID: `GOV-INF-F03-001-2026-09-06`
- Audit ID: `AUD-INF-F03-AE-V1-20260906-001`
- Frozen baseline: `164d938bcd4bbd7e8c48c8128cacd6e64ff0287a`
- Pilot PR: `#18`
- Pilot head before governance: `ec49f49346a051a9dada2cdf97d0c85e7205e018`
- Decision date: `2026-09-06`
- Actor class: `authorized human governor`
- Authorization basis: the explicit human instruction for this checkpoint
- Activation authorized: **no**

This decision governs only the exact scientific identities, proposition, effects, evidence, and source findings listed below. It does not alter existing governed propositions, resolve ontology fields, start another Family, or authorize model/recommendation/application changes.

## Existing corpus decisions

Retain unchanged: `REL-RDS-0001`, `REL-RDS-0002`, `REL-RDS-0003`, `REL-RDS-0014`, `REL-RDS-0015`, `REL-INF-023`, `REL-INF-029`, and V1-incomplete `REL-TEC-060`. Their current authority and causal-traversal treatment do not change.

Retype-review only, not implemented: `REL-INF-003`, `REL-INF-008`. Revision proposals only, not implemented: `REL-INF-006`, `REL-INF-041`, `REL-INF-046`, `REL-INF-048`. Current `RESEARCH_NEEDED` disposition retained for `REL-INF-007`, `REL-INF-009`.

## Exact governed-inactive records

### Relationship and evidence

- `REL-CAND-INF-F03-001` → `REL-V1-INF-F03-001`
- `EVA-REL-CAND-INF-F03-001` → `EVA-V1-INF-F03-REL-001`

The proposition is: explicit uncertainty disclosure can alter perceived source credibility, with direction and magnitude depending on uncertainty type, numeric versus unquantified verbal format, message type, population, and context. It has no universal monotonic polarity. Evidence is `MIXED`, strength `MODERATE`, confidence `MODERATE`. Numeric formats' small/null findings, factual/scientific/numerical scope, and surveyed/experimental population limits remain explicit. Credibility calibration and objective accuracy are excluded.

### HappeningType identities

- `HT-CAND-INF-F03-001` → `HT-V1-INF-F03-001`
- `HT-CAND-INF-F03-002` → `HT-V1-INF-F03-002`
- `HT-CAND-INF-F03-004` → `HT-V1-INF-F03-004`
- `HT-CAND-INF-F03-005` → `HT-V1-INF-F03-005`
- `HT-CAND-INF-F03-006` → `HT-V1-INF-F03-006`
- `HT-CAND-INF-F03-007` → `HT-V1-INF-F03-007`

Identity governance implies no effect. Multi-talker babble and overnight sleep loss are non-deliberate exposure/process identities and are not practitioner-actionable. Automatic rewriting has no identity-level efficacy or fidelity claim.

### EffectAssertions and evidence

- `EA-CAND-INF-F03-001` → `EA-V1-INF-F03-001`; evidence `EVA-AE-CAND-INF-F03-001` → `EVA-AE-V1-INF-F03-001`
- `EA-CAND-INF-F03-002` → `EA-V1-INF-F03-002`; evidence `EVA-AE-CAND-INF-F03-002` → `EVA-AE-V1-INF-F03-002`

For EA-001, `LEVEL / DECREASE` applies only to machine-readable `LEXICAL_LOW_FREQUENCY` and/or `SYNTACTIC_CENTER_EMBEDDED_CLAUSE` feature scope. It is not a whole-INF-077 decrease and confers no comprehension, readability, completeness, contradiction, or fidelity claim. For EA-002, justified quantified bounds increase explicit disclosure in INF-015 only; accuracy, trust, and calibration require separate assertions.

All twelve root scientific records above are `GOVERNED + INACTIVE`. No Occurrence, moderation assertion, CausalPathway, or other new Relationship is governed.

## Selective sources

`SRC-CAND-INF-F03-001/002/003` are registered as `SRC-550/551/552`. The other eleven supplemental candidates remain noncanonical because they only support background, rejected, blocked, or research-needed work. `SRC-429` and `SRC-444` remain byte-identical.

## Non-governed and hypothesis dispositions

Relationships `REL-CAND-INF-F03-002/003/004`, `HT-CAND-INF-F03-003`, Effects `EA-CAND-INF-F03-003/004/005/006/007`, all existing-edge review proposals, H04/H07/H08/H09/H12/H13/H16/H17, and H20 remain non-governed/NOT_ELIGIBLE. H20 remains blocked.

Rejected pilot hypotheses are H01/H02/H03/H05/H06/H10/H11/H14/H15/H18/H19 for the reasons recorded in the pilot package: derivational duplication, calculation dependence, shared-input or temporal-independence failure, wrong semantic type, unsupported causal generalization, or direct-RDS targeting.

## Future review triggers

Activation needs a separate authorized human decision after source/evidence reconciliation, graph and actionability simulation, and complete checkpoint validation. Any change to the scientific scope, polarity, feature dimensions, target, or identity requires new governance.
"""
    return package, decision


def materialize() -> None:
    workspace = read(CANDIDATE / "workspace.json")
    relationship, relationship_evidence = make_relationship(workspace)
    happening_types = make_happening_types(workspace)
    effects, ae_evidence = make_effects_and_evidence(workspace)

    write_json(RI_DATA / "source-register.json", {
        "schemaVersion": "1.0.0",
        "sources": merge_records(RI_DATA / "source-register.json", "sources", SOURCE_RECORDS),
    })
    write_json(RI_DATA / "relationships.json", {
        "schemaVersion": "1.0.0",
        "relationships": merge_records(RI_DATA / "relationships.json", "relationships", [relationship]),
    })
    write_json(RI_DATA / "evidence-assessments.json", {
        "schemaVersion": "1.0.0",
        "evidenceAssessments": merge_records(RI_DATA / "evidence-assessments.json", "evidenceAssessments", [relationship_evidence]),
    })

    relationship_finding_store = {
        "schemaVersion": "1.0.0",
        "auditId": AUDIT_ID,
        "governanceDecisionId": DECISION_ID,
        "records": [{
            "assertionId": relationship["id"],
            "evidenceAssessmentId": relationship_evidence["id"],
            "governanceDecisionRecord": DECISION_PATH,
            "sourceFindings": REL_FINDINGS,
        }],
    }
    write_json(RI_DATA / "relationship-source-findings.json", relationship_finding_store)

    catalog = read(AE_DATA / "catalog.json")
    for key, records in {
        "happeningTypes": happening_types,
        "effectAssertions": effects,
        "evidenceAssessments": ae_evidence,
    }.items():
        merged = {record["id"]: record for record in catalog[key]}
        merged.update({record["id"]: record for record in records})
        catalog[key] = [merged[identifier] for identifier in sorted(merged)]
    authorized = [*happening_types, *effects, *ae_evidence]
    authorization = {
        "decisionId": DECISION_ID,
        "decisionRecord": DECISION_PATH,
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR",
        "effectiveDate": EFFECTIVE_DATE,
        "authorizedObjects": [
            {"id": record["id"], "revision": record["revision"], "recordHash": ae.digest(record)}
            for record in sorted(authorized, key=lambda row: row["id"])
        ],
        "recordClass": "SCIENTIFIC_RECORD",
    }
    authorizations = {record["decisionId"]: record for record in catalog["authorizations"]}
    authorizations[DECISION_ID] = authorization
    catalog["authorizations"] = [authorizations[identifier] for identifier in sorted(authorizations)]
    write_json(AE_DATA / "catalog.json", catalog)

    source_queue = read(CANDIDATE / "source-registration-queue.json")
    for row in source_queue:
        if row["id"] in SOURCE_MAP:
            row["registrationPerformed"] = True
            row["registrationStatus"] = "CANONICALIZED_FOR_GOVERNED_INACTIVE_RECORD"
            row["canonicalDuplicateId"] = SOURCE_MAP[row["id"]]
            row["canonicalDuplicateIds"] = [SOURCE_MAP[row["id"]]]
            row["metadataStatus"] = "CANONICAL_BIBLIOGRAPHY_VERIFIED"
            if row["id"] == "SRC-CAND-INF-F03-001":
                row["authors"] = "Eric Martínez; Francis Mollica; Edward Gibson"
    write_json(CANDIDATE / "source-registration-queue.json", source_queue)

    registration_manifest = {
        "schemaVersion": "1.0.0",
        "auditId": AUDIT_ID,
        "governanceDecisionId": DECISION_ID,
        "verificationDate": EFFECTIVE_DATE,
        "supplementalSourcesEvaluated": 14,
        "registeredCount": 3,
        "duplicateCount": 0,
        "rejectedOrUnverifiedCount": 0,
        "registrations": [
            {
                "candidateSourceId": candidate_id,
                "canonicalSourceId": source_id,
                "deduplicationOutcome": "NEW_CANONICAL_RECORD_NO_IDENTIFIER_DUPLICATE",
                "verificationStatus": "VERIFIED_VIA_PUBMED_IDENTIFIER_AND_BIBLIOGRAPHY",
                "governedRecordsSupported": (
                    ["HT-V1-INF-F03-001", "EA-V1-INF-F03-001"] if source_id == "SRC-550"
                    else ["REL-V1-INF-F03-001", "HT-V1-INF-F03-002", "EA-V1-INF-F03-002"]
                ),
            }
            for candidate_id, source_id in SOURCE_MAP.items()
        ],
        "notRegistered": [
            {
                "candidateSourceId": row["id"],
                "reason": "Used only for background, rejected, blocked, or RESEARCH_NEEDED work; no governed record requires canonical registration at this checkpoint.",
            }
            for row in source_queue if row["id"] not in SOURCE_MAP
        ],
        "unchangedCanonicalSources": ["SRC-429", "SRC-444"],
        "recordsBlockedBySourceVerification": [],
    }
    write_json(DOCS / "INF_F03_SOURCE_REGISTRATION_MANIFEST.json", registration_manifest)

    rejected = ["H01", "H02", "H03", "H05", "H06", "H10", "H11", "H14", "H15", "H18", "H19"]
    research_needed = ["H04", "H07", "H08", "H09", "H12", "H13", "H16", "H17"]
    lineage = [
        {"objectType": "RELATIONSHIP", "candidateId": "REL-CAND-INF-F03-001", "canonicalId": relationship["id"], "evidenceCandidateId": "EVA-REL-CAND-INF-F03-001", "evidenceCanonicalId": relationship_evidence["id"]},
        *[
            {"objectType": "HAPPENING_TYPE", "candidateId": candidate_id, "canonicalId": canonical_id}
            for candidate_id, canonical_id in HT_MAP.items()
        ],
        *[
            {"objectType": "EFFECT_ASSERTION", "candidateId": f"EA-CAND-INF-F03-{number:03d}", "canonicalId": f"EA-V1-INF-F03-{number:03d}", "evidenceCandidateId": f"EVA-AE-CAND-INF-F03-{number:03d}", "evidenceCanonicalId": f"EVA-AE-V1-INF-F03-{number:03d}"}
            for number in (1, 2)
        ],
    ]
    materialization_manifest = {
        "schemaVersion": "1.0.0",
        "materializationId": "INF-F03-GOVERNANCE-MATERIALIZATION-001",
        "auditId": AUDIT_ID,
        "frozenScientificBaseline": BASELINE,
        "pilotHeadBeforeGovernance": PILOT_HEAD,
        "governanceDecisionId": DECISION_ID,
        "governanceDecisionRecord": DECISION_PATH,
        "effectiveDate": EFFECTIVE_DATE,
        "activationAuthorized": False,
        "productionGraphEligible": False,
        "candidateLineage": lineage,
        "governedInactiveCounts": {"relationships": 1, "happeningTypes": 6, "effectAssertions": 2, "evidenceAssessments": 3, "totalScientificRecords": 12, "sourceFindings": 5},
        "newActiveRecords": 0,
        "remainingNonGoverned": {
            "relationships": ["REL-CAND-INF-F03-002", "REL-CAND-INF-F03-003", "REL-CAND-INF-F03-004"],
            "happeningTypes": ["HT-CAND-INF-F03-003"],
            "effectAssertions": [f"EA-CAND-INF-F03-{number:03d}" for number in range(3, 8)],
            "revisionAndRetypeProposals": ["REL-INF-003", "REL-INF-008", "REL-INF-006", "REL-INF-041", "REL-INF-046", "REL-INF-048"],
            "researchNeededHypotheses": research_needed,
            "blockedHypotheses": ["H20"],
        },
        "rejectedHypotheses": rejected,
        "activeProductionCounts": {"drivers": 770, "rds": 41, "entities": 811, "relationships": 456, "causalRelationships": 435},
    }
    write_json(AE_DATA / "INF-F03-materialization-manifest.json", materialization_manifest)

    audit_manifest_path = DOCS / "INF_F03_AUDIT_MANIFEST.json"
    audit_manifest = read(audit_manifest_path)
    audit_manifest.update({
        "governanceDecision": DECISION_ID,
        "noScientificHumanDecision": False,
        "newGoverned": 12,
        "newActive": 0,
        "governanceCheckpoint": {
            "decisionRecord": "INF_F03_GOVERNANCE_DECISION_001.md",
            "pilotHeadBeforeGovernance": PILOT_HEAD,
            "activationAuthorized": False,
            "governedInactiveRecords": 12,
            "governedSourceFindings": 5,
        },
        "sourceRegistration": {"evaluated": 14, "registered": 3, "duplicates": 0, "unverified": 0, "blockedRecords": 0},
    })
    audit_manifest["documents"] = sorted(set(audit_manifest.get("documents", [])) | {
        "INF_F03_GOVERNANCE_DECISION_001.md",
        "INF_F03_SOURCE_REGISTRATION_MANIFEST.json",
    })
    write_json(audit_manifest_path, audit_manifest)

    package, decision = governance_documents()
    write_text(DOCS / "INF_F03_GOVERNANCE_DECISION_PACKAGE.md", package)
    write_text(DOCS / "INF_F03_GOVERNANCE_DECISION_001.md", decision)

    write_json(AE_DATA / "catalog.json", catalog)


def main() -> int:
    materialize()
    print(f"Materialized {DECISION_ID}")
    print("  Governed inactive Relationship: 1")
    print("  Governed inactive HappeningTypes: 6")
    print("  Governed inactive EffectAssertions: 2")
    print("  Governed inactive EvidenceAssessments: 3")
    print("  Governed sourceFindings: 5")
    print("  New active records: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
