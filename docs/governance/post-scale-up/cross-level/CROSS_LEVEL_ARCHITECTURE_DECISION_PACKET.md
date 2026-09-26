# DP-PSG-002 - cross-level exposure architecture decision packet

**Status:** HUMAN ARCHITECTURE GOVERNANCE REQUIRED

## Recommendation

Adopt the bounded A+B+C hybrid. A typed reusable mapping carries the level-transition/exposure contract. C becomes an exact ID/version reference plus claim-specific qualifiers on a Relationship. B is conditional: reference real bridge Drivers/HappeningTypes when the science requires them, and never mint plumbing constructs.

## Required safeguards

- Mapping is noncausal, non-evidentiary and non-executable by itself.
- Exact immutable versions; no default/latest selection.
- Actual and perceived exposure stay distinct.
- Membership, eligibility, policy adoption and implementation remain insufficient alone.
- Network routes depend on WP-PSG-003; aggregate causal-source authority remains WP-PSG-005.
- WP-PSG-004 receives contribution/alternate-route references; WP-PSG-007 governs genuine construct gaps.
- Existing science and dispositions remain unchanged until separate re-adjudication.

## Exact bounded approval statement

> Approve the bounded WP-PSG-002 architecture direction tested in DP-PSG-002: use an immutable, versioned CrossLevelExposureMapping as a separate noncausal scientific routing/eligibility contract; require each governed cross-level Relationship to reference an exact mapping ID/version with claim-specific qualifiers; and require references to existing Driver or HappeningType intermediates only when they are scientifically substantive parts of the pathway. The mapping must distinguish source state, implementation/transmission, eligibility or membership, actual exposure, optional perceived exposure, temporal order and target response; mapping existence must confer no causal evidence, lifecycle, weight, propagation or execution authority. This approval authorizes architecture direction and later non-production prototyping only. It does not authorize Relationship reclassification, cross-level edge execution or activation, new Drivers, new HappeningTypes, Network State changes, RDS causal-source eligibility, production migration, ontology mutation, lifecycle change, source registration or activation; each requires separate governance.
