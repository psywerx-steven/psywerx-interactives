# Cross-level exposure contract

The proposed object is a versioned `SCIENTIFIC_ROUTING_ELIGIBILITY_CONTRACT`. It is not a Driver, RDS, HappeningType, EffectAssertion, Relationship or Network State. It has no polarity, weight, activation value, lifecycle or propagation state. Mapping existence is not evidence.

## Field applicability

- Required universally: mappingId, mappingVersion, relationshipId, sourceEntityId, sourceLevel, targetEntityId, targetLevel, routeType, exposureDefinition, exposureUnit, temporalOrder, evidenceReferences, scopeLimitations, causalEvidence=false, executionAuthority=false, provenance.
- Required conditionally: membershipRule, eligibilityRule, implementationRequirement, assignmentRule, exposureWindow, exposureIntensity, coverageRule, contactRule, transmissionRule, perceptionRequired, perceptionEntityId, intermediateEntityIds, happeningTypeIds, networkStateDependency.
- Optional: contextRequirements, claimSpecificQualifiers, implementationEvidenceReferences, exposureEvidenceReferences.
- Prohibited/not applicable: activationStatus, activationValue, edgeWeight, fcmNodeState, lifecycleStatus, polarity, propagationValue.

## Routes

| Route | Meaning |
|---|---|
| `MEMBERSHIP` | Defines risk set only; never sufficient exposure. |
| `ELIGIBILITY` | Defines possible coverage only. |
| `ASSIGNMENT` | Assigns target unit to condition; receipt/contact still explicit. |
| `IMPLEMENTATION` | Formal state is realized in practice. |
| `ENFORCEMENT` | Rule is applied through a specified enforcement process. |
| `CONTACT` | Target unit encounters specified actor/context. |
| `INFORMATION_EXPOSURE` | Specified information is delivered or displayed; attention/perception separate. |
| `RESOURCE_ACCESS` | Resource becomes actually accessible to target unit. |
| `SERVICE_DELIVERY` | Specified service is delivered. |
| `SOCIAL_INTERACTION` | Bounded interaction constitutes exposure. |
| `NETWORK_POSITION` | Exact Network State creates a bounded opportunity/context; metric alone insufficient. |
| `AMBIENT_CONTEXT` | Persistent context applies without fabricating a discrete event. |
| `OBSERVATION` | Target can observe a specified condition. |
| `MONITORING` | Target is actually subject to monitoring. |
| `SANCTION_EXPOSURE` | Target receives or faces a specified applied sanction. |
| `INCENTIVE_EXPOSURE` | Target receives or faces a specified implemented incentive. |

Perception is required only when it is part of the stated mechanism or target. Membership, eligibility, assignment and implementation cannot substitute for actual exposure. Ambient contexts need bounded membership/exposure windows but no fabricated event. Discrete operations may reference an existing HappeningType. Exact source, implementation/transmission, exposure and response order is mandatory.

## Actual and perceived exposure patterns

| Pattern | Contract treatment |
|---|---|
| Objective exposure directly affects target | `perceptionRequired=false`; actual exposure remains mandatory. |
| Objective exposure must be interpreted | `perceptionRequired=true` with an exact perception entity/reference. |
| Target is perception of context | Actual encounter/observation and the perception target are both explicit; objective state alone cannot satisfy the target. |

## Dependencies

- `WP-PSG-003`: exact Network State identity and state/boundary transition; metric recalculation is not exposure.
- `WP-PSG-004`: underlying contribution identity, intermediate route IDs and alternate aggregate/constituent representations.
- `WP-PSG-005`: exact RDS/profile, mapping ID/version, constituent mapping, exposure route and temporal alignment; causal eligibility stays false.
- `WP-PSG-007`: genuine missing construct identities only; no architecture-plumbing Drivers or HappeningTypes.
