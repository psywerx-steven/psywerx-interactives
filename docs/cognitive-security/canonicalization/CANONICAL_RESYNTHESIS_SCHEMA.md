# Cognitive Security Canonical Re-synthesis Schema

**Status:** Draft public-safe schema and governance contract

**Scope:** Canonical analytical artifacts produced after the deduplicated
selection overlay. This is not the live public-data schema.

This document defines required record shapes, controlled vocabularies, and
cross-record invariants. Private builds may add lineage fields, but public-safe
records must follow the allowlist and privacy boundary below.

## General serialization rules

- JSON is UTF-8 and ends with one newline.
- Primary keys are stable strings and unique within each collection.
- Records are sorted by primary key.
- Set-like identifier arrays are unique and sorted.
- A missing scalar is `null`; a missing collection is `[]`.
- Generated timestamps, random values, and machine-specific paths are
  prohibited.
- Counts are nonnegative integers. Shares are numbers from 0 through 1.
- Every foreign key resolves to an entity in the same governed package.
- Every relationship uses a recognized semantic role.
- Public records contain no private lineage or review detail.

## Shared types

### `adjudicationStatus`

Allowed values:

- `candidate` — generated or proposed and awaiting analyst review;
- `analyst-reviewed-draft` — evidence has been examined, but the checkpoint
  still requires the designated human approval;
- `analyst-reviewed` — evidence has been examined and the proposal confirmed;
- `revised` — evidence review changed the proposal;
- `recomputed` — support was deterministically recalculated from the governed
  canonical selection; or
- `canonical` — governed and eligible for canonical publication.

### Confidence labels

Working-package proposal confidence uses `high` or `medium`. Final governed
family decisions use `high`, `moderate`, or `review`; theme, tension,
narrative, and scenario decisions use `high`, `medium`, or `review`.
Confidence describes the adjudication judgment, not the quality, importance,
or validity of the underlying evidence.

### `corpusSupportProfile`

```text
uniqueContentUnitSupportCount: integer
publicReleaseCoverageCount: integer
itemSupportCount: integer
clusterSupportCount: integer
familySupportCount: integer
categoryBreadth: integer
topOneContentUnitShare: number
topTwoContentUnitShare: number
topFiveContentUnitShare: number
effectiveContentUnitCount: number
inheritedPublicReleaseCoverageCount: integer
directSupportItemCount: integer
derivedSupportItemCount: integer
directSupportShare: number
historicalToCorrectedSensitivity: sensitivity
adjudicationStatus: adjudicationStatus
limitations: string[]
```

`effectiveContentUnitCount` is the inverse-Herfindahl effective count of
content-unit item shares. The concentration fields and effective count are
transparent distribution measures, not evidence-quality scores.

Suggested `sensitivity` shape:

```text
status: "stable" | "mild" | "moderate" | "high" | "unassessable"
historicalItemSupportCount: integer | null
correctedItemSupportCount: integer | null
absoluteChange: integer | null
percentChange: number | null
historicalSourceIdentityCoverageCount: integer | null
correctedContentUnitCoverageCount: integer | null
coverageAbsoluteChange: integer | null
coveragePercentChange: number | null
```

Unassessable fields are `null`, not zero.

## Selection overlay

Selection records are private because they join historical identities and
items to canonical analytical units. Public output exposes only aggregate
counts and the shared-content relationship where useful.

### `canonicalContentUnitSelection`

```text
canonicalContentUnitId: string
publicReleaseIds: string[]
selectedRepresentationId: string
analyticalStatus: "selected-canonical-content"
contributesAnalyticalWeight: true
selectionReason: "governed-canonical-content-representation"
```

For the one selected recording with two public releases, `analyticalStatus` is
`selected-with-shared-release-inheritance`; this does not change its unit
weight.

### `historicalIdentitySelection` — private only

```text
sourceIdentityId: string
canonicalContentUnitId: string | null
publicReleaseId: string | null
identityKind: string
historicalItemCount: integer
analyticalStatus: "canonical-content-representative" | "confirmed-alias-excluded" | "shared-content-reuse-excluded"
contributesAnalyticalWeight: boolean
```

### `historicalItemSelection` — private only

```text
itemId: string
sourceIdentityId: string
canonicalContentUnitId: string | null
analyticalStatus: "included-canonical-content" | "excluded-confirmed-alias" | "excluded-shared-content-reuse"
contributesAnalyticalWeight: boolean
selectionReason: string
```

### `publicReleaseContentMap` — private draft only

```text
publicReleaseId: string
canonicalContentUnitId: string
relationshipRole: "direct-content-representation" | "shared-content-inheritance"
contributesAnalyticalWeight: boolean
```

Invariants:

- there are 269 historical identities, 242 public releases, and 241 selected
  recording/content units;
- an included item has exactly one selected content unit and weight 1;
- excluded aliases and reused content have weight 0;
- one public release may inherit relationships from shared content, but an
  inherited relationship never creates a selected item; and
- the exact included-item count is computed from the overlay.

## Cluster support

The 127 cluster definitions remain governed inputs. Canonicalization adds a
support record rather than altering their substantive identities.

### `clusterSupport`

```text
clusterId: string
clusterName: string
focalCategoryMembership: { categoryId: string, categoryName: string }
canonicalPrimaryItemCount: integer
canonicalSecondaryItemCount: integer
governedWeightedCount: integer
uniqueContentUnitCoverage: integer
publicReleaseCoverage: integer
supportConcentration: {
  topOneContentUnitShare: number,
  topTwoContentUnitShare: number,
  topFiveContentUnitShare: number,
  effectiveContentUnitCount: number,
  dominatedByOneOrTwoContentUnits: boolean
}
historicalToCorrectedChange: {
  historicalPrimaryItemCount: integer,
  historicalSecondaryItemCount: integer,
  historicalWeightedCount: integer,
  weightedAbsoluteChange: integer,
  weightedPercentChange: number | null,
  historicalDistinctSourceIdentityCoverage: integer,
  correctedContentUnitCoverage: integer,
  coverageAbsoluteChange: integer,
  coveragePercentChange: number | null
}
sensitivityStatus: "stable" | "moderate-sensitivity" | "review-required" | "lost-all-support"
investigationTriggers: string[]
corpusSupportProfile: corpusSupportProfile
```

The governed weighted count is calculated from the declared primary/secondary
weighting rule. It is not a measure of real-world importance.

## Canonical families

### `canonicalFamily`

```text
familyId: string
name: string
category: string
definition: string
inclusionRules: string[]
exclusionRules: string[]
distinguishingBoundaries: string
memberClusterIds: string[]
secondaryRelatedClusterIds: string[]
corpusSupportProfile: corpusSupportProfile
mappingConfidence: {
  highClusterAssignments: integer,
  moderateClusterAssignments: integer,
  reviewClusterAssignments: integer,
  proposedMediumAssignmentsEvidenceReviewed: integer,
  minimum: "high" | "moderate" | "review"
}
adjudicationStatus: adjudicationStatus
limitations: string[]
```

Invariants:

- every cluster has exactly one `primary-family-membership` relationship;
- every family has at least one member cluster;
- a family contains clusters from exactly one focal category;
- secondary relationships require an evidence-reviewed decision; and
- member and secondary lists cannot contain the same cluster-family pair.

Family-level confidence must be traceable to member-mapping decisions. It
must not be calculated as an undocumented numeric average.

## Canonical themes

### `canonicalTheme`

```text
themeId: string
name: string
definition: string
boundaryConditions: string
internalAnalyticalRole: string | null
publicLevel: "theme"
primaryFamilyIds: string[]
secondaryFamilyIds: string[]
primaryClusterIds: string[]
secondaryClusterIds: string[]
familyRelationships: familyRelationship[]
categoryBreadth: integer
corpusSupportProfile: corpusSupportProfile
strategicSignificance: string
operationalImplications: string
limitations: string[]
adjudicationStatus: adjudicationStatus
adjudicationConfidence: "high" | "medium" | "review"
```

`familyRelationship` identifies `familyId`, `semanticRole`, and whether its
analytical weight is primary or secondary. Key Concept relationships use
`conceptual-framing`; Future Trend relationships use `future-extension`.

All themes occupy one public level. Any internal analytical-role field is
private metadata and cannot create a visible hierarchy.

Primary and secondary lists are mutually exclusive at each entity level.
`categoryBreadth` must equal the distinct focal categories represented by
traceable governed primary support, not conceptual framing alone.

## Canonical tensions

### `canonicalTension`

```text
tensionId: string
name: string
tensionType: string
definition: string
poleALabel: string
poleAAssumption: string
poleBLabel: string
poleBAssumption: string
conditionsFavoringA: string[]
conditionsFavoringB: string[]
falseDichotomyCaveat: string
supportingFamilyIds: string[]
supportingClusterIds: string[]
supportingCanonicalContentUnits: string[]
corpusSupportProfile: corpusSupportProfile
evidenceBalanceAcrossPoles: poleBalance
neighborDistinctions: object
limitations: string[]
adjudicationStatus: adjudicationStatus
adjudicationConfidence: "high" | "medium" | "review"
adjudicationDecision: "retain" | "merge" | "split" | "reject"
adjudicationRationale: string
evidenceAssessment: string
reviewRequired: boolean
reviewFlags: string[]
```

Private records additionally retain `sourceCandidateIds`,
`historicalTensionIds` for historical tensions with surviving positive-weight
evidence, `proposedHistoricalTensionIds` for design-proposal ancestry, and
item-level allocation lineage.

### `poleBalance`

```text
poleAItemCount: integer
poleBItemCount: integer
sharedAcrossPolesItemCount: integer
poleAAnalyticalWeight: number
poleBAnalyticalWeight: number
totalAnalyticalWeight: number
poleAShare: number
poleBShare: number
bothPolesDirectlySupported: boolean
```

### `tensionEvidenceAllocation` — private only

```text
historicalTensionId: string
sourceCandidateId: string
historicalItemId: string
itemId: string  # retained canonical evidence item
canonicalContentUnitId: string
sourcePoleOccurrence: "A" | "B"
historicalPole: "A" | "B" | "both"
normalizedPole: "A" | "B"
canonicalTensionId: string
primaryClusterId: string
primaryFamilyId: string
semanticRole: "tension-evidence-pole-a" | "tension-evidence-pole-b"
orientationTreatment: string
lineageTreatment: "direct-retained-item" | "governed-canonical-counterpart-substitution"
allocationAuthority: "canonical-architecture-candidate-lineage" | "governed-split-item-adjudication"
included: boolean
analyticalSupportWeight: number  # all occurrences for one canonical item sum to 1
exclusionReason: string | null
allocationRationale: string
adjudicationStatus: adjudicationStatus
```

Private allocation records may additionally retain confidence, category-drift,
bridge, overlap, and internal review metadata from the governed adjudication
inputs. Those fields and all item identifiers are excluded from public output.

A retained canonical evidence item has total analytical weight at most one
across the complete canonical tension layer. Cross-tension collisions use one
governed winning occurrence and zero-weight losing lineage. Repeated lineage
inside one tension may share that unit budget, including a genuine dual-pole
bridge, without increasing the quantitative item count. Evidence inherited
from a broad historical candidate is allocated rather than copied wholesale.
Excluded alias items never contribute weight; only their reviewed retained
counterparts may do so.

## Canonical narratives

### `canonicalNarrative`

```text
narrativeId: string
name: string
shortVersion: string
coreClaim: string
integratesThemeIds: string[]
integratesTensionIds: string[]
supportingFamilyIds: string[]
supportingClusterIds: string[]
categoryBreadth: integer
unresolvedIssue: string
boundaryConditions: string
corpusSupportProfile: corpusSupportProfile
limitations: string[]
adjudicationStatus: adjudicationStatus
adjudicationConfidence: "high" | "medium" | "review"
adjudicationDecision: string
adjudicationRationale: string
historicalNarrativeIds: string[]  # private draft only
```

A narrative must integrate multiple themes, families, and categories, include
at least one tension and one unresolved issue, and resolve through canonical
relationships to lower-level evidence.

## Canonical category findings

### `canonicalCategoryFinding`

```text
findingId: string
categoryId: string
findingType: "family-finding" | "integrative-category-finding" | "open-question"
title: string
finding: string
supportingFamilyIds: string[]
supportingClusterIds: string[]
supportingContentUnitCount: integer
corpusSupportProfile: corpusSupportProfile
openQuestions: string[]
limitations: string[]
adjudicationStatus: adjudicationStatus
```

No historical finding count is imposed on this collection.

## Canonical scenarios

### `canonicalScenario`

```text
scenarioId: string
title: string
scenarioType: string
description: string
relevantThemeIds: string[]
relevantTensionIds: string[]
relevantFutureTrendFamilyIds: string[]
relevantKeyConceptFamilyIds: string[]
triggerConditions: string[]
branchPoints: string[]
plausiblePathways: string[]
indicators: string[]
counterSignposts: string[]
mitigatingConditions: string[]
tensionPoleDynamics: tensionPoleDynamic[]
relationshipsToOtherScenarios: scenarioRelationship[]
strategicImplications: string[]
responseOptions: string[]
researchQuestions: string[]
uncertaintyStatement: string
corpusSupportProfile: corpusSupportProfile
adjudicationStatus: adjudicationStatus
adjudicationConfidence: "high" | "medium" | "review"
reviewRequired: boolean
reviewFlags: string[]
historicalScenarioId: string  # private draft only
evidenceSelection: evidenceSelection  # private draft only
limitations: string[]
```

Supporting shapes:

```text
tensionPoleDynamic:
  tensionId: string
  direction: string
  dynamic: string
  rationale: string

scenarioRelationship:
  targetScenarioId: string
  semanticRole: "scenario-amplifies" | "scenario-mitigates" | "contextual-connection"
  qualifier: string | null
  rationale: string
  causalClaim: false

evidenceSelection:
  pathwayOrdinals: integer[]
  indicatorOrdinals: integer[]
  actionOrdinals: integer[]
  selectionRationales: object
```

Scenario arrays have no prescribed number of entries. Every scenario states
that it is a plausibility exercise rather than a prediction.

## Canonical relationships

### `canonicalRelationship`

```text
relationshipId: string
sourceType: string
sourceId: string
targetType: string
targetId: string
semanticRole: relationshipSemanticRole
qualifier: string | null
supportProfileId: string | null
adjudicationStatus: adjudicationStatus
```

### `relationshipSemanticRole`

The closed minimum vocabulary is:

```text
direct-coded-support
direct-content-representation
primary-family-membership
secondary-family-relationship
primary-theme-support
secondary-theme-support
conceptual-framing
future-extension
tension-evidence-pole-a
tension-evidence-pole-b
integrates
activated-tension
scenario-amplifies
scenario-mitigates
contextual-connection
shared-content-inheritance
```

`conceptual-framing`, `future-extension`, `contextual-connection`, and
`shared-content-inheritance` are not direct evidence. Scenario qualifiers such
as “may enable” or “may worsen” remain conditional descriptions and do not
assert causation.

Public release provenance applies the vocabulary as follows:

- the provenance collection has one `clusterRelationship` descriptor using
  `direct-coded-support` and `causalClaim: false`, applied to every
  release-to-cluster record;
- a release-to-tension record has a `relationships` array containing
  `tension-evidence-pole-a` when Pole A weight is positive and
  `tension-evidence-pole-b` when Pole B weight is positive;
- each tension relationship carries its positive `analyticalWeight` and
  `causalClaim: false`; and
- positive support for both poles produces both roles in the same
  release-to-tension record.

`direct-coded-support` is reserved for direct cluster coding provenance and is
never used for a tension evidence path.

### Public primary-support projection

The canonical public projection names content-unit breadth
`primaryContentUnitCount`. This measure follows the governed primary evidence
path for each entity type. Direct item coding applies only to clusters;
families, themes, narratives, findings, and scenarios derive primary evidence
through their governed supporting constructs, while tensions use directly
allocated pole evidence.

## Public allowlist and privacy boundary

Public-safe canonical entities may expose:

- canonical IDs, names, definitions, and boundary statements;
- canonical entity-to-entity relationships;
- aggregate support dimensions and limitations;
- public-release links; and
- governed adjudication status establishing publication eligibility.

Public artifacts must exclude:

- historical source-identity and private item identifiers;
- item text, excerpts, raw transcript text, and transcript hashes;
- source filenames, worksheets, row references, and local paths;
- internal review notes and candidate-allocation rationales;
- historical-to-canonical migration tables; and
- secrets, credentials, model-operation metadata, or machine-specific state.

Public provenance resolves downward only through useful canonical entities:

```text
canonical entity
  -> families
    -> clusters
      -> public releases
```

## Package-level validation

A canonical draft package is valid only when:

1. the selection overlay proves the governed corpus counts and exact retained
   item count;
2. no excluded or inherited record contributes analytical weight;
3. all 127 clusters have one primary family and no family is empty;
4. every medium-confidence mapping has an evidence-reviewed decision;
5. all relationship endpoints resolve and use the controlled vocabulary;
6. tension allocations are pole-aware and free of accidental duplication;
7. every retained higher-order entity has traceable support and limitations;
8. Key Concepts and Future Trends are represented in the cross-level audit;
9. duplicate IDs, duplicate set members, and semantic self-links are rejected;
10. checkpoint-level privacy and secret scans pass;
11. the checkpoint procedure runs two identical builds and confirms
    byte-identical artifacts;
12. regression tests pass; and
13. the current public Explorer and live public JSON remain unchanged.

Passing these checks permits an analytical checkpoint commit. It does not
authorize public canonical implementation; that requires separate human
approval.
