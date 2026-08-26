# PSYWERX Driver Schema v1.1

Schema v1.1 is the current canonical public-driver schema for the standardized
PSYWERX Driver Ontology workbooks. It retains every Schema v1.0 field and adds
the optional `Time Scale Qualifier` field. Historical Schema v1.0 documentation
remains available in `DRIVER_SCHEMA_V1.md`.

Every generated record contains every canonical JSON key. An absent optional
scalar is `null`; an absent optional list is an empty array. Required values
must be present and non-empty. The importer reports missing optional columns as
warnings and missing required columns as errors.

| Canonical field | Spreadsheet header | JSON type | Requirement | Technical meaning | Normalization |
|---|---|---|---|---|---|
| id | ID | string | Required | Permanent unique driver identifier. | Preserve the explicit cell value exactly; never case-fold, slug, or regenerate it. |
| name | Name | string | Required | Canonical variable name. | Trim and collapse whitespace. |
| aliases | Other Names / Aliases | array of strings | Optional | Alternative and legacy terms. | Split on semicolons, pipes, or line breaks. |
| layer | Layer | string | Required | Primary layer assignment. | Normalize to one of the eight canonical layer values. Resolve from the explicit column, canonical filename, designated title cell, or layer-bearing worksheet name, in that order. Never infer from descriptive content. |
| family | Family | string | Required | Canonical primary family name. | Trim and collapse whitespace. |
| definition | Definition | string | Required | Concise statement of what varies. | Trim and collapse whitespace. |
| dataType | Data Type | string | Required | General variable type. | Trim and collapse whitespace; preserve workbook terminology. |
| representationScale | Representation / Scale | string | Required | Plausible encodings or scales. | Trim and collapse whitespace. |
| polarityDirection | Polarity / Direction of Interpretation | string | Required | Meaning of movement or categories. | Trim and collapse whitespace. |
| mechanism | Mechanism | string | Required | How a change may affect downstream variables. | Trim and collapse whitespace. |
| likelyUpstreamInfluences | Likely Upstream Influences | array of strings | Optional | Factors likely to change the driver. | Split on semicolons, pipes, or line breaks. |
| likelyDownstreamInfluences | Likely Downstream Influences | array of strings | Optional | Factors the driver may change. | Split on semicolons, pipes, or line breaks. |
| moderatorsBoundaryConditions | Moderators / Boundary Conditions | string | Required | Conditions changing effect strength, direction, threshold, or persistence. | Trim and collapse whitespace. |
| typicalInteractionCandidates | Typical Interaction Candidates | array of strings | Optional | Plausible interacting drivers; not established edges. | Split on semicolons, pipes, or line breaks. |
| modifiability | Modifiability / Malleability | string | Required | Practical changeability. | Trim and collapse whitespace; preserve controlled term. |
| volatility | Volatility | string | Required | Natural fluctuation without deliberate intervention. | Trim and collapse whitespace; preserve controlled term. |
| timeScaleOfChange | Time Scale of Change | array of strings | Required | Typical elapsed time over which the driver state meaningfully changes. | Split only on semicolons; validate canonical values, exclusivity, uniqueness, and shortest-to-longest order. |
| timeScaleQualifier | Time Scale Qualifier | string or null | Optional | Narrative qualification when canonical bands cannot fully preserve meaningful change-speed information. | Trim and collapse whitespace. Do not use for faceted filtering or as a replacement for Persistence / Recovery. |
| onsetCausalLag | Onset / Causal Lag | array of strings | Required | Delay from driver-state change to a downstream consequence. | Split only on semicolons; validate canonical values, exclusivity, uniqueness, and shortest-to-longest order. `Stable / Not applicable` is not permitted. |
| persistenceRecovery | Persistence / Recovery | string | Required | Duration or reversibility after the initiating condition changes. | Trim and collapse whitespace. |
| indicators | Indicators | array of strings | Optional | Observable signals of driver state. | Split on semicolons, pipes, or line breaks. |
| measurementAssessmentMethods | Measurement / Assessment Methods | string | Required | Ways to estimate or infer the driver. | Trim and collapse whitespace. |
| observability | Observability | string | Required | General directness of observation. | Trim and collapse whitespace; preserve controlled term. |
| measurementCaveats | Measurement Caveats | string | Required | Known assessment limitations. | Trim and collapse whitespace. |
| evidenceStrength | Evidence Strength | string | Required | Overall maturity of support. | Trim and collapse whitespace; preserve controlled term. |
| evidenceNotes | Evidence Notes | string | Required | Supported claims, uncertainty, and transferability limits. | Trim and collapse whitespace. |
| commonMisinterpretations | Common Misinterpretations | string | Required | Common construct misuse. | Trim and collapse whitespace. |
| keySources | Key Sources | array of strings | Required | Representative Evidence IDs. | Split on semicolons, pipes, or line breaks. |
| source | Generated by importer | object | Required | Public provenance containing workbook filename and worksheet name. | Never include a local filesystem path. |

## Canonical layers

- Biological
- Psychological
- Social
- Cultural
- Physical / Environmental
- Institutional / Structural
- Informational
- Technological

## Canonical temporal vocabulary

The controlled Time Scale of Change vocabulary is:

1. `Seconds–Minutes`
2. `Minutes–Hours`
3. `Hours–Days`
4. `Days–Weeks`
5. `Weeks–Months`
6. `Months–Years`
7. `Years–Generations`
8. `Mixed / Context-dependent`
9. `Stable / Not applicable`

Onset / Causal Lag uses the same vocabulary except that
`Stable / Not applicable` is prohibited.

Canonical capitalization, spacing, and en-dash punctuation are required.
Semicolons delimit multiple values. Values must be unique and ordered shortest
to longest. A broad contiguous range must be represented by every canonical
band it spans. Multiple distinct, noncontiguous scales may also be listed when
they describe separate operating regimes rather than one continuous range.

`Mixed / Context-dependent` is exclusive and cannot be combined with another
value. `Stable / Not applicable` is also exclusive. It means meaningful change
speed is ordinarily not applicable because the modeled driver state is
effectively invariant over the relevant unit or time horizon.

## Temporal field distinctions

- **Time Scale of Change** describes how quickly the driver state itself moves.
- **Onset / Causal Lag** describes the delay between driver-state change and a
  downstream consequence.
- **Persistence / Recovery** describes how long the changed state persists and
  how it returns toward baseline.
- **Time Scale Qualifier** preserves narrative nuance that the controlled bands
  cannot express fully, such as acute episodes against a chronic baseline,
  developmental course, cause-dependent timing, stable status, or a more
  precise bound.

Chronic persistence does not automatically imply a long Time Scale of Change.
The qualifier is descriptive metadata and must not be used as a filtering
facet.

## Validation behavior

The importer requires one driver table per workbook, compares complete header
signatures across workbooks, validates every required value, and reports
optional omissions and unexpected columns. It rejects conflicting layer
evidence, duplicate IDs, invalid record types, non-canonical layers, invalid
temporal values, duplicate temporal values, out-of-order temporal values, and
violations of exclusive temporal categories.

All non-driver worksheets are intentionally skipped. The importer builds the
complete combined dataset in memory and atomically replaces
`data/drivers.json` only when validation finishes without errors.
