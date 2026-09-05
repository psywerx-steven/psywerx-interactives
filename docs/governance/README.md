# Relationship + Intervention Architecture V1

**Package status:** Proposed for governance approval

**Prepared:** 2026-09-05

**Production impact:** None

This directory is a governance proposal. It does not replace Relationship
Schema v3, change any canonical entity or relationship, publish an intervention
catalog, or change application behavior. Until an authorized PSYWERX
governance decision adopts some or all of this package, the current governed
artifacts and contracts remain authoritative.

## Current governed baseline

- 770 Drivers and 41 relational/derived states (RDS), for 811 entities;
- 105 Families in eight Layers;
- Relationship Schema v3 with 450 active records: 431 fully specified active
  causal relationships and 19 active noncausal relationships;
- protected Driver/RDS v0.3 migration artifacts and CI invariants; and
- a separate Scenario Operationalization v1 service contract that produces
  transient analytical examples, not interventions or canonical knowledge.

The repository's `data/migration-manifest.json` still labels v0.3 a
`NON_AUTHORITATIVE_MIGRATION_PREVIEW`, while CI mechanically protects its exact
partition, counts, and 431 causal propositions. This package preserves that
status language; declaring the preview fully authoritative is a separate
governance decision.

## Proposed V1 package

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

## Non-authoritative draft rule

Files under `docs/governance/drafts/` are proposals only. Their presence does
not authorize generation of production data, migration of existing records,
or activation of candidates. A later approved implementation must choose
canonical file locations, controlled vocabularies, migration behavior, and CI
gates explicitly.

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
