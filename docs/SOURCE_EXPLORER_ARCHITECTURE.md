# Source Explorer architecture

`data/sources.json` is the governed bibliographic registry. The Explorer does
not create a second source authority. At load time, `drivers/source-index.js`
projects registry records that are explicitly referenced by canonical
`Entity.keySources` into a normalized, read-only view with stable governed
`sourceId`, original `citation`, conservatively parsed metadata, external
identifiers/links, and nullable annotation fields.

Source identity is not rewritten in the client. The governed Source ID is the
stable identity, and repeated Entity references are deduplicated by that ID.
DOI, canonical URL, bibliographic identity, and normalized citation keys are
computed in that order for audit purposes. Colliding identifiers are reported
as suspected duplicates but are not automatically merged because conflicting
legacy citations/locators can make identity uncertain.

Relationships have one direction of authority:

`Source -> Driver -> Family -> Layer`

- `driverIds` come only from explicit canonical Driver `keySources` references.
- `familyIds` are derived from those Drivers' governed `primaryFamilyId` values.
- `layerIds` are derived from those Families' governed Layer placement.
- Layer and Family are never stored as independent source classifications.
- Citation does not assert that a source establishes a Driver as causal in
  every population, context, or relationship.

RDS remains a separate entity type. Its explicit citations are retained as
`rdsIds`, but RDS does not enter `driverIds` and does not contribute to the
Layer, Family, or Driver source facets.

Future annotated-bibliography content belongs on the normalized source record.
The projection already reserves nullable fields for summary, evidence notes,
study type, methodology, population/context, findings, limitations, evidence
quality, and relevant mechanisms. Populate those fields only from governed
source data; do not infer or generate them in the Explorer.

Run the source contract and browser acceptance checks with:

```powershell
node --test tests/source_index.test.js
py -m unittest tests.test_drivers_sources -v
py drivers/tools/browser_qa.py --chromium "C:\Program Files\Google\Chrome\Application\chrome.exe"
```
