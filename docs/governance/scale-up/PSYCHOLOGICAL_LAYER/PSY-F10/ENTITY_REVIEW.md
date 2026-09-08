# PSY-F10 — Decision Valuation Across Risk, Time & Effort

Audit `AUD-PSY-F10-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All ten full canonical records,20 RELATED_SEARCH aliases and empty crosswalk read. Definitions, mechanisms, types/scales, direction, modifiability/volatility, timings, measurements, caveats, sources, narratives/interactions and null metadata retained. No blocked fields repaired.

No Family RDS. Related PSY-078 remains external-input derived; reference point not discrepancy and no direct RDS target.

### PSY-084 — Loss Aversion

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which equivalent losses are weighted more heavily than gains relative to a reference point.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC113; SRC187.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-084",
  "indicators": [
    "Mixed-gamble choices",
    "selling/buying asymmetry",
    "model parameter"
  ],
  "keySources": [
    "SRC113",
    "SRC187"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Tilts valuation toward avoiding losses and can alter risk choice, exchange, and resistance to change.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Loss Aversion",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher values = greater relative weighting of losses over gains.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Estimated loss-aversion coefficient; choice-indifference ratio",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Equivalent loss versus gain sensitivity around a specified reference, not risk aversion or any framing contrast.

Loss/gain utility fitting needs reference, units and model; choice changes may alter beliefs or reference without altering loss-aversion parameter.

Momentary task/domain/stakes versus person-level tendency; no universal coefficient.

Existing INF-044 revision review only; no loss-aversion decrease from framing a risky choice.

Boundary references: PSY-085, PSY-086, PSY-087. Sources: SRC113, SRC187, SRC-408, SRC-CAND-PSY-LAYER-0116.

### PSY-085 — Reference Point

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Magnitude / level",
  "definition": "The outcome level currently used as the baseline against which gains and losses are psychologically evaluated.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC113; SRC187.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-085",
  "indicators": [
    "Stated expectation",
    "status quo",
    "gain/loss classification",
    "model estimate"
  ],
  "keySources": [
    "SRC113",
    "SRC187"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Reclassifies identical outcomes as gains or losses and changes marginal subjective value.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Reference Point",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher values = a higher comparison baseline; effects depend on outcomes relative to it.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Outcome units; status quo, expectation, goal, or social-comparison baseline",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Outcome level serving as gain/loss baseline, not generic goal salience or perceived discrepancy.

Status quo, expectations, goals and social comparison can supply different baselines; outcome reference must be identified.

Reference adaptation and exposure timing require repeated measurement; no implicit fixed baseline.

No independent exact reference-level effect extracted; keep reference update versus changed utility separate.

Boundary references: PSY-084, PSY-028, PSY-078. Sources: SRC113, SRC187, SRC126.

### PSY-086 — Risk Preference

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Bipolar continuous",
  "definition": "The person's relative preference for uncertain versus certain outcomes within a specified domain and state.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC113; SRC188.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-086",
  "indicators": [
    "Lottery choices",
    "certainty equivalents",
    "risk-taking behavior"
  ],
  "keySources": [
    "SRC113",
    "SRC188"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Changes the subjective value assigned to outcome variability and uncertainty.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Risk Preference",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Negative values = risk avoidance; positive values = risk seeking, under the defined convention.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Risk averse–neutral–risk seeking; utility curvature estimate",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Preference across uncertain versus specified certain outcomes, bipolar avoidance-to-seeking; not risk perception or fear.

Domain/stakes, probability, expected value and framing must align; survey willingness and revealed choice differ.

State and stable heterogeneity coexist; between-person survey associations not within-person change.

Reuse F05 fear/anger reviews; no cross-domain universal risk direction or new duplicate.

Boundary references: PSY-008, PSY-041, PSY-043, PSY-084. Sources: SRC188, SRC115, SRC-CAND-PSY-LAYER-0117.

### PSY-087 — Probability Weighting

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Other structured type",
  "definition": "The transformation by which objective or stated probabilities receive greater or lesser decision weight.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC113; SRC187.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-087",
  "indicators": [
    "Lottery choices",
    "probability-matching task",
    "fitted weighting parameters"
  ],
  "keySources": [
    "SRC113",
    "SRC187"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Changes the impact of unlikely and likely outcomes on subjective valuation.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Probability Weighting",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Values indicate overweighting or underweighting relative to identity weighting.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Estimated weighting function or probability-specific decision weights",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Transformation of stated/objective probability into decision weight, not subjective probability belief or graph weight.

Structured weighting function; curves can cross. Experience changes sampling/beliefs as well as as-if decision weights.

Description versus learned experience requires explicit exposure histories and probability accuracy.

No uniform sign across probability range; FUNCTIONAL_SHAPE allowed for Driver but exact parameter/pointwise scope not established. No numerical execution.

Boundary references: PSY-086, PSY-088, PSY-003. Sources: SRC187, SRC-CAND-PSY-LAYER-0112.

### PSY-088 — Ambiguity Aversion

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which options with unknown or imprecise probabilities are valued less than comparable options with known probabilities.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC189; SRC123.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-088",
  "indicators": [
    "Ellsberg-type choices",
    "ambiguity premium",
    "information-seeking choice"
  ],
  "keySources": [
    "SRC189",
    "SRC123"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Adds a subjective penalty to options whose outcome probabilities are unclear.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Ambiguity Aversion",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher values = stronger avoidance of probability ambiguity.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Choice premium; ambiguity-aversion parameter; low–high scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Preference penalty for unknown/ill-specified probabilities relative to comparable known risk.

Ambiguity level and domain-specific attitude differ; learning probabilities changes exposure, not necessarily aversion.

State/task conditions versus broader intolerance of uncertainty must not collapse.

No exact canonical ambiguity-aversion manipulation retained; not universal aversion or intolerance scale identity.

Boundary references: PSY-086, PSY-087, PSY-132. Sources: SRC189, SRC123, SRC-CAND-PSY-LAYER-0117.

### PSY-089 — Delay Discounting

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Rate",
  "definition": "The rate at which the subjective value of an outcome decreases as delay to receipt increases.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC126; SRC190.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-089",
  "indicators": [
    "Intertemporal choices",
    "indifference points",
    "fitted discount parameter"
  ],
  "keySources": [
    "SRC126",
    "SRC190"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Shifts preference toward sooner outcomes and away from delayed consequences.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Delay Discounting",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher values = steeper devaluation of delayed outcomes.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Hyperbolic or exponential discount parameter; indifference points",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Rate at which outcome value declines with delay; distinguish present premium, effort cost and moral impulsivity.

Fitted rate, indifference points and AUC differ. Rung2019 tests two local indifference points rather than a uniquely identified full rate/curve.

Immediate cue-present effect differs from uncued persistence, trait change and actual future behavior.

EA0018 RN pending exact rate/curve specification: positive local discounting evidence retained, no whole-construct universal decrease. LEVEL of intrinsic rate differs from RATE-of-change.

Boundary references: PSY-090, PSY-091, PSY-082. Sources: SRC126, SRC190, SRC-CAND-PSY-LAYER-0107, SRC-CAND-PSY-LAYER-0108, SRC-CAND-PSY-LAYER-0110, SRC-CAND-PSY-LAYER-0114.

### PSY-090 — Present Bias

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Magnitude / level",
  "definition": "The extra weight assigned to outcomes available now relative to outcomes delayed by any positive amount.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC126; SRC190.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-090",
  "indicators": [
    "Preference reversal",
    "immediate-choice premium",
    "fitted beta parameter"
  ],
  "keySources": [
    "SRC126",
    "SRC190"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Creates time-inconsistent preferences and weakens follow-through on earlier plans.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Present Bias",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher present bias = greater extra preference for immediate outcomes.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Beta parameter; preference reversal across immediate versus delayed choices",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Extra premium for now over all positively delayed outcomes, not general steep discounting or all impulsive behavior.

Conventional beta parameter falls as present bias rises; explicit coding convention required. A two-option now-later task does not separately identify beta and long-run delta.

Immediate/nonimmediate matched comparisons and repeated decisions needed; no permanent disposition from one task.

Canonical beta scale is preserved but directional convention flagged. Trait association and delay discounting do not prove trait→present-bias causality.

Boundary references: PSY-089, PSY-125, PSY-082. Sources: SRC126, SRC205, SRC190.

### PSY-091 — Effort Discounting

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Rate",
  "definition": "The rate at which the subjective value of an outcome decreases as required physical or cognitive effort increases.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC191; SRC118.",
  "evidenceStrength": "Moderate",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-091",
  "indicators": [
    "Effort-choice task",
    "persistence",
    "fitted effort cost"
  ],
  "keySources": [
    "SRC191",
    "SRC118"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Reduces selection and persistence of effortful options unless reward, identity, or goal value offsets the cost.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Effort Discounting",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher values = steeper devaluation as required effort increases.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Effort-discount parameter; effort indifference points",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Decline in subjective outcome value as required effort increases; distinguish motivation, effort expenditure and capacity.

Physical/cognitive effort costs depend on reward, baseline/comparator and task ability; drug/PET study estimates choices not broad executive capacity.

Acute drug/task effects versus enduring cost preference; no generalized pharmacologic benefit.

No exact whole-rate effect or dopaminergic causal Driver inferred from PET association; prescription/clinical use outside scope.

Boundary references: PSY-031, PSY-035, PSY-057, PSY-058. Sources: SRC191, SRC-CAND-PSY-LAYER-0113.

### PSY-092 — Decision Conflict

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Magnitude / level",
  "definition": "The degree of difficulty or tension produced by similarly valued, incompatible options or uncertain tradeoffs.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC192; SRC115.",
  "evidenceStrength": "Moderate",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-092",
  "indicators": [
    "Long response time",
    "reversals",
    "indecision",
    "conflict rating"
  ],
  "keySources": [
    "SRC192",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Delays choice, increases information search, and raises susceptibility to defaults or avoidance.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Decision Conflict",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = greater conflict among active options.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Low–high conflict; response-time or indecision index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "High"
}
```

Subjective decision difficulty/tension under competing alternatives, not reaction time or deferral alone.

Choice overload studies use satisfaction/confidence/regret/deferral; these are not interchangeable latent conflict measures.

During choice versus postchoice regret/confidence; no fixed more-options→conflict effect.

Heterogeneous null/positive choice-overload findings do not support universal direct conflict or task-difficulty identity.

Boundary references: PSY-056, PSY-084, PSY-088. Sources: SRC192, SRC-CAND-PSY-LAYER-0118.

### PSY-093 — Default Option Preference

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating named biases as immutable defects or assuming one parameter estimated in one task transfers unchanged to all decisions.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which an option's designation as the preselected or status-quo choice increases its subjective preference.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC193; SRC113.",
  "evidenceStrength": "Strong",
  "family": "Decision Valuation Across Risk, Time & Effort",
  "id": "PSY-093",
  "indicators": [
    "Default uptake",
    "opt-out versus opt-in difference",
    "switching reluctance"
  ],
  "keySources": [
    "SRC193",
    "SRC113"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Choice",
    "risk taking",
    "delay",
    "effort allocation",
    "switching",
    "persistence with defaults"
  ],
  "likelyUpstreamInfluences": [
    "Option attributes",
    "framing",
    "stakes",
    "affect",
    "reference outcomes",
    "time horizon",
    "uncertainty"
  ],
  "measurementAssessmentMethods": "Incentivized or hypothetical choice tasks; adaptive titration; model-based parameter estimation; structured self-report",
  "measurementCaveats": "Estimated parameters can be task-, domain-, stake-, and model-dependent; descriptive regularities are not fixed universal traits.",
  "mechanism": "Defaults imply endorsement, reduce effort, and establish a reference point, increasing passive selection.",
  "moderatorsBoundaryConditions": "Domain, wealth or resource state, experience, numeracy, affect, time pressure, and elicitation method.",
  "modifiability": "Moderate",
  "name": "Default Option Preference",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Can shift with framing and state; stable individual differences are only partly persistent.",
  "polarityDirection": "Higher values = stronger preference shift toward the default.",
  "primaryFamilyId": "PSY-F10",
  "relatedFamilyIds": [],
  "representationScale": "Choice-rate difference or individual default-susceptibility estimate",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours",
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Reference Point",
    "Probability Weighting",
    "Mood Valence",
    "Decision Conflict"
  ],
  "volatility": "Moderate"
}
```

Increased subjective preference from default/status-quo designation, not observed uptake alone.

Selection can result from ease, inertia, endorsement or cost without independent preference change; latent construct must be separately aligned.

Current option designation, reversible choice and subsequent preference persistence separate.

EA0019 RN: strong default-choice literature is not sufficient evidence for exact subjective preference or practitioner permission.

Boundary references: PSY-084, PSY-085, PSY-089. Sources: SRC193, SRC-CAND-PSY-LAYER-0115.
