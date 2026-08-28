# PSYWERX Relationship Schema v2.0

Relationship Schema v2.0 is the canonical technical contract for governed,
directed PSYWERX Driver-to-Driver causal assertions. The eight private
`Relationships` worksheets are authoritative; `data/relationships.json` is a
deterministic public build artifact.

The public envelope is:

```json
{
  "schemaVersion": "2.0",
  "relationships": []
}
```

## Canonical fields

| JSON field | Spreadsheet header | Type | Requirement |
|---|---|---|---|
| id | Relationship ID | string | Required, permanent, globally unique |
| sourceDriverId | Source Driver ID | string | Required exact Driver ID |
| sourceDriverName | Source Driver | string | Required; must match the source ID |
| targetDriverId | Target Driver ID | string | Required exact Driver ID |
| targetDriverName | Target Driver | string | Required; must match the target ID |
| causalRole | Causal Role | enum | Required |
| polarity | Polarity | enum | Required |
| directness | Directness | enum | Required |
| mechanism | Mechanism | string | Required |
| conditionsModerators | Conditions / Moderators | string | Required |
| moderatorDriverIds | Moderator Driver IDs | string array | Optional; exact Driver IDs |
| sourceLevel | Source Level | enum | Required |
| targetLevel | Target Level | enum | Required |
| levelTransitionMechanism | Level-Transition Mechanism | string/null | Required when levels differ |
| lagProfile | Lag Profile | enum array | Required; semicolon-separated in XLSX |
| lagLowerBound | Lag Lower Bound | number/null | Optional |
| lagUpperBound | Lag Upper Bound | number/null | Optional |
| lagUnit | Lag Unit | enum/null | Required when either numeric bound is used |
| lagNarrative | Lag Narrative | string | Required source-preserving description |
| exposurePattern | Exposure Pattern | enum | Required |
| effectPersistence | Effect Persistence | string/null | Optional |
| evidenceStrength | Evidence Strength | enum | Required |
| confidence | Confidence | enum | Required |
| generalizabilityContext | Generalizability / Context | string | Required |
| reciprocalProcessId | Reciprocal Process ID | string/null | Optional linkage between directed feedback edges |
| governanceClass | Governance Class | enum | Required |
| supportingEvidenceIds | Supporting Evidence IDs | string array | Required; exact Evidence IDs |
| notesCaveats | Notes / Caveats | string/null | Optional |
| source | Generated provenance | object | Required; workbook filename, worksheet, and row only |

Every public record has the same keys. Absent optional scalars are `null` and
absent optional lists are `[]`. Numeric lag bounds are valid only as a complete
lower-bound, upper-bound, and unit set. Driver state-change speed and
relationship onset lag remain distinct concepts.

## Controlled values

- `causalRole`: `CAUSES`, `ENABLES`, `CONSTRAINS`, `MODERATES`
- `polarity`: `POSITIVE`, `NEGATIVE`, `NON_MONOTONIC`, `CONTEXT_DEPENDENT`, `UNSIGNED`
- `directness`: `DIRECT_AT_STATED_RESOLUTION`, `MEDIATED_PATH`, `UNKNOWN`
- `lagProfile`: `IMMEDIATE`, `SHORT`, `INTERMEDIATE`, `DELAYED`, `LONG`, `STRUCTURAL`, `INTERGENERATIONAL`, `MIXED_CONTEXT_DEPENDENT`
- `exposurePattern`: `PULSE`, `SUSTAINED`, `CUMULATIVE`, `REPEATED`, `NOT_SPECIFIED`
- `confidence`: `HIGH`, `MODERATE`, `LOW`
- `governanceClass`: `CORE`, `CONTEXT_DEPENDENT`, `SCENARIO_SPECIFIC`, `HYPOTHESIZED`

Endpoint levels use: `PERSON`, `DYAD_INTERPERSONAL`, `SMALL_GROUP`, `NETWORK`,
`COMMUNITY`, `ORGANIZATION`, `INSTITUTIONAL_FIELD`, `SOCIETY`,
`STATE_JURISDICTION`, `INFORMATION_OBJECT_CORPUS`, `INFORMATION_SYSTEM`,
`TECHNOLOGICAL_SYSTEM`, `PHYSICAL_SETTING`, or `ECOLOGICAL_SYSTEM`.

## Governance and causal scope

`CORE` edges are broadly reusable, high-confidence backbone assertions.
`CONTEXT_DEPENDENT` edges are canonical only with explicit mechanism,
conditions, generalizability, evidence, and confidence. These are the only two
classes permitted in the public canonical graph.

`SCENARIO_SPECIFIC` edges belong in bounded model packages and
`HYPOTHESIZED` edges belong in governed research queues. Both use the same
technical vocabulary but are excluded from `data/relationships.json`; neither
may be silently promoted into the universal graph.

Directness is resolution-dependent. A mediated candidate is represented by
its governed source-to-mediator and mediator-to-target segments, with the
overly direct shortcut omitted. Reciprocal processes are two separately
directed records joined by a stable reciprocal-process ID and appropriate time
semantics.

## Validation and safety

The importer requires eight exact 28-column worksheets. Relationship IDs and
directed endpoint pairs must be unique; self-edges and dangling Driver or
Evidence references are errors. Source and target names must exactly match
their IDs, and each relationship must reside in its source Driver's Layer
workbook. Cross-level edges require an explicit transition mechanism.

The complete graph is validated in memory before the public JSON is atomically
replaced. Output is UTF-8, deterministic, and includes no private paths or
analysis-only governance artifacts. Relationship Schema v1.0 remains
documented separately as the historical migration source contract.
