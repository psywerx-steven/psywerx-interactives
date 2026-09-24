# RDS contract option comparison

### Option A — REJECT_AS_UNIVERSAL_ARCHITECTURE

Worked: Clear for RDS-0006 and a single exact PSY-078 difference rule; Strong deterministic consumer contract.

Failed: Collapses legitimate metric/context variants; Pressures underdefined and estimated constructs into false determinism; Duplicates application context or embeds it as universal identity; Produces excessive not-applicable fields.

### Option B — VIABLE_BUT_INCOMPLETE_ALONE

Worked: Separates construct, computation profile, and application binding; Supports exact versions and multiple legitimate variants; Preserves existing DER-V1-SOC-F07-001 additively.

Failed: Needs an explicit zero-profile safe state; Needs strict identity rules to prevent proliferation; Cannot permit default or latest-profile resolution.

### Option C — SAFE_FALLBACK_NOT_SUFFICIENT_ALONE

Worked: Preserves unknown as unknown; Keeps CUL-088 and INS-039 scientifically valid but non-executable; Avoids fabricated formulas.

Failed: Provides no execution architecture for RDS-0006; Leaves well-defined metrics unavailable; Does not solve versioning for future profiles.

### Option B_PLUS_C — RECOMMENDED_ADVISORY

Worked: B defines executable profiles and exact bindings; C is the mandatory default when no eligible governed profile/binding exists; Supports zero, one, or multiple profiles without ambiguity; Maintains a separate WP-PSG-005 causal gate.

Failed: Adds consumer verbosity; Requires governance discipline and registry validation; Does not itself resolve any missing derivation or causal-source case.

## Qualitative decision matrix

| Criterion | A | B | C | B+C |
| --- | --- | --- | --- | --- |
| Scientific fidelity | mixed | strong | strong | strong |
| Determinism | strong | strong | not applicable | strong |
| Context specificity | weak | strong | strong | strong |
| Versioning | strong | strong | simple | strong |
| Latent constructs | weak | strong with typed profiles | strong | strong with typed profiles |
| Migration safety | weak | strong | strong | strong |
| Profile proliferation risk | high | medium if unchecked | none | controlled by identity rules |
| Consumer clarity | mixed | strong | strong | strong |
| Causal firewall | strong | strong | strong | strong |
| WP-PSG-005 compatibility | weak | strong | defers | strong |

## Skeptical architecture review

- **Overconstraint:** A turns context-specific and estimated constructs into one universal formula.
- **Profile explosion:** B requires the identity rules in the companion document and registry-level duplicate review.
- **Semantic drift:** profile definitions must cite an immutable RDS definition hash and never redefine the construct.
- **Version ambiguity:** exact profile and binding versions are mandatory; `latest` is prohibited.
- **False determinism:** estimation and measurement profiles remain typed and may not execute as deterministic derivations.
- **Migration instability:** existing IDs and lineage remain stable; additive wrappers precede any governed migration.
- **Consumer complexity:** B+C is more explicit, but the added fields expose rather than hide real ambiguity.
- **Causal leakage:** profile governance never changes `causalSourceEligible=false`; WP-PSG-005 remains separate.
- **Rollback:** removing a test/additive wrapper returns the repository to the current non-executable safe state without rewriting the RDS.
