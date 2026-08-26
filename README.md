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

4. Preview the static site with a local HTTP server (opening the HTML file
   directly will not allow the browser to fetch JSON):

   ```powershell
   py -m http.server 8000
   ```

   Then open <http://localhost:8000/drivers/>.

5. Review and commit only the generated public artifact and pipeline changes:

   ```powershell
   git add data/drivers.json scripts/build_drivers.py scripts/migrate_driver_schema_v1_1.py docs/DRIVER_SCHEMA_V1_1.md requirements.txt README.md .gitignore source-data/.gitkeep
   git commit -m "Build driver data from local spreadsheets"
   ```
