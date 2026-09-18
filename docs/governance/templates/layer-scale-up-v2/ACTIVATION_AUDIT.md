# Layer Scale-Up V2 — activation audit prompt

Audit only the newly governed inactive records authorized by `[GOVERNANCE_DECISION]`. This is read-only; activation is not authorized.

For each Relationship, HappeningType, EffectAssertion, and EvidenceAssessment choose exactly:

- `READY_FOR_ACTIVATION_REVIEW`
- `KEEP_INACTIVE`
- `BLOCKED`

Require exact machine-readable scope, governed source-resolved evidence, no architecture or construct blocker, no RDS/RelationalState target violation, no duplicate contribution, no unresolved dependency, and no implication of numerical executability or practitioner actionability. Evaluate identity activation separately from efficacy. Evidence follows its assertion dependency; deliberate type/effect pairs may require atomic activation.

Return every record, exact reason, dependency order, source audit, RDS safety, blockers, and counts. Perform zero status changes and preserve all inactive records until a separate human activation decision.
