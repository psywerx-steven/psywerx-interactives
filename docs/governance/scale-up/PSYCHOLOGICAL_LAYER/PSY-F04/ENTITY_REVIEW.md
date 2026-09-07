# PSY-F04 — Motivation, Goals & Psychological Needs

Audit `AUD-PSY-F04-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All 15 frozen Driver records, 30 RELATED_SEARCH aliases and empty crosswalk list read; definitions, scale, direction, mechanism, indicators, methods, evidence, time/lag/persistence, modifiability, volatility, observability, caveats and narrative fields retained. No blocked local metadata found or repaired. Likelihood versus commitment, trait versus state, task versus goal and outcome versus measure distinctions flagged rather than canonical edits.

No local RDS. All endpoints of the 16 incident propositions are Drivers. PSY-078 in F09 is not targeted; its complete audit belongs to F09. A goal target-performance-gap indicator does not authorize formula-as-causality or Driver reclassification.

### PSY-026 — Intention Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The strength of commitment to perform a specified behavior within a stated time and context.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC110; SRC107; SRC174.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-026",
  "indicators": [
    "Stated likelihood",
    "commitment language",
    "preparation"
  ],
  "keySources": [
    "SRC110",
    "SRC107",
    "SRC174"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Organizes preparatory cognition and increases the probability of action when capability and opportunity permit.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Intention Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = stronger intention to perform the behavior.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high intention; probability or likelihood of acting",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Commitment to a specified behavior, time and context; not performance or intention enactment.

Canonical probability/likelihood and commitment scales may measure different aspects. Retain action/time/referent and distinguish behavioral expectation from resolved intention.

Current strength and later stability are different; intention-behavior follow-up is not a direct effect on intention.

Eight previously dispositioned incident claims reused; no automatic intention-to-action shortcut.

Boundary references: PSY-027, PSY-076, PSY-031. Sources: SRC107, SRC109, SRC110, SRC174, SRC140, SRC-CAND-PSY-LAYER-0037.

### PSY-027 — Goal Commitment

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of attachment to and determination to pursue a specified goal.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC118; SRC139.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-027",
  "indicators": [
    "Persistence",
    "goal-protective choices",
    "commitment ratings"
  ],
  "keySources": [
    "SRC118",
    "SRC139"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Sustains effort and protects the goal against distraction and setbacks.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Goal Commitment",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = stronger commitment to continued goal pursuit.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high commitment scale",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Attachment and determination toward a specified goal; not achieved performance or moral conviction itself.

Five-item commitment measurement work differs from persistence outcomes. Shared action-commitment indicators with PSY-110 can create circular association.

Goal attachment can persist while goal remains valued/feasible; no generic permanent change.

Exact difficulty/commitment direction requires independent measurement and feasibility; no universal dose-response inferred.

Boundary references: PSY-026, PSY-110, PSY-029. Sources: SRC118, SRC-CAND-PSY-LAYER-0033, SRC-CAND-PSY-LAYER-0034, SRC164.

### PSY-028 — Goal Specificity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a goal defines a clear target, criterion, or endpoint.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC118; SRC139.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-028",
  "indicators": [
    "Quantified target",
    "unambiguous endpoint",
    "agreement in goal coding"
  ],
  "keySources": [
    "SRC118",
    "SRC139"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Reduces ambiguity and improves attention, planning, feedback interpretation, and effort direction.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Goal Specificity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = more clearly specified target and criterion.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Vague–specific; coded goal precision",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Clarity of a goal's target/criterion/endpoint; not difficulty or execution planning.

Externally specifying a target does not prove participant encoded a correspondingly precise internal goal. Coded verbal precision requires fidelity and independent assessment.

Assigned instructions precede task, but no automatic later monitoring intensity or persistence.

No new effect from goal-setting behavior outcomes alone; action versus represented-goal alignment remains research-needed.

Boundary references: PSY-029, PSY-076, PSY-077. Sources: SRC118, SRC139, SRC-CAND-PSY-LAYER-0035.

### PSY-029 — Goal Difficulty

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Magnitude / level",
  "definition": "The perceived level of effort, skill, or performance required to attain a specified goal.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC118; SRC111.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-029",
  "indicators": [
    "Difficulty rating",
    "target gap",
    "effort mobilization"
  ],
  "keySources": [
    "SRC118",
    "SRC111"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Can mobilize effort when commitment and capability are adequate but induce disengagement when infeasible.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Goal Difficulty",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived challenge.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Very easy–very difficult; target-performance gap",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Perceived difficulty of attaining the goal, not objective task difficulty or success probability alone.

Canonical target-performance-gap indicator does not replace perceived effort/skill demand. Keep classification unchanged.

Perceived feasibility can change after feedback; difficulty-performance studies do not identify difficulty-to-commitment timing.

Preserve existing NON_MONOTONIC sign and distinguish task versus goal difficulty; no invented inverted-U parameters.

Boundary references: PSY-027, PSY-006. Sources: SRC118, SRC111, SRC-CAND-PSY-LAYER-0033, SRC-CAND-PSY-LAYER-0035.

### PSY-030 — Goal Conflict

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which pursuing one active goal interferes with or prevents progress toward another.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC118; SRC109.",
  "evidenceStrength": "Moderate",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-030",
  "indicators": [
    "Competing commitments",
    "switching",
    "delay",
    "perceived incompatibility"
  ],
  "keySources": [
    "SRC118",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Divides resources, increases decision conflict, and can delay, switch, or abandon action.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Goal Conflict",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = greater incompatibility among active goals.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "No conflict–severe conflict; pairwise conflict matrix",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Interference among two or more active personal goals, not one difficult task or generic decision conflict.

Resource conflict versus inherent incompatibility and remembered versus experienced interference require explicit goal pairs; shared item judgments can inflate associations.

Dynamic competing priorities differ from static goal-network ratings.

Conflict's moderation of intention-behavior is inconsistent; not evidence all intentions decrease.

Boundary references: PSY-031, PSY-026. Sources: SRC118, SRC109, SRC-CAND-PSY-LAYER-0037, SRC-CAND-PSY-LAYER-0041.

### PSY-031 — Goal Priority

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Ordinal",
  "definition": "The relative importance assigned to a specified goal compared with other active goals.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC118; SRC139.",
  "evidenceStrength": "Moderate",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-031",
  "indicators": [
    "Ranked goals",
    "time allocation",
    "sacrifice for goal"
  ],
  "keySources": [
    "SRC118",
    "SRC139"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Directs attention and resources toward the goal when conflicts arise.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Goal Priority",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = greater priority relative to competing goals.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Rank order; normalized importance weight; low–high priority",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Relative priority among active goals; not goal commitment, normative approval or achieved behavior.

Rank or normalized importance is a representation, not a causal numerical weight. Priority manipulation checks require exact comparison set.

A temporary prioritization prompt cannot establish enduring value change.

Promising priority experiments concern intention-behavior coupling, not an isolated ordinary edge or exact currently modeled target.

Boundary references: PSY-030, PSY-027, PSY-026. Sources: SRC118, SRC-CAND-PSY-LAYER-0037, SRC174.

### PSY-032 — Intrinsic Motivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which an activity is pursued for inherent interest, enjoyment, or satisfaction.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC138.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-032",
  "indicators": [
    "Voluntary engagement",
    "enjoyment",
    "persistence without external reward"
  ],
  "keySources": [
    "SRC108",
    "SRC138"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Supports sustained engagement by making activity performance itself rewarding.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Intrinsic Motivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = more activity engagement for inherent interest or enjoyment.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high intrinsic motivation subscale",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Pursuing an activity for inherent interest/enjoyment, not all autonomous reasons or any persistence.

Interest/enjoyment subscale is separated from competence, value, effort and choice subscales. Free-choice time and task output are not identical to the latent construct.

Bounded unit-end homework interest does not establish trait change, long-term learning or general work motivation.

Retain one bounded homework-interest effect; option-choice null and design/missingness limitations preserved.

Boundary references: PSY-033, PSY-034, PSY-036. Sources: SRC108, SRC-CAND-PSY-LAYER-0028, SRC-CAND-PSY-LAYER-0029, SRC-CAND-PSY-LAYER-0030, SRC-CAND-PSY-LAYER-0031, SRC-CAND-PSY-LAYER-0032.

### PSY-033 — Autonomous Motivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which action is experienced as self-endorsed and congruent with personally accepted values or goals.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC138.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-033",
  "indicators": [
    "Perceived choice",
    "identified reasons",
    "persistence"
  ],
  "keySources": [
    "SRC108",
    "SRC138"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Supports internalization, persistence, and flexible engagement by aligning action with chosen values.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Autonomous Motivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = greater self-endorsement of the reason for action.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high autonomous regulation composite",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Self-endorsed regulation consistent with accepted values/goals, which can include non-enjoyable but valued action.

Identified regulation differs from intrinsic interest. Relative autonomy composites can mix facets and should not be interpreted as one manipulated primitive.

Momentary volition and internalization over longer periods need separate evidence.

Need satisfaction and autonomous regulation share volition wording; meta-analytic path models do not isolate this mediator.

Boundary references: PSY-032, PSY-035, PSY-034. Sources: SRC108, SRC138, SRC-CAND-PSY-LAYER-0029, SRC-CAND-PSY-LAYER-0030.

### PSY-034 — Controlled Motivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which action is driven by external demands, rewards, punishments, or internal pressure such as guilt or contingent self-worth.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC138.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-034",
  "indicators": [
    "Compliance under monitoring",
    "pressure ratings",
    "guilt-based reasons"
  ],
  "keySources": [
    "SRC108",
    "SRC138"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Can initiate behavior through pressure while reducing persistence or well-being when control is removed.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Controlled Motivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = greater experienced pressure or contingent motivation.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high controlled regulation composite",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Pressure-driven regulation through external demands or internal guilt; not mere reward receipt.

Pressure/tension rating is not itself controlled regulation; external and introjected motives can coexist with autonomous reasons.

Short-lived task tension does not show stable extrinsic orientation.

Reward contingency reviews differ in tasks, measures and inclusion rules; no universal reward-crowding or controlled-motivation effect.

Boundary references: PSY-032, PSY-033, PSY-039. Sources: SRC108, SRC-CAND-PSY-LAYER-0029, SRC-CAND-PSY-LAYER-0031, SRC-CAND-PSY-LAYER-0032.

### PSY-035 — Autonomy Need Satisfaction

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person experiences choice, volition, and self-endorsement in a relevant context.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC138.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-035",
  "indicators": [
    "Choice and volition ratings",
    "self-endorsed reasons"
  ],
  "keySources": [
    "SRC108",
    "SRC138"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Supports internalization and self-directed regulation by reducing experienced coercion.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Autonomy Need Satisfaction",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater experienced volition and choice.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high need-satisfaction scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Experienced volition and choice in a context, not objective options, legal autonomy or generic perceived control.

Perceived option availability and freely endorsed action are distinguishable. A manipulation check about options cannot stand in for whole need satisfaction.

State experience, not permanent freedom or personality; canonical delay remains unverified narrative.

Choice effects on intrinsic interest do not independently establish autonomy as a causal mediator.

Boundary references: PSY-033, PSY-013. Sources: SRC108, SRC138, SRC-CAND-PSY-LAYER-0029, SRC-CAND-PSY-LAYER-0030.

### PSY-036 — Competence Need Satisfaction

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person feels effective and capable of achieving valued outcomes in a relevant context.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC138.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-036",
  "indicators": [
    "Mastery ratings",
    "challenge engagement",
    "persistence"
  ],
  "keySources": [
    "SRC108",
    "SRC138"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Supports engagement and persistence by making effective action feel attainable and reinforcing.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Competence Need Satisfaction",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater experienced effectiveness and mastery.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high competence-satisfaction scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Experienced effectiveness/capability in valued activities; distinguish prospective self-efficacy from current mastery.

Feeling competent and successful test performance are distinct. Need scales, task-specific competence and capability expectancy require scope matching.

Task-level feedback may alter current appraisal without changing skill or enduring competence.

Homework competence ratings are promising, but no additional formal effect retained without fuller need/valued-outcome alignment.

Boundary references: PSY-006, PSY-032. Sources: SRC108, SRC138, SRC-CAND-PSY-LAYER-0029, SRC-CAND-PSY-LAYER-0031.

### PSY-037 — Relatedness Need Satisfaction

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person feels cared for, connected to, and significant to relevant others.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC138.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-037",
  "indicators": [
    "Connection ratings",
    "willingness to engage",
    "relational security"
  ],
  "keySources": [
    "SRC108",
    "SRC138"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Supports internalization and sustained engagement by linking action to valued relationships.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Relatedness Need Satisfaction",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater experienced connection and mutual care.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high relatedness-satisfaction scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Feeling cared for, connected and significant to others; not number of ties, support availability or ostracism exposure.

Substantial content overlap with PSY-020 belonging requires contextual referents, not automatic synonymy or causal inverse.

A virtual exclusion moment does not establish sustained relatedness need change.

Reuse F03 social-exclusion research; no duplicate inverse effect or new social-tie claim.

Boundary references: PSY-020, PSY-019, PSY-024. Sources: SRC108, SRC135, SRC221.

### PSY-038 — Approach Motivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The strength of motivation to move toward a desired outcome, reward, or opportunity.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC163; SRC115.",
  "evidenceStrength": "Moderate",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-038",
  "indicators": [
    "Approach choice",
    "reduced latency",
    "effort toward reward"
  ],
  "keySources": [
    "SRC163",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Increases exploration, effort, and action readiness toward positively valued targets.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Approach Motivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = stronger movement toward desired outcomes.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high approach motivation or activation",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Current motivation toward a desired outcome, not enduring reward sensitivity or every effort choice.

Effort discounting in reward tasks is a partial behavioral operationalization; distinguish cognitive from physical domains and motivational quality.

State responsiveness can vary despite stable trait disposition; no state-to-trait conversion.

Sleep restriction reduced cognitive effort willingness but not physical willingness; exact broad approach endpoint remains unresolved.

Boundary references: PSY-127, PSY-039. Sources: SRC163, SRC-CAND-PSY-LAYER-0036, SRC-CAND-PSY-LAYER-0038.

### PSY-039 — Avoidance Motivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The strength of motivation to prevent, escape, or distance from an unwanted outcome or threat.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC163; SRC124.",
  "evidenceStrength": "Moderate",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-039",
  "indicators": [
    "Avoidance choice",
    "vigilance",
    "withdrawal",
    "safety action"
  ],
  "keySources": [
    "SRC163",
    "SRC124"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Directs vigilance and action toward threat prevention, withdrawal, or safety behavior.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Avoidance Motivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = stronger movement away from unwanted outcomes.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high avoidance motivation or inhibition",
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
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Current motivation to avoid/prevent an unwanted state; can coexist with approach motivation.

Avoidance-oriented goal instructions and fear/arousal measures are not interchangeable. Performance-avoidance and mastery/approach contrasts bundle goal content.

Immediate threat-driven motivation does not establish trait avoidance.

No automatic inverse relationship with approach and no direct effect derived from fear-appeal behavior.

Boundary references: PSY-038, PSY-009, PSY-128. Sources: SRC163, SRC-CAND-PSY-LAYER-0036, SRC124, SRC-CAND-PSY-LAYER-0015.

### PSY-040 — Anticipated Regret

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing intrinsic, autonomous, controlled, approach, and avoidance motivation into a single amount of motivation.",
  "dataType": "Unipolar continuous",
  "definition": "The expected intensity of regret that would be felt after choosing or failing to choose a specified action.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC140; SRC141.",
  "evidenceStrength": "Strong",
  "family": "Motivation, Goals & Psychological Needs",
  "id": "PSY-040",
  "indicators": [
    "Regret ratings",
    "intention change",
    "predecisional simulation"
  ],
  "keySources": [
    "SRC140",
    "SRC141"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Goal choice",
    "intention",
    "effort",
    "persistence",
    "disengagement",
    "action planning"
  ],
  "likelyUpstreamInfluences": [
    "Values",
    "incentives",
    "autonomy support",
    "need states",
    "feedback",
    "anticipated consequences"
  ],
  "measurementAssessmentMethods": "Motivation and goal scales; goal elicitation; behavioral persistence tasks; repeated intention assessment",
  "measurementCaveats": "Motivation is action- and context-specific; stated goals and intentions can overpredict behavior when opportunity or control is weak.",
  "mechanism": "Adds a prospective emotional cost to options and can increase intention for regret-avoiding action.",
  "moderatorsBoundaryConditions": "Goal conflict, feasibility, autonomy, feedback quality, time horizon, identity relevance, and opportunity.",
  "modifiability": "High",
  "name": "Anticipated Regret",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater expected regret associated with the specified choice or omission.",
  "primaryFamilyId": "PSY-F04",
  "relatedFamilyIds": [],
  "representationScale": "Low–high anticipated regret for each option",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Self-Efficacy",
    "Outcome Valuation",
    "Goal Commitment",
    "Action Plan Specificity"
  ],
  "volatility": "Moderate"
}
```

Expected regret concerning a specific future action OR omission, not experienced regret after an outcome.

Question wording determines whether more regret predicts less or more intention. Shared self-report and prior preference may explain associations.

Prospective prediction does not identify a causal effect of the latent anticipated emotion.

Current mechanism already refers to not acting; revision proposal makes that qualification explicit and lowers causal certainty without implementing a change.

Boundary references: PSY-026, PSY-005. Sources: SRC140, SRC141, SRC115.
