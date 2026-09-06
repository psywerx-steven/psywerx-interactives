# Relationship + Intervention Architecture V1

**Package status:** Governed architecture with production infrastructure;
scientific population not authorized

**Prepared:** 2026-09-05

**Scientific data/application behavior impact:** None

This directory contains the governed Relationship + Intervention Architecture
V1 design and its non-production schema drafts. The architecture decision does
not replace Relationship Schema v3, change any canonical entity or
relationship, publish an intervention catalog, or change application behavior.
Production V1 infrastructure is recorded separately below. Scientific
population, Family audits, application behavior changes, and deployment remain
unauthorized.

**Decision records:**

- [`GOV-REL-INT-V1-2026-09-05`](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)
- [`MIGRATION_BASELINE_ADOPTION_V0_3-2026-09-05`](MIGRATION_BASELINE_ADOPTION_V0_3.md)
- [`RELATIONSHIP_INTERVENTION_V1_IMPLEMENTATION-2026-09-05`](RELATIONSHIP_INTERVENTION_V1_IMPLEMENTATION_RECORD.md)

## Current governed baseline

- 770 Drivers and 41 relational/derived states (RDS), for 811 entities;
- 105 Families in eight Layers;
- Relationship Schema v3 with 450 active records: 431 fully specified active
  causal relationships and 19 active noncausal relationships;
- protected Driver/RDS v0.3 migration artifacts and CI invariants; and
- a separate Scenario Operationalization v1 service contract that produces
  transient analytical examples, not interventions or canonical knowledge.

PR #11 preserved the then-current `NON_AUTHORITATIVE_MIGRATION_PREVIEW`
designation and required a separate governance action before it could change.
The linked Migration Baseline Adoption V0.3 decision now adopts the exact v0.3
specification as `GOVERNED_MIGRATION_SPECIFICATION` and its deterministic output
as `GOVERNED_MIGRATION_BASELINE`. That adoption has its own branch, decision
record, validation, and pull request; it does not govern individual scientific
records beyond the exact migration decisions it names.

## Governed V1 architecture package

1. [Relationship Architecture V1](RELATIONSHIP_ARCHITECTURE_V1.md) defines the
   meanings of relationship, causal field requirements, RDS participation, and
   the compatibility path from Relationship Schema v3.
2. [Intervention Architecture V1](INTERVENTION_ARCHITECTURE_V1.md) defines a
   Driver-centered Intervention catalog, contextual effect assertions, and
   packages.
3. [Relationship + Intervention Governance V1](RELATIONSHIP_INTERVENTION_GOVERNANCE_V1.md)
   separates candidate generation, evidence review, and explicit governance.
4. [Family Audit Workflow V1](FAMILY_AUDIT_WORKFLOW_V1.md) defines the later
   repeatable production workflow and completeness controls.
5. [Pilot Recommendation V1](PILOT_RECOMMENDATION_V1.md) recommends three
   Families for a later pilot; it does not execute the pilot.
6. [`drafts/`](drafts/) contains non-production JSON Schema drafts for design
   review and tooling experiments.
7. [Decision Package](RELATIONSHIP_INTERVENTION_V1_DECISION_PACKAGE.md) records
   the D01–D14 analysis and final outcomes.
8. [Governance Decision](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)
   records the human authorization and scope limits.
9. [Migration Baseline Adoption V0.3](MIGRATION_BASELINE_ADOPTION_V0_3.md)
   separately records authority for the exact v0.3 migration specification and
   generated baseline while preserving all listed open governance items.
10. [V1 Implementation Record](RELATIONSHIP_INTERVENTION_V1_IMPLEMENTATION_RECORD.md)
    records the production schema/tooling materialization and its continuing
    scientific-population stop gate.

## Authorized Family pilots

- [`BIO-F01 — Sleep & Circadian Regulation`](pilots/BIO-F01/BIO_F01_GOVERNANCE_DECISION_PACKAGE.md)
  is the first structured scientific audit under V1. Its Relationship,
  EvidenceAssessment, Intervention, and InterventionEffect records are
  preserved as non-governed candidates for audit lineage.
  [`Governance Decision 001`](pilots/BIO-F01/BIO_F01_GOVERNANCE_DECISION_001.md)
  selectively materializes approved records under canonical V1 IDs.
  [`Activation Decision 001`](pilots/BIO-F01/BIO_F01_ACTIVATION_DECISION_001.md)
  authorizes the exact bounded active subset while retaining all listed
  research-needed, revision, and acoustic exclusions. It does not authorize a
  second Family, new model/recommendation behavior, or deployment.

## Non-production draft-schema rule

Files under `docs/governance/drafts/` preserve the reviewed design-stage
materialization but are not production schemas. The implemented contracts are
under `schemas/relationship-intervention/v1/`; their presence does not authorize
scientific population, Family audits, or activation of candidates.

## Internal critique record

| Question | Revision made before finalization |
| --- | --- |
| Is it unnecessarily complex or are types redundant? | Aggregation became derivation metadata; placement stayed in entity metadata; measurement stayed primarily in Operationalizations; mediation became a pathway rather than another edge. |
| Are fields reliably populatable? | Numeric strength, functional form, numeric lag, persistence, dose, frequency, duration, reversibility, feasibility, and channel are optional/context-dependent rather than forced placeholders. |
| Does it turn RDS back into Drivers? | Direct RDS intervention targets are prohibited; executable RDS values require derivation/measurement provenance and anti-double-counting rules. |
| Can practitioners understand it? | The workflow begins with a Family and Driver; relationship meanings and intervention effect modes use bounded questions and broad categories. |
| Can researchers defend it? | Causality, association, derivation, evidence strength, confidence, uncertainty, and conflict are separate. |
| Can machines use it? | Stable IDs, normalized Effect records, typed targets, lifecycle states, and draft JSON Schemas support deterministic validation. |
| Does it support causal modeling without overclaiming? | Only governed active causal records enter traversal; scenario weights remain model-package artifacts; noncausal relations are excluded. |
| Is intervention Driver-centered? | Every governed Intervention needs a Driver effect or exact edge effect with a mechanistic Driver; external taxonomies are crosswalks only. |
| Are mechanisms cleanly separated? | Intervention Effect stores intervention -> target mechanism; Relationship stores entity -> entity mechanism. |
| Are provenance, conflict, and updates supported? | Source IDs, evidence rationale/disposition, conflicting sources, uncertainty, immutable revisions, supersession, and decision records are required or recommended explicitly. |
| Can it scale? | Identity, effects, pathways, and crosswalks are normalized rather than embedded; Family ownership prevents repeated ontology-wide review. |
