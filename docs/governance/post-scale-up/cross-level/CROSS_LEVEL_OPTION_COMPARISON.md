# Cross-level architecture option comparison

| Option | Result | What worked | What failed |
|---|---|---|---|
| A | VIABLE_BUT_INCOMPLETE_ALONE | Reusable typed contract; Runtime validation; Ambient and discrete routes; Separation from causal evidence | Needs exact Relationship attachment; Can proliferate without identity rules; May look causal unless prohibited semantics are enforced |
| B | REJECT_AS_UNIVERSAL_REQUIREMENT | Uses real intermediate constructs when scientifically present; Keeps substantive mechanisms in ontology | Missing bridge constructs; Artificial plumbing Drivers; Long paths; HappeningType/state confusion; Ontology bloat |
| C | REJECT_AS_COMPLETE_SOLUTION | Small additive migration; Relationship-local clarity; Backward-compatible display | Duplicates route content; Weak reuse; Metadata may be ignored; Cannot centrally version shared mappings |
| A+B | VIABLE_WITH_ATTACHMENT_GAP | Typed route plus real bridges only when warranted | Relationship still needs exact versioned reference |
| A+C | VIABLE_CORE | Reusable mapping plus exact mapping reference and claim qualifiers | Does not by itself state when bridge entities are scientifically required |
| A+B+C | RECOMMENDED_BOUNDED_HYBRID | Reusable contract; Exact Relationship reference; Conditional real bridge references; Fail-closed validation; Ambient and discrete exposure | Requires migration and consumer awareness; Needs strict identity/proliferation governance |

The recommended bounded hybrid is A+B+C with A+C as the required architecture and B conditional on scientific meaning. Option B is rejected as a universal bridge requirement; Option C is rejected as a complete solution; Option A alone lacks an exact claim attachment.

## Decision matrix

| Criterion | A | B | C | Bounded A+B+C |
|---|---|---|---|---|
| Scientific fidelity | High if noncausal | High only for real intermediates | Moderate | High with conditional B |
| Cross-level explicitness | High | Path-dependent | Relationship-local | High and claim-bound |
| Ontology burden | One new contract class | Potentially high | Low | Bounded by no-plumbing rule |
| Runtime enforceability | High | Incomplete when bridges absent | Moderate | High |
| Reuse | High | Varies | Low | High |
| Migration safety | Additive registry | Potential ontology migration | Additive fields | Additive but consumer-aware |
| Ambient context | Supported | May fabricate state/event | Displayable | Supported without fake event |
| Discrete exposure | Supported | Supported via real HT | Displayable | Supported with optional HT ref |
| Perception mediation | Conditional explicit | Requires real perception Driver | Easy to omit | Explicit and optionally entity-bound |
| Network State compatibility | Can require exact reference | Cannot replace state | Weak alone | Fail-closed dependency |
| WP-PSG-005 compatibility | Supplies route contract | Supplies real intermediates | Attaches exact mapping | Complete handoff; no authorization |
| Contribution-control compatibility | Can expose alternate routes | May reveal duplicate paths | Claim-local qualifier | Best handoff to WP-PSG-004 |
| Consumer clarity / rollback | Central and removable | Harder if ontology added | Simple but duplicative | Exact ref; remove integration to rollback |

## Skeptical architecture review

- **Hidden causal entity:** Prevented only if the mapping schema prohibits polarity, weights, lifecycle, node state, propagation and execution authority.
- **Relationship or Actions & Events duplication:** Avoided by storing only an exact mapping reference on the Relationship and referencing, rather than copying, real intermediate entities/events.
- **Metadata-only causal shortcut:** Prevented because complete mapping still returns RESEARCH_NEEDED when identification is ecological or otherwise inadequate.
- **Partial exposure:** Unbound partial coverage fails; an exact included target set or governed selection rule is required.
- **Ambient context:** Representable through AMBIENT_CONTEXT without fabricating a HappeningType.
- **Multi-stage implementation:** The core four-stage temporal contract is enforceable; claim-specific intermediate references remain optional/conditional.
- **Ontology bloat:** Conditional B rejects Drivers or HappeningTypes created solely as plumbing.
- **Too generic to validate:** Route-specific requirements, exact levels, exposure definition, coverage and temporal checks keep the contract bounded.
- **Ignored by consumers:** Future validators and execution consumers must fail closed; display-only handling is insufficient for execution.
- **Impossible migration:** 13 of 38 rows need no cross-level migration; blocked/research/network-dependent rows remain safely unmigrated.
