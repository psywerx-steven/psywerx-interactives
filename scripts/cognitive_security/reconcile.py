"""Deterministic source-identity reconciliation for the podcast corpus.

The v1.0 normalized ``episodes`` collection is a source-file identity table:
its IDs are derived from ``source_file``.  This module preserves those IDs and
builds a separate underlying-episode model without mutating the historical
normalized dataset.

Only the governed legacy/modern numbering pattern is auto-collapsed.  Fuzzy
title similarity and re-release wording are never sufficient evidence.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import re
import unicodedata
from typing import Any, Iterable, Mapping, Sequence

from .utils import deterministic_id, natural_key, normalize_text, normalized_key


RECONCILIATION_SCHEMA_VERSION = "1.1"
RECONCILIATION_METHOD_VERSION = "1.0"

# Transcript forensics are not build inputs, so confirmed decisions that rely
# on that external review are frozen here by stable source identity.  The
# decision is reproducible from the XLSX-derived EPI IDs without pretending
# that title similarity alone established the relationship.
GOVERNED_EDITED_RELEASE_ALIASES = (
    {
        "aliasGroupId": "EAG-186",
        "episodeNumber": 186,
        "canonicalSourceIdentityId": "EPI-72ED08B56161C224",
        "aliasSourceIdentityId": "EPI-A91997718EEC2E8A",
        "mappingBasis": (
            "governed-transcript-forensic-decision",
            "source-transcript-explicitly-identifies-edited-podcast-release",
            "transcript-sequence-similarity-approximately-0.97",
            "five-word-shingle-overlap-approximately-0.633",
            "modern-numbered-source-preferred",
        ),
    },
)

GOVERNED_DISTINCT_PUBLICATION_REUSES = (
    {
        "originalSourceIdentityId": "EPI-72E94D7AF43A4BD3",
        "reuseSourceIdentityId": "EPI-9960393907F71603",
        "governedTreatment": "distinct-publication-unit",
    },
)

MAPPING_STATUSES = frozenset(
    {
        "unique",
        "confirmed-alias",
        "likely-alias",
        "ambiguous",
        "unresolved",
        "excluded-non-episode",
    }
)

_LEGACY_EPISODE = re.compile(
    r"^\s*the\s+cognitive\s+crucible\s+episode\s+#?\s*0*(\d+)\b[\s:：.\-–—]*",
    flags=re.IGNORECASE,
)
_MODERN_EPISODE = re.compile(
    r"^\s*#\s*0*(\d+)\b[\s:：.\-–—]*",
    flags=re.IGNORECASE,
)
_LEADING_EPISODE = re.compile(
    r"^\s*0*(\d{1,3})\b[\s:：.\-–—]+",
    flags=re.IGNORECASE,
)
_TEXT_EXTENSION = re.compile(r"\.txt\s*$", flags=re.IGNORECASE)
_TITLE_STOPWORDS = frozenset({"a", "an", "and", "for", "in", "of", "on", "the", "to", "with"})


def _text_without_extension(value: Any) -> str:
    return _TEXT_EXTENSION.sub("", normalize_text(value) or "").strip()


def _number_match(value: Any) -> tuple[int | None, str | None]:
    """Return a governed leading episode number and its source convention."""

    text = _text_without_extension(value)
    if not text:
        return None, None
    for expression, kind in (
        (_LEGACY_EPISODE, "legacy-numbered"),
        (_MODERN_EPISODE, "modern-numbered"),
        (_LEADING_EPISODE, "leading-numbered"),
    ):
        match = expression.match(text)
        if match:
            return int(match.group(1)), kind
    return None, None


def parse_episode_number(value: Any) -> int | None:
    """Parse only governed leading episode-number conventions."""

    return _number_match(value)[0]


def _strip_episode_prefix(value: Any) -> str:
    text = _text_without_extension(value)
    for expression in (_LEGACY_EPISODE, _MODERN_EPISODE, _LEADING_EPISODE):
        match = expression.match(text)
        if match:
            return text[match.end() :].strip()
    return text


def normalize_episode_title(value: Any) -> str:
    """Build a conservative comparison title, retaining internal punctuation."""

    text = unicodedata.normalize("NFKC", _strip_episode_prefix(value)).casefold()
    return re.sub(r"\s+", " ", text).strip()


def normalize_source_filename(value: Any) -> str:
    """Normalize a source filename for comparison without exposing a path."""

    text = _text_without_extension(value).replace("\\", "/").rsplit("/", 1)[-1]
    return normalize_episode_title(text)


def _title_tokens(value: Any) -> set[str]:
    return {
        token
        for token in normalized_key(_strip_episode_prefix(value)).split()
        if token and token not in _TITLE_STOPWORDS
    }


def _token_corroboration(left: Any, right: Any) -> dict[str, Any]:
    left_tokens = _title_tokens(left)
    right_tokens = _title_tokens(right)
    overlap = left_tokens & right_tokens
    denominator = min(len(left_tokens), len(right_tokens))
    overlap_coefficient = len(overlap) / denominator if denominator else 0.0
    corroborated = bool(overlap) and overlap_coefficient >= 0.5
    return {
        "corroborated": corroborated,
        "overlapCoefficient": round(overlap_coefficient, 6),
        "sharedTokens": sorted(overlap),
        "leftTokenCount": len(left_tokens),
        "rightTokenCount": len(right_tokens),
    }


def _episode_number_evidence(record: Mapping[str, Any]) -> tuple[int | None, str, bool]:
    title_number, title_kind = _number_match(record.get("episodeTitle"))
    file_number, file_kind = _number_match(record.get("sourceFile"))
    conflict = (
        title_number is not None
        and file_number is not None
        and title_number != file_number
    )
    number = file_number if file_number is not None else title_number
    kind = file_kind or title_kind or "unnumbered"
    return number, kind, conflict


def _source_identity_record(
    episode: Mapping[str, Any],
    observed_counts: Mapping[str, Mapping[str, int]],
) -> dict[str, Any]:
    source_identity_id = str(episode.get("episodeId") or "").strip()
    number, kind, number_conflict = _episode_number_evidence(episode)
    title = normalize_text(episode.get("episodeTitle"))
    source_file = normalize_text(episode.get("sourceFile"))
    counts = observed_counts.get(source_identity_id, {})
    if number == 0 and "trailer" in _title_tokens(title or source_file):
        kind = "trailer"
    normalized_title = normalize_episode_title(title or source_file)
    normalized_title_key = normalized_key(normalized_title)
    if normalized_title_key.startswith("re release") or normalized_title_key.startswith("rerelease"):
        kind = "re-release"
    return {
        "sourceIdentityId": source_identity_id,
        "podcast": normalize_text(episode.get("podcast")),
        "sourceEpisodeTitle": title,
        "sourceFile": source_file,
        "parsedEpisodeNumber": number,
        "identityKind": kind,
        "numberEvidenceConflict": number_conflict,
        "normalizedTitle": normalized_title,
        "normalizedSourceFilename": normalize_source_filename(source_file),
        "originalItemCount": int(counts.get("itemCount", episode.get("itemCount") or 0)),
        "focalItemCount": int(counts.get("focalItemCount", episode.get("focalItemCount") or 0)),
        "contextualItemCount": int(
            counts.get("contextualItemCount", episode.get("contextualItemCount") or 0)
        ),
        "source": deepcopy(episode.get("source")),
    }


def _observed_item_counts(items: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"itemCount": 0, "focalItemCount": 0, "contextualItemCount": 0}
    )
    for item in items:
        source_id = str(item.get("sourceIdentityId") or item.get("episodeId") or "").strip()
        if not source_id:
            continue
        counts[source_id]["itemCount"] += 1
        scope = str(item.get("scope") or "").strip().casefold()
        if scope == "focal":
            counts[source_id]["focalItemCount"] += 1
        elif scope == "contextual":
            counts[source_id]["contextualItemCount"] += 1
    return dict(counts)


def build_source_identity_records(dataset: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convert historical v1.0 episode/source records without changing IDs."""

    counts = _observed_item_counts(list(dataset.get("items", ())))
    records = [
        _source_identity_record(episode, counts)
        for episode in dataset.get("episodes", ())
    ]
    return sorted(records, key=lambda row: natural_key(row["sourceIdentityId"]))


def _flag(
    flag_type: str,
    source_ids: Iterable[str],
    *,
    status: str,
    reason: str,
    episode_number: int | None = None,
    evidence: Mapping[str, Any] | None = None,
    sources: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    ordered_ids = sorted(set(source_ids), key=natural_key)
    return {
        "episodeReconciliationFlagId": deterministic_id(
            "ERF", flag_type, *ordered_ids, reason
        ),
        "flagType": flag_type,
        "sourceIdentityIds": ordered_ids,
        "candidateEpisodeNumber": episode_number,
        "status": status,
        "reason": reason,
        "evidence": dict(evidence or {}),
        "sources": sorted(
            (deepcopy(source) for source in sources if isinstance(source, Mapping)),
            key=lambda source: (
                natural_key(source.get("artifactId")),
                natural_key(source.get("sheet")),
                int(source.get("rowNumber") or 0),
            ),
        ),
    }


def _mapping(
    identity: Mapping[str, Any],
    *,
    canonical_episode_id: str | None,
    candidate_episode_id: str | None,
    status: str,
    role: str,
    basis: Sequence[str],
    confidence: str,
    alias_group_id: str | None = None,
    decision_source: str = "automatic-rule-v1",
) -> dict[str, Any]:
    if status not in MAPPING_STATUSES:
        raise ValueError(f"Unsupported reconciliation status: {status!r}")
    source_identity_id = str(identity["sourceIdentityId"])
    return {
        "episodeSourceMappingId": deterministic_id("ESM", source_identity_id),
        "sourceIdentityId": source_identity_id,
        "candidateCanonicalEpisodeId": candidate_episode_id,
        "canonicalEpisodeId": canonical_episode_id,
        "aliasGroupId": alias_group_id,
        "mappingStatus": status,
        "mappingRole": role,
        "mappingBasis": list(basis),
        "confidence": confidence,
        "collapseEligible": status == "confirmed-alias" and role == "alias",
        "decisionSource": decision_source,
        "source": deepcopy(identity.get("source")),
    }


def _canonical_episode(
    canonical_identity: Mapping[str, Any],
    members: Sequence[Mapping[str, Any]],
    *,
    status: str,
) -> dict[str, Any]:
    canonical_source_id = str(canonical_identity["sourceIdentityId"])
    source_ids = [canonical_source_id] + sorted(
        {
            str(member["sourceIdentityId"])
            for member in members
            if str(member["sourceIdentityId"]) != canonical_source_id
        },
        key=natural_key,
    )
    return {
        "episodeId": canonical_source_id,
        "podcast": canonical_identity.get("podcast"),
        "episodeTitle": canonical_identity.get("sourceEpisodeTitle"),
        "parsedEpisodeNumber": canonical_identity.get("parsedEpisodeNumber"),
        "canonicalSourceIdentityId": canonical_source_id,
        "sourceIdentityIds": source_ids,
        "sourceIdentityCount": len(source_ids),
        "originalItemCount": sum(int(member.get("originalItemCount") or 0) for member in members),
        "reconciledSensitivityItemCount": int(canonical_identity.get("originalItemCount") or 0),
        "originalFocalItemCount": sum(int(member.get("focalItemCount") or 0) for member in members),
        "reconciledSensitivityFocalItemCount": int(canonical_identity.get("focalItemCount") or 0),
        "originalContextualItemCount": sum(
            int(member.get("contextualItemCount") or 0) for member in members
        ),
        "reconciledSensitivityContextualItemCount": int(
            canonical_identity.get("contextualItemCount") or 0
        ),
        "reconciliationStatus": status,
        "source": deepcopy(canonical_identity.get("source")),
    }


def build_episode_reconciliation(dataset: Mapping[str, Any]) -> dict[str, Any]:
    """Build the governed 269-source-identity reconciliation in memory."""

    identities = build_source_identity_records(dataset)
    identity_by_id = {record["sourceIdentityId"]: record for record in identities}
    if len(identity_by_id) != len(identities):
        raise ValueError("Source identity IDs must be unique before reconciliation.")

    modern_by_number: dict[int, list[dict[str, Any]]] = defaultdict(list)
    legacy_by_number: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for identity in identities:
        # Conflicting title/file episode numbers are authoritative review
        # conditions. Never allow such an identity to enter an automatic pair;
        # otherwise its peer could remain collapse-eligible after the conflict
        # is discovered below.
        if identity.get("numberEvidenceConflict"):
            continue
        number = identity.get("parsedEpisodeNumber")
        if identity["identityKind"] == "modern-numbered" and isinstance(number, int):
            modern_by_number[number].append(identity)
        elif identity["identityKind"] == "legacy-numbered" and isinstance(number, int):
            legacy_by_number[number].append(identity)

    mappings_by_source: dict[str, dict[str, Any]] = {}
    flags: list[dict[str, Any]] = []
    alias_groups: list[dict[str, Any]] = []
    canonical_members: dict[str, list[dict[str, Any]]] = {}

    # Begin with a conservative one-to-one model.  Governed rules below may
    # replace it only with a confirmed mapping.
    for identity in identities:
        source_id = str(identity["sourceIdentityId"])
        if identity["identityKind"] == "trailer":
            mappings_by_source[source_id] = _mapping(
                identity,
                canonical_episode_id=source_id,
                candidate_episode_id=source_id,
                status="unique",
                role="canonical",
                basis=("distinct-public-feed-release", "episode-zero-trailer"),
                confidence="high",
            )
            canonical_members[source_id] = [identity]
            flags.append(
                _flag(
                    "episode-zero-trailer-retained",
                    (source_id,),
                    status="resolved",
                    reason=(
                        "Episode #000 is an introductory trailer but remains a distinct "
                        "public feed release under the governed corpus unit."
                    ),
                    episode_number=0,
                    sources=(identity.get("source") or {},),
                )
            )
            continue
        mappings_by_source[source_id] = _mapping(
            identity,
            canonical_episode_id=source_id,
            candidate_episode_id=source_id,
            status="unique",
            role="canonical",
            basis=("distinct-source-identity",),
            confidence="high",
        )
        canonical_members[source_id] = [identity]
        if identity["identityKind"] == "re-release":
            mappings_by_source[source_id] = _mapping(
                identity,
                canonical_episode_id=source_id,
                candidate_episode_id=source_id,
                status="unique",
                role="canonical",
                basis=(
                    "confirmed-content-reuse",
                    "distinct-public-feed-release",
                    "not-collapsed-by-governed-publication-unit",
                ),
                confidence="high",
                decision_source="governed-transcript-forensic-decision",
            )

    # Only legacy-vs-modern pairs for episode numbers 2-27 are governed
    # automatic candidates.  Same-number evidence still requires meaningful
    # normalized title-token corroboration.
    for episode_number in range(2, 28):
        modern = modern_by_number.get(episode_number, [])
        legacy = legacy_by_number.get(episode_number, [])
        if len(modern) != 1 or len(legacy) != 1:
            candidates = modern + legacy
            if candidates:
                flags.append(
                    _flag(
                        "numbered-pair-cardinality",
                        (str(row["sourceIdentityId"]) for row in candidates),
                        status="pending",
                        reason=(
                            "A governed episode number did not have exactly one modern "
                            "and one legacy source identity."
                        ),
                        episode_number=episode_number,
                        sources=(row.get("source") or {} for row in candidates),
                    )
                )
                for identity in candidates:
                    source_id = str(identity["sourceIdentityId"])
                    mappings_by_source[source_id]["mappingStatus"] = "ambiguous"
                    mappings_by_source[source_id]["mappingRole"] = "candidate"
                    mappings_by_source[source_id]["candidateCanonicalEpisodeId"] = None
                    mappings_by_source[source_id]["mappingBasis"] = [
                        "governed-episode-number-cardinality-unresolved"
                    ]
                    mappings_by_source[source_id]["confidence"] = "low"
            continue

        modern_identity = modern[0]
        legacy_identity = legacy[0]
        corroboration = _token_corroboration(
            modern_identity.get("sourceEpisodeTitle") or modern_identity.get("sourceFile"),
            legacy_identity.get("sourceEpisodeTitle") or legacy_identity.get("sourceFile"),
        )
        canonical_id = str(modern_identity["sourceIdentityId"])
        legacy_id = str(legacy_identity["sourceIdentityId"])
        alias_group_id = f"EAG-{episode_number:03d}"
        if not corroboration["corroborated"]:
            for identity in (modern_identity, legacy_identity):
                source_id = str(identity["sourceIdentityId"])
                mappings_by_source[source_id] = _mapping(
                    identity,
                    canonical_episode_id=source_id,
                    candidate_episode_id=canonical_id,
                    status="likely-alias",
                    role="candidate",
                    basis=("same-governed-episode-number", "title-corroboration-insufficient"),
                    confidence="moderate",
                    alias_group_id=alias_group_id,
                )
            flags.append(
                _flag(
                    "likely-alias-title-review",
                    (canonical_id, legacy_id),
                    status="pending",
                    reason=(
                        "The source identities share a governed episode number but the "
                        "normalized title tokens do not meet the confirmation threshold."
                    ),
                    episode_number=episode_number,
                    evidence=corroboration,
                    sources=(
                        modern_identity.get("source") or {},
                        legacy_identity.get("source") or {},
                    ),
                )
            )
            continue

        basis = (
            "same-governed-episode-number",
            "corroborating-normalized-title-tokens",
            "modern-numbered-source-preferred",
        )
        mappings_by_source[canonical_id] = _mapping(
            modern_identity,
            canonical_episode_id=canonical_id,
            candidate_episode_id=canonical_id,
            status="confirmed-alias",
            role="canonical",
            basis=basis,
            confidence="high",
            alias_group_id=alias_group_id,
        )
        mappings_by_source[legacy_id] = _mapping(
            legacy_identity,
            canonical_episode_id=canonical_id,
            candidate_episode_id=canonical_id,
            status="confirmed-alias",
            role="alias",
            basis=basis,
            confidence="high",
            alias_group_id=alias_group_id,
        )
        canonical_members[canonical_id] = [modern_identity, legacy_identity]
        canonical_members.pop(legacy_id, None)
        alias_groups.append(
            {
                "aliasGroupId": alias_group_id,
                "episodeNumber": episode_number,
                "mappingStatus": "confirmed-alias",
                "canonicalEpisodeId": canonical_id,
                "canonicalSourceIdentityId": canonical_id,
                "sourceIdentityIds": [canonical_id, legacy_id],
                "sourceTitles": [
                    modern_identity.get("sourceEpisodeTitle"),
                    legacy_identity.get("sourceEpisodeTitle"),
                ],
                "sourceFiles": [
                    modern_identity.get("sourceFile"),
                    legacy_identity.get("sourceFile"),
                ],
                "mappingBasis": list(basis),
                "confidence": "high",
                "titleTokenEvidence": corroboration,
                "originalItemCount": int(modern_identity["originalItemCount"])
                + int(legacy_identity["originalItemCount"]),
                "reconciledSensitivityItemCount": int(
                    modern_identity["originalItemCount"]
                ),
            }
        )

    for decision in GOVERNED_DISTINCT_PUBLICATION_REUSES:
        original_id = str(decision["originalSourceIdentityId"])
        reuse_id = str(decision["reuseSourceIdentityId"])
        if original_id not in identity_by_id or reuse_id not in identity_by_id:
            raise ValueError(
                "A governed content-reuse decision references a missing source "
                f"identity: {original_id!r}, {reuse_id!r}."
            )
        flags.append(
            _flag(
                "confirmed-content-reuse-distinct-publication-unit",
                (original_id, reuse_id),
                status="resolved",
                reason=(
                    "The #83 re-release is content-equivalent to the earlier public "
                    "feed record but remains a distinct canonical episode under the "
                    "governed publication unit."
                ),
                episode_number=83,
                evidence={
                    "contentReuse": "confirmed-by-transcript-forensics",
                    "governedTreatment": decision["governedTreatment"],
                    "automaticCollapse": False,
                    "fuzzyTitleRuleUsed": False,
                },
                sources=(
                    identity_by_id[original_id].get("source") or {},
                    identity_by_id[reuse_id].get("source") or {},
                ),
            )
        )

    # One additional precursor/edited-release relationship is confirmed by a
    # governed transcript-forensic decision.  It is deliberately not inferred
    # from fuzzy title similarity during the build.
    for decision in GOVERNED_EDITED_RELEASE_ALIASES:
        canonical_id = str(decision["canonicalSourceIdentityId"])
        alias_id = str(decision["aliasSourceIdentityId"])
        if canonical_id not in identity_by_id or alias_id not in identity_by_id:
            raise ValueError(
                "A governed edited-release alias decision references a missing "
                f"source identity: {canonical_id!r}, {alias_id!r}."
            )
        canonical_identity = identity_by_id[canonical_id]
        alias_identity = identity_by_id[alias_id]
        alias_group_id = str(decision["aliasGroupId"])
        basis = tuple(str(value) for value in decision["mappingBasis"])
        mappings_by_source[canonical_id] = _mapping(
            canonical_identity,
            canonical_episode_id=canonical_id,
            candidate_episode_id=canonical_id,
            status="confirmed-alias",
            role="canonical",
            basis=basis,
            confidence="high",
            alias_group_id=alias_group_id,
            decision_source="governed-transcript-forensic-decision",
        )
        mappings_by_source[alias_id] = _mapping(
            alias_identity,
            canonical_episode_id=canonical_id,
            candidate_episode_id=canonical_id,
            status="confirmed-alias",
            role="alias",
            basis=basis,
            confidence="high",
            alias_group_id=alias_group_id,
            decision_source="governed-transcript-forensic-decision",
        )
        canonical_members[canonical_id] = [canonical_identity, alias_identity]
        canonical_members.pop(alias_id, None)
        alias_groups.append(
            {
                "aliasGroupId": alias_group_id,
                "episodeNumber": decision["episodeNumber"],
                "mappingStatus": "confirmed-alias",
                "canonicalEpisodeId": canonical_id,
                "canonicalSourceIdentityId": canonical_id,
                "sourceIdentityIds": [canonical_id, alias_id],
                "sourceTitles": [
                    canonical_identity.get("sourceEpisodeTitle"),
                    alias_identity.get("sourceEpisodeTitle"),
                ],
                "sourceFiles": [
                    canonical_identity.get("sourceFile"),
                    alias_identity.get("sourceFile"),
                ],
                "mappingBasis": list(basis),
                "confidence": "high",
                "forensicEvidence": {
                    "decisionType": "governed-transcript-forensic-decision",
                    "sequenceSimilarityApproximate": 0.97,
                    "fiveWordShingleOverlapApproximate": 0.633,
                    "explicitEditedReleaseStatement": True,
                    "fuzzyTitleRuleUsed": False,
                },
                "originalItemCount": int(canonical_identity["originalItemCount"])
                + int(alias_identity["originalItemCount"]),
                "reconciledSensitivityItemCount": int(
                    canonical_identity["originalItemCount"]
                ),
            }
        )

    for identity in identities:
        if identity.get("numberEvidenceConflict"):
            source_id = str(identity["sourceIdentityId"])
            mappings_by_source[source_id]["mappingStatus"] = "ambiguous"
            mappings_by_source[source_id]["mappingRole"] = "candidate"
            mappings_by_source[source_id]["candidateCanonicalEpisodeId"] = None
            mappings_by_source[source_id]["mappingBasis"] = [
                "conflicting-episode-number-evidence"
            ]
            mappings_by_source[source_id]["confidence"] = "low"
            flags.append(
                _flag(
                    "conflicting-episode-number-evidence",
                    (source_id,),
                    status="pending",
                    reason="Episode title and source filename encode different episode numbers.",
                    sources=(identity.get("source") or {},),
                )
            )

    mappings = sorted(
        mappings_by_source.values(), key=lambda row: natural_key(row["sourceIdentityId"])
    )
    episodes = sorted(
        (
            _canonical_episode(
                members[0],
                members,
                status=(
                    "confirmed-alias" if len(members) > 1 else "unique"
                ),
            )
            for canonical_id, members in canonical_members.items()
            if mappings_by_source[canonical_id]["mappingStatus"]
            not in {"ambiguous", "likely-alias", "unresolved"}
        ),
        key=lambda row: natural_key(row["episodeId"]),
    )

    # Review candidates are kept as distinct provisional episodes.  This path
    # is not exercised by the governed current corpus but prevents silent loss
    # if future input stops satisfying the automatic rule.
    represented_ids = {row["episodeId"] for row in episodes}
    for mapping in mappings:
        if mapping["mappingStatus"] not in {"likely-alias", "ambiguous", "unresolved"}:
            continue
        source_id = str(mapping["sourceIdentityId"])
        if source_id in represented_ids:
            continue
        identity = identity_by_id[source_id]
        episodes.append(_canonical_episode(identity, [identity], status=mapping["mappingStatus"]))
        represented_ids.add(source_id)
    episodes.sort(key=lambda row: natural_key(row["episodeId"]))

    review_queue = [
        deepcopy(flag)
        for flag in flags
        if flag.get("status") == "pending"
    ]
    return {
        "schemaVersion": RECONCILIATION_SCHEMA_VERSION,
        "methodVersion": RECONCILIATION_METHOD_VERSION,
        "sourceIdentities": identities,
        "episodes": episodes,
        "mappings": mappings,
        "flags": sorted(
            flags, key=lambda row: natural_key(row["episodeReconciliationFlagId"])
        ),
        "aliasGroups": sorted(alias_groups, key=lambda row: natural_key(row["aliasGroupId"])),
        "reviewQueue": sorted(
            review_queue, key=lambda row: natural_key(row["episodeReconciliationFlagId"])
        ),
    }


def apply_episode_reconciliation(
    dataset: Mapping[str, Any], reconciliation: Mapping[str, Any]
) -> dict[str, Any]:
    """Return a copied v1.1 dataset with both source and episode identities."""

    result = deepcopy(dict(dataset))
    mappings = {
        str(row.get("sourceIdentityId")): row
        for row in reconciliation.get("mappings", ())
    }
    reconciled_items: list[dict[str, Any]] = []
    for item in dataset.get("items", ()):
        record = deepcopy(dict(item))
        source_identity_id = str(
            record.get("sourceIdentityId") or record.get("episodeId") or ""
        ).strip()
        mapping = mappings.get(source_identity_id)
        if mapping is None:
            raise ValueError(
                f"Item {record.get('itemId')!r} has unmapped source identity "
                f"{source_identity_id!r}."
            )
        record["sourceIdentityId"] = source_identity_id
        record["episodeId"] = mapping.get("canonicalEpisodeId")
        reconciled_items.append(record)
    result["episodes"] = deepcopy(list(reconciliation.get("episodes", ())))
    result["episode_source_identities"] = deepcopy(
        list(reconciliation.get("sourceIdentities", ()))
    )
    result["episode_source_mappings"] = deepcopy(
        list(reconciliation.get("mappings", ()))
    )
    result["episode_reconciliation_flags"] = deepcopy(
        list(reconciliation.get("flags", ()))
    )
    result["items"] = reconciled_items
    return result


__all__ = (
    "GOVERNED_DISTINCT_PUBLICATION_REUSES",
    "GOVERNED_EDITED_RELEASE_ALIASES",
    "MAPPING_STATUSES",
    "RECONCILIATION_METHOD_VERSION",
    "RECONCILIATION_SCHEMA_VERSION",
    "apply_episode_reconciliation",
    "build_episode_reconciliation",
    "build_source_identity_records",
    "normalize_episode_title",
    "normalize_source_filename",
    "parse_episode_number",
)
