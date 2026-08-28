# PSYWERX Plain-Language Data Schema v1.0

This schema defines the independently versioned public plain-language content
layer for PSYWERX Drivers. It implements the writing requirements in the
[PSYWERX Plain-Language Standard v1.0](./PLAIN_LANGUAGE_STANDARD_V1.md) without
changing the canonical Driver Schema or the scientific ontology.

The public artifact is `data/plain_language.json`. Content is joined to a
canonical Driver by permanent `driverId`; it never replaces the canonical name,
definition, Layer, Family, or technical fields in `data/drivers.json`.

## Envelope

| Key | Type | Requirement | Meaning |
| --- | --- | --- | --- |
| `schemaVersion` | string | Required | Public data-contract version. Schema v1.0 uses `1.0`. |
| `contentVersion` | string | Required | Independently governed wording release. The approved initial release uses `1.0`. |
| `standardVersion` | string | Required | Plain-Language Standard used for the content. The initial release uses `1.0`. |
| `drivers` | array | Required | Publication-approved plain-language Driver records. |

## Driver record

Every published record has exactly the following keys.

| Field | JSON type | Requirement | Meaning and normalization |
| --- | --- | --- | --- |
| `driverId` | string | Required | Permanent canonical Driver ID. Preserve exactly and resolve to one record in `data/drivers.json`. |
| `plainLanguageLabel` | string | Required | Approved public label. Preserve the approved UTF-8 wording exactly. |
| `plainLanguageExplanation` | string | Required | Approved public explanation. Preserve the approved UTF-8 wording exactly. |
| `analyticQuestion` | string | Required | Approved question that helps a practitioner investigate the Driver state. Preserve exactly. |
| `whatThisDoesNotMean` | string or null | Optional | Approved boundary clarification. An intentionally absent statement is `null`, not an empty string. |

## Publication eligibility

The governed private release source is
`analysis/plain_language_release_candidate_v2/plain_language_release_candidate_v2.csv`.
The initial public release contains the 737 records with an `APPROVED` human
decision and one of these release-source dispositions:

- `CALIBRATED_APPROVED`
- `EDITORIAL_RELEASE_CANDIDATE`
- `EDITORIAL_REVISED_CANDIDATE`

The 22 `BLOCKED_ON_ONTOLOGY_REVIEW` records and three
`SUBJECT_MATTER_REVIEW_REQUIRED` records are excluded. In particular, provisional
SME-review wording is not public. Their absence from this editorial dataset does
not remove the corresponding canonical Drivers from `data/drivers.json`; the
Explorer displays a neutral under-review notice and retains the canonical record.

Private governance fields—including risk, QA findings, release-source status,
human decision, notes, and review priority—must not appear in the public JSON.
Inclusion in this release is the public approval signal.

## Build and validation behavior

Run `py scripts\build_plain_language.py` from the repository root. The exporter:

- reads the complete approved release into memory;
- requires all 762 source rows and unique permanent Driver IDs;
- compares the canonical name, definition, Layer, and Family snapshots exactly
  with `data/drivers.json`;
- requires exactly 737 approved records and withholds exactly 22 ontology-blocked
  and three SME-review records;
- requires the three permanent fields for every published record;
- converts only an empty optional boundary statement to `null`;
- emits records in canonical `data/drivers.json` order;
- preserves UTF-8 and writes deterministic, pretty-printed JSON with LF endings;
- rejects private/local paths and non-schema fields; and
- builds and validates completely before atomically replacing the public file.

The private CSV remains the governed editorial source, just as ignored XLSX
workbooks remain the local source for the canonical taxonomy. The generated JSON
is the repository-controlled static artifact used by GitHub Pages.

## Versioning

Plain-language content versions independently from Driver Schema v1.1. Wording
changes do not change canonical ontology semantics. A future release must update
the content version and pass the same approval, exact-ID, canonical-invariant,
protection, and deterministic-output checks.
