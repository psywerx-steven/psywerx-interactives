# Completeness and integrity report

Audit: `AUD-SOC-F07-AE-V1-20260906-001`. Frozen baseline: `f0be9c24288bd128231e0d1243b34c03ad055906`. Candidate-only; no governance, activation or source registration.

Recorded coverage flags are not instructions to invent edges.

|Metric | Value |
|--- | --- |
| activeEffectCount | 0 |
| blockedEntityCount | 4 |
| causalIncident | 7 |
| causallyIsolatedEntities | 7 |
| crossLayer | 2 |
| drivers | 1 |
| entities | 13 |
| id | SOC-F07 |
| internal | 4 |
| isolatedFamily | False |
| layer | Social |
| legacyIncompleteIncident | 7 |
| memberIds | ['RDS-0005', 'RDS-0006', 'RDS-0007', 'SOC-049', 'SOC-050', 'SOC-051', 'SOC-052', 'SOC-053', 'SOC-054', 'SOC-055', 'SOC-056', 'SOC-057', 'SOC-102'] |
| name | Network Structure & Position |
| nativeActionsEventsEffectIds | [] |
| rds | 12 |
| rdsCausalSourceCount | 5 |
| sameLayerCrossFamily | 1 |

## Corpus and candidate counts


|Metric | Value |
|--- | --- |
| production | {'drivers': 770, 'rds': 41, 'entities': 811, 'combinedActiveRelationships': 457, 'combinedActiveCausal': 436, 'combinedBySemantic': {'CAUSAL': 436, 'COMPOSITIONAL': 1, 'SEMANTIC': 8, 'REALIZATION': 2, 'DERIVATIONAL': 9, 'EMPIRICAL_NONCAUSAL': 1}} |
| existingDisposition | {'REVISION_CANDIDATE': 2, 'RETAIN_AS_IS': 3, 'RETYPE_CANDIDATE': 4, 'RESEARCH_NEEDED': 1} |
| hypothesisDisposition | {'REJECTED': 15, 'RESEARCH_NEEDED': 11, 'REVIEW_READY': 1, 'BLOCKED_NEEDS_GOVERNANCE_INPUT': 2} |
| newRelationships | 1 |
| newRelationshipSemantics | {'DERIVATIONAL': 1} |
| happeningTypes | 8 |
| effectAssertions | 3 |
| evidenceAssessments | 11 |
| sourceFindings | 34 |
| findingDisposition | {'INSUFFICIENT': 24, 'MIXED': 5, 'NULL_FINDING': 3, 'SUPPORTS': 2} |
| sources | 33 |
| canonicalReused | 15 |
| supplemental | 18 |
| sourceDesignDistribution | {'EVIDENCE_SYNTHESIS': 7, 'THEORETICAL_MECHANISTIC': 7, 'EXPERIMENTAL': 10, 'DEFINITIONAL_CALCULATIONAL': 3, 'UNTESTED_HYPOTHESIS': 1, 'MODEL_SIMULATION': 1, 'QUASI_EXPERIMENTAL': 2, 'OBSERVATIONAL_LONGITUDINAL': 2} |
| scientificRecordLifecycle | {'REVIEW_READY': 10, 'RESEARCH_NEEDED': 13} |
| revisionProposals | 6 |
| ontologyTargetGaps | 12 |
| separateGovernanceBlockedItems | 14 |
| newGoverned | 0 |
| newActive | 0 |
| note | Evidence findings nested within candidate assessments are not extra scientific identities. Revision/target-gap/hypothesis ledgers counted separately. |

## Structural flags

No production edge changed, so before/after production degree, isolates, cycles and connectivity are identical. All five current RDS causal sources were audited: SOC-052, SOC-054, SOC-055, SOC-056, SOC-053. Four internal RDS-to-RDS claims have shared-input/temporal risks. The one same-Layer outgoing claim needs scoped reinforcement evidence. Suspicious-hub/contradiction signals are review flags, not diagnoses. No new causal candidate, reciprocal edge or pathway was created.

The retained derivation is noncausal and adds no causal degree. RDS metrics can share adjacency, degree distributions, shortest paths and partitions; missing data and graph-size effects are not independent causes. No duplicate projection was counted.

## RDS and action coverage

All twelve RDS have explicit antecedent/target-gap ledgers; none is an EffectAssertion direct target. SOC-102 has complete search screening across eight origins/nine domains/eleven properties, but no adequately aligned supported effect. Eight identities do not imply eight efficacious interventions. Five origins have retained identities (SOC/INS/ENV/INF/TEC); BIO/PSY/CUL are searched no-findings for exact effects. No identity or effect is practitioner-eligible.

## Protected science

{'passed': True, 'filesCompared': 133}; comparison covers pre-existing data, schemas, migration handoff, scenario service, BIO-F01 and INF-F03 documents. New GOVERNED=0; new ACTIVE=0. Production counts remain 770 Drivers / 41 RDS / 811 entities / 457 active Relationships / 436 active causal.

## Self-review

All three potential Driver effects were retained only as research-needed hypotheses. No direct metric manipulation, intervention ranking, numeric execution, homophily-as-influence or reachability-as-mediation was admitted. Per-record findings distinguish source designs; model/theory evidence is not labeled empirical. Access limitations prevent stronger exact-edge claims.

## Exact before/after graph metrics


|Entity | Causal in before/after | Causal out before/after | Isolated |
|--- | --- | --- | --- |
| RDS-0005 | 0/0 | 0/0 | True |
| RDS-0006 | 0/0 | 0/0 | True |
| RDS-0007 | 0/0 | 0/0 | True |
| SOC-049 | 0/0 | 0/0 | True |
| SOC-050 | 0/0 | 0/0 | True |
| SOC-051 | 0/0 | 0/0 | True |
| SOC-052 | 0/0 | 1/1 | False |
| SOC-053 | 1/1 | 1/1 | False |
| SOC-054 | 0/0 | 1/1 | False |
| SOC-055 | 0/0 | 1/1 | False |
| SOC-056 | 1/1 | 1/1 | False |
| SOC-057 | 4/4 | 0/0 | False |
| SOC-102 | 0/0 | 0/0 | True |

Semantic scope split: {'CAUSAL/crossLayer': 2, 'SEMANTIC/sameLayerCrossFamily': 3, 'CAUSAL/internal': 4, 'CAUSAL/sameLayerCrossFamily': 1}. Maximum Family incident causal degree: 4. No reciprocal incident pair. Generic entity-ID overlap metrics miss shared external adjacency inputs; this pilot flags that limitation explicitly.
