# PSYWERX Plain-Language Standard v1.0

**Status:** Authoritative content-writing and quality-assurance standard  
**Applies to:** Permanent plain-language content for canonical PSYWERX Drivers  
**Does not modify:** The PSYWERX Driver Schema or canonical taxonomy

## 1. Purpose

PSYWERX plain-language content makes technical Driver constructs usable by intelligent professional practitioners who may not have specialist training in the Driver's source discipline. It must improve comprehension without replacing, weakening, or silently changing scientific meaning.

The target is professional general-audience clarity, not child-level readability. Simpler terminology is valuable only when the same variable, scope, unit, boundaries, and uncertainty survive the simplification.

## 2. Canonical authority

The following remain authoritative:

- canonical Driver ID and name;
- canonical scientific definition;
- ontology Layer and Family;
- technical taxonomy fields, including variable type, representation, mechanism, boundaries, timing, measurement, evidence, and provenance.

Plain-language content is interpretive support attached to a permanent Driver ID. It is not a substitute definition, ontology revision, measurement instrument, causal finding, or scenario assessment.

If plain-language wording conflicts with canonical content, the canonical content wins. The candidate must be revised; canonical content must not be altered to accommodate the candidate.

## 3. Permanent content model

Schema v1.0 recommends exactly three required permanent plain-language content fields and one optional field. These fields are not yet additions to the Driver Schema.

| Field | Status | Purpose |
| --- | --- | --- |
| `plainLanguageLabel` | Required | Supports scanning, navigation, search, compact displays, and rapid recognition of the variable. |
| `plainLanguageExplanation` | Required | Explains what the variable means while preserving its scientifically important scope and boundaries. |
| `analyticQuestion` | Required | Helps a practitioner investigate or assess the Driver state itself. |
| `whatThisDoesNotMean` | Optional | Prevents a predictable high-cost misunderstanding or collapse into a neighboring construct. |

The three required fields have different jobs. Apparent overlap is acceptable when each field remains optimized for its function. `whatThisDoesNotMean` is conditional, not filler; absence should mean that no concise clarification is necessary after review.

## 4. Plain-language label standard

### Preferred form

- Approximately 4–9 words.
- Concrete and immediately interpretable.
- Professional and concise.
- Active where an active rendering is clearer.
- A phrase rather than necessarily a complete sentence.
- It may, but need not, begin with “How.”
- It must still represent the Driver state.

### Avoid

- unnecessary specialist jargon;
- passive construction when a clearer active rendering exists;
- a downstream consequence in place of the Driver;
- a mechanism in place of the Driver;
- a broad topic, actor, entity, or domain in place of a variable;
- evaluative wording that implies high or low is universally desirable;
- invented causal direction.

The label may use words such as “amount,” “level,” “likelihood,” “availability,” “difference,” “scope,” or “configuration” when they make the variable explicit. Do not force a single label template across all representation types.

## 5. Plain-language explanation standard

### Preferred length and purpose

The preferred length is approximately 40–65 words. An explanation may extend toward 80 words only when needed to preserve meaning. Its primary question is:

> What does this variable actually mean?

The explanation need not repeat every caveat already available elsewhere in the canonical Driver record. It must retain the caveats that prevent a material change in meaning.

### Required qualities

Every explanation must:

- preserve variable-state framing;
- preserve important scope conditions;
- explain jargon when possible;
- distinguish the state from an outcome;
- distinguish the state from a mechanism or process;
- distinguish the state from surrounding context;
- preserve multidimensionality where it is material;
- preserve comparison, denominator, or baseline requirements where material;
- preserve probabilistic language;
- preserve population, group, actor, system, place, message, or other unit-of-analysis distinctions;
- preserve important measurement boundaries;
- retain context dependence or nonlinearity when loss would change interpretation;
- avoid invented causal direction;
- avoid universal behavioral consequences;
- avoid case-specific causality;
- avoid scientific claims absent from the canonical ontology.

### Editing priority

When brevity competes with fidelity, use this priority:

1. Same variable.
2. Same unit and scope.
3. Same essential comparison, denominator, configuration, or probability.
4. Same causal stage and boundary from neighboring Drivers.
5. Same important qualifications.
6. Stylistic compactness.

## 6. Mandatory variable-state rule

Every explanation must make clear that the Driver is a variable: an amount, level, degree, rate, probability, magnitude, availability, configuration, profile, prevalence, intensity, condition, duration, category, or other measurable state.

Bad:

> Peer pressure

Better:

> How strongly peers signal or enforce a particular behavior

Bad:

> Technology visibility

Better:

> How visible a user's actions are to other people on the platform

Bad:

> Sleep is important

Better:

> How much sleep a person is getting relative to their need

A topic label alone is insufficient. A benefit statement, warning, or consequence is also insufficient. The wording must expose what can vary.

## 7. Analytic-question standard

The analytic question helps a practitioner investigate or assess the Driver state. Its preferred length is approximately 8–25 words.

### Requirements

- Ask about the Driver itself, not a downstream outcome.
- Preserve a denominator, comparison, reference group, baseline, time window, network boundary, audience, or configuration when material.
- Match the Driver's representation rather than forcing identical syntax.
- Remain portable across scenarios.
- Avoid presuming that a high or low state is desirable.
- Avoid presuming that the Driver is present, causal, or actionable in a specific case.
- End as a question.

### Representation-sensitive patterns

| Representation | Useful question form |
| --- | --- |
| Magnitude or level | How strong is …? |
| Probability | How likely is …? |
| Availability | How available is …? |
| Disparity | How much does X differ across …? |
| Network structure | How often …? / What share …? |
| Configuration | What configuration currently exists? |
| Profile | What pattern or profile is present? |
| Category | Which category applies under the defined classification? |

These are patterns, not mandatory templates. Syntactic diversity is desirable when it improves fit and avoids mechanical repetition.

## 8. Optional `whatThisDoesNotMean`

Use this field when a short boundary statement prevents a likely, material misunderstanding. It is recommended when one or more of the following apply:

- Meaning Preservation Risk is `HIGH`;
- the Driver is commonly confused with another construct;
- ordinary-language simplification could erase an important distinction;
- a nearby ontology Driver appears superficially synonymous;
- the construct commonly attracts causal overclaiming;
- the concept is socially, politically, or ethically easy to overinterpret;
- the state could be confused with an outcome, mechanism, diagnosis, actor, or entity.

Keep it concise. State the boundary directly. Do not use it to repeat the explanation, list every caveat, argue policy, or introduce new claims.

## 9. Causal precision rule

Plain-language simplification may simplify terminology; it must not simplify the causal model. Preserve causal stages and avoid converting a precursor into a consequence.

Canonical causal sequence:

> system allocation → exposure → human reception

Bad simplification:

> How much the algorithm makes people see something

Better simplification:

> How much the system increases an item's distribution or exposure relative to a defined baseline

Never turn:

- opportunity into behavior;
- exposure into effect;
- capability into use;
- disparity into intent;
- susceptibility into determination;
- network position into actual influence;
- availability into consumption;
- physiological state into behavioral outcome;
- information content into audience belief;
- a group-level distribution into an individual trait.

## 10. Cross-Layer parity

Plain-language content must treat all eight Layers as genuine causal conditions. Psychological Drivers must not sound uniquely causal while Biological, Social, Cultural, Physical / Environmental, Institutional / Structural, Informational, and Technological Drivers are reduced to passive background.

Maintain comparable causal seriousness while preserving each Layer's nature-of-variable boundary:

- Biological wording describes bodily states and susceptibilities without determinism.
- Psychological wording describes internal appraisals, valuations, beliefs, or states without treating them as universal explanations.
- Social wording preserves relational, group, and network units.
- Cultural wording preserves shared conventions and aggregate units without essentializing members.
- Physical / Environmental wording preserves external material and spatial conditions rather than converting them into perceptions.
- Institutional / Structural wording preserves rules, distributions, authority, access, and implementation conditions rather than reducing them to personal inconvenience.
- Informational wording preserves properties of content or information environments rather than audience response.
- Technological wording preserves system configuration, capability, and affordance rather than actual use, effectiveness, or behavioral outcome.

## 11. Meaning Preservation Risk rubric

Meaning Preservation Risk measures the difficulty of simplifying a Driver without distorting it. It does not measure whether the Driver itself is socially sensitive, harmful, controversial, or important.

### Risk factors

Assess at least:

- technical construct complexity;
- multidimensionality;
- dependence on measurement definition, denominator, baseline, network boundary, or classification rule;
- counterintuitive meaning;
- common conceptual confusion;
- overlap with nearby Drivers;
- causal-overclaim risk;
- genetic or biological determinism risk;
- cultural essentialism risk;
- institutional or political interpretation risk;
- network-measure interpretation risk;
- algorithmic or AI capability interpretation risk;
- context dependence;
- nonlinear or nonmonotonic interpretation;
- population-versus-individual distinction.

### Categories

| Risk | Definition | Typical indicators | Required treatment |
| --- | --- | --- | --- |
| `LOW` | The variable is comparatively direct, familiar, and bounded; ordinary-language substitution is unlikely to change its meaning. | Mostly unidimensional; obvious unit; limited nearby overlap; low causal-overclaim risk. | Standard-capability candidate, automated checks, and sampled human QA. |
| `MODERATE` | Meaning depends on one or more technical distinctions, context conditions, comparisons, or neighboring constructs that a reasonable simplification could lose. | Important denominator or baseline; some jargon; moderate overlap; unit or direction needs explanation. | High-capability candidate, independent critique, automated semantic checks, and larger sampled human QA. |
| `HIGH` | Simplification has a substantial chance of changing the variable, causal stage, unit, dimensionality, or scientific qualification. | Critical measurement dependence; counterintuitive metric; multidimensional construct; determinism or essentialism risk; network, disparity, cultural, genetic, or AI-capability interpretation risk; strong nearby overlap; nonlinear meaning. | Highest-capability candidate, deep reasoning, independent semantic critique, explicit canonical comparison, nearby-Driver and causal-overclaim checks, and targeted human review. |

### Classification rule

Use holistic expert judgment, supported by recorded risk factors. A single critical factor may justify `HIGH`; several interacting moderate factors may also justify `HIGH`. Do not average away a severe failure mode. When classification is uncertain between two levels, route to the higher level until critique resolves the uncertainty.

Risk may be reassessed after Family review, but it must not be lowered merely because candidate prose sounds fluent.

## 12. Model and reasoning routing

Routing is capability-based and must not depend on a permanent product or model name.

### STANDARD-CAPABILITY PASS

Use for `LOW`-risk Drivers:

- standard high-quality candidate generation;
- automated structural and lexical validation;
- sampled human QA.

### HIGH-CAPABILITY PASS

Use for `MODERATE`-risk Drivers:

- high-capability generation with full canonical context;
- an independent critique pass;
- automated structural and semantic checks;
- larger stratified human QA;
- escalation of unresolved ambiguity.

### MAXIMUM-REASONING / DEEP-REVIEW PASS

Use for `HIGH`-risk Drivers:

- the highest-capability available model;
- maximum or deep reasoning where available;
- an independent second-pass semantic critique that does not inherit the generator's conclusions;
- explicit comparison with the canonical definition and boundaries;
- nearby-Driver confusion review;
- causal-overclaim review;
- targeted human review for the highest-risk subsets and every unresolved item.

Stronger resources are used to improve nuance retention, ambiguity detection, boundary preservation, distinction from neighboring Drivers, and detection of unintended causal claims—not merely polish or tone.

## 13. Required HIGH-risk second-pass critique

Every `HIGH`-risk candidate requires an independent critique. The critic must receive the canonical Driver record, relevant Family boundaries, candidate fields, and nearby Driver names or definitions. It must answer:

1. Does the wording preserve the same variable as the canonical definition?
2. Has any important qualifier disappeared?
3. Has a multidimensional construct been reduced to one dimension?
4. Has susceptibility become determination?
5. Has association become causation?
6. Has opportunity or capability become behavior?
7. Has exposure become effect?
8. Has a network metric become “influence” or “importance”?
9. Has a cultural group-level construct become an individual trait?
10. Has institutional disparity become intent or discrimination without evidence?
11. Has an AI or technology capability become actual use or performance?
12. Has a contextual condition become a psychological state?
13. Has directionality been invented?
14. Has nonlinearity or context dependence disappeared?
15. Is the analytic question assessing the Driver itself?
16. Could the explanation be confused with a neighboring Driver?

The critique records `PASS`, `REVISE`, or `ESCALATE` plus findings. Any material meaning distortion requires revision. An unresolved canonical ambiguity, boundary conflict, or scientific question requires escalation rather than stylistic guessing.

## 14. Automated quality checks

Run automated checks on every candidate. Structural checks may block publication; semantic heuristics flag records for review and must not automatically rewrite substantive wording.

### Identity and source fidelity

- Driver ID exists exactly once in the canonical dataset.
- Candidate canonical name, Layer, Family, and definition match the canonical record.
- Canonical definition is unchanged.
- No candidate is joined by row number or mutable name alone.

### Required content

- All three required plain-language fields are populated.
- Optional `whatThisDoesNotMean` is either concise text or empty/null according to the eventual editorial format.
- No field contains placeholder text or empty meaning.

### Form and length

- Label is approximately 4–9 words, with exceptions flagged.
- Explanation is approximately 40–65 words; 66–80 words is allowed but flagged for necessity review; other lengths are flagged.
- Analytic question is approximately 8–25 words.
- Analytic question ends with a question mark.
- Files decode as UTF-8.
- No local filesystem path is present.

### Semantic heuristics

- Variable-state language or an equivalent measurable construction is present.
- Unsupported deterministic phrases are flagged, including “causes people to,” “makes people,” “determines behavior,” and “guarantees,” unless canonical content explicitly warrants the claim.
- A normalized exact copy or near-copy of the canonical definition is flagged as insufficient simplification.
- Invented source citations, references, identifiers, or evidence claims are flagged.
- Accidental substitution of a nearby Driver's canonical name is flagged.
- Outcome, mechanism, actor/entity, diagnosis, and broad-topic substitutions are flagged.
- Population-to-individual and group-to-member shifts are flagged.

Automated semantic flags are review signals, not proof of error. The system must never silently “fix” a flagged scientific distinction.

## 15. Family-based consistency review

The 105 canonical Families are the primary semantic QA grouping. Review all candidate Drivers in a Family together rather than only in numerical ID order.

For every Family:

- compare all labels and explanations side by side;
- distinguish neighboring constructs;
- maintain consistent terminology for shared dimensions;
- detect identical or near-duplicate explanations;
- detect collapsed distinctions;
- check that analytic questions discriminate between Drivers;
- use Family definition, inclusion rule, exclusion rule, and representative Drivers as boundaries;
- escalate any candidate that appears to belong to a different Driver or Family.

Family review may cause candidate revision or risk escalation. It must not change the canonical taxonomy in this workflow.

## 16. Human-review and approval principles

Manual review is risk-based rather than a requirement to approve all 762 records individually.

- `LOW`: random and stratified sample review after automated and Family QA.
- `MODERATE`: larger stratified review; review every flagged or low-confidence item.
- `HIGH`: review all unresolved or critical-risk items; review all candidates by default unless a governed sampling exception is supported by clean independent critique and high confidence.

Stratify by Layer, Family, risk, data type, and—where useful—evidence strength. Escalate canonical conflicts, material critique findings, unresolved nearby-Driver overlap, unsupported causal language, and reviewer disagreement.

Approval requires canonical fidelity, completed required fields, passed structural checks, resolution of material semantic flags, completed risk-routed critique, Family consistency, cross-Layer parity, and the required human-review disposition.

## 17. Editorial governance metadata

Keep editorial metadata separate from public taxonomy fields until a later schema and publication decision. Recommended metadata includes:

- `meaningPreservationRisk`;
- `generationConfidence`;
- `critiqueStatus`;
- `critiqueFindings`;
- `humanReviewStatus`;
- `reviewerNotes`;
- `plainLanguageVersion`;
- `reviewDate`.

Preferred location: a separate, versioned editorial dataset in the governed analysis layer, keyed by permanent Driver ID. Do not place provisional generation or critique metadata in source workbooks. Do not add it to public Driver JSON or the Driver Schema without explicit governance approval.

## 18. Scenario-layer separation

The future architecture is:

> **CANONICAL TAXONOMY** — stable / scientific  
> ↓  
> **REVIEWED PLAIN-LANGUAGE CONTENT** — stable / governed  
> ↓  
> **SCENARIO CONTEXTUALIZATION** — dynamic / illustrative

Scenario inputs may later include Actor, Behavior / Objective, and Context. Dynamic outputs may include what the Driver means in that setting, why it might matter, a question to investigate, possible indicators, and an important caveat.

Scenario-generated content must:

- never replace the canonical definition;
- never replace reviewed permanent plain-language content;
- never claim the Driver is causal in the actual case;
- be labeled illustrative and hypothesis-generating;
- use canonical Driver meaning as its constraint;
- remain stored or displayed separately from permanent content.

No scenario-specific content belongs in the permanent plain-language production workflow.

## 19. Calibration baseline

The approved ten-Driver calibration established these general style preferences:

- favor direct professional wording over technical restatement;
- make the comparison or variable explicit without beginning every label with “How”;
- translate jargon while retaining critical technical boundaries;
- prefer concrete analytic questions tailored to representation type;
- state probabilistic and group-level qualifications plainly;
- preserve causal stages and distinguish system allocation from effect;
- use `whatThisDoesNotMean` for concise, high-value boundary protection.

INS-075 Differential Enforcement Magnitude is the model example: it states the measurable disparity, preserves the comparison denominator and institutional context, and explicitly avoids converting observed disparity into cause, intent, legality, or moral judgment.

## 20. Versioning and change control

Plain-language content should be versioned independently from the canonical Driver Schema. A content revision must retain the permanent Driver ID and record its standard version, review status, and review date in editorial governance metadata.

Changes to this writing standard require documented governance review. Changes to canonical Driver definitions, Layers, Families, or technical fields are outside this standard and must follow ontology governance.
