# PSY-F02 — Risk, Threat & Coping Appraisal

Audit `AUD-PSY-F02-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

Every canonical field (definitions, aliases/crosswalks, mechanism, scales, indicators, time/persistence, measurement, sources and nulls) is frozen and inspected. Shared generic indicator/narrative fields do not substitute for construct-specific evidence. No repairs.

All nine actual members are Drivers; PSY-132 is the ninth. No Family RDS and no direct RDS effect.

### PSY-008 — Perceived Outcome Likelihood

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The subjective probability that a specified adverse or beneficial outcome will occur under stated conditions.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC124; SRC107.",
  "evidenceStrength": "Strong",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-008",
  "indicators": [
    "Probability estimate",
    "susceptibility rating",
    "preparedness intention"
  ],
  "keySources": [
    "SRC124",
    "SRC107"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Changes expected costs and benefits and therefore vigilance, preparation, avoidance, or pursuit.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "High",
  "name": "Perceived Outcome Likelihood",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater judged likelihood of the specified outcome.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "0–1 probability; percentage; ordinal likelihood",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Moderate"
}
```

Conditional probability of a specified outcome, including beneficial outcomes; only adverse-outcome scopes can support the fear edge.

Conditional susceptibility differs from unconditional risk, emotional worry, response effectiveness and success expectancy.

Minutes–hours is a metadata band, not an estimated universal delay; illness risk assessments depend on future interval.

No repair of generic indicators (preparedness intention is an outcome, not a probability measure).

Boundary references: PSY-004, PSY-006, PSY-009. Sources: SRC124, SRC-CAND-PSY-LAYER-0010, SRC-CAND-PSY-LAYER-0014.

### PSY-009 — Perceived Threat Severity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Magnitude / level",
  "definition": "The judged magnitude of harm or seriousness associated with a specified threat outcome.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC124; SRC137.",
  "evidenceStrength": "Strong",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-009",
  "indicators": [
    "Severity rating",
    "anticipated harm",
    "prioritization of protective action"
  ],
  "keySources": [
    "SRC124",
    "SRC137"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Raises the subjective cost of exposure and can increase protective motivation when coping is judged feasible.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "High",
  "name": "Perceived Threat Severity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived seriousness or harm.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "Low–high severity; expected loss magnitude; multidomain severity profile",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Moderate"
}
```

Perceived seriousness of a named adverse outcome, not likelihood, objective hazard or emotional fear.

Severity profiles may have multiple harm dimensions; use named dimension/aggregate specification. Vaccine review's severity non-detection cannot imply zero.

Immediate appraisal and longer persistence must be measured separately; no stable trait inferred.

SRC124 identifier conflict and SRC137 policing-legitimacy source alignment unresolved.

Boundary references: PSY-008, PSY-041. Sources: SRC124, SRC137, SRC-423, SRC-CAND-PSY-LAYER-0014.

### PSY-010 — Response Efficacy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a specified response is believed capable of reducing a threat or producing its intended protective effect.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC124; SRC107.",
  "evidenceStrength": "Strong",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-010",
  "indicators": [
    "Effectiveness rating",
    "intervention choice",
    "expected risk reduction"
  ],
  "keySources": [
    "SRC124",
    "SRC107"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Determines whether a proposed action is represented as instrumentally useful.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "Moderate",
  "name": "Response Efficacy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater expected effectiveness of the response.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "0–1 expected effectiveness; low–high efficacy",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Low"
}
```

Expected effectiveness of a protective response, not capability to perform it. Related to action-outcome expectancy under protective scope.

Information asserting efficacy and a respondent's appraisal are separate; intention/behavior effects alone are not direct efficacy evidence.

Belief updating can be rapid despite days–weeks metadata; no automatic rewrite of time scale.

Broad literature mixes self/response efficacy and message content; no compound mechanism from marginal meta-regression.

Boundary references: PSY-004, PSY-011, SOC-077. Sources: SRC124, SRC-CAND-PSY-LAYER-0015, SRC-CAND-PSY-LAYER-0017.

### PSY-011 — Self-Efficacy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person believes they can successfully execute a specified action under relevant conditions.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC111; SRC112; SRC107.",
  "evidenceStrength": "Strong",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-011",
  "indicators": [
    "Capability confidence",
    "task choice",
    "effort and persistence"
  ],
  "keySources": [
    "SRC111",
    "SRC112",
    "SRC107"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Alters action choice, effort, persistence, and recovery from setbacks through perceived capability.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "Moderate",
  "name": "Self-Efficacy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater perceived personal capability.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "Behavior-specific 0–100 confidence items; low–high capability",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Low"
}
```

Task-specific perceived capability, not actual skill, probability of any outcome, or general trait confidence.

Can-do questions may reflect incentive motivation as well as capability; task choice/persistence are outcomes and not identical to the construct.

Learning may alter task-specific capability belief, not enduring personality. Within-person change cannot be inferred from between-person prediction.

CF-PSY-LAYER-0002 remains unresolved; no merger with success expectancy.

Boundary references: PSY-006, PSY-012, PSY-014. Sources: SRC111, SRC112, SRC107.

### PSY-012 — Perceived Behavioral Control

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The judged ease or difficulty of performing a specified behavior, including perceived control over internal and external constraints.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC110; SRC107.",
  "evidenceStrength": "Strong",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-012",
  "indicators": [
    "Control ratings",
    "perceived ease",
    "initiation expectation"
  ],
  "keySources": [
    "SRC110",
    "SRC107"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Shapes intention and can predict action when it tracks actual control.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "High",
  "name": "Perceived Behavioral Control",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived control or ease.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "Very difficult–very easy; no control–complete control",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Moderate"
}
```

Judged ease/control of performing the behavior, including external constraints. Distinguish control over performance from control over consequences.

Ease, capacity and opportunity items can load differently; do not assume all match the self-efficacy synthesis or formula-based indirect PBC score.

Momentary judged feasibility can change with resources; causal persistence not specified by canonical onset band.

Need dimension-specific construct measures and actual-opportunity conditions for existing positive intention claim.

Boundary references: PSY-011, PSY-013. Sources: SRC110, SRC107, SRC112.

### PSY-013 — Perceived Controllability

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The judged degree to which a specified situation or outcome can be influenced by one's actions or available responses.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC124; SRC122.",
  "evidenceStrength": "Moderate",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-013",
  "indicators": [
    "Control appraisal",
    "action–outcome contingency rating",
    "coping choice"
  ],
  "keySources": [
    "SRC124",
    "SRC122"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Changes coping selection, effort, stress appraisal, and willingness to act.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "High",
  "name": "Perceived Controllability",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived ability to influence the situation or outcome.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "No control–complete control; low–high influence",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Moderate"
}
```

Judged influence over a specified situation/outcome. A real or modeled control affordance is not the perception itself.

Meine task-control item reasonably aligns only when the specified situation is that task, not specifically stressor termination or generic life agency. Privacy limited control is not whole privacy security.

Momentary repeated task ratings cannot establish days/months of control or chronic stress resilience.

No new production controller-state Driver; existing technology affordances require independent usage/awareness measures.

Boundary references: PSY-012, PSY-015. Sources: SRC-CAND-PSY-LAYER-0013, SRC-CAND-PSY-LAYER-0018, SRC122.

### PSY-014 — Coping Self-Efficacy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The belief that one can deploy effective cognitive, emotional, or behavioral responses to manage a specified stressor.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC111; SRC121.",
  "evidenceStrength": "Moderate",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-014",
  "indicators": [
    "Coping confidence",
    "strategy use",
    "persistence under stress"
  ],
  "keySources": [
    "SRC111",
    "SRC121"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Supports engagement and adaptive coping while reducing helpless or avoidant responses.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "Moderate",
  "name": "Coping Self-Efficacy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater perceived ability to cope effectively.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "Situation-specific low–high confidence scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Low"
}
```

Confidence in deploying coping responses to a specified stressor; narrower than general self-efficacy but not a synonym for low helplessness.

Coping scale contains problem/emotion/support facets; validation does not identify an independent causal mediator. CET package must be distinguished from its components.

Three-month trial follow-up differs from immediate manipulation; pre-HAART clinical setting is not a current universal treatment effect.

Source and facet-specific fidelity/completeness needed before a broad effect candidate can be review-ready.

Boundary references: PSY-011, PSY-015, PSY-019. Sources: SRC-CAND-PSY-LAYER-0011, SRC-CAND-PSY-LAYER-0012, SRC111, SRC121.

### PSY-015 — Perceived Helplessness

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assuming higher threat always increases protective action; low efficacy can instead produce denial, avoidance, or paralysis.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person expects that their actions will not meaningfully influence important outcomes in a specified context.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC109; SRC122.",
  "evidenceStrength": "Moderate",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-015",
  "indicators": [
    "Passivity",
    "disengagement",
    "low controllability judgments"
  ],
  "keySources": [
    "SRC109",
    "SRC122"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Protective intention",
    "vigilance",
    "avoidance",
    "coping selection",
    "fear and anxiety"
  ],
  "likelyUpstreamInfluences": [
    "Threat cues",
    "bodily sensations",
    "prior outcomes",
    "risk communication",
    "actual control and resources"
  ],
  "measurementAssessmentMethods": "Threat- and coping-appraisal scales; probability/severity elicitation; scenario tasks; repeated state assessment",
  "measurementCaveats": "Appraisals are domain- and time-specific and may diverge from objective hazard, actual skill, or actual control.",
  "mechanism": "Reduces initiation and persistence by weakening expected action–outcome contingency.",
  "moderatorsBoundaryConditions": "Response efficacy, personal capability, immediacy, uncertainty, prior experience, and resource availability.",
  "modifiability": "Moderate",
  "name": "Perceived Helplessness",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater expected ineffectiveness of personal action.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "Low–high helplessness; controllability-reversed scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Fear Intensity",
    "Response Efficacy",
    "Self-Efficacy",
    "Perceived Outcome Likelihood"
  ],
  "volatility": "Low"
}
```

Expectation that personal actions will not affect outcomes; not simply fatigue, current distress or a diagnostic disorder.

A single 'feeling helpless' rating may not establish expected action-outcome ineffectiveness. Reverse-coded controllability scales risk mechanical inverse duplication.

Transient experimental helplessness does not show persistent learned helplessness, depression or chronic trait change.

No causal edge solely between simultaneous inverse/self-report measures; exact future expectation indicator missing.

Boundary references: PSY-013, PSY-014. Sources: SRC-CAND-PSY-LAYER-0013, SRC109, SRC122.

### PSY-132 — Subjective Uncertainty

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Do not treat Subjective Uncertainty as interchangeable with PSY-131; INF-015; PSY-116 or as a universal, context-free cause.",
  "dataType": "Magnitude / level",
  "definition": "Current perceived lack of confidence about relevant states, causes, outcomes, or probabilities.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "A dynamic perceived-uncertainty state is distinct from PSY-131 intolerance of uncertainty and INF-015 disclosure.",
  "evidenceStrength": "Strong",
  "family": "Risk, Threat & Coping Appraisal",
  "id": "PSY-132",
  "indicators": [
    "Construct-valid indicators of subjective uncertainty measured for the specified unit, setting, and reference period"
  ],
  "keySources": [
    "SRC-494",
    "SRC-496",
    "SRC-505"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Information seeking",
    "anxiety",
    "confidence",
    "decision delay"
  ],
  "likelyUpstreamInfluences": [
    "Ambiguous information",
    "inconsistent sources",
    "novelty",
    "low knowledge"
  ],
  "measurementAssessmentMethods": "Use a validated construct-specific instrument, administrative or sensor measure, or transparent composite with explicit unit and reference period.",
  "measurementCaveats": "Feasible With Explicit Unit; proxy measures require construct-validity review.",
  "mechanism": "State uncertainty changes search, vigilance, delay, reliance on authorities, and susceptibility to closure cues.",
  "moderatorsBoundaryConditions": "Interpret only for the specified population, unit, setting, exposure, reference period, and measurement method; effects may vary across contexts.",
  "modifiability": "Moderate",
  "name": "Subjective Uncertainty",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Mixed / Context-dependent"
  ],
  "persistenceRecovery": "Persistence and recovery depend on exposure, baseline state, intervention, and system feedback.",
  "polarityDirection": "Higher values = greater subjective uncertainty.",
  "primaryFamilyId": "PSY-F02",
  "relatedFamilyIds": [],
  "representationScale": "Continuous or ordinal construct-specific measure with population, setting, reference period, and unit explicitly specified.",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": "Typical state-change speed is context-dependent; do not infer persistence from this band.",
  "typicalInteractionCandidates": [
    "Ambiguous information",
    "inconsistent sources",
    "Information seeking",
    "anxiety"
  ],
  "volatility": "Moderate"
}
```

Current uncertainty about specified states/causes/outcomes/probabilities, distinct from intolerance-of-uncertainty disposition or disclosure.

Model-derived irreducible uncertainty, entropy, confidence rating and experienced lack of confidence are not interchangeable. Generic sensor/administrative language in canonical measurement field is insufficient specificity.

Dynamic state changes in learning trials cannot silently adopt hours–days persistence; exact window required.

Measure/reference-object boundary needs human review; no repair of INF-F03 H20 or uncertainty architecture.

Boundary references: PSY-131, PSY-116, INF-015. Sources: SRC-CAND-PSY-LAYER-0016, SRC-494, SRC-496, SRC-505.
