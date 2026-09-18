# PSY-F01 — Beliefs, Attitudes & Outcome Expectancies

Audit `AUD-PSY-F01-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

BASELINE.json preserves every canonical field including nulls, aliases and crosswalks. research.json contains entity-specific interpretation; no canonical repairs. Null timeScaleQualifier is unspecified, not a governance block.

No RDS member in this Family. No direct RDS effect target or calculated attitude index used as a manipulable entity.

### PSY-001 — Attitude Valence

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Bipolar continuous",
  "definition": "The degree to which performing a specified behavior is evaluated unfavorably or favorably.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC107; SRC110.",
  "evidenceStrength": "Strong",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-001",
  "indicators": [
    "Evaluative ratings",
    "approach or avoidance language",
    "choice preference"
  ],
  "keySources": [
    "SRC107",
    "SRC110"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Changes the subjective desirability of an option and contributes to intention and choice when accessible and relevant.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "Moderate",
  "name": "Attitude Valence",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Negative values = unfavorable evaluation; positive values = favorable evaluation.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "Validated semantic-differential or Likert composite anchored unfavorable–favorable",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Low"
}
```

Behavior-specific favorable/unfavorable evaluation; distinct from evaluation of an object, belief truth, intention and action. Evaluative conditioning of an arbitrary stimulus does not establish change in the specified behavior attitude.

Use directly elicited behavior-specific valence, not an expectancy-times-value calculated index. Shared self-report and item wording require temporal alignment.

Canonical minutes–hours onset/days–weeks change is not an empirically estimated universal lag; health intervention follow-up varies.

Outcome/behavior correspondence and operational invariance across populations; canonical definition untouched.

Boundary references: PSY-002, PSY-005, PSY-026. Sources: SRC107, SRC110, SRC-CAND-PSY-LAYER-0004, SRC-407.

### PSY-002 — Attitude Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Multidimensional",
  "definition": "The degree to which a behavior-specific evaluation is confident, accessible, stable, and resistant to change.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC156; SRC117.",
  "evidenceStrength": "Moderate",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-002",
  "indicators": [
    "Response latency",
    "test–retest stability",
    "certainty and importance ratings"
  ],
  "keySources": [
    "SRC156",
    "SRC117"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Strong attitudes are retrieved more readily, guide interpretation, and resist counterpersuasion.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "Moderate",
  "name": "Attitude Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = stronger and more consequential attitude.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "Composite of certainty, accessibility, importance, stability, and resistance",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Low"
}
```

Multidimensional certainty/accessibility/stability/resistance profile, not favorable valence. Increasing certainty in an unfavorable attitude need not increase intention to perform a behavior.

A single attitude-certainty item does not measure every dimension of Attitude Strength. No whole-profile decrease/increase inferred.

A within-session certainty difference is not demonstrated durable attitude stability or enduring resistance.

Profile dimensions may dissociate; candidate-only boundary issue, not Driver-to-RDS reclassification.

Boundary references: PSY-001, PSY-116. Sources: SRC156.

### PSY-003 — Belief Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of confidence or commitment attached to a specified proposition about the world.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC168; SRC169.",
  "evidenceStrength": "Moderate",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-003",
  "indicators": [
    "Confidence rating",
    "resistance to revision",
    "betting or calibration response"
  ],
  "keySources": [
    "SRC168",
    "SRC169"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Weights the proposition more heavily in inference, prediction, and action selection.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "Moderate",
  "name": "Belief Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater confidence that the proposition is true.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "0–1 subjective probability or ordinal confidence scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Low"
}
```

Confidence attached to a particular proposition, distinct from factual accuracy, general credulity and source trust. Keep the proposition referent fixed: confidence in a false claim versus its negation have opposite directions.

Perceived-truth ratings are defensible bounded indicators of belief confidence, not knowledge or calibrated probability. Metacognitive Confidence overlaps when explicitly about the same belief.

Exposure studies support tested sessions/delays only; no lifetime belief change inferred.

PSY-003/PSY-116 same-belief scope may be a duplicate representation; do not merge definitions or propagate both without reconciliation.

Boundary references: PSY-063, PSY-067, PSY-113, PSY-116, PSY-118. Sources: SRC168, SRC169, SRC-CAND-PSY-LAYER-0001, SRC-CAND-PSY-LAYER-0002, SRC-433, SRC-CAND-PSY-LAYER-0007.

### PSY-004 — Outcome Expectancy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Unipolar continuous",
  "definition": "The judged likelihood that performing a specified action will produce a specified consequence.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC110; SRC111.",
  "evidenceStrength": "Strong",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-004",
  "indicators": [
    "Probability judgments",
    "consequence-belief items",
    "expectancy ratings"
  ],
  "keySources": [
    "SRC110",
    "SRC111"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Links action to anticipated consequences, altering expected value and action selection.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "Moderate",
  "name": "Outcome Expectancy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater expected likelihood of the specified consequence.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "0–1 probability; 0–100%; low–high expectancy",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Low"
}
```

Probability of an action producing a named outcome, not desirability, probability of completing the action, or reinforcement value. The outcome can be aversive.

A belief-based attitude index includes outcome expectancy by construction; compare independently measured attitude before interpreting an effect.

Specify feedback/learning before subsequent probability judgment; theory alone supplies no causal lag.

Reinforcement Expectancy combines probability and value; Observationally Learned Expectancy specifies acquisition route. Neither is automatically an independent cause of the broader construct.

Boundary references: PSY-005, PSY-006, PSY-010, PSY-073, PSY-074. Sources: SRC110, SRC111, SRC112.

### PSY-005 — Outcome Valuation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Bipolar continuous",
  "definition": "The subjective desirability or aversiveness assigned to a specified possible outcome.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC110; SRC113.",
  "evidenceStrength": "Strong",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-005",
  "indicators": [
    "Valence ratings",
    "willingness to trade",
    "approach or avoidance preference"
  ],
  "keySources": [
    "SRC110",
    "SRC113"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Weights expected consequences in preference formation, motivation, and choice.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "Moderate",
  "name": "Outcome Valuation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Negative values = aversive; positive values = desirable.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "Negative–neutral–positive valuation; utility or willingness-to-pay measure",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Low"
}
```

Desirability of a specified possible outcome, not probability of obtaining it or expected utility of an action. Food pleasantness may index a narrow outcome but not all motivational value.

Willingness to pay bundles resource constraints and trade-offs; consumption frequency is not a direct value score. Avoid formula-derived attitude double counting.

Within-meal sensory-specific change is transient, not a durable change in abstract values.

Canonical contextual meaning must be specified before transfer from food pleasantness to generic outcome valuation.

Boundary references: PSY-001, PSY-004. Sources: SRC110, SRC113, SRC-CAND-PSY-LAYER-0005.

### PSY-006 — Success Expectancy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Unipolar continuous",
  "definition": "The judged likelihood of successfully completing a specified task or attaining a specified goal.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC108; SRC111; SRC118.",
  "evidenceStrength": "Strong",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-006",
  "indicators": [
    "Predicted success",
    "effort choice",
    "persistence expectation"
  ],
  "keySources": [
    "SRC108",
    "SRC111",
    "SRC118"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Changes expected return on effort and willingness to initiate or persist.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "Moderate",
  "name": "Success Expectancy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater expected probability of success.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "0–1 probability; 0–100%; ordinal likelihood",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Low"
}
```

Probability of completing a task/goal. Self-Efficacy concerns ability to execute an action under conditions; the two can coincide for a tightly specified success criterion but must not be declared identical.

Predicted success is direct; effort choice and persistence are outcomes/proxies. Incentives and motivation can contaminate can-do judgments.

Feedback-related task expectancy is not a stable optimistic disposition; timing and task difficulty must align.

No exact aligned feedback effect sufficiently extracted yet; causal isolation does not justify an edge.

Boundary references: PSY-011, PSY-012. Sources: SRC108, SRC111, SRC118, SRC112.

### PSY-007 — Perceived Relevance

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a favorable belief or attitude as sufficient for behavior despite capability, opportunity, habits, or competing goals.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a cue, issue, outcome, or action is judged pertinent to the person's current goals, identity, needs, or situation.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC117; SRC156.",
  "evidenceStrength": "Moderate",
  "family": "Beliefs, Attitudes & Outcome Expectancies",
  "id": "PSY-007",
  "indicators": [
    "Attention",
    "elaboration",
    "relevance ratings",
    "recall priority"
  ],
  "keySources": [
    "SRC117",
    "SRC156"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Intention strength",
    "option preference",
    "effort allocation",
    "persistence",
    "information acceptance"
  ],
  "likelyUpstreamInfluences": [
    "Prior experience",
    "information exposure",
    "observed outcomes",
    "social evaluation",
    "affective response"
  ],
  "measurementAssessmentMethods": "Validated construct-specific scales; structured belief elicitation; choice or expectancy tasks; repeated assessment",
  "measurementCaveats": "Self-report may conflate evaluation, expectancy, and intention; behavior-specific wording and temporal alignment are essential.",
  "mechanism": "Increases allocation of attention and elaboration and changes the weight placed on associated information.",
  "moderatorsBoundaryConditions": "Behavioral specificity, direct experience, attitude accessibility, temporal stability, opportunity, and competing goals.",
  "modifiability": "High",
  "name": "Perceived Relevance",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater judged personal or task relevance.",
  "primaryFamilyId": "PSY-F01",
  "relatedFamilyIds": [],
  "representationScale": "Low–high relevance rating; relevance probability",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Metacognitive Confidence",
    "Perceived Descriptive Norm",
    "Self-Efficacy",
    "Outcome Valuation"
  ],
  "volatility": "Moderate"
}
```

Judged pertinence to current goals/identity/situation, not stimulus salience, perceived argument quality, or mere exposure duration.

Attention/elaboration listed as indicators may also be downstream consequences; do not circularly measure relevance by its hypothesized effect.

Proposed near-term versus distant policy applicability manipulates a situation; perceived relevance and processing must be separately checked.

The 1981 experiment manipulates involvement and tests argument/source sensitivity; it does not directly establish every dimension of elaboration depth.

Boundary references: PSY-056, PSY-059, PSY-095, PSY-114. Sources: SRC-CAND-PSY-LAYER-0003, SRC156, SRC162.
