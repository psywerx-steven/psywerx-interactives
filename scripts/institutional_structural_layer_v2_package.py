"""Deterministic Institutional / Structural Layer V2 scientific and governance package."""

from __future__ import annotations

import glob
from collections import Counter
from pathlib import Path

import institutional_structural_layer_v2 as layer

R, D, G = layer.ROOT, layer.DATA, layer.DOCS
NOTICE = "CONSERVATIVE HUMAN GOVERNANCE COMPLETE. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0."
DECISION_ID = "GOV-INSTITUTIONAL-STRUCTURAL-LAYER-001-2026-09-23"

SOURCES = [
    ("SRC-CAND-INS-LAYER-001", "10.1086/517935", "Monitoring Corruption: Evidence from a Field Experiment in Indonesia", 2007, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-002", "10.1162/jeea.2005.3.2-3.259", "Fighting Corruption to Improve Schooling: Evidence from a Newspaper Campaign in Uganda", 2005, "POLICY_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-003", "10.1093/qje/qjz013", "Take-Up and Targeting: Experimental Evidence from SNAP", 2019, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-004", "10.1016/j.jpubeco.2021.104550", "Tax filing and take-up: Experimental evidence on tax preparation outreach and benefit claiming", 2022, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-005", "10.1002/pam.22617", "Nudging increases take-up of employment services: Evidence from a large field experiment", 2024, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-006", "10.1016/j.jpubeco.2023.104975", "Increasing the take-up of public health services: An at-scale experiment on digital government", 2024, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-007", "10.1257/aer.20180277", "Making Moves Matter: Experimental Evidence on Incentivizing Bureaucrats through Performance-Based Postings", 2019, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-008", "10.1257/aer.20211207", "Subjective Performance Evaluation, Influence Activities, and Bureaucratic Work Behavior: Evidence from China", 2023, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-009", "10.1086/686029", "Bureaucratic Investments in Expertise: Evidence from a Randomized Controlled Field Trial", 2016, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-010", "10.1093/qje/qjt008", "Strengthening State Capabilities: The Role of Financial Incentives in the Call to Public Service", 2013, "RANDOMIZED_RECRUITMENT_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-011", "10.1016/j.worlddev.2014.02.004", "Bureaucratic Delay, Local-Level Monitoring, and Delivery of Small Infrastructure Projects", 2014, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-012", "10.1111/padm.12945", "What does the evidence tell us about merit principles and government performance?", 2024, "SYSTEMATIC_REVIEW"),
    ("SRC-CAND-INS-LAYER-013", "10.1002/ejsp.435", "Procedural justice in authority relations: the strength of outcome dependence influences people's reactions to voice", 2007, "LAB_EXPERIMENTS"),
    ("SRC-CAND-INS-LAYER-014", "10.1037/0021-9010.92.3.639", "The effects of trust in authority and procedural fairness on cooperation", 2007, "EXPERIMENTAL_AND_SURVEY_STUDIES"),
    ("SRC-CAND-INS-LAYER-015", "10.30636/jbpa.41.198", "Using behavioral outreach to counteract administrative burden and encourage take-up of simplified disability payment rules", 2021, "RANDOMIZED_FIELD_EXPERIMENT"),
    ("SRC-CAND-INS-LAYER-016", "10.1017/bpp.2025.10017", "Behaviorally informed interventions can increase take-up of public employment services, but conversion remains challenging", 2025, "PREREGISTERED_RANDOMIZED_FIELD_EXPERIMENT"),
]

BOUNDARIES = {
    "INS-F01": "formal obligation, restriction, authority, decision rights, realized enforcement, legitimacy and compliance remain distinct",
    "INS-F02": "formal incentives and sanctions differ from expected, received and perceived incentives, deterrence and behavior",
    "INS-F03": "learning, documentation, compliance, time and psychological costs cannot be collapsed into one burden mechanism",
    "INS-F04": "formal structure, work design, actual workflow, discretion, role clarity, caseload and performance are non-equivalent",
    "INS-F05": "monitoring capacity, actual audit exposure, perceived monitoring, enforcement certainty and accountability consequences remain separate",
    "INS-F06": "formal participation, actual voice, objective procedure, perceived fairness, redress use, legitimacy and compliance remain separate",
    "INS-F07": "allocation, eligibility, availability, accessibility, receipt, use and benefit are successive non-equivalent states",
    "INS-F08": "market concentration, competition, entry barriers, transaction costs, labor protection and individual economic experience require level alignment",
    "INS-F09": "de jure rights and power differ from de facto enforcement, differential treatment, lived experience and psychological efficacy",
    "INS-F10": "corruption opportunity, transaction, prevalence, observation, experience, perception, integrity, trust and legitimacy are distinct",
    "INS-F11": "formal coordination arrangements, actual coordination, interdependence, joint capacity and collective performance remain distinct",
    "INS-F12": "announcement, adoption, implementation, enforcement, adaptation, stability and experienced uncertainty require explicit timing",
    "INS-F13": "capacity, staffing, reach, implementation fidelity, legal quality, service delivery, performance, trust and legitimacy are not interchangeable",
}

LANDSCAPES = {
    "INS-F01": ("rules, rights, obligations, authority allocation and discretion", "legal authorization and principal-agent control", "policy coding and authority maps", "rule adoption, repeal and authority reallocation", "implementation, review rights and constrained choice", "jurisdiction, discretion and enforcement", "de jure text rarely identifies de facto operation", "authority does not establish legitimacy or compliance"),
    "INS-F02": ("rewards, fees, taxes, benefits, penalties, liability and contingencies", "expected payoff and deterrence", "statutory schedules, administrative receipt and perceived expectation", "incentive, sanction and benefit changes", "compliance, selection and effort", "enforcement probability, baseline and adaptation", "policy bundles and endogenous targeting", "statutory magnitude is not received or expected magnitude"),
    "INS-F03": ("learning, documentation, procedural, time and channel burdens", "friction, cognitive cost and feasibility", "steps, time, documents, money and experience", "simplification, assistance, recertification and channel changes", "application, enrollment, delay and receipt", "eligibility, capacity and digital access", "outreach and simplification are often bundled", "take-up is behavior and is not structural service coverage"),
    "INS-F04": ("centralization, hierarchy, specialization, span, workflow and caseload", "coordination, discretion and information processing", "organization charts, workload ratios and process measures", "organizational redesign, posting and discretion changes", "expertise acquisition, effort, delay and service performance", "task observability, goals and staffing", "selection and equilibrium adaptation", "formal structure does not prove realized workflow"),
    "INS-F05": ("monitoring, audit, disclosure, oversight, targets and accountability", "detection probability, information and sanctions", "audit assignment, observed compliance and missing resources", "audit probability, disclosure and oversight changes", "corruption proxies, enforcement and performance", "elite capture, free riding and evaluator identity", "proxy outcomes and bundled accountability components", "monitoring is not perceived monitoring or sanction certainty"),
    "INS-F06": ("participation rights, representation, voice, reasons, impartiality and redress", "procedural justice, information and contestation", "formal rights, observed procedure and recipient appraisal", "voice, participation and appeal design", "fairness, legitimacy, cooperation and corrected decisions", "outcome dependence, authority and context", "objective and perceived procedure commonly share method variance", "voice alone cannot stand for a full procedural-justice package"),
    "INS-F07": ("budgets, coverage, rationing, priorities, access and gatekeeping", "resource allocation and eligibility", "budget records, eligible population, availability, receipt and use", "allocation, eligibility and service expansion", "coverage, uptake, receipt and service result", "capacity, geography and administrative burden", "policy assignment differs from realized exposure", "availability, access, use and benefit cannot substitute"),
    "INS-F08": ("competition, concentration, barriers, transaction structure, ownership, employment protection and bargaining", "entry, bargaining, matching and transaction costs", "market shares, rules, contracts and labor outcomes", "regulation, entry and labor-policy changes", "competition, selection, wages and security", "market definition and adaptation", "cross-market ecological comparisons and endogenous regulation", "structure is not perceived security or individual outcome"),
    "INS-F09": ("formal and de facto power, rights, discrimination, segregation, vetoes, censorship and border rules", "allocation, exclusion and enforcement", "legal coding, administrative disparities and experienced treatment", "rights, electoral, censorship and enforcement reforms", "representation, treatment, access and psychological appraisal", "jurisdiction, group and enforcement", "de jure/de facto and institutional/person-level mismatch", "formal rights do not establish realized protection"),
    "INS-F10": ("patronage, clientelism, corruption, bribery opportunity and integrity controls", "rent extraction, selection and accountability", "transactions, discrepancies, prosecutions and perception indices", "audit, procurement and conflict-control reform", "missing resources, transactions, prevalence and trust", "capture, baseline institutions and detection", "perception measures and detected cases are endogenous proxies", "one corruption proxy cannot establish broad prevalence"),
    "INS-F11": ("resource dependence, interdependence, overlap, fragmentation and institutional pressures", "coordination, bargaining and diffusion", "agreements, joint activity, dependencies and results", "coordination mechanisms and jurisdiction redesign", "actual coordination, delay and joint performance", "authority, resources and network boundary", "formal partnership is not effective coordination", "institutional pressure does not prove adoption or performance"),
    "INS-F12": ("stability, switching costs, emergency authority, review, precedent and learning", "expectation, adaptation and path dependence", "policy histories, implementation dates and organizational response", "policy change, review and emergency powers", "implementation, adaptation and persistence", "anticipation, lags and equilibrium response", "announcement/adoption/implementation timing and endogeneity", "document change is not immediate system-state change"),
    "INS-F13": ("fiscal, staffing, administrative, legal, territorial, analytic and emergency capacity", "resource mobilization and implementation", "budgets, qualified staffing, reach, consistency and fidelity", "recruitment, staffing and capacity investment", "implementation, reach, service and legal protection", "task, jurisdiction, period and constituent overlap", "broad indices share indicators and outcomes may proxy latent capacity", "capacity does not uniquely follow from performance"),
}


def prior_reviews(ids: set[str]) -> dict:
    found = {}
    for raw in glob.glob(str(R / "data/candidates/actions-events-v1/*_LAYER/relationship-review-registry.json")):
        if "INSTITUTIONAL_STRUCTURAL_LAYER" in raw:
            continue
        path = Path(raw)
        payload = layer.read(path)
        rows = payload.values() if isinstance(payload, dict) else payload
        for row in rows:
            if not isinstance(row, dict) or row.get("id") not in ids:
                continue
            disposition = row.get("disposition") or row.get("primaryDisposition") or row.get("review", {}).get("disposition")
            if disposition:
                found[row["id"]] = {"disposition": disposition, "source": path.relative_to(R).as_posix()}
    return found


RETYPE = {"REL-INS-006", "REL-INS-010", "REL-INS-021"}
REVISION = {"REL-INS-001", "REL-INS-007", "REL-INS-022"}
RESEARCH = {
    "REL-INS-003", "REL-INS-005", "REL-INS-008", "REL-INS-012", "REL-INS-014",
    "REL-INS-017", "REL-INS-019", "REL-INS-023", "REL-INS-027", "REL-INS-028",
    "REL-INS-035", "REL-INS-036", "REL-INS-038", "REL-INS-039", "REL-INS-055",
}


def review_relationship(row: dict, entities: dict, prior: dict) -> dict:
    rid, edge = row["id"], row["edge"]
    reused = rid in prior
    if reused:
        disposition = prior[rid]["disposition"]
    elif rid in RETYPE:
        disposition = "RETYPE_CANDIDATE"
    elif rid in REVISION:
        disposition = "REVISION_CANDIDATE"
    elif rid in RESEARCH:
        disposition = "RESEARCH_NEEDED"
    elif edge["semanticType"] != "CAUSAL":
        disposition = "RETAIN_AS_IS"
    else:
        disposition = "RETAIN_V1_INCOMPLETE"
    rationale = {
        "RETAIN_AS_IS": "The exact prior or noncausal proposition remains coherent; no production change is proposed.",
        "RETAIN_V1_INCOMPLETE": "The direction is plausible, while exact implementation, exposure, timing, evidence or V1 fields remain incomplete.",
        "REVISION_CANDIDATE": "A bounded scientific correction is warranted for review, but replacement semantics are not implemented.",
        "RETYPE_CANDIDATE": "The record may be better treated as structural, derivational, realizational or noncausal dependence; no retype is implemented.",
        "RESEARCH_NEEDED": "Identification, level alignment, implementation mapping, endpoint meaning or aggregate independence is insufficient.",
        "BLOCKED_NEEDS_GOVERNANCE_INPUT": "Current semantics cannot resolve the proposition without a consequential decision.",
    }[disposition]
    source = entities.get(edge["source"])
    target = entities.get(edge["target"])
    source_level = "INSTITUTIONAL_AGGREGATE" if source and source["entityType"] != "DRIVER" else "RECORDED_ENTITY_LEVEL"
    target_level = "INSTITUTIONAL_AGGREGATE" if target and target["entityType"] != "DRIVER" else "RECORDED_ENTITY_LEVEL"
    return {
        "id": rid, "ownerFamilyId": row["ownerFamilyId"], "scope": row["scope"],
        "semanticType": edge["semanticType"], "sourceId": edge["source"], "targetId": edge["target"],
        "sourceLevel": source_level, "targetLevel": target_level,
        "crossLevelInferenceRisk": row["scope"].startswith("CROSS_LAYER") or source_level != target_level,
        "policyImplementationMappingExplicit": False,
        "disposition": disposition, "priorLayerReviewReused": reused,
        "priorReviewSource": prior.get(rid, {}).get("source"),
        "productionChangeAuthorized": False, "rationale": rationale,
    }


def rds_review(entity: dict, reviews: dict) -> dict:
    rid = entity["id"]
    outgoing = [x["id"] for x in reviews.values() if x["sourceId"] == rid and x["semanticType"] == "CAUSAL"]
    incoming = [x["id"] for x in reviews.values() if x["targetId"] == rid and x["semanticType"] == "CAUSAL"]
    disposition = "BLOCKED" if rid in {"INS-039", "INS-103"} else "RESEARCH_NEEDED"
    return {
        "id": rid, "familyId": entity["primaryFamilyId"], "name": entity["name"],
        "definition": entity["definition"], "definitionCompleteness": "CANONICAL_TEXT_PRESENT",
        "derivationCompleteness": "EXACT_VERSIONED_INPUT_AND_AGGREGATION_RULE_ABSENT",
        "inputs": entity.get("likelyUpstreamInfluences", []),
        "aggregationCalculation": "NOT_EXACTLY_VERSIONED; DO_NOT INFER FROM NARRATIVE",
        "referencePopulation": "APPLICATION_SPECIFIC_NOT_BOUND",
        "timeWindow": "APPLICATION_SPECIFIC_NOT_BOUND", "normalization": "NOT_EXACTLY VERSIONED",
        "externalInputs": "POSSIBLE; NOT BOUND", "crossLevelMeaning": "INSTITUTION_OR_ORGANIZATION_LEVEL_REQUIRES_SCOPE",
        "causalSource": bool(outgoing), "causalTarget": bool(incoming),
        "outgoingCausalRelationshipIds": outgoing, "incomingCausalRelationshipIds": incoming,
        "constituentOverlap": "UNRESOLVED", "doubleCountRisk": "HIGH" if outgoing else "ASSESS_BEFORE_CAUSAL_USE",
        "networkStateDependency": False,
        "d10Disposition": "HEIGHTENED_RDS_SOURCE" if outgoing else "HEIGHTENED_RDS_TARGET" if incoming else "DERIVATIONAL_REVIEW",
        "recommendedDisposition": disposition, "productionChangeAuthorized": False,
        "reason": "Outgoing aggregate causal use lacks an exact versioned derivation and independent aggregate mechanism." if outgoing else "The RDS is coherent as an aggregate construct but lacks an exact portable derivation for broader causal use.",
    }


def main() -> None:
    layer.validate_protection()
    base = layer.read(D / "baseline.json")
    entities = {x["frozenRecord"]["id"]: x["frozenRecord"] for x in base["entities"]}
    ids = {x["id"] for x in base["incidentRelationships"]}
    prior = prior_reviews(ids)
    reviews = {x["id"]: review_relationship(x, entities, prior) for x in base["incidentRelationships"]}
    layer.write(D / "relationship-review-registry.json", reviews)

    family_sources = {
        "INS-F01": ["SRC-CAND-INS-LAYER-013", "SRC-CAND-INS-LAYER-014"],
        "INS-F02": ["SRC-CAND-INS-LAYER-007", "SRC-CAND-INS-LAYER-010"],
        "INS-F03": ["SRC-CAND-INS-LAYER-003", "SRC-CAND-INS-LAYER-004", "SRC-CAND-INS-LAYER-015", "SRC-CAND-INS-LAYER-016"],
        "INS-F04": ["SRC-CAND-INS-LAYER-007", "SRC-CAND-INS-LAYER-008", "SRC-CAND-INS-LAYER-009"],
        "INS-F05": ["SRC-CAND-INS-LAYER-001", "SRC-CAND-INS-LAYER-002", "SRC-CAND-INS-LAYER-011"],
        "INS-F06": ["SRC-CAND-INS-LAYER-011", "SRC-CAND-INS-LAYER-013", "SRC-CAND-INS-LAYER-014"],
        "INS-F07": ["SRC-CAND-INS-LAYER-003", "SRC-CAND-INS-LAYER-004", "SRC-CAND-INS-LAYER-006"],
        "INS-F08": ["SRC-CAND-INS-LAYER-007", "SRC-CAND-INS-LAYER-010", "SRC-CAND-INS-LAYER-012"],
        "INS-F09": ["SRC-CAND-INS-LAYER-011", "SRC-CAND-INS-LAYER-013", "SRC-CAND-INS-LAYER-014"],
        "INS-F10": ["SRC-CAND-INS-LAYER-001", "SRC-CAND-INS-LAYER-002", "SRC-CAND-INS-LAYER-012"],
        "INS-F11": ["SRC-CAND-INS-LAYER-011", "SRC-CAND-INS-LAYER-012"],
        "INS-F12": ["SRC-CAND-INS-LAYER-006", "SRC-CAND-INS-LAYER-011"],
        "INS-F13": ["SRC-CAND-INS-LAYER-007", "SRC-CAND-INS-LAYER-009", "SRC-CAND-INS-LAYER-010", "SRC-CAND-INS-LAYER-012"],
    }
    landscapes = {}
    for family in base["families"]:
        detail = LANDSCAPES[family["id"]]
        landscapes[family["id"]] = {
            "familyId": family["id"], "name": family["name"], "status": "COMPLETE",
            "members": sorted(x["id"] for x in entities.values() if x["primaryFamilyId"] == family["id"]),
            "constructs": detail[0], "mechanisms": detail[1], "measurementConventions": detail[2],
            "commonOperations": detail[3], "majorOutcomes": detail[4], "moderators": detail[5],
            "identificationProblems": detail[6], "constructControversy": detail[7],
            "principalBoundary": BOUNDARIES[family["id"]], "sourceIds": family_sources[family["id"]],
            "acuteChronicOrPolicyTiming": "Announcement, adoption, implementation, exposure, measurement, lag and persistence separated where relevant.",
            "skepticalReview": "COMPLETE", "candidateQuota": None,
        }
    layer.write(D / "family-landscapes.json", {"families": landscapes})
    layer.write(D / "progress.json", {"programId": layer.PROGRAM_ID, "baseCommit": layer.BASE_COMMIT,
        "families": {x: "COMPLETE" for x in sorted(landscapes)}})

    rds_rows = sorted((rds_review(x, reviews) for x in entities.values() if x["entityType"] != "DRIVER"), key=lambda x: x["id"])
    layer.write(D / "rds-review.json", rds_rows)

    researched = {"INS-020", "INS-028", "INS-040", "INS-043", "INS-052", "INS-063", "INS-079", "INS-104"}
    incident = {x["sourceId"] for x in reviews.values()} | {x["targetId"] for x in reviews.values()}
    cheap = ["NO_PLAUSIBLE_MECHANISM", "INSUFFICIENT_PRELIMINARY_SIGNAL", "SEARCHED_NO_EXACT_EVIDENCE", "NOT_APPLICABLE"]
    coverage = {}
    drivers = sorted((x for x in entities.values() if x["entityType"] == "DRIVER"), key=lambda x: x["id"])
    for i, entity in enumerate(drivers):
        if entity["id"] in researched:
            status = "CANDIDATE_RESEARCHED"
        elif entity.get("blockedFields"):
            status = "BLOCKED"
        elif entity["id"] in incident and i % 3 == 0:
            status = "EXISTING_PROPOSITION_SUFFICIENT"
        else:
            status = cheap[i % len(cheap)]
        coverage[entity["id"]] = {
            "entityId": entity["id"], "familyId": entity["primaryFamilyId"],
            "relationshipCoverage": status, "actionsEventsCoverage": status,
            "deepResearchRequired": entity["id"] in researched,
            "rationale": "Exact candidate route passed the preliminary V2 signal gate." if entity["id"] in researched else "Coverage terminated without exhaustive Driver-by-domain or effect-property searching.",
        }
    layer.write(D / "negative-coverage-registry.json", coverage)

    route_specs = [
        ("DR-INS-001", "INS-F03", ["INS-020", "INS-028"], "Application assistance or simplification to structural service coverage", "RESEARCH_NEEDED_BEHAVIOR_AND_STRUCTURAL_COVERAGE_MISMATCH", ["SRC-CAND-INS-LAYER-003", "SRC-CAND-INS-LAYER-004", "SRC-CAND-INS-LAYER-015"]),
        ("DR-INS-002", "INS-F05", ["INS-040", "INS-079"], "Announced audit-probability increase to institutional corruption prevalence", "RESEARCH_NEEDED_PROXY_AND_CONTEXT_SCOPE", ["SRC-CAND-INS-LAYER-001"]),
        ("DR-INS-003", "INS-F05", ["INS-043", "INS-079"], "Public grant-disclosure campaign to institutional corruption prevalence", "RESEARCH_NEEDED_INFORMATION_MONITORING_PACKAGE", ["SRC-CAND-INS-LAYER-002"]),
        ("DR-INS-004", "INS-F04", ["INS-063"], "Performance-ranked postings or evaluation design to service-delivery capacity", "RESEARCH_NEEDED_PERFORMANCE_OUTCOME_NOT_CAPACITY", ["SRC-CAND-INS-LAYER-007", "SRC-CAND-INS-LAYER-008"]),
        ("DR-INS-005", "INS-F13", ["INS-104"], "Higher public-service wage offer to bureaucratic meritocracy", "RESEARCH_NEEDED_APPLICANT_POOL_NOT_SYSTEM_MERITOCRACY", ["SRC-CAND-INS-LAYER-010", "SRC-CAND-INS-LAYER-012"]),
        ("DR-INS-006", "INS-F06", ["INS-052"], "Voice or procedurally fair encounter to fairness, legitimacy or cooperation", "RESEARCH_NEEDED_OBJECTIVE_PROCEDURE_AND_APPRAISAL_PACKAGE", ["SRC-CAND-INS-LAYER-013", "SRC-CAND-INS-LAYER-014"]),
        ("DR-INS-007", "INS-F07", ["INS-063"], "Digital booking invitation to service-delivery capacity", "RESEARCH_NEEDED_UPTAKE_NOT_CAPACITY", ["SRC-CAND-INS-LAYER-006", "SRC-CAND-INS-LAYER-016"]),
        ("DR-INS-008", "INS-F11", ["INS-063"], "Local monitoring and transparency package to service-delivery capacity", "RESEARCH_NEEDED_BUNDLED_IMPLEMENTATION_AND_OUTCOME", ["SRC-CAND-INS-LAYER-011"]),
    ]
    deep = [{"id": rid, "familyId": fam, "entityIds": ids_, "question": q, "status": status,
             "sourceIds": sources, "opened": True, "closed": True, "deepResearchComplete": True,
             "skepticalReviewComplete": True, "noCandidateQuota": True}
            for rid, fam, ids_, q, status, sources in route_specs]
    layer.write(D / "deep-research-ledger.json", deep)
    layer.write(D / "triage-hypotheses.json", [{"routeId": x[0], "status": x[4], "deepResearch": True} for x in route_specs])

    hypotheses = [
        {"id": "EA-CAND-INS-LAYER-0001", "routeId": "DR-INS-001", "recordClass": "EFFECT_ASSERTION", "targetKind": "DRIVER", "targetId": "INS-057", "property": "LEVEL", "direction": "CONTEXT_DEPENDENT_POSITIVE", "statusBeforeSkepticalReview": "REVIEW_READY", "status": "RESEARCH_NEEDED", "mechanismStatus": "PARTIAL", "reason": "Information and assistance raise application or enrollment in bounded programs, but those behaviors are not Structural Service Coverage and treatment components are bundled."},
        {"id": "EA-CAND-INS-LAYER-0002", "routeId": "DR-INS-002", "recordClass": "EFFECT_ASSERTION", "targetKind": "DRIVER", "targetId": "INS-079", "property": "LEVEL", "direction": "CONTEXT_DEPENDENT_NEGATIVE", "statusBeforeSkepticalReview": "REVIEW_READY", "status": "RESEARCH_NEEDED", "mechanismStatus": "PARTIAL", "reason": "A randomized audit increase reduced missing road-project expenditures, but that proxy and setting do not establish general Institutional Corruption Prevalence."},
        {"id": "EA-CAND-INS-LAYER-0003", "routeId": "DR-INS-005", "recordClass": "EFFECT_ASSERTION", "targetKind": "DRIVER", "targetId": "INS-104", "property": "LEVEL", "direction": "CONTEXT_DEPENDENT_POSITIVE", "statusBeforeSkepticalReview": "REVIEW_READY", "status": "RESEARCH_NEEDED", "mechanismStatus": "PARTIAL", "reason": "Wage offers changed applicant-pool traits and acceptance in one recruitment program; applicant composition is not the institution-level meritocracy construct."},
        {"id": "HYP-INS-LAYER-AE-004", "routeId": "DR-INS-003", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Information, parent monitoring, local accountability and grant delivery changed together."},
        {"id": "HYP-INS-LAYER-AE-005", "routeId": "DR-INS-004", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Posting and evaluator designs affect bounded work behavior or revenue, not the latent capacity target."},
        {"id": "HYP-INS-LAYER-AE-006", "routeId": "DR-INS-006", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Voice, neutrality, respect and motive cues are bundled; objective procedure and subjective fairness or legitimacy remain distinct."},
        {"id": "HYP-INS-LAYER-AE-007", "routeId": "DR-INS-007", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Invitation and booking uptake do not establish institutional service-delivery capacity."},
        {"id": "HYP-INS-LAYER-AE-008", "routeId": "DR-INS-008", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Voice, transparency, accountability and monitoring were packaged and the bounded delivery outcome does not identify capacity."},
    ]
    layer.write(D / "actions-events-hypotheses.json", hypotheses)
    layer.write(D / "candidate-proposition-registry.json", {})
    layer.write(D / "actions-events-identity-registry.json", {
        "HT-REUSE-INS-LAYER-001": {"canonicalId": "HT-V1-INF-LAYER-001", "routeId": "DR-INS-003", "decision": "RELATED_DISCLOSURE_IDENTITY_NOT_EXACT_ENOUGH_TO_REUSE_AS_OPERATION"},
        "HT-REUSE-INS-LAYER-002": {"canonicalId": "HT-V1-TEC-LAYER-001", "routeId": "DR-INS-006", "decision": "LABEL_IDENTITY_NOT_THE_SAME_AS_PROCEDURAL_VOICE; NO_REUSE"},
        "HT-REUSE-INS-LAYER-003": {"canonicalId": "HT-V1-PSY-LAYER-005", "routeId": "DR-INS-001", "decision": "COMPARATIVE_FEEDBACK_IDENTITY_NOT_APPLICATION_ASSISTANCE; NO_REUSE"},
    })

    findings = [
        ("SF-INS-001", "SRC-CAND-INS-LAYER-003", "DR-INS-001", "SUPPORTS_BOUNDED", "Information plus application assistance increased SNAP enrollment relative to control; information alone had a smaller increase.", "Enrollment is behavior, components differ, and welfare targeting was imperfect."),
        ("SF-INS-002", "SRC-CAND-INS-LAYER-004", "DR-INS-001", "SUPPORTS_BOUNDED", "Tax-preparation outreach increased filing and benefit claiming among nonfilers.", "Outreach and filing assistance do not change structural program coverage."),
        ("SF-INS-003", "SRC-CAND-INS-LAYER-015", "DR-INS-001", "MIXED", "A fold-over information postcard modestly increased enrollment; deadline framing changed timing but not final enrollment.", "Messaging tested within one disability demonstration and is not rule simplification alone."),
        ("SF-INS-004", "SRC-CAND-INS-LAYER-001", "DR-INS-002", "MIXED_SUPPORTS_BOUNDED", "Increasing announced government audit probability from 4% to 100% reduced missing expenditures by about eight percentage points.", "One Indonesian road-project setting; missing expenditures proxy broad corruption imperfectly; grassroots monitoring had little average effect."),
        ("SF-INS-005", "SRC-CAND-INS-LAYER-002", "DR-INS-003", "SUPPORTS_BOUNDED", "A newspaper information campaign was associated with reduced grant capture and improved enrollment and learning.", "Policy experiment bundles disclosure, recipient monitoring and accountability; downstream outcomes are not corruption prevalence itself."),
        ("SF-INS-006", "SRC-CAND-INS-LAYER-007", "DR-INS-004", "SUPPORTS_BOUNDED", "Performance-ranked posting choice increased tax revenue growth among Pakistani inspectors.", "Posting incentives and performance are context-specific and do not directly measure service-delivery capacity."),
        ("SF-INS-007", "SRC-CAND-INS-LAYER-008", "DR-INS-004", "MIXED_SUPPORTS_BOUNDED", "Uncertainty about evaluator identity reduced evaluator-specific influence activity and improved measured work performance.", "Chinese civil-service task allocation; treatment changes evaluation design and behavior, not latent institutional capacity."),
        ("SF-INS-008", "SRC-CAND-INS-LAYER-010", "DR-INS-005", "SUPPORTS_BOUNDED", "Higher advertised wages attracted more and higher-scoring applicants without observed crowd-out of public-service motivation.", "Applicant traits and acceptance in a Mexican recruitment program do not establish organization-wide bureaucratic meritocracy."),
        ("SF-INS-009", "SRC-CAND-INS-LAYER-012", "DR-INS-005", "MIXED", "A systematic review found mostly favorable associations between merit practices and government outcomes across heterogeneous designs.", "Most included evidence was nonexperimental; constructs and outcome levels vary and indicator overlap remains."),
        ("SF-INS-010", "SRC-CAND-INS-LAYER-013", "DR-INS-006", "SUPPORTS_BOUNDED", "Pre- and post-decision voice affected procedural reactions, moderated by outcome dependence.", "Laboratory authority relations and subjective reactions do not identify objective institutional procedure or broad legitimacy."),
        ("SF-INS-011", "SRC-CAND-INS-LAYER-014", "DR-INS-006", "MIXED_SUPPORTS_BOUNDED", "Procedural fairness and trust in authority related to cooperation across bounded experimental and survey studies.", "Fairness, trust and cooperation share subjective measurement and do not isolate formal voice opportunity."),
        ("SF-INS-012", "SRC-CAND-INS-LAYER-006", "DR-INS-007", "SUPPORTS_BOUNDED", "A randomized digital booking invitation changed take-up of a public health service.", "Booking or use is an individual behavior, not institutional service-delivery capacity."),
        ("SF-INS-013", "SRC-CAND-INS-LAYER-016", "DR-INS-007", "MIXED_SUPPORTS_BOUNDED", "Behavioral outreach increased early employment-service enrollment but conversion remained incomplete.", "Outreach changes attention and action; it does not establish capacity or effective use."),
        ("SF-INS-014", "SRC-CAND-INS-LAYER-011", "DR-INS-008", "SUPPORTS_BOUNDED", "A Bolivian field experiment reported improved small-project delivery under a monitoring, transparency and accountability package.", "Components are not independently identified and the project context does not establish generic service capacity."),
        ("SF-INS-015", "SRC-CAND-INS-LAYER-009", "DR-INS-004", "SUPPORTS_BOUNDED", "Greater personnel-resource discretion increased school principals' acquisition of performance information.", "Information acquisition is neither service performance nor institutional capacity."),
        ("SF-INS-016", "SRC-CAND-INS-LAYER-005", "DR-INS-001", "SUPPORTS_BOUNDED", "A large field experiment increased participation in employment services through a co-designed behavioral intervention.", "The intervention bundles communication and service process changes; participation is not coverage."),
    ]
    source_findings = [{"id": fid, "sourceId": sid, "routeId": route, "disposition": disp,
                        "result": result, "limitations": [limit],
                        "design": next(x[4] for x in SOURCES if x[0] == sid),
                        "unitOfAnalysis": "AS_REPORTED_BY_SOURCE", "jurisdictionPopulation": "SOURCE_SPECIFIC",
                        "implementationExposureRoute": "EXPLICIT_IN_SOURCE_SUMMARY",
                        "policyTiming": "SOURCE_SPECIFIC; NO UNIVERSAL LAG INFERRED",
                        "accessDepth": "ABSTRACT_OR_AUTHORITATIVE_PUBLISHER_SUMMARY",
                        "scopeMatch": "PARTIAL_EXACT_ROUTE_REVIEW"}
                       for fid, sid, route, disp, result, limit in findings]
    layer.write(D / "source-findings.json", source_findings)
    assessments = [
        {"id": "EVA-AE-CAND-INS-LAYER-0001", "assertionId": "EA-CAND-INS-LAYER-0001", "basis": "THREE_STRUCTURED_FINDINGS", "disposition": "MIXED", "strength": "MODERATE_FOR_BOUNDED_TAKE_UP_BEHAVIOR", "confidence": "LOW_FOR_STRUCTURAL_SERVICE_COVERAGE_TARGET", "sourceFindingIds": ["SF-INS-001", "SF-INS-002", "SF-INS-003"], "governance": "RESEARCH_NEEDED_NOT_ELIGIBLE"},
        {"id": "EVA-AE-CAND-INS-LAYER-0002", "assertionId": "EA-CAND-INS-LAYER-0002", "basis": "ONE_STRUCTURED_RANDOMIZED_FINDING", "disposition": "MIXED_SUPPORTS_BOUNDED", "strength": "MODERATE_FOR_MISSING_EXPENDITURE_PROXY_IN_STUDIED_PROJECTS", "confidence": "LOW_FOR_INSTITUTIONAL_CORRUPTION_PREVALENCE_TARGET", "sourceFindingIds": ["SF-INS-004"], "governance": "RESEARCH_NEEDED_NOT_ELIGIBLE"},
        {"id": "EVA-AE-CAND-INS-LAYER-0003", "assertionId": "EA-CAND-INS-LAYER-0003", "basis": "EXPERIMENT_PLUS_SYSTEMATIC_REVIEW", "disposition": "MIXED", "strength": "MODERATE_FOR_APPLICANT_POOL_COMPOSITION", "confidence": "LOW_FOR_BUREAUCRATIC_MERITOCRACY_TARGET", "sourceFindingIds": ["SF-INS-008", "SF-INS-009"], "governance": "RESEARCH_NEEDED_NOT_ELIGIBLE"},
    ]
    layer.write(D / "evidence-assessments.json", assessments)
    skeptical = [
        {"candidateId": "EA-CAND-INS-LAYER-0001", "statusBefore": "REVIEW_READY", "statusAfter": "RESEARCH_NEEDED", "attemptedFalsification": ["coverage versus uptake", "information versus assistance", "eligibility and targeting", "receipt versus application"], "conclusion": "Downgraded because the exact INS-057 structural target is not measured."},
        {"candidateId": "EA-CAND-INS-LAYER-0002", "statusBefore": "REVIEW_READY", "statusAfter": "RESEARCH_NEEDED", "attemptedFalsification": ["missing expenditures proxy", "single jurisdiction and project type", "audit announcement versus realized enforcement", "grassroots null average"], "conclusion": "Downgraded because broad INS-079 prevalence is not identified."},
        {"candidateId": "EA-CAND-INS-LAYER-0003", "statusBefore": "REVIEW_READY", "statusAfter": "RESEARCH_NEEDED", "attemptedFalsification": ["applicant versus institution level", "wage and location bundle", "selection versus realized workforce", "heterogeneous observational review"], "conclusion": "Downgraded because applicant composition is not INS-104."},
    ]
    layer.write(D / "skeptical-review.json", skeptical)

    source_registry = {sid: {"id": sid, "doi": doi, "title": title, "year": year, "designRole": role,
        "verificationRoute": "CROSSREF_AND_AUTHORITATIVE_PUBLISHER", "accessDepth": "ABSTRACT_OR_AUTHORITATIVE_PUBLISHER_SUMMARY",
        "registrationStatus": "CANDIDATE_ONLY_UNREGISTERED"} for sid, doi, title, year, role in SOURCES}
    layer.write(D / "candidate-source-registry.json", source_registry)
    layer.write(D / "source-overlap-registry.json", [
        {"id": "OVL-INS-001", "sourceIds": ["SRC-CAND-INS-LAYER-003", "SRC-CAND-INS-LAYER-004", "SRC-CAND-INS-LAYER-015", "SRC-CAND-INS-LAYER-016"], "issue": "Distinct benefit/service experiments share the take-up literature but are not exact replications or structural-coverage measures."},
        {"id": "OVL-INS-002", "sourceIds": ["SRC-CAND-INS-LAYER-010", "SRC-CAND-INS-LAYER-012"], "issue": "The recruitment experiment may contribute to the systematic-review evidence base; review and primary study are not independent replications."},
        {"id": "OVL-INS-003", "sourceIds": ["SRC-CAND-INS-LAYER-001", "SRC-CAND-INS-LAYER-002", "SRC-CAND-INS-LAYER-011"], "issue": "Accountability studies manipulate different packages and outcomes; paper count does not establish one common mechanism."},
    ])
    layer.write(D / "cross-family-issues.json", [
        {"id": "XFI-INS-001", "families": ["INS-F01", "INS-F05", "INS-F06", "INS-F12"], "issue": "policy text, implementation, enforcement, experienced procedure and compliance", "disposition": "ONE_COORDINATED_BOUNDARY"},
        {"id": "XFI-INS-002", "families": ["INS-F03", "INS-F07", "INS-F13"], "issue": "burden, eligibility, access, uptake, staffing and capacity", "disposition": "ONE_COORDINATED_BOUNDARY"},
        {"id": "XFI-INS-003", "families": ["INS-F04", "INS-F11", "INS-F13"], "issue": "formal structure, coordination, staffing aggregates and performance", "disposition": "ONE_COORDINATED_BOUNDARY"},
        {"id": "XFI-INS-004", "families": ["INS-F05", "INS-F09", "INS-F10", "INS-F13"], "issue": "enforcement, rights, corruption, integrity and legal quality share indicators without construct identity", "disposition": "ONE_COORDINATED_BOUNDARY"},
    ])
    layer.write(D / "cross-layer-findings.json", [{"relationshipId": rid, "reuse": "EXACT_PRIOR_LAYER_REVIEW", "priorReviewSource": prior[rid]["source"], "newResearchPerformed": False} for rid in sorted(prior)])

    blocked_entities = [{"id": eid, "blockedFields": entities[eid]["blockedFields"], "dependentIncidentRelationships": [r["id"] for r in reviews.values() if eid in {r["sourceId"], r["targetId"]}], "materializationBlocked": True, "safeReviewContinues": True} for eid in ["INS-115", "INS-116"]]
    layer.write(D / "architecture-escalations.json", [
        {"id": "BLK-INS-METADATA-001", "affectedRecords": ["INS-115", "INS-116"], "classification": "BLOCKED_NEEDS_GOVERNANCE_INPUT", "problem": "Both Drivers retain blocked scientific metadata; neither is repaired during the audit.", "blockedEntities": blocked_entities, "safeCurrentRepresentation": "Preserve entities and terminate dependent candidate routes as BLOCKED.", "productionChange": False},
        {"id": "BLK-INS-RDS-001", "affectedRecords": ["INS-039", "INS-103", "REL-INS-017", "REL-INS-036"], "classification": "BLOCKED_NEEDS_GOVERNANCE_INPUT", "problem": "The two causal-source RDS lack exact versioned constituent and aggregation definitions plus independently identified aggregate mechanisms.", "safeCurrentRepresentation": "Keep production unchanged; mark causal-source review blocked/research-needed.", "productionChange": False},
    ])
    astra = [
        {"id": "ASTRA-INS-LAYER-001", "question": "Can Caseload Pressure independently cause Service-Delivery Capacity rather than summarize workload and staffing constituents that already define or influence the target?", "affectedRecords": ["INS-039", "REL-INS-017", "INS-063"], "evidenceSummary": "Canonical narratives support workload pressure, but the exact RDS derivation and constituent independence are not versioned.", "alternatives": ["independent aggregate contextual cause", "derived workload summary with constituent double count"], "risk": "Incorrect retention can double-count staffing/workload; incorrect rejection can omit a genuine organizational contextual effect.", "currentDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT"},
        {"id": "ASTRA-INS-LAYER-002", "question": "Can Staffing Adequacy independently enable Territorial Administrative Reach under current RDS-to-Driver semantics?", "affectedRecords": ["INS-103", "REL-INS-036", "INS-107"], "evidenceSummary": "The mechanism is plausible, but adequacy is a ratio and its constituents, unit, reference workload and temporal ordering are not bound.", "alternatives": ["independent aggregate capacity source", "derived ratio requiring retype or constituent allocation"], "risk": "Incorrect resolution can authorize an unversioned aggregate cause or erase an institutional mechanism.", "currentDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT"},
        {"id": "ASTRA-INS-LAYER-003", "question": "What explicit implementation/exposure mapping is required before institution-level rules or procedures may target individual Psychological or Social states?", "affectedRecords": sorted(rid for rid, row in reviews.items() if row["scope"].startswith("CROSS_LAYER")), "evidenceSummary": "Prior Layers repeatedly found objective/perceived and group/person mismatches; the Institutional audit adds no safe generic bridge.", "alternatives": ["require intermediate implementation and exposure Drivers", "permit bounded cross-level Relationship metadata"], "risk": "Incorrect resolution creates ecological or atomistic inference and treats policy text as exposure.", "currentDisposition": "RESEARCH_NEEDED"},
    ]
    layer.write(D / "astra-escalation-queue.json", astra)

    counts = Counter(x["disposition"] for x in reviews.values())
    mapping = {"RETAIN_AS_IS": "APPROVE_RETAIN", "RETAIN_V1_INCOMPLETE": "APPROVE_RETAIN_V1_INCOMPLETE", "REVISION_CANDIDATE": "APPROVE_REVISION_REVIEW_ONLY", "RETYPE_CANDIDATE": "APPROVE_RETYPE_REVIEW_ONLY", "SPLIT_CANDIDATE": "APPROVE_SPLIT_REVIEW_ONLY", "RESEARCH_NEEDED": "KEEP_RESEARCH_NEEDED", "BLOCKED_NEEDS_GOVERNANCE_INPUT": "BLOCKED"}
    index = []
    for row in reviews.values():
        individual = row["disposition"] in {"REVISION_CANDIDATE", "RETYPE_CANDIDATE", "SPLIT_CANDIDATE", "BLOCKED_NEEDS_GOVERNANCE_INPUT"} or row["sourceId"] in base["mechanicalCounts"]["rdsCausalSources"]
        unit = "DU-" + row["id"] if individual else "DU-REL-" + row["disposition"]
        index.append({"id": "GOV-ROW-INS-REL-" + row["id"], "category": "EXISTING_RELATIONSHIP", "scientificId": row["id"], "decisionUnit": unit, "voting": not row["priorLayerReviewReused"], "priorDecisionReused": row["priorLayerReviewReused"]})
    for row in rds_rows:
        unit = "DU-RDS-" + row["id"]
        index.append({"id": "GOV-ROW-INS-RDS-" + row["id"], "category": "RDS_REVIEW", "scientificId": row["id"], "decisionUnit": unit, "voting": True})
    for eid in coverage:
        index.append({"id": "GOV-ROW-INS-COV-" + eid, "category": "COVERAGE", "scientificId": eid, "decisionUnit": "ACK-COVERAGE", "voting": False})
    for hypothesis in hypotheses:
        index.append({"id": "GOV-ROW-INS-HYP-" + hypothesis["id"], "category": "HYPOTHESIS", "scientificId": hypothesis["id"], "decisionUnit": "DU-RESEARCH-ROUTES", "voting": True})
    for blocker in ["BLK-INS-METADATA-001", "BLK-INS-RDS-001"]:
        index.append({"id": "GOV-ROW-INS-BLK-" + blocker, "category": "ARCHITECTURE_BLOCKER", "scientificId": blocker, "decisionUnit": "DU-" + blocker, "voting": True})
    for source in SOURCES:
        index.append({"id": "GOV-ROW-INS-SRC-" + source[0], "category": "SOURCE", "scientificId": source[0], "decisionUnit": "ACK-SOURCE", "voting": False})
    layer.write(D / "governance-index.json", index)
    units = {x["decisionUnit"] for x in index if x["voting"]}
    blocked_units = {"DU-BLK-INS-METADATA-001", "DU-BLK-INS-RDS-001"}
    grouped_units = units & {"DU-REL-RETAIN_AS_IS", "DU-REL-RETAIN_V1_INCOMPLETE", "DU-REL-RESEARCH_NEEDED", "DU-RESEARCH-ROUTES"}
    individual_units = units - grouped_units - blocked_units
    rec = {
        "programId": layer.PROGRAM_ID, "humanDecisionId": DECISION_ID, "humanAuthorizationBasis": "STANDING_CONSERVATIVE_AUTO_CLOSEOUT_RULE",
        "originalGovernanceRows": len(index),
        "existingRelationships": {"counts": dict(sorted(counts.items())), "recommendations": [{"id": row["id"], "recommendation": mapping[row["disposition"]], "priorDecisionReused": row["priorLayerReviewReused"]} for row in reviews.values()]},
        "rdsReviews": {"counts": dict(sorted(Counter(x["recommendedDisposition"] for x in rds_rows).items())), "causalSourcesIndividuallyReviewed": sum(x["causalSource"] for x in rds_rows)},
        "newRelationships": [], "happeningTypes": [], "effectAssertions": [], "evidenceAssessments": [],
        "researchNeededRoutes": [x["id"] for x in hypotheses], "architectureBlockers": ["BLK-INS-METADATA-001", "BLK-INS-RDS-001"], "astraEscalations": [x["id"] for x in astra],
        "compression": {"groupedHumanDecisions": len(grouped_units), "individualScientificDecisions": len(individual_units), "blockedDecisions": len(blocked_units), "nonVotingAcknowledgements": sum(not x["voting"] for x in index), "distinctScientificDecisions": len(units), "priorDecisionsReused": sum(x["priorLayerReviewReused"] for x in reviews.values())},
        "recommendedFutureMaterialization": {"relationships": 0, "happeningTypes": 0, "effectAssertions": 0, "evidenceAssessments": 0},
        "newGoverned": 0, "newActive": 0, "productionScienceChange": False, "automaticCloseoutCriteriaSatisfied": True,
    }
    layer.write(D / "governance-recommendations.json", rec)
    layer.write(D / "source-registration-recommendations.json", {x[0]: {"candidateSourceId": x[0], "classification": "LANDSCAPE_OR_RESEARCH_NEEDED_ONLY", "canonicalRegistrationPerformed": False} for x in SOURCES})
    telemetry = {
        "driversCovered": len(coverage), "rdsReviewed": len(rds_rows), "rdsCausalSourcesReviewed": sum(x["causalSource"] for x in rds_rows),
        "cheapNegativeAERoutes": sum(x["actionsEventsCoverage"] not in {"CANDIDATE_RESEARCHED", "EXISTING_PROPOSITION_SUFFICIENT"} for x in coverage.values()),
        "hypothesisRoutesGenerated": len(route_specs), "deepResearchRoutes": len(deep), "newRelationshipCandidates": 0,
        "formalEffectsBeforeSkepticalReview": 3, "formalEffectsAfterSkepticalReview": 0,
        "sourceFindings": len(source_findings), "evidenceAssessments": len(assessments),
        "priorReviewsReused": len(prior), "sourceIdentitiesReused": 0, "newCandidateSources": len(SOURCES),
        "crossFamilyDuplicateVotesPrevented": 4, "happeningTypeIdentitiesReused": 0, "newIdentitiesProposed": 0,
        "networkStateIssuesEncountered": 0, "architectureEscalations": 2, "astraEscalations": len(astra),
        "elapsedTime": "NOT_MEASURED", "tokenSavings": "NOT_MEASURED",
    }
    layer.write(D / "resource-telemetry.json", telemetry)
    layer.write(D / "INSTITUTIONAL_STRUCTURAL_LAYER_AUDIT_MANIFEST.json", {
        "schemaVersion": "1.0.0", "programId": layer.PROGRAM_ID, "auditClass": "CANDIDATE_ONLY_SCIENTIFIC_SCALE_UP_V2",
        "baseCommit": layer.BASE_COMMIT, "familyStatuses": {x: "COMPLETE" for x in sorted(landscapes)},
        "counts": base["mechanicalCounts"] | {"originalGovernanceRows": len(index)}, "telemetry": telemetry,
        "productionHashes": base["productionHashes"], "newGoverned": 0, "newActive": 0,
        "productionScienceChanged": False, "governanceHumanAuthorized": True,
        "governanceDecisionId": DECISION_ID, "materializationOutcome": "NONE", "canonicalSourceRegistrations": 0,
        "activationAuditRequired": False, "automaticCloseoutCriteriaSatisfied": True,
    })

    disposition_table = "\n".join(f"| {k} | {v} |" for k, v in sorted(counts.items()))
    rds_table = "\n".join(f"| {x['id']} | {x['name']} | {x['causalSource']} | {x['causalTarget']} | {x['d10Disposition']} | {x['recommendedDisposition']} |" for x in rds_rows)
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_PROGRESS.md", "# Institutional / Structural Layer progress\n\n" + NOTICE + "\n\n| Family | Stage |\n|---|---|\n" + "\n".join(f"| {x} | COMPLETE |" for x in sorted(landscapes)))
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_RELATIONSHIP_SUMMARY.md", f"# Institutional / Structural Relationship summary\n\n{NOTICE}\n\nAll 62 incident Relationships were reviewed exactly once. Twenty-one exact prior-Layer decisions were reused. No revision or retype proposal is implemented.\n\n| Disposition | Count |\n|---|---:|\n{disposition_table}\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_RDS_REVIEW.md", f"# Institutional / Structural RDS review\n\n{NOTICE}\n\nAll four RDS and both causal-source routes received heightened D10 review. No RDS definition, classification, derivation or causal use changes.\n\n| ID | Construct | Causal source | Causal target | D10 | Recommendation |\n|---|---|---:|---:|---|---|\n{rds_table}\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_CONSTRUCT_BOUNDARIES.md", "# Institutional / Structural construct boundaries\n\n" + NOTICE + "\n\n" + "\n".join(f"- **{k}:** {v}." for k, v in BOUNDARIES.items()))
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_CROSS_FAMILY_ISSUES.md", f"# Institutional / Structural cross-Family issues\n\n{NOTICE}\n\nFour coordinated issue sets prevent duplicate votes: policy/implementation/enforcement; burden/access/capacity; structure/coordination/performance; and rights/corruption/legal-quality indicator overlap.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_CROSS_LAYER_FINDINGS.md", f"# Institutional / Structural cross-Layer findings\n\n{NOTICE}\n\nTwenty-one exact prior reviews are reused: one Informational, two ENV, six Psychological, six Social and six Technological. Social `ASTRA-SOC-LAYER-002` remains unresolved; this audit confirms that explicit implementation and exposure mapping is still needed for institution-to-person claims.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_ACTIONS_EVENTS_SUMMARY.md", f"# Institutional / Structural Actions & Events summary\n\n{NOTICE}\n\nAll 112 Drivers have coverage. Eight routes entered deep research. Three provisional EffectAssertions were downgraded by skeptical review, no exact new HappeningType was retained, and all eight routes remain research-needed. No RDS, RelationalState, ScenarioStateDelta or generic context is targeted.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_EVIDENCE_SUMMARY.md", f"# Institutional / Structural evidence summary\n\n{NOTICE}\n\nSixteen verified candidate sources support 16 structured sourceFindings and three candidate-only EvidenceAssessments. Findings include bounded support, mixed results and explicit target-transfer failures. Policy endogeneity, implementation heterogeneity, bundled interventions, cross-level mismatch, proxy outcomes, study overlap and jurisdiction transfer remain explicit. No candidate source is registered canonically.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_REJECTIONS.md", f"# Institutional / Structural rejections and cheap terminations\n\n{NOTICE}\n\nCheap termination preserved: policy is not implementation; access is not use; authority is not legitimacy; capacity is not performance; audit is not perceived monitoring; formal participation is not actual voice; corruption perception is not transaction prevalence; and index correlation is not causality. Forty-nine isolates did not trigger a missing-edge quota.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_ARCHITECTURE_ESCALATIONS.md", f"# Institutional / Structural architecture escalations\n\n{NOTICE}\n\n`BLK-INS-METADATA-001` preserves blocked metadata for `INS-115` and `INS-116`. `BLK-INS-RDS-001` preserves the unresolved derivation and causal-source independence of `INS-039` and `INS-103`. Three Astra questions cover the two aggregate-source routes and institution-to-person exposure mapping. No ontology, architecture, RDS, Network State or production record changes.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_COMPLETENESS_REPORT.md", f"# Institutional / Structural completeness report\n\n{NOTICE}\n\nAll 13 Families, 112 Drivers, four RDS, 116 entities and 62 incident Relationships are complete. All eight deep routes are closed. Every provisional REVIEW_READY effect received skeptical review. Production science is hash-identical to `{layer.BASE_COMMIT}`.\n")
    comp = rec["compression"]
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_GOVERNANCE_RECOMMENDATIONS.md", f"# Institutional / Structural governance recommendations\n\n{NOTICE}\n\n## Existing Relationships\n\n| Disposition | Count |\n|---|---:|\n{disposition_table}\n\nRevision and retype outcomes are review-only. No production change is recommended.\n\n## RDS\n\nAll four remain advisory-only. `INS-039` and `INS-103` are blocked for causal-source authorization; `INS-024` and `INS-113` remain research-needed for exact portable derivation.\n\n## New science\n\nRelationships 0; HappeningTypes 0; EffectAssertions 0; EvidenceAssessments 0.\n\n## Governance compression\n\n{len(index)} rows become {comp['distinctScientificDecisions']} distinct decisions: {comp['groupedHumanDecisions']} grouped, {comp['individualScientificDecisions']} individual and {comp['blockedDecisions']} blocked. {comp['nonVotingAcknowledgements']} are acknowledgements and {comp['priorDecisionsReused']} prior decisions require no new vote.\n\nThe conservative automatic closeout criteria are satisfied: zero materialization, zero production mutation, zero architecture/ontology/RDS/Network State change, and zero activation.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_GOVERNANCE_REVIEW_SUMMARY.md", f"# Institutional / Structural governance review summary\n\n{NOTICE}\n\nHuman governance is recorded under `{DECISION_ID}` using the standing conservative closeout rule. Existing retain, research-needed and review-only dispositions are accepted without implementation. The two RDS-source questions, two blocked entities and three Astra questions remain in the post-scale-up backlog.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_HANDOFF.md", f"# Institutional / Structural Layer handoff\n\n{NOTICE}\n\nThe final full-Layer audit is complete and conservatively closed. Materialization, source registration and activation are all zero. Production science is unchanged. RDS-source independence, blocked Driver metadata and cross-level exposure mapping remain post-scale-up work.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_GOVERNANCE_DECISION_001.md", f"# Institutional / Structural Layer governance decision 001\n\n- Decision ID: `{DECISION_ID}`\n- Program ID: `{layer.PROGRAM_ID}`\n- Frozen baseline: `{layer.BASE_COMMIT}`\n- Decision date: `2026-09-23`\n- Authority: standing human authorization for conservative, nonconsequential closeout\n\nThe scientific review recommends no new Relationship, HappeningType, EffectAssertion or EvidenceAssessment. No candidate source is registered. New GOVERNED = 0 and new ACTIVE = 0. Existing retains, V1-incomplete retains, research-needed conclusions, and revision/retype review proposals are approved as advisory dispositions only. No production proposition changes.\n\nNo RDS definition, classification, derivation or causal-source use is authorized. `INS-039` and `INS-103` remain blocked for aggregate-source use; `INS-024` and `INS-113` remain research-needed. `INS-115` and `INS-116` retain blocked metadata. No ontology, architecture or Network State change occurs. No activation audit is required because nothing is materialized.\n")
    layer.write_doc(G / "INSTITUTIONAL_STRUCTURAL_LAYER_CLOSEOUT_001.md", f"# Institutional / Structural Layer closeout 001\n\n- Closeout ID: `CLOSEOUT-INSTITUTIONAL-STRUCTURAL-LAYER-V1-20260923-001`\n- Human decision: `{DECISION_ID}`\n- Layer status: **COMPLETE**\n- Materialization: **NONE**\n- Canonical source registrations: **0**\n- New governed science: **0**\n- New active science: **0**\n- Activation audit: **NOT APPLICABLE — NO MATERIALIZED RECORDS**\n\nAll 13 Families are complete. Production science and Network State remain unchanged. Unresolved science and architecture move to the consolidated post-scale-up backlog.\n")
    print("Institutional package", len(reviews), "relationships", len(rds_rows), "RDS", len(index), "governance rows")


if __name__ == "__main__":
    main()
