# INF-F03 entity and RDS review

Audit AUD-INF-F03-AE-V1-20260906-001; frozen main `164d938bcd4bbd7e8c48c8128cacd6e64ff0287a`. Candidate-only recommendations; no scientific approval or activation.

All canonical fields, aliases/crosswalks and incident records are frozen in the [generalized baseline](../../../../reports/actions-events-v1/INF-F03-pilot-baseline/INF-F03_baseline.json). Nulls remain null.

## INF-010 — Decision-Relevant Information Completeness

Ratio over PRESENT_INFORMATION and DECISION_INFORMATION_REQUIREMENT_SET. No canonical constituent Driver IDs; requirement-set denominator/weights/update window must be declared. Mechanism/indicators reuse ambiguity language: record tension, do not repair. Outgoing REL-INF-007 and incoming REL-INF-008 need heightened review.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "commonMisinterpretations": "Treating information completeness as a universal effect or as identical to the recipient’s resulting perception.",
  "constituentSpecifications": [
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "PRESENT_INFORMATION",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "DECISION_INFORMATION_REQUIREMENT_SET",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    }
  ],
  "dataType": "Magnitude / level",
  "definition": "Proportion of decision-relevant facts, alternatives, conditions, and limitations included in a message.",
  "derivationLogic": "Calculate coverage of the specified decision-information requirement set, including weighting and missing-information treatment.",
  "derivationType": "RATIO",
  "directManipulability": "VIA_CONSTITUENTS",
  "entitySubtype": "RELATIONAL_DERIVED_STATE",
  "entityType": "RELATIONAL_DERIVED_STATE",
  "evidenceNotes": "Representative evidence supports behavioral relevance, but message-design effects are usually heterogeneous and often small. Ambiguity is not identical to risk: risk may involve known probabilities, while ambiguity involves missing or poorly specified probabilities/information.",
  "evidenceStrength": "Moderate",
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-010",
  "indicators": [
    "Unknown probability of an outcome",
    "missing source details",
    "unclear operational criteria."
  ],
  "keySources": [
    "SRC-424",
    "SRC-428",
    "SRC-429"
  ],
  "layer": "Informational",
  "likelyDownstreamInfluences": [
    "Comprehension",
    "perceived uncertainty",
    "confidence",
    "decision quality"
  ],
  "likelyUpstreamInfluences": [
    "Language",
    "editing",
    "evidence uncertainty",
    "translation"
  ],
  "measurementAssessmentMethods": "Structured content analysis; message audit; randomized message experiment; exposure-log linkage; expert coding",
  "measurementCaveats": "Content coding can be subjective; intended message properties may differ from what recipients perceive; effects are context dependent.",
  "mechanism": "Ambiguity alters confidence and perceived risk, can increase hesitation or avoidance, and encourages inference from other cues.",
  "moderatorsBoundaryConditions": "Prior beliefs; literacy and numeracy; culture; task stakes; attention; channel; repetition; source; time pressure",
  "modifiability": "High",
  "name": "Decision-Relevant Information Completeness",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Persists until message revision",
  "polarityDirection": "Higher values = greater information completeness unless a categorical representation is used.",
  "primaryFamilyId": "INF-F03",
  "ratioSpecification": {
    "denominator": "specified decision-information requirement set",
    "numerator": "represented decision-relevant requirements"
  },
  "recalculationBehavior": "Recalculate when a required constituent, reference, boundary, formula, or analysis window changes.",
  "relatedFamilyIds": [],
  "representationScale": "0–1 content-coded index; low / moderate / high; domain-specific continuous measure",
  "scopeRequirements": "Specify requirement set, evidence universe, weights, denominator, scope, and update behavior.",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_7_Informational_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Information Completeness × source disclosure",
    "Information Completeness × prior belief",
    "Information Completeness × audience capability"
  ],
  "uncertaintyPropagation": "Preserve and report constituent uncertainty; use analytic propagation or simulation when the selected operationalization supports it, otherwise note uncertainty qualitatively.",
  "volatility": "Moderate"
}
```

Derivation version: no per-record version identifier; freeze by baseline record hash, not an invented formula version. Calculation window is a scope requirement, not a supplied numeric window. Temporal and mechanistic independence of causal use are NOT_CONFIRMED. Uncertainty propagation remains as governed; operationalization is not selected.

## INF-011 — Information-Set Contradiction

Claim-set/contradiction-rule derivation. Incompatible clear propositions need not be ambiguous. Same text can inflate score association; no fixed calculation window/version selected. Outgoing REL-INF-009 is a heightened-review flag, not newly created exogenous agency.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "commonMisinterpretations": "Treating internal message contradiction as a universal effect or as identical to the recipient’s resulting perception.",
  "constituentSpecifications": [
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "CLAIM_SET",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "CONTRADICTION_RULE",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    }
  ],
  "dataType": "Magnitude / level",
  "definition": "Exposure to mutually inconsistent claims, recommendations, estimates, or causal accounts.",
  "derivationLogic": "Evaluate contradiction relations among the specified claims or information items using an explicit logical or semantic rule.",
  "derivationType": "CLAIM_RELATION",
  "directManipulability": "VIA_CONSTITUENTS",
  "entitySubtype": "RELATIONAL_DERIVED_STATE",
  "entityType": "RELATIONAL_DERIVED_STATE",
  "evidenceNotes": "Representative evidence supports behavioral relevance, but message-design effects are usually heterogeneous and often small. The independent behavioral effect of contradiction is less standardized than framing or repetition; consequences depend strongly on trust and prior beliefs.",
  "evidenceStrength": "Moderate",
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-011",
  "indicators": [
    "Two agencies issue incompatible guidance",
    "experts offer divergent estimates",
    "repeated reports reverse recommendations."
  ],
  "keySources": [
    "SRC-429",
    "SRC-428",
    "SRC-434"
  ],
  "layer": "Informational",
  "likelyDownstreamInfluences": [
    "Comprehension",
    "perceived uncertainty",
    "confidence",
    "decision quality"
  ],
  "likelyUpstreamInfluences": [
    "Language",
    "editing",
    "evidence uncertainty",
    "translation"
  ],
  "measurementAssessmentMethods": "Structured content analysis; message audit; randomized message experiment; exposure-log linkage; expert coding",
  "measurementCaveats": "Content coding can be subjective; intended message properties may differ from what recipients perceive; effects are context dependent.",
  "mechanism": "Conflict increases uncertainty and comparison burden, can reduce confidence or trust, and may push people toward pre-existing beliefs or simpler heuristics.",
  "moderatorsBoundaryConditions": "Prior beliefs; literacy and numeracy; culture; task stakes; attention; channel; repetition; source; time pressure",
  "modifiability": "High",
  "name": "Information-Set Contradiction",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Persists until message revision",
  "polarityDirection": "Higher values = greater internal message contradiction.",
  "primaryFamilyId": "INF-F03",
  "recalculationBehavior": "Recalculate when a required constituent, reference, boundary, formula, or analysis window changes.",
  "relatedFamilyIds": [],
  "representationScale": "0–1 content-coded index; low / moderate / high; domain-specific continuous measure",
  "scopeRequirements": "Specify claim set, contradiction relation, scope, uncertainty treatment, and update behavior.",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_7_Informational_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Internal Message Contradiction × source disclosure",
    "Internal Message Contradiction × prior belief",
    "Internal Message Contradiction × audience capability"
  ],
  "uncertaintyPropagation": "Preserve and report constituent uncertainty; use analytic propagation or simulation when the selected operationalization supports it, otherwise note uncertainty qualitatively.",
  "volatility": "Moderate"
}
```

Derivation version: no per-record version identifier; freeze by baseline record hash, not an invented formula version. Calculation window is a scope requirement, not a supplied numeric window. Temporal and mechanistic independence of causal use are NOT_CONFIRMED. Uncertainty propagation remains as governed; operationalization is not selected.

## INF-012 — Message Ambiguity

Definition concerns materially different interpretations of wording/structure; some inherited indicators instead concern unknown probabilities/missing information. Keep linguistic ambiguity separate from uncertainty and omission.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "commonMisinterpretations": "Treating message ambiguity as a universal effect or as identical to the recipient’s resulting perception.",
  "dataType": "Magnitude / level",
  "definition": "Degree to which message wording or structure permits multiple materially different interpretations.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Representative evidence supports behavioral relevance, but message-design effects are usually heterogeneous and often small. Ambiguity is not identical to risk: risk may involve known probabilities, while ambiguity involves missing or poorly specified probabilities/information.",
  "evidenceStrength": "Moderate",
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-012",
  "indicators": [
    "Unknown probability of an outcome",
    "missing source details",
    "unclear operational criteria."
  ],
  "keySources": [
    "SRC-424",
    "SRC-428",
    "SRC-429"
  ],
  "layer": "Informational",
  "likelyDownstreamInfluences": [
    "Comprehension",
    "perceived uncertainty",
    "confidence",
    "decision quality"
  ],
  "likelyUpstreamInfluences": [
    "Language",
    "editing",
    "evidence uncertainty",
    "translation"
  ],
  "measurementAssessmentMethods": "Structured content analysis; message audit; randomized message experiment; exposure-log linkage; expert coding",
  "measurementCaveats": "Content coding can be subjective; intended message properties may differ from what recipients perceive; effects are context dependent.",
  "mechanism": "Ambiguity alters confidence and perceived risk, can increase hesitation or avoidance, and encourages inference from other cues.",
  "moderatorsBoundaryConditions": "Prior beliefs; literacy and numeracy; culture; task stakes; attention; channel; repetition; source; time pressure",
  "modifiability": "High",
  "name": "Message Ambiguity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Persists until message revision",
  "polarityDirection": "Higher values = greater message ambiguity.",
  "primaryFamilyId": "INF-F03",
  "relatedFamilyIds": [],
  "representationScale": "0–1 content-coded index; low / moderate / high; domain-specific continuous measure",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_7_Informational_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Message Ambiguity × source disclosure",
    "Message Ambiguity × prior belief",
    "Message Ambiguity × audience capability"
  ],
  "volatility": "Moderate"
}
```

## INF-013 — Message Conceptual Complexity

Definition includes syntactic depth alongside conceptual interactions, overlapping INF-077. Conceptual-only operationalization unresolved; do not use sentence length/grade level as the construct.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "commonMisinterpretations": "Treating message complexity as a universal effect or as identical to the recipient’s resulting perception.",
  "dataType": "Magnitude / level",
  "definition": "Structural and conceptual complexity of a message, including syntactic depth, dependency load, and number of interacting propositions.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Representative evidence supports behavioral relevance, but message-design effects are usually heterogeneous and often small. Simplification can improve comprehension but may remove nuance; optimal complexity depends on expertise and task.",
  "evidenceStrength": "Moderate",
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-013",
  "indicators": [
    "Dense legal language",
    "unexplained acronyms",
    "multi-clause instructions",
    "highly technical risk descriptions."
  ],
  "keySources": [
    "SRC-425",
    "SRC-426",
    "SRC-427"
  ],
  "layer": "Informational",
  "likelyDownstreamInfluences": [
    "Comprehension",
    "perceived uncertainty",
    "confidence",
    "decision quality"
  ],
  "likelyUpstreamInfluences": [
    "Language",
    "editing",
    "evidence uncertainty",
    "translation"
  ],
  "measurementAssessmentMethods": "Structured content analysis; message audit; randomized message experiment; exposure-log linkage; expert coding",
  "measurementCaveats": "Content coding can be subjective; intended message properties may differ from what recipients perceive; effects are context dependent.",
  "mechanism": "Higher processing demands can reduce comprehension, increase errors, and shift reliance toward simpler cues or prior beliefs.",
  "moderatorsBoundaryConditions": "Prior beliefs; literacy and numeracy; culture; task stakes; attention; channel; repetition; source; time pressure",
  "modifiability": "High",
  "name": "Message Conceptual Complexity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Persists until message revision",
  "polarityDirection": "Higher values = greater message complexity.",
  "primaryFamilyId": "INF-F03",
  "relatedFamilyIds": [],
  "representationScale": "0–1 content-coded index; low / moderate / high; domain-specific continuous measure",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_7_Informational_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Message Complexity × source disclosure",
    "Message Complexity × prior belief",
    "Message Complexity × audience capability"
  ],
  "volatility": "Moderate"
}
```

## INF-014 — Message–Audience Readability

FIT inputs INF-077, INF-053, MESSAGE_REPRESENTATION, AUDIENCE_READING_CAPABILITY, AUDIENCE_PRIOR_KNOWLEDGE. Both causal incoming edges need independence checks. Readability is not comprehension performance. Shared language/audience inputs prohibit aggregate plus constituent propagation.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "commonMisinterpretations": "Treating message readability as a universal effect or as identical to the recipient’s resulting perception.",
  "constituentSpecifications": [
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": "INF-077",
      "externalParameterType": null,
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": "INF-053",
      "externalParameterType": null,
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "MESSAGE_REPRESENTATION",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "AUDIENCE_READING_CAPABILITY",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "AUDIENCE_PRIOR_KNOWLEDGE",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    }
  ],
  "dataType": "Magnitude / level",
  "definition": "Ease with which the language and layout of a message can be decoded by its intended audience.",
  "derivationLogic": "Evaluate audience-relative decoding and initial-interpretation fit from surface-linguistic demand, representation, language accessibility, reading capabilities, and relevant prior knowledge.",
  "derivationType": "FIT",
  "directManipulability": "VIA_CONSTITUENTS",
  "entitySubtype": "RELATIONAL_STATE",
  "entityType": "RELATIONAL_DERIVED_STATE",
  "evidenceNotes": "Representative evidence supports behavioral relevance, but message-design effects are usually heterogeneous and often small. Simplification can improve comprehension but may remove nuance; optimal complexity depends on expertise and task.",
  "evidenceStrength": "Moderate",
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-014",
  "indicators": [
    "Dense legal language",
    "unexplained acronyms",
    "multi-clause instructions",
    "highly technical risk descriptions."
  ],
  "keySources": [
    "SRC-425",
    "SRC-426",
    "SRC-427"
  ],
  "layer": "Informational",
  "likelyDownstreamInfluences": [
    "Comprehension",
    "perceived uncertainty",
    "confidence",
    "decision quality"
  ],
  "likelyUpstreamInfluences": [
    "Language",
    "editing",
    "evidence uncertainty",
    "translation"
  ],
  "measurementAssessmentMethods": "Structured content analysis; message audit; randomized message experiment; exposure-log linkage; expert coding",
  "measurementCaveats": "Content coding can be subjective; intended message properties may differ from what recipients perceive; effects are context dependent.",
  "mechanism": "Higher processing demands can reduce comprehension, increase errors, and shift reliance toward simpler cues or prior beliefs.",
  "moderatorsBoundaryConditions": "Prior beliefs; literacy and numeracy; culture; task stakes; attention; channel; repetition; source; time pressure",
  "modifiability": "High",
  "name": "Message–Audience Readability",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Persists until message revision",
  "polarityDirection": "Higher values = greater message readability unless a categorical representation is used.",
  "primaryFamilyId": "INF-F03",
  "recalculationBehavior": "Recalculate when a required constituent, reference, boundary, formula, or analysis window changes.",
  "relatedFamilyIds": [],
  "representationScale": "0–1 content-coded index; low / moderate / high; domain-specific continuous measure",
  "scopeRequirements": "Specify message, audience, channel and layout, reading capability, prior knowledge, and fit rule.",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_7_Informational_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Message Readability × source disclosure",
    "Message Readability × prior belief",
    "Message Readability × audience capability"
  ],
  "uncertaintyPropagation": "Preserve and report constituent uncertainty; use analytic propagation or simulation when the selected operationalization supports it, otherwise note uncertainty qualitatively.",
  "volatility": "Moderate"
}
```

Derivation version: no per-record version identifier; freeze by baseline record hash, not an invented formula version. Calculation window is a scope requirement, not a supplied numeric window. Temporal and mechanistic independence of causal use are NOT_CONFIRMED. Uncertainty propagation remains as governed; operationalization is not selected.

## INF-015 — Claim Uncertainty Disclosure

Disclosure is information about uncertainty, not uncertainty itself, recipient perception, trust or calibrated confidence. Explicit interval insertion can change the message property without establishing downstream benefits.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "commonMisinterpretations": "Treating uncertainty disclosure as a universal effect or as identical to the recipient’s resulting perception.",
  "dataType": "Other structured type",
  "definition": "Explicit information about the limits, ranges, confidence, or uncertainty attached to a claim, estimate, or forecast.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Representative evidence supports behavioral relevance, but message-design effects are usually heterogeneous and often small. Effects on trust are not uniformly negative; wording, source, stakes, numeracy, and type of uncertainty matter.",
  "evidenceStrength": "Moderate",
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-015",
  "indicators": [
    "Forecast ranges",
    "'low confidence' intelligence judgments",
    "explicit limitations or error bounds."
  ],
  "keySources": [
    "SRC-428",
    "SRC-424",
    "SRC-429"
  ],
  "layer": "Informational",
  "likelyDownstreamInfluences": [
    "Comprehension",
    "perceived uncertainty",
    "confidence",
    "decision quality"
  ],
  "likelyUpstreamInfluences": [
    "Language",
    "editing",
    "evidence uncertainty",
    "translation"
  ],
  "measurementAssessmentMethods": "Structured content analysis; message audit; randomized message experiment; exposure-log linkage; expert coding",
  "measurementCaveats": "Content coding can be subjective; intended message properties may differ from what recipients perceive; effects are context dependent.",
  "mechanism": "Uncertainty disclosure can change perceived credibility, confidence, risk judgments, and action thresholds by altering how definitive the information appears.",
  "moderatorsBoundaryConditions": "Prior beliefs; literacy and numeracy; culture; task stakes; attention; channel; repetition; source; time pressure",
  "modifiability": "High",
  "name": "Claim Uncertainty Disclosure",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Persists until message revision",
  "polarityDirection": "Higher values = greater uncertainty disclosure unless a categorical representation is used.",
  "primaryFamilyId": "INF-F03",
  "relatedFamilyIds": [],
  "representationScale": "Explicit categorical coding plus attribute-specific dimensions",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_7_Informational_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Uncertainty Disclosure × source disclosure",
    "Uncertainty Disclosure × prior belief",
    "Uncertainty Disclosure × audience capability"
  ],
  "volatility": "Moderate"
}
```

## INF-077 — Message Surface-Linguistic Complexity

Multidimensional objective lexical/syntactic/morphological features. Blocked mechanism/modifiability/etc remain null. Research of reversible text edits does not resolve canonical blocked fields. Fewer words alone is not lower complexity.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "blockedFields": [
    "mechanism",
    "modifiability",
    "volatility",
    "timeScaleOfChange",
    "onsetCausalLag",
    "persistenceRecovery",
    "measurementAssessmentMethods",
    "observability",
    "evidenceStrength",
    "evidenceNotes",
    "keySources"
  ],
  "commonMisinterpretations": null,
  "dataType": "Multidimensional",
  "definition": "The degree of objective surface-language complexity in a specified message arising from vocabulary rarity or specialization, syntactic depth, morphological complexity, sentence structure, and comparable linguistic decoding features, independent of the audience’s resulting comprehension.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": null,
  "evidenceStrength": null,
  "family": "Clarity, Complexity & Completeness",
  "id": "INF-077",
  "indicators": [],
  "keySources": [],
  "layer": "Informational",
  "likelyDownstreamInfluences": [],
  "likelyUpstreamInfluences": [],
  "measurementAssessmentMethods": null,
  "measurementCaveats": "Do not substitute one grade-level formula for the full construct. Keep conceptual complexity, audience-language fit, readability, comprehension, and cognitive load distinct.",
  "mechanism": null,
  "metadataStatus": "PARTIAL_GOVERNED_PREVIEW",
  "moderatorsBoundaryConditions": null,
  "modifiability": null,
  "name": "Message Surface-Linguistic Complexity",
  "observability": null,
  "onsetCausalLag": [],
  "persistenceRecovery": null,
  "polarityDirection": "Multidimensional representation; no universal high–low behavioral interpretation.",
  "primaryFamilyId": "INF-F03",
  "relatedFamilyIds": [],
  "representationScale": "Multidimensional profile of lexical frequency or familiarity, syntactic depth, dependency length, morphological complexity, sentence structure, and related features.",
  "source": {
    "decisionRecord": "https://app.notion.com/p/3cdf827a3d15815897b1fb28cfa20fe5",
    "specification": "_migration_handoff_v0.3",
    "status": "GOVERNED_PREVIEW"
  },
  "timeScaleOfChange": [],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [],
  "volatility": null
}
```

## RDS-0001 — Message Cohesion

CLAIM_RELATION over MESSAGE_ELEMENTS/MESSAGE_ELEMENT_RELATIONS. Missing operational segmentation/weight/normalization/window/version and blocked metadata stay unresolved. Cohesion, coherence and comprehension differ. No incident causal edge; do not invent one.

```json
{
  "aliases": [],
  "associatedLayers": [
    "Informational"
  ],
  "blockedFields": [
    "mechanism",
    "modifiability",
    "volatility",
    "timeScaleOfChange",
    "onsetCausalLag",
    "persistenceRecovery",
    "measurementAssessmentMethods",
    "observability",
    "evidenceStrength",
    "evidenceNotes",
    "keySources"
  ],
  "commonMisinterpretations": null,
  "constituentSpecifications": [
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "MESSAGE_ELEMENTS",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "MESSAGE_ELEMENT_RELATIONS",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    }
  ],
  "dataType": "Magnitude / level",
  "definition": "The degree to which explicit lexical, referential, logical, causal, and discourse links connect propositions or sections within a specified non-narrative message so that relationships among ideas are recoverable from the information object.",
  "derivationLogic": "Compute or assess the governed pattern and strength of lexical, referential, logical, causal, and discourse relations among the specified message elements.",
  "derivationType": "CLAIM_RELATION",
  "directManipulability": "VIA_CONSTITUENTS",
  "entitySubtype": "RELATIONAL_DERIVED_STATE",
  "entityType": "RELATIONAL_DERIVED_STATE",
  "evidenceNotes": null,
  "evidenceStrength": null,
  "family": "Clarity, Complexity & Completeness",
  "id": "RDS-0001",
  "indicators": [],
  "keySources": [],
  "layer": "Informational",
  "likelyDownstreamInfluences": [],
  "likelyUpstreamInfluences": [],
  "measurementAssessmentMethods": null,
  "measurementCaveats": null,
  "mechanism": null,
  "metadataStatus": "PARTIAL_GOVERNED_PREVIEW",
  "moderatorsBoundaryConditions": null,
  "modifiability": null,
  "name": "Message Cohesion",
  "observability": null,
  "onsetCausalLag": [],
  "persistenceRecovery": null,
  "polarityDirection": "Higher values = stronger recoverable linkage among the specified message elements.",
  "primaryFamilyId": "INF-F03",
  "recalculationBehavior": "Recalculate when a required constituent, reference, boundary, formula, or analysis window changes.",
  "relatedFamilyIds": [],
  "representationScale": "Multidimensional cohesion profile over a specified message and relation set.",
  "scopeRequirements": "Specify message boundary, element segmentation, relation types, weighting, normalization, missing-link treatment, and update rule.",
  "source": {
    "decisionRecord": "https://app.notion.com/p/3cdf827a3d15815897b1fb28cfa20fe5",
    "specification": "_migration_handoff_v0.3",
    "status": "GOVERNED_PREVIEW"
  },
  "timeScaleOfChange": [],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [],
  "uncertaintyPropagation": "Preserve and report constituent uncertainty; propagate analytically or by simulation when supported, otherwise note it qualitatively.",
  "volatility": null
}
```

Derivation version: no per-record version identifier; freeze by baseline record hash, not an invented formula version. Calculation window is a scope requirement, not a supplied numeric window. Temporal and mechanistic independence of causal use are NOT_CONFIRMED. Uncertainty propagation remains as governed; operationalization is not selected.
