# Focused architecture review

Status: **PROPOSAL / NON_PRODUCTION**. Architecture decisions remain **PENDING**. Accessed 2026-09-06. Machine-readable citations and access levels are in [SOURCES.json](SOURCES.json). These sources inform representation; they do not approve PSYWERX scientific claims.

The strongest common pattern is to distinguish a reusable description, a particular happening, a scoped assertion about consequences, and the evidence/provenance for that assertion. None of the reviewed approaches supplies PSYWERX's human-governance policy, Driver/RDS rules, or a ready-made cross-Layer catalog.

## Useful patterns and limits

| Source | Problem solved and idea to borrow | PSYWERX limit / do not adopt |
|---|---|---|
| AE-SRC-001, [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) | Classes differ from individuals; omitted facts can remain unknown. Use separate type and occurrence IDs. | Do not replace JSON validation with OWL reasoning or equate logical entailment with empirical evidence. |
| AE-SRC-002, [SOSA/SSN](https://www.w3.org/TR/vocab-ssn/) | Separate procedure, actuation, observation, property, and result. Reuse action identity across episodes. | Its device-centered cardinalities do not fit every human action or natural process. An observed result is not proof of every alleged consequence. |
| AE-SRC-003, [OWL-Time 2017](https://www.w3.org/TR/2017/REC-owl-time-20171019/) | Represent instants, intervals, duration, reference time, and overlap explicitly. | Do not infer causality from ordering or require precise timestamps when unknown. Recurrence/exposure patterns still need a PSYWERX profile. |
| AE-SRC-004, [ECTO](https://github.com/EnvironmentOntology/environmental-exposure-ontology) | Compose an exposure from recipient, stressor, route, and medium. | Do not import its precomposed classes or treat organism-centered exposure definitions as sufficient for every institution or network. |
| AE-SRC-005, [PROV-O](https://www.w3.org/TR/prov-o/) | Attribute a revision to an activity, agent, inputs, and method; qualify provenance relations. | PROV's influence and derivation are not PSYWERX causal assertions. Good provenance does not establish truth. |
| AE-SRC-006, [SEPIO](https://sepio-framework.github.io/sepio-linkml/EvidenceLine/) | Preserve proposition-specific evidence lines and distinguish support direction from strength. | Do not import numeric evidence scores, clinical variant categories, or duplicate statement encodings. Use current model documentation, not the outdated legacy OWL model. |
| AE-SRC-007, [Pearl 2009](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf) | Make causal questions, assumptions, and model-based results explicit. | PSYWERX's incomplete catalog cannot be interpreted as a fully specified structural causal model. Missing catalog edges are coverage gaps, not zero-effect assumptions. |
| AE-SRC-008, [VanderWeele 2009](https://pubmed.ncbi.nlm.nih.gov/19806059/) | Distinguish effect variation across moderator strata from effects of intervening on both variables. | Abstract-only support warrants this conceptual distinction, not implementation of the paper's estimators. |
| AE-SRC-009, [ASA 2016](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf) | Preserve uncertainty and reporting context alongside statistical results. | Do not interpret nonsignificance as no effect, significance as importance, or a p-value as claim confidence. |

## Design conclusions recommended for this proposal

These are PSYWERX design inferences from the comparison, not statements that outside standards govern PSYWERX.

1. Use three scientific objects: a reusable Action/Event Type, an Occurrence/Exposure Episode, and a contextual Effect Assertion. Keep Intervention identifiable through compatibility/profile semantics. An episode can be observed without any causal effect being established.
2. Store origin tags separately from targets. Human intentionality, actor-relative control, and location relative to a system boundary are independent fields. Do not infer statistical exogeneity from an external origin.
3. Keep source-level evidence findings before synthesis. A finding's design, disposition, population, measure, limitations, and dataset dependence must survive disagreement with the overall synthesis. Keep extraction, synthesis, model inference, and hypothesis production distinguishable.
4. Represent a changed property separately from its transformation: for example variability/decrease, lag/lengthen, or functional shape/cyclic. Contextual direction avoids a single sign falsely standing for an entire cycle or nonlinear response.
5. Keep relationship modification tied to an exact edge. If the event changes moderator Driver M, and a separate assertion describes M's modification of A→B, link the mechanisms and suppress duplicate contribution in any later execution plan.
6. Use the existing Driver/RDS constraints for every kind of happening. Rebranding an intervention as an event cannot justify direct manipulation of an RDS or causal propagation of a formula.
7. Permit governed eligibility, research completeness, evidence confidence, and quantitative/recommendation eligibility to differ. The prototype may demonstrate checks; it cannot grant real approval.

The pragmatic alternative to three objects is a single catalog record containing identity, episodes, and effects. It is cheaper initially but duplicates actions across populations and permits occurrence evidence to bleed into efficacy claims. A full upper-ontology/RDF migration offers interoperability but adds commitments, reasoner behavior, and migration costs outside the task. The proposed normalized JSON profile preserves current V1 assets while retaining future crosswalk options.

## Reproducible review log and stopping rule

| Question | Search/access route | Selection and outcome |
|---|---|---|
| How to distinguish reusable type and happening? | Direct W3C OWL Primer and SOSA/SSN documentation | Included primary standards; reviewed class/individual, procedure/actuation/result sections. |
| How to describe duration and ongoing exposure? | Direct W3C OWL-Time; ECTO maintainer README | Included 2017 pinned Recommendation and compositional exposure pattern. Latest OWL-Time URL resolved to a 2022 draft, so version status is explicit. |
| How to attach evidence and its production history? | PROV-O; legacy SEPIO repository followed to current maintainer documentation | Included current SEPIO Statement/EvidenceLine pages; legacy warning recorded rather than silently adopting outdated schema. |
| What separates association, causal assumptions, and moderator manipulation? | Author-hosted Pearl PDF; search concepts `VanderWeele distinction interaction effect modification 2009` | Reviewed selected full-text Pearl sections and the PubMed abstract/metadata for VanderWeele. Detailed estimation implementation excluded. |
| How to preserve null results and uncertainty? | Search concepts `ASA statement p values statistical significance 2016 six principles`; direct ASA PDF | Included original association announcement. Secondary explanations and discussion forums were excluded. |

This was a focused architecture review, not a systematic scientific review. Primary public standards, maintainer explanations, original method authors, and a methods body's own statement were preferred. Inclusion required a direct connection to a design decision and an inspectable passage/section. Sources about biological intervention efficacy, broad news, and taxonomy population were outside scope.

Nine sources cover the main competing structural choices. Further reading is not needed to choose a provisional normalized prototype. Remaining uncertainty concerns PSYWERX governance choices and implementation profile details, not an authorization to populate science. BFO's public landing pages were inspected only as discovery material; no substantive BFO claims or alignment are made. Two PMC direct-access attempts encountered verification pages; no conclusions rely on them. No paid access, source registration, or external job was used.
