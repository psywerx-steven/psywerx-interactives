# PSYWERX Source Registry Schema v1.0

Source Registry Schema v1.0 defines the compact public citation registry built
from the `Evidence Library` worksheets in the eight canonical PSYWERX Driver
Ontology workbooks. It gives public applications a stable way to resolve the
Evidence IDs already cited by Drivers and Relationships without publishing the
workbooks' private analytical notes.

The public artifact uses this envelope:

```json
{
  "schemaVersion": "1.0",
  "sources": []
}
```

## Canonical fields

| Canonical field | Source | JSON type | Requirement | Technical meaning and normalization |
|---|---|---|---|---|
| `id` | `Evidence ID` | string | Required | Permanent PSYWERX source identity. Preserve the explicit workbook value exactly. Both governed forms, `SRC001`–`SRC404` and `SRC-405` onward, are valid; punctuation must not be rewritten. |
| `citationText` | `Citation / Title` | string | Required | Source-authored citation or title. Trim surrounding whitespace only; preserve internal wording and UTF-8 characters. |
| `year` | `Year` | integer or `null` | Optional | Four-digit publication or source year. Convert numeric cells and four-digit text cells to an integer; use `null` when the source cell is empty. |
| `evidenceType` | `Evidence Type` | string | Required | Source-authored evidence classification. Preserve after trimming surrounding whitespace. This field is not treated as a controlled vocabulary in v1.0. |
| `evidenceStrength` | `Evidence Strength` | string | Required | Strength assigned to the Evidence record. Require exact membership in Codebook term `CB-EVI-EVIDENCE-STRENGTH`. |
| `sourceUrl` | `Source URL` | string or `null` | Optional | Explicit URL present in the workbook. Preserve it exactly after trimming. Never synthesize a value for this field. |
| `resolutionType` | Generated | string | Required | How the public link was established: `DOI`, `URL`, `IDENTIFIER`, `SEARCH`, or `UNRESOLVED`. |
| `resolvedIdentifier` | Generated from explicit source text | string or `null` | Optional | Explicit DOI or supported scholarly identifier used for resolution. It is never inferred from a title. |
| `href` | Generated | string or `null` | Optional | Public HTTPS destination. A `SEARCH` value is a labelled scholarly-search query, not an asserted source URL. Use `null` only for `UNRESOLVED`. |
| `linkLabel` | Generated | string or `null` | Optional | Interface label appropriate to the resolution type, such as `Open DOI`, `Open source`, or `Search Google Scholar`. |
| `driverIds` | Derived from `data/drivers.json` | array of strings | Required | Canonical Drivers that cite this Evidence ID in `keySources`. Sort in canonical Driver dataset order; use `[]` when no Driver cites it. |
| `relationshipIds` | Derived from `data/relationships.json` | array of strings | Required | Canonical Relationships that cite this Evidence ID in `supportingEvidenceIds`. Sort deterministically; use `[]` when unused. |
| `source` | Generated provenance | object | Required | Workbook basename, worksheet name, and one-based row number. Never include an absolute or local directory path. |

In the governed v0.3 preview, `driverIds` remains a legacy field name for
backward compatibility. Its permanent IDs resolve against `data/entities.json`
and may therefore identify a Driver or a retyped RDS. No source linkage is
renamed or discarded during retyping.

Every record contains every canonical key. The registry intentionally omits
workbook-only analytical fields such as population, findings, effect direction,
limitations, and verification notes. Those fields remain governed source data;
their omission is a public-release boundary, not data loss in the ontology.

## Exact worksheet contract

Each of the eight workbooks must contain one worksheet named `Evidence Library`.
Row 4 must contain these 13 headers, in this exact order, and semantic records
begin in row 5:

1. Evidence ID
2. Linked Driver IDs
3. Family / Domain
4. Citation / Title
5. Year
6. Evidence Type
7. Population
8. Finding
9. Direction / Effect
10. Limitations
11. Evidence Strength
12. Source URL
13. Verification Note

The builder validates the full table contract even though only the approved
public subset is emitted. `Linked Driver IDs` is validated against canonical
Driver IDs and retained in the workbook as source-authored context. Public
`driverIds` is derived from the actual `keySources` references consumed by the
Driver Explorer; differing sets produce a diagnostic rather than an automatic
rewrite or merge.

## Permanent identity

Evidence IDs are explicit governed identifiers. Schema v1.0 recognizes both
historical forms already present in the ontology:

- `SRC001` through `SRC404`
- `SRC-405` and later IDs using the hyphenated form

The difference is not a migration opportunity. A builder must preserve exact
identity, reject duplicate IDs, and never generate a replacement from row
position, citation text, DOI, or URL. Duplicate URLs are warnings and must not
cause Evidence records to be merged: one publication can support separately
scoped Evidence records.

## Governed link resolution

Link resolution uses only explicit source material and follows this precedence:

1. **DOI** — a DOI explicitly labelled with `doi:` in citation metadata or
   carried by an explicit `doi.org` Source URL. Use the explicit DOI resolver
   URL when present; otherwise construct only the standard `https://doi.org/`
   resolver from that explicit DOI. DOI-shaped text embedded in another
   publisher URL is not reinterpreted; the explicit publisher URL remains a
   `URL` resolution.
2. **URL** — the explicit HTTP(S) `Source URL`, without DOI interpretation.
3. **IDENTIFIER** — a supported, explicitly labelled scholarly identifier in
   citation metadata. Schema v1.0 supports PMID, PMCID, and arXiv identifiers
   using their standard public resolvers.
4. **SEARCH** — a Google Scholar query built from the preserved citation text
   when no explicit resolvable information exists. This is always labelled as a
   search fallback and is never represented as the source's URL.
5. **UNRESOLVED** — no citation or safe public resolution is possible.

The builder never invents a DOI, guesses a publication URL from a title, or
uses a URL merely because it appears to describe a similar work. Live network
availability is outside deterministic build validation.

## Cross-dataset validation

Before replacing the public JSON, the builder validates in memory that:

- exactly eight canonical layer workbooks and eight Evidence Library worksheets
  are present;
- all worksheet headers match the v1.0 contract;
- every permanent Evidence ID is valid and globally unique;
- every source-authored Linked Driver ID exists;
- every Driver `keySources` and Relationship `supportingEvidenceIds` reference
  resolves to one registry record;
- Evidence Strength values match the governed Codebook vocabulary;
- all generated links are valid HTTP(S) URLs;
- every record has the exact canonical key structure; and
- no local Windows path or private repository path is exposed.

The complete payload is sorted by the numeric portion of its permanent ID,
serialized as UTF-8 with two-space indentation and a final newline, then written
with an atomic replacement. Any validation error leaves an existing
`data/sources.json` untouched.

Run the builder from the repository root:

```powershell
py scripts\build_sources.py
```

The optional `--source-dir` argument exists for validating an authorized copy
of the canonical workbook set; the default remains the private local
`source-data/` directory.
