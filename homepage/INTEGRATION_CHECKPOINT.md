# Homepage integration checkpoint

- Branch: `feature/psywerx-homepage-preview`
- Base: `origin/main` at `59cf40931b9d63811422dd2c9e648888178f9e09`
- Generated preview: `homepage-preview/`
- Source and editorial inputs: `homepage/`
- Existing root redirect, `CNAME`, explorer applications, data, migrations, and reanalysis work remain outside this change.
- Feed selections remain drafts. Preview mode displays them with preview labeling; release mode excludes them.
- LinkedIn was verified from the current public PSYWERX LinkedIn company page. The public site's embedded MailerLite form did not expose a verified standalone newsletter destination, so newsletter remains unconnected.

Validation completed on 2026-09-07:

- 24/24 homepage unit and repository-integration checks passed.
- 106/106 homepage browser checks passed through local HTTP at 1440, 1280, 1024, 768, 500, 390, and 320 px, including preview/release editorial behavior.
- 19/19 existing Cognitive Security browser checks passed across 55 public routes.
- 21/21 scenario-service tests passed.
- Newly inherited `origin/main` suites passed: SOC-F07 pilot 36/36, SOC-F07 governance 19/19, Network State 43/43.
- The documented full Cognitive Security static suite has one pre-existing presentation-overlay manifest byte-count mismatch; the homepage changes do not touch that package.
- Both live explorer destinations returned HTTP 200. All six unchanged supplied web assets match their package SHA-256 hashes.
- Generated staging output contains eight files totaling 235,490 bytes.

Resume by running:

```powershell
py homepage/tools/build_homepage.py --mode preview --tool-links preview
py -m unittest tests.test_homepage_preview -v
py homepage/tools/browser_qa.py
```
