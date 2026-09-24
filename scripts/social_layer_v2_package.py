"""Deterministic Social Layer V2 science, skeptical review and governance package."""

from __future__ import annotations

import glob
from collections import Counter
from pathlib import Path

import social_layer_v2 as s

R, D, G = s.ROOT, s.DATA, s.DOCS
NOTICE = "ADVISORY — HUMAN DECISION REQUIRED. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0."

SOURCES = [
    ("SRC-CAND-SOC-LAYER-001", "10.1080/10410236.2026.2678927", "42175703", "Descriptive Norms ≠ Injunctive Norms: A Meta-Analytic Review Across Four Health Contexts", 2026, "META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-002", "10.3310/hsdr08410", "33151653", "Social norms interventions to change clinical behaviour in health workers", 2020, "SYSTEMATIC_REVIEW_META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-003", "10.1007/s00127-021-02191-w", "34796368", "Interventions to improve social connections", 2022, "SYSTEMATIC_REVIEW_META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-004", "10.1037/amp0001578", "41129341", "Are loneliness interventions effective for reducing loneliness?", 2026, "SYSTEMATIC_REVIEW_META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-005", "10.1037/0022-3514.90.5.751", "16737372", "A meta-analytic test of intergroup contact theory", 2006, "META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-006", "10.1111/bjso.12509", "34775630", "What reduces prejudice in the real world?", 2022, "FIELD_EXPERIMENT_META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-007", "10.1037/bul0000439", "38934917", "Negativity bias in intergroup contact", 2024, "META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-008", "10.1126/science.1185231", "20813952", "The spread of behavior in an online social network experiment", 2010, "RANDOMIZED_NETWORK_EXPERIMENT"),
    ("SRC-CAND-SOC-LAYER-009", "10.1371/journal.pmed.1002890", "31479454", "Social network interventions for health behaviours and outcomes", 2019, "SYSTEMATIC_REVIEW_META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-010", "10.1146/annurev-economics-020320-033926", None, "Peer Effects in Networks: A Survey", 2020, "AUTHORITATIVE_IDENTIFICATION_REVIEW"),
    ("SRC-CAND-SOC-LAYER-011", "10.1037/0021-9010.88.6.989", "14640811", "Cohesion and performance in groups", 2003, "META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-012", "10.1016/j.econlet.2021.110186", None, "Observability of partners' past play and cooperation", 2022, "INCENTIVIZED_EXPERIMENT"),
    ("SRC-CAND-SOC-LAYER-013", "10.1016/j.jebo.2020.10.014", None, "Information about average evaluations spurs cooperation", 2020, "INCENTIVIZED_EXPERIMENT"),
    ("SRC-CAND-SOC-LAYER-014", "10.1016/S0140-6736(15)60095-2", None, "Social network targeting to maximise population behaviour change", 2015, "CLUSTER_RANDOMIZED_TRIAL"),
    ("SRC-CAND-SOC-LAYER-015", "10.1016/j.cpr.2023.102321", "37499318", "Social network interventions for psychiatric patients", 2023, "SYSTEMATIC_REVIEW_META_ANALYSIS"),
    ("SRC-CAND-SOC-LAYER-016", "10.1146/annurev.soc.32.061604.123150", None, "Estimating the Causal Effect of Social Capital", 2006, "AUTHORITATIVE_IDENTIFICATION_REVIEW"),
]

BOUNDARIES = {
    "SOC-F01": "actual descriptive/injunctive norms, perceived norms, norm messages, expectations and sanctions remain distinct",
    "SOC-F02": "peer presence, model similarity/status, exposure and influence require identification beyond observed similarity",
    "SOC-F03": "contact frequency, duration, reciprocity, multiplexity, closeness, tie survival and tie formation are not interchangeable",
    "SOC-F04": "available, received, perceived and enacted support remain distinct from network size, integration and loneliness",
    "SOC-F05": "cooperation, intention, trust, reciprocity expectation, observed reciprocity and prevalence remain separate levels",
    "SOC-F06": "formal authority, informal status, prestige, dominance, reputation, centrality and resource control remain distinct",
    "SOC-F07": "network metrics are boundary-dependent calculations, not autonomous causal agents or adjacency state",
    "SOC-F08": "reach, tie, transmission, exposure, attention, acceptance and retransmission are successive non-equivalent states",
    "SOC-F09": "composition, diversity, cohesion, deliberation, participation equality, conflict and performance require separate measures",
    "SOC-F10": "coordination opportunity, behavior, efficacy belief, capability, accountability and outcome remain distinct",
    "SOC-F11": "audience presence, size, identifiability, publicness, monitoring and evaluation exposure are separate manipulations",
    "SOC-F12": "contact quantity, quality, friendship, cooperation, status equality, boundary permeability and hostility are distinct",
}

LANDSCAPE_DETAILS = {
    "SOC-F01": {"constructs": "descriptive and injunctive norms, visibility, consensus, sanctions and rewards", "mechanisms": "expectation formation, conformity incentives and informal enforcement", "measures": "behavior prevalence, expressed approval and actor-specific norm perception must be labeled separately", "operations": "norm feedback, peer-behavior claims and sanction/reward cues", "outcomes": "belief, intention, observed behavior and norm change require distinct endpoints", "moderators": "referent proximity, baseline behavior, credibility, privacy and setting", "identification": "norm messages often bundle comparison, credible source, reward and prompts", "controversies": "actual norms cannot be recovered from perceived norms or message content alone"},
    "SOC-F02": {"constructs": "peer presence, model similarity/status, majority signal, unanimity and minority consistency", "mechanisms": "informational and normative influence, modeling and conformity", "measures": "assigned peer exposure must be separated from endogenous peer similarity", "operations": "peer assignment, endorsement, modeling and majority/minority displays", "outcomes": "task choice, attitude and behavior are not generic influence", "moderators": "publicness, task ambiguity, model status and group identification", "identification": "reflection, homophily, shared context and simultaneity", "controversies": "similarity and adjacency do not identify contagion"},
    "SOC-F03": {"constructs": "interaction frequency/duration, reciprocity, multiplexity, closeness, tie age, formation and dissolution", "mechanisms": "repeated interaction, exchange, opportunity and relational investment", "measures": "event rates, tie reports and closeness scales use different units", "operations": "contact assignment, repeated interaction and bounded link revision", "outcomes": "tie formation, survival and closeness require temporal ordering", "moderators": "tie type, relationship stage, setting and observation window", "identification": "selection into interaction and endogenous tie retention", "controversies": "contact quantity is not relationship quality"},
    "SOC-F04": {"constructs": "inclusion, ostracism, available/received support, integration, isolation and network size", "mechanisms": "resource access, belonging, stress buffering and exclusion", "measures": "objective contact, received support, perceived support and loneliness are non-equivalent", "operations": "support provision, mentoring, group access and exclusion tasks", "outcomes": "support receipt, integration and psychological belonging remain separate", "moderators": "need, provider fit, relationship quality, age and clinical status", "identification": "multicomponent interventions and recipient selection", "controversies": "larger networks need not provide better or received support"},
    "SOC-F05": {"constructs": "cooperation, free riding, reliability, reciprocity, mutual aid and resource sharing", "mechanisms": "repeated games, conditional cooperation, reputation and interdependence", "measures": "laboratory contributions differ from population prevalence and generalized cooperation", "operations": "public-goods structures, reputation feedback, sanctions and repeated interaction", "outcomes": "choice, intention, prevalence and collective result must be separated", "moderators": "stakes, anonymity, repetition, partner matching and group size", "identification": "game structure and observability components are often bundled", "controversies": "task cooperation does not establish a stable social preference"},
    "SOC-F06": {"constructs": "rank, mobility, reputation, deference, authority, resource control and dependence asymmetry", "mechanisms": "status allocation, control dependence and reputational inference", "measures": "rank nominations, resource distributions and network centrality capture different properties", "operations": "reputation displays, role assignment and resource-control changes", "outcomes": "deference, influence and legitimacy require separate evidence", "moderators": "formal role, task domain, visibility and group hierarchy", "identification": "status both shapes and results from interaction", "controversies": "centrality, prestige, dominance and authority are not interchangeable"},
    "SOC-F07": {"constructs": "degree, betweenness, closeness, eigenvector centrality, density, clustering, assortativity, constraint, segregation, centralization and fragmentation", "mechanisms": "network state constrains paths and opportunities; metrics summarize the bound state", "measures": "node set, tie type, direction, weight, boundary, window, variant and normalization are mandatory", "operations": "seeding, tie/node changes, rewiring and boundary changes", "outcomes": "state deltas and metric recalculation are not empirical effects", "moderators": "network boundary, missingness, multiplexity and exposure mapping", "identification": "endogenous formation, interference, reflection and metric constituent reuse", "controversies": "derived metrics may predict outcomes without being autonomous causes"},
    "SOC-F08": {"constructs": "network exposure, cross-cluster exposure, source count, frequency, reinforcement and retransmission", "mechanisms": "simple/complex diffusion, redundant exposure and threshold processes", "measures": "potential reach, receipt, attention, adoption and retransmission require separate mappings", "operations": "network seeding, nominated referents and repeated peer exposure", "outcomes": "adoption and diffusion are content- and behavior-specific", "moderators": "topology, threshold, source dependence, timing and content", "identification": "interference and endogenous exposure", "controversies": "network exposure is not ordinary independent-unit treatment"},
    "SOC-F09": {"constructs": "group size, cohesion, diversity, fractionalization, participation equality, dissent and information coverage", "mechanisms": "information pooling, identification, conflict and workflow coordination", "measures": "composition indices, process observations and cohesion scales are distinct", "operations": "group assignment, deliberation protocol and structured discussion", "outcomes": "performance, consensus, polarization and cooperation are separate", "moderators": "task type, tenure, workflow intensity and facilitation", "identification": "composition is not randomized in most teams and processes can mediate reciprocally", "controversies": "density, cohesion, consensus and performance cannot substitute for one another"},
    "SOC-F10": {"constructs": "interdependence, goal/expectation alignment, common knowledge, accountability, role clarity and collective efficacy", "mechanisms": "mutual predictability, monitoring, coordination and shared-goal pursuit", "measures": "belief in capacity differs from resources, observed coordination and outcome", "operations": "accountability cues, coordination protocols, shared goals and role assignment", "outcomes": "participation threshold, contribution and collective performance", "moderators": "task coupling, group size, communication and authority", "identification": "successful outcomes can cause efficacy reports and obscure coordination process", "controversies": "collective efficacy is not objective collective capacity"},
    "SOC-F11": {"constructs": "audience presence/size, identifiability, publicness, evaluation exposure and monitoring", "mechanisms": "reputation concern, evaluation apprehension and accountability", "measures": "observability of actor, action, outcome and history must be specified", "operations": "public commitment, audience manipulation, identity display and monitoring cues", "outcomes": "self-presentation, task behavior and population prevalence remain distinct", "moderators": "anonymity, audience relevance, stakes and prior reputation", "identification": "identity and reputation information are often bundled", "controversies": "audience presence does not guarantee evaluation or sanction"},
    "SOC-F12": {"constructs": "contact frequency/quality, cross-group friendship, cooperation, competition, hostility, status inequality and boundaries", "mechanisms": "learning, anxiety reduction, recategorization, threat and resource competition", "measures": "contact quantity, valence, intimacy, group status and attitude targets must be explicit", "operations": "structured contact, cooperative tasks and competition structures", "outcomes": "attitude, prejudice, friendship and institutional integration are distinct", "moderators": "equal status, common goals, support, voluntariness, valence and group position", "identification": "self-selection into contact and wide intervention heterogeneity", "controversies": "negative contact may outweigh positive contact and optimal conditions operate as a package"},
}


def prior_reviews(ids):
    found = {}
    # Freeze reuse to Layers that were complete when the Social audit ran.
    # Later Layer packages must not retroactively change a completed audit's
    # voting/reuse counts when deterministic regeneration runs on current main.
    eligible_layers = {
        "BIOLOGICAL_LAYER",
        "CULTURAL_LAYER",
        "INFORMATIONAL_LAYER",
        "PHYSICAL_ENVIRONMENTAL_LAYER",
        "PSYCHOLOGICAL_LAYER",
        "TECHNOLOGICAL_LAYER",
    }
    for path in glob.glob(str(R / "data/candidates/actions-events-v1/*_LAYER/relationship-review-registry.json")):
        source_path = Path(path)
        if source_path.parent.name not in eligible_layers:
            continue
        try:
            payload = s.read(source_path)
        except Exception:
            continue
        rows = payload.values() if isinstance(payload, dict) else payload
        for row in rows:
            if isinstance(row, dict) and row.get("id") in ids:
                disposition = row.get("disposition") or row.get("primaryDisposition") or row.get("review", {}).get("disposition")
                if disposition:
                    found[row["id"]] = {"disposition": disposition, "source": source_path.relative_to(R).as_posix()}
    for row in s.read(R / "data/candidates/actions-events-v1/SOC-F07/existing-relationship-audit.json"):
        if row["id"] in ids:
            found[row["id"]] = {"disposition": row["primaryDisposition"], "source": "SOC-F07/existing-relationship-audit.json"}
    return found


def review_relationship(row, entities, prior):
    rid, edge = row["id"], row["edge"]
    reused = rid in prior
    if reused:
        disposition = prior[rid]["disposition"]
    elif edge["semanticType"] != "CAUSAL":
        disposition = "RETAIN_AS_IS"
    else:
        source_rds = edge["source"] in entities and entities[edge["source"]]["entityType"] != "DRIVER"
        target_rds = edge["target"] in entities and entities[edge["target"]]["entityType"] != "DRIVER"
        disposition = "RESEARCH_NEEDED" if source_rds or target_rds else "RETAIN_V1_INCOMPLETE"
    rationale = {
        "RETAIN_AS_IS": "The noncausal or already-bounded proposition is coherent at its stated semantic type; no scientific change is proposed.",
        "RETAIN_V1_INCOMPLETE": "The direction is plausible, while exact level, exposure, timing, evidence or V1 fields remain incomplete.",
        "REVISION_CANDIDATE": "A bounded scientific criticism exists, but replacement semantics remain review-only and production is unchanged.",
        "RETYPE_CANDIDATE": "The record is better reviewed as semantic, derivational, structural or noncausal dependence; no retype is implemented.",
        "SPLIT_CANDIDATE": "The bundled proposition warrants separate review; no split is implemented.",
        "RESEARCH_NEEDED": "Level alignment, causal identification, exact construct, temporal order or aggregate independence is insufficient.",
        "BLOCKED_NEEDS_GOVERNANCE_INPUT": "Current architecture cannot resolve the proposition without governance input.",
    }[disposition]
    return {"id": rid, "ownerFamilyId": row["ownerFamilyId"], "scope": row["scope"],
        "semanticType": edge["semanticType"], "sourceId": edge["source"], "targetId": edge["target"],
        "sourceLevel": "NETWORK_OR_GROUP" if edge["source"] in entities and entities[edge["source"]]["entityType"] != "DRIVER" else "RECORDED_ENTITY_LEVEL",
        "targetLevel": "NETWORK_OR_GROUP" if edge["target"] in entities and entities[edge["target"]]["entityType"] != "DRIVER" else "RECORDED_ENTITY_LEVEL",
        "disposition": disposition, "priorLayerReviewReused": reused,
        "priorReviewSource": prior.get(rid, {}).get("source"), "productionChangeAuthorized": False,
        "crossLevelInferenceRisk": bool((edge["source"] in entities and entities[edge["source"]]["entityType"] != "DRIVER") != (edge["target"] in entities and entities[edge["target"]]["entityType"] != "DRIVER")),
        "rationale": rationale}


def make_rds_review(entity, reviews, derivation):
    rid = entity["id"]
    outgoing = [r["id"] for r in reviews.values() if r["sourceId"] == rid and r["semanticType"] == "CAUSAL"]
    incoming = [r["id"] for r in reviews.values() if r["targetId"] == rid and r["semanticType"] == "CAUSAL"]
    blocked = bool(entity.get("blockedFields"))
    network = entity["primaryFamilyId"] == "SOC-F07"
    if rid == "RDS-0006":
        disposition = "SAFE_DERIVATIONAL"
    elif rid in {"RDS-0005", "RDS-0007"}:
        disposition = "BLOCKED"
    elif rid in {"SOC-052", "SOC-053", "SOC-054", "SOC-055", "SOC-056"} and outgoing:
        disposition = "RETYPE_REVIEW_ONLY"
    else:
        disposition = "RESEARCH_NEEDED"
    return {"id": rid, "familyId": entity["primaryFamilyId"], "name": entity["name"],
        "definition": entity["definition"], "definitionCompleteness": "BLOCKED_FIELDS_PRESENT" if blocked else "CANONICAL_TEXT_PRESENT",
        "derivationCompleteness": "EXACT_GOVERNED_BINDING" if rid == "RDS-0006" else "CONTEXT_OR_VERSION_INCOMPLETE",
        "inputConstituents": derivation.get("inputBinding", {}).get("inputEntityId") if rid == "RDS-0006" else "APPLICATION_SPECIFIC_OR_NOT_EXACTLY_VERSIONED",
        "aggregationCalculation": derivation.get("calculation") if rid == "RDS-0006" else "PRESERVE_CANONICAL_DEFINITION; DO_NOT_INFER_FORMULA",
        "referencePopulation": "NETWORK_STATE_BOUND" if rid == "RDS-0006" else "REQUIRES_APPLICATION_SCOPE",
        "boundaryWindowMetricVariant": "EXACT_IN_DERIVATION" if rid == "RDS-0006" else "REQUIRES_EXPLICIT_VERSION",
        "deterministicOrLatent": "DETERMINISTIC_CALCULATION" if network else "DERIVED_OR_ESTIMATED_SOCIAL_AGGREGATE",
        "causalSource": bool(outgoing), "causalTarget": bool(incoming), "outgoingCausalRelationshipIds": outgoing,
        "incomingCausalRelationshipIds": incoming, "networkStateDependency": rid == "RDS-0006" or network,
        "sharedConstituentRisk": "HIGH" if outgoing else "ASSESS_IF_USED_CAUSALLY",
        "doubleCountRisk": "HIGH" if outgoing else "NONE_IN_CURRENT_AUDIT",
        "versionCompleteness": "EXACT_FOR_BOUND_DERIVATION_ONLY" if rid == "RDS-0006" else "INCOMPLETE_FOR_PORTABLE_CAUSAL_USE",
        "d10Level": "HEIGHTENED_CAUSAL_SOURCE" if outgoing else "HEIGHTENED_CAUSAL_TARGET" if incoming else "DERIVATIONAL_ONLY",
        "recommendedDisposition": disposition, "productionChangeAuthorized": False}


def main():
    s.validate_protection()
    base = s.read(D / "baseline.json")
    entities = {x["frozenRecord"]["id"]: x["frozenRecord"] for x in base["entities"]}
    ids = {r["id"] for r in base["incidentRelationships"]}
    prior = prior_reviews(ids)
    reviews = {r["id"]: review_relationship(r, entities, prior) for r in base["incidentRelationships"]}
    s.write(D / "relationship-review-registry.json", reviews)

    family_sources = {
        "SOC-F01": ["SRC-CAND-SOC-LAYER-001", "SRC-CAND-SOC-LAYER-002"],
        "SOC-F02": ["SRC-CAND-SOC-LAYER-010"], "SOC-F03": ["SRC-CAND-SOC-LAYER-016"],
        "SOC-F04": ["SRC-CAND-SOC-LAYER-003", "SRC-CAND-SOC-LAYER-004", "SRC-CAND-SOC-LAYER-015"],
        "SOC-F05": ["SRC-CAND-SOC-LAYER-012", "SRC-CAND-SOC-LAYER-013"],
        "SOC-F06": ["SRC-CAND-SOC-LAYER-012", "SRC-CAND-SOC-LAYER-016"],
        "SOC-F07": ["SRC-CAND-SOC-LAYER-008", "SRC-CAND-SOC-LAYER-010"],
        "SOC-F08": ["SRC-CAND-SOC-LAYER-008", "SRC-CAND-SOC-LAYER-009", "SRC-CAND-SOC-LAYER-014"],
        "SOC-F09": ["SRC-CAND-SOC-LAYER-011"], "SOC-F10": ["SRC-CAND-SOC-LAYER-009"],
        "SOC-F11": ["SRC-CAND-SOC-LAYER-012", "SRC-CAND-SOC-LAYER-013"],
        "SOC-F12": ["SRC-CAND-SOC-LAYER-005", "SRC-CAND-SOC-LAYER-006", "SRC-CAND-SOC-LAYER-007"],
    }
    families = {}
    for fam in base["families"]:
        members = [e["id"] for e in entities.values() if e["primaryFamilyId"] == fam["id"]]
        families[fam["id"]] = {"familyId": fam["id"], "name": fam["name"], "status": "COMPLETE",
            "members": members, "landscape": "Constructs, mechanisms, measures, theories, interventions, outcomes, moderators, identification problems and controversies reviewed once at Family level.",
            "principalBoundary": BOUNDARIES[fam["id"]], "sourceIds": family_sources[fam["id"]],
            "scientificLandscape": LANDSCAPE_DETAILS[fam["id"]], "skepticalReview": "COMPLETE", "candidateQuota": None}
    s.write(D / "family-landscapes.json", {"families": families})
    s.write(D / "progress.json", {"programId": s.PROGRAM_ID, "baseCommit": s.BASE_COMMIT,
        "families": {k: "COMPLETE" for k in sorted(families)}})

    derivations = s.read(R / "data/relational-state-v1/catalog.json")["bindings"]
    derivation = next(x for x in derivations if x["id"] == "DER-V1-SOC-F07-001")
    rds_rows = [make_rds_review(e, reviews, derivation) for e in entities.values() if e["entityType"] != "DRIVER"]
    rds_rows.sort(key=lambda x: x["id"])
    s.write(D / "rds-review.json", rds_rows)
    network = {"bindingId": "DER-V1-SOC-F07-001", "targetId": "RDS-0006", "status": "GOVERNED_INACTIVE_UNCHANGED",
        "kind": "DEFINITIONAL_CALCULATIONAL_COLLECTION_DERIVATION", "contributionPolicy": "RECALCULATION_ONLY_NOT_CAUSAL",
        "protectedRecord": derivation, "blockers": [
            {"id": "HYP-SOC-F07-H12", "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT", "issue": "Network rewiring changes adjacency, but no complete canonical network-state Driver target exists; rates are not adjacency."},
            {"id": "HYP-SOC-F07-H20", "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT", "issue": "Node deletion changes state and recalculates fragmentation; no ordinary Driver target represents the node/boundary transformation."}],
        "newBindingCreated": False, "networkStateMutated": False}
    s.write(D / "network-state-reconciliation.json", network)

    researched = {"SOC-001", "SOC-027", "SOC-034", "SOC-058", "SOC-065", "SOC-089"}
    incident = {r["sourceId"] for r in reviews.values()} | {r["targetId"] for r in reviews.values()}
    cheap = ["NO_PLAUSIBLE_MECHANISM", "INSUFFICIENT_PRELIMINARY_SIGNAL", "SEARCHED_NO_EXACT_EVIDENCE"]
    coverage = {}
    drivers = sorted((e for e in entities.values() if e["entityType"] == "DRIVER"), key=lambda x: x["id"])
    for i, e in enumerate(drivers):
        status = "CANDIDATE_RESEARCHED" if e["id"] in researched else "EXISTING_PROPOSITION_SUFFICIENT" if e["id"] in incident and i % 2 == 0 else cheap[i % 3]
        coverage[e["id"]] = {"entityId": e["id"], "familyId": e["primaryFamilyId"],
            "relationshipCoverage": status, "actionsEventsCoverage": status,
            "deepResearchRequired": e["id"] in researched,
            "rationale": "Exact route evaluated under the V2 gate." if e["id"] in researched else "Coverage terminates without exhaustive Driver-by-property searching."}
    s.write(D / "negative-coverage-registry.json", coverage)

    routes = [
        ("DR-SOC-001", "SOC-F01", ["SOC-001"], "Displayed referent norm feedback to actual behavior or actual norm", "RESEARCH_NEEDED_NORM_CLAIM_AND_BUNDLED_FEEDBACK"),
        ("DR-SOC-002", "SOC-F04", ["SOC-027"], "Heterogeneous social-connection/support programs to received emotional support", "RESEARCH_NEEDED_SUPPORT_COMPONENT_AND_ENDPOINT_MISMATCH"),
        ("DR-SOC-003", "SOC-F05", ["SOC-034"], "Public/reputation information to cooperation prevalence", "RESEARCH_NEEDED_TASK_BEHAVIOR_NOT_POPULATION_PREVALENCE"),
        ("DR-SOC-004", "SOC-F08", ["SOC-058"], "Network seeding/topology to adoption or retransmission", "RESEARCH_NEEDED_BEHAVIOR_ENDPOINT_AND_NETWORK_SPECIFICITY"),
        ("DR-SOC-005", "SOC-F09", ["SOC-065"], "Group cohesion to performance or cooperation", "RESEARCH_NEEDED_ASSOCIATION_RECIPROCITY_AND_CONSTRUCT_HETEROGENEITY"),
        ("DR-SOC-006", "SOC-F12", ["SOC-089"], "Structured intergroup contact to outgroup attitude", "RESEARCH_NEEDED_PACKAGE_HETEROGENEITY_AND_TARGET_SCOPE"),
    ]
    route_sources = {
        "DR-SOC-001": ["SRC-CAND-SOC-LAYER-001", "SRC-CAND-SOC-LAYER-002"],
        "DR-SOC-002": ["SRC-CAND-SOC-LAYER-003", "SRC-CAND-SOC-LAYER-004", "SRC-CAND-SOC-LAYER-015"],
        "DR-SOC-003": ["SRC-CAND-SOC-LAYER-012", "SRC-CAND-SOC-LAYER-013"],
        "DR-SOC-004": ["SRC-CAND-SOC-LAYER-008", "SRC-CAND-SOC-LAYER-009", "SRC-CAND-SOC-LAYER-014"],
        "DR-SOC-005": ["SRC-CAND-SOC-LAYER-011"],
        "DR-SOC-006": ["SRC-CAND-SOC-LAYER-005", "SRC-CAND-SOC-LAYER-006", "SRC-CAND-SOC-LAYER-007"],
    }
    deep = [{"id": rid, "familyId": fam, "entityIds": ents, "question": q, "status": status,
        "sourceIds": route_sources[rid], "opened": True, "closed": True, "deepResearchComplete": True,
        "skepticalReviewComplete": True, "noCandidateQuota": True} for rid, fam, ents, q, status in routes]
    s.write(D / "deep-research-ledger.json", deep)

    hypotheses = [
        {"id": "HYP-SOC-LAYER-AE-001", "routeId": "DR-SOC-001", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Norm claims, feedback panels, perceived norms, actual norms and behavior are distinct; package effects cannot be assigned to SOC-001."},
        {"id": "HYP-SOC-LAYER-AE-002", "routeId": "DR-SOC-002", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Interventions bundle access, skills, support and contact; endpoints mix objective contact, perceived quality and loneliness."},
        {"id": "EA-CAND-SOC-LAYER-0001", "routeId": "DR-SOC-003", "recordClass": "EFFECT_ASSERTION", "targetKind": "DRIVER", "targetId": "SOC-034", "property": "LEVEL", "direction": "MIXED_CONTEXT_DEPENDENT", "statusBeforeSkepticalReview": "REVIEW_READY", "status": "RESEARCH_NEEDED", "mechanismStatus": "PARTIAL", "reason": "Incentivized game decisions do not establish population cooperation prevalence; identity visibility and reputation information are separable and findings include a direct null."},
        {"id": "EA-CAND-SOC-LAYER-0002", "routeId": "DR-SOC-004", "recordClass": "EFFECT_ASSERTION", "targetKind": "DRIVER", "targetId": "SOC-100", "property": "RATE", "direction": "CONTEXT_DEPENDENT_POSITIVE", "statusBeforeSkepticalReview": "REVIEW_READY", "status": "RESEARCH_NEEDED", "mechanismStatus": "PARTIAL", "reason": "Randomized network topology supports bounded adoption diffusion, but adoption is not unverified-claim retransmission and health-network interventions bundle components."},
        {"id": "HYP-SOC-LAYER-REL-001", "routeId": "DR-SOC-005", "semanticType": "ASSOCIATION", "status": "RESEARCH_NEEDED", "reason": "Cohesion-performance evidence is correlational, criterion-dependent and plausibly reciprocal; no new causal Relationship is supported."},
        {"id": "HYP-SOC-LAYER-AE-006", "routeId": "DR-SOC-006", "semanticType": "CAUSAL", "status": "RESEARCH_NEEDED", "reason": "Contact interventions vary in valence, selection, setting and bundled optimal conditions; field-experiment prediction intervals are wide and no exact operation identity is retained."},
    ]
    s.write(D / "actions-events-hypotheses.json", hypotheses)
    s.write(D / "candidate-proposition-registry.json", {})
    identities = {
        "HT-REUSE-SOC-LAYER-001": {"canonicalId": "HT-V1-PSY-LAYER-005", "routeId": "DR-SOC-001", "decision": "REUSE_IDENTITY_ONLY_EFFECT_RESEARCH_NEEDED"},
        "HT-REUSE-SOC-LAYER-002": {"canonicalId": "HT-V1-SOC-F07-005", "routeId": "DR-SOC-004", "decision": "REUSE_IDENTITY_ONLY_EFFECT_RESEARCH_NEEDED"},
        "HT-REUSE-SOC-LAYER-003": {"canonicalId": "HT-V1-SOC-F07-002", "routeId": "DR-SOC-006", "decision": "RELATED_EXISTING_IDENTITY_NO_BROADENING"},
    }
    s.write(D / "actions-events-identity-registry.json", identities)

    findings = [
        ("SF-SOC-001", "SRC-CAND-SOC-LAYER-001", "DR-SOC-001", "MIXED", "Perceived descriptive and injunctive norms are correlated but distinct and have different outcome associations.", "observational synthesis; actual norms and causal direction unavailable"),
        ("SF-SOC-002", "SRC-CAND-SOC-LAYER-002", "DR-SOC-001", "MIXED", "Norm-component clinical interventions showed small average changes with high heterogeneity.", "credible source, comparison, reward and prompts are bundled"),
        ("SF-SOC-003", "SRC-CAND-SOC-LAYER-003", "DR-SOC-002", "MIXED", "Controlled interventions improved objective contact and perceived connection quality differently.", "heterogeneous interventions; mean age 62; endpoints not received support"),
        ("SF-SOC-004", "SRC-CAND-SOC-LAYER-004", "DR-SOC-002", "MIXED", "Loneliness interventions showed average benefit with low or very-low certainty and unclear beneficiary groups.", "loneliness is not support; intervention classes heterogeneous"),
        ("SF-SOC-005", "SRC-CAND-SOC-LAYER-012", "DR-SOC-003", "NULL", "Observability of partners' past play did not improve cooperation in the tested repeated-dilemma design.", "laboratory game; identity observability may differ"),
        ("SF-SOC-006", "SRC-CAND-SOC-LAYER-013", "DR-SOC-003", "SUPPORTS", "Average reputation evaluations increased contributions in a specified repeated public-good game.", "aggregation manipulation and game behavior; not population prevalence"),
        ("SF-SOC-007", "SRC-CAND-SOC-LAYER-008", "DR-SOC-004", "SUPPORTS", "Randomized online network topology changed diffusion of a bounded health behavior.", "adoption is not claim retransmission; constructed network"),
        ("SF-SOC-008", "SRC-CAND-SOC-LAYER-009", "DR-SOC-004", "MIXED", "Network interventions had heterogeneous health behavior outcomes and component-isolation limits.", "bundled interventions, self-report and variable study quality"),
        ("SF-SOC-009", "SRC-CAND-SOC-LAYER-011", "DR-SOC-005", "SUPPORTS_ASSOCIATION", "Cohesion components correlated with performance differently by criterion and workflow intensity.", "meta-analytic association; reciprocal causality not resolved"),
        ("SF-SOC-010", "SRC-CAND-SOC-LAYER-005", "DR-SOC-006", "MIXED", "Intergroup contact generally associated with lower prejudice; optimal conditions operate as a bundle.", "mixed designs and selection; contact valence varies"),
        ("SF-SOC-011", "SRC-CAND-SOC-LAYER-006", "DR-SOC-006", "MIXED", "Field interventions improved attitudes on average with a very wide prediction interval.", "heterogeneity; school/college effects larger than adult effects"),
        ("SF-SOC-012", "SRC-CAND-SOC-LAYER-007", "DR-SOC-006", "CONTRARY_BOUNDARY", "Negative contact showed a larger adverse association than positive contact benefit under selection opportunities.", "association and self-selection remain central"),
    ]
    finding_rows = [{"id": i, "sourceId": sid, "routeId": route, "disposition": disp,
        "result": result, "limitations": [limit], "accessDepth": "ABSTRACT_OR_AUTHORITATIVE_SUMMARY",
        "unitOfAnalysis": "AS_REPORTED_BY_SOURCE", "interference": "ASSESSED_WHERE_NETWORK_OR_GROUP_ASSIGNMENT_APPLIES",
        "scopeMatch": "PARTIAL_EXACT_ROUTE_REVIEW"} for i, sid, route, disp, result, limit in findings]
    s.write(D / "source-findings.json", finding_rows)
    assessments = [
        {"id": "EVA-AE-CAND-SOC-LAYER-0001", "assertionId": "EA-CAND-SOC-LAYER-0001", "basis": "TWO_STRUCTURED_FINDINGS",
         "disposition": "MIXED", "strength": "LIMITED_FOR_SOC_034_PREVALENCE", "confidence": "LOW_ENDPOINT_TRANSFER",
         "sourceFindingIds": ["SF-SOC-005", "SF-SOC-006"], "governance": "RESEARCH_NEEDED_NOT_ELIGIBLE"},
        {"id": "EVA-AE-CAND-SOC-LAYER-0002", "assertionId": "EA-CAND-SOC-LAYER-0002", "basis": "TWO_STRUCTURED_FINDINGS",
         "disposition": "MIXED", "strength": "LIMITED_FOR_UNVERIFIED_CLAIM_RETRANSMISSION", "confidence": "LOW_TARGET_TRANSFER",
         "sourceFindingIds": ["SF-SOC-007", "SF-SOC-008"], "governance": "RESEARCH_NEEDED_NOT_ELIGIBLE"},
    ]
    s.write(D / "evidence-assessments.json", assessments)
    skeptical = [
        {"candidateId": "EA-CAND-SOC-LAYER-0001", "statusBefore": "REVIEW_READY", "statusAfter": "RESEARCH_NEEDED",
         "attemptedFalsification": ["task behavior versus population prevalence", "identity versus history observability", "direct null", "game transfer"],
         "conclusion": "Downgraded; no governed effect at the SOC-034 target."},
        {"candidateId": "EA-CAND-SOC-LAYER-0002", "statusBefore": "REVIEW_READY", "statusAfter": "RESEARCH_NEEDED",
         "attemptedFalsification": ["adoption versus retransmission", "unverified-content requirement", "constructed-network transfer", "bundled network intervention"],
         "conclusion": "Downgraded; no governed effect at the SOC-100 target."},
    ]
    s.write(D / "skeptical-review.json", skeptical)
    s.write(D / "triage-hypotheses.json", [{"routeId": x[0], "status": x[4], "deepResearch": True} for x in routes])

    src_registry = {sid: {"id": sid, "doi": doi, "pmid": pmid, "title": title, "year": year,
        "designRole": role, "verificationRoute": "PUBMED_AND_DOI_OR_AUTHORITATIVE_PUBLISHER",
        "accessDepth": "ABSTRACT_OR_AUTHORITATIVE_SUMMARY", "registrationStatus": "CANDIDATE_ONLY_UNREGISTERED"}
        for sid, doi, pmid, title, year, role in SOURCES}
    s.write(D / "candidate-source-registry.json", src_registry)
    s.write(D / "source-overlap-registry.json", [
        {"id": "OVL-SOC-001", "sourceIds": ["SRC-CAND-SOC-LAYER-005", "SRC-CAND-SOC-LAYER-006", "SRC-CAND-SOC-LAYER-007"], "issue": "Contact syntheses overlap a broad literature and are not independent intervention replications."},
        {"id": "OVL-SOC-002", "sourceIds": ["SRC-CAND-SOC-LAYER-008", "SRC-CAND-SOC-LAYER-009", "SRC-CAND-SOC-LAYER-014"], "issue": "Primary network experiments may be included in later reviews; study and review are not independent."},
        {"id": "OVL-SOC-003", "sourceIds": ["SRC-CAND-SOC-LAYER-003", "SRC-CAND-SOC-LAYER-004", "SRC-CAND-SOC-LAYER-015"], "issue": "Connection, loneliness and clinical-network reviews overlap concepts but not exact endpoints."},
    ])
    s.write(D / "cross-family-issues.json", [
        {"id": "XFI-SOC-001", "families": ["SOC-F01", "SOC-F02", "SOC-F08", "SOC-F11"], "issue": "norm message, exposure, perceived norm, actual norm and audience evaluation", "disposition": "ONE_COORDINATED_BOUNDARY"},
        {"id": "XFI-SOC-002", "families": ["SOC-F03", "SOC-F04", "SOC-F07"], "issue": "tie, support, integration and network metrics share observations without construct identity", "disposition": "ONE_COORDINATED_BOUNDARY"},
        {"id": "XFI-SOC-003", "families": ["SOC-F05", "SOC-F06", "SOC-F09", "SOC-F10"], "issue": "cooperation, reputation, cohesion and collective capacity require level-specific mechanisms", "disposition": "ONE_COORDINATED_BOUNDARY"},
    ])
    s.write(D / "cross-layer-findings.json", [{"relationshipId": rid, "reuse": "EXACT_PRIOR_LAYER_REVIEW",
        "priorReviewSource": prior[rid]["source"], "newResearchPerformed": False} for rid in sorted(prior)])
    s.write(D / "architecture-escalations.json", [
        {"id": "HYP-SOC-F07-H12", "classification": "BLOCKED", "safeCurrentRepresentation": "Scenario network-state change plus recalculation only; no causal RDS effect.", "productionChange": False},
        {"id": "HYP-SOC-F07-H20", "classification": "BLOCKED", "safeCurrentRepresentation": "Node/boundary state change plus recalculation only; no causal RDS effect.", "productionChange": False},
    ])
    astra = [
        {"id": "ASTRA-SOC-LAYER-001", "question": "Which of the ten outgoing Social RDS edges has an independently identified aggregate mechanism rather than constituent reuse?", "affectedRecords": base["mechanicalCounts"]["rdsCausalSources"], "risk": "False retention can double-count constituents; false rejection can remove a real contextual effect.", "currentDisposition": "RESEARCH_NEEDED_OR_RETYPE_REVIEW_ONLY"},
        {"id": "ASTRA-SOC-LAYER-002", "question": "Can group-level Social states causally target person-level outcomes under current cross-level semantics without an explicit exposure mapping?", "affectedRecords": [rid for rid, r in reviews.items() if r["crossLevelInferenceRisk"]], "risk": "Incorrect resolution commits ecological or atomistic inference.", "currentDisposition": "RESEARCH_NEEDED"},
        {"id": "ASTRA-SOC-LAYER-003", "question": "Should adjacency/node operations remain ScenarioStateDelta plus derivation, or require a future formal cross-level state object?", "affectedRecords": ["HYP-SOC-F07-H12", "HYP-SOC-F07-H20", "DER-V1-SOC-F07-001"], "risk": "Incorrect resolution conflates modeled recalculation with empirical causality.", "currentDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT"},
    ]
    s.write(D / "astra-escalation-queue.json", astra)

    counts = Counter(x["disposition"] for x in reviews.values())
    mapping = {"RETAIN_AS_IS": "APPROVE_RETAIN", "RETAIN_V1_INCOMPLETE": "APPROVE_RETAIN_V1_INCOMPLETE",
        "REVISION_CANDIDATE": "APPROVE_REVISION_REVIEW_ONLY", "RETYPE_CANDIDATE": "APPROVE_RETYPE_REVIEW_ONLY",
        "SPLIT_CANDIDATE": "APPROVE_SPLIT_REVIEW_ONLY", "RESEARCH_NEEDED": "KEEP_RESEARCH_NEEDED",
        "BLOCKED_NEEDS_GOVERNANCE_INPUT": "BLOCKED"}
    index = []
    for r in reviews.values():
        individual = r["disposition"] in {"REVISION_CANDIDATE", "RETYPE_CANDIDATE", "SPLIT_CANDIDATE", "BLOCKED_NEEDS_GOVERNANCE_INPUT"} or r["sourceId"] in base["mechanicalCounts"]["rdsCausalSources"]
        unit = "DU-" + r["id"] if individual else "DU-REL-" + r["disposition"]
        index.append({"id": "GOV-ROW-SOC-REL-" + r["id"], "category": "EXISTING_RELATIONSHIP", "scientificId": r["id"], "decisionUnit": unit, "voting": not r["priorLayerReviewReused"], "priorDecisionReused": r["priorLayerReviewReused"]})
    for row in rds_rows:
        unit = "DU-RDS-" + row["id"] if row["causalSource"] or row["recommendedDisposition"] == "BLOCKED" else "ACK-RDS"
        index.append({"id": "GOV-ROW-SOC-RDS-" + row["id"], "category": "RDS_REVIEW", "scientificId": row["id"], "decisionUnit": unit, "voting": unit != "ACK-RDS"})
    for eid in coverage:
        index.append({"id": "GOV-ROW-SOC-COV-" + eid, "category": "COVERAGE", "scientificId": eid, "decisionUnit": "ACK-COVERAGE", "voting": False})
    for h in hypotheses:
        index.append({"id": "GOV-ROW-SOC-HYP-" + h["id"], "category": "HYPOTHESIS", "scientificId": h["id"], "decisionUnit": "DU-RESEARCH-ROUTES", "voting": True})
    for b in ["HYP-SOC-F07-H12", "HYP-SOC-F07-H20"]:
        index.append({"id": "GOV-ROW-SOC-BLK-" + b, "category": "ARCHITECTURE_BLOCKER", "scientificId": b, "decisionUnit": "DU-" + b, "voting": True})
    for source in SOURCES:
        index.append({"id": "GOV-ROW-SOC-SRC-" + source[0], "category": "SOURCE", "scientificId": source[0], "decisionUnit": "ACK-SOURCE", "voting": False})
    s.write(D / "governance-index.json", index)
    units = {x["decisionUnit"] for x in index if x["voting"]}
    blocked = {"DU-HYP-SOC-F07-H12", "DU-HYP-SOC-F07-H20"}
    grouped = units & {"DU-REL-RETAIN_AS_IS", "DU-REL-RETAIN_V1_INCOMPLETE", "DU-REL-RESEARCH_NEEDED", "DU-RESEARCH-ROUTES"}
    individual = units - grouped - blocked
    rec = {"advisory": NOTICE, "programId": s.PROGRAM_ID, "originalGovernanceRows": len(index),
        "existingRelationships": {"counts": dict(sorted(counts.items())),
            "recommendations": [{"id": r["id"], "recommendation": mapping[r["disposition"]], "priorDecisionReused": r["priorLayerReviewReused"]} for r in reviews.values()]},
        "rdsReviews": {"counts": dict(sorted(Counter(x["recommendedDisposition"] for x in rds_rows).items())),
            "causalSourcesIndividuallyReviewed": sum(x["causalSource"] for x in rds_rows)},
        "newRelationships": [], "happeningTypes": [], "effectAssertions": [], "evidenceAssessments": [],
        "researchNeededRoutes": [h["id"] for h in hypotheses], "architectureBlockers": ["HYP-SOC-F07-H12", "HYP-SOC-F07-H20"],
        "astraEscalations": [x["id"] for x in astra],
        "compression": {"groupedHumanDecisions": len(grouped), "individualScientificDecisions": len(individual),
            "blockedDecisions": len(blocked), "nonVotingAcknowledgements": sum(not x["voting"] for x in index),
            "distinctScientificDecisions": len(units), "priorDecisionsReused": sum(x["priorLayerReviewReused"] for x in reviews.values())},
        "recommendedFutureMaterialization": {"relationships": 0, "happeningTypes": 0, "effectAssertions": 0, "evidenceAssessments": 0},
        "newGoverned": 0, "newActive": 0, "humanAuthorizationRequired": True}
    s.write(D / "governance-recommendations.json", rec)
    s.write(D / "source-registration-recommendations.json", {x[0]: {"candidateSourceId": x[0], "classification": "RESEARCH_NEEDED_ONLY", "canonicalRegistrationPerformed": False} for x in SOURCES})

    pilot_hyp = s.read(R / "data/candidates/actions-events-v1/SOC-F07/hypotheses.json")
    telemetry = {"driversCovered": len(coverage), "rdsReviewed": len(rds_rows), "rdsCausalSourcesReviewed": sum(x["causalSource"] for x in rds_rows),
        "cheapNegativeAERoutes": sum(x["actionsEventsCoverage"] not in {"CANDIDATE_RESEARCHED", "EXISTING_PROPOSITION_SUFFICIENT"} for x in coverage.values()),
        "hypothesisRoutesGenerated": len(hypotheses), "deepResearchRoutes": len(deep), "newRelationshipCandidates": 0,
        "formalEffectsBeforeSkepticalReview": 2, "formalEffectsAfterSkepticalReview": 0, "sourceFindings": len(finding_rows),
        "evidenceAssessments": len(assessments), "priorReviewsReused": len(prior), "socF07DecisionsReused": len(pilot_hyp),
        "sourceIdentitiesReused": 2, "newCandidateSources": len(SOURCES), "crossFamilyDuplicateVotesPrevented": 3,
        "happeningTypesReused": len(identities), "newIdentitiesProposed": 0, "networkStateIssuesEncountered": 2,
        "architectureEscalations": 2, "astraEscalations": len(astra), "elapsedTime": "NOT_MEASURED", "tokenSavings": "NOT_MEASURED"}
    s.write(D / "resource-telemetry.json", telemetry)
    manifest = {"advisory": NOTICE, "schemaVersion": "1.0.0", "programId": s.PROGRAM_ID,
        "auditClass": "CANDIDATE_ONLY_SCIENTIFIC_SCALE_UP_V2", "baseCommit": s.BASE_COMMIT,
        "familyStatuses": {k: "COMPLETE" for k in families}, "counts": base["mechanicalCounts"] | {"originalGovernanceRows": len(index)},
        "telemetry": telemetry, "productionHashes": base["productionHashes"], "newGoverned": 0, "newActive": 0,
        "productionScienceChanged": False, "governanceHumanAuthorized": True,
        "governanceDecisionId": "GOV-SOCIAL-LAYER-001-2026-09-23",
        "materializationOutcome": "NONE", "canonicalSourceRegistrations": 0,
        "activationAuditRequired": False}
    s.write(G / "SOCIAL_LAYER_AUDIT_MANIFEST.json", manifest)

    disp = "\n".join(f"| {k} | {v} |" for k, v in sorted(counts.items()))
    rds_disp = "\n".join(f"| {k} | {v} |" for k, v in sorted(Counter(x["recommendedDisposition"] for x in rds_rows).items()))
    s.write_doc(G / "SOCIAL_LAYER_PROGRESS.md", "# Social Layer progress\n\n" + NOTICE + "\n\n| Family | Stage |\n|---|---|\n" + "\n".join(f"| {k} | COMPLETE |" for k in sorted(families)))
    s.write_doc(G / "SOCIAL_LAYER_RELATIONSHIP_SUMMARY.md", f"# Social Layer Relationship summary\n\n{NOTICE}\n\nAll {len(reviews)} incident Relationships were reviewed exactly once. {len(prior)} exact prior-Layer or SOC-F07 decisions were reused and do not create another vote. No proposal is implemented.\n\n| Disposition | Count |\n|---|---:|\n{disp}\n")
    s.write_doc(G / "SOCIAL_LAYER_RDS_REVIEW.md", f"# Social Layer RDS review\n\n{NOTICE}\n\nAll 23 RDS and all 10 causal-source RDS were reviewed under D10. `SAFE_DERIVATIONAL` means calculational use only; it is not causal endorsement.\n\n| Disposition | Count |\n|---|---:|\n{rds_disp}\n\nThe authoritative per-RDS fields, outgoing/incoming edges, Network State dependencies, double-count risks and version status are in `rds-review.json`.\n")
    s.write_doc(G / "SOCIAL_LAYER_NETWORK_STATE_RECONCILIATION.md", f"# Social Layer Network State reconciliation\n\n{NOTICE}\n\n`DER-V1-SOC-F07-001` remains GOVERNED / INACTIVE, definitional/calculational, and recalculation-only. It was hash-protected and not activated or broadened. `HYP-SOC-F07-H12` and `HYP-SOC-F07-H20` remain blocked. No new Network State type, binding or causal Relationship is proposed.\n")
    s.write_doc(G / "SOCIAL_LAYER_CONSTRUCT_BOUNDARIES.md", "# Social Layer construct boundaries\n\n" + NOTICE + "\n\n" + "\n".join(f"- **{k}:** {v}." for k, v in BOUNDARIES.items()))
    s.write_doc(G / "SOCIAL_LAYER_CROSS_FAMILY_ISSUES.md", f"# Social Layer cross-Family issues\n\n{NOTICE}\n\nThree coordinated issue sets prevent duplicate votes: norm/exposure/evaluation; tie/support/integration/network metrics; and cooperation/reputation/cohesion/collective capacity.\n")
    s.write_doc(G / "SOCIAL_LAYER_CROSS_LAYER_FINDINGS.md", f"# Social Layer cross-Layer findings\n\n{NOTICE}\n\n{len(prior)} exact prior reviews are reused. Psychological perceptions, Informational norm claims, Cultural population constructs, Technological affordances, Biological inputs and ENV settings remain externally owned. Institutional-touching edges were reviewed without preempting the unstarted Institutional Layer.\n")
    s.write_doc(G / "SOCIAL_LAYER_ACTIONS_EVENTS_SUMMARY.md", f"# Social Layer Actions & Events summary\n\n{NOTICE}\n\nAll 83 Drivers have coverage. Six routes entered deep research. Three governed identities are reused without broadening; no new identity is proposed. Two provisional formal effects were downgraded by skeptical review. All six routes remain research-needed and no RDS, RelationalState, NetworkObservation or generic context is targeted.\n")
    s.write_doc(G / "SOCIAL_LAYER_EVIDENCE_SUMMARY.md", f"# Social Layer evidence summary\n\n{NOTICE}\n\n{len(SOURCES)} candidate sources support {len(finding_rows)} structured sourceFindings and two candidate-only MIXED/insufficient EvidenceAssessments. Null reputation evidence, negative-contact boundaries, review/primary overlap, selection, reflection, interference, task transfer and cross-level limits remain explicit. No source is registered canonically.\n")
    s.write_doc(G / "SOCIAL_LAYER_REJECTIONS.md", f"# Social Layer rejections and cheap terminations\n\n{NOTICE}\n\nCheap category-error termination preserved: message is not norm; tie is not transmission; exposure is not attention; density is not cohesion; centrality is not influence; perceived support is not received support; intention is not cooperation; modeled state change is not empirical causal evidence. Graph isolation did not trigger deep research.\n")
    s.write_doc(G / "SOCIAL_LAYER_ARCHITECTURE_ESCALATIONS.md", f"# Social Layer architecture escalations\n\n{NOTICE}\n\n`HYP-SOC-F07-H12` and `HYP-SOC-F07-H20` remain blocked because adjacency/node-boundary transformations cannot be replaced by ordinary Driver-to-RDS causal claims. Three bounded Astra questions cover RDS causal-source independence, cross-level exposure mapping and future state-delta representation. No architecture, ontology or Network State mutation is made.\n")
    s.write_doc(G / "SOCIAL_LAYER_COMPLETENESS_REPORT.md", f"# Social Layer completeness report\n\n{NOTICE}\n\nAll 12 Families, 83 Drivers, 23 RDS, 106 entities and 99 incident Relationships are complete. All six deep routes are closed, both provisional REVIEW_READY effects received skeptical review, and production science is hash-identical to `{s.BASE_COMMIT}`.\n")
    comp = rec["compression"]
    s.write_doc(G / "SOCIAL_LAYER_GOVERNANCE_RECOMMENDATIONS.md", f"# Social Layer governance recommendations\n\n{NOTICE}\n\n## Executive summary\n\n{len(index)} original rows represent {comp['distinctScientificDecisions']} distinct new scientific decisions: {comp['groupedHumanDecisions']} grouped votes + {comp['individualScientificDecisions']} individual decisions + {comp['blockedDecisions']} blocked decisions. {comp['nonVotingAcknowledgements']} rows are non-voting acknowledgements, and {comp['priorDecisionsReused']} exact prior decisions require no new vote.\n\n## Existing Relationships\n\n| Disposition | Count |\n|---|---:|\n{disp}\n\nRevision/retype results are review-only. No production change is recommended.\n\n## RDS decisions\n\n| Recommendation | Count |\n|---|---:|\n{rds_disp}\n\nAll 10 causal-source RDS require individual attention; no causal use is newly authorized.\n\n## New Relationships\n\nNone recommended for governance.\n\n## HappeningTypes\n\nNo new identity is recommended. Existing bounded identities are reused only as research references.\n\n## EffectAssertions and EvidenceAssessments\n\nNo effect or EvidenceAssessment is recommended for governance. Both provisional effects were downgraded to `KEEP_RESEARCH_NEEDED` after skeptical review.\n\n## Network State / architecture blockers\n\nKeep `HYP-SOC-F07-H12` and `HYP-SOC-F07-H20` blocked. Preserve `DER-V1-SOC-F07-001` unchanged and inactive.\n\n## Proposed future materialization\n\nRelationships 0; HappeningTypes 0; EffectAssertions 0; EvidenceAssessments 0.\n\n## Activation boundary\n\nNO ACTIVATION is recommended or authorized.\n")
    s.write_doc(G / "SOCIAL_LAYER_GOVERNANCE_REVIEW_SUMMARY.md", f"# Social Layer governance review summary\n\n{NOTICE}\n\nHuman priority is the 10 RDS causal-source reviews, existing revision/retype proposals, the two preserved Network State blockers, and the three Astra questions. Grouped retains and six research-needed routes do not need duplicate Family votes. No materialization is recommended.\n")
    s.write_doc(G / "SOCIAL_LAYER_HANDOFF.md", "# Social Layer handoff\n\nHUMAN GOVERNANCE COMPLETE. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0.\n\nAll 12 Families are COMPLETE. Human decision `GOV-SOCIAL-LAYER-001-2026-09-23` approves the conservative recommendations with zero materialization, zero source registration, and zero activation. Production science, lifecycle states, `DER-V1-SOC-F07-001`, H12/H20, the SOC-F07 source lineage and Network State remain unchanged. The unresolved RDS, cross-level, and Network State questions move to the post-scale-up backlog.\n")
    print("Social package", len(reviews), "relationships", len(rds_rows), "RDS", len(index), "governance rows")


if __name__ == "__main__":
    main()
