# PSY-F07 — Knowledge, Memory & Mental Representation

Audit `AUD-PSY-F07-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All seven complete canonical records and15 RELATED_SEARCH aliases reviewed; no crosswalk entries. Definitions, types/scales, mechanisms, polarity, timing/lag/persistence, modifiability, observability, measurement caveats, sources and upstream/downstream/interaction fields preserved. Zero blocked local fields; no canonical repair.

No local RDS or incident RDS endpoint. DomainKnowledge remains multidimensional Driver; PSY-078 belongs F09. Internal concept maps are not network RDS or scientific Relationships; no direct RDS target.

### PSY-063 — Causal Belief Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Unipolar continuous",
  "definition": "The confidence assigned to a specified proposition that one factor causally influences another.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC151; SRC109.",
  "evidenceStrength": "Moderate",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-063",
  "indicators": [
    "Causal ratings",
    "intervention choice",
    "causal-map edge weight"
  ],
  "keySources": [
    "SRC151",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Guides prediction, responsibility attribution, and selection of actions believed to have leverage.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "Moderate",
  "name": "Causal Belief Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = stronger belief in the specified causal relation.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "0–1 causal probability; low–high causal confidence",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "Low"
}
```

Confidence in one specified causal proposition, not whether the proposition is true or its objective causal magnitude.

Causal-rating response format changes observed judgment; unidirectional versus bidirectional scales are not interchangeable. Correct conditional-probability learning does not guarantee correct causal integration.

Belief after observed outcomes separated from prior confidence and real outcome generation.

Existing veracity→causal-belief mechanism concerns accuracy, whereas target is confidence/strength. No accuracy repair or numerical causal weight.

Boundary references: PSY-003, PSY-116, INF-067. Sources: SRC-CAND-PSY-LAYER-0073, SRC-CAND-PSY-LAYER-0074, SRC151, SRC109.

### PSY-064 — Mental Model Coherence

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which a person's internal representation of a situation forms a connected, noncontradictory account that supports inference.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC151; SRC109.",
  "evidenceStrength": "Moderate",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-064",
  "indicators": [
    "Concept-map structure",
    "inference consistency",
    "explanation coherence"
  ],
  "keySources": [
    "SRC151",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Supports prediction and planning by permitting consistent simulation of relationships and outcomes.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "Moderate",
  "name": "Mental Model Coherence",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often durable; accessibility and confidence can change faster than underlying knowledge.",
  "polarityDirection": "Higher values = more internally coherent representation.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "Low–high coherence; concept-map consistency; model-fit score",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "Low"
}
```

Connected, internally noncontradictory representation supporting inference; internal coherence does not establish external truth.

External concept maps and test performance are imperfect indicators, not direct observations of all internal connections or a real social network.

Learning/organization across sessions versus momentary inference; no assumed instant restructuring.

Concept-mapping learning outcomes do not establish exact internal coherence or complete knowledge organization; STRUCTURE search stays insufficient.

Boundary references: PSY-065, PSY-063. Sources: SRC151, SRC-CAND-PSY-LAYER-0076.

### PSY-065 — Domain Knowledge

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Multidimensional",
  "definition": "The amount and organization of accurate knowledge held about a specified domain.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC151; SRC109.",
  "evidenceStrength": "Strong",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-065",
  "indicators": [
    "Knowledge-test performance",
    "explanation accuracy",
    "expert classification"
  ],
  "keySources": [
    "SRC151",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Improves interpretation, prediction, option generation, and error detection within the domain.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "Moderate",
  "name": "Domain Knowledge",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often durable; accessibility and confidence can change faster than underlying knowledge.",
  "polarityDirection": "Higher values = greater accurate and usable domain knowledge.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "Test score; calibrated knowledge profile; concept coverage and accuracy",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "Low"
}
```

Amount AND organization of accurate domain knowledge, a multidimensional profile, not any retained text.

A recall score can be inaccurate, narrow or disorganized. Selected idea-unit recall is not whole-profile increase; concept-map accuracy and domain coverage must be checked.

Durable knowledge versus current cue accessibility and practice performance; no universal transfer.

Existing feature-scope architecture question applies to multidimensional knowledge; no generic signed whole-construct effect from one score.

Boundary references: PSY-064, PSY-066, PSY-070. Sources: SRC151, SRC109, SRC-CAND-PSY-LAYER-0070, SRC-CAND-PSY-LAYER-0076.

### PSY-066 — Memory Accessibility

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Unipolar continuous",
  "definition": "The readiness with which a specified memory, concept, or association can be retrieved under current cues.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC152; SRC125.",
  "evidenceStrength": "Strong",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-066",
  "indicators": [
    "Recall latency",
    "free-recall probability",
    "accessibility rating"
  ],
  "keySources": [
    "SRC152",
    "SRC125"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Increases the likelihood that retrieved content shapes appraisal, prediction, and choice.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "Moderate",
  "name": "Memory Accessibility",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = faster or more probable retrieval under the specified cue.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "Low–high accessibility; response latency; recall probability",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "High"
}
```

Retrieval readiness of specified material under current cues; probability and latency are canonical indicators but different estimands.

Delayed title-cued recall probability of scored idea units aligns to that specific material/cue. Not storage capacity, general memory ability, knowledge accuracy or all cues.

Five-minute result reverses delayed advantage in primary study; candidate restricted to two-day/one-week tests, not universal persistence.

One bounded delayed-recall effect retained; no unsupported generalization to recognition, all intervals, aging or clinical memory.

Boundary references: PSY-065, PSY-067, PSY-058. Sources: SRC-CAND-PSY-LAYER-0070, SRC-CAND-PSY-LAYER-0071, SRC-CAND-PSY-LAYER-0075, SRC-CAND-PSY-LAYER-0077, SRC-CAND-PSY-LAYER-0079.

### PSY-067 — Familiarity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a stimulus, claim, person, or action feels previously encountered or known.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC125; SRC171.",
  "evidenceStrength": "Strong",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-067",
  "indicators": [
    "Familiarity rating",
    "recognition response",
    "exposure history"
  ],
  "keySources": [
    "SRC125",
    "SRC171"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Can increase fluency, liking, perceived truth, and default acceptance while remaining separable from recollection and accuracy.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "Moderate",
  "name": "Familiarity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often durable; accessibility and confidence can change faster than underlying knowledge.",
  "polarityDirection": "Higher values = stronger feeling of prior exposure or knowing.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "Novel–highly familiar; recognition-familiarity estimate",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "Low"
}
```

Feeling previously encountered/known, not actual repetition, accurate recollection or objective familiarity count.

Subjective familiarity distinguished from ease and recognition accuracy; attribution and expectations matter.

Exposure history and later felt familiarity distinct; frozen weeks/months metadata does not prohibit studying a bounded state but is not repaired.

Reuse repeated-claim identity and existing fluency review; no new universal familiarity effect or belief-truth equivalence.

Boundary references: PSY-061, PSY-066, PSY-003. Sources: SRC125, SRC171, SRC-CAND-PSY-LAYER-0078, SRC-CAND-PSY-LAYER-0079.

### PSY-068 — Memory Confidence

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of confidence that a specified memory or recollection is accurate.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC169; SRC184.",
  "evidenceStrength": "Moderate",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-068",
  "indicators": [
    "Confidence rating",
    "confidence–accuracy calibration",
    "report persistence"
  ],
  "keySources": [
    "SRC169",
    "SRC184"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Changes reliance on recalled information and willingness to revise or communicate it.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "Moderate",
  "name": "Memory Confidence",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater subjective confidence in memory accuracy.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "0–100% confidence; low–high certainty",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "Low"
}
```

Confidence that a particular recollection is accurate, not actual accuracy or confidence in future learning.

Current and retrospective certainty differ; initial uncontaminated lineup confidence and post-feedback confidence cannot be pooled. A future recall prediction is not this Driver.

Immediate identification certainty versus later contaminated reporting; no timeless confidence-accuracy equivalence.

Feedback effect remains research-needed until exact current-confidence contrast is extracted. SRC184 stored PMID wrong; intended source documented without repair.

Boundary references: PSY-116, PSY-003. Sources: SRC169, SRC184, SRC-CAND-PSY-LAYER-0072, SRC-CAND-PSY-LAYER-0070.

### PSY-069 — Prior-Belief Congruence

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Equating familiarity, accessibility, confidence, and accuracy, or treating a mental model as an objective system description.",
  "dataType": "Bipolar continuous",
  "definition": "The degree to which new information is perceived as consistent with the person's existing beliefs or expectations.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC153; SRC117.",
  "evidenceStrength": "Strong",
  "family": "Knowledge, Memory & Mental Representation",
  "id": "PSY-069",
  "indicators": [
    "Congruence rating",
    "selective recall",
    "acceptance or counterarguing"
  ],
  "keySources": [
    "SRC153",
    "SRC117"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Prediction",
    "interpretation",
    "planning",
    "confidence",
    "causal attribution",
    "choice"
  ],
  "likelyUpstreamInfluences": [
    "Learning",
    "repeated exposure",
    "expertise",
    "retrieval cues",
    "information quality",
    "prior beliefs"
  ],
  "measurementAssessmentMethods": "Knowledge tests; recall/recognition tasks; concept mapping; confidence ratings; structured elicitation",
  "measurementCaveats": "Accessible or familiar information may be inaccurate; observed recall depends on cues and does not fully reveal stored representation.",
  "mechanism": "Changes ease of integration, scrutiny, affective response, and likelihood of belief updating.",
  "moderatorsBoundaryConditions": "Cue match, recency, interference, expertise, motivation, stress, and context congruence.",
  "modifiability": "High",
  "name": "Prior-Belief Congruence",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Negative values = contradiction; positive values = congruence.",
  "primaryFamilyId": "PSY-F07",
  "relatedFamilyIds": [],
  "representationScale": "Strongly inconsistent–neutral–strongly consistent",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Processing Fluency",
    "Mental Model Coherence",
    "Metacognitive Confidence",
    "Prior-Belief Congruence"
  ],
  "volatility": "Moderate"
}
```

Perceived fit of new information to existing beliefs; distinct from objective agreement or truth.

Perceived congruence needs an aligned report/manipulation check; schema-consistent false recall and counterargument production are different outcomes.

Prior belief precedes message and perceived fit; counterarguing can reshape reported fit, requiring separated measurements.

No formal semantic equality or causal effect from confirmation-bias theory alone; REL-PSY-033 remains research-needed.

Boundary references: PSY-003, PSY-115, PSY-114. Sources: SRC153, SRC117, SRC-CAND-PSY-LAYER-0078.
