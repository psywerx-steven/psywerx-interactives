"""Approved, deterministic public projection for canonical Cognitive Security data.

Every public object is constructed from an explicit allowlist.  This module never
copies a private record and then removes keys: private inputs remain read-only and
unknown fields fail closed at the recursive public-schema boundary.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "2.0"
CONTENT_VERSION = "canonical-resynthesis"
METHOD_VERSION = "deduplicated-canonical-resynthesis"
APPROVED_CHECKPOINT_COMMIT = "99e6732ac01a7b6f06b2eaf6490efb05093b97ea"
SUPPORT_INTERPRETATION = (
    "Corpus support reflects recurrence and breadth within this practitioner discourse "
    "corpus. It does not indicate scientific validity, consensus, importance, prevalence, "
    "or real-world effect size."
)
SUPPORT_LIMITATION = (
    "Broader traceable reach includes governed derived support and must not be interpreted "
    "as additional independent primary evidence."
)
_INTERNAL_PROSE = re.compile(
    r"(?i)\b(?:adjudicat\w*|legacy (?:id|identifier|record|artifact|output|schema|builder|data)|"
    r"(?:schema|data|legacy|implementation) migration|review queue|review flag\w*|"
    r"analyst[- ]review\w*|historical (?:lineage|mapping|candidate|finding|theme|"
    r"narrative|scenario|support|source|cluster|quotation)|source candidate\w*)\b"
)
_LEGACY_ID = re.compile(
    r"\b(?:TD-\d{3}|N\d{2}|S\d{2}|XTHEME[-_A-Z0-9]*|MC-\d+|[A-Z]{2,6}-M\d{2})\b"
)
SC04_NOTICE = (
    "Legal, privacy, civil-liberties, ethics, consent, and affected-community reviews are "
    "required before any operational use. Response options are analytical possibilities, "
    "not validated recommendations. This scenario is not a recommendation to deploy "
    "identity-linked monitoring."
)

EXPECTED_COUNTS = {
    "categoryCount": 7,
    "familyCount": 50,
    "clusterCount": 127,
    "clusterSummaryCount": 127,
    "themeCount": 11,
    "tensionCount": 20,
    "narrativeCount": 5,
    "categoryFindingCount": 64,
    "scenarioCount": 6,
    "publicReleaseCount": 242,
    "episodeSummaryCount": 242,
    "canonicalContentUnitCount": 241,
    "canonicalItemCount": 12933,
    "canonicalFocalItemCount": 9822,
    "canonicalContextualItemCount": 3111,
    "heatmapCellCount": 77,
}

PUBLIC_FILE_ORDER = (
    "manifest.json", "coverage.json", "categories.json", "clusters.json",
    "cluster_summaries.json", "families.json", "themes.json", "tensions.json",
    "narratives.json", "category_findings.json", "scenarios.json", "episodes.json",
    "episode_summaries.json", "relationships.json", "relationship_semantics.json",
    "provenance.json", "heatmap.json", "qa_report.json",
)

CHECKPOINT_FILES = {
    "selection": "canonical_corpus_selection.json",
    "families": "canonical_families_draft.json",
    "themes": "canonical_themes_draft.json",
    "tensions": "canonical_tensions_draft.json",
    "narratives": "canonical_narratives_draft.json",
    "findings": "canonical_category_findings_draft.json",
    "scenarios": "canonical_scenarios_draft.json",
    "cluster_support": "cluster_support_recomputed.json",
    "tension_allocation": "tension_evidence_allocation.json",
    "relationship_semantics": "relationship_semantics.json",
    "review_queue": "canonicalization_review_queue.json",
}
NORMALIZED_FILES = {
    "categories": "categories.json",
    "category_summaries": "category_summaries.json",
    "clusters": "clusters.json",
    "cluster_summaries": "cluster_summaries.json",
    "episodes": "episodes.json",
    "items": "items.json",
    "assignments": "item_cluster_assignments.json",
}


class PublicProjectionError(RuntimeError):
    """The private checkpoint cannot safely produce the approved public package."""


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicProjectionError(f"Cannot read required JSON {path}: {exc}") from exc


def _natural(value: str) -> tuple[Any, ...]:
    return tuple(int(part) if part.isdigit() else part.lower()
                 for part in re.split(r"(\d+)", value))


def _ordered_strings(values: Iterable[str]) -> list[str]:
    return sorted(set(values), key=_natural)


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise PublicProjectionError("Expected text or an array of text")


def _records(document: Any, name: str) -> list[dict[str, Any]]:
    value = document.get("records") if isinstance(document, dict) else document
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise PublicProjectionError(f"{name} must contain an array of records")
    return value


def _dump_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n").encode("utf-8")


def verify_approved_checkpoint_commit(repo_root: Path, checkpoint_dir: Path) -> None:
    """Fail unless the approved commit exists and is an ancestor of the worktree HEAD."""
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{APPROVED_CHECKPOINT_COMMIT}^{{commit}}"],
            cwd=repo_root, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", APPROVED_CHECKPOINT_COMMIT, "HEAD"],
            cwd=repo_root, check=True, capture_output=True, text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PublicProjectionError(
            f"Approved checkpoint {APPROVED_CHECKPOINT_COMMIT} is not available on HEAD"
        ) from exc
    expected = (repo_root / "analysis" / "cognitive-security" / "canonical-resynthesis").resolve()
    if checkpoint_dir.resolve() != expected:
        raise PublicProjectionError(f"Checkpoint must be the governed repo path: {expected}")


def load_projection_inputs(
    checkpoint_dir: Path,
    normalized_dir: Path,
    episode_summaries_path: Path,
) -> dict[str, Any]:
    """Read all projection inputs without altering them."""
    inputs: dict[str, Any] = {}
    for key, filename in CHECKPOINT_FILES.items():
        inputs[key] = _read_json(checkpoint_dir / filename)
    for key, filename in NORMALIZED_FILES.items():
        inputs[f"normalized_{key}"] = _read_json(normalized_dir / filename)
    inputs["episode_summaries"] = _read_json(episode_summaries_path)
    return inputs


def _assert_count(label: str, actual: int, expected: int) -> None:
    if actual != expected:
        raise PublicProjectionError(f"{label}: expected {expected}, found {actual}")


def _validate_checkpoint(inputs: Mapping[str, Any]) -> None:
    selection = inputs["selection"]
    counts = selection.get("counts", {})
    expected_private = {
        "publicReleaseCount": 242,
        "canonicalAnalyticalContentUnitCount": 241,
        "canonicalItemCount": 12933,
        "canonicalFocalItemCount": 9822,
        "canonicalContextualItemCount": 3111,
    }
    for key, expected in expected_private.items():
        if counts.get(key) != expected:
            raise PublicProjectionError(
                f"Checkpoint count {key}: expected {expected}, found {counts.get(key)!r}"
            )
    for key, expected in (("families", 50), ("themes", 11), ("tensions", 20),
                          ("narratives", 5), ("findings", 64), ("scenarios", 6),
                          ("cluster_support", 127)):
        _assert_count(key, len(_records(inputs[key], key)), expected)
    for key, expected in (("normalized_categories", 10), ("normalized_clusters", 127),
                          ("normalized_cluster_summaries", 127),
                          ("normalized_episodes", 242), ("normalized_items", 14397),
                          ("normalized_assignments", 10940), ("episode_summaries", 242)):
        _assert_count(key, len(_records(inputs[key], key)), expected)
    shared = selection.get("sharedContentRelationships", [])
    _assert_count("shared-content relationship", len(shared), 1)
    edge = shared[0]
    expected_edge = {
        "sourcePublicReleaseId": "EPI-9960393907F71603",
        "targetPublicReleaseId": "EPI-72E94D7AF43A4BD3",
        "semanticRole": "shared-content-inheritance",
        "contributesEvidence": False,
    }
    for key, value in expected_edge.items():
        if edge.get(key) != value:
            raise PublicProjectionError(f"Episode 83 inheritance {key} is not approved")
    audit = inputs["review_queue"].get("redundancyAudit", {})
    redundancy_expected = {
        "comparisonCount": 3511,
        "potentialRedundancyCount": 7,
        "resolvedDistinctCount": 7,
        "unresolvedPotentialRedundancyCount": 0,
    }
    for key, value in redundancy_expected.items():
        if audit.get(key) != value:
            raise PublicProjectionError(f"Redundancy audit {key} is not approved")


def _support(
    profile: Mapping[str, Any], metrics: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    direct = profile.get("directSupportItemCount")
    derived = profile.get("derivedSupportItemCount")
    total = profile.get("itemSupportCount")
    if not all(type(value) is int and value >= 0 for value in (direct, derived, total)):
        raise PublicProjectionError("Support profile counts must be non-negative integers")
    if direct + derived != total:
        raise PublicProjectionError("Support profile direct and derived counts do not sum")
    concentration = {
        "topOneContentUnitShare": profile.get("topOneContentUnitShare"),
        "topTwoContentUnitShare": profile.get("topTwoContentUnitShare"),
        "topFiveContentUnitShare": profile.get("topFiveContentUnitShare"),
        "effectiveContentUnitCount": profile.get("effectiveContentUnitCount"),
    }
    limits = [str(value) for value in profile.get("limitations") or []
              if not _INTERNAL_PROSE.search(str(value))
              and not _LEGACY_ID.search(str(value))]
    metrics = metrics or {}
    primary_concentration = metrics.get("concentration")
    if primary_concentration is None and derived == 0:
        primary_concentration = concentration
    primary_content_count = metrics.get("primaryContentUnitCount")
    if primary_content_count is None and derived == 0:
        primary_content_count = profile.get("uniqueContentUnitSupportCount")
    if primary_content_count is None and direct == 0:
        primary_content_count = 0
    primary_item_count = metrics.get("itemCount", direct)
    derived_or_broader_count = total - primary_item_count
    if primary_item_count < 0 or derived_or_broader_count < 0:
        raise PublicProjectionError("Primary support cannot exceed broader traceable reach")
    if derived_or_broader_count and SUPPORT_LIMITATION not in limits:
        limits.append(SUPPORT_LIMITATION)
    return {
        "primarySupport": {
            "itemCount": primary_item_count,
            "share": round(primary_item_count / total, 6) if total else 0.0,
            "primaryContentUnitCount": primary_content_count,
            "primaryClusterCount": metrics.get("primaryClusterCount", profile.get("clusterSupportCount")),
            "primaryFamilyCount": metrics.get("primaryFamilyCount", profile.get("familySupportCount")),
            "categoryBreadth": metrics.get("categoryBreadth", profile.get("categoryBreadth")),
            "concentration": primary_concentration,
        },
        "broaderTraceableReach": {
            "itemCount": total,
            "derivedItemCount": derived_or_broader_count,
            "contentUnitCount": profile.get("uniqueContentUnitSupportCount"),
            "publicReleaseCount": profile.get("publicReleaseCoverageCount"),
            "inheritedPublicReleaseCount": profile.get("inheritedPublicReleaseCoverageCount"),
            "clusterCount": profile.get("clusterSupportCount"),
            "familyCount": profile.get("familySupportCount"),
            "categoryBreadth": profile.get("categoryBreadth"),
            "secondaryOrDerivedClusterCount": max(
                0, profile.get("clusterSupportCount", 0)
                - metrics.get("primaryClusterCount", profile.get("clusterSupportCount", 0))
            ),
            "secondaryOrDerivedFamilyCount": max(
                0, profile.get("familySupportCount", 0)
                - metrics.get("primaryFamilyCount", profile.get("familySupportCount", 0))
            ),
            "concentration": concentration,
        },
        "interpretation": SUPPORT_INTERPRETATION,
        "limitations": limits,
    }


def _safe_limitations(values: Iterable[Any]) -> list[str]:
    return [str(value).replace("corrected corpus", "canonical corpus")
            .replace("corrected evidence", "canonical evidence")
            for value in values
            if not _INTERNAL_PROSE.search(str(value)) and not _LEGACY_ID.search(str(value))]


def _sanitize_public_values(value: Any) -> Any:
    """Return a fresh tree with internal process terminology normalized away."""
    if isinstance(value, dict):
        return {key: _sanitize_public_values(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_sanitize_public_values(child) for child in value]
    if not isinstance(value, str):
        return value
    replacements = (
        (r"\bAdjudicative\b", "Evidence-assessing"),
        (r"\badjudicative\b", "evidence-assessing"),
        (r"\bAdjudicating\b", "Evaluating"),
        (r"\badjudicating\b", "evaluating"),
        (r"\bAdjudication\b", "Evaluation"),
        (r"\badjudication\b", "evaluation"),
        (r"\bAdjudicate\b", "Evaluate"),
        (r"\badjudicate\b", "evaluate"),
        (r"\bcorrected corpus\b", "canonical corpus"),
        (r"\bcorrected evidence\b", "canonical evidence"),
        (r"\bcorrected support\b", "canonical support"),
        (r"\bcorrected count\b", "canonical count"),
    )
    result = value
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    return result


def _support_metrics_for_items(
    item_ids: set[str], item_by_id: Mapping[str, Mapping[str, Any]],
    primary_cluster_count: int, primary_family_count: int,
) -> dict[str, Any]:
    content_counts = Counter(str(item_by_id[item_id]["sourceIdentityId"])
                             for item_id in item_ids if item_id in item_by_id)
    total = sum(content_counts.values())
    shares = sorted((count / total for count in content_counts.values()), reverse=True) if total else []
    herfindahl = sum(share * share for share in shares)
    categories = {str(item_by_id[item_id]["categoryId"]) for item_id in item_ids
                  if item_id in item_by_id and item_by_id[item_id].get("scope") == "focal"}
    return {
        "itemCount": len(item_ids),
        "primaryContentUnitCount": len(content_counts),
        "primaryClusterCount": primary_cluster_count,
        "primaryFamilyCount": primary_family_count,
        "categoryBreadth": len(categories),
        "concentration": {
            "topOneContentUnitShare": round(shares[0], 6) if shares else 0.0,
            "topTwoContentUnitShare": round(sum(shares[:2]), 6) if shares else 0.0,
            "topFiveContentUnitShare": round(sum(shares[:5]), 6) if shares else 0.0,
            "effectiveContentUnitCount": round(1.0 / herfindahl, 6) if herfindahl else 0.0,
        },
    }


def _build_support_metrics(inputs: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Reconstruct governed primary evidence breadth without exposing private identities."""
    selected = {str(value) for value in inputs["selection"]["selectedItemIds"]}
    item_by_id = {str(row["itemId"]): row
                  for row in _records(inputs["normalized_items"], "items")}
    retained_by_cluster: dict[str, set[str]] = defaultdict(set)
    for row in _records(inputs["normalized_assignments"], "assignments"):
        item_id = str(row["itemId"])
        if item_id not in selected:
            continue
        for key in ("primaryClusterId", "secondaryClusterId"):
            cluster_id = str(row.get(key) or "")
            if cluster_id:
                retained_by_cluster[cluster_id].add(item_id)
    families = _records(inputs["families"], "families")
    family_clusters = {str(row["familyId"]): set(map(str, row["memberClusterIds"]))
                       for row in families}
    cluster_family = {cluster_id: family_id for family_id, cluster_ids in family_clusters.items()
                      for cluster_id in cluster_ids}
    tension_items: dict[str, set[str]] = defaultdict(set)
    for row in _records(inputs["tension_allocation"], "tension allocation"):
        if row.get("included") and float(row.get("analyticalSupportWeight") or 0) > 0:
            item_id = str(row["itemId"])
            if item_id in selected:
                tension_items[str(row["canonicalTensionId"])].add(item_id)

    metrics: dict[str, dict[str, Any]] = {}
    for cluster_id, item_ids in retained_by_cluster.items():
        metrics[cluster_id] = _support_metrics_for_items(item_ids, item_by_id, 1, 0)
    for family_id, cluster_ids in family_clusters.items():
        item_ids = set().union(*(retained_by_cluster[cid] for cid in cluster_ids))
        metrics[family_id] = _support_metrics_for_items(
            item_ids, item_by_id, len(cluster_ids), 1)
    for row in _records(inputs["tensions"], "tensions"):
        tension_id = str(row["tensionId"])
        metrics[tension_id] = _support_metrics_for_items(
            tension_items[tension_id], item_by_id,
            len(row["supportingClusterIds"]), len(row["supportingFamilyIds"]),
        )
    for row in _records(inputs["themes"], "themes"):
        theme_id = str(row["themeId"])
        primary_families = {str(rel["familyId"]) for rel in row["familyRelationships"]
                            if rel["semanticRole"] == "primary-theme-support"}
        primary_clusters = {str(cid) for cid in row["primaryClusterIds"]
                            if cluster_family.get(str(cid)) in primary_families}
        primary_items = set().union(*(retained_by_cluster[cid] for cid in primary_clusters))
        metrics[theme_id] = _support_metrics_for_items(
            primary_items, item_by_id, len(primary_clusters), len(primary_families))
    for row in _records(inputs["narratives"], "narratives"):
        primary_items = set().union(*(tension_items[str(tid)] for tid in row["integratesTensionIds"]))
        clusters = {str(cid) for tid in row["integratesTensionIds"]
                    for cid in next(t for t in _records(inputs["tensions"], "tensions")
                                    if t["tensionId"] == tid)["supportingClusterIds"]}
        primary_families = {cluster_family[cid] for cid in clusters if cid in cluster_family}
        metrics[str(row["narrativeId"])] = _support_metrics_for_items(
            primary_items, item_by_id, len(clusters), len(primary_families))
    for row in _records(inputs["findings"], "findings"):
        primary_items = (set() if row["findingType"] == "open-question" else
                         set().union(*(retained_by_cluster[str(cid)] for cid in row["supportingClusterIds"])))
        metrics[str(row["findingId"])] = _support_metrics_for_items(
            primary_items, item_by_id,
            0 if row["findingType"] == "open-question" else len(row["supportingClusterIds"]),
            0 if row["findingType"] == "open-question" else len(row["supportingFamilyIds"]),
        )
    for row in _records(inputs["scenarios"], "scenarios"):
        primary_items = set().union(*(tension_items[str(tid)] for tid in row["relevantTensionIds"]))
        clusters = {str(cid) for tid in row["relevantTensionIds"]
                    for cid in next(t for t in _records(inputs["tensions"], "tensions")
                                    if t["tensionId"] == tid)["supportingClusterIds"]}
        primary_families = {cluster_family[cid] for cid in clusters if cid in cluster_family}
        metrics[str(row["scenarioId"])] = _support_metrics_for_items(
            primary_items, item_by_id, len(clusters), len(primary_families))
    return metrics


def _entity_support(inputs: Mapping[str, Any], entity_id: str, profile: Mapping[str, Any]) -> dict[str, Any]:
    return _support(profile, inputs["_support_metrics"].get(entity_id))


def _project_categories(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    summaries = {row["categoryId"]: row for row in _records(
        inputs["normalized_category_summaries"], "normalized category summaries")}
    focal_ids = {row["focalCategoryMembership"]["categoryId"]
                 for row in _records(inputs["cluster_support"], "cluster support")}
    output = []
    for row in _records(inputs["normalized_categories"], "normalized categories"):
        if row["categoryId"] not in focal_ids:
            continue
        summary = summaries[row["categoryId"]]
        output.append({
            "categoryId": row["categoryId"], "name": row["name"], "scope": row["scope"],
            "summary": summary["summary"], "soWhat": summary["soWhat"],
        })
    return sorted(output, key=lambda row: _natural(row["categoryId"]))


def _project_clusters(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(({
        "clusterId": row["clusterId"], "categoryId": row["categoryId"],
        "name": row["name"], "definition": row["definition"],
        "inclusionCriteria": _text_list(row.get("inclusionCriteria")),
        "exclusionCriteria": _text_list(row.get("exclusionCriteria")),
        "nearNeighborDistinctions": _text_list(row.get("nearNeighborDistinctions")),
    } for row in _records(inputs["normalized_clusters"], "normalized clusters")),
        key=lambda row: _natural(row["clusterId"]))


def _project_cluster_summaries(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    source = {row["clusterId"]: row for row in _records(
        inputs["normalized_cluster_summaries"], "normalized cluster summaries")}
    output = []
    for support in _records(inputs["cluster_support"], "cluster support"):
        row = source[support["clusterId"]]
        recurring = []
        for theme in row.get("recurringThemes") or []:
            recurring.append({
                "name": theme.get("name"), "description": theme.get("description"),
            })
        output.append({
            "clusterId": support["clusterId"], "categoryId": row["categoryId"],
            "summary": row["summary"],
            "operationalImplications": row["operationalImplications"],
            "strategicSignificance": row["strategicSignificance"],
            "primarySecondaryDistinction": row["primarySecondaryDistinction"],
            "recurringThemes": recurring,
            "canonicalPrimaryItemCount": support["canonicalPrimaryItemCount"],
            "canonicalSecondaryItemCount": support["canonicalSecondaryItemCount"],
            "governedWeightedCount": support["governedWeightedCount"],
            "support": _entity_support(inputs, support["clusterId"], support["corpusSupportProfile"]),
        })
    return sorted(output, key=lambda row: _natural(row["clusterId"]))


def _family_category_ids(
    family: Mapping[str, Any], cluster_category: Mapping[str, str]
) -> list[str]:
    return _ordered_strings(cluster_category[cluster_id]
                            for cluster_id in family["memberClusterIds"])


def _project_families(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    cluster_category = {row["clusterId"]: row["categoryId"]
                        for row in _records(inputs["normalized_clusters"], "clusters")}
    output = []
    for row in _records(inputs["families"], "families"):
        category_ids = _family_category_ids(row, cluster_category)
        if len(category_ids) != 1:
            raise PublicProjectionError(
                f"Family {row['familyId']} must resolve to exactly one focal category"
            )
        output.append({
            "familyId": row["familyId"], "categoryId": category_ids[0],
            "name": row["name"], "definition": row["definition"],
            "inclusionRules": list(row.get("inclusionRules") or []),
            "exclusionRules": list(row.get("exclusionRules") or []),
            "distinguishingBoundaries": row["distinguishingBoundaries"],
            "memberClusterIds": _ordered_strings(row["memberClusterIds"]),
            "secondaryRelatedClusterIds": _ordered_strings(row.get("secondaryRelatedClusterIds") or []),
            "support": _entity_support(inputs, row["familyId"], row["corpusSupportProfile"]),
            "limitations": _safe_limitations(row.get("limitations") or []),
        })
    return sorted(output, key=lambda row: _natural(row["familyId"]))


def _project_themes(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    output = []
    for row in _records(inputs["themes"], "themes"):
        relationships = [{
            "familyId": rel["familyId"], "analyticalWeight": rel["analyticalWeight"],
            "semanticRole": rel["semanticRole"],
        } for rel in row.get("familyRelationships") or []]
        output.append({
            "themeId": row["themeId"], "name": row["name"],
            "definition": row["definition"], "boundaryConditions": row["boundaryConditions"],
            "strategicSignificance": row["strategicSignificance"],
            "operationalImplications": row["operationalImplications"],
            "primaryFamilyIds": _ordered_strings(row["primaryFamilyIds"]),
            "secondaryFamilyIds": _ordered_strings(row["secondaryFamilyIds"]),
            "primaryClusterIds": _ordered_strings(row["primaryClusterIds"]),
            "secondaryClusterIds": _ordered_strings(row["secondaryClusterIds"]),
            "familyRelationships": sorted(relationships,
                key=lambda rel: (_natural(rel["familyId"]), rel["semanticRole"])),
            "categoryBreadth": row["categoryBreadth"],
            "support": _entity_support(inputs, row["themeId"], row["corpusSupportProfile"]),
            "limitations": _safe_limitations(row.get("limitations") or []),
        })
    return sorted(output, key=lambda row: _natural(row["themeId"]))


def _project_tensions(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    output = []
    for row in _records(inputs["tensions"], "tensions"):
        balances = row["evidenceBalanceAcrossPoles"]
        pole_balance = {
            "poleAItemCount": balances["poleAItemCount"],
            "poleBItemCount": balances["poleBItemCount"],
            "sharedAcrossPolesItemCount": balances["sharedAcrossPolesItemCount"],
            "poleAAnalyticalWeight": balances["poleAAnalyticalWeight"],
            "poleBAnalyticalWeight": balances["poleBAnalyticalWeight"],
            "totalAnalyticalWeight": balances["totalAnalyticalWeight"],
            "poleAShare": balances["poleAShare"], "poleBShare": balances["poleBShare"],
            "bothPolesDirectlySupported": balances["bothPolesDirectlySupported"],
        }
        neighbors = [{"tensionId": tension_id, "distinction": distinction}
                     for tension_id, distinction in sorted(
                         (row.get("neighborDistinctions") or {}).items(),
                         key=lambda pair: _natural(pair[0]))]
        output.append({
            "tensionId": row["tensionId"], "name": row["name"],
            "tensionType": row["tensionType"], "definition": row["definition"],
            "poleALabel": row["poleALabel"], "poleAAssumption": row["poleAAssumption"],
            "poleBLabel": row["poleBLabel"], "poleBAssumption": row["poleBAssumption"],
            "conditionsFavoringA": list(row.get("conditionsFavoringA") or []),
            "conditionsFavoringB": list(row.get("conditionsFavoringB") or []),
            "falseDichotomyCaveat": row["falseDichotomyCaveat"],
            "evidenceAssessment": row["evidenceAssessment"], "poleBalance": pole_balance,
            "supportingFamilyIds": _ordered_strings(row["supportingFamilyIds"]),
            "supportingClusterIds": _ordered_strings(row["supportingClusterIds"]),
            "neighborDistinctions": neighbors,
            "support": _entity_support(inputs, row["tensionId"], row["corpusSupportProfile"]),
            "limitations": _safe_limitations(row.get("limitations") or []),
        })
    return sorted(output, key=lambda row: _natural(row["tensionId"]))


def _project_narratives(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(({
        "narrativeId": row["narrativeId"], "name": row["name"],
        "shortVersion": row["shortVersion"], "coreClaim": row["coreClaim"],
        "boundaryConditions": row["boundaryConditions"], "unresolvedIssue": row["unresolvedIssue"],
        "integratesThemeIds": _ordered_strings(row["integratesThemeIds"]),
        "integratesTensionIds": _ordered_strings(row["integratesTensionIds"]),
        "supportingFamilyIds": _ordered_strings(row["supportingFamilyIds"]),
        "supportingClusterIds": _ordered_strings(row["supportingClusterIds"]),
        "categoryBreadth": row["categoryBreadth"],
        "support": _entity_support(inputs, row["narrativeId"], row["corpusSupportProfile"]),
        "limitations": _safe_limitations(row.get("limitations") or []),
    } for row in _records(inputs["narratives"], "narratives")),
        key=lambda row: _natural(row["narrativeId"]))


def _project_findings(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(({
        "findingId": row["findingId"], "findingType": row["findingType"],
        "categoryId": row["categoryId"], "title": row["title"],
        "finding": row["finding"].replace("corrected corpus", "canonical corpus")
            .replace("corrected evidence", "canonical evidence"),
        "openQuestions": list(row.get("openQuestions") or []),
        "supportingFamilyIds": _ordered_strings(row["supportingFamilyIds"]),
        "supportingClusterIds": _ordered_strings(row["supportingClusterIds"]),
        "support": _entity_support(inputs, row["findingId"], row["corpusSupportProfile"]),
        "limitations": _safe_limitations(row.get("limitations") or []),
    } for row in _records(inputs["findings"], "findings")),
        key=lambda row: _natural(row["findingId"]))


def _project_scenarios(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    output = []
    for row in _records(inputs["scenarios"], "scenarios"):
        dynamics = [{
            "tensionId": item["tensionId"], "direction": item["direction"],
            "dynamic": item["dynamic"], "rationale": item["rationale"],
        } for item in row.get("tensionPoleDynamics") or []]
        related = [{
            "targetScenarioId": item["targetScenarioId"],
            "semanticRole": item["semanticRole"], "qualifier": item["qualifier"],
            "rationale": item["rationale"], "causalClaim": item["causalClaim"],
        } for item in row.get("relationshipsToOtherScenarios") or []]
        output.append({
            "scenarioId": row["scenarioId"], "scenarioType": row["scenarioType"],
            "title": row["title"], "description": row["description"],
            "uncertaintyStatement": row["uncertaintyStatement"],
            "triggerConditions": list(row.get("triggerConditions") or []),
            "plausiblePathways": list(row.get("plausiblePathways") or []),
            "indicators": list(row.get("indicators") or []),
            "counterSignposts": list(row.get("counterSignposts") or []),
            "branchPoints": list(row.get("branchPoints") or []),
            "strategicImplications": list(row.get("strategicImplications") or []),
            "mitigatingConditions": list(row.get("mitigatingConditions") or []),
            "responseOptions": list(row.get("responseOptions") or []),
            "researchQuestions": list(row.get("researchQuestions") or []),
            "relevantThemeIds": _ordered_strings(row["relevantThemeIds"]),
            "relevantTensionIds": _ordered_strings(row["relevantTensionIds"]),
            "relevantKeyConceptFamilyIds": _ordered_strings(row["relevantKeyConceptFamilyIds"]),
            "relevantFutureTrendFamilyIds": _ordered_strings(row["relevantFutureTrendFamilyIds"]),
            "tensionPoleDynamics": sorted(dynamics, key=lambda item: _natural(item["tensionId"])),
            "relationshipsToOtherScenarios": sorted(related,
                key=lambda item: (_natural(item["targetScenarioId"]), item["semanticRole"])),
            "support": _entity_support(inputs, row["scenarioId"], row["corpusSupportProfile"]),
            "limitations": _safe_limitations(row.get("limitations") or []),
            "publicNotice": SC04_NOTICE if row["scenarioId"] == "SC-04" else None,
        })
    return sorted(output, key=lambda row: _natural(row["scenarioId"]))


def _project_episodes(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    roles = {row["publicReleaseId"]: row["relationshipRole"]
             for row in inputs["selection"]["publicReleaseContentMap"]}
    output = [{
        "episodeId": row["episodeId"], "podcast": row["podcast"],
        "episodeTitle": row["episodeTitle"],
        "parsedEpisodeNumber": row.get("parsedEpisodeNumber"),
        "contentRole": roles[row["episodeId"]],
    } for row in _records(inputs["normalized_episodes"], "episodes")]
    return sorted(output, key=lambda row: _natural(row["episodeId"]))


def _project_episode_summaries(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(({
        "episodeId": row["episodeId"], "episodeNumber": row["episodeNumber"],
        "episodeTitle": row["episodeTitle"], "summary": row["summary"],
        "whyItMatters": row["whyItMatters"], "keyTopics": list(row.get("keyTopics") or []),
        "summaryMethod": re.sub(r"(?i)-v\d+(?:\.\d+)*$", "", row["summaryMethod"]),
        "summaryWordCount": row["summaryWordCount"],
        "transcriptWordCount": row["transcriptWordCount"],
    } for row in _records(inputs["episode_summaries"], "episode summaries")),
        key=lambda row: _natural(row["episodeId"]))


def _relationship_id(
    source_type: str, source_id: str, target_type: str, target_id: str,
    semantic_role: str, qualifier: str | None,
) -> str:
    raw = "|".join((source_type, source_id, target_type, target_id,
                    semantic_role, qualifier or ""))
    return "CSR-" + sha256(raw.encode("utf-8")).hexdigest()[:20].upper()


def _relationship(
    source_type: str, source_id: str, target_type: str, target_id: str,
    semantic_role: str, qualifier: str | None = None, causal_claim: bool = False,
) -> dict[str, Any]:
    return {
        "relationshipId": _relationship_id(source_type, source_id, target_type,
                                             target_id, semantic_role, qualifier),
        "sourceType": source_type, "sourceId": source_id,
        "targetType": target_type, "targetId": target_id,
        "semanticRole": semantic_role, "qualifier": qualifier,
        "causalClaim": causal_claim,
    }


def _project_relationships(
    clusters: list[dict[str, Any]], families: list[dict[str, Any]],
    themes: list[dict[str, Any]], tensions: list[dict[str, Any]],
    narratives: list[dict[str, Any]], findings: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cluster_family: dict[str, str] = {}
    for family in families:
        rows.append(_relationship("family", family["familyId"], "category",
                                  family["categoryId"], "contextual-connection",
                                  "within-category"))
        for cluster_id in family["memberClusterIds"]:
            cluster_family[cluster_id] = family["familyId"]
            rows.append(_relationship("cluster", cluster_id, "family", family["familyId"],
                                      "primary-family-membership", "governed-primary"))
        for cluster_id in family["secondaryRelatedClusterIds"]:
            rows.append(_relationship("cluster", cluster_id, "family", family["familyId"],
                                      "secondary-family-relationship", "governed-secondary"))
    for theme in themes:
        family_roles = {rel["familyId"]: rel["semanticRole"]
                        for rel in theme["familyRelationships"]}
        for rel in theme["familyRelationships"]:
            rows.append(_relationship("theme", theme["themeId"], "family", rel["familyId"],
                                      rel["semanticRole"], rel["analyticalWeight"]))
        for cluster_id in theme["primaryClusterIds"]:
            role = family_roles[cluster_family[cluster_id]]
            rows.append(_relationship("theme", theme["themeId"], "cluster", cluster_id,
                                      role, "governed-primary"))
        for cluster_id in theme["secondaryClusterIds"]:
            role = family_roles[cluster_family[cluster_id]]
            rows.append(_relationship("theme", theme["themeId"], "cluster", cluster_id,
                                      role, "governed-secondary"))
    theme_clusters = {row["themeId"]: set(row["primaryClusterIds"] + row["secondaryClusterIds"])
                      for row in themes}
    for tension in tensions:
        for family_id in tension["supportingFamilyIds"]:
            rows.append(_relationship("tension", tension["tensionId"], "family", family_id,
                                      "contextual-connection", "governed-traceable-support"))
        tension_clusters = set(tension["supportingClusterIds"])
        for cluster_id in tension_clusters:
            rows.append(_relationship("tension", tension["tensionId"], "cluster", cluster_id,
                                      "contextual-connection", "governed-traceable-support"))
        # This link is transparently derived from two governed cluster sets.  It is
        # useful for filtering but is neither an independently adjudicated nor causal link.
        for theme_id, supported_clusters in theme_clusters.items():
            if tension_clusters & supported_clusters:
                rows.append(_relationship(
                    "tension", tension["tensionId"], "theme", theme_id,
                    "contextual-connection", "shared-governed-cluster-support", False,
                ))
    for narrative in narratives:
        for target_type, key in (("theme", "integratesThemeIds"),
                                 ("tension", "integratesTensionIds"),
                                 ("family", "supportingFamilyIds"),
                                 ("cluster", "supportingClusterIds")):
            for target_id in narrative[key]:
                rows.append(_relationship("narrative", narrative["narrativeId"],
                                          target_type, target_id, "integrates"))
    for finding in findings:
        for target_type, key in (("family", "supportingFamilyIds"),
                                 ("cluster", "supportingClusterIds")):
            for target_id in finding[key]:
                rows.append(_relationship("finding", finding["findingId"], target_type,
                                          target_id, "integrates", "finding-support"))
    for scenario in scenarios:
        for target_type, key, role in (
            ("theme", "relevantThemeIds", "integrates"),
            ("tension", "relevantTensionIds", "activated-tension"),
            ("family", "relevantKeyConceptFamilyIds", "conceptual-framing"),
            ("family", "relevantFutureTrendFamilyIds", "future-extension"),
        ):
            for target_id in scenario[key]:
                rows.append(_relationship("scenario", scenario["scenarioId"], target_type,
                                          target_id, role))
        for related in scenario["relationshipsToOtherScenarios"]:
            rows.append(_relationship(
                "scenario", scenario["scenarioId"], "scenario", related["targetScenarioId"],
                related["semanticRole"], related["qualifier"], related["causalClaim"],
            ))
    unique = {row["relationshipId"]: row for row in rows}
    if len(unique) != len(rows):
        raise PublicProjectionError("Canonical public relationships contain duplicate identities")
    return sorted(rows, key=lambda row: _natural(row["relationshipId"]))


def _project_relationship_semantics(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(({
        "semanticRole": row["semanticRole"], "meaning": row["meaning"],
        "causalClaim": row["causalClaim"],
    } for row in _records(inputs["relationship_semantics"], "relationship semantics")),
        key=lambda row: row["semanticRole"])


def _direct_release_by_content(selection: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in selection["publicReleaseContentMap"]:
        if row["contributesAnalyticalWeight"]:
            content_id = str(row["canonicalContentUnitId"])
            if content_id in result:
                raise PublicProjectionError(f"Multiple weighted releases represent {content_id}")
            result[content_id] = str(row["publicReleaseId"])
    return result


def _project_provenance(inputs: Mapping[str, Any]) -> dict[str, Any]:
    selected = {str(value) for value in inputs["selection"]["selectedItemIds"]}
    item_content = {str(row["itemId"]): str(row["sourceIdentityId"])
                    for row in _records(inputs["normalized_items"], "items")}
    release_by_content = _direct_release_by_content(inputs["selection"])
    cluster_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in _records(inputs["normalized_assignments"], "assignments"):
        item_id = str(row["itemId"])
        if item_id not in selected:
            continue
        content_id = item_content[item_id]
        primary = str(row.get("primaryClusterId") or "")
        secondary = str(row.get("secondaryClusterId") or "")
        if primary:
            cluster_counts[(primary, content_id)]["primary"] += 1
        if secondary:
            cluster_counts[(secondary, content_id)]["secondary"] += 1
    cluster_to_releases: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (cluster_id, content_id), counts in sorted(
        cluster_counts.items(), key=lambda pair: (_natural(pair[0][0]), _natural(pair[0][1]))
    ):
        if content_id not in release_by_content:
            raise PublicProjectionError(f"No direct public release for content unit {content_id}")
        cluster_to_releases[cluster_id].append({
            "episodeId": release_by_content[content_id],
            "primaryItemCount": counts["primary"], "secondaryItemCount": counts["secondary"],
            "governedWeightedCount": 2 * counts["primary"] + counts["secondary"],
        })
    tension_weights: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in _records(inputs["tension_allocation"], "tension allocation"):
        if not row.get("included") or float(row.get("analyticalSupportWeight") or 0) <= 0:
            continue
        content_id = str(row["canonicalContentUnitId"])
        pole = str(row["normalizedPole"])
        tension_weights[(str(row["canonicalTensionId"]), content_id)][pole] += float(
            row["analyticalSupportWeight"])
    tension_to_releases: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (tension_id, content_id), weights in sorted(
        tension_weights.items(), key=lambda pair: (_natural(pair[0][0]), _natural(pair[0][1]))
    ):
        relationships = []
        for pole, semantic_role in (
            ("A", "tension-evidence-pole-a"),
            ("B", "tension-evidence-pole-b"),
        ):
            analytical_weight = round(weights[pole], 6)
            if analytical_weight > 0:
                relationships.append({
                    "semanticRole": semantic_role,
                    "analyticalWeight": analytical_weight,
                    "causalClaim": False,
                })
        tension_to_releases[tension_id].append({
            "episodeId": release_by_content[content_id],
            "relationships": relationships,
        })
    shared = [{
        "relationshipId": _relationship_id(
            "episode", row["sourcePublicReleaseId"], "episode", row["targetPublicReleaseId"],
            row["semanticRole"], "non-weighted-inheritance"),
        "sourceEpisodeId": row["sourcePublicReleaseId"],
        "targetEpisodeId": row["targetPublicReleaseId"],
        "semanticRole": row["semanticRole"],
        "contributesAnalyticalWeight": False,
    } for row in inputs["selection"]["sharedContentRelationships"]]
    cluster_rows = sum(len(value) for value in cluster_to_releases.values())
    tension_rows = sum(len(value) for value in tension_to_releases.values())
    return {
        "schemaVersion": SCHEMA_VERSION,
        "interpretation": (
            "Lazy aggregate provenance links canonical constructs to the single weighted public "
            "release for each content unit. Shared-content releases inherit display context only."
        ),
        "counts": {
            "clusterReleaseLinkCount": cluster_rows,
            "tensionReleaseLinkCount": tension_rows,
            "sharedContentRelationshipCount": len(shared),
        },
        "clusterRelationship": {
            "semanticRole": "direct-coded-support",
            "causalClaim": False,
        },
        "clusterToReleases": {key: value for key, value in sorted(
            cluster_to_releases.items(), key=lambda pair: _natural(pair[0]))},
        "tensionToReleases": {key: value for key, value in sorted(
            tension_to_releases.items(), key=lambda pair: _natural(pair[0]))},
        "sharedContentRelationships": shared,
    }


def _project_heatmap(
    inputs: Mapping[str, Any], categories: list[dict[str, Any]],
    families: list[dict[str, Any]], themes: list[dict[str, Any]],
) -> dict[str, Any]:
    family_by_id = {row["familyId"]: row for row in families}
    category_family_ids = {category["categoryId"]: {
        family["familyId"] for family in families if category["categoryId"] == family["categoryId"]
    } for category in categories}
    selected = {str(value) for value in inputs["selection"]["selectedItemIds"]}
    item_content = {str(row["itemId"]): str(row["sourceIdentityId"])
                    for row in _records(inputs["normalized_items"], "items")}
    cluster_content: dict[str, set[str]] = defaultdict(set)
    for row in _records(inputs["normalized_assignments"], "assignments"):
        item_id = str(row["itemId"])
        if item_id not in selected:
            continue
        for key in ("primaryClusterId", "secondaryClusterId"):
            cluster_id = str(row.get(key) or "")
            if cluster_id:
                cluster_content[cluster_id].add(item_content[item_id])
    cells = []
    for theme in themes:
        primary_theme_families = {rel["familyId"] for rel in theme["familyRelationships"]
                                  if rel["semanticRole"] == "primary-theme-support"}
        for category in categories:
            category_id = category["categoryId"]
            category_cluster_ids = {cluster_id for family_id in category_family_ids[category_id]
                                    for cluster_id in family_by_id[family_id]["memberClusterIds"]}
            category_content_ids = {content_id for cluster_id in category_cluster_ids
                                    for content_id in cluster_content[cluster_id]}
            primary_family_ids = primary_theme_families & category_family_ids[category_id]
            primary_cluster_ids = {cluster_id for family_id in primary_family_ids
                                   for cluster_id in family_by_id[family_id]["memberClusterIds"]}
            primary_content_ids = {content_id for cluster_id in primary_cluster_ids
                                   for content_id in cluster_content[cluster_id]}
            denominator = len(category_family_ids[category_id])
            cluster_denominator = len(category_cluster_ids)
            content_denominator = len(category_content_ids)
            family_share = len(primary_family_ids) / denominator if denominator else 0.0
            cluster_share = len(primary_cluster_ids) / cluster_denominator if cluster_denominator else 0.0
            content_share = len(primary_content_ids) / content_denominator if content_denominator else 0.0
            cells.append({
                "categoryId": category_id, "themeId": theme["themeId"],
                "primaryFamilyCount": len(primary_family_ids),
                "categoryFamilyCount": denominator,
                "primaryClusterCount": len(primary_cluster_ids),
                "categoryClusterCount": cluster_denominator,
                "primaryContentUnitCount": len(primary_content_ids),
                "categoryContentUnitCount": content_denominator,
                "primaryFamilyShare": round(family_share, 6),
                "primaryClusterShare": round(cluster_share, 6),
                "primaryContentUnitShare": round(content_share, 6),
                "normalizedPrimarySupportBreadth": round(
                    (family_share + cluster_share + content_share) / 3, 6),
            })
    return {
        "schemaVersion": SCHEMA_VERSION,
        "interpretation": (
            "Each cell is the mean of governed primary family, cluster, and content-unit "
            "breadth within a category; it is breadth, not strength or importance."
        ),
        "normalization": (
            "mean(primaryFamilyCount/categoryFamilyCount, "
            "primaryClusterCount/categoryClusterCount, "
            "primaryContentUnitCount/categoryContentUnitCount)"
        ),
        "cells": cells,
    }


def _coverage(counts: Mapping[str, int]) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "contentVersion": CONTENT_VERSION,
        "counts": dict(counts),
        "supportModel": {
            "layers": ["primarySupport", "broaderTraceableReach"],
            "primaryMeaning": (
                "Governed evidence designated as primary for the entity. The evidence path "
                "depends on entity type; item, content-unit, cluster, family, category, and "
                "concentration measures describe its breadth."
            ),
            "broaderMeaning": (
                "Total traceable analytical reach, including governed secondary, "
                "conceptual, future-extension, or derived support."
            ),
            "interpretation": SUPPORT_INTERPRETATION,
            "compositeScoreProhibited": True,
        },
        "contentSelection": {
            "publicReleaseCount": 242,
            "weightedPublicReleaseCount": 241,
            "inheritedPublicReleaseCount": 1,
            "canonicalContentUnitCount": 241,
            "canonicalItemCount": 12933,
            "canonicalFocalItemCount": 9822,
            "canonicalContextualItemCount": 3111,
        },
    }


def _qa_report(
    counts: Mapping[str, int], provenance: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "pass",
        "checks": {
            "governedInputContract": True,
            "deterministicSerialization": True,
            "recursiveAllowlist": True,
            "privacyGuard": True,
            "canonicalCounts": True,
            "relationshipEndpointsResolve": True,
            "episode83SingleAnalyticalWeight": True,
            "episode83InheritanceEdge": True,
            "heatmapComplete": True,
            "compositeScoreAbsent": True,
        },
        "counts": dict(counts),
        "provenanceCounts": dict(provenance["counts"]),
        "redundancyResolution": {
            "comparisonCount": 3511,
            "flaggedPairCount": 7,
            "resolvedDistinctPairCount": 7,
            "unresolvedPairCount": 0,
        },
    }


def _build_payloads_once(inputs: Mapping[str, Any]) -> dict[str, Any]:
    _validate_checkpoint(inputs)
    work = dict(inputs)
    work["_support_metrics"] = _build_support_metrics(work)
    categories = _project_categories(work)
    clusters = _project_clusters(work)
    cluster_summaries = _project_cluster_summaries(work)
    families = _project_families(work)
    themes = _project_themes(work)
    tensions = _project_tensions(work)
    narratives = _project_narratives(work)
    findings = _project_findings(work)
    scenarios = _project_scenarios(work)
    episodes = _project_episodes(work)
    episode_summaries = _project_episode_summaries(work)
    provenance = _project_provenance(work)
    relationships = _project_relationships(
        clusters, families, themes, tensions, narratives, findings, scenarios)
    for edge in provenance["sharedContentRelationships"]:
        relationships.append(_relationship(
            "episode", edge["sourceEpisodeId"], "episode", edge["targetEpisodeId"],
            edge["semanticRole"], "non-weighted-inheritance", False,
        ))
    relationships.sort(key=lambda row: _natural(row["relationshipId"]))
    heatmap = _project_heatmap(work, categories, families, themes)
    counts = {
        **EXPECTED_COUNTS,
        "relationshipCount": len(relationships),
        "relationshipSemanticRoleCount": len(_records(
            work["relationship_semantics"], "relationship semantics")),
        **provenance["counts"],
    }
    payloads: dict[str, Any] = {
        "coverage.json": _coverage(counts),
        "categories.json": categories,
        "clusters.json": clusters,
        "cluster_summaries.json": cluster_summaries,
        "families.json": families,
        "themes.json": themes,
        "tensions.json": tensions,
        "narratives.json": narratives,
        "category_findings.json": findings,
        "scenarios.json": scenarios,
        "episodes.json": episodes,
        "episode_summaries.json": episode_summaries,
        "relationships.json": relationships,
        "relationship_semantics.json": _project_relationship_semantics(work),
        "provenance.json": provenance,
        "heatmap.json": heatmap,
        "qa_report.json": _qa_report(counts, provenance),
    }
    payloads = {name: _sanitize_public_values(value) for name, value in payloads.items()}
    non_manifest_bytes = {name: _dump_bytes(value) for name, value in payloads.items()}
    files = [{"name": name, "bytes": len(non_manifest_bytes[name])}
             for name in PUBLIC_FILE_ORDER if name != "manifest.json"]
    payloads["manifest.json"] = {
        "schemaVersion": SCHEMA_VERSION,
        "contentVersion": CONTENT_VERSION,
        "methodVersion": METHOD_VERSION,
        "counts": counts,
        "fileCount": len(PUBLIC_FILE_ORDER),
        "publicFiles": list(PUBLIC_FILE_ORDER),
        "lazyFiles": ["relationships.json", "provenance.json"],
        "files": files,
    }
    return {name: payloads[name] for name in PUBLIC_FILE_ORDER}


# Recursive schemas are the publication boundary.  A schema dictionary requires
# exactly its listed keys; a single-element list applies its schema to every item;
# ("map", schema) permits only string keys with the stated value schema.
TEXT = str
BOOL = bool
INT = int
NUMBER = (int, float)
NULL_TEXT = (str, type(None))
NULL_INT = (int, type(None))

CONCENTRATION_SCHEMA = {
    "topOneContentUnitShare": NUMBER,
    "topTwoContentUnitShare": NUMBER,
    "topFiveContentUnitShare": NUMBER,
    "effectiveContentUnitCount": NUMBER,
}
SUPPORT_SCHEMA = {
    "primarySupport": {
        "itemCount": INT, "share": NUMBER, "primaryContentUnitCount": INT,
        "primaryClusterCount": INT, "primaryFamilyCount": INT,
        "categoryBreadth": INT, "concentration": CONCENTRATION_SCHEMA,
    },
    "broaderTraceableReach": {
        "itemCount": INT, "derivedItemCount": INT, "contentUnitCount": INT,
        "publicReleaseCount": INT, "inheritedPublicReleaseCount": INT,
        "clusterCount": INT, "familyCount": INT, "categoryBreadth": INT,
        "secondaryOrDerivedClusterCount": INT,
        "secondaryOrDerivedFamilyCount": INT,
        "concentration": CONCENTRATION_SCHEMA,
    },
    "interpretation": TEXT, "limitations": [TEXT],
}
COUNTS_SCHEMA = {key: INT for key in (
    *EXPECTED_COUNTS.keys(), "relationshipCount", "relationshipSemanticRoleCount",
    "clusterReleaseLinkCount", "tensionReleaseLinkCount",
    "sharedContentRelationshipCount",
)}
PROVENANCE_COUNTS_SCHEMA = {
    "clusterReleaseLinkCount": INT, "tensionReleaseLinkCount": INT,
    "sharedContentRelationshipCount": INT,
}
RELATIONSHIP_SCHEMA = {
    "relationshipId": TEXT, "sourceType": TEXT, "sourceId": TEXT,
    "targetType": TEXT, "targetId": TEXT, "semanticRole": TEXT,
    "qualifier": NULL_TEXT, "causalClaim": BOOL,
}

PUBLIC_SCHEMAS: dict[str, Any] = {
    "manifest.json": {
        "schemaVersion": TEXT, "contentVersion": TEXT, "methodVersion": TEXT,
        "counts": COUNTS_SCHEMA, "fileCount": INT,
        "publicFiles": [TEXT], "lazyFiles": [TEXT],
        "files": [{"name": TEXT, "bytes": INT}],
    },
    "coverage.json": {
        "schemaVersion": TEXT, "contentVersion": TEXT, "counts": COUNTS_SCHEMA,
        "supportModel": {
            "layers": [TEXT], "primaryMeaning": TEXT, "broaderMeaning": TEXT,
            "interpretation": TEXT, "compositeScoreProhibited": BOOL,
        },
        "contentSelection": {
            "publicReleaseCount": INT, "weightedPublicReleaseCount": INT,
            "inheritedPublicReleaseCount": INT, "canonicalContentUnitCount": INT,
            "canonicalItemCount": INT, "canonicalFocalItemCount": INT,
            "canonicalContextualItemCount": INT,
        },
    },
    "categories.json": [{
        "categoryId": TEXT, "name": TEXT, "scope": TEXT,
        "summary": TEXT, "soWhat": TEXT,
    }],
    "clusters.json": [{
        "clusterId": TEXT, "categoryId": TEXT, "name": TEXT,
        "definition": TEXT, "inclusionCriteria": [TEXT], "exclusionCriteria": [TEXT],
        "nearNeighborDistinctions": [TEXT],
    }],
    "cluster_summaries.json": [{
        "clusterId": TEXT, "categoryId": TEXT, "summary": TEXT,
        "operationalImplications": TEXT, "strategicSignificance": TEXT,
        "primarySecondaryDistinction": TEXT,
        "recurringThemes": [{"name": TEXT, "description": TEXT}],
        "canonicalPrimaryItemCount": INT, "canonicalSecondaryItemCount": INT,
        "governedWeightedCount": INT, "support": SUPPORT_SCHEMA,
    }],
    "families.json": [{
        "familyId": TEXT, "categoryId": TEXT, "name": TEXT, "definition": TEXT,
        "inclusionRules": [TEXT], "exclusionRules": [TEXT],
        "distinguishingBoundaries": TEXT, "memberClusterIds": [TEXT],
        "secondaryRelatedClusterIds": [TEXT], "support": SUPPORT_SCHEMA,
        "limitations": [TEXT],
    }],
    "themes.json": [{
        "themeId": TEXT, "name": TEXT, "definition": TEXT,
        "boundaryConditions": TEXT, "strategicSignificance": TEXT,
        "operationalImplications": TEXT, "primaryFamilyIds": [TEXT],
        "secondaryFamilyIds": [TEXT], "primaryClusterIds": [TEXT],
        "secondaryClusterIds": [TEXT],
        "familyRelationships": [{
            "familyId": TEXT, "analyticalWeight": TEXT, "semanticRole": TEXT,
        }],
        "categoryBreadth": INT, "support": SUPPORT_SCHEMA, "limitations": [TEXT],
    }],
    "tensions.json": [{
        "tensionId": TEXT, "name": TEXT, "tensionType": TEXT, "definition": TEXT,
        "poleALabel": TEXT, "poleAAssumption": TEXT, "poleBLabel": TEXT,
        "poleBAssumption": TEXT, "conditionsFavoringA": [TEXT],
        "conditionsFavoringB": [TEXT], "falseDichotomyCaveat": TEXT,
        "evidenceAssessment": TEXT,
        "poleBalance": {
            "poleAItemCount": INT, "poleBItemCount": INT,
            "sharedAcrossPolesItemCount": INT, "poleAAnalyticalWeight": NUMBER,
            "poleBAnalyticalWeight": NUMBER, "totalAnalyticalWeight": NUMBER,
            "poleAShare": NUMBER, "poleBShare": NUMBER,
            "bothPolesDirectlySupported": BOOL,
        },
        "supportingFamilyIds": [TEXT], "supportingClusterIds": [TEXT],
        "neighborDistinctions": [{"tensionId": TEXT, "distinction": TEXT}],
        "support": SUPPORT_SCHEMA, "limitations": [TEXT],
    }],
    "narratives.json": [{
        "narrativeId": TEXT, "name": TEXT, "shortVersion": TEXT,
        "coreClaim": TEXT, "boundaryConditions": TEXT, "unresolvedIssue": TEXT,
        "integratesThemeIds": [TEXT], "integratesTensionIds": [TEXT],
        "supportingFamilyIds": [TEXT], "supportingClusterIds": [TEXT],
        "categoryBreadth": INT, "support": SUPPORT_SCHEMA, "limitations": [TEXT],
    }],
    "category_findings.json": [{
        "findingId": TEXT, "findingType": TEXT, "categoryId": TEXT,
        "title": TEXT, "finding": TEXT, "openQuestions": [TEXT],
        "supportingFamilyIds": [TEXT], "supportingClusterIds": [TEXT],
        "support": SUPPORT_SCHEMA, "limitations": [TEXT],
    }],
    "scenarios.json": [{
        "scenarioId": TEXT, "scenarioType": TEXT, "title": TEXT,
        "description": TEXT, "uncertaintyStatement": TEXT,
        "triggerConditions": [TEXT], "plausiblePathways": [TEXT],
        "indicators": [TEXT], "counterSignposts": [TEXT], "branchPoints": [TEXT],
        "strategicImplications": [TEXT], "mitigatingConditions": [TEXT],
        "responseOptions": [TEXT], "researchQuestions": [TEXT],
        "relevantThemeIds": [TEXT], "relevantTensionIds": [TEXT],
        "relevantKeyConceptFamilyIds": [TEXT], "relevantFutureTrendFamilyIds": [TEXT],
        "tensionPoleDynamics": [{
            "tensionId": TEXT, "direction": TEXT, "dynamic": TEXT, "rationale": TEXT,
        }],
        "relationshipsToOtherScenarios": [{
            "targetScenarioId": TEXT, "semanticRole": TEXT, "qualifier": TEXT,
            "rationale": TEXT, "causalClaim": BOOL,
        }],
        "support": SUPPORT_SCHEMA, "limitations": [TEXT], "publicNotice": NULL_TEXT,
    }],
    "episodes.json": [{
        "episodeId": TEXT, "podcast": TEXT, "episodeTitle": TEXT,
        "parsedEpisodeNumber": NULL_INT, "contentRole": TEXT,
    }],
    "episode_summaries.json": [{
        "episodeId": TEXT, "episodeNumber": NULL_INT, "episodeTitle": TEXT,
        "summary": TEXT, "whyItMatters": TEXT, "keyTopics": [TEXT],
        "summaryMethod": TEXT, "summaryWordCount": INT, "transcriptWordCount": INT,
    }],
    "relationships.json": [RELATIONSHIP_SCHEMA],
    "relationship_semantics.json": [{
        "semanticRole": TEXT, "meaning": TEXT, "causalClaim": BOOL,
    }],
    "provenance.json": {
        "schemaVersion": TEXT, "interpretation": TEXT,
        "counts": PROVENANCE_COUNTS_SCHEMA,
        "clusterRelationship": {"semanticRole": TEXT, "causalClaim": BOOL},
        "clusterToReleases": ("map", [{
            "episodeId": TEXT, "primaryItemCount": INT, "secondaryItemCount": INT,
            "governedWeightedCount": INT,
        }]),
        "tensionToReleases": ("map", [{
            "episodeId": TEXT,
            "relationships": [{
                "semanticRole": TEXT, "analyticalWeight": NUMBER,
                "causalClaim": BOOL,
            }],
        }]),
        "sharedContentRelationships": [{
            "relationshipId": TEXT, "sourceEpisodeId": TEXT, "targetEpisodeId": TEXT,
            "semanticRole": TEXT, "contributesAnalyticalWeight": BOOL,
        }],
    },
    "heatmap.json": {
        "schemaVersion": TEXT, "interpretation": TEXT, "normalization": TEXT,
        "cells": [{
            "categoryId": TEXT, "themeId": TEXT, "primaryFamilyCount": INT,
            "categoryFamilyCount": INT, "primaryClusterCount": INT,
            "categoryClusterCount": INT, "primaryContentUnitCount": INT,
            "categoryContentUnitCount": INT, "primaryFamilyShare": NUMBER,
            "primaryClusterShare": NUMBER, "primaryContentUnitShare": NUMBER,
            "normalizedPrimarySupportBreadth": NUMBER,
        }],
    },
    "qa_report.json": {
        "schemaVersion": TEXT, "status": TEXT,
        "checks": {
            "governedInputContract": BOOL, "deterministicSerialization": BOOL,
            "recursiveAllowlist": BOOL, "privacyGuard": BOOL,
            "canonicalCounts": BOOL, "relationshipEndpointsResolve": BOOL,
            "episode83SingleAnalyticalWeight": BOOL, "episode83InheritanceEdge": BOOL,
            "heatmapComplete": BOOL, "compositeScoreAbsent": BOOL,
        },
        "counts": COUNTS_SCHEMA, "provenanceCounts": PROVENANCE_COUNTS_SCHEMA,
        "redundancyResolution": {
            "comparisonCount": INT, "flaggedPairCount": INT,
            "resolvedDistinctPairCount": INT, "unresolvedPairCount": INT,
        },
    },
}


def _validate_shape(value: Any, schema: Any, location: str) -> None:
    if isinstance(schema, tuple) and len(schema) == 2 and schema[0] == "map":
        if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
            raise PublicProjectionError(f"{location} must be a string-keyed object")
        for key, child in value.items():
            _validate_shape(child, schema[1], f"{location}.{key}")
        return
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            raise PublicProjectionError(f"{location} must be an object")
        actual, expected = set(value), set(schema)
        if actual != expected:
            raise PublicProjectionError(
                f"{location} keys differ from allowlist; missing={sorted(expected-actual)}, "
                f"unknown={sorted(actual-expected)}"
            )
        for key, child_schema in schema.items():
            _validate_shape(value[key], child_schema, f"{location}.{key}")
        return
    if isinstance(schema, list):
        if len(schema) != 1 or not isinstance(value, list):
            raise PublicProjectionError(f"{location} must be an array")
        for index, child in enumerate(value):
            _validate_shape(child, schema[0], f"{location}[{index}]")
        return
    permitted = schema if isinstance(schema, tuple) else (schema,)
    if not any(type(value) is allowed for allowed in permitted):
        names = ", ".join(allowed.__name__ for allowed in permitted)
        raise PublicProjectionError(f"{location} must have exact type {names}")


_BANNED_KEYS = {
    "historicalid", "historicalids", "historicalitemid", "historicalitemids",
    "historicalscenarioid", "historicaltensionids", "historicalnarrativeids",
    "adjudicationstatus", "adjudicationconfidence", "adjudicationdecision",
    "adjudicationrationale", "reviewflags", "reviewrequired", "reviewquestions",
    "sourceidentityid", "sourceidentityids", "sourcecandidateids", "sourcefile",
    "sourcepath", "inputpath", "outputpath", "itemid", "itemids",
    "representativeitemids", "canonicalcontentunitid", "canonicalcontentunitids",
    "supportingcanonicalcontentunits", "evidenceexcerpt", "importance",
}
_PRIVATE_PATH = re.compile(r"(?i)(?:[a-z]:\\(?:users|documents)\\|/users/|\.xlsx(?:\b|$))")


def _privacy_guard(value: Any, location: str = "$", key: str | None = None) -> None:
    if isinstance(value, dict):
        for child_key, child in value.items():
            normalized = re.sub(r"[^a-z0-9]", "", child_key.lower())
            if normalized in _BANNED_KEYS:
                raise PublicProjectionError(f"Private field {child_key!r} escaped at {location}")
            if "score" in normalized and normalized not in {
                "compositescoreprohibited", "compositescoreabsent"
            }:
                raise PublicProjectionError(f"Score-like field {child_key!r} escaped at {location}")
            _privacy_guard(child, f"{location}.{child_key}", child_key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _privacy_guard(child, f"{location}[{index}]", key)
    elif isinstance(value, str):
        if _PRIVATE_PATH.search(value):
            raise PublicProjectionError(f"Private filesystem reference escaped at {location}")
        if _INTERNAL_PROSE.search(value) or _LEGACY_ID.search(value) \
                or re.search(r"(?i)\bcorrected (?:corpus|evidence|support|count)\b", value):
            raise PublicProjectionError(f"Implementation-history prose escaped at {location}")
        if re.search(r"(?i)(?:^|[-_])v\d+(?:\.\d+)*(?:$|[-_])", value):
            raise PublicProjectionError(f"Implementation-version label escaped at {location}")


def _assert_unique(records: list[dict[str, Any]], key: str, label: str) -> set[str]:
    values = [str(row[key]) for row in records]
    if len(values) != len(set(values)):
        raise PublicProjectionError(f"Duplicate {label} identifiers")
    return set(values)


def _validate_supports(payloads: Mapping[str, Any]) -> None:
    support_files = (
        "cluster_summaries.json", "families.json", "themes.json", "tensions.json",
        "narratives.json", "category_findings.json", "scenarios.json",
    )
    for filename in support_files:
        for index, row in enumerate(payloads[filename]):
            support = row["support"]
            if support["interpretation"] != SUPPORT_INTERPRETATION:
                raise PublicProjectionError(f"{filename}[{index}] support interpretation changed")
            primary = support["primarySupport"]
            broader = support["broaderTraceableReach"]
            if primary["itemCount"] + broader["derivedItemCount"] != broader["itemCount"]:
                raise PublicProjectionError(f"{filename}[{index}] support layers do not reconcile")
            if primary["primaryContentUnitCount"] > broader["contentUnitCount"]:
                raise PublicProjectionError(f"{filename}[{index}] primary breadth exceeds total")
            for layer in (primary["concentration"], broader["concentration"]):
                if not (0 <= layer["topOneContentUnitShare"]
                        <= layer["topTwoContentUnitShare"]
                        <= layer["topFiveContentUnitShare"] <= 1):
                    raise PublicProjectionError(f"{filename}[{index}] concentration is invalid")


def _validate_invariants(payloads: Mapping[str, Any]) -> None:
    categories = payloads["categories.json"]
    clusters = payloads["clusters.json"]
    summaries = payloads["cluster_summaries.json"]
    families = payloads["families.json"]
    themes = payloads["themes.json"]
    tensions = payloads["tensions.json"]
    narratives = payloads["narratives.json"]
    findings = payloads["category_findings.json"]
    scenarios = payloads["scenarios.json"]
    episodes = payloads["episodes.json"]
    episode_summaries = payloads["episode_summaries.json"]
    relationships = payloads["relationships.json"]
    semantics = payloads["relationship_semantics.json"]
    heatmap = payloads["heatmap.json"]
    provenance = payloads["provenance.json"]
    for records, expected, label in (
        (categories, 7, "categories"), (clusters, 127, "clusters"),
        (summaries, 127, "cluster summaries"), (families, 50, "families"),
        (themes, 11, "themes"), (tensions, 20, "tensions"),
        (narratives, 5, "narratives"), (findings, 64, "findings"),
        (scenarios, 6, "scenarios"), (episodes, 242, "episodes"),
        (episode_summaries, 242, "episode summaries"), (heatmap["cells"], 77, "heatmap cells"),
    ):
        _assert_count(label, len(records), expected)
    ids = {
        "category": _assert_unique(categories, "categoryId", "category"),
        "cluster": _assert_unique(clusters, "clusterId", "cluster"),
        "family": _assert_unique(families, "familyId", "family"),
        "theme": _assert_unique(themes, "themeId", "theme"),
        "tension": _assert_unique(tensions, "tensionId", "tension"),
        "narrative": _assert_unique(narratives, "narrativeId", "narrative"),
        "finding": _assert_unique(findings, "findingId", "finding"),
        "scenario": _assert_unique(scenarios, "scenarioId", "scenario"),
        "episode": _assert_unique(episodes, "episodeId", "episode"),
    }
    if _assert_unique(summaries, "clusterId", "cluster summary") != ids["cluster"]:
        raise PublicProjectionError("Cluster summary coverage differs from cluster definitions")
    if _assert_unique(episode_summaries, "episodeId", "episode summary") != ids["episode"]:
        raise PublicProjectionError("Episode summary coverage differs from episode catalog")
    member_clusters = [cluster_id for family in families for cluster_id in family["memberClusterIds"]]
    if len(member_clusters) != 127 or set(member_clusters) != ids["cluster"]:
        raise PublicProjectionError("Families must partition all 127 clusters exactly once")
    if any(family["categoryId"] not in ids["category"] for family in families):
        raise PublicProjectionError("Family category endpoints do not resolve")
    role_ids = _assert_unique(semantics, "semanticRole", "semantic role")
    _assert_unique(relationships, "relationshipId", "relationship")
    for row in relationships:
        if row["sourceType"] not in ids or row["sourceId"] not in ids[row["sourceType"]]:
            raise PublicProjectionError(f"Relationship source does not resolve: {row['relationshipId']}")
        if row["targetType"] not in ids or row["targetId"] not in ids[row["targetType"]]:
            raise PublicProjectionError(f"Relationship target does not resolve: {row['relationshipId']}")
        if row["semanticRole"] not in role_ids:
            raise PublicProjectionError(f"Relationship role is not governed: {row['semanticRole']}")
        if row["causalClaim"]:
            raise PublicProjectionError("Canonical public relationships cannot assert causality")
    cluster_relationship = provenance["clusterRelationship"]
    if cluster_relationship["semanticRole"] != "direct-coded-support" \
            or cluster_relationship["causalClaim"]:
        raise PublicProjectionError(
            "Direct-coded-support is reserved for noncausal cluster provenance")
    cluster_provenance_count = 0
    for cluster_id, links in provenance["clusterToReleases"].items():
        if cluster_id not in ids["cluster"]:
            raise PublicProjectionError(f"Cluster provenance endpoint does not resolve: {cluster_id}")
        seen_episode_ids: set[str] = set()
        for link in links:
            episode_id = link["episodeId"]
            if episode_id not in ids["episode"] or episode_id in seen_episode_ids:
                raise PublicProjectionError(
                    f"Cluster provenance release is missing or duplicated: {cluster_id}/{episode_id}")
            seen_episode_ids.add(episode_id)
            cluster_provenance_count += 1
    tension_provenance_count = 0
    tension_weight_totals: dict[str, Counter[str]] = defaultdict(Counter)
    pole_roles = {
        "tension-evidence-pole-a": "A",
        "tension-evidence-pole-b": "B",
    }
    for tension_id, links in provenance["tensionToReleases"].items():
        if tension_id not in ids["tension"]:
            raise PublicProjectionError(f"Tension provenance endpoint does not resolve: {tension_id}")
        seen_episode_ids = set()
        for link in links:
            episode_id = link["episodeId"]
            if episode_id not in ids["episode"] or episode_id in seen_episode_ids:
                raise PublicProjectionError(
                    f"Tension provenance release is missing or duplicated: {tension_id}/{episode_id}")
            seen_episode_ids.add(episode_id)
            relationship_roles = [row["semanticRole"] for row in link["relationships"]]
            if not relationship_roles or len(relationship_roles) != len(set(relationship_roles)):
                raise PublicProjectionError(
                    f"Tension provenance roles are empty or duplicated: {tension_id}/{episode_id}")
            if any(role not in pole_roles or role not in role_ids for role in relationship_roles):
                raise PublicProjectionError(
                    f"Tension provenance uses a nongoverned pole role: {tension_id}/{episode_id}")
            for relationship in link["relationships"]:
                if relationship["causalClaim"] or relationship["analyticalWeight"] <= 0:
                    raise PublicProjectionError(
                        f"Tension provenance must be noncausal with positive weight: {tension_id}/{episode_id}")
                tension_weight_totals[tension_id][pole_roles[relationship["semanticRole"]]] += float(
                    relationship["analyticalWeight"])
            tension_provenance_count += 1
    if cluster_provenance_count != provenance["counts"]["clusterReleaseLinkCount"]:
        raise PublicProjectionError("Cluster provenance link count changed")
    if tension_provenance_count != provenance["counts"]["tensionReleaseLinkCount"]:
        raise PublicProjectionError("Tension provenance link count changed")
    for tension in tensions:
        tension_id = tension["tensionId"]
        expected_balance = tension["poleBalance"]
        for pole, key in (("A", "poleAAnalyticalWeight"), ("B", "poleBAnalyticalWeight")):
            if not math.isclose(
                tension_weight_totals[tension_id][pole], expected_balance[key], abs_tol=1e-9
            ):
                raise PublicProjectionError(
                    f"Tension provenance {pole} weight does not reconcile: {tension_id}")
    if Counter(row["findingType"] for row in findings) != Counter({
        "family-finding": 50, "integrative-category-finding": 7, "open-question": 7,
    }):
        raise PublicProjectionError("Canonical finding type counts changed")
    notices = {row["scenarioId"]: row["publicNotice"] for row in scenarios}
    if notices.get("SC-04") != SC04_NOTICE or any(
        value is not None for key, value in notices.items() if key != "SC-04"):
        raise PublicProjectionError("SC-04 must carry the only approved public notice")
    for required in ("legal", "privacy", "civil-liberties", "ethics", "consent",
                     "affected-community", "not validated recommendations"):
        if required not in SC04_NOTICE.lower():
            raise PublicProjectionError(f"SC-04 public notice lost required safeguard: {required}")
    original = "EPI-72E94D7AF43A4BD3"
    inherited = "EPI-9960393907F71603"
    episode_by_id = {row["episodeId"]: row for row in episodes}
    if episode_by_id[original]["contentRole"] != "direct-content-representation":
        raise PublicProjectionError("Episode 83 original must carry analytical weight")
    if episode_by_id[inherited]["contentRole"] != "shared-content-inheritance":
        raise PublicProjectionError("Episode 83 re-release must inherit without analytical weight")
    shared = provenance["sharedContentRelationships"]
    if len(shared) != 1 or shared[0]["sourceEpisodeId"] != inherited \
            or shared[0]["targetEpisodeId"] != original \
            or shared[0]["semanticRole"] != "shared-content-inheritance" \
            or shared[0]["contributesAnalyticalWeight"]:
        raise PublicProjectionError("Episode 83 inheritance edge changed")
    analytical_provenance_ids = {row["episodeId"] for values in provenance["clusterToReleases"].values()
                                 for row in values} | {
        row["episodeId"] for values in provenance["tensionToReleases"].values() for row in values}
    if inherited in analytical_provenance_ids:
        raise PublicProjectionError("Episode 83 inherited release has analytical provenance")
    expected_pairs = {(category_id, theme_id) for category_id in ids["category"]
                      for theme_id in ids["theme"]}
    actual_pairs = {(row["categoryId"], row["themeId"]) for row in heatmap["cells"]}
    if actual_pairs != expected_pairs or len(actual_pairs) != 77:
        raise PublicProjectionError("Heatmap is not the complete 7 by 11 matrix")
    for cell in heatmap["cells"]:
        shares = (
            cell["primaryFamilyCount"] / cell["categoryFamilyCount"],
            cell["primaryClusterCount"] / cell["categoryClusterCount"],
            cell["primaryContentUnitCount"] / cell["categoryContentUnitCount"],
        )
        if not all(math.isclose(cell[key], round(value, 6), abs_tol=1e-9)
                   for key, value in zip(("primaryFamilyShare", "primaryClusterShare",
                                          "primaryContentUnitShare"), shares)):
            raise PublicProjectionError("Heatmap component share changed")
        expected = round(sum(shares) / 3, 6)
        if not math.isclose(cell["normalizedPrimarySupportBreadth"], expected, abs_tol=1e-9):
            raise PublicProjectionError("Heatmap normalization changed")
    _validate_supports(payloads)


def validate_public_payloads(payloads: Mapping[str, Any]) -> None:
    if set(payloads) != set(PUBLIC_FILE_ORDER):
        raise PublicProjectionError("Public package filenames differ from the allowlist")
    if set(PUBLIC_SCHEMAS) != set(PUBLIC_FILE_ORDER):
        raise PublicProjectionError("Internal recursive schema coverage is incomplete")
    for filename in PUBLIC_FILE_ORDER:
        _validate_shape(payloads[filename], PUBLIC_SCHEMAS[filename], filename)
        _privacy_guard(payloads[filename], filename)
    manifest = payloads["manifest.json"]
    if manifest["schemaVersion"] != SCHEMA_VERSION or manifest["contentVersion"] != CONTENT_VERSION:
        raise PublicProjectionError("Manifest version identifiers changed")
    if manifest["fileCount"] != len(PUBLIC_FILE_ORDER):
        raise PublicProjectionError("Manifest file count is incorrect")
    if manifest["publicFiles"] != list(PUBLIC_FILE_ORDER):
        raise PublicProjectionError("Manifest publicFiles order is not canonical")
    if manifest["lazyFiles"] != ["relationships.json", "provenance.json"]:
        raise PublicProjectionError("Manifest lazyFiles contract changed")
    if [row["name"] for row in manifest["files"]] != [
        name for name in PUBLIC_FILE_ORDER if name != "manifest.json"]:
        raise PublicProjectionError("Manifest file inventory is not canonical")
    _validate_invariants(payloads)


def build_and_serialize(inputs: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Build twice and require byte-identical output before returning anything."""
    first = _build_payloads_once(inputs)
    validate_public_payloads(first)
    first_bytes = {name: _dump_bytes(first[name]) for name in PUBLIC_FILE_ORDER}
    second = _build_payloads_once(inputs)
    validate_public_payloads(second)
    second_bytes = {name: _dump_bytes(second[name]) for name in PUBLIC_FILE_ORDER}
    if first_bytes != second_bytes:
        raise PublicProjectionError("Canonical public projection is not deterministic")
    return first, first_bytes


def write_package_atomic(
    output_dir: Path, payloads: Mapping[str, Any], serialized: Mapping[str, bytes]
) -> None:
    """Publish into a stable directory, committing the package manifest last.

    OneDrive-backed Windows worktrees do not preserve inherited ACLs reliably when
    whole reparse-point directories are renamed.  Each file replacement is atomic,
    the previous package is retained in memory for rollback, and manifest.json is
    the final commit marker; the public directory itself is never moved or absent.
    """
    validate_public_payloads(payloads)
    expected_bytes = {name: _dump_bytes(payloads[name]) for name in PUBLIC_FILE_ORDER}
    if dict(serialized) != expected_bytes:
        raise PublicProjectionError("Serialized package does not match validated payloads")
    output_dir = output_dir.resolve()
    if output_dir.name != "cognitive-security" or output_dir.parent.name != "data":
        raise PublicProjectionError("Refusing to publish outside data/cognitive-security")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".canonical-stage-", dir=output_dir))

    def remove_tree(path: Path) -> None:
        def clear_read_only(function: Any, target: str, _error: Any) -> None:
            os.chmod(target, stat.S_IWRITE)
            function(target)
        shutil.rmtree(path, onerror=clear_read_only)

    def replace_file(source: Path, destination: Path) -> None:
        if os.name != "nt" or not destination.exists():
            os.replace(source, destination)
            return
        # ReplaceFileW retains the destination DACL and other attributes, unlike
        # MoveFileEx/os.replace. This is essential in managed/OneDrive worktrees.
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        replace = kernel32.ReplaceFileW
        replace.argtypes = (
            wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
            wintypes.DWORD, wintypes.LPVOID, wintypes.LPVOID,
        )
        replace.restype = wintypes.BOOL
        if not replace(str(destination), str(source), None, 0, None, None):
            error = ctypes.get_last_error()
            raise OSError(error, f"ReplaceFileW failed for {destination}")

    def replace_bytes(path: Path, content: bytes) -> None:
        descriptor, temporary_name = tempfile.mkstemp(prefix=".canonical-restore-", dir=output_dir)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            replace_file(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

    existing_files = {
        path.name: path.read_bytes() for path in output_dir.iterdir() if path.is_file()
    }
    original_names = set(existing_files)

    try:
        for filename in PUBLIC_FILE_ORDER:
            path = staging / filename
            with path.open("wb") as handle:
                handle.write(serialized[filename])
                handle.flush()
                os.fsync(handle.fileno())
        readback = {name: (staging / name).read_bytes() for name in PUBLIC_FILE_ORDER}
        if readback != dict(serialized):
            raise PublicProjectionError("Staged public package failed byte verification")
        staged_payloads = {name: _read_json(staging / name) for name in PUBLIC_FILE_ORDER}
        validate_public_payloads(staged_payloads)
        for filename in PUBLIC_FILE_ORDER:
            if filename != "manifest.json":
                replace_file(staging / filename, output_dir / filename)
        for legacy_name in sorted(original_names - set(PUBLIC_FILE_ORDER)):
            legacy_path = output_dir / legacy_name
            os.chmod(legacy_path, stat.S_IWRITE)
            legacy_path.unlink()
        replace_file(staging / "manifest.json", output_dir / "manifest.json")
        published = {name: (output_dir / name).read_bytes() for name in PUBLIC_FILE_ORDER}
        if published != dict(serialized):
            raise PublicProjectionError("Published public package failed byte verification")
    except Exception:
        for name, content in existing_files.items():
            replace_bytes(output_dir / name, content)
        for name in set(PUBLIC_FILE_ORDER) - original_names:
            path = output_dir / name
            if path.exists():
                os.chmod(path, stat.S_IWRITE)
                path.unlink()
        raise
    finally:
        if staging.exists():
            remove_tree(staging)
