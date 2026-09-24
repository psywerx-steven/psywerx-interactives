# RDS migration classification

This is a planning classification of all 41 current RDS. It authorizes no migration and does not deactivate or reinterpret existing production records.

| Category | Count |
| --- | --- |
| READY_FOR_PROFILE_MATERIALIZATION | 1 |
| PROFILE_DEFINITION_REQUIRED | 13 |
| MULTIPLE_PROFILE_REVIEW_REQUIRED | 12 |
| LATENT_ESTIMATION_DESIGN_REQUIRED | 0 |
| NON_EXECUTABLE_PENDING_SCIENCE | 13 |
| BLOCKED_BY_ONTOLOGY | 2 |
| TOTAL | 41 |

`LATENT_ESTIMATION_DESIGN_REQUIRED` has count zero because no current RDS record is explicitly governed as latent/estimated. The architecture still needs that profile type so future reviews do not force estimated states into deterministic formulas.

## Record classification

| RDS | Layer | Category | Basis |
| --- | --- | --- | --- |
| BIO-003 | Biological | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| BIO-006 | Biological | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| CUL-088 | Cultural | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| INF-004 | Informational | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| INF-010 | Informational | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| INF-011 | Informational | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| INF-014 | Informational | BLOCKED_BY_ONTOLOGY | Current governed blocker prevents safe profile governance without an ontology/metadata decision. |
| INF-053 | Informational | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| INF-068 | Informational | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| INS-024 | Institutional / Structural | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| INS-039 | Institutional / Structural | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| INS-103 | Institutional / Structural | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| INS-113 | Institutional / Structural | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| PSY-078 | Psychological | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| RDS-0001 | Informational | BLOCKED_BY_ONTOLOGY | Current governed blocker prevents safe profile governance without an ontology/metadata decision. |
| RDS-0002 | Biological | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| RDS-0003 | Biological | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| RDS-0004 | Biological | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| RDS-0005 | Social | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| RDS-0006 | Social | READY_FOR_PROFILE_MATERIALIZATION | Existing exact governed DER-V1-SOC-F07-001 can be wrapped additively; no causal authorization follows. |
| RDS-0007 | Social | NON_EXECUTABLE_PENDING_SCIENCE | Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics. |
| SOC-018 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-022 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-024 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-035 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-041 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-046 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-047 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-049 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-050 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-051 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-052 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-053 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-054 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-055 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-056 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-057 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-074 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-076 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |
| SOC-090 | Social | MULTIPLE_PROFILE_REVIEW_REQUIRED | Metric family, boundary, variant, or context permits materially distinct computations requiring identity review. |
| SOC-096 | Social | PROFILE_DEFINITION_REQUIRED | Construct metadata exists, but no exact governed computation profile and binding were found. |

`READY_FOR_PROFILE_MATERIALIZATION` means structurally ready for a later governed additive wrapper, not authorized now. `NON_EXECUTABLE_PENDING_SCIENCE` describes behavior under the proposed contract and does not alter any current production relationship or lifecycle state.
