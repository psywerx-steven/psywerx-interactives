# Post-Scale-Up blocker backlog

This is the consolidated planning backlog after all eight full-Layer audits. It records safe current states and future work; it does not change science, architecture, ontology or activation.

## Counts

| Class | Items |
|---|---:|
| A_RDS_DEFINITION_DERIVATION | 5 |
| B_RDS_CAUSAL_SOURCE_INDEPENDENCE | 5 |
| C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY | 2 |
| D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION | 4 |
| E_MECHANISMSTATUS_ACTIVATION_CONTRACT | 2 |
| F_CONSTRUCT_CLASSIFICATION_ONTOLOGY | 4 |
| G_SOURCE_GOVERNANCE | 2 |
| H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS | 8 |
| I_CANDIDATE_SCIENCE_RESEARCH_NEEDED | 8 |
| J_INACTIVE_GOVERNED_BUNDLES | 4 |

## Items

### BLK-PSY-001 — Psychological

- Class: `A_RDS_DEFINITION_DERIVATION`
- Affected records: PSY relational derived-state route
- Scientific problem: The target construct and derivation are not exact enough for governed causal use.
- Architecture problem: Current target semantics cannot safely carry the proposed effect.
- Current safe state: Preserve governed records and blocker; no new causal use.
- Consequence if unresolved: The affected route remains unavailable to active consumers.
- Blocks active execution: **YES**
- Recommended future work: `DEDICATED_RDS_AND_TARGET_GOVERNANCE`

### BLK-PSY-002 — Psychological

- Class: `F_CONSTRUCT_CLASSIFICATION_ONTOLOGY`
- Affected records: PSY construct-classification route
- Scientific problem: A candidate cannot be classified without changing its scientific meaning.
- Architecture problem: A classification decision would alter ontology semantics.
- Current safe state: Leave the candidate blocked and production unchanged.
- Consequence if unresolved: One candidate route remains unavailable.
- Blocks active execution: **YES**
- Recommended future work: `ONTOLOGY_GOVERNANCE`

### BLK-PSY-003 — Psychological

- Class: `D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION`
- Affected records: REL-V1-PSY-LAYER-001, EA-V1-PSY-LAYER-001, CONTRIB-PSY-LAYER-REPETITION-001
- Scientific problem: Relationship and EffectAssertion encode one repetition contribution.
- Architecture problem: Active contribution deduplication is not defined.
- Current safe state: Keep both representations inactive and preserve shared lineage.
- Consequence if unresolved: The repetition contribution cannot activate safely.
- Blocks active execution: **YES**
- Recommended future work: `CONTRIBUTION_DEDUP_ARCHITECTURE`

### HYP-INF-F03-H20 — Informational

- Class: `F_CONSTRUCT_CLASSIFICATION_ONTOLOGY`
- Affected records: INF-013, INF-077
- Scientific problem: Conceptual and surface-definition overlap cannot be resolved by selecting one measure.
- Architecture problem: No governed identity, merge or feature-scope rule resolves the boundary.
- Current safe state: Preserve both definitions and blocked metadata.
- Consequence if unresolved: Dependent candidates remain research-needed or blocked.
- Blocks active execution: **YES**
- Recommended future work: `CONSTRUCT_BOUNDARY_GOVERNANCE`

### ARCH-INF-LAYER-0001 — Informational

- Class: `A_RDS_DEFINITION_DERIVATION`
- Affected records: 7 Informational RDS
- Scientific problem: Portable derivations and constituent overlap remain incomplete for broader causal use.
- Architecture problem: RDS causal-source semantics require dedicated review.
- Current safe state: No new RDS target, source authorization or Network State binding.
- Consequence if unresolved: Aggregate routes remain conservative and inactive.
- Blocks active execution: **YES**
- Recommended future work: `RDS_ARCHITECTURE_REVIEW`

### META-INF-LAYER-0001 — Informational

- Class: `G_SOURCE_GOVERNANCE`
- Affected records: 11 INF-F03 source-queue rows
- Scientific problem: Candidate provenance includes unresolved work/version and source-identity rows.
- Architecture problem: Canonical registration contract is not satisfied for every row.
- Current safe state: Keep the queue candidate-only and truthful.
- Consequence if unresolved: Some deferred candidates lack canonical provenance.
- Blocks active execution: **NO**
- Recommended future work: `SOURCE_IDENTITY_RESOLUTION`

### BLK-BIO-RDS-001 — Biological

- Class: `A_RDS_DEFINITION_DERIVATION`
- Affected records: BIO-F01 five RDS, BIO-003
- Scientific problem: Exact versioned calculation and aggregation definitions are insufficient, especially for BIO-003 constituent overlap.
- Architecture problem: Current RDS architecture cannot establish independent causal-source use.
- Current safe state: Keep RDS definitions and causal-source semantics unchanged.
- Consequence if unresolved: Broader Biological RDS execution remains blocked.
- Blocks active execution: **YES**
- Recommended future work: `RDS_DERIVATION_GOVERNANCE`

### ASTRA-BIO-LAYER-001 — Biological

- Class: `B_RDS_CAUSAL_SOURCE_INDEPENDENCE`
- Affected records: BIO-003 outgoing route
- Scientific problem: It is unresolved whether the source is independent of sleep-duration constituents.
- Architecture problem: Aggregate contribution control is undefined.
- Current safe state: No new causal authorization.
- Consequence if unresolved: Potential double counting remains avoided by deferral.
- Blocks active execution: **YES**
- Recommended future work: `CAUSAL_SOURCE_ADJUDICATION`

### BLK-CUL-RDS-001 — Cultural

- Class: `A_RDS_DEFINITION_DERIVATION`
- Affected records: CUL-088, REL-CUL-042, CUL-061
- Scientific problem: Generational Cultural Distance lacks a governed metric, aggregation and reference window.
- Architecture problem: RDS causal-source architecture is not versioned for this route.
- Current safe state: Keep REL-CUL-042 unchanged and the review disposition blocked.
- Consequence if unresolved: The distance route cannot support new active execution.
- Blocks active execution: **YES**
- Recommended future work: `RDS_METRIC_GOVERNANCE`

### ASTRA-CUL-LAYER-001 — Cultural

- Class: `B_RDS_CAUSAL_SOURCE_INDEPENDENCE`
- Affected records: CUL-088, REL-CUL-042
- Scientific problem: Aggregate distance may share constituents with its target or contextual inputs.
- Architecture problem: Independent aggregate causal semantics are unresolved.
- Current safe state: No causal-source authorization.
- Consequence if unresolved: Possible contextual effects remain unavailable.
- Blocks active execution: **YES**
- Recommended future work: `AGGREGATE_CAUSAL_REVIEW`

### BLK-ENV-ACTIVATION-001 — Physical / Environmental

- Class: `E_MECHANISMSTATUS_ACTIVATION_CONTRACT`
- Affected records: EVA-AE-V1-ENV-LAYER-001, HT-V1-ENV-LAYER-001, EA-V1-ENV-LAYER-001
- Scientific problem: The bounded natural-walk effect is supported, but the multisensory package does not identify a component mechanism.
- Architecture problem: ACTIVE EffectAssertions currently require mechanismStatus other than UNKNOWN.
- Current safe state: Preserve the governed bundle inactive and mechanismStatus UNKNOWN.
- Consequence if unresolved: The bounded bundle cannot activate under the current contract.
- Blocks active execution: **YES**
- Recommended future work: `ACTIVATION_LIFECYCLE_GOVERNANCE`

### BLK-TEC-ACTIVATION-001 — Technological

- Class: `E_MECHANISMSTATUS_ACTIVATION_CONTRACT`
- Affected records: EVA-AE-V1-TEC-LAYER-001, HT-V1-TEC-LAYER-001, EA-V1-TEC-LAYER-001
- Scientific problem: The bounded AI-label effect does not identify a sufficiently exact mechanism across media and interface boundaries.
- Architecture problem: ACTIVE EffectAssertions require a non-UNKNOWN mechanismStatus.
- Current safe state: Preserve the governed bundle inactive and scientific qualifiers intact.
- Consequence if unresolved: The Tech bundle cannot activate under the current contract.
- Blocks active execution: **YES**
- Recommended future work: `ACTIVATION_LIFECYCLE_GOVERNANCE`

### BLK-TEC-METADATA-001 — Technological

- Class: `F_CONSTRUCT_CLASSIFICATION_ONTOLOGY`
- Affected records: TEC-097, TEC-098, TEC-099
- Scientific problem: Blocked scientific metadata remains unresolved.
- Architecture problem: Repair could imply an unauthorized construct or architecture decision.
- Current safe state: Preserve blocked fields.
- Consequence if unresolved: Dependent candidates remain unavailable.
- Blocks active execution: **YES**
- Recommended future work: `METADATA_AND_ONTOLOGY_GOVERNANCE`

### HYP-SOC-F07-H12 — Social

- Class: `D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION`
- Affected records: network adjacency, degree RDS
- Scientific problem: Network rewiring changes adjacency and derived metrics but does not prove an empirical causal effect.
- Architecture problem: No complete canonical adjacency-state Driver target exists.
- Current safe state: Use ScenarioStateDelta plus recalculation only.
- Consequence if unresolved: The proposed causal effect remains blocked.
- Blocks active execution: **YES**
- Recommended future work: `NETWORK_STATE_ARCHITECTURE`

### HYP-SOC-F07-H20 — Social

- Class: `D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION`
- Affected records: node deletion, fragmentation RDS
- Scientific problem: Node deletion changes state and recalculates fragmentation.
- Architecture problem: No ordinary Driver represents the node/boundary transformation.
- Current safe state: Preserve blocked derivation metadata and recalculation-only semantics.
- Consequence if unresolved: The proposed causal effect remains blocked.
- Blocks active execution: **YES**
- Recommended future work: `NETWORK_STATE_ARCHITECTURE`

### ASTRA-SOC-LAYER-001 — Social

- Class: `B_RDS_CAUSAL_SOURCE_INDEPENDENCE`
- Affected records: 10 Social RDS causal sources
- Scientific problem: Independent aggregate mechanisms and constituent double counting remain unresolved.
- Architecture problem: Current RDS source semantics do not encode contribution independence.
- Current safe state: Keep advisory dispositions and production unchanged.
- Consequence if unresolved: Ten aggregate-source routes need dedicated review before broader use.
- Blocks active execution: **YES**
- Recommended future work: `RDS_CAUSAL_SOURCE_PROGRAM`

### ASTRA-SOC-LAYER-002 — Social

- Class: `C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY`
- Affected records: group-to-person Relationships
- Scientific problem: Group states do not automatically expose individual actors.
- Architecture problem: No generic exposure mapping bridges group and person levels.
- Current safe state: Keep affected edges research-needed or review-only.
- Consequence if unresolved: Cross-level active execution remains scientifically constrained.
- Blocks active execution: **YES**
- Recommended future work: `CROSS_LEVEL_EXPOSURE_ARCHITECTURE`

### ASTRA-SOC-LAYER-003 — Social

- Class: `D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION`
- Affected records: HYP-SOC-F07-H12, HYP-SOC-F07-H20, DER-V1-SOC-F07-001
- Scientific problem: Adjacency and membership operations mix empirical interventions, state changes and metric recalculation.
- Architecture problem: A future cross-level state object may be needed.
- Current safe state: Preserve the governed derivation inactive and recalculation-only.
- Consequence if unresolved: Some network operations cannot be represented as causal Effects.
- Blocks active execution: **YES**
- Recommended future work: `NETWORK_STATE_R_AND_D`

### SRC-CAND-SOC-F07-010 — Social

- Class: `G_SOURCE_GOVERNANCE`
- Affected records: HT-CAND-SOC-F07-008
- Scientific problem: A verified non-PubMed source binding lacks a satisfied canonical registration route.
- Architecture problem: The source contract must preserve truthful non-PubMed provenance.
- Current safe state: Keep the candidate source queue intact.
- Consequence if unresolved: One candidate identity remains provenance-constrained.
- Blocks active execution: **NO**
- Recommended future work: `NON_PUBMED_SOURCE_REGISTRATION`

### BLK-INS-METADATA-001 — Institutional / Structural

- Class: `F_CONSTRUCT_CLASSIFICATION_ONTOLOGY`
- Affected records: INS-115, INS-116
- Scientific problem: Scientific mechanism, time, observability, evidence and source fields remain blocked.
- Architecture problem: Repair would require separate scientific governance.
- Current safe state: Keep both Drivers blocked and terminate dependent routes conservatively.
- Consequence if unresolved: No current incident edge is lost, but future materialization is blocked.
- Blocks active execution: **YES**
- Recommended future work: `DRIVER_METADATA_GOVERNANCE`

### BLK-INS-RDS-001 — Institutional / Structural

- Class: `A_RDS_DEFINITION_DERIVATION`
- Affected records: INS-039, INS-103, REL-INS-017, REL-INS-036
- Scientific problem: The two causal-source RDS lack exact versioned inputs, aggregation and independent aggregate mechanisms.
- Architecture problem: Current architecture cannot control constituent overlap safely.
- Current safe state: No new RDS definition, retype or causal-source authorization.
- Consequence if unresolved: Both aggregate-source routes remain blocked for future active use.
- Blocks active execution: **YES**
- Recommended future work: `RDS_DERIVATION_AND_CAUSAL_GOVERNANCE`

### ASTRA-INS-LAYER-001 — Institutional / Structural

- Class: `B_RDS_CAUSAL_SOURCE_INDEPENDENCE`
- Affected records: INS-039, REL-INS-017, INS-063
- Scientific problem: Caseload Pressure may summarize workload/staffing constituents that also define or cause capacity.
- Architecture problem: Independent aggregate contribution is unresolved.
- Current safe state: Keep the edge unchanged and advisory review blocked.
- Consequence if unresolved: Potential double counting remains avoided by deferral.
- Blocks active execution: **YES**
- Recommended future work: `AGGREGATE_CAUSAL_ADJUDICATION`

### ASTRA-INS-LAYER-002 — Institutional / Structural

- Class: `B_RDS_CAUSAL_SOURCE_INDEPENDENCE`
- Affected records: INS-103, REL-INS-036, INS-107
- Scientific problem: Staffing Adequacy is a ratio whose independent effect on territorial reach is not established.
- Architecture problem: Ratio constituents, unit and temporal order are not bound.
- Current safe state: Keep production unchanged and block new authorization.
- Consequence if unresolved: The route cannot be broadened or numerically executed.
- Blocks active execution: **YES**
- Recommended future work: `AGGREGATE_CAUSAL_ADJUDICATION`

### ASTRA-INS-LAYER-003 — Institutional / Structural

- Class: `C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY`
- Affected records: 20 Institutional cross-Layer causal propositions
- Scientific problem: Institution-level policies and procedures need explicit implementation and exposure routes before targeting person-level states.
- Architecture problem: Current metadata lacks a generic cross-level bridge.
- Current safe state: Reuse prior conservative reviews; no new bridge or edge.
- Consequence if unresolved: Cross-level claims remain limited to existing governed scope.
- Blocks active execution: **YES**
- Recommended future work: `CROSS_LEVEL_EXPOSURE_ARCHITECTURE`

### BACKLOG-REL-PSYCHOLOGICAL_LAYER — Psychological

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 57 revision, 5 retype, 2 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-PSYCHOLOGICAL_LAYER — Psychological

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 36 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-INFORMATIONAL_LAYER — Informational

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 12 revision, 18 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-INFORMATIONAL_LAYER — Informational

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 16 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-BIOLOGICAL_LAYER — Biological

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 5 revision, 0 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-BIOLOGICAL_LAYER — Biological

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 14 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-CULTURAL_LAYER — Cultural

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 6 revision, 5 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-CULTURAL_LAYER — Cultural

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 36 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-PHYSICAL_ENVIRONMENTAL_LAYER — Physical / Environmental

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 2 revision, 4 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-PHYSICAL_ENVIRONMENTAL_LAYER — Physical / Environmental

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 9 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-TECHNOLOGICAL_LAYER — Technological

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 3 revision, 31 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-TECHNOLOGICAL_LAYER — Technological

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 22 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-SOCIAL_LAYER — Social

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 7 revision, 4 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-SOCIAL_LAYER — Social

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 30 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### BACKLOG-REL-INSTITUTIONAL_STRUCTURAL_LAYER — Institutional / Structural

- Class: `H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS`
- Affected records: 8 revision, 3 retype, 0 split
- Scientific problem: Full-Layer review found bounded revision, retype or split proposals that remain advisory.
- Architecture problem: No architecture change is implied until each proposition is separately governed.
- Current safe state: Keep every production Relationship unchanged.
- Consequence if unresolved: Known semantic debt remains visible without destabilizing production.
- Blocks active execution: **NO**
- Recommended future work: `RELATIONSHIP_PROPOSITION_GOVERNANCE`

### BACKLOG-RN-INSTITUTIONAL_STRUCTURAL_LAYER — Institutional / Structural

- Class: `I_CANDIDATE_SCIENCE_RESEARCH_NEEDED`
- Affected records: 26 existing Relationship reviews plus Layer candidate routes
- Scientific problem: Exact causal identification, target alignment, scope or evidence remains insufficient.
- Architecture problem: No architecture decision is required merely to retain research-needed status.
- Current safe state: Keep candidate and advisory records non-governed or inactive as recorded.
- Consequence if unresolved: Potential science remains unavailable for new production use.
- Blocks active execution: **NO**
- Recommended future work: `TARGETED_EVIDENCE_RESEARCH`

### INACTIVE-BIO-IDENTITY-001 — Biological

- Class: `J_INACTIVE_GOVERNED_BUNDLES`
- Affected records: HT-V1-BIO-LAYER-001
- Scientific problem: A coherent caffeine-cessation identity has no governed eligible effect.
- Architecture problem: No independent active meaning is required.
- Current safe state: GOVERNED / INACTIVE; KEEP_INACTIVE.
- Consequence if unresolved: Identity remains reusable for future evidence work.
- Blocks active execution: **NO**
- Recommended future work: `EFFECT_EVIDENCE_RESEARCH`

### INACTIVE-INF-IDENTITY-001 — Informational

- Class: `J_INACTIVE_GOVERNED_BUNDLES`
- Affected records: HT-V1-INF-LAYER-001
- Scientific problem: A reference-group prevalence-display identity has no governed eligible effect.
- Architecture problem: No independent active meaning is required.
- Current safe state: GOVERNED / INACTIVE; KEEP_INACTIVE.
- Consequence if unresolved: Identity remains reusable for future evidence work.
- Blocks active execution: **NO**
- Recommended future work: `EFFECT_EVIDENCE_RESEARCH`

### INACTIVE-ENV-BUNDLE-001 — Physical / Environmental

- Class: `J_INACTIVE_GOVERNED_BUNDLES`
- Affected records: EVA-AE-V1-ENV-LAYER-001, HT-V1-ENV-LAYER-001, EA-V1-ENV-LAYER-001
- Scientific problem: Bounded evidence/effect bundle remains scientifically valid but activation-blocked.
- Architecture problem: See BLK-ENV-ACTIVATION-001.
- Current safe state: GOVERNED / INACTIVE.
- Consequence if unresolved: No active production participation.
- Blocks active execution: **YES**
- Recommended future work: `ACTIVATION_CONTRACT_GOVERNANCE`

### INACTIVE-TEC-BUNDLE-001 — Technological

- Class: `J_INACTIVE_GOVERNED_BUNDLES`
- Affected records: EVA-AE-V1-TEC-LAYER-001, HT-V1-TEC-LAYER-001, EA-V1-TEC-LAYER-001
- Scientific problem: Bounded evidence/effect bundle remains scientifically valid but activation-blocked.
- Architecture problem: See BLK-TEC-ACTIVATION-001.
- Current safe state: GOVERNED / INACTIVE.
- Consequence if unresolved: No active production participation.
- Blocks active execution: **YES**
- Recommended future work: `ACTIVATION_CONTRACT_GOVERNANCE`
