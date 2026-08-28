# PSYWERX Interactives

Public-facing interactive tools, visualizations, and web applications for
PSYWERX. The repository is designed for static hosting with GitHub Pages.

## Interactives

- [Driver Explorer](./drivers/) — browses the governed Layer → Family → Driver
  taxonomy using dependency-free static assets. Canonical Driver names remain
  the public names, with reviewed explanations as supporting context.
- [Driver Codebook](./drivers/codebook/) — documents governed taxonomy fields
  and controlled vocabularies.

## Repository structure

- `data/` contains shared static data files.
- `drivers/` contains the Driver Explorer application.
- `shared/` contains styles and other assets reusable across interactives.
- `source-data/` is the ignored local location for private XLSX taxonomy files.
- `scripts/` contains local data-import utilities.
- `scenario-service/` contains the optional secure server-side Scenario
  operationalization service. It is not required by GitHub Pages.
- `docs/DRIVER_SCHEMA_V1_1.md` defines the current canonical
  spreadsheet-to-JSON contract enforced by the importer.
- `docs/DRIVER_SCHEMA_V1.md` preserves the historical Schema v1.0 contract.
- `docs/FAMILY_SCHEMA_V1.md` defines the canonical Family Schema v1.0 and its
  Driver-to-Family validation rules.
- `docs/CODEBOOK_SCHEMA_V1.md` defines the canonical Codebook Schema v1.0,
  permanent Codebook Term IDs, and controlled-vocabulary validation rules.
- `docs/RELATIONSHIP_SCHEMA_V2.md` defines the current canonical causal-edge
  contract and governance classes. `docs/RELATIONSHIP_SCHEMA_V1.md` preserves
  the historical migration source contract.
- `docs/PLAIN_LANGUAGE_STANDARD_V1.md` defines the governed writing and review
  standard for public Driver explanations.
- `docs/PLAIN_LANGUAGE_SCHEMA_V1.md` defines the independently versioned public
  plain-language data contract.
- `docs/PUBLIC_TAXONOMY_EXPLORER_V1.md` defines the public information
  architecture and causal-feature-off boundary.
- `docs/SOURCE_SCHEMA_V1.md` defines the governed public source registry.
- `docs/SCENARIO_OPERATIONALIZATION_SCHEMA_V1.md` and
  `docs/SCENARIO_SERVICE_SETUP.md` define the optional Scenario service contract
  and deployment boundary.

## Build driver data locally

The public `data/drivers.json` file is generated locally; the website itself has
no Python or runtime dependencies.

1. Put one or more `.xlsx` taxonomy files in `source-data/`. Files in this
   directory are ignored by Git, except for the placeholder `.gitkeep` file.
2. Create and activate a virtual environment, then install the importer dependency:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
   ```

3. Run the importer from the repository root:

   ```powershell
   py scripts\build_drivers.py
   ```

   The importer validates each workbook against the canonical
   [PSYWERX Driver Schema v1.1](./docs/DRIVER_SCHEMA_V1_1.md), combines all valid
   layers, and intentionally skips non-driver worksheets. It can infer a
   canonical layer from the workbook filename or worksheet/title information
   when no layer column is present. The existing public JSON is replaced only
   after a successful, validated import.

   Schema v1.1 workbooks include the optional `Time Scale Qualifier` column
   and enforce the canonical Time Scale of Change and Onset / Causal Lag
   vocabularies. For a controlled migration of standardized Schema v1.0
   workbooks, run this once before the importer:

   ```powershell
   py scripts\migrate_driver_schema_v1_1.py
   ```

   The migration stages and validates all eight workbooks before replacing any
   source file. It preserves Driver IDs and unrelated taxonomy content.

## Build approved plain-language data locally

The public `data/plain_language.json` file is an independently versioned
editorial layer keyed to permanent Driver IDs. It does not add fields to the
canonical Driver Schema or modify `data/drivers.json`.

Content version 1.1 combines the governed base editorial source and the private
31-Driver ontology-release supplement:

`analysis/plain_language_release_candidate_v2/plain_language_release_candidate_v2.csv`

`analysis/causal_explorer_release_v1/new_driver_plain_language_review.csv`

The `analysis/` directory is ignored and must remain private unless publication
is explicitly approved. Build canonical Driver data first, then export only the
approved fields:

```powershell
py scripts\build_drivers.py
py scripts\build_plain_language.py
```

The exporter enforces
[Plain-Language Data Schema v1.0](./docs/PLAIN_LANGUAGE_SCHEMA_V1.md), verifies
the 793 combined governed editorial-source IDs and stable identity snapshots,
and writes 768 approved public records. The exporter withholds the 22 ontology-blocked and three
subject-matter-review records, including provisional wording, and never
publishes editorial QA or human-review metadata. Failed validation does not
replace good public data.

## Build Family data locally

The public `data/families.json` file is generated from the `Families`
worksheet in each source workbook. Build `drivers.json` first because Family
validation uses it as the authoritative Driver dataset.

```powershell
py scripts\build_drivers.py
py scripts\build_families.py
```

The Family importer enforces [Family Schema v1.0](./docs/FAMILY_SCHEMA_V1.md),
globally unique permanent Family IDs and names, exact Driver-to-Family
coverage, source Driver Count assertions, and representative Driver linkage.
It preserves representative Driver names and derives their stable Driver IDs.
The generated JSON is deterministic and is replaced only after complete
validation succeeds.

For standardized workbooks whose Codebooks do not yet contain the canonical
Family ID and Driver Count governance rows, run this once before importing:

```powershell
py scripts\migrate_family_governance_v1.py
```

## Build Codebook data locally

Each source workbook contains an identical `Codebook` worksheet. The worksheet
has 59 populated rows: three structural rows (title, governance instruction,
and headers) and 56 semantic term records. Only the 56 semantic records receive
permanent, URL-safe Codebook Term IDs and become public entries.

For the current standardized workbooks, run the one-time ID migration before
the first Codebook import:

```powershell
py scripts\migrate_codebook_ids_v1.py
```

The migration verifies that all eight source Codebooks are identical, stages
all workbook changes, preserves unrelated worksheets, validates the original 48 IDs,
and replaces the source workbooks only after successful validation.

When initializing older standardized workbooks, apply the one-time migrations
in this order so the permanent Codebook ID column is added last:

```powershell
py scripts\migrate_driver_schema_v1_1.py
py scripts\migrate_family_governance_v1.py
py scripts\migrate_codebook_ids_v1.py
```

Generate the canonical public `data/codebook.json` file with:

```powershell
py scripts\build_codebook.py
```

The importer enforces [Codebook Schema v1.0](./docs/CODEBOOK_SCHEMA_V1.md),
selects one canonical copy only after confirming equality across all eight
workbooks, and validates source-controlled Driver vocabularies against
`data/drivers.json`. Allowed-but-unused values remain valid. Used-but-undefined
values stop the import, and failed validation never replaces good public data.

## Build Relationship data locally

The public `data/relationships.json` file is generated from the 28-column
Relationship Schema v2 worksheet in each source workbook. Build Drivers and
the Codebook first because Relationship validation uses canonical Driver IDs,
names, Evidence IDs, and controlled causal/governance vocabularies.

```powershell
py scripts\build_drivers.py
py scripts\build_codebook.py
py scripts\build_relationships.py
```

The importer enforces
[Relationship Schema v2.0](./docs/RELATIONSHIP_SCHEMA_V2.md), exact Driver
ID/name resolution, globally unique Relationship IDs and directed Driver
pairs, no self-relationships, deterministic output, and public-only source
provenance. Cross-level edges require a transition mechanism. Only `CORE` and
well-specified `CONTEXT_DEPENDENT` edges enter the canonical public graph;
`SCENARIO_SPECIFIC` and `HYPOTHESIZED` edges remain governed research/model
artifacts.

The structured `Relationships` worksheets are authoritative for
evidence-bearing graph edges. Narrative Driver fields such as likely upstream
or downstream influences and interaction candidates remain descriptive
metadata and are not converted into edges. The current graph is intentionally
conservative and non-exhaustive, so a missing edge does not establish that no
influence exists.

After the one-time workbook migrations have been applied, the exact full
public-data rebuild order is:

```powershell
py scripts\build_drivers.py
py scripts\build_plain_language.py
py scripts\build_families.py
py scripts\build_codebook.py
py scripts\build_relationships.py
py scripts\build_sources.py
```

The governed ontology-remediation release v1 was applied once with:

```powershell
py scripts\migrate_ontology_remediation_v1.py
```

That migration depends on the private, ignored remediation release-candidate
package. It creates a complete proposed diff, ID manifest, rollback copies, and
staged validation before replacing any canonical workbook; it is not part of a
routine public-data rebuild. The normal repeatable workflow is the six-builder
sequence above.

## Build governed source links locally

The public `data/sources.json` registry is generated from the Evidence Library
worksheets and resolves every Driver `keySources` identifier to governed
citation text and a safe link. Direct links use only explicit DOI, URL, or
supported scholarly identifiers from source data. A citation without a direct
link receives a clearly labeled scholarly-search fallback; the builder never
invents a DOI or bibliographic URL.

Build canonical Driver and Relationship data first, then run:

```powershell
py scripts\build_sources.py
```

The builder validates all public Driver and Relationship evidence references,
reports duplicate URLs without merging permanent Source IDs, produces
deterministic UTF-8 JSON, and replaces the existing registry only after a
successful full validation.

## Preview the static site

Opening the HTML file directly will not allow the browser to fetch JSON. Start
a local HTTP server from the repository root. The Explorer loads Driver,
Family, approved explanation, Codebook, and Source JSON using GitHub
Pages-compatible relative paths. It does not fetch Relationship data during
normal public startup; relationship infrastructure remains preserved for a
future graph-complete release.

```powershell
py -m http.server 8000
```

Then open <http://localhost:8000/drivers/>.

The static taxonomy works without Scenario AI. On localhost,
`drivers/config.js` points to the optional service at
`http://localhost:8787/v1/operationalize`; follow
[`docs/SCENARIO_SERVICE_SETUP.md`](./docs/SCENARIO_SERVICE_SETUP.md) to run it.
Production Scenario AI stays disabled until a secure endpoint is deployed and
configured. No API secret belongs in browser code.

## Commit generated data

Review and commit only the generated public artifacts and pipeline changes:

```powershell
git add data/ drivers/ shared/ scripts/ docs/ scenario-service/ README.md .gitignore requirements.txt
git commit -m "Publish PSYWERX taxonomy Explorer release"
```
