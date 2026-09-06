# INF-F03 governed-inactive scientific checkpoint

Audit **AUD-INF-F03-AE-V1-20260906-001**, frozen main
`164d938bcd4bbd7e8c48c8128cacd6e64ff0287a`. Governance decision
`GOV-INF-F03-001-2026-09-06` materializes an exact approved subset as inactive;
activation remains unauthorized.

Start with the [human decision package](INF_F03_GOVERNANCE_DECISION_PACKAGE.md),
then the [completeness and skeptical review](INF_F03_COMPLETENESS_REPORT.md).
The package deliberately retains uncertain claims as research-needed. A
REVIEW_READY record is prepared for review, not scientifically authoritative.

## Deliverables

- [Entity/RDS review](INF_F03_ENTITY_RDS_REVIEW.md): all eight canonical records,
  derivation inputs and interpretation risks; no blocked fields repaired.
- [Existing relationship audit](INF_F03_EXISTING_RELATIONSHIP_AUDIT.md): 14 active
  and two deprecated propositions; six exact revision/retype proposals are in the
  [candidate revision file](../../../../data/candidates/actions-events-v1/INF-F03/revision-proposals.json).
- [Evidence summary](INF_F03_EVIDENCE_SUMMARY.md) and [search log](INF_F03_RESEARCH_LOG.md):
  14 supplemental sources and 15 existing source references checked at the
  recorded access depth, including metadata-only alignment checks. This is a
  structured evidence audit, not a formal systematic review or 29 full-paper reviews.
- [Candidate workspace](../../../../data/candidates/actions-events-v1/INF-F03/workspace.json):
  four Relationship candidates, seven HappeningTypes, seven EffectAssertions,
  and 20 EvidenceAssessments. RI evidence has validated AE source-finding
  [sidecars](../../../../data/candidates/actions-events-v1/INF-F03/relationship-source-findings.json),
  not a production schema extension. No observed occurrences, pathways or moderation created.
- [Four Driver search ledgers](../../../../data/candidates/actions-events-v1/INF-F03/driver-search-ledger.json):
  every Layer, domain and effect property considered; insufficient evidence is not zero.
- [Source registration queue](../../../../data/candidates/actions-events-v1/INF-F03/source-registration-queue.json)
  and [registration manifest](INF_F03_SOURCE_REGISTRATION_MANIFEST.json): three
  required references were verified and registered as `SRC-550`–`SRC-552`; eleven
  remain proposal-only.
- [Human decision record](INF_F03_GOVERNANCE_DECISION_001.md): exact dispositions,
  canonical lineage, scientific boundaries, and explicit activation withholding.
- [Independent activation-readiness audit](INF_F03_ACTIVATION_AUDIT_001.md):
  record-by-record recommendations, dependency order, evidence/source checks,
  practitioner-use separation, and the EA-001 feature-scope enforcement blocker.
- [Manifest](INF_F03_AUDIT_MANIFEST.json),
  [frozen generalized baseline](../../../../reports/actions-events-v1/INF-F03-pilot-baseline/INF-F03_baseline.json),
  and [execution record](EXECUTION.md).

## Scientific review priorities

1. Message content versus audience processing: reading time, comprehension and
   credibility must not silently substitute for Cognitive Load or calibrated confidence.
2. INF-013 and INF-077 overlap: syntactic depth appears in conceptual metadata.
   Choosing a measure cannot resolve an ontology decision.
3. The four RDS are calculations/relations/fit, not independently manipulated causes.
   INF-011 already has outgoing causal use without a recorded incoming causal edge;
   this is an existing exogenous-root risk, not a new candidate effect.
4. Noise decreases some output quantities but not normalized complexity in the
   inspected experiment. Sleep-loss communication effects depend on task/role.
   Simplification can remove information. These findings stay explicit and bounded.
5. Numeric versus verbal uncertainty disclosure can affect source credibility
   differently. The REVIEW_READY proposition is conditional, not a universal sign.

## Reproduce without changing science

```text
python scripts/build_inf_f03_pilot.py
python -m unittest discover -s tests -p test_inf_f03_pilot.py
python -m unittest discover -s tests -p test_inf_f03_activation_audit_001.py
python scripts/validate_inf_f03_pilot.py
```

The renderer accepts reviewed inputs, performs no search and writes only this
pilot's candidate/docs directories. The last command validates committed HEAD in
isolated clones so migration/BIO regeneration cannot mutate the working science.
The generalized runner's frozen output is not a second scientific graph.

All 44 lifecycle-bearing candidate/evidence/revision records are NOT_ELIGIBLE:
12 REVIEW_READY and 32 RESEARCH_NEEDED, including four blocked revision proposals.
The separate hypothesis ledger contains 11 rejected category errors, eight
research questions and one ontology-governance block; it is not a new governed
REJECTED-state catalog.

Twelve new root scientific records are GOVERNED + INACTIVE: one Relationship,
six HappeningTypes, two EffectAssertions, and three EvidenceAssessments. Five
normalized source findings support those exact governed assertions. Candidate
copies and every excluded/research-needed item remain NOT_ELIGIBLE.

Stop after an unmerged PR. No scientific activation, further source registration,
existing-edge replacement, BIO revision, third Family, modeling/ranking algorithm
or deployment.
