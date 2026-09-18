# PSY-F05 — Affect & Emotion

Audit `AUD-PSY-F05-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All14 frozen Driver records,28 RELATED_SEARCH aliases and empty crosswalk reviewed; preserve definitions, mechanisms, scale, polarity/direction, modifiability, volatility, lag/time/persistence, indicators, methods, observability, caveats, evidence and narrative fields. No blocked canonical local fields found or repaired. Measurement/proxy, state/trait and current-versus-recall-window issues recorded.

No local RDS. All17 incident endpoints are Drivers, including external BIO-009, CUL-076, SOC-027 and SOC-082. PSY-078 remains a protected F09 RDS, not an effect target. No formula contribution or aggregate propagation introduced.

### PSY-041 — Fear Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of an emotion centered on imminent or concrete threat and action readiness to escape or protect.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC115; SRC175; SRC124.",
  "evidenceStrength": "Strong",
  "family": "Affect & Emotion",
  "id": "PSY-041",
  "indicators": [
    "Fear rating",
    "escape tendency",
    "threat-focused attention"
  ],
  "keySources": [
    "SRC115",
    "SRC175",
    "SRC124"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Prioritizes threat information and prepares avoidance or protective action, conditional on perceived efficacy and control.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Fear Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense fear.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme fear; repeated state rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Current response to an imminent/concrete threat, not diffuse anxiety or objective risk.

Fear/scared ratings differ from avoidance, startle and threat-appraisal scales; separate film narrative from actual danger.

Seconds/minutes after a specified threat; not an enduring trait.

Existing threat and risky-choice edges reused; composite reappraisal outcome does not establish a separate fear effect.

Boundary references: PSY-042, PSY-008, PSY-009, PSY-086. Sources: SRC115, SRC176, SRC147, SRC-CAND-PSY-LAYER-0046, SRC-CAND-PSY-LAYER-0047, SRC-CAND-PSY-LAYER-0048, SRC-CAND-PSY-LAYER-0058.

### PSY-042 — Anxiety Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of diffuse apprehension, tension, or uncertainty about possible future threat.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC147; SRC148; SRC115.",
  "evidenceStrength": "Strong",
  "family": "Affect & Emotion",
  "id": "PSY-042",
  "indicators": [
    "State-anxiety score",
    "worry",
    "vigilance",
    "avoidance"
  ],
  "keySources": [
    "SRC147",
    "SRC148",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Increases threat monitoring and worry while potentially consuming working-memory resources.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Anxiety Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense anxiety.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme state anxiety; validated state scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Apprehension/tension about uncertain future threat; not diagnosis, stable punishment sensitivity or intolerance of uncertainty.

STAI-state mixes calm/upset and tension; DASS anxiety emphasizes somatic symptoms, while task worry is narrower. Common-method overlap with trait scales remains.

Acute anxiety and four-week/trait outcomes separated.

Cyclic-sighing anxiety superiority not established; EA-0008 remains UNKNOWN/research-needed.

Boundary references: PSY-041, PSY-131, PSY-128, PSY-132, PSY-058. Sources: SRC123, SRC147, SRC148, SRC207, SRC-CAND-PSY-LAYER-0042, SRC-CAND-PSY-LAYER-0043, SRC-CAND-PSY-LAYER-0053.

### PSY-043 — Anger Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of anger arising from perceived offense, obstruction, injustice, or blame.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC115; SRC176.",
  "evidenceStrength": "Strong",
  "family": "Affect & Emotion",
  "id": "PSY-043",
  "indicators": [
    "Anger rating",
    "confrontation tendency",
    "hostile attribution"
  ],
  "keySources": [
    "SRC115",
    "SRC176"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Increases approach readiness, blame, risk acceptance, confrontation, and corrective action under some conditions.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Anger Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense anger.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme anger; state-anger scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Current anger about offense, obstruction, injustice or blame; not aggression or stable hostility.

Angry/irritated ratings can overlap frustration; hostile attribution and confrontational behavior are not independent measures of anger itself.

Episode-specific appraisal and later decisions require separation; regulation strategy is not available capacity.

Films can co-induce fear; no pure-anger assumption or universal risk preference effect.

Boundary references: PSY-052, PSY-079, PSY-101, PSY-086. Sources: SRC115, SRC121, SRC143, SRC144, SRC176, SRC-CAND-PSY-LAYER-0047, SRC-CAND-PSY-LAYER-0048, SRC-CAND-PSY-LAYER-0058.

### PSY-044 — Disgust Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of aversion associated with contamination, revulsion, or moralized rejection.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC115; SRC177.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-044",
  "indicators": [
    "Disgust rating",
    "avoidance distance",
    "rejection judgments"
  ],
  "keySources": [
    "SRC115",
    "SRC177"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Promotes avoidance, rejection, and boundary protection while biasing evaluation of associated targets.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Disgust Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense disgust.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme disgust; domain-specific rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Aversion/revulsion across contamination and moralized contexts; bodily and moral domains not identical.

Disgust adjective can express condemnation metaphorically; facial/nausea measures require alignment rather than semantic equivalence.

Immediate elicitation versus stable sensitivity and later judgment distinguished.

Moral-conviction→disgust sources misaligned; publication-bias-sensitive reverse-direction literature cannot validate it.

Boundary references: PSY-110, PSY-043. Sources: SRC177, SRC-CAND-PSY-LAYER-0049, SRC-CAND-PSY-LAYER-0046, SRC-CAND-PSY-LAYER-0047.

### PSY-045 — Shame Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of painful negative evaluation of the global self following actual or anticipated failure or exposure.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC178; SRC115.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-045",
  "indicators": [
    "Shame rating",
    "hiding",
    "withdrawal",
    "defensive anger"
  ],
  "keySources": [
    "SRC178",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Can motivate concealment, withdrawal, appeasement, or defensive externalization depending on coping options.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Shame Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense shame.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme shame; event-specific rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Negative evaluation of the global self under exposure/failure; not guilt about a specific act.

Shame/embarrassment grouped item is not a pure shame measure; proneness, self-evaluation and cultural display norms differ.

Current experience distinct from shame-proneness or years of socialization.

Source PMID mismatch flagged; cultural tightness not exact shame-regulation norm manipulation.

Boundary references: PSY-046, PSY-049, CUL-076. Sources: SRC178, SRC-498, SRC-CAND-PSY-LAYER-0052.

### PSY-046 — Guilt Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of negative evaluation of a specific action or omission for which the person feels responsible.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC178; SRC115.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-046",
  "indicators": [
    "Guilt rating",
    "apology",
    "repair or restitution intent"
  ],
  "keySources": [
    "SRC178",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Can motivate confession, repair, restitution, or avoidance when responsibility and repair feasibility are salient.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Guilt Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense guilt.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme guilt; event-specific rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Negative evaluation of one's specific act/omission and responsibility, not global defective self.

Guilt/remorse items, reparative intention and behavior are not identical; scenario manipulations can bundle harm, agency and norm cues.

Event-related guilt may persist, but hypothetical scenarios do not prove enduring moral change.

General induction review insufficient for a precisely operationalized guilt action/effect or guilt→repair pathway.

Boundary references: PSY-045, PSY-110. Sources: SRC178, SRC-CAND-PSY-LAYER-0046, SRC-CAND-PSY-LAYER-0052.

### PSY-047 — Sadness Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of sadness associated with perceived loss, helplessness, or unattained goals.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC115; SRC142.",
  "evidenceStrength": "Strong",
  "family": "Affect & Emotion",
  "id": "PSY-047",
  "indicators": [
    "Sadness rating",
    "reduced approach",
    "support seeking"
  ],
  "keySources": [
    "SRC115",
    "SRC142"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Changes reward valuation, information processing, withdrawal, and support seeking depending on context.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Sadness Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense sadness.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme sadness; state rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Current sadness in response to loss or unattained goals; not depression diagnosis or all unpleasantness.

DES sad/downhearted/blue aligns better than K6 depression/worthlessness or broad negative-affect totals. Film study extracted contrasts compare emotion profiles, not an isolated sadness-versus-neutral estimand.

Retrospective rating of feelings during clip is not day-long mood or later recovery.

EA-0009 remains research-needed pending exact clip/comparator contrast; no arbitrary universal film effect.

Boundary references: PSY-050, PSY-052. Sources: SRC-CAND-PSY-LAYER-0045, SRC-CAND-PSY-LAYER-0046, SRC-CAND-PSY-LAYER-0047, SRC-CAND-PSY-LAYER-0048, SRC-CAND-PSY-LAYER-0054.

### PSY-048 — Hope Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of positive expectation and affect that a valued future outcome remains attainable.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC179; SRC118.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-048",
  "indicators": [
    "Hope rating",
    "continued effort",
    "pathway generation"
  ],
  "keySources": [
    "SRC179",
    "SRC118"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Sustains approach and planning by maintaining perceived attainability of valued outcomes.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Hope Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense hope.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme hope; state rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Positive expectation/affect concerning a valued attainable future; not optimism trait or all goal agency/pathways.

Snyder-style agency/pathways scores and positive/hopeful compound items mix cognition/motivation with affect; no measure-as-construct equivalence.

Current hope differs from multi-session goal therapy and stable expectancy.

Candidate hypothesis only: exact affective component and goal/time referent unresolved.

Boundary references: PSY-004, PSY-026, PSY-027. Sources: SRC179, SRC-CAND-PSY-LAYER-0048, SRC-CAND-PSY-LAYER-0056.

### PSY-049 — Pride Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of positive self-evaluation linked to achievement, identity, or social recognition.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC180; SRC115.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-049",
  "indicators": [
    "Pride rating",
    "posture or display",
    "achievement persistence"
  ],
  "keySources": [
    "SRC180",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Reinforces identity-congruent achievement and can increase persistence, status behavior, or display.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Pride Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = more intense pride of the specified form.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme pride; authentic/hubristic subscales where needed",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Positive self-evaluation around achievement/identity/recognition; authentic and hubristic components not interchangeable.

Separate seven-item facet scales, state versus dispositional prompts and social display; PANAS proud item cannot establish all dimensions.

Achievement-episode response not stable disposition.

Intended source identified at PMID17352606, stored17352607 is a different paper. Facet-wide effect not inferred.

Boundary references: PSY-045, PSY-046. Sources: SRC180, SRC-CAND-PSY-LAYER-0052.

### PSY-050 — Mood Valence

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Bipolar continuous",
  "definition": "The overall pleasantness or unpleasantness of a person's current diffuse affective state.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC142; SRC115.",
  "evidenceStrength": "Strong",
  "family": "Affect & Emotion",
  "id": "PSY-050",
  "indicators": [
    "Valence rating",
    "positive/negative affect profile",
    "affect-congruent recall"
  ],
  "keySources": [
    "SRC142",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Acts as contextual information and changes attention, memory accessibility, valuation, and judgment strategy.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Mood Valence",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Negative values = more unpleasant mood; positive values = more pleasant mood.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "Negative–neutral–positive; repeated mood rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Diffuse current bipolar pleasantness/unpleasantness; not every positive emotion or life satisfaction.

PANAS positive affect includes activation/alertness, and negative affect is a separate scale. Their sum/difference is not automatically canonical valence; film study explicitly reports PA problems.

Momentary bipolar state versus retrospective week/month symptom composite distinguished.

No generic mood effect retained from PANAS, positive-composite reappraisal or cash-transfer happiness.

Boundary references: PSY-047, PSY-051, PSY-121. Sources: SRC142, SRC-CAND-PSY-LAYER-0042, SRC-CAND-PSY-LAYER-0045, SRC-CAND-PSY-LAYER-0047, SRC-CAND-PSY-LAYER-0048, SRC-CAND-PSY-LAYER-0053.

### PSY-051 — Subjective Arousal

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Unipolar continuous",
  "definition": "The consciously experienced level of activation, alertness, or agitation at a given time.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC142; SRC115.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-051",
  "indicators": [
    "Arousal rating",
    "activation language",
    "response vigor"
  ],
  "keySources": [
    "SRC142",
    "SRC115"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Changes action readiness and the intensity with which appraisals and emotions influence attention and choice.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Subjective Arousal",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = greater felt activation.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "Calm/low activation–high activation; arousal scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Consciously felt activation/alertness/agitation, not autonomic arousal.

Respiration, cortisol, heart rate, EMG and generic emotional intensity are not equivalent to subjective activation. Film 'no emotion–intense emotion' scale is an especially important proxy mismatch.

Momentary activation during exposure, not inferred from physiological recovery or trait measures.

Audience effect source bundle not exact evidence; no respiration→subjective-arousal shortcut.

Boundary references: BIO-009, PSY-050, SOC-082. Sources: SRC-CAND-PSY-LAYER-0042, SRC-CAND-PSY-LAYER-0047, SRC-CAND-PSY-LAYER-0053, SRC-509.

### PSY-052 — Frustration Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of aversive affect produced by blocked, delayed, or repeatedly unsuccessful goal pursuit.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC181; SRC118.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-052",
  "indicators": [
    "Frustration rating",
    "error escalation",
    "switching or quitting"
  ],
  "keySources": [
    "SRC181",
    "SRC118"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Increases switching, persistence, aggression, or disengagement depending on control and coping options.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Frustration Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = greater frustration.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "None–extreme frustration; event-specific scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Aversive affect from blocked/delayed goal pursuit; not obstruction itself or aggression.

Self-reported frustration differs from response force, speed, frowning and task performance; replication found divergent channels.

Proximity/effort before blockage and retrospective emotion after it; no dynamic trajectory from one report.

Real blockage may elicit frustration, but exact manipulated Driver missing; task-world operation and perceived goal conflict/difficulty not conflated.

Boundary references: PSY-043, PSY-029, PSY-030. Sources: SRC181, SRC-CAND-PSY-LAYER-0057, SRC-CAND-PSY-LAYER-0041.

### PSY-053 — Empathic Concern

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of other-oriented feelings of care and concern for a person perceived to be in need.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC145; SRC182.",
  "evidenceStrength": "Moderate",
  "family": "Affect & Emotion",
  "id": "PSY-053",
  "indicators": [
    "Concern rating",
    "helping allocation",
    "attention to need"
  ],
  "keySources": [
    "SRC145",
    "SRC182"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Raises the subjective value of relieving another person's need and can motivate helping.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Empathic Concern",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = stronger other-oriented concern.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "Low–high state concern; target-specific rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes",
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "High"
}
```

Other-oriented care and concern for another in need, not self-compassion, personal distress or emotion sharing.

IRI empathic-concern items, donation behavior, empathic accuracy and neural sharing are different. Compassion interventions may target self, others or both.

Current concern and multiweek habitual compassion outcomes require separate scope.

Review active-control conclusions differ; exact target of compassion/measurement unsettled. No generic meditation→concern effect.

Boundary references: PSY-037, PSY-019. Sources: SRC145, SRC182, SRC-CAND-PSY-LAYER-0050, SRC-CAND-PSY-LAYER-0051.

### PSY-054 — Perceived Stress

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Assigning a universal behavioral direction to an emotion; the same emotion can support different actions under different appraisals.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which current demands are appraised as unpredictable, uncontrollable, or exceeding available coping resources.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC146; SRC121.",
  "evidenceStrength": "Strong",
  "family": "Affect & Emotion",
  "id": "PSY-054",
  "indicators": [
    "Stress rating",
    "overload report",
    "coping change"
  ],
  "keySources": [
    "SRC146",
    "SRC121"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attention allocation",
    "risk appraisal",
    "approach or avoidance",
    "judgment",
    "communication",
    "action readiness"
  ],
  "likelyUpstreamInfluences": [
    "Situation appraisal",
    "goal progress",
    "social signals",
    "memory",
    "physiological state",
    "environmental conditions"
  ],
  "measurementAssessmentMethods": "Validated state scales; experience sampling; behavioral expression coding; multimethod assessment",
  "measurementCaveats": "Emotion labels, intensity, and expression vary across people and cultures; self-report, behavior, and physiology need not converge.",
  "mechanism": "Alters attention, coping, inhibition, and persistence through appraisal of overload and control.",
  "moderatorsBoundaryConditions": "Emotion intensity, regulation strategy, target, certainty, culture, time pressure, and current goals.",
  "modifiability": "High",
  "name": "Perceived Stress",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived demand-resource imbalance.",
  "primaryFamilyId": "PSY-F05",
  "relatedFamilyIds": [],
  "representationScale": "Low–high perceived stress; repeated state scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Emotion Regulation Capacity",
    "Subjective Arousal",
    "Perceived Controllability",
    "Attentional Salience"
  ],
  "volatility": "Moderate"
}
```

Appraisal that demands exceed coping resources, not cortisol or all negative affect.

PSS unpredictable/uncontrollable/overload appraisal differs from DASS stress/tension and K6 distress. PSS past-month aggregation cannot silently stand for a momentary scalar.

Canonical minutes/hours dynamics versus recalled past week/month, intervention follow-up and physiological recovery differ.

Cash-transfer appraisal finding promising but timing/context and spillovers require scoped follow-up; no physiology pathway or broad policy effect.

Boundary references: PSY-013, PSY-019, PSY-057, BIO-009, SOC-027. Sources: SRC146, SRC-CAND-PSY-LAYER-0043, SRC-CAND-PSY-LAYER-0044, SRC-CAND-PSY-LAYER-0055, SRC-CAND-PSY-LAYER-0054.
