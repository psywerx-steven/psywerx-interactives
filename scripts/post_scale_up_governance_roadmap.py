"""Build the read-only post-scale-up dependency-normalized governance roadmap."""

from __future__ import annotations

import glob
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/layer-scale-up-v2/post-scale-up-blocker-backlog.json"
COMPLETENESS = ROOT / "reports/layer-scale-up-v2/layer-scale-up-final-completeness.json"
DATA = ROOT / "data/governance/post-scale-up"
DOCS = ROOT / "docs/governance/post-scale-up"
BASE_COMMIT = "57e2bb6f559fde7fe7caa2b39e0bf6cac78615d7"
ROADMAP_ID = "POST-SCALE-UP-GOVERNANCE-ROADMAP-V1-20260924-001"
RDS_DECISION_PATH = DATA / "rds/rds-contract-architecture-decision-001.json"

ROOT_IDS = {
    "RDS_DEF": "ROOT-RDS-DEFINITION-DERIVATION-001",
    "CROSS_LEVEL": "ROOT-CROSS-LEVEL-EXPOSURE-001",
    "NETWORK": "ROOT-NETWORK-STATE-TRANSITION-001",
    "CONTRIBUTION": "ROOT-CONTRIBUTION-IDENTITY-001",
    "RDS_CAUSAL": "ROOT-RDS-CAUSAL-SOURCE-001",
    "ACTIVATION": "ROOT-ACTIVE-EFFECT-MECHANISM-001",
    "ONTOLOGY": "ROOT-CONSTRUCT-ONTOLOGY-001",
    "SOURCE": "ROOT-SOURCE-GOVERNANCE-001",
    "REL_DEBT": "ROOT-RELATIONSHIP-SEMANTIC-DEBT-001",
    "RESEARCH": "ROOT-TARGETED-EVIDENCE-001",
}

WP_IDS = {key: f"WP-PSG-{index:03d}" for index, key in enumerate(ROOT_IDS, 1)}

PROTECTED_PATHS = [
    "data/entities.json", "data/drivers.json", "data/families.json", "data/aliases.json",
    "data/sources.json", "data/relationships.json",
]
for pattern in (
    "data/relationship-intervention-v1/*",
    "data/actions-events-v1/*",
    "data/relational-state-v1/*",
):
    PROTECTED_PATHS.extend(
        Path(path).relative_to(ROOT).as_posix()
        for path in glob.glob(str(ROOT / pattern)) if Path(path).is_file()
    )
PROTECTED_PATHS = sorted(set(PROTECTED_PATHS))


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rds_direction_decision():
    if not RDS_DECISION_PATH.exists():
        return None
    decision = read(RDS_DECISION_PATH)
    assert decision["decisionPacketId"] == "DP-PSG-001"
    assert decision["workPackageId"] == "WP-PSG-001"
    assert decision["decisionOutcome"] == "APPROVED_BOUNDED_OPTION_B_PLUS_C_DIRECTION"
    assert decision["productionImplementationStatus"] == "NOT_AUTHORIZED_NOT_STARTED"
    return decision


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def protection_snapshot():
    return {path: digest(ROOT / path) for path in PROTECTED_PATHS}


def validate_or_initialize_protection():
    path = DATA / "protected-baseline.json"
    current = protection_snapshot()
    if path.exists():
        recorded = read(path)
        assert recorded["productionHashes"] == current, "Protected production science changed"
    else:
        write_json(path, {
            "schemaVersion": "1.0.0", "roadmapId": ROADMAP_ID, "sourceMain": BASE_COMMIT,
            "hashNormalization": "CRLF_TO_LF", "productionHashes": current,
        })
    return current


ROOT_DEFS = [
    {
        "key": "RDS_DEF", "title": "Shared RDS definition and derivation contract",
        "cluster": "RDS_DEFINITION_DERIVATION_GOVERNANCE", "dependencies": [], "sequenceBand": "BAND_1_FOUNDATION",
        "problem": "Affected RDS lack portable versioned contracts for inputs, aggregation, reference population, window, metric variant, normalization or constituent mapping.",
        "decision": "Select the mandatory contract and versioning rules for an RDS to be calculable and reviewable; do not decide causal-source eligibility here.",
        "options": [
            "A: require one fully versioned derivation specification for every executable RDS",
            "B: allow named derivation profiles with explicit application bindings",
            "C: retain narrative RDS as non-executable constructs until a profile is governed",
        ],
        "layers": ["Psychological", "Informational", "Biological", "Cultural", "Social", "Institutional / Structural"],
        "architecture": True, "ontology": False, "research": False,
    },
    {
        "key": "CROSS_LEVEL", "title": "Cross-level exposure and group-to-person causal semantics",
        "cluster": "CROSS_LEVEL_EXPOSURE_GOVERNANCE", "dependencies": [], "sequenceBand": "BAND_1_FOUNDATION",
        "problem": "Group, institution and network states do not automatically become exposures experienced by individual targets.",
        "decision": "Choose how membership, eligibility, implementation, contact, actual exposure, perceived exposure and response are represented without inferring a shortcut.",
        "options": [
            "A: govern an explicit typed CrossLevelExposureMapping object",
            "B: require existing Driver/HappeningType bridge records for every level transition",
            "C: add mandatory exposure-path metadata to cross-level Relationships while retaining current entity classes",
        ],
        "layers": ["Social", "Institutional / Structural", "Psychological"],
        "architecture": True, "ontology": True, "research": False,
    },
    {
        "key": "NETWORK", "title": "Network State, ScenarioStateDelta and metric recalculation boundary",
        "cluster": "NETWORK_STATE_REPRESENTATION", "dependencies": [], "sequenceBand": "BAND_1_FOUNDATION",
        "problem": "Node, tie, membership and boundary operations are being confused with empirical interventions, metric recalculation and causal effects.",
        "decision": "Assign network state, state changes, empirical operations, derivations and causal EffectAssertions to explicit non-overlapping representations.",
        "options": [
            "A: extend typed ScenarioStateDelta operations within Network State V1",
            "B: introduce a governed NetworkStateTransition record distinct from Actions & Events",
            "C: retain current recalculation-only bindings and leave unsupported operations blocked",
        ],
        "layers": ["Social"], "architecture": True, "ontology": True, "research": False,
    },
    {
        "key": "CONTRIBUTION", "title": "Contribution identity and double-count control",
        "cluster": "CONTRIBUTION_IDENTITY_DOUBLE_COUNT", "dependencies": [ROOT_IDS["RDS_DEF"], ROOT_IDS["NETWORK"]],
        "sequenceBand": "BAND_2_CONTROL",
        "problem": "One underlying contribution may appear through Relationship plus EffectAssertion, constituent plus aggregate RDS, or state recalculation plus a causal edge.",
        "decision": "Choose whether and how causal contribution identity spans representation classes without turning derivation into causality.",
        "options": [
            "A: generalize governed contribution groups across Relationship, EffectAssertion and RDS routes",
            "B: retain lineage links and enforce consumer-side mutual exclusion",
            "C: use separate class-specific controls and keep cross-class cases blocked",
        ],
        "layers": ["Psychological", "Biological", "Cultural", "Social", "Institutional / Structural"],
        "architecture": True, "ontology": False, "research": False,
    },
    {
        "key": "RDS_CAUSAL", "title": "Aggregate RDS causal-source independence",
        "cluster": "RDS_AGGREGATE_CAUSAL_SOURCE", "dependencies": [ROOT_IDS["RDS_DEF"], ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["CONTRIBUTION"]],
        "sequenceBand": "BAND_3_ADJUDICATION",
        "problem": "A defined aggregate can still double-count constituents or lack an independent aggregate mechanism, temporal order or contextual exposure route.",
        "decision": "Apply one reusable test before adjudicating any individual RDS as an independent causal source.",
        "options": [
            "A: allow only independently manipulable aggregates with distinct mechanisms",
            "B: allow contextual aggregate exposures with explicit cross-level mapping and contribution control",
            "C: prohibit aggregate causal-source use and retain aggregates as descriptive/derivational",
        ],
        "layers": ["Informational", "Biological", "Cultural", "Social", "Institutional / Structural"],
        "architecture": True, "ontology": False, "research": True,
    },
    {
        "key": "ACTIVATION", "title": "Active empirical effect versus mechanism-knowledge contract",
        "cluster": "MECHANISMSTATUS_ACTIVATION_CONTRACT", "dependencies": [], "sequenceBand": "BAND_2_CONTROL",
        "problem": "Two governed bounded effects have evidence for effect existence while mechanismStatus correctly remains UNKNOWN; the current active contract requires non-UNKNOWN mechanism knowledge.",
        "decision": "Decide whether active eligibility always requires mechanism knowledge or whether effect-existence eligibility is a distinct governed dimension.",
        "options": [
            "A: retain the current contract and keep both bundles inactive",
            "B: create a restricted active empirical-effect class with UNKNOWN mechanism and stronger scope safeguards",
            "C: separate effect-existence eligibility from mechanism-knowledge eligibility",
            "D: retain one active class but add consumer capability restrictions for unknown-mechanism effects",
        ],
        "layers": ["Physical / Environmental", "Technological"],
        "architecture": True, "ontology": False, "research": False,
    },
    {
        "key": "ONTOLOGY", "title": "Construct identity, feature and blocked-metadata governance",
        "cluster": "CONSTRUCT_CLASSIFICATION_ONTOLOGY", "dependencies": [], "sequenceBand": "BAND_1_FOUNDATION",
        "problem": "Construct overlap, feature-versus-identity questions and blocked scientific metadata are mixed under one ontology backlog class.",
        "decision": "Use separate adjudication tracks for identity equivalence, feature representation, classification and missing scientific metadata.",
        "options": [
            "A: retain distinct constructs and govern explicit mappings",
            "B: govern identity/merge only when definitions and evidence establish equivalence",
            "C: add feature or dimension representation only through separate ontology governance",
        ],
        "layers": ["Psychological", "Informational", "Technological", "Institutional / Structural"],
        "architecture": False, "ontology": True, "research": True,
    },
    {
        "key": "SOURCE", "title": "Truthful multi-route source registration contract",
        "cluster": "SOURCE_GOVERNANCE", "dependencies": [], "sequenceBand": "BAND_1_FOUNDATION",
        "problem": "Candidate provenance includes DOI/PubMed, publisher, report/book and verified non-PubMed identities with different access depths.",
        "decision": "Define identity and access-depth fields that permit canonical registration without overstating verification.",
        "options": [
            "A: identifier-specific verification profiles under one source schema",
            "B: one canonical identity record plus separate verification assertions",
            "C: retain unsupported routes in candidate queues until authoritative identifiers exist",
        ],
        "layers": ["Informational", "Social"], "architecture": False, "ontology": False, "research": False,
    },
    {
        "key": "REL_DEBT", "title": "Production Relationship semantic-debt program",
        "cluster": "RELATIONSHIP_SEMANTIC_DEBT", "dependencies": [ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["NETWORK"], ROOT_IDS["CONTRIBUTION"], ROOT_IDS["RDS_CAUSAL"], ROOT_IDS["ONTOLOGY"]],
        "sequenceBand": "BAND_4_MIGRATION_PLANNING",
        "problem": "Layer audits recorded revision, retype and split proposals, including duplicated cross-Layer reviews, without changing production.",
        "decision": "Govern deduplicated work streams after prerequisite semantics are decided; preserve proposition-level votes for science-changing migrations.",
        "options": [
            "A: migrate by semantic-defect work stream",
            "B: migrate by Layer after shared architecture decisions",
            "C: retain production and close only independently governable high-value defects",
        ],
        "layers": ["Biological", "Psychological", "Social", "Cultural", "Physical / Environmental", "Institutional / Structural", "Informational", "Technological"],
        "architecture": False, "ontology": False, "research": True,
    },
    {
        "key": "RESEARCH", "title": "Targeted evidence and inactive-knowledge program",
        "cluster": "TARGETED_EVIDENCE_RESEARCH", "dependencies": [ROOT_IDS["RDS_CAUSAL"], ROOT_IDS["ACTIVATION"], ROOT_IDS["ONTOLOGY"], ROOT_IDS["SOURCE"], ROOT_IDS["REL_DEBT"]],
        "sequenceBand": "BAND_5_TARGETED_RESEARCH",
        "problem": "Eight Layer queues mix high-value exact research, architecture-blocked questions, endpoint mismatch, identification limits and future evidence watch.",
        "decision": "Open only bounded research tasks whose target and representation are stable; keep safe inactive identities available for later evidence.",
        "options": [
            "A: research only architecture-independent high-value targets first",
            "B: wait for all shared architecture decisions before new evidence work",
            "C: operate parallel evidence-watch and architecture-dependent queues with explicit gates",
        ],
        "layers": ["Biological", "Psychological", "Social", "Cultural", "Physical / Environmental", "Institutional / Structural", "Informational", "Technological"],
        "architecture": False, "ontology": False, "research": True,
    },
]


ITEM_ROOT = {
    "A_RDS_DEFINITION_DERIVATION": "RDS_DEF",
    "B_RDS_CAUSAL_SOURCE_INDEPENDENCE": "RDS_CAUSAL",
    "C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY": "CROSS_LEVEL",
    "E_MECHANISMSTATUS_ACTIVATION_CONTRACT": "ACTIVATION",
    "F_CONSTRUCT_CLASSIFICATION_ONTOLOGY": "ONTOLOGY",
    "G_SOURCE_GOVERNANCE": "SOURCE",
    "H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS": "REL_DEBT",
    "I_CANDIDATE_SCIENCE_RESEARCH_NEEDED": "RESEARCH",
}

ITEM_DEPENDENCIES = {
    "ASTRA-BIO-LAYER-001": ["BLK-BIO-RDS-001", ROOT_IDS["CONTRIBUTION"]],
    "ASTRA-CUL-LAYER-001": ["BLK-CUL-RDS-001", ROOT_IDS["CONTRIBUTION"]],
    "ASTRA-SOC-LAYER-001": [ROOT_IDS["RDS_DEF"], ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["CONTRIBUTION"]],
    "ASTRA-INS-LAYER-001": ["BLK-INS-RDS-001", ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["CONTRIBUTION"]],
    "ASTRA-INS-LAYER-002": ["BLK-INS-RDS-001", ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["CONTRIBUTION"]],
    "HYP-SOC-F07-H12": ["ASTRA-SOC-LAYER-003"],
    "HYP-SOC-F07-H20": ["ASTRA-SOC-LAYER-003"],
    "INACTIVE-ENV-BUNDLE-001": ["BLK-ENV-ACTIVATION-001"],
    "INACTIVE-TEC-BUNDLE-001": ["BLK-TEC-ACTIVATION-001"],
}

RESEARCH_CLASS = {
    "BACKLOG-RN-PSYCHOLOGICAL_LAYER": ("INSUFFICIENT_EXACT_ENDPOINT", [ROOT_IDS["CONTRIBUTION"], ROOT_IDS["ONTOLOGY"]]),
    "BACKLOG-RN-INFORMATIONAL_LAYER": ("MEASUREMENT_LIMITED", [ROOT_IDS["RDS_DEF"], ROOT_IDS["ONTOLOGY"], ROOT_IDS["SOURCE"]]),
    "BACKLOG-RN-BIOLOGICAL_LAYER": ("MEASUREMENT_LIMITED", [ROOT_IDS["RDS_DEF"], ROOT_IDS["RDS_CAUSAL"]]),
    "BACKLOG-RN-CULTURAL_LAYER": ("IDENTIFICATION_LIMITED", [ROOT_IDS["RDS_DEF"], ROOT_IDS["RDS_CAUSAL"]]),
    "BACKLOG-RN-PHYSICAL_ENVIRONMENTAL_LAYER": ("HIGH_VALUE_TARGETED_RESEARCH", []),
    "BACKLOG-RN-TECHNOLOGICAL_LAYER": ("FUTURE_EVIDENCE_WATCH", [ROOT_IDS["ACTIVATION"], ROOT_IDS["ONTOLOGY"]]),
    "BACKLOG-RN-SOCIAL_LAYER": ("ARCHITECTURE_BLOCKED_RESEARCH", [ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["NETWORK"], ROOT_IDS["RDS_CAUSAL"]]),
    "BACKLOG-RN-INSTITUTIONAL_STRUCTURAL_LAYER": ("ARCHITECTURE_BLOCKED_RESEARCH", [ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["RDS_CAUSAL"], ROOT_IDS["ONTOLOGY"]]),
}

RELATIONSHIP_DEBT_DEPENDENCIES = {
    "BACKLOG-REL-PSYCHOLOGICAL_LAYER": [ROOT_IDS["CONTRIBUTION"], ROOT_IDS["ONTOLOGY"]],
    "BACKLOG-REL-INFORMATIONAL_LAYER": [ROOT_IDS["RDS_DEF"], ROOT_IDS["CONTRIBUTION"], ROOT_IDS["ONTOLOGY"]],
    "BACKLOG-REL-BIOLOGICAL_LAYER": [ROOT_IDS["RDS_DEF"], ROOT_IDS["RDS_CAUSAL"]],
    "BACKLOG-REL-CULTURAL_LAYER": [ROOT_IDS["RDS_DEF"], ROOT_IDS["RDS_CAUSAL"], ROOT_IDS["ONTOLOGY"]],
    "BACKLOG-REL-PHYSICAL_ENVIRONMENTAL_LAYER": [ROOT_IDS["ONTOLOGY"]],
    "BACKLOG-REL-TECHNOLOGICAL_LAYER": [ROOT_IDS["ONTOLOGY"]],
    "BACKLOG-REL-SOCIAL_LAYER": [ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["NETWORK"], ROOT_IDS["CONTRIBUTION"], ROOT_IDS["RDS_CAUSAL"]],
    "BACKLOG-REL-INSTITUTIONAL_STRUCTURAL_LAYER": [ROOT_IDS["RDS_DEF"], ROOT_IDS["CROSS_LEVEL"], ROOT_IDS["RDS_CAUSAL"], ROOT_IDS["ONTOLOGY"]],
}


def root_for(item):
    identifier = item["id"]
    if item["category"] == "D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION":
        return "CONTRIBUTION" if identifier == "BLK-PSY-003" else "NETWORK"
    if item["category"] == "J_INACTIVE_GOVERNED_BUNDLES":
        return "ACTIVATION" if "ENV" in identifier or "TEC" in identifier else "RESEARCH"
    return ITEM_ROOT[item["category"]]


def normalized_type(item):
    category, identifier = item["category"], item["id"]
    if category == "G_SOURCE_GOVERNANCE":
        return "SOURCE_DEBT"
    if category == "H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS":
        return "SEMANTIC_DEBT"
    if category == "I_CANDIDATE_SCIENCE_RESEARCH_NEEDED":
        return "SCIENTIFIC_RESEARCH_QUEUE"
    if category == "J_INACTIVE_GOVERNED_BUNDLES":
        return "DOWNSTREAM_MANIFESTATION" if "ENV" in identifier or "TEC" in identifier else "INACTIVE_BUT_SAFE"
    if identifier in {"HYP-SOC-F07-H12", "HYP-SOC-F07-H20"}:
        return "DOWNSTREAM_MANIFESTATION"
    return "DEPENDENT_BLOCKER"


def item_flags(item, key):
    category = item["category"]
    return {
        "scientificDecisionRequired": category in {"B_RDS_CAUSAL_SOURCE_INDEPENDENCE", "C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY", "D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION", "E_MECHANISMSTATUS_ACTIVATION_CONTRACT", "F_CONSTRUCT_CLASSIFICATION_ONTOLOGY", "H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS"},
        "architectureDecisionRequired": key in {"RDS_DEF", "CROSS_LEVEL", "NETWORK", "CONTRIBUTION", "RDS_CAUSAL", "ACTIVATION"},
        "ontologyDecisionRequired": key in {"CROSS_LEVEL", "NETWORK", "ONTOLOGY"},
        "sourceDecisionRequired": key == "SOURCE",
        "newResearchRequired": category == "I_CANDIDATE_SCIENCE_RESEARCH_NEEDED" or key in {"RDS_CAUSAL", "ONTOLOGY"},
        "productionMutationEventuallyRequired": category == "H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS" or item["blocksActiveExecution"],
    }


def semantic_debt_analysis():
    entity_types = {row["id"]: row["entityType"] for row in read(ROOT / "data/entities.json")}
    reviews = defaultdict(list)
    for raw in glob.glob(str(ROOT / "data/candidates/actions-events-v1/*_LAYER/relationship-review-registry.json")):
        layer = Path(raw).parent.name
        payload = read(Path(raw))
        rows = payload.values() if isinstance(payload, dict) else payload
        for row in rows:
            disposition = row.get("disposition") or row.get("primaryDisposition")
            if disposition not in {"REVISION_CANDIDATE", "RETYPE_CANDIDATE", "SPLIT_CANDIDATE"}:
                continue
            identifier = row.get("id") or row.get("frozenRecord", {}).get("id")
            reason = " ".join(filter(None, [
                row.get("rationale"), row.get("review", {}).get("rationale"),
                row.get("review", {}).get("rdsReview"), row.get("review", {}).get("nullContrary"),
            ])).lower()
            source = row.get("sourceId") or row.get("frozenRecord", {}).get("subjectEntityId")
            target = row.get("targetId") or row.get("frozenRecord", {}).get("objectEntityId")
            reviews[identifier].append({"layer": layer, "disposition": disposition, "reason": reason,
                                        "sourceId": source, "targetId": target,
                                        "crossLevel": bool(row.get("crossLevelInferenceRisk")) or "level transition" in reason})

    def stream(entries):
        dispositions = {row["disposition"] for row in entries}
        reason = " ".join(row["reason"] for row in entries)
        if "SPLIT_CANDIDATE" in dispositions:
            return "SPLIT_CONSTRUCT", [ROOT_IDS["ONTOLOGY"]]
        if any(row["crossLevel"] for row in entries):
            return "CROSS_LEVEL_REVIEW", [ROOT_IDS["CROSS_LEVEL"]]
        source_rds = any(entity_types.get(row["sourceId"]) != "DRIVER" for row in entries if row["sourceId"])
        target_rds = any(entity_types.get(row["targetId"]) != "DRIVER" for row in entries if row["targetId"])
        if source_rds:
            return "RDS_SOURCE_REVIEW", [ROOT_IDS["RDS_DEF"], ROOT_IDS["CONTRIBUTION"], ROOT_IDS["RDS_CAUSAL"]]
        if "RETYPE_CANDIDATE" in dispositions:
            if target_rds or re.search(r"formula|calculat|deriv|ratio|input|nested|inverse", reason):
                return "CAUSAL_TO_DERIVATIONAL", [ROOT_IDS["RDS_DEF"], ROOT_IDS["CONTRIBUTION"]]
            if re.search(r"associat|correlat|co-vary|covary", reason):
                return "CAUSAL_TO_ASSOCIATION", []
            return "TARGET_RETYPE", [ROOT_IDS["ONTOLOGY"]]
        if re.search(r"mediat|direct edge|directness|intervening|pathway", reason):
            return "DIRECTNESS_REVISION", []
        return "BOUNDARY_REVISION", []

    records = []
    for identifier in sorted(reviews):
        workstream, dependencies = stream(reviews[identifier])
        records.append({"relationshipId": identifier, "reviewRows": len(reviews[identifier]),
                        "reviewingLayers": sorted({row["layer"] for row in reviews[identifier]}),
                        "disposition": reviews[identifier][0]["disposition"], "workstream": workstream,
                        "dependsOnRootIssues": dependencies, "productionMutationAuthorized": False})
    return {
        "layerReviewRows": sum(row["reviewRows"] for row in records),
        "uniqueRelationships": len(records),
        "duplicateCrossLayerReviewRowsCollapsed": sum(row["reviewRows"] - 1 for row in records),
        "dispositionCountsByUniqueRelationship": dict(sorted(Counter(row["disposition"] for row in records).items())),
        "workstreamCounts": dict(sorted(Counter(row["workstream"] for row in records).items())),
        "architectureDependentRelationships": sum(bool(row["dependsOnRootIssues"]) for row in records),
        "architectureIndependentRelationships": sum(not row["dependsOnRootIssues"] for row in records),
        "records": records,
    }


def descendants(start, reverse):
    seen, todo = set(), deque(reverse.get(start, []))
    while todo:
        node = todo.popleft()
        if node in seen:
            continue
        seen.add(node)
        todo.extend(reverse.get(node, []))
    return seen


def build_dependency_map(backlog):
    item_ids = {item["id"] for item in backlog}
    reverse = defaultdict(list)
    preliminary = []
    for item in backlog:
        key = root_for(item)
        dependencies = list(ITEM_DEPENDENCIES.get(item["id"], []))
        dependencies.extend(RELATIONSHIP_DEBT_DEPENDENCIES.get(item["id"], []))
        research_class = None
        if item["id"] in RESEARCH_CLASS:
            research_class, waits = RESEARCH_CLASS[item["id"]]
            dependencies.extend(waits)
        root = next(row for row in ROOT_DEFS if row["key"] == key)
        duplicate = []
        if item["id"] in {"HYP-SOC-F07-H12", "HYP-SOC-F07-H20"}:
            duplicate = ["ASTRA-SOC-LAYER-003"]
        if item["id"] == "INACTIVE-ENV-BUNDLE-001":
            duplicate = ["BLK-ENV-ACTIVATION-001"]
        if item["id"] == "INACTIVE-TEC-BUNDLE-001":
            duplicate = ["BLK-TEC-ACTIVATION-001"]
        row = {
            "id": item["id"], "class": item["category"], "normalizedType": normalized_type(item),
            "layer": item["layer"], "affectedRecords": item["affectedRecords"],
            "blocksActiveExecution": item["blocksActiveExecution"], "rootIssueId": ROOT_IDS[key],
            "dependsOn": sorted(set(dependencies)), "blocksOrConstrains": [],
            "duplicateOrDerivativeOf": duplicate, **item_flags(item, key),
            "currentSafeState": item["currentSafeState"], "numberOfDirectDependentItems": 0,
            "numberOfIndirectDependentItems": 0,
            "estimatedScopeOfImpact": "PROGRAM_WIDE" if key in {"RDS_DEF", "CONTRIBUTION", "REL_DEBT", "RESEARCH"} else ("MULTI_LAYER" if len(root["layers"]) > 1 else "LAYER"),
            "recommendedWorkPackage": WP_IDS[key], "recommendedSequenceBand": root["sequenceBand"],
            "dependencyStatus": "PARTIALLY_DEPENDENT" if item["id"] in RESEARCH_CLASS or item["id"] in RELATIONSHIP_DEBT_DEPENDENCIES else ("DERIVATIVE" if duplicate else ("SAFE_NO_ACTION" if normalized_type(item) == "INACTIVE_BUT_SAFE" else "PREREQUISITE_PENDING")),
            "researchQueueClass": research_class,
        }
        preliminary.append(row)
        for dep in row["dependsOn"]:
            if dep in item_ids:
                reverse[dep].append(row["id"])
    by_id = {row["id"]: row for row in preliminary}
    for row in preliminary:
        direct = sorted(reverse.get(row["id"], []))
        indirect = descendants(row["id"], reverse) - set(direct)
        row["blocksOrConstrains"] = direct
        row["numberOfDirectDependentItems"] = len(direct)
        row["numberOfIndirectDependentItems"] = len(indirect)
    return {
        "schemaVersion": "1.0.0", "roadmapId": ROADMAP_ID, "sourceBacklogCheckpoint": read(SOURCE)["checkpointId"],
        "sourceBacklogItemCount": len(backlog), "sourceActiveBlockingCount": sum(row["blocksActiveExecution"] for row in backlog),
        "normalizationCounts": dict(sorted(Counter(row["normalizedType"] for row in preliminary).items())),
        "trueRootIssueCount": len(ROOT_DEFS), "items": preliminary,
    }


def build_roots(dep_map, semantic_debt):
    items_by_root = defaultdict(list)
    for item in dep_map["items"]:
        items_by_root[item["rootIssueId"]].append(item)
    root_reverse = defaultdict(list)
    for definition in ROOT_DEFS:
        for dependency in definition["dependencies"]:
            root_reverse[dependency].append(ROOT_IDS[definition["key"]])
    roots = []
    for definition in ROOT_DEFS:
        identifier = ROOT_IDS[definition["key"]]
        direct = items_by_root[identifier]
        downstream_roots = descendants(identifier, root_reverse)
        roots.append({
            "id": identifier, "title": definition["title"], "cluster": definition["cluster"],
            "problemStatement": definition["problem"], "dependencies": definition["dependencies"],
            "absorbedBacklogItemIds": [row["id"] for row in direct],
            "layersAffected": definition["layers"], "decisionRequired": definition["decision"],
            "designAlternatives": definition["options"], "architectureDecisionRequired": definition["architecture"],
            "ontologyDecisionRequired": definition["ontology"], "newResearchRequired": definition["research"],
            "recommendedWorkPackage": WP_IDS[definition["key"]], "recommendedSequenceBand": definition["sequenceBand"],
            "directOriginalItems": len(direct), "activeBlockingOriginalItems": sum(row["blocksActiveExecution"] for row in direct),
            "downstreamRootIssueIds": sorted(downstream_roots),
            "downstreamOriginalItemCount": sum(len(items_by_root[root]) for root in downstream_roots),
            "currentSafeState": "Preserve every recorded scientific, ontology, architecture and lifecycle state until a later human decision.",
        })
    return {
        "schemaVersion": "1.0.0", "roadmapId": ROADMAP_ID, "rootIssueCount": len(roots),
        "roots": roots, "relationshipSemanticDebt": semantic_debt,
        "researchQueues": [{"backlogItemId": item_id, "primaryClass": value[0], "waitsForRootIssues": value[1]}
                           for item_id, value in RESEARCH_CLASS.items()],
    }


def work_packages(roots):
    by_id = {root["id"]: root for root in roots["roots"]}
    rds_decision = rds_direction_decision()
    packages = []
    for definition in ROOT_DEFS:
        key, identifier = definition["key"], ROOT_IDS[definition["key"]]
        root = by_id[identifier]
        packages.append({
            "workPackageId": WP_IDS[key], "rootIssueId": identifier, "title": definition["title"],
            "problemStatement": definition["problem"], "backlogItemsAbsorbed": root["absorbedBacklogItemIds"],
            "layersAffected": definition["layers"], "recordsAffected": "See blocker-dependency-map affectedRecords for every absorbed item.",
            "dependencies": definition["dependencies"], "decisionsRequired": [definition["decision"]],
            "researchRequired": definition["research"], "architectureRequired": definition["architecture"],
            "ontologyRequired": definition["ontology"], "sourceGovernanceRequired": key == "SOURCE",
            "productionMigrationEventuallyRequired": key in {"RDS_DEF", "CROSS_LEVEL", "NETWORK", "CONTRIBUTION", "RDS_CAUSAL", "ACTIVATION", "ONTOLOGY", "REL_DEBT"},
            "whatCanBeDecidedAutomatically": ["inventory and dependency verification", "deduplication", "option completeness checks", "protected-state validation"],
            "whatRequiresHumanScientificGovernance": [definition["decision"], "any production migration", "any activation or causal-source authorization"],
            "entryCriteria": ["all absorbed records remain in their current safe state", "dependency inputs are documented", "protected hashes pass"],
            "exitCriteria": ["one option is explicitly human-governed", "migration scope and rollback are approved", "dependent records have a re-adjudication plan"],
            "testsRequired": ["schema and dependency DAG", "protected production hashes", "migration-specific validator tests before implementation", "dependent scientific re-adjudication"],
            "expectedDownstreamItemsUnblocked": root["directOriginalItems"] + root["downstreamOriginalItemCount"],
            "safeRollbackState": root["currentSafeState"],
            "stages": {"A_problemNormalization": "COMPLETE", "B_designAlternatives": "COMPLETE",
                       "C_skepticalArchitectureReview": "COMPLETE" if key in {"RDS_DEF", "CROSS_LEVEL", "NETWORK", "CONTRIBUTION", "RDS_CAUSAL", "ACTIVATION"} else "DEFERRED_UNTIL_SELECTED",
                       "D_humanGovernanceDecision": "COMPLETE_BOUNDED_DIRECTION_APPROVED" if key == "RDS_DEF" and rds_decision else "NOT_STARTED", "E_implementation": "NOT_STARTED",
                       "F_migrationRevalidation": "NOT_STARTED", "G_scientificReadjudication": "NOT_STARTED"},
            "governanceDecisionId": rds_decision["decisionId"] if key == "RDS_DEF" and rds_decision else None,
            "prototypeImplementationAuthorization": "AUTHORIZED_NON_PRODUCTION_ONLY" if key == "RDS_DEF" and rds_decision else "NOT_AUTHORIZED",
            "productionImplementationStatus": "NOT_AUTHORIZED_NOT_STARTED" if key == "RDS_DEF" and rds_decision else "NOT_STARTED",
            "recommendedSequenceBand": definition["sequenceBand"],
        })
    return {"schemaVersion": "1.0.0", "roadmapId": ROADMAP_ID, "workPackages": packages}


def decision_packets(roots):
    by_id = {root["id"]: root for root in roots["roots"]}
    keys = ["RDS_DEF", "CROSS_LEVEL", "NETWORK", "CONTRIBUTION", "RDS_CAUSAL", "ACTIVATION"]
    skeptical = {
        "RDS_DEF": ["A may overconstrain context-specific or latent indices and require broad migration.", "B may produce profile proliferation and ambiguous version selection.", "C is safest but keeps otherwise coherent RDS unavailable for execution."],
        "CROSS_LEVEL": ["A creates a new governed object and a nontrivial migration surface.", "B avoids a new class but may create long, incomplete bridge paths.", "C is backward-compatible but metadata alone may be too weak for runtime validation."],
        "NETWORK": ["A may stretch ScenarioStateDelta beyond its present bounded role.", "B is explicit but introduces a new architecture class and binding rules.", "C preserves safety while leaving legitimate network operations unavailable."],
        "CONTRIBUTION": ["A may incorrectly equate scientifically distinct contributions.", "B depends on every consumer enforcing mutual exclusion consistently.", "C avoids overgeneralization but leaves fragmented controls and blocked cross-class cases."],
        "RDS_CAUSAL": ["A may exclude legitimate contextual aggregate effects.", "B can preserve contextual causality but needs exposure mapping and strict double-count control.", "C is simple and safe but prevents every aggregate from acting as a causal source."],
        "ACTIVATION": ["A ties effect usability to mechanism knowledge and leaves bounded evidence inactive.", "B risks consumers treating a restricted class as simulation-ready.", "C is scientifically explicit but requires broad schema and consumer migration.", "D minimizes record change but can create divergent consumer behavior."],
    }
    packets = []
    rds_decision = rds_direction_decision()
    for index, key in enumerate(keys, 1):
        definition, root = next(row for row in ROOT_DEFS if row["key"] == key), by_id[ROOT_IDS[key]]
        packets.append({
            "decisionPacketId": f"DP-PSG-{index:03d}", "rootIssueId": root["id"], "workPackageId": WP_IDS[key],
            "title": definition["title"], "currentProblem": definition["problem"],
            "whyItMatters": f"It directly contains {root['activeBlockingOriginalItems']} active-execution blockers and constrains {root['downstreamOriginalItemCount']} items in downstream root programs.",
            "currentSafeState": root["currentSafeState"], "affectedLayers": definition["layers"],
            "affectedBacklogItems": root["absorbedBacklogItemIds"], "options": definition["options"],
            "scientificImplications": "The chosen option must preserve construct identity, causal identification, level alignment and unknown-as-unknown semantics.",
            "architectureImplications": "Any selected representation requires a separately governed schema/validator design and migration plan.",
            "simulationImplications": "No option may imply numeric weight, propagation, recommendation or execution eligibility by itself.",
            "migrationImplications": "Existing governed records remain valid; later implementation must be additive or explicitly migrated with rollback and protected-science comparison.",
            "whatEachOptionUnblocks": [{"option": option.split(":", 1)[0], "unblocks": "Later design, migration and scientific re-adjudication for the packet's dependent records."} for option in definition["options"]],
            "risks": ["scientific overstatement", "double counting", "consumer misinterpretation", "irreversible migration without rollback"],
            "skepticalArchitectureReview": skeptical[key],
            "recommendedNextResearchOrTest": "Build a non-production schema/validator prototype and migration dry run; do not alter production records." if key == "RDS_DEF" and rds_decision else "Create executable examples and counterexamples against current validators before the human option vote; do not alter production records.",
            "humanDecisionStatus": "HUMAN_APPROVED_BOUNDED_DIRECTION" if key == "RDS_DEF" and rds_decision else "REQUIRED_NOT_TAKEN",
            "humanDecisionId": rds_decision["decisionId"] if key == "RDS_DEF" and rds_decision else None,
            "approvedOption": "BOUNDED_OPTION_B_PLUS_C" if key == "RDS_DEF" and rds_decision else None,
            "authorizationBoundary": rds_decision["notAuthorized"] if key == "RDS_DEF" and rds_decision else None,
        })
    return {"schemaVersion": "1.0.0", "roadmapId": ROADMAP_ID, "decisionPackets": packets}


def render_dependency(dep_map, roots):
    counts = dep_map["normalizationCounts"]
    lines = ["# Post-Scale-Up dependency analysis", "", "**READ-ONLY GOVERNANCE PLANNING — NO SCIENCE, ONTOLOGY, ARCHITECTURE OR LIFECYCLE CHANGE**", "",
             f"The historical backlog retains all {dep_map['sourceBacklogItemCount']} rows and all {dep_map['sourceActiveBlockingCount']} active-execution flags. Dependency normalization yields {dep_map['trueRootIssueCount']} reusable root issues.", "",
             "| Normalized type | Original rows |", "|---|---:|"]
    lines.extend(f"| {key} | {value} |" for key, value in counts.items())
    lines += ["", "Four rows are downstream manifestations rather than independent decisions: Social H12/H20 derive from the Network State boundary, and the ENV/Tech inactive bundle rows derive from their activation-contract blockers. Biological and Informational identity-only records are inactive but safe because no eligible governed effect exists.", "", "## Root dependencies", "",
              "```mermaid", "graph TD", "  RDSDEF[RDS definition] --> CONTRIB[Contribution identity]", "  NETWORK[Network State boundary] --> CONTRIB", "  CROSS[Cross-level exposure] --> RDSCAUSE[RDS causal-source test]", "  RDSDEF --> RDSCAUSE", "  CONTRIB --> RDSCAUSE", "  CROSS --> REL[Relationship semantic debt]", "  NETWORK --> REL", "  CONTRIB --> REL", "  RDSCAUSE --> REL", "  ONTOLOGY[Construct/ontology] --> REL", "  RDSCAUSE --> RESEARCH[Targeted evidence]", "  ACT[Activation contract] --> RESEARCH", "  ONTOLOGY --> RESEARCH", "  SOURCE[Source governance] --> RESEARCH", "  REL --> RESEARCH", "```", "",
              "The structured dependency map is authoritative. Root dependencies are prerequisites for later decisions; they do not authorize implementation."]
    return "\n".join(lines)


def render_roadmap(dep_map, roots, packages):
    rds_decision = rds_direction_decision()
    status_text = "DP-PSG-001 Stage D records a bounded human-approved B+C direction; its non-production prototype is authorized, while production implementation and every other Stage D–G decision remain unstarted." if rds_decision else "Stages D–G remain prohibited until later human governance."
    lines = ["# Post-Scale-Up governance roadmap", "", f"This roadmap converts the 44-row historical backlog into decision-ready work packages. Stages A and B are complete here; skeptical architecture review is complete for the six highest-consequence packets. {status_text}", "",
             "| Order | Work package | Root issue | Band | Dependencies | Original rows |", "|---:|---|---|---|---|---:|"]
    for index, package in enumerate(packages["workPackages"], 1):
        lines.append(f"| {index} | `{package['workPackageId']}` {package['title']} | `{package['rootIssueId']}` | {package['recommendedSequenceBand']} | {', '.join(package['dependencies']) or 'None'} | {len(package['backlogItemsAbsorbed'])} |")
    lines += ["", "## Sequence finding", "", "The tentative sequence is retained with one clarification: construct/ontology and source-governance design can run in parallel with the foundation band, but Relationship migration and targeted evidence must wait for the applicable prerequisite decisions. Aggregate causal-source adjudication follows RDS definition, cross-level exposure and contribution-control decisions.", "",
              "## Highest leverage", "", f"`{WP_IDS['RDS_DEF']}` comes first. It spans six Layers, directly normalizes five definition blockers, and supplies the input/constituent contract required before five aggregate causal-source rows can be judged. A well-defined RDS is not thereby authorized as a cause.", "",
              "DP-PSG-001 selects only the bounded B+C architecture direction. No production validator, source, RDS, Relationship or lifecycle state changes, and no causal-source use is authorized."]
    return "\n".join(lines)


def render_packets(packets):
    lines = ["# Root decision packages", "", "DP-PSG-001 records the bounded human-approved B+C architecture direction. The remaining packets are ready for later human scientific/architecture governance and have no selected option.", ""]
    for packet in packets["decisionPackets"]:
        lines += [f"## {packet['decisionPacketId']} — {packet['title']}", "", f"- Root issue: `{packet['rootIssueId']}`", f"- Work package: `{packet['workPackageId']}`", f"- Human decision status: `{packet['humanDecisionStatus']}`", f"- Human decision ID: `{packet['humanDecisionId']}`" if packet['humanDecisionId'] else "- Human decision ID: none", f"- Approved option: `{packet['approvedOption']}`" if packet['approvedOption'] else "- Approved option: none", f"- Current problem: {packet['currentProblem']}", f"- Why it matters: {packet['whyItMatters']}", f"- Current safe state: {packet['currentSafeState']}", f"- Affected Layers: {', '.join(packet['affectedLayers'])}", "", "### Options", ""]
        lines.extend(f"- {option}" for option in packet["options"])
        lines += ["", "### Skeptical architecture review", ""]
        lines.extend(f"- {finding}" for finding in packet["skepticalArchitectureReview"])
        lines += ["", f"- Scientific implications: {packet['scientificImplications']}", f"- Architecture implications: {packet['architectureImplications']}", f"- Simulation implications: {packet['simulationImplications']}", f"- Migration implications: {packet['migrationImplications']}", f"- Recommended next test: {packet['recommendedNextResearchOrTest']}", ""]
    return "\n".join(lines)


def render_rds(roots):
    return f"""# Shared RDS governance program

**DESIGN ONLY — NO RDS IS ALTERED OR AUTHORIZED AS A CAUSAL SOURCE**

## Two separate gates

1. **Definition/derivation gate:** exact derivation, aggregation, input contract, reference population, boundary, time window, metric variant, normalization and constituent mapping.
2. **Causal-source gate:** only after gate 1, test deterministic derivation, independent variability, distinct aggregate mechanism, constituent overlap, temporal order, evidence at the aggregate level and contextual exposure mapping.

Passing gate 1 never implies passing gate 2.

## Shared program

`{WP_IDS['RDS_DEF']}` establishes versioned profiles reusable across Psychological, Informational, Biological, Cultural, Social and Institutional / Structural RDS. Network metrics additionally require node/tie set, direction, weight, missingness and boundary contracts. `{WP_IDS['RDS_CAUSAL']}` then applies one aggregate-source test to BIO-003, CUL-088, the 10 Social RDS source routes, INS-039/INS-103 and any Informational broader causal use.

The causal-source test asks whether the aggregate is more than a deterministic summary; whether constituents are already upstream; whether a distinct aggregate mechanism and temporal order exist; whether evidence estimates the aggregate; and whether the aggregate is a contextual exposure with an explicit cross-level route. Uncertainty remains `BLOCKED` or `RESEARCH_NEEDED`.
"""


def render_cross_network():
    return f"""# Cross-level and Network architecture options

**DESIGN ALTERNATIVES ONLY — NO ARCHITECTURE OR NETWORK STATE CHANGE**

## Cross-level exposure

`ASTRA-SOC-LAYER-002` and `ASTRA-INS-LAYER-003` share one root question: how a group, institution or network state becomes an exposure experienced by a person. The required chain distinguishes aggregate context, membership, eligibility, implementation, contact, actual exposure, perceived exposure and response.

- Option A: explicit typed `CrossLevelExposureMapping`.
- Option B: existing Driver/HappeningType bridge records for each transition.
- Option C: mandatory exposure-path metadata on cross-level Relationships.

## Network State

`DER-V1-SOC-F07-001` stays governed/inactive and recalculation-only. H12/H20 remain blocked. Network State owns node/tie/membership/boundary observations; Actions & Events own empirical operations; ScenarioStateDelta owns modeled state changes; derivations own deterministic metric recalculation; EffectAssertions require empirical causal evidence.

- Option A: typed ScenarioStateDelta operations within Network State V1.
- Option B: a separate governed NetworkStateTransition record.
- Option C: retain current architecture and leave unsupported operations blocked.

## Contribution identity

Relationship/EffectAssertion duplication, Driver/RDS constituent duplication, and recalculation/causal-edge duplication share a concern but are not assumed identical. `{WP_IDS['CONTRIBUTION']}` tests whether contribution groups can safely span these classes, whether consumer mutual exclusion is sufficient, or whether class-specific controls must remain separate.
"""


def render_activation():
    return f"""# Activation contract options

**NO ACTIVATION, VALIDATOR CHANGE OR MECHANISMSTATUS CHANGE**

The ENV and Technological governed bundles remain `GOVERNED / INACTIVE`, `MIXED_SUPPORTS_BOUNDED`, with `mechanismStatus = UNKNOWN`. Their inactive bundle rows are downstream manifestations of the two activation blockers, not two additional root decisions.

| Option | Scientific meaning | Architecture / validator | Simulation and consumer consequence | Migration |
|---|---|---|---|---|
| A — retain contract | Active effects require identified mechanism | No change | Bundles remain excluded | None |
| B — restricted empirical-effect class | Effect existence may be governed separately under stronger scope safeguards | New class and validator branch | Consumers must reject unsupported propagation | Additive records or migration |
| C — two eligibility dimensions | Effect existence and mechanism knowledge are independent governed fields | Schema and validator redesign | Consumers declare which eligibility they require | Broad backward-compatible migration required |
| D — capability-restricted active status | One active class with explicit unknown-mechanism restrictions | Consumer capability contract and validator changes | Prevent simulation/propagation while allowing bounded catalog use | Consumer and record migration |

No option is selected. Any later decision must address scope, double counting, quantitative execution, simulation eligibility, consumer expectations, rollback and backward compatibility.
"""


def main():
    validate_or_initialize_protection()
    source = read(SOURCE)
    completeness = read(COMPLETENESS)
    assert completeness["totals"] == {"layers": 8, "families": 105, "drivers": 770, "rds": 41, "entities": 811}
    assert len(source["items"]) == 44 and source["blockingActiveExecutionCount"] == 24
    debt = semantic_debt_analysis()
    dep_map = build_dependency_map(source["items"])
    roots = build_roots(dep_map, debt)
    packages = work_packages(roots)
    packets = decision_packets(roots)
    write_json(DATA / "blocker-dependency-map.json", dep_map)
    write_json(DATA / "root-issues.json", roots)
    write_json(DATA / "work-packages.json", packages)
    write_json(DATA / "decision-packets.json", packets)
    write_text(DOCS / "POST_SCALE_UP_DEPENDENCY_ANALYSIS.md", render_dependency(dep_map, roots))
    write_text(DOCS / "POST_SCALE_UP_GOVERNANCE_ROADMAP.md", render_roadmap(dep_map, roots, packages))
    write_text(DOCS / "ROOT_DECISION_PACKAGES.md", render_packets(packets))
    write_text(DOCS / "RDS_GOVERNANCE_PROGRAM.md", render_rds(roots))
    write_text(DOCS / "CROSS_LEVEL_AND_NETWORK_ARCHITECTURE_OPTIONS.md", render_cross_network())
    write_text(DOCS / "ACTIVATION_CONTRACT_OPTIONS.md", render_activation())
    print(json.dumps({"roadmapId": ROADMAP_ID, "originalItems": 44, "blocking": 24,
                      "rootIssues": len(roots["roots"]), "workPackages": len(packages["workPackages"]),
                      "decisionPackets": len(packets["decisionPackets"]),
                      "semanticDebtUniqueRelationships": debt["uniqueRelationships"]}, indent=2))


if __name__ == "__main__":
    main()
