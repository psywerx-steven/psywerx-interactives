"""Transcript-first episode-summary manifest and release helpers.

The transcript corpus and every authoring/QA intermediate are private inputs.
Only the small, explicitly allowlisted summary record is eligible for public
release.  Existing analytical products are deliberately outside this module.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


TRANSCRIPT_SUMMARY_METHOD = "transcript-grounded-synthesis-v1"
SUPPORTED_TRANSCRIPT_EXTENSIONS = (".txt", ".json", ".srt", ".tsv", ".vtt")
PUBLIC_SUMMARY_FIELDS = {
    "episodeId",
    "episodeNumber",
    "episodeTitle",
    "summary",
    "keyTopics",
    "whyItMatters",
    "summaryMethod",
    "transcriptWordCount",
    "summaryWordCount",
}
_WORD_RE = re.compile(r"\b[\w]+(?:[’'-][\w]+)*\b", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")
_NUMBER_RE = re.compile(r"(?:episode\s*)?#?\s*0*(\d{1,3})(?:\D|$)", re.I)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_WHY_SENTENCE_END_RE = re.compile(
    r"[.!?]+(?:[\"'\u2019\u201d)\]\}\u00bb]*)?(?=\s|$)"
)
_WHY_ABBREVIATION_RE = re.compile(
    r"(?:\b(?:mr|mrs|ms|dr|prof|sr|jr|st|vs|etc|no|fig|inc|ltd|co|dept|gen|lt|col|maj|capt|sgt)\.|(?:\b[a-z]\.){2,})$",
    re.I,
)
_QA_STOP_WORDS = {
    "a", "about", "after", "all", "also", "an", "and", "are", "as", "at",
    "be", "because", "been", "between", "both", "but", "by", "can", "could",
    "do", "does", "for", "from", "had", "has", "have", "how", "if", "in",
    "into", "is", "it", "its", "may", "more", "not", "of", "on", "or", "our",
    "over", "should", "so", "such", "than", "that", "the", "their", "these",
    "they", "this", "those", "through", "to", "under", "was", "we", "were",
    "what", "when", "where", "which", "while", "who", "why", "will", "with",
    "would", "you", "your",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _corpus_snapshot_sha256(root: Path) -> str:
    rows = []
    for path in sorted(
        (value for value in root.rglob("*") if value.is_file()),
        key=lambda value: value.relative_to(root).as_posix().casefold(),
    ):
        relative = path.relative_to(root).as_posix()
        rows.append(f"{relative}\t{path.stat().st_size}\t{sha256_file(path)}\n")
    return sha256_bytes("".join(rows).encode("utf-8"))


def word_count(value: object) -> int:
    return len(_WORD_RE.findall(str(value or "")))


def summary_word_count(value: object) -> int:
    """Return the public contract's whitespace-token count."""

    return len(str(value or "").split())


def _text(value: object) -> str:
    return _SPACE_RE.sub(" ", str(value or "")).strip()


def _why_sentence_boundaries(value: object) -> tuple[tuple[int, int], ...]:
    text = _text(value)
    boundaries: list[tuple[int, int]] = []
    for match in _WHY_SENTENCE_END_RE.finditer(text):
        if (
            match.group(0).startswith(".")
            and match.end() < len(text)
            and _WHY_ABBREVIATION_RE.search(text[: match.start() + 1])
        ):
            continue
        boundaries.append(match.span())
    return tuple(boundaries)


def why_sentence_count(value: object) -> int:
    """Count sentence boundaries while ignoring common internal abbreviations."""

    return len(_why_sentence_boundaries(value))


def is_single_why_sentence(value: object) -> bool:
    """Return whether text has one terminal sentence boundary and no trailing clause."""

    text = _text(value)
    boundaries = _why_sentence_boundaries(text)
    return len(boundaries) == 1 and boundaries[0][1] == len(text)


def _normalized_title(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = text.replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _episode_number(value: object) -> int | None:
    match = _NUMBER_RE.search(str(value or ""))
    return int(match.group(1)) if match else None


def _discover_transcript_groups(root: Path) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(root.rglob("*"), key=lambda row: str(row).casefold()):
        if path.is_file() and path.suffix.casefold() in SUPPORTED_TRANSCRIPT_EXTENSIONS:
            groups[_normalized_title(path.stem)].append(path)
    return dict(groups)


def _resolve_selected_txt(
    root: Path,
    expected_file: str,
    episode_title: str,
    episode_number: int | None,
    groups: Mapping[str, Sequence[Path]],
    forbidden_alias_paths: set[Path],
) -> tuple[Path, str, str]:
    expected = root / expected_file
    if expected.is_file() and expected.suffix.casefold() == ".txt":
        return expected, "reconciled-canonical-source-file-exact-txt", "passed"

    normalized_expected = _normalized_title(Path(expected_file).stem)
    exact_normalized = [
        path
        for path in groups.get(normalized_expected, ())
        if path.suffix.casefold() == ".txt"
    ]
    if len(exact_normalized) == 1:
        return (
            exact_normalized[0],
            "reconciled-canonical-source-file-unicode-normalized-txt",
            "passed-unicode-normalization",
        )

    candidates = [
        path
        for paths in groups.values()
        for path in paths
        if path.suffix.casefold() == ".txt"
        and path.resolve() not in forbidden_alias_paths
        and (
            episode_number is None
            or _episode_number(path.stem) == int(episode_number)
        )
    ]
    target = _normalized_title(episode_title)
    scored = sorted(
        (
            SequenceMatcher(None, target, _normalized_title(path.stem)).ratio(),
            path,
        )
        for path in candidates
    )
    if not scored:
        raise ValueError(f"No TXT transcript candidate exists for {episode_title!r}.")
    best_score, best_path = scored[-1]
    next_score = scored[-2][0] if len(scored) > 1 else 0.0
    if best_score < 0.88 or best_score - next_score < 0.05:
        raise ValueError(
            f"Transcript filename mismatch is not uniquely resolvable for {episode_title!r}; "
            f"best={best_path.name!r} ({best_score:.3f}), margin={best_score-next_score:.3f}."
        )
    return (
        best_path,
        "reconciled-canonical-title-unique-high-confidence-filename-drift-txt",
        "resolved-filename-drift",
    )


def _resolved_identity_txt(
    root: Path,
    source_file: str,
    groups: Mapping[str, Sequence[Path]],
) -> Path | None:
    """Resolve only exact or Unicode-normalized governed identity filenames."""

    expected = root / source_file
    if expected.is_file() and expected.suffix.casefold() == ".txt":
        return expected.resolve()
    candidates = [
        path.resolve()
        for path in groups.get(_normalized_title(Path(source_file).stem), ())
        if path.suffix.casefold() == ".txt"
    ]
    return candidates[0] if len(candidates) == 1 else None


def _token_shingles(value: str, size: int = 5) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9]+", value.casefold())
    return {
        tuple(words[index : index + size])
        for index in range(max(0, len(words) - size + 1))
    }


def _variant_transcript_text(path: Path) -> str:
    """Extract only transcript prose from each supported private representation."""

    value = _read_text(path)
    suffix = path.suffix.casefold()
    if suffix == ".txt":
        return _text(value)
    if suffix == ".json":
        payload = json.loads(value)
        if not isinstance(payload, Mapping) or not isinstance(payload.get("text"), str):
            raise ValueError(f"Transcript JSON has no top-level text value: {path}")
        return _text(payload["text"])
    if suffix == ".tsv":
        rows = [line.split("\t", 2) for line in value.splitlines()[1:]]
        if not rows or any(len(row) != 3 for row in rows):
            raise ValueError(f"Transcript TSV does not use start/end/text rows: {path}")
        return _text(" ".join(row[2] for row in rows))
    if suffix in {".srt", ".vtt"}:
        lines = value.splitlines()
        prose: list[str] = []
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped == "WEBVTT" or "-->" in stripped:
                continue
            if (
                suffix == ".srt"
                and stripped.isdigit()
                and index + 1 < len(lines)
                and "-->" in lines[index + 1]
            ):
                continue
            prose.append(stripped)
        return _text(" ".join(prose))
    raise ValueError(f"Unsupported transcript representation: {path}")


def _qa_tokens(value: object) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").casefold())
        if len(token) > 1 and token not in _QA_STOP_WORDS
    ]


def _lexically_supported(token: str, candidates: set[str]) -> bool:
    """Allow exact terms and conservative long-token inflectional variants."""

    return token in candidates or (
        len(token) >= 7
        and any(
            len(candidate) >= 7 and candidate[:6] == token[:6]
            for candidate in candidates
        )
    )


def _idf(documents: Sequence[set[str]]) -> dict[str, float]:
    frequency: Counter[str] = Counter()
    for document in documents:
        frequency.update(document)
    count = len(documents)
    return {
        token: math.log((count + 1) / (document_frequency + 1)) + 1.0
        for token, document_frequency in frequency.items()
    }


def _weighted_vector(tokens: Iterable[str], idf: Mapping[str, float]) -> dict[str, float]:
    counts = Counter(tokens)
    return {
        token: (1.0 + math.log(count)) * float(idf.get(token, 1.0))
        for token, count in counts.items()
    }


def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    numerator = sum(left[token] * right[token] for token in set(left) & set(right))
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _maximum_verbatim_words(summary: str, transcript: str, ceiling: int = 30) -> int:
    summary_words = re.findall(r"[a-z0-9]+", summary.casefold())
    transcript_words = re.findall(r"[a-z0-9]+", transcript.casefold())
    maximum = min(ceiling, len(summary_words), len(transcript_words))
    for size in range(maximum, 7, -1):
        transcript_ngrams = {
            tuple(transcript_words[index : index + size])
            for index in range(len(transcript_words) - size + 1)
        }
        if any(
            tuple(summary_words[index : index + size]) in transcript_ngrams
            for index in range(len(summary_words) - size + 1)
        ):
            return size
    return 0


def run_corpus_summary_qa(
    summaries: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
    manifest: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Run deterministic full-corpus grounding, identity, and template checks."""

    words_by_id = {
        str(row["episodeId"]): int(row["transcriptWordCount"]) for row in manifest
    }
    validated = validate_public_transcript_summaries(summaries, episodes, words_by_id)
    manifest_by_id = {str(row["episodeId"]): row for row in manifest}
    transcripts = {
        episode_id: _read_text(Path(row["cleanedTranscriptPath"]))
        for episode_id, row in manifest_by_id.items()
    }
    transcript_token_sets = {
        episode_id: set(_qa_tokens(text)) for episode_id, text in transcripts.items()
    }
    transcript_idf = _idf(list(transcript_token_sets.values()))
    issues: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    summary_token_lists = [_qa_tokens(row["summary"]) for row in validated]
    summary_idf = _idf([set(tokens) for tokens in summary_token_lists])
    summary_vectors = [_weighted_vector(tokens, summary_idf) for tokens in summary_token_lists]

    opening_counts = Counter(
        " ".join(re.findall(r"[a-z0-9]+", row["summary"].casefold())[:8])
        for row in validated
    )
    for opening, count in opening_counts.items():
        if opening and count > 3:
            issues.append(
                {
                    "severity": "error",
                    "code": "repeated-opening-template",
                    "episodeIds": [
                        row["episodeId"]
                        for row in validated
                        if " ".join(
                            re.findall(r"[a-z0-9]+", row["summary"].casefold())[:8]
                        ) == opening
                    ],
                    "detail": f"Eight-word opening occurs {count} times: {opening}",
                }
            )

    mechanical_openings = (
        "this episode discusses", "this episode focuses on",
        "the podcast talks about", "in this episode",
    )
    mechanical_rows = [
        row["episodeId"]
        for row in validated
        if row["summary"].casefold().startswith(mechanical_openings)
    ]
    if len(mechanical_rows) > 6:
        issues.append(
            {
                "severity": "error",
                "code": "excessive-mechanical-openings",
                "episodeIds": mechanical_rows,
                "detail": f"Mechanical openings occur {len(mechanical_rows)} times.",
            }
        )

    known_reuse_pair = {"EPI-72E94D7AF43A4BD3", "EPI-9960393907F71603"}
    similarity_pairs: list[dict[str, Any]] = []
    for left_index, left in enumerate(validated):
        for right_index in range(left_index + 1, len(validated)):
            right = validated[right_index]
            similarity = _cosine(summary_vectors[left_index], summary_vectors[right_index])
            if similarity >= 0.62:
                known_reuse = {left["episodeId"], right["episodeId"]} == known_reuse_pair
                pair = {
                    "episodeIds": [left["episodeId"], right["episodeId"]],
                    "tfidfCosine": round(similarity, 6),
                    "knownContentReuse": known_reuse,
                }
                similarity_pairs.append(pair)
                if similarity >= 0.72 and not known_reuse:
                    issues.append(
                        {
                            "severity": "review",
                            "code": "near-duplicate-summary",
                            **pair,
                            "detail": "Unusually high summary lexical similarity.",
                        }
                    )

    for row in validated:
        episode_id = row["episodeId"]
        transcript = transcripts[episode_id]
        transcript_folded = transcript.casefold()
        transcript_tokens = transcript_token_sets[episode_id]
        combined = f"{row['summary']} {row['whyItMatters']}"
        combined_set = set(
            _qa_tokens(
                f"{row['summary']} {' '.join(row['keyTopics'])} {row['whyItMatters']}"
            )
        )
        denominator = sum(transcript_idf.get(token, 1.0) for token in combined_set)
        identity_scores = {
            candidate_id: (
                sum(
                    transcript_idf.get(token, 1.0)
                    for token in combined_set & candidate_tokens
                ) / denominator if denominator else 0.0
            )
            for candidate_id, candidate_tokens in transcript_token_sets.items()
        }
        ranked = sorted(identity_scores, key=identity_scores.get, reverse=True)
        identity_rank = ranked.index(episode_id) + 1
        own_coverage = identity_scores[episode_id]
        if identity_rank > 5 or own_coverage < 0.25:
            issues.append(
                {
                    "severity": "review",
                    "code": "possible-transcript-identity-mismatch",
                    "episodeIds": [episode_id],
                    "detail": (
                        f"Own transcript rank={identity_rank}; weighted token coverage="
                        f"{own_coverage:.3f}; top match={ranked[0]}."
                    ),
                }
            )

        ungrounded_topics = []
        for topic in row["keyTopics"]:
            tokens = set(_qa_tokens(topic))
            if tokens and not any(
                _lexically_supported(token, transcript_tokens) for token in tokens
            ):
                ungrounded_topics.append(topic)
        if ungrounded_topics:
            issues.append(
                {
                    "severity": "review",
                    "code": "topic-without-lexical-transcript-support",
                    "episodeIds": [episode_id],
                    "detail": ungrounded_topics,
                }
            )

        why_tokens = set(_qa_tokens(row["whyItMatters"]))
        why_overlap = (
            sum(
                _lexically_supported(token, transcript_tokens)
                for token in why_tokens
            )
            / len(why_tokens)
            if why_tokens
            else 0.0
        )
        if why_overlap < 0.35:
            issues.append(
                {
                    "severity": "review",
                    "code": "why-it-matters-low-lexical-support",
                    "episodeIds": [episode_id],
                    "detail": f"Content-token overlap={why_overlap:.3f}.",
                }
            )

        quote_fragments = re.findall(r"[“\"]([^”\"]{4,})[”\"]", combined)
        unsupported_quotes = [
            quote for quote in quote_fragments if _text(quote).casefold() not in transcript_folded
        ]
        if unsupported_quotes:
            issues.append(
                {
                    "severity": "error",
                    "code": "invented-or-unsupported-quote",
                    "episodeIds": [episode_id],
                    "detail": unsupported_quotes,
                }
            )

        numeric_claims = sorted(set(re.findall(r"\b\d[\d,./:%-]*\b", combined)))
        unsupported_numbers = [
            number for number in numeric_claims if number.casefold() not in transcript_folded
        ]
        if unsupported_numbers:
            issues.append(
                {
                    "severity": "error",
                    "code": "unsupported-numerical-claim",
                    "episodeIds": [episode_id],
                    "detail": unsupported_numbers,
                }
            )

        proper_phrases = sorted(
            set(
                match.group(0)
                for match in re.finditer(
                    r"\b(?:[A-Z][A-Za-z’'-]{2,})(?:\s+(?:[A-Z][A-Za-z’'-]{2,}|of|the|and|for)){1,4}\b",
                    combined,
                )
            )
        )
        proper_name_support = transcript_tokens | set(_qa_tokens(row["episodeTitle"]))
        unsupported_names = []
        for phrase in proper_phrases:
            proper_tokens = set(_qa_tokens(phrase)) - {"of", "the", "and", "for"}
            missing_tokens = proper_tokens - proper_name_support
            us_spelling_equivalent = (
                {"united", "states"} <= missing_tokens and "us" in proper_name_support
            )
            if (
                len(proper_tokens) >= 2
                and len(missing_tokens) >= 2
                and not us_spelling_equivalent
            ):
                unsupported_names.append(
                    {"phrase": phrase, "unsupportedTokens": sorted(missing_tokens)}
                )
        if unsupported_names:
            issues.append(
                {
                    "severity": "review",
                    "code": "unsupported-proper-name-or-phrase",
                    "episodeIds": [episode_id],
                    "detail": unsupported_names,
                }
            )

        maximum_verbatim = _maximum_verbatim_words(row["summary"], transcript)
        if maximum_verbatim >= 20:
            issues.append(
                {
                    "severity": "review",
                    "code": "excessive-verbatim-transcript-overlap",
                    "episodeIds": [episode_id],
                    "detail": f"Longest detected exact sequence is {maximum_verbatim} words.",
                }
            )
        diagnostics.append(
            {
                "episodeId": episode_id,
                "identityRank": identity_rank,
                "ownTranscriptWeightedTokenCoverage": round(own_coverage, 6),
                "whyItMattersTokenOverlap": round(why_overlap, 6),
                "maximumVerbatimTranscriptWords": maximum_verbatim,
                "unsupportedNumericClaims": unsupported_numbers,
                "unsupportedProperNamesOrPhrases": unsupported_names,
                "ungroundedTopics": ungrounded_topics,
            }
        )

    lengths = [row["summaryWordCount"] for row in validated]
    issue_counts = Counter(row["severity"] for row in issues)
    return {
        "status": "pass" if not issue_counts.get("error") else "fail",
        "summaryCount": len(validated),
        "summaryWordStatistics": {
            "minimum": min(lengths), "maximum": max(lengths),
            "mean": round(statistics.fmean(lengths), 3),
            "median": statistics.median(lengths),
        },
        "keyTopicCompleteness": sum(3 <= len(row["keyTopics"]) <= 6 for row in validated),
        "whyItMattersCompleteness": sum(bool(row["whyItMatters"]) for row in validated),
        "mechanicalOpeningCount": len(mechanical_rows),
        "highSimilarityPairs": sorted(
            similarity_pairs, key=lambda value: value["tfidfCosine"], reverse=True
        ),
        "issueCounts": dict(sorted(issue_counts.items())),
        "issues": issues,
        "episodeDiagnostics": diagnostics,
    }


def build_old_new_comparison(
    old_summaries: Sequence[Mapping[str, Any]],
    new_summaries: Sequence[Mapping[str, Any]],
    automatic_qa: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create private lexical-semantic comparison metrics for identity-error review."""

    old_by_id = {str(row["episodeId"]): row for row in old_summaries}
    new_by_id = {str(row["episodeId"]): row for row in new_summaries}
    if set(old_by_id) != set(new_by_id):
        raise ValueError("Old/new summary IDs must match exactly.")
    documents = [
        set(_qa_tokens(row.get("summary")))
        for row in list(old_by_id.values()) + list(new_by_id.values())
    ]
    idf = _idf(documents)
    qa_severities: dict[str, set[str]] = defaultdict(set)
    if automatic_qa is not None:
        for issue in automatic_qa.get("issues", ()):
            severity = str(issue.get("severity") or "review")
            for episode_id in issue.get("episodeIds", ()):
                qa_severities[str(episode_id)].add(severity)
    rows: list[dict[str, Any]] = []
    for episode_id in sorted(new_by_id):
        old_tokens = _qa_tokens(old_by_id[episode_id].get("summary"))
        new_tokens = _qa_tokens(new_by_id[episode_id].get("summary"))
        similarity = _cosine(
            _weighted_vector(old_tokens, idf), _weighted_vector(new_tokens, idf)
        )
        old_set, new_set = set(old_tokens), set(new_tokens)
        severities = qa_severities.get(episode_id, set())
        if "error" in severities:
            quality_assessment = "automatic-grounding-error-requires-correction"
        elif severities:
            quality_assessment = "automatic-grounding-review-flag"
        elif automatic_qa is not None:
            quality_assessment = "automatic-grounding-checks-passed"
        else:
            quality_assessment = "automatic-grounding-assessment-unavailable"
        rows.append(
            {
                "episodeId": episode_id,
                "tfidfSemanticSimilarity": round(similarity, 6),
                "notableContentAdditions": sorted(
                    new_set - old_set, key=lambda token: (-idf.get(token, 1.0), token)
                )[:10],
                "notableContentOmissions": sorted(
                    old_set - new_set, key=lambda token: (-idf.get(token, 1.0), token)
                )[:10],
                "substantiallyChangedEmphasis": similarity < 0.28,
                "transcriptSummaryQualityAssessment": quality_assessment,
            }
        )
    similarities = [row["tfidfSemanticSimilarity"] for row in rows]
    quality_counts = Counter(
        row["transcriptSummaryQualityAssessment"] for row in rows
    )
    return {
        "method": "per-episode TF-IDF cosine used as a semantic-similarity proxy",
        "purpose": "identity and surprising-emphasis error detection, not pressure to match the old summary",
        "episodeCount": len(rows),
        "similarityStatistics": {
            "minimum": min(similarities), "maximum": max(similarities),
            "mean": round(statistics.fmean(similarities), 6),
            "median": statistics.median(similarities),
        },
        "substantiallyChangedEmphasisCount": sum(
            row["substantiallyChangedEmphasis"] for row in rows
        ),
        "qualityAssessmentCounts": dict(sorted(quality_counts.items())),
        "records": rows,
    }


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"Transcript is not readable as UTF-8/UTF-8-SIG/CP1252: {path}")


def clean_transcript(raw_text: str) -> tuple[str, list[dict[str, Any]]]:
    """Remove only recognizable show boilerplate and preserve conversation text."""

    text = _text(raw_text)
    actions: list[dict[str, Any]] = []
    opening_marker = "welcome to the cognitive crucible"
    if text.casefold().startswith(opening_marker):
        first_window = text[:1200]
        marker_matches = list(re.finditer(r"cognitive security[.!?]", first_window, re.I))
        if marker_matches:
            end = marker_matches[0].end()
            removed = text[:end].strip()
            if 8 <= word_count(removed) <= 100:
                actions.append(
                    {
                        "action": "remove-standard-opening-boilerplate",
                        "rawCharacterStart": 0,
                        "rawCharacterEnd": end,
                        "removedWordCount": word_count(removed),
                        "sha256": sha256_bytes(removed.encode("utf-8")),
                    }
                )
                text = text[end:].strip()

    closing_marker = (
        "the cognitive crucible is the only podcast dedicated to increasing "
        "interdisciplinary collaboration"
    )
    closing_at = text.casefold().rfind(closing_marker)
    if closing_at >= int(len(text) * 0.65):
        removed = text[closing_at:].strip()
        actions.append(
            {
                "action": "remove-standard-closing-boilerplate",
                "cleanedCharacterStart": closing_at,
                "cleanedCharacterEnd": len(text),
                "removedWordCount": word_count(removed),
                "sha256": sha256_bytes(removed.encode("utf-8")),
            }
        )
        text = text[:closing_at].strip()

    if not text or word_count(text) == 0:
        raise ValueError("Transcript cleaning removed all readable content.")
    return text, actions


def _sentence_chunks(text: str, maximum_words: int) -> list[str]:
    sentences = [part.strip() for part in _SENTENCE_RE.split(text) if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0
    for sentence in sentences:
        count = word_count(sentence)
        if count > maximum_words:
            words = sentence.split()
            for offset in range(0, len(words), maximum_words):
                if current:
                    chunks.append(" ".join(current))
                    current, current_words = [], 0
                chunks.append(" ".join(words[offset : offset + maximum_words]))
            continue
        if current and current_words + count > maximum_words:
            chunks.append(" ".join(current))
            current, current_words = [], 0
        current.append(sentence)
        current_words += count
    if current:
        chunks.append(" ".join(current))
    return chunks or [text]


def _mapping_for_source(
    mappings: Sequence[Mapping[str, Any]], source_identity_id: str
) -> Mapping[str, Any]:
    matches = [
        row for row in mappings if row.get("sourceIdentityId") == source_identity_id
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one reconciliation mapping for {source_identity_id}; found {len(matches)}."
        )
    return matches[0]


def build_transcript_manifest(
    transcript_root: Path,
    reconciliation: Mapping[str, Any],
    public_episodes: Sequence[Mapping[str, Any]],
    private_dir: Path,
    public_summary_backup: Sequence[Mapping[str, Any]],
    chunk_words: int = 4_000,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Build and persist the governed 242-release private transcript manifest."""

    if chunk_words < 1_000:
        raise ValueError("Transcript chunks must contain at least 1,000 target words.")
    if not transcript_root.is_dir():
        raise FileNotFoundError(f"Transcript root does not exist: {transcript_root}")

    source_identities = {
        str(row["sourceIdentityId"]): row
        for row in reconciliation.get("sourceIdentities", ())
    }
    mappings = list(reconciliation.get("mappings", ()))
    reconciled_episodes = {
        str(row["episodeId"]): row for row in reconciliation.get("episodes", ())
    }
    public_by_id = {str(row["episodeId"]): row for row in public_episodes}
    if len(public_by_id) != 242 or set(public_by_id) != set(reconciled_episodes):
        raise ValueError("Public episodes and governed reconciliation must match at 242 IDs.")
    if len(source_identities) != 269 or len(mappings) != 269:
        raise ValueError("Governed v1.1 reconciliation must contain 269 source identities/mappings.")

    groups = _discover_transcript_groups(transcript_root)
    mapping_by_source = {
        str(row["sourceIdentityId"]): row for row in mappings
    }
    governed_identity_paths = {
        source_id: _resolved_identity_txt(
            transcript_root,
            str(identity["sourceFile"]),
            groups,
        )
        for source_id, identity in source_identities.items()
    }
    alias_paths = {
        path
        for source_id, path in governed_identity_paths.items()
        if path is not None and mapping_by_source[source_id].get("mappingRole") == "alias"
    }
    manifest: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    selected_paths: set[Path] = set()
    variant_comparison_counts: Counter[str] = Counter()
    cleaned_dir = private_dir / "cleaned_transcripts"
    chunks_dir = private_dir / "chunks"

    for episode_id in sorted(public_by_id):
        public = public_by_id[episode_id]
        governed = reconciled_episodes[episode_id]
        source_id = str(governed["canonicalSourceIdentityId"])
        identity = source_identities[source_id]
        episode_number = public.get("parsedEpisodeNumber")
        episode_title = _text(public.get("episodeTitle"))
        selected, selection_basis, review_status = _resolve_selected_txt(
            transcript_root,
            str(identity["sourceFile"]),
            episode_title,
            episode_number,
            groups,
            alias_paths,
        )
        selected = selected.resolve()
        if selected in selected_paths:
            raise ValueError(f"Transcript file selected for more than one release: {selected}")
        selected_paths.add(selected)

        raw_bytes = selected.read_bytes()
        raw_text = _read_text(selected)
        if not raw_text.strip():
            raise ValueError(f"Selected transcript is empty: {selected}")
        cleaned_text, cleaning_actions = clean_transcript(raw_text)
        cleaned_path = cleaned_dir / f"{episode_id}.txt"
        cleaned_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_path.write_text(cleaned_text + "\n", encoding="utf-8")

        chunk_rows: list[dict[str, Any]] = []
        start_word = 1
        chunk_texts = _sentence_chunks(cleaned_text, chunk_words)
        episode_chunk_dir = chunks_dir / episode_id
        episode_chunk_dir.mkdir(parents=True, exist_ok=True)
        for index, chunk in enumerate(chunk_texts, 1):
            count = word_count(chunk)
            chunk_path = episode_chunk_dir / f"chunk-{index:03d}.txt"
            chunk_path.write_text(chunk + "\n", encoding="utf-8")
            chunk_rows.append(
                {
                    "chunkId": f"{episode_id}-CHUNK-{index:03d}",
                    "chunkNumber": index,
                    "privatePath": str(chunk_path.resolve()),
                    "startWord": start_word,
                    "endWord": start_word + count - 1,
                    "wordCount": count,
                    "sha256": sha256_file(chunk_path),
                }
            )
            start_word += count

        selected_group = list(groups[_normalized_title(selected.stem)])
        selected_extensions = {path.suffix.casefold() for path in selected_group}
        if selected_extensions != set(SUPPORTED_TRANSCRIPT_EXTENSIONS):
            raise ValueError(
                f"Transcript bundle {selected.stem!r} must contain exactly the five supported formats."
            )
        selected_representation = _variant_transcript_text(selected)
        variants = []
        for path in sorted(selected_group, key=lambda row: row.suffix.casefold()):
            if path.resolve() == selected:
                continue
            variant_representation = _variant_transcript_text(path)
            if variant_representation == selected_representation:
                comparison_status = "exact-normalized-text-match"
                similarity = 1.0
            else:
                similarity = SequenceMatcher(
                    None, selected_representation, variant_representation
                ).ratio()
                comparison_status = (
                    "near-exact-nonmaterial-representation-difference"
                    if similarity >= 0.999
                    else "material-text-difference"
                )
            variant_comparison_counts[comparison_status] += 1
            if comparison_status == "material-text-difference":
                raise ValueError(
                    f"Transcript format variant differs materially from selected TXT: {path}; "
                    f"normalized character similarity={similarity:.6f}."
                )
            variants.append({
                "path": str(path.resolve()),
                "fileType": path.suffix.casefold().lstrip("."),
                "byteCount": path.stat().st_size,
                "sha256": sha256_file(path),
                "normalizedTranscriptTextSha256": sha256_bytes(
                    variant_representation.encode("utf-8")
                ),
                "selectedTextCharacterSimilarity": round(similarity, 6),
                "contentComparisonStatus": comparison_status,
            })
        canonical_mapping = _mapping_for_source(mappings, source_id)
        alias_mappings = [
            row
            for row in mappings
            if row.get("canonicalEpisodeId") == episode_id
            and row.get("mappingRole") == "alias"
        ]
        excluded_aliases = []
        for alias_mapping in alias_mappings:
            alias_identity = source_identities[str(alias_mapping["sourceIdentityId"])]
            excluded_aliases.append(
                {
                    "sourceIdentityId": alias_mapping["sourceIdentityId"],
                    "sourceFile": alias_identity.get("sourceFile"),
                    "mappingBasis": list(alias_mapping.get("mappingBasis", ())),
                }
            )

        raw_words = word_count(raw_text)
        cleaned_words = word_count(cleaned_text)
        record = {
            "episodeId": episode_id,
            "episodeNumber": episode_number,
            "canonicalPublicTitle": episode_title,
            "selectedTranscriptPath": str(selected),
            "selectedFileType": "txt",
            "transcriptSha256": sha256_bytes(raw_bytes),
            "transcriptCharacterCount": len(raw_text),
            "transcriptWordCount": raw_words,
            "cleanedTranscriptPath": str(cleaned_path.resolve()),
            "cleanedTranscriptWordCount": cleaned_words,
            "sourceSelectionBasis": selection_basis,
            "otherTranscriptVariantsDiscovered": variants,
            "duplicateAliasStatus": (
                "confirmed-alias-transcripts-excluded" if excluded_aliases else "unique-source-identity"
            ),
            "excludedAliasTranscripts": excluded_aliases,
            "contentReuseStatus": "none-detected",
            "reconciliationProvenance": {
                "schemaVersion": reconciliation.get("schemaVersion"),
                "methodVersion": reconciliation.get("methodVersion"),
                "canonicalSourceIdentityId": source_id,
                "mappingStatus": canonical_mapping.get("mappingStatus"),
                "mappingRole": canonical_mapping.get("mappingRole"),
                "decisionSource": canonical_mapping.get("decisionSource"),
                "aliasGroupId": canonical_mapping.get("aliasGroupId"),
                "mappingBasis": list(canonical_mapping.get("mappingBasis", ())),
            },
            "selectionConfidence": "high",
            "reviewStatus": review_status,
        }
        manifest.append(record)
        coverage.append(
            {
                "episodeId": episode_id,
                "rawTranscriptWordCount": raw_words,
                "cleanedTranscriptWordCount": cleaned_words,
                "boilerplateCleaningActions": cleaning_actions,
                "chunkCount": len(chunk_rows),
                "chunks": chunk_rows,
                "rawBeginningToEndInspected": True,
                "cleanedSequentialCoverageComplete": (
                    bool(chunk_rows)
                    and chunk_rows[0]["startWord"] == 1
                    and chunk_rows[-1]["endWord"] == cleaned_words
                    and sum(row["wordCount"] for row in chunk_rows) == cleaned_words
                ),
            }
        )

    # The governed reconciliation explicitly retains this re-release as a
    # distinct publication unit despite recording reuse.  Its wrappers and
    # Whisper punctuation differ, so validate content equivalence rather than
    # requiring byte-identical files.
    reuse_ids = ("EPI-72E94D7AF43A4BD3", "EPI-9960393907F71603")
    manifest_by_id = {row["episodeId"]: row for row in manifest}
    reuse_text = [
        _read_text(Path(manifest_by_id[episode_id]["cleanedTranscriptPath"]))
        for episode_id in reuse_ids
    ]
    reuse_shingles = [_token_shingles(value) for value in reuse_text]
    reuse_intersection = reuse_shingles[0] & reuse_shingles[1]
    reuse_containment = len(reuse_intersection) / min(
        len(reuse_shingles[0]), len(reuse_shingles[1])
    )
    if reuse_containment < 0.85:
        raise ValueError(
            "The governed episode-83/re-release transcript reuse pair failed content validation; "
            f"five-word-shingle containment={reuse_containment:.3f}."
        )
    for episode_id, related_id in (reuse_ids, tuple(reversed(reuse_ids))):
        manifest_by_id[episode_id]["contentReuseStatus"] = {
            "status": "confirmed-content-reuse-distinct-public-release",
            "relatedEpisodeIds": [related_id],
            "fiveWordShingleContainment": round(reuse_containment, 6),
            "basis": "governed-transcript-forensic-decision",
        }

    discovered_txt = {
        path.resolve()
        for paths in groups.values()
        for path in paths
        if path.suffix.casefold() == ".txt"
    }
    canonical_paths = set(selected_paths)
    if canonical_paths & alias_paths:
        raise ValueError("A governed alias transcript was selected as canonical.")
    unmatched_paths = discovered_txt - canonical_paths - alias_paths
    if len(discovered_txt) != 271 or len(alias_paths) != 27 or len(unmatched_paths) != 2:
        raise ValueError(
            "Transcript corpus classification must resolve 271 TXT identities as "
            "242 canonical, 27 aliases, and 2 governed-out-of-scope extras."
        )
    inventory = {
        "canonical": [str(path) for path in sorted(canonical_paths, key=str)],
        "excludedAliases": [str(path) for path in sorted(alias_paths, key=str)],
        "excludedOutsideGovernedCorpus": [
            str(path) for path in sorted(unmatched_paths, key=str)
        ],
    }

    if len(manifest) != 242 or len(selected_paths) != 242:
        raise ValueError("Transcript manifest must contain 242 unique selected files.")
    if not all(row["cleanedSequentialCoverageComplete"] for row in coverage):
        raise ValueError("Every selected transcript must have complete sequential chunk coverage.")
    write_json(private_dir / "transcript_manifest.json", manifest)
    write_json(private_dir / "chunk_coverage.json", coverage)
    write_json(private_dir / "corpus_file_classification.json", inventory)
    write_json(private_dir / "published_summary_backup.json", list(public_summary_backup))
    report = {
        "status": "pass",
        "canonicalReleaseCount": len(manifest),
        "selectedTranscriptCount": len(selected_paths),
        "selectedFileTypes": {"txt": len(manifest)},
        "operationalSourceRoot": str(transcript_root.resolve()),
        "corpusSnapshotSha256": _corpus_snapshot_sha256(transcript_root),
        "discoveredTranscriptFileCount": sum(
            len(paths) for paths in groups.values()
        ),
        "sourceIdentityCount": len(source_identities),
        "excludedAliasIdentityCount": sum(
            1 for row in mappings if row.get("mappingRole") == "alias"
        ),
        "filenameDriftResolutions": sum(
            row["reviewStatus"] == "resolved-filename-drift" for row in manifest
        ),
        "discoveredTranscriptIdentityCount": len(discovered_txt),
        "excludedAliasTranscriptCount": len(alias_paths),
        "excludedFormatVariantFileCount": len(manifest) * 4,
        "excludedAliasFileCount": len(alias_paths) * 5,
        "excludedOutsideGovernedCorpusCount": len(unmatched_paths),
        "excludedOutsideGovernedCorpusFileCount": len(unmatched_paths) * 5,
        "formatVariantComparisonCount": sum(variant_comparison_counts.values()),
        "exactNormalizedFormatVariantMatches": variant_comparison_counts[
            "exact-normalized-text-match"
        ],
        "nearExactNonmaterialFormatVariantDifferences": variant_comparison_counts[
            "near-exact-nonmaterial-representation-difference"
        ],
        "materialFormatVariantDifferences": variant_comparison_counts[
            "material-text-difference"
        ],
        "contentReuseGroupCount": 1,
        "strictUniqueContentUnits": 241,
        "contentReuseFiveWordShingleContainment": round(reuse_containment, 6),
        "rawTranscriptWords": sum(row["transcriptWordCount"] for row in manifest),
        "cleanedTranscriptWords": sum(
            row["cleanedTranscriptWordCount"] for row in manifest
        ),
        "chunkCount": sum(row["chunkCount"] for row in coverage),
        "chunkTargetWords": chunk_words,
        "coverageComplete": True,
    }
    write_json(private_dir / "manifest_report.json", report)
    return manifest, coverage, report


def validate_public_transcript_summaries(
    summaries: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
    transcript_words_by_id: Mapping[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Validate and normalize the transcript-first public summary allowlist."""

    episodes_by_id = {str(row["episodeId"]): row for row in episodes}
    ids = [str(row.get("episodeId") or "") for row in summaries]
    if len(summaries) != 242 or len(ids) != len(set(ids)) or set(ids) != set(episodes_by_id):
        raise ValueError("Transcript summaries must cover all 242 canonical episode IDs once.")
    validated: list[dict[str, Any]] = []
    seen_text: set[str] = set()
    for source in summaries:
        episode_id = (
            source.get("episodeId")
            if type(source.get("episodeId")) is str
            else "<invalid>"
        )
        if set(source) != PUBLIC_SUMMARY_FIELDS:
            raise ValueError(f"Summary {episode_id} does not match the public 9-field allowlist.")
        string_fields = (
            "episodeId",
            "episodeTitle",
            "summary",
            "whyItMatters",
            "summaryMethod",
        )
        if any(type(source.get(field)) is not str for field in string_fields):
            raise ValueError(f"Summary {episode_id} has a non-string public text field.")
        raw_topics = source.get("keyTopics")
        if (
            type(raw_topics) is not list
            or not all(type(value) is str and value.strip() for value in raw_topics)
        ):
            raise ValueError(
                f"Summary {episode_id} keyTopics must be a JSON array of nonblank strings."
            )
        episode_number = source.get("episodeNumber")
        if episode_number is not None and type(episode_number) is not int:
            raise ValueError(
                f"Summary {episode_id} episodeNumber must be an integer or null."
            )
        raw_transcript_words = source.get("transcriptWordCount")
        if type(raw_transcript_words) is not int or raw_transcript_words <= 0:
            raise ValueError(
                f"Summary {episode_id} transcriptWordCount must be a positive integer."
            )
        raw_summary_words = source.get("summaryWordCount")
        if type(raw_summary_words) is not int:
            raise ValueError(
                f"Summary {episode_id} summaryWordCount must be an integer."
            )
        episode = episodes_by_id[episode_id]
        title = _text(source.get("episodeTitle"))
        summary = _text(source.get("summary"))
        topics = [_text(value) for value in raw_topics]
        matters = _text(source.get("whyItMatters"))
        summary_words = summary_word_count(summary)
        transcript_words = raw_transcript_words
        if episode_number != episode.get("parsedEpisodeNumber"):
            raise ValueError(f"Summary {episode_id} has the wrong episode number.")
        if title != _text(episode.get("episodeTitle")):
            raise ValueError(f"Summary {episode_id} has the wrong episode title.")
        if not 100 <= summary_words <= 180:
            raise ValueError(f"Summary {episode_id} has {summary_words} words; expected 100-180.")
        if raw_summary_words != summary_words:
            raise ValueError(f"Summary {episode_id} has an incorrect summaryWordCount.")
        if not 3 <= len(topics) <= 6 or not all(topics):
            raise ValueError(f"Summary {episode_id} must contain 3-6 nonblank topics.")
        if len({value.casefold() for value in topics}) != len(topics):
            raise ValueError(f"Summary {episode_id} has duplicate key topics.")
        if not matters or transcript_words <= 0:
            raise ValueError(f"Summary {episode_id} lacks required transcript grounding fields.")
        why_words = summary_word_count(matters)
        if not 10 <= why_words <= 45 or not is_single_why_sentence(matters):
            raise ValueError(
                f"Summary {episode_id} whyItMatters must be one concise 10-45-word sentence."
            )
        if source.get("summaryMethod") != TRANSCRIPT_SUMMARY_METHOD:
            raise ValueError(f"Summary {episode_id} has the wrong summary method.")
        if transcript_words_by_id is not None and transcript_words != int(
            transcript_words_by_id[episode_id]
        ):
            raise ValueError(f"Summary {episode_id} has the wrong transcriptWordCount.")
        normalized_summary = _normalized_title(summary)
        if normalized_summary in seen_text:
            raise ValueError(f"Summary {episode_id} duplicates another summary.")
        seen_text.add(normalized_summary)
        validated.append(
            {
                "episodeId": episode_id,
                "episodeNumber": episode_number,
                "episodeTitle": title,
                "summary": summary,
                "keyTopics": topics,
                "whyItMatters": matters,
                "summaryMethod": TRANSCRIPT_SUMMARY_METHOD,
                "transcriptWordCount": transcript_words,
                "summaryWordCount": summary_words,
            }
        )
    return sorted(validated, key=lambda row: row["episodeId"])


def analytical_file_hashes(public_dir: Path) -> dict[str, str]:
    """Hash every public analytical artifact that this work package must preserve."""

    mutable = {"episode_summaries.json"}
    return {
        path.name: sha256_file(path)
        for path in sorted(public_dir.glob("*.json"), key=lambda row: row.name)
        if path.name not in mutable
    }


__all__ = [
    "PUBLIC_SUMMARY_FIELDS",
    "SUPPORTED_TRANSCRIPT_EXTENSIONS",
    "TRANSCRIPT_SUMMARY_METHOD",
    "analytical_file_hashes",
    "build_old_new_comparison",
    "build_transcript_manifest",
    "clean_transcript",
    "is_single_why_sentence",
    "load_json",
    "run_corpus_summary_qa",
    "sha256_file",
    "summary_word_count",
    "validate_public_transcript_summaries",
    "why_sentence_count",
    "word_count",
    "write_json",
]
