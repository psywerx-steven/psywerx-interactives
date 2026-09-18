# PSY-F12 — Agency, Attribution & Moral Judgment

Audit `AUD-PSY-F12-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All ten complete canonical Driver records, aliases/crosswalks and eight incident claims read. Definition, mechanism, scale/direction, timing, modifiability/volatility, measurements, sources/narratives/interactions and missingness preserved. No source or canonical field repaired.

No Family RDS. Nominal attribution locus and relative value priorities are not universally ordered scalar effects; no RDS/RelationalState direct target.

### PSY-104 — Perceived Agency

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person experiences themselves as able to initiate and control actions that produce effects.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC197; SRC111.",
  "evidenceStrength": "Moderate",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-104",
  "indicators": [
    "Agency rating",
    "action-effect prediction",
    "voluntary initiation"
  ],
  "keySources": [
    "SRC197",
    "SRC111"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Supports intentional action, responsibility acceptance, and effort by representing oneself as an effective causal agent.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "High",
  "name": "Perceived Agency",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = stronger experienced authorship and control of action.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "Low–high sense-of-agency rating; action-effect binding measure",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Moderate"
}
```

Experience of initiating/controlling action and producing effects; not self-efficacy, legal responsibility or one implicit timing measure.

Binding, sensory attenuation and explicit agency can dissociate; no universal shorter-delay sign.

Minutes; action/feedback timing and learned delay distribution matter.

Canonical SRC197 PMID misresolves; intended DOI identified, no source repair. EA24 RN.

Boundary references: PSY-105, PSY-013. Sources: SRC197, SRC-CAND-PSY-LAYER-0139, SRC-CAND-PSY-LAYER-0142, SRC-CAND-PSY-LAYER-0143, SRC-CAND-PSY-LAYER-0146.

### PSY-105 — Responsibility Attribution

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a specified actor is judged responsible for producing or preventing an outcome.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC198.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-105",
  "indicators": [
    "Responsibility rating",
    "blame",
    "punishment or repair allocation"
  ],
  "keySources": [
    "SRC198"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Changes blame, sanction, forgiveness, compensation, and expectations for corrective action.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "Moderate",
  "name": "Responsibility Attribution",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Specific judgments can revise rapidly; convictions and attribution styles can persist much longer.",
  "polarityDirection": "Higher values = greater attributed responsibility.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "0–100% responsibility; low–high judgment",
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
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Moderate"
}
```

Attribution of responsibility for producing/preventing outcome; distinguish causal involvement, intention, blame and punishment.

Judgments use causal/mental-state information differently; controllability is not locus alone.

Minutes-hours; outcome knowledge and attribution order must be explicit.

No exact direct effect retained from helping/punishment judgments alone.

Boundary references: PSY-104, PSY-106, PSY-107. Sources: SRC198, SRC-CAND-PSY-LAYER-0152.

### PSY-106 — Causal Attribution Locus

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Nominal categorical",
  "definition": "The represented location of primary causal influence for an outcome, such as within the actor, situation, or another agent.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC163; SRC199.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-106",
  "indicators": [
    "Causal explanation coding",
    "intervention target",
    "attribution ratings"
  ],
  "keySources": [
    "SRC163",
    "SRC199"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Directs intervention, blame, learning, and prediction toward different causal targets.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "Moderate",
  "name": "Causal Attribution Locus",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Specific judgments can revise rapidly; convictions and attribution styles can persist much longer.",
  "polarityDirection": "Categories identify attributed causal locus and have no inherent ordering.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "Actor; situation; other agent; mixed, optionally with weights",
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
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Moderate"
}
```

Nominal attribution locus: actor, situation, other or mixed; not a stable locus-of-control trait.

Unordered categories cannot be scalar INCREASE/DECREASE; optional weights need an explicit comparison.

Situational attribution minutes-hours; not durable personality change.

SRC163 BIS/BAS does not validate attribution locus. No scalar effect forced.

Boundary references: PSY-105, PSY-107, PSY-014. Sources: SRC163, SRC-CAND-PSY-LAYER-0152.

### PSY-107 — Intentionality Attribution

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a specified outcome or action is judged to have been knowingly and purposefully produced.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC163; SRC198.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-107",
  "indicators": [
    "Intent rating",
    "blame",
    "punishment",
    "mental-state inference"
  ],
  "keySources": [
    "SRC163",
    "SRC198"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Increases moral blame and punitive response and alters prediction of future behavior.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "Moderate",
  "name": "Intentionality Attribution",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Specific judgments can revise rapidly; convictions and attribution styles can persist much longer.",
  "polarityDirection": "Higher values = greater attributed intentionality.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "Accidental–fully intentional; component profile of desire, belief, foresight, and control",
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
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Moderate"
}
```

Attribution of knowing/purposeful action; not the actor's actual intention or moral wrongness.

Desire, belief, foresight and control profile; side-effect judgment depends on culture/status, not universal harm rule.

Judgment after vignette information, not evidence of actor's earlier causal state.

Cross-cultural convenience comparisons not randomized culture effects; measure/profile scope unresolved.

Boundary references: PSY-105, PSY-106. Sources: SRC198, SRC-CAND-PSY-LAYER-0150, SRC-CAND-PSY-LAYER-0151.

### PSY-108 — Perceived Freedom Threat

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which a message, rule, or actor is perceived as illegitimately restricting behavioral or attitudinal freedom.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC128; SRC200.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-108",
  "indicators": [
    "Restriction rating",
    "anger",
    "resistance",
    "opposite-choice tendency"
  ],
  "keySources": [
    "SRC128",
    "SRC200"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Elicits motivational pressure to restore autonomy and increases resistance or opposite responding.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "High",
  "name": "Perceived Freedom Threat",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived restriction of freedom.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "None–high freedom-threat rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Moderate"
}
```

Perceived illegitimate restriction of behavioral/attitudinal freedom, not the objective restriction itself.

Four-item pressure/freedom-threat checks align more closely than surveillance scope or generic autonomy.

Immediate health-message appraisal; not assumed lasting restrictions.

Bounded high-control message EA23; social-value threat and bundled scripts constrain attribution.

Boundary references: PSY-032, PSY-109, PSY-100. Sources: SRC128, SRC200, SRC-CAND-PSY-LAYER-0136, SRC-CAND-PSY-LAYER-0156.

### PSY-109 — Psychological Reactance Intensity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Magnitude / level",
  "definition": "The current intensity of motivational arousal directed at restoring a freedom perceived to be threatened.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC128; SRC200.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-109",
  "indicators": [
    "Anger",
    "negative cognitions",
    "opposite choice",
    "noncompliance"
  ],
  "keySources": [
    "SRC128",
    "SRC200"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Increases message rejection, counterarguing, source derogation, or behavior that reasserts choice.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "High",
  "name": "Psychological Reactance Intensity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Typically transient to hours, but repeated appraisal or rumination can prolong the state.",
  "polarityDirection": "Higher values = stronger motivation to restore threatened freedom.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "None–high reactance; anger plus negative-cognition composite",
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
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "High"
}
```

Current motivational arousal to restore threatened freedom; not trait reactance or all oppositional behavior.

Anger/negative-cognition composite can contain target counterarguments; REL-PSY-048 part-whole risk.

Seconds-minutes/hours; measurement order not identified mediation.

Retype-review only; no whole composite causes its own indicator.

Boundary references: PSY-108, PSY-115, PSY-043. Sources: SRC128, SRC200, SRC-CAND-PSY-LAYER-0137, SRC-CAND-PSY-LAYER-0138.

### PSY-110 — Moral Conviction Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a position or preference is experienced as grounded in fundamental right and wrong.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC164; SRC160.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-110",
  "indicators": [
    "Moral-basis rating",
    "unwillingness to compromise",
    "action commitment"
  ],
  "keySources": [
    "SRC164",
    "SRC160"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Increases certainty, resistance to compromise, willingness to act, and intolerance of procedural outcomes viewed as immoral.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "Moderate",
  "name": "Moral Conviction Strength",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Often persists for days to months; updating depends on counterevidence and confidence.",
  "polarityDirection": "Higher values = stronger experience of the position as a moral imperative.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "Low–high moral-conviction scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Days–Weeks"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Low"
}
```

Attitude experienced as fundamental right/wrong; distinct from strength, correctness, religion and moral identity.

Moralization ratings, conviction, affect and behavior separate; longitudinal association not causal mediation.

Days-weeks with possible situational onset; enduring moralization needs repeated measurement.

CUL norms→individual conviction need level/timing/identification; existing F04/F05 reviews reused.

Boundary references: PSY-027, PSY-044, PSY-103, PSY-111. Sources: SRC164, SRC296, SRC-CAND-PSY-LAYER-0141.

### PSY-111 — Moral Obligation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of felt personal duty to perform or avoid a specified action because it is judged morally required.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC164; SRC130.",
  "evidenceStrength": "Moderate",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-111",
  "indicators": [
    "Duty ratings",
    "guilt anticipation",
    "principled intention"
  ],
  "keySources": [
    "SRC164",
    "SRC130"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Adds a deontic motive to action independent of instrumental outcome value or social approval.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "High",
  "name": "Moral Obligation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Persists while the goal remains valued and feasible; may decay or be revised after feedback.",
  "polarityDirection": "Higher values = stronger felt moral requirement.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "No duty–strong duty; action-specific obligation scale",
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
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Moderate"
}
```

Action-specific felt personal duty, not legal requirement, perceived approval or action frequency.

Norm-activation SEM and moral nudges' behavior outcomes do not directly establish felt obligation change.

Minutes-hours/days; intention and performed action are distinct.

Cross-sectional moral-obligation associations not causal pathways; direct action target uncertain.

Boundary references: PSY-110, PSY-017, PSY-103. Sources: SRC164, SRC-CAND-PSY-LAYER-0148, SRC-CAND-PSY-LAYER-0155.

### PSY-112 — Personal Value Priority

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Collapsing causation, intention, agency, responsibility, blame, and punishment into one undifferentiated moral judgment.",
  "dataType": "Ordinal",
  "definition": "The relative importance assigned to a specified trans-situational guiding value within the person's value hierarchy.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC165; SRC108.",
  "evidenceStrength": "Strong",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-112",
  "indicators": [
    "Value ranking",
    "value-congruent choices",
    "tradeoff decisions"
  ],
  "keySources": [
    "SRC165",
    "SRC108"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Blame",
    "punishment",
    "forgiveness",
    "resistance",
    "helping",
    "principled action"
  ],
  "likelyUpstreamInfluences": [
    "Observed conduct",
    "causal information",
    "intention cues",
    "freedom constraints",
    "norms",
    "consequences"
  ],
  "measurementAssessmentMethods": "Attribution and moral-judgment vignettes; agency scales; behavioral allocation tasks; repeated state assessment",
  "measurementCaveats": "Judgments vary with framing, culture, actor identity, outcome information, and distinctions among causation, intent, and responsibility.",
  "mechanism": "Shapes goal selection and evaluation by making value-congruent outcomes more important across situations.",
  "moderatorsBoundaryConditions": "Outcome severity, intent evidence, role expectations, power, group membership, culture, and accountability.",
  "modifiability": "Low",
  "name": "Personal Value Priority",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = greater priority relative to competing values.",
  "primaryFamilyId": "PSY-F12",
  "relatedFamilyIds": [],
  "representationScale": "Rank order; ipsative or normalized value-importance score",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Weeks–Months",
    "Months–Years"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Intentionality Attribution",
    "Responsibility Attribution",
    "Perceived Freedom Threat",
    "Moral Conviction Strength"
  ],
  "volatility": "Low"
}
```

Relative transsituational priority hierarchy of personal values, not temporary value salience.

Ordinal ranks and relative importance require specified value/comparator; rank numeral sign can invert importance.

Canonical weeks/months-years; four-week benevolence package evidence not permanent whole-hierarchy change.

Generic canonical persistence text questionable, retained. Positive four-week results not rejected, but package/profile effect RN.

Boundary references: PSY-103, PSY-110, PSY-095. Sources: SRC165, SRC-CAND-PSY-LAYER-0145, SRC-CAND-PSY-LAYER-0154.

### PSY-135 — Perspective-Taking Capacity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Do not treat Perspective-Taking Capacity as interchangeable with PSY-047; PSY-048 or as a universal, context-free cause.",
  "dataType": "Magnitude / level",
  "definition": "Current capacity to infer and represent another actor's viewpoint, knowledge, intentions, and constraints.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Cognitive perspective representation is distinct from affective empathic concern and supports multi-actor coordination models.",
  "evidenceStrength": "Moderate",
  "family": "Agency, Attribution & Moral Judgment",
  "id": "PSY-135",
  "indicators": [
    "Construct-valid indicators of perspective-taking capacity measured for the specified unit, setting, and reference period"
  ],
  "keySources": [
    "SRC-494",
    "SRC-495"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Attribution accuracy",
    "empathy",
    "cooperation",
    "conflict"
  ],
  "likelyUpstreamInfluences": [
    "Cognitive load",
    "knowledge",
    "motivation",
    "intergroup contact"
  ],
  "measurementAssessmentMethods": "Use a validated construct-specific instrument, administrative or sensor measure, or transparent composite with explicit unit and reference period.",
  "measurementCaveats": "Feasible With Explicit Unit; proxy measures require construct-validity review.",
  "mechanism": "Perspective taking affects attribution, coordination, empathy, negotiation, and interpretation of ambiguous action.",
  "moderatorsBoundaryConditions": "Interpret only for the specified population, unit, setting, exposure, reference period, and measurement method; effects may vary across contexts.",
  "modifiability": "Moderate",
  "name": "Perspective-Taking Capacity",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Mixed / Context-dependent"
  ],
  "persistenceRecovery": "Persistence and recovery depend on exposure, baseline state, intervention, and system feedback.",
  "polarityDirection": "Higher values = greater perspective-taking capacity.",
  "primaryFamilyId": "PSY-F12",
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
    "Cognitive load",
    "knowledge",
    "Attribution accuracy",
    "empathy"
  ],
  "volatility": "Moderate"
}
```

Current capacity to represent another's knowledge/viewpoint/intentions; not affective empathy or compliance with instructions.

Visual-task selection, interpersonal accuracy and confidence are distinct operationalizations; task transfer unproven.

Hours-days; acute sleep/task effects not enduring general capacity change.

Perspective instruction EA25 RN; conversation adds information rather than proving capacity change.

Boundary references: PSY-047, PSY-048, PSY-058. Sources: SRC-494, SRC-495, SRC-CAND-PSY-LAYER-0140, SRC-CAND-PSY-LAYER-0144, SRC-CAND-PSY-LAYER-0153.
