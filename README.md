# PSYWERX Interactives

Public-facing interactive tools, visualizations, and web applications for
PSYWERX. The repository is designed for static hosting with GitHub Pages.

## Interactives

- [Driver Explorer](./drivers/) — an early placeholder that renders a small
  sample of behavioral drivers.

## Repository structure

- `data/` contains shared static data files.
- `drivers/` contains the Driver Explorer application.
- `shared/` contains styles and other assets reusable across interactives.
- `source-data/` is the ignored local location for private XLSX taxonomy files.
- `scripts/` contains local data-import utilities.
- `docs/DRIVER_SCHEMA_V1_1.md` defines the current canonical
  spreadsheet-to-JSON contract enforced by the importer.
- `docs/DRIVER_SCHEMA_V1.md` preserves the historical Schema v1.0 contract.
- `docs/FAMILY_SCHEMA_V1.md` defines the canonical Family Schema v1.0 and its
  Driver-to-Family validation rules.
- `docs/CODEBOOK_SCHEMA_V1.md` defines the canonical Codebook Schema v1.0,
  permanent Codebook Term IDs, and controlled-vocabulary validation rules.
- `docs/RELATIONSHIP_SCHEMA_V1.md` defines the canonical Relationship Schema
  v1.0, Driver-reference rules, and graph validation requirements.

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
has 51 populated rows: three structural rows (title, governance instruction,
and headers) and 48 semantic term records. Only the 48 semantic records receive
permanent, URL-safe Codebook Term IDs and become public entries.

For the current standardized workbooks, run the one-time ID migration before
the first Codebook import:

```powershell
py scripts\migrate_codebook_ids_v1.py
```

The migration verifies that all eight source Codebooks are identical, stages
all workbook changes, preserves unrelated worksheets, validates all 48 IDs,
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

The public `data/relationships.json` file is generated from the 13-column
`Relationships` worksheet in each source workbook. Build Drivers and the
Codebook first because Relationship validation uses canonical Driver IDs and
names plus the Codebook-controlled `Expected Direction` and relationship
`Evidence Strength` vocabularies.

```powershell
py scripts\build_drivers.py
py scripts\build_codebook.py
py scripts\build_relationships.py
```

The importer enforces
[Relationship Schema v1.0](./docs/RELATIONSHIP_SCHEMA_V1.md), exact Driver
ID/name resolution, globally unique Relationship IDs and directed Driver
pairs, no self-relationships, deterministic output, and public-only source
provenance. Future explicit cross-layer edges are valid; the current source
set is within-layer.

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
py scripts\build_families.py
py scripts\build_codebook.py
py scripts\build_relationships.py
```

## Preview the static site

Opening the HTML file directly will not allow the browser to fetch JSON. Start
a local HTTP server from the repository root:

```powershell
py -m http.server 8000
```

Then open <http://localhost:8000/drivers/>.

## Commit generated data

Review and commit only the generated public artifacts and pipeline changes:

```powershell
git add data/drivers.json data/families.json data/codebook.json data/relationships.json scripts/build_drivers.py scripts/build_families.py scripts/build_codebook.py scripts/build_relationships.py scripts/migrate_driver_schema_v1_1.py scripts/migrate_family_governance_v1.py scripts/migrate_codebook_ids_v1.py docs/DRIVER_SCHEMA_V1_1.md docs/FAMILY_SCHEMA_V1.md docs/CODEBOOK_SCHEMA_V1.md docs/RELATIONSHIP_SCHEMA_V1.md requirements.txt README.md .gitignore source-data/.gitkeep
git commit -m "Build ontology data from local spreadsheets"
```
