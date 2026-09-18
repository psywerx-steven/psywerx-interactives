# PSY-F13 — Epistemic Trust & Persuasion

Audit `AUD-PSY-F13-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All seven full canonical records and18 incident claims read, including external endpoint definitions/INF068 derivation, aliases and empty crosswalks. Scales, mechanisms, timing, measurements, sources, narratives/interactions and missingness retained. No canonical repair.

No Family RDS. External incoming INF-068 is ratio-derived Material Selective-Omission Degree, not a directly manipulated primitive. Denominator/materiality universe/presented-versus-available input and detection/temporal mechanism explicitly audited. No direct RDS effect.

### PSY-113 — Perceived Source Credibility

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Multidimensional",
  "definition": "The degree to which a specified source is judged knowledgeable, trustworthy, and appropriate to rely upon for a claim.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC117; SRC201.",
  "evidenceStrength": "Strong",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-113",
  "indicators": [
    "Credibility rating",
    "reliance choice",
    "belief update after source cue"
  ],
  "keySources": [
    "SRC117",
    "SRC201"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Changes the weight assigned to communicated information, especially when direct verification is difficult.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "Moderate",
  "name": "Perceived Source Credibility",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater judged credibility of the source.",
  "primaryFamilyId": "PSY-F13",
  "relatedFamilyIds": [],
  "representationScale": "Expertise, trustworthiness, and benevolence profile; overall credibility",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Moderate"
}
```

Perceiver-specific expertise, trustworthiness and reliance-appropriateness profile; not truth, source identity or facial attractiveness.

Source/study trustworthiness and expertise dimensions must be specified; benevolence and overall profile cannot be inferred from one rating.

Hours-days with possible immediate updates; uncertainty format and prior source context matter.

Existing INF-F03 governed bounded claim retained unchanged; no duplicate or calibration claim. General dimension scope escalation reused.

Boundary references: PSY-118, PSY-116, PSY-003. Sources: SRC201, SRC-CAND-PSY-LAYER-0161, SRC-CAND-PSY-LAYER-0165, SRC-551, SRC-552.

### PSY-114 — Perceived Argument Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which an argument is judged logically compelling, relevant, and evidentially supportive of its conclusion.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC117; SRC162.",
  "evidenceStrength": "Strong",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-114",
  "indicators": [
    "Argument rating",
    "conclusion acceptance",
    "thought valence"
  ],
  "keySources": [
    "SRC117",
    "SRC162"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Increases belief updating when the recipient is motivated and able to elaborate.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "High",
  "name": "Perceived Argument Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "May be transient or persist as a revised belief depending on elaboration, confidence, and reinforcement.",
  "polarityDirection": "Higher values = stronger perceived support for the conclusion.",
  "primaryFamilyId": "PSY-F13",
  "relatedFamilyIds": [],
  "representationScale": "Weak–strong argument rating; evidence-quality profile",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Moderate"
}
```

Judged logical/relevant/evidential support for a conclusion, not objective Evidence Quality.

Pretested strong/weak arguments, thought valence and acceptance can be circular; source162 is Need-for-Cognition measurement, not exact argument validity.

Immediate appraisal may persist; no automatic lasting belief update.

No isolated content-defined direct effect retained; preserve content/perception distinction and F01 existing review.

Boundary references: PSY-059, PSY-069, PSY-113. Sources: SRC117, SRC162, SRC-CAND-PSY-LAYER-0167.

### PSY-115 — Counterarguing Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Magnitude / level",
  "definition": "The amount and strength of thoughts generated to challenge, refute, or qualify a persuasive claim.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC131; SRC117.",
  "evidenceStrength": "Strong",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-115",
  "indicators": [
    "Thought-listing",
    "rebuttal quality",
    "reduced belief change"
  ],
  "keySources": [
    "SRC131",
    "SRC117"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Reduces acceptance by supplying alternative explanations and undermining message claims.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "High",
  "name": "Counterarguing Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "May be transient or persist as a revised belief depending on elaboration, confidence, and reinforcement.",
  "polarityDirection": "Higher values = more numerous or stronger counterarguments.",
  "primaryFamilyId": "PSY-F13",
  "relatedFamilyIds": [],
  "representationScale": "Thought count and quality; low–high counterarguing scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Moderate"
}
```

Amount and strength of generated rebuttal/qualification; not disagreement, reactance composite or belief rejection by definition.

Thought count/quality need separate measures; bogus feedback changes perceived thought type, not actual generated thoughts.

Seconds-minutes to hours; thought listing and downstream confidence measured separately.

F12 part-whole retype review reused; no independent cause inferred from self-reported cognition in composite.

Boundary references: PSY-109, PSY-117, PSY-069. Sources: SRC131, SRC117, SRC-CAND-PSY-LAYER-0163, SRC-CAND-PSY-LAYER-0167.

### PSY-116 — Metacognitive Confidence

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of confidence assigned to the accuracy or validity of a specified judgment, belief, or decision.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC168; SRC169; SRC156.",
  "evidenceStrength": "Strong",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-116",
  "indicators": [
    "Confidence rating",
    "calibration",
    "revision threshold",
    "advice taking"
  ],
  "keySources": [
    "SRC168",
    "SRC169",
    "SRC156"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Changes reliance, persistence, communication, and willingness to revise the underlying judgment.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "Moderate",
  "name": "Metacognitive Confidence",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = greater subjective confidence in the specified judgment.",
  "primaryFamilyId": "PSY-F13",
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
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Low"
}
```

Confidence in a specified judgment, not objective accuracy, calibration, sensitivity or general self-esteem.

Calibration can change without mean confidence; underconfidence correction, Brier score and meta-d metrics distinct.

Canonical days-weeks/low volatility versus trial-specific judgments; eight-session training is not universal lasting certainty.

EA26 RN scope/transfer; existing INF046 proposal pointer only. No unresolved prior-pilot repair.

Boundary references: PSY-068, PSY-003, PSY-002. Sources: SRC168, SRC169, SRC156, SRC-CAND-PSY-LAYER-0158, SRC-CAND-PSY-LAYER-0159, SRC-CAND-PSY-LAYER-0164.

### PSY-117 — Resistance Motivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Unipolar continuous",
  "definition": "The strength of motivation to defend an existing attitude or autonomy against an anticipated persuasive attempt.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC131; SRC128.",
  "evidenceStrength": "Strong",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-117",
  "indicators": [
    "Counterarguments",
    "message avoidance",
    "reduced attitude change"
  ],
  "keySources": [
    "SRC131",
    "SRC128"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Promotes scrutiny, counterarguing, selective exposure, and rehearsal of defenses.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "High",
  "name": "Resistance Motivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "May be transient or persist as a revised belief depending on elaboration, confidence, and reinforcement.",
  "polarityDirection": "Higher values = stronger motivation to resist persuasion.",
  "primaryFamilyId": "PSY-F13",
  "relatedFamilyIds": [],
  "representationScale": "Low–high resistance motivation; warning response",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Moderate"
}
```

Motivation to defend existing attitude/autonomy before persuasion; not successful resistance or induced counterarguments themselves.

Forewarning/inoculation effects on attitude outcomes not direct independent motivation measurement.

Immediate anticipated appeal versus delay/persistence; low involvement can generate preemptive agreement.

EA27 RN; no uniform warning effect or mediation from inferred threat.

Boundary references: PSY-109, PSY-108, PSY-115. Sources: SRC131, SRC128, SRC-CAND-PSY-LAYER-0162, SRC-CAND-PSY-LAYER-0163.

### PSY-118 — Epistemic Trust

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Unipolar continuous",
  "definition": "The willingness to treat information from a specified person or system as relevant, reliable, and generalizable beyond the immediate exchange.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC166; SRC136.",
  "evidenceStrength": "Moderate",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-118",
  "indicators": [
    "Information uptake",
    "advice weighting",
    "generalization of communicated claims"
  ],
  "keySources": [
    "SRC166",
    "SRC136"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Permits efficient social learning and belief updating when firsthand verification is costly.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "Moderate",
  "name": "Epistemic Trust",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater willingness to learn from and generalize the source's information.",
  "primaryFamilyId": "PSY-F13",
  "relatedFamilyIds": [],
  "representationScale": "Low–high epistemic-trust scale; reliance probability",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Moderate"
}
```

Willingness to use/generalize a specified source's information beyond one exchange; not all interpersonal trust or reliance behavior.

ETMCQ general stance/mistrust/credulity distinct from specified-source state; AI trust/reliance measures need exact alignment.

Hours-days/relationship history; cross-sectional adversity associations not causal development.

SRC166 wrong DOI unchanged. No therapy-effect or AI reliability→epistemic generalization shortcut.

Boundary references: PSY-021, PSY-113, PSY-135. Sources: SRC166, SRC136, SRC-CAND-PSY-LAYER-0160, SRC-474, SRC-CAND-PSY-LAYER-0170.

### PSY-119 — Perceived Information Sufficiency

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating source credibility or fluency as an objective property rather than a perceiver-specific judgment or cue.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which the information currently available is judged sufficient to make a specified decision or reach a conclusion.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC167; SRC119.",
  "evidenceStrength": "Moderate",
  "family": "Epistemic Trust & Persuasion",
  "id": "PSY-119",
  "indicators": [
    "Search stopping",
    "sufficiency rating",
    "decision readiness"
  ],
  "keySources": [
    "SRC167",
    "SRC119"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Belief updating",
    "acceptance",
    "rejection",
    "information search",
    "resistance",
    "sharing intention"
  ],
  "likelyUpstreamInfluences": [
    "Source cues",
    "argument content",
    "prior beliefs",
    "uncertainty",
    "warnings",
    "social endorsement"
  ],
  "measurementAssessmentMethods": "Credibility and argument-rating scales; belief-updating tasks; thought-listing; confidence calibration; search behavior",
  "measurementCaveats": "Acceptance can reflect source heuristics, content, fluency, prior belief, or social alignment; confidence is not equivalent to accuracy.",
  "mechanism": "Reduces additional search and increases readiness to decide or communicate a conclusion.",
  "moderatorsBoundaryConditions": "Prior belief, involvement, motivation, ability, source identity, message repetition, and accountability.",
  "modifiability": "High",
  "name": "Perceived Information Sufficiency",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater judged adequacy of available information.",
  "primaryFamilyId": "PSY-F13",
  "relatedFamilyIds": [],
  "representationScale": "Insufficient–fully sufficient; sufficiency gap",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Perceived Source Credibility",
    "Perceived Argument Strength",
    "Prior-Belief Congruence",
    "Need for Cognition"
  ],
  "volatility": "Moderate"
}
```

Perceived adequacy for a specified decision, not actual completeness, search stopping or nominal uncertainty alone.

Information adequacy five-item scale includes relevance/believability/trust; composite versus exact sufficiency item unresolved.

Minutes-hours/reversible; additional information can alter decisions/confidence without uniform adequacy change.

EA28 RN; external INF068 RDS denominator/universe and detection must be explicit; no direct RDS target.

Boundary references: PSY-130, PSY-116, PSY-061. Sources: SRC167, SRC119, SRC-CAND-PSY-LAYER-0157, SRC-CAND-PSY-LAYER-0169, SRC-CAND-PSY-LAYER-0168.
