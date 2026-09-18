# PSY-F08 — Learning, Habit & Automaticity

Audit `AUD-PSY-F08-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All five complete canonical Driver records,10 RELATED_SEARCH aliases and empty crosswalk reviewed. Definitions, mechanisms, scales/types, polarity, timing/lag/persistence, volatility/modifiability, measurements/caveats, sources and narratives/interactions preserved. No blocked local fields repaired.

No local RDS or incident RDS endpoint. Composite scores remain measurements, not authorization to reclassify. PSY-071/073 multidimensional fields preserved; same Layer scope escalation, no direct RDS/state target.

### PSY-070 — Habit Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Inferring habit solely from repeated behavior or assuming learned responses cannot be overridden by goals and context change.",
  "dataType": "Unipolar continuous",
  "definition": "The strength of a learned propensity for a specified context to cue a specified behavior with reduced deliberation.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC116; SRC154.",
  "evidenceStrength": "Strong",
  "family": "Learning, Habit & Automaticity",
  "id": "PSY-070",
  "indicators": [
    "Self-report habit index",
    "context-linked repetition",
    "behavior stability"
  ],
  "keySources": [
    "SRC116",
    "SRC154"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Automatic action initiation",
    "persistence",
    "reduced deliberation",
    "cue-driven choice"
  ],
  "likelyUpstreamInfluences": [
    "Behavioral repetition",
    "stable context cues",
    "reinforcement history",
    "modeling",
    "goal consistency"
  ],
  "measurementAssessmentMethods": "Habit and automaticity scales; cue-response tasks; behavioral trace analysis; longitudinal repeated measurement",
  "measurementCaveats": "Frequency, habit, automaticity, and cue association are related but not identical; self-report may not capture automatic processes well.",
  "mechanism": "Allows stable cues to trigger action efficiently and compete with current intentions.",
  "moderatorsBoundaryConditions": "Context stability, reward schedule, cue specificity, competing goals, stress, and opportunity for repetition.",
  "modifiability": "Moderate",
  "name": "Habit Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can persist for months or years in stable contexts and weaken with cue disruption or sustained retraining.",
  "polarityDirection": "Higher values = stronger learned context–behavior propensity.",
  "primaryFamilyId": "PSY-F08",
  "relatedFamilyIds": [],
  "representationScale": "Low–high habit-strength composite; context-specific index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Cue–Response Association Strength",
    "Outcome Expectancy",
    "Implementation Intention Strength",
    "Self-Control Capacity"
  ],
  "volatility": "Low"
}
```

Learned context→behavior propensity with reduced deliberation, not behavioral frequency alone.

SRHI includes repetition, automaticity and identity items; SRBAI removes some contamination but remains self-report. Devaluation insensitivity can also reflect deficient goal-directed control.

Learning across weeks/months differs from expression over seconds; successful-learner curve threshold not universal acquisition time.

Repetition/habit candidate remains RN: within-person improvement, successful-learner selection and assay limitations do not identify universal causal habit gain.

Boundary references: PSY-071, PSY-072, PSY-026, PSY-075. Sources: SRC116, SRC154, SRC-CAND-PSY-LAYER-0082, SRC-CAND-PSY-LAYER-0083, SRC-CAND-PSY-LAYER-0084, SRC-CAND-PSY-LAYER-0086, SRC-CAND-PSY-LAYER-0090.

### PSY-071 — Behavioral Automaticity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Inferring habit solely from repeated behavior or assuming learned responses cannot be overridden by goals and context change.",
  "dataType": "Multidimensional",
  "definition": "The degree to which a specified behavior is initiated or executed quickly, efficiently, unintentionally, or with limited awareness.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC116; SRC154.",
  "evidenceStrength": "Strong",
  "family": "Learning, Habit & Automaticity",
  "id": "PSY-071",
  "indicators": [
    "Fast initiation",
    "low reported awareness or effort",
    "dual-task resilience"
  ],
  "keySources": [
    "SRC116",
    "SRC154"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Automatic action initiation",
    "persistence",
    "reduced deliberation",
    "cue-driven choice"
  ],
  "likelyUpstreamInfluences": [
    "Behavioral repetition",
    "stable context cues",
    "reinforcement history",
    "modeling",
    "goal consistency"
  ],
  "measurementAssessmentMethods": "Habit and automaticity scales; cue-response tasks; behavioral trace analysis; longitudinal repeated measurement",
  "measurementCaveats": "Frequency, habit, automaticity, and cue association are related but not identical; self-report may not capture automatic processes well.",
  "mechanism": "Reduces reliance on deliberative resources and increases cue-driven response probability.",
  "moderatorsBoundaryConditions": "Context stability, reward schedule, cue specificity, competing goals, stress, and opportunity for repetition.",
  "modifiability": "Moderate",
  "name": "Behavioral Automaticity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can persist for months or years in stable contexts and weaken with cue disruption or sustained retraining.",
  "polarityDirection": "Higher values = greater automatic initiation or execution.",
  "primaryFamilyId": "PSY-F08",
  "relatedFamilyIds": [],
  "representationScale": "Automaticity subscales; latency/interference indicators",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Cue–Response Association Strength",
    "Outcome Expectancy",
    "Implementation Intention Strength",
    "Self-Control Capacity"
  ],
  "volatility": "Low"
}
```

Multiple automaticity dimensions: speed, efficiency, intention and awareness may dissociate.

A four-item self-report subscale does not demonstrate all speed/interference/awareness facets. Habit composites containing the same items cannot independently cause their own subscale.

Available execution features versus enduring acquired cue propensity; short task effects not lifelong automaticity.

Layer feature-scope blocker applies; no whole multidimensional automaticity increase or scalar composite identity forced.

Boundary references: PSY-070, PSY-072, PSY-058, PSY-079. Sources: SRC-CAND-PSY-LAYER-0082, SRC-CAND-PSY-LAYER-0086, SRC116, SRC154.

### PSY-072 — Cue–Response Association Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Inferring habit solely from repeated behavior or assuming learned responses cannot be overridden by goals and context change.",
  "dataType": "Unipolar continuous",
  "definition": "The strength of the learned association between a specified cue and a specified response representation.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC120; SRC116.",
  "evidenceStrength": "Strong",
  "family": "Learning, Habit & Automaticity",
  "id": "PSY-072",
  "indicators": [
    "Priming effect",
    "response latency",
    "cue-specific action probability"
  ],
  "keySources": [
    "SRC120",
    "SRC116"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Automatic action initiation",
    "persistence",
    "reduced deliberation",
    "cue-driven choice"
  ],
  "likelyUpstreamInfluences": [
    "Behavioral repetition",
    "stable context cues",
    "reinforcement history",
    "modeling",
    "goal consistency"
  ],
  "measurementAssessmentMethods": "Habit and automaticity scales; cue-response tasks; behavioral trace analysis; longitudinal repeated measurement",
  "measurementCaveats": "Frequency, habit, automaticity, and cue association are related but not identical; self-report may not capture automatic processes well.",
  "mechanism": "Increases the speed and probability with which the cue activates the response.",
  "moderatorsBoundaryConditions": "Context stability, reward schedule, cue specificity, competing goals, stress, and opportunity for repetition.",
  "modifiability": "Moderate",
  "name": "Cue–Response Association Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can persist for months or years in stable contexts and weaken with cue disruption or sustained retraining.",
  "polarityDirection": "Higher values = stronger cue-linked activation of the response.",
  "primaryFamilyId": "PSY-F08",
  "relatedFamilyIds": [],
  "representationScale": "Low–high association; reaction-time or priming index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Cue–Response Association Strength",
    "Outcome Expectancy",
    "Implementation Intention Strength",
    "Self-Control Capacity"
  ],
  "volatility": "Low"
}
```

Learned association between a specific cue and response representation; not just frequent responding or cue accessibility.

Cue→response priming distinguished from neutral→cue accessibility and goal performance. Shared reaction-time measures need baseline and exact lexical contrasts.

Rapid plan encoding may affect a task immediately, unlike months-long habit development; frozen metadata retained not generalized.

If-then-plan effect RN pending exact priming contrast and source identity reconciliation; no mediation record or automaticity-profile effect.

Boundary references: PSY-075, PSY-066, PSY-071. Sources: SRC-CAND-PSY-LAYER-0087, SRC114, SRC120, SRC155.

### PSY-073 — Reinforcement Expectancy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Inferring habit solely from repeated behavior or assuming learned responses cannot be overridden by goals and context change.",
  "dataType": "Multidimensional",
  "definition": "The expected probability and value of reinforcement following a specified response in a specified context.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC109; SRC111.",
  "evidenceStrength": "Moderate",
  "family": "Learning, Habit & Automaticity",
  "id": "PSY-073",
  "indicators": [
    "Reward expectation",
    "choice under learned contingencies",
    "prediction rating"
  ],
  "keySources": [
    "SRC109",
    "SRC111"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Automatic action initiation",
    "persistence",
    "reduced deliberation",
    "cue-driven choice"
  ],
  "likelyUpstreamInfluences": [
    "Behavioral repetition",
    "stable context cues",
    "reinforcement history",
    "modeling",
    "goal consistency"
  ],
  "measurementAssessmentMethods": "Habit and automaticity scales; cue-response tasks; behavioral trace analysis; longitudinal repeated measurement",
  "measurementCaveats": "Frequency, habit, automaticity, and cue association are related but not identical; self-report may not capture automatic processes well.",
  "mechanism": "Supports learned response selection by representing anticipated reinforcement under the cue.",
  "moderatorsBoundaryConditions": "Context stability, reward schedule, cue specificity, competing goals, stress, and opportunity for repetition.",
  "modifiability": "Moderate",
  "name": "Reinforcement Expectancy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater expected reinforcing value of the response.",
  "primaryFamilyId": "PSY-F08",
  "relatedFamilyIds": [],
  "representationScale": "Expected probability × subjective value; contingency rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Cue–Response Association Strength",
    "Outcome Expectancy",
    "Implementation Intention Strength",
    "Self-Control Capacity"
  ],
  "volatility": "Low"
}
```

Expected reinforcement probability AND subjective value after a response in context; not reward amount or reward sensitivity.

Probability, value and product cannot be substituted without explicit scale/operation; choice, anticipatory pleasure and expectancy ratings differ.

Recent updating versus stable sensitivity; extinction/devaluation may change value without changing remembered probability.

Multidimensional probability/value target not satisfied by one manipulated reward or choice score; no signed effect retained.

Boundary references: PSY-004, PSY-074, PSY-127. Sources: SRC111, SRC109, SRC-CAND-PSY-LAYER-0089, SRC-CAND-PSY-LAYER-0093.

### PSY-074 — Observationally Learned Expectancy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Inferring habit solely from repeated behavior or assuming learned responses cannot be overridden by goals and context change.",
  "dataType": "Unipolar continuous",
  "definition": "An action–outcome expectation formed or updated from observing another person's behavior and consequences.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC111; SRC109.",
  "evidenceStrength": "Moderate",
  "family": "Learning, Habit & Automaticity",
  "id": "PSY-074",
  "indicators": [
    "Prediction after modeling",
    "imitation choice",
    "vicarious efficacy change"
  ],
  "keySources": [
    "SRC111",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Automatic action initiation",
    "persistence",
    "reduced deliberation",
    "cue-driven choice"
  ],
  "likelyUpstreamInfluences": [
    "Behavioral repetition",
    "stable context cues",
    "reinforcement history",
    "modeling",
    "goal consistency"
  ],
  "measurementAssessmentMethods": "Habit and automaticity scales; cue-response tasks; behavioral trace analysis; longitudinal repeated measurement",
  "measurementCaveats": "Frequency, habit, automaticity, and cue association are related but not identical; self-report may not capture automatic processes well.",
  "mechanism": "Transfers observed contingencies into the observer's choice and efficacy representations without direct experience.",
  "moderatorsBoundaryConditions": "Context stability, reward schedule, cue specificity, competing goals, stress, and opportunity for repetition.",
  "modifiability": "Moderate",
  "name": "Observationally Learned Expectancy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater expected likelihood of the modeled consequence.",
  "primaryFamilyId": "PSY-F08",
  "relatedFamilyIds": [],
  "representationScale": "0–1 expected outcome probability after modeled exposure",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Cue–Response Association Strength",
    "Outcome Expectancy",
    "Implementation Intention Strength",
    "Self-Control Capacity"
  ],
  "volatility": "Low"
}
```

Expectation of an action's outcome acquired by observing another person's behavior/consequence; acquisition route matters.

Cue-pain intensity expectancy and imitation performance are not necessarily action-outcome probability. Vicarious efficacy is not expected outcome likelihood.

Observation followed by prediction/choice; no inference of learning failure from no imitation or of durable transfer from one exposure.

Observational-pain evidence does not yet align exact action/probability endpoint; no causal edge or effect forced.

Boundary references: PSY-004, PSY-073, PSY-006. Sources: SRC111, SRC-CAND-PSY-LAYER-0092.
