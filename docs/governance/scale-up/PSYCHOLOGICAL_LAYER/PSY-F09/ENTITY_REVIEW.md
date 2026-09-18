# PSY-F09 — Planning, Self-Regulation & Executive Control

Audit `AUD-PSY-F09-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All9 complete canonical records,19aliases (18RELATED_SEARCH,1DEPRECATED_TERM) and empty crosswalk reviewed. Definitions/mechanisms, types/scales, direction, modifiability/volatility, times/lag/persistence, measurements/caveats, observability, evidence, narratives/interactions and null metadata preserved. No blocked fields repaired.

PSY-078 is the only Layer RDS. Required external desired/reference and perceived-current values are not invented Driver constituents. Same-person/goal/window/units/sign and input uncertainty required. Difference recomputation is not causal propagation; signed decrease differs from movement toward zero. Structured rds-review.json records all safeguards.

## Structured RDS safeguard review

```json
{
  "baseline": "de38b3948f511602af7aa94a9cd80b78e1a00298",
  "calculationWindow": "SCENARIO_SPECIFIC_REQUIRED_NOT_FILLED",
  "canonicalDriverConstituents": [],
  "canonicalMetadataModified": false,
  "causalSource": false,
  "denominator": "NOT_SPECIFIED_NOT_REQUIRED_BY_GENERIC_DIFFERENCE",
  "derivationType": "DIFFERENCE",
  "directEffectTargetPermitted": false,
  "entityId": "PSY-078",
  "entityType": "RELATIONAL_DERIVED_STATE",
  "exogenousRootRisk": "NO_CURRENT_OUTGOING_CLAIM; narrative mechanisms are not causal edges",
  "familyId": "PSY-F09",
  "formula": "desired_or_reference_state - perceived_current_state",
  "formulaTreatedAsCausality": false,
  "humanDecision": "PENDING — APPROVE / MODIFY / REJECT",
  "illustration": {
    "cases": [
      {
        "currentAfter": 9,
        "currentBefore": 8,
        "differenceAfter": 1,
        "differenceBefore": 2,
        "reference": 10
      },
      {
        "currentAfter": 11,
        "currentBefore": 12,
        "differenceAfter": -1,
        "differenceBefore": -2,
        "reference": 10
      }
    ],
    "conclusion": "Both approach zero; numeric change directions differ. Not evidence for or against any real intervention.",
    "purpose": "Sign logic only, no scientific simulation or calibrated output",
    "recordClass": "SYNTHETIC_NON_PRODUCTION"
  },
  "incomingCausalIds": [
    "REL-PSY-037"
  ],
  "newCausalRdsEndpoints": 0,
  "newDerivationalRecords": 0,
  "outgoingCausalIds": [],
  "programId": "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260907-001",
  "requiredAlignment": [
    "person",
    "goal domain",
    "reference state",
    "perceived current state",
    "units",
    "sign convention",
    "window",
    "update behavior"
  ],
  "requiredInputs": [
    {
      "entityId": null,
      "kind": "EXTERNAL_PARAMETER",
      "required": true,
      "type": "DESIRED_OR_REFERENCE_STATE"
    },
    {
      "entityId": null,
      "kind": "EXTERNAL_PARAMETER",
      "required": true,
      "type": "PERCEIVED_CURRENT_STATE"
    }
  ],
  "reviewDisposition": "SPLIT_CANDIDATE_FOR_REL_PSY_037_ONLY",
  "sharedInputRisks": [
    "Monitoring may update perceived current information, not world state.",
    "Goal/reference changes alter RDS without progress.",
    "Repeated scores share reference/current inputs; do not propagate both constituent update and independent RDS causal contribution."
  ],
  "uncertainty": "Preserve uncertainty and shared-input dependence; operational analytic method not selected or implemented."
}
```

### PSY-075 — Implementation Intention Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Unipolar continuous",
  "definition": "The strength and accessibility of a commitment linking a specified situational cue to a specified goal-directed response.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC114; SRC120; SRC155.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-075",
  "indicators": [
    "If–then plan presence",
    "cue recognition",
    "plan-consistent action"
  ],
  "keySources": [
    "SRC114",
    "SRC120",
    "SRC155"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Makes the cue more accessible and delegates response initiation to the cue when the underlying goal is active.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "High",
  "name": "Implementation Intention Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = stronger cue–response commitment in service of an active goal.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Absent–strong if–then commitment; plan-quality rating",
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
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Strength and accessibility of cue-linked commitment, not merely assignment to an if-then-plan condition.

Plan production, declared commitment and cue-response priming need separate measures; goal achievement is downstream.

Minutes/hours of encoding versus maintained access over days/weeks; no stable-habit equivalence.

Reuse F08 if-then identity HT0014; no duplicate or direct effect on strength inferred from plan instruction. Existing REL-PSY-036 proposal remains exact.

Boundary references: PSY-026, PSY-072, PSY-076. Sources: SRC114, SRC120, SRC155, SRC-CAND-PSY-LAYER-0087, SRC-CAND-PSY-LAYER-0103.

### PSY-076 — Action Plan Specificity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which a plan specifies what action will occur, when, where, how, and with what resources.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC114; SRC155.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-076",
  "indicators": [
    "Named action/time/place",
    "resource preparation",
    "plan completeness"
  ],
  "keySources": [
    "SRC114",
    "SRC155"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Reduces translation ambiguity and supports preparation, cue recognition, and coordination.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "High",
  "name": "Action Plan Specificity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = greater plan specificity and completeness.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Vague–specific; coded completeness of action elements",
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
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Specificity of the person's action plan: what/when/where/how/resources, not external recommendation specificity.

Plan content coding differs from internal uptake; intervention-arm uptake and specificity are selected, not independently randomized.

Immediate plan detail versus repeated execution over weeks; gym attendance null does not prove no plan formed.

No signed effect from external recommendations or guided plan-generation without exact comparator and internal-plan measurement.

Boundary references: PSY-028, PSY-075, PSY-077. Sources: SRC118, SRC-CAND-PSY-LAYER-0102, SRC-CAND-PSY-LAYER-0103.

### PSY-077 — Self-Monitoring Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Frequency",
  "definition": "The frequency and attentional intensity with which a person observes and compares their behavior or progress against a target.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC139; SRC109.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-077",
  "indicators": [
    "Tracking frequency",
    "recorded progress",
    "feedback checking"
  ],
  "keySources": [
    "SRC139",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Makes discrepancies visible and enables feedback-driven adjustment.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "Moderate",
  "name": "Self-Monitoring Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = more frequent or intensive monitoring.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Checks per period; low–high monitoring frequency/intensity",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days",
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Frequency and attentional intensity of observing/comparing own behavior or progress with a goal, not passive tracking availability.

Recording frequency is one operational facet; attention/comparison, target stability, reactivity and reporting distinguish actual monitoring from sensor collection.

Checks occur hours/days; goal attainment and calculated discrepancy updates can follow through different paths.

Prompt/check candidate EA0016 remains RN pending exact protocol, comparator and monitoring-versus-recording alignment; no automatic gap reduction.

Boundary references: PSY-028, PSY-078, PSY-120. Sources: SRC139, SRC185, SRC202, SRC203, SRC-512.

### PSY-078 — Perceived Goal–State Discrepancy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "constituentSpecifications": [
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "DESIRED_OR_REFERENCE_STATE",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    },
    {
      "alignmentRequirements": "Match analytic level, scope, and time window",
      "entityId": null,
      "externalParameterType": "PERCEIVED_CURRENT_STATE",
      "required": true,
      "role": "CONSTITUENT_OR_INPUT",
      "unitScaleExpectations": "Aligned with derivation logic"
    }
  ],
  "dataType": "Bipolar continuous",
  "definition": "The magnitude and direction of the difference between a desired target state and the person's perceived current state.",
  "derivationLogic": "Subtract perceived current state from the desired or reference state using the declared sign convention.",
  "derivationType": "DIFFERENCE",
  "differenceSpecification": {
    "referenceConvention": "Specify person, goal domain, reference state, perceived current state, units, sign convention, and update behavior.",
    "signConvention": "Negative or positive values indicate direction; magnitude indicates distance from target."
  },
  "directManipulability": "VIA_CONSTITUENTS",
  "entitySubtype": "RELATIONAL_DERIVED_STATE",
  "entityType": "RELATIONAL_DERIVED_STATE",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC185; SRC118.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-078",
  "indicators": [
    "Target–current gap",
    "corrective action",
    "progress rate"
  ],
  "keySources": [
    "SRC185",
    "SRC118"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Generates corrective motivation and guides persistence, escalation, revision, or disengagement.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "High",
  "name": "Perceived Goal–State Discrepancy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Negative or positive values indicate direction; magnitude indicates distance from target.",
  "primaryFamilyId": "PSY-F09",
  "recalculationBehavior": "Recalculate when a required constituent, reference, boundary, formula, or analysis window changes.",
  "relatedFamilyIds": [],
  "representationScale": "Below target–at target–above target; quantitative gap",
  "scopeRequirements": "Specify person, goal domain, reference state, perceived current state, units, sign convention, and update behavior.",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "uncertaintyPropagation": "Preserve and report constituent uncertainty; use analytic propagation or simulation when the selected operationalization supports it, otherwise note uncertainty qualitatively.",
  "volatility": "Moderate"
}
```

Signed perceived reference-minus-current difference; RDS, not primitive motivation or directly manipulated capacity.

Two required external inputs, same person/goal/window/units. Neither input has a canonical constituent Driver ID; formula and sign are not inferred from outcome scales.

Recalculate after input/reference/window changes. Monitoring may reveal discrepancy immediately; later action changes perceived current state.

HEIGHTENED incoming REL-PSY-037 requires split review: revealing gap versus later corrective action. Toward zero is not universal numeric decrease; no RDS effect target.

Boundary references: PSY-028, PSY-077, PSY-027. Sources: SRC185, SRC118, SRC139.

### PSY-079 — Emotion Regulation Capacity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Magnitude / level",
  "definition": "The currently available capacity to modify the intensity, duration, expression, or consequences of emotion in service of goals.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC121; SRC143; SRC144.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-079",
  "indicators": [
    "Regulation success",
    "strategy use",
    "recovery",
    "expression change"
  ],
  "keySources": [
    "SRC121",
    "SRC143",
    "SRC144"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Changes how strongly emotion constrains attention, valuation, communication, and action.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "Moderate",
  "name": "Emotion Regulation Capacity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = greater capacity to alter emotion or its consequences effectively.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Low–high capacity; strategy-success rating; task performance",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days",
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Currently available ability to regulate intensity, duration, expression or consequences to a goal; not habitual strategy preference.

ERSQ past-week skills profile and observed expression are not instantaneous latent capacity. ART package contains several skills; common-factor comparator matters.

Skills acquisition across weeks versus deployment now; emotion reduction not universal goal or capacity evidence.

ART waitlist advantage and active-comparator nondetection preserved; no atomic reappraisal efficacy from package, no new effect or mediation record.

Boundary references: PSY-043, PSY-047, PSY-080, PSY-083. Sources: SRC121, SRC143, SRC144, SRC-CAND-PSY-LAYER-0099, SRC-CAND-PSY-LAYER-0100.

### PSY-080 — Attentional Control Capacity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Magnitude / level",
  "definition": "The currently available capacity to direct, sustain, or shift attention according to goals despite distraction or threat.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC148; SRC149.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-080",
  "indicators": [
    "Interference cost",
    "sustained-attention errors",
    "control rating"
  ],
  "keySources": [
    "SRC148",
    "SRC149"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Protects task-relevant processing and limits capture by distractors or worry.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "Moderate",
  "name": "Attentional Control Capacity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = greater goal-directed control of attention.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Low–high control; interference or switching performance",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days",
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Current goal-directed attention control despite interference; distinguish allocation, WM availability and trait self-report.

Executive tasks carry speed/accuracy, strategy and motivation components. Anxiety may lower efficiency without lowering final accuracy.

Momentary fatigue versus trained skill and trait; no duration/magnitude inferred from RDoC framework.

BIO-019 needs exact fatigue-to-control evidence. F06 protective-control polarity concern retained; no RDS or task-score shortcut.

Boundary references: PSY-055, PSY-058, PSY-081, PSY-082. Sources: SRC148, SRC149, SRC-CAND-PSY-LAYER-0095, SRC-CAND-PSY-LAYER-0096, SRC-CAND-PSY-LAYER-0097, SRC-CAND-PSY-LAYER-0105.

### PSY-081 — Response Inhibition Capacity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Magnitude / level",
  "definition": "The currently available capacity to suppress or stop a dominant, prepotent, or already initiated response.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC149; SRC186.",
  "evidenceStrength": "Strong",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-081",
  "indicators": [
    "Stop-signal latency",
    "commission errors",
    "restraint behavior"
  ],
  "keySources": [
    "SRC149",
    "SRC186"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Permits goals and rules to override impulses or automatic responses.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "Moderate",
  "name": "Response Inhibition Capacity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = greater ability to suppress the specified response.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Low–high capacity; stop-signal or go/no-go performance",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days",
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Current ability to stop/suppress prepotent or initiated response; not consumption, go speed or self-reported restraint.

GNG withholding and SST stopping differ; go RT, Stroop interference, WM and inhibitory capacity cannot be pooled as semantic identity.

Immediate task gains versus transfer and four-month followup; sleep protocols not enduring trait changes.

EA0017 remains RN. Review pooled heterogeneous cognitive measures; Enge active-control null versus passive-control latency improvement must not disappear.

Boundary references: PSY-058, PSY-070, PSY-080, PSY-082. Sources: SRC149, SRC186, SRC-CAND-PSY-LAYER-0104, SRC-CAND-PSY-LAYER-0105, SRC-CAND-PSY-LAYER-0106.

### PSY-082 — Self-Control Capacity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Magnitude / level",
  "definition": "The currently available capacity to align behavior with valued longer-term goals when immediate impulses or competing responses are present.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC157; SRC186.",
  "evidenceStrength": "Moderate",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-082",
  "indicators": [
    "Delay or restraint behavior",
    "state-control rating",
    "persistence"
  ],
  "keySources": [
    "SRC157",
    "SRC186"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Supports inhibition, attention, and strategy deployment when immediate and longer-term goals conflict.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "Moderate",
  "name": "Self-Control Capacity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = greater current capacity for goal-consistent restraint.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Low–high state capacity; behavioral restraint index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days",
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Current goal-aligned control under impulse/conflict, not stable conscientiousness, moral worth or a proven depletable substance.

Task/questionnaire convergence heterogeneous; executive-task measures weaker than informant reports. SRC157 stored PMID wrong; exact intended work verified separately.

Sequential short tasks do not establish universal finite-resource depletion; training literature does not prove permanent trait change.

Large replication outcomes differ. Preserve confirmatory nondetection and small positive task-specific result; no universal depletion edge or capacity-increase claim.

Boundary references: PSY-070, PSY-080, PSY-081, PSY-120. Sources: SRC157, SRC-CAND-PSY-LAYER-0095, SRC-CAND-PSY-LAYER-0096, SRC-CAND-PSY-LAYER-0097.

### PSY-083 — Coping Strategy Flexibility

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating self-regulatory failure as a fixed personal deficit when task demands, opportunity, goals, or fatigue may dominate.",
  "dataType": "Magnitude / level",
  "definition": "The capacity to vary coping strategies in response to changing demands, controllability, and feedback.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC121; SRC143.",
  "evidenceStrength": "Moderate",
  "family": "Planning, Self-Regulation & Executive Control",
  "id": "PSY-083",
  "indicators": [
    "Strategy switching",
    "context-fit ratings",
    "coping repertoire"
  ],
  "keySources": [
    "SRC121",
    "SRC143"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Plan execution",
    "error correction",
    "persistence",
    "impulse inhibition",
    "emotion modulation",
    "goal attainment"
  ],
  "likelyUpstreamInfluences": [
    "Goal importance",
    "feedback",
    "cognitive resources",
    "training",
    "stress",
    "environmental structure"
  ],
  "measurementAssessmentMethods": "Planning and regulation scales; executive-control tasks; diary or experience sampling; behavioral performance measures",
  "measurementCaveats": "Performance tasks and self-report capture different facets; capacity can be distinguished from momentary deployment and opportunity.",
  "mechanism": "Improves regulation by matching strategy to situational demands rather than rigidly repeating one response.",
  "moderatorsBoundaryConditions": "Cognitive load, fatigue, stress, task complexity, cue availability, motivation, and plan quality.",
  "modifiability": "Moderate",
  "name": "Coping Strategy Flexibility",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = greater ability to adapt coping strategy to context.",
  "primaryFamilyId": "PSY-F09",
  "relatedFamilyIds": [],
  "representationScale": "Low–high flexibility; repertoire × context-fit measure",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days",
    "Weeks–Months"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Goal Commitment",
    "Cognitive Load",
    "Self-Monitoring Intensity",
    "Implementation Intention Strength"
  ],
  "volatility": "Moderate"
}
```

Adaptive selection/revision of coping to demands/controllability/feedback, not repertoire size alone or cognitive switching.

Fit, perceived ability and variation operationalizations differ; country differences and self-report adjustment associations not causal culture or clinical benefit.

Within-situation adaptation versus training across weeks; performance and retrospective repertoire not instantaneous flexibility.

Chinese workplace serious-play/CBT packages and coping-fit synthesis remain RN for exact Driver; discriminative-thinking mediation not identified.

Boundary references: PSY-014, PSY-062, PSY-079. Sources: SRC143, SRC-CAND-PSY-LAYER-0098, SRC-CAND-PSY-LAYER-0101.
