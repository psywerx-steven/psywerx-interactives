# Relationship + Intervention Architecture V1 Governance Decision

**Decision ID:** `GOV-REL-INT-V1-2026-09-05`

**Decision date:** 2026-09-05

**Authority:** Authorized human governor

**Source authorization:** The explicit human governance instruction directing
materialization of D01–D14 on PR #11, supplied on 2026-09-05

**Decision-package baseline:**
`b4714ef25fe9491b9953b2e7d3b42d2bcf1a5460`

**Status:** Governed architecture decision; production implementation not
authorized

## Decision

The authorized human governor approved the Relationship + Intervention
Architecture V1 decisions below. A `MODIFY` outcome adopts the replacement rule
recorded in the governed
[decision package](RELATIONSHIP_INTERVENTION_V1_DECISION_PACKAGE.md), not the
superseded recommendation text.

| ID | Outcome | Governed result |
| --- | --- | --- |
| D01 | `APPROVE` | Seven relation families and `predicate` as the only relationship subtype |
| D02 | `APPROVE` | Symmetric first-class noncausal Association records |
| D03 | `MODIFY` | `PRECEDES` and qualified-state `TRANSITIONS_TO`; bare entity transformation is invalid |
| D04 | `APPROVE` | Normalized n-ary Moderation assertion targeting one governed causal relationship |
| D05 | `APPROVE` | Governed causal segments plus separately governed CausalPathway assertions |
| D06 | `MODIFY` | Split directness semantics with `MODELED_LOCAL_LINK`, `TOTAL_EFFECT`, and `UNRESOLVED_SHORTCUT` |
| D07 | `APPROVE` | Intervention and InterventionEffect objects; Package as an Intervention subtype |
| D08 | `MODIFY` | Driver/Relationship target vocabulary only; no generic context target/effect mode |
| D09 | `MODIFY` | Absolute RDS target prohibition and required mechanistic Driver linkage for active relationship effects |
| D10 | `APPROVE` | Standard, heightened, and exceptional Driver/RDS causal gates |
| D11 | `APPROVE` | Six lifecycle states plus separate activation and block states |
| D12 | `MODIFY` | Automated non-governed research transitions; human-only governance and activation |
| D13 | `APPROVE` | Lossless, ID-stable, null-preserving, provenance-preserving V3-to-V1 migration model |
| D14 | `APPROVE` | Preview authority may change only through a separate migration-baseline adoption action |

The exact canonical vocabulary, validation semantics, compatibility rules, and
safeguards are the D01–D14 rules in the decision package as modified by this
authorization. Architecture documents and non-production draft schemas in this
PR materialize those rules.

## Authority boundaries

This decision governs the architecture needed for later implementation. It
does not:

- approve, reject, revise, or activate any scientific Relationship;
- approve or populate an Intervention or InterventionEffect;
- authorize a Family audit, pilot, relationship audit, or intervention search;
- authorize production V1 schemas, datasets, migration, or application use;
- reclassify a Driver or RDS;
- resolve a deferred migration or ontology item;
- alter source workbooks, scenario-service behavior, application behavior, or
  public Explorer behavior; or
- authorize deployment.

The existing 431 governed active causal Relationships retain their current V3
scientific authority and content. The draft V1 schemas remain in
`docs/governance/drafts/`; they are design artifacts, not production contracts.

## Governance and automation rule

AI and automation may create, research, enrich, validate, deduplicate, and move
non-governed records among the authorized research-workflow states while those
records remain `NOT_ELIGIBLE`. Only an authorized human governor may govern,
reject, activate, inactivate, deprecate, or substantively revise canonical
scientific knowledge. Automation may materialize an already authorized exact
human decision without broadening or interpreting it.

## Separate baseline action

D14 authorizes the rule requiring a separate baseline-adoption decision. The
source authorization also authorizes a later, separate branch and pull request
to adopt the exact v0.3 migration baseline. That action must not be combined
with PR #11 and must retain its own decision record, validation, and merge
history.

## Implementation gate

Merging PR #11 records the governed architecture only. Production
Relationship V1 implementation, Intervention catalogs/effects, population,
Family audits, modeling changes, and deployment each remain outside this
decision and require separate authorization.
