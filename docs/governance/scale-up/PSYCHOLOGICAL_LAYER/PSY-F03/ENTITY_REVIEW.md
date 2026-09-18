# PSY-F03 — Normative & Relational Perceptions

Audit `AUD-PSY-F03-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All 12 frozen canonical records, 20 RELATED_SEARCH aliases and empty crosswalk list reviewed. Generic upstream/downstream/interaction fields are research prompts, not evidence. Behavior/complaint/withdrawal indicators are not automatically the perception. Null subtype/qualifier fields and no blocked canonical fields remain unchanged; suggested source/construct issues are separate candidate questions.

No local RDS. Incoming REL-SOC-067 has external SOC-096 RDS: GROUP_A_STATUS + GROUP_B_STATUS + COMMON_SOCIAL_FIELD, difference/gap rule, aligned window and uncertainty. PSY-022 is not a formula input; genuine appraisal mechanism remains possible but must be temporally independent from status ratings. No formula-as-causality, exogenous-root assumption or direct RDS effect target.

### PSY-016 — Perceived Descriptive Norm

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Proportion",
  "definition": "The judged prevalence or frequency of a specified behavior among a relevant reference group.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC132; SRC170; SRC107.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-016",
  "indicators": [
    "Estimated prevalence",
    "perceived peer frequency",
    "norm-consistent intention"
  ],
  "keySources": [
    "SRC132",
    "SRC170",
    "SRC107"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Provides social evidence about typical action and can shift expectations and conformity.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Descriptive Norm",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater perceived prevalence of the behavior.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Estimated percentage; frequency distribution; low–high prevalence",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Judged prevalence/frequency of a specified behavior in a named reference group; not actual prevalence or perceived approval.

Estimated peer behavior needs denominator, period and referent. Own behavior and perceived norms can be reciprocally related; intention is not a norm indicator.

Momentary feedback and 3/6-month recall are different time scales; neither establishes a universal lag.

Weekly drink volume may not match frequency/prevalence without inspecting exact questionnaire; retained feedback effect stays research-needed.

Boundary references: PSY-017, SOC-001. Sources: SRC132, SRC170, SRC-CAND-PSY-LAYER-0019, SRC-CAND-PSY-LAYER-0024.

### PSY-017 — Perceived Injunctive Norm

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Bipolar continuous",
  "definition": "The judged degree to which relevant others approve or disapprove of a specified behavior.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC132; SRC110; SRC107.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-017",
  "indicators": [
    "Approval ratings",
    "anticipated sanction",
    "conformity intention"
  ],
  "keySources": [
    "SRC132",
    "SRC110",
    "SRC107"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Changes anticipated social consequences and perceived obligation to conform.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Injunctive Norm",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Negative values = disapproval; positive values = approval.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Strong disapproval–neutral–strong approval",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Judged approval/disapproval by specified others, not actual expressed approval or perceived behavior prevalence.

Sanction expectations, approval of behavior and approval of the actor are distinct; common referent/items can induce overlap.

Current approval judgments do not imply stable cultural norms changed.

Behavior outcomes from normative messages do not identify an isolated injunctive perception effect.

Boundary references: PSY-016, PSY-018, SOC-002. Sources: SRC132, SRC110, SRC107.

### PSY-018 — Anticipated Social Approval

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Bipolar continuous",
  "definition": "The expected amount of approval, acceptance, or positive regard from relevant others following a specified action.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC132; SRC170.",
  "evidenceStrength": "Moderate",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-018",
  "indicators": [
    "Expected praise",
    "anticipated acceptance",
    "social-reward rating"
  ],
  "keySources": [
    "SRC132",
    "SRC170"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Adds anticipated relational reward or cost to action valuation.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "High",
  "name": "Anticipated Social Approval",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater expected social approval.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Expected rejection–neutral–expected approval",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Expected relational approval after one's specified action; prospectively contingent, unlike others' current approval of behavior.

Expected acceptance and social reward require action/others specified. Need for approval is a motive, not the expectancy.

Canonical seconds–minutes onset is not an empirically estimated universal delay.

Assigned sources address self-other norm discrepancies or adolescent behavior associations, not exact anticipated-approval manipulation.

Boundary references: PSY-017, PSY-005. Sources: SRC132, SRC170.

### PSY-019 — Perceived Social Support

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Multidimensional",
  "definition": "The degree to which emotional, informational, or instrumental support is judged available from others when needed.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC134; SRC108.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-019",
  "indicators": [
    "Support-availability ratings",
    "help-seeking expectation",
    "named support sources"
  ],
  "keySources": [
    "SRC134",
    "SRC108"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Changes coping resources, help seeking, perceived feasibility, and persistence under stress.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Social Support",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater perceived availability or adequacy of support.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Subscale profile or overall low–high availability",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Judged availability of emotional/informational/instrumental help; not help received or network size.

Support subscales can overlap coping-scale support-seeking items. Objective contacts do not validate perceived availability.

Brief offer, months-long package and chronic network resources require separate assessments.

Broad interventions do not identify one exact support operation; reuse F02 REL-PSY-016 review and shared CF-0010.

Boundary references: PSY-014, PSY-020. Sources: SRC134, SRC108, SRC-CAND-PSY-LAYER-0026.

### PSY-020 — Perceived Belonging

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person feels accepted, included, and connected within a relevant relationship or group.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC135; SRC108.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-020",
  "indicators": [
    "Belonging ratings",
    "inclusion language",
    "affiliation or withdrawal"
  ],
  "keySources": [
    "SRC135",
    "SRC108"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Alters affiliation, conformity, withdrawal, and the value of group-related outcomes.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Belonging",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = stronger felt inclusion and connection.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Low–high belonging; momentary or chronic scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Felt acceptance/inclusion/connection with a relevant group; distinguish need for belonging, loneliness and perceived exclusion.

Need-threat belonging items such as outsider wording overlap exclusion checks. Do not infer independent causal mediation from their inverse scores.

Transient game ratings cannot establish chronic inclusion or changes to relational ties.

No automatic conversion of exclusion effect into a separate independent belonging contribution.

Boundary references: PSY-024, PSY-019. Sources: SRC135, SRC221, SRC-CAND-PSY-LAYER-0020.

### PSY-021 — Interpersonal Trust

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Unipolar continuous",
  "definition": "The willingness to accept vulnerability based on positive expectations about a specified person's intentions or behavior.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC136; SRC109.",
  "evidenceStrength": "Moderate",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-021",
  "indicators": [
    "Trust ratings",
    "reliance choices",
    "disclosure or delegation"
  ],
  "keySources": [
    "SRC136",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Reduces perceived transaction risk and supports cooperation, disclosure, and reliance.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Interpersonal Trust",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater willingness to rely on the person under vulnerability.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Low–high trust; probability of reliable or benevolent conduct",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Willingness to accept vulnerability toward a specified person, not generalized trust, institutional trust or factual accuracy.

Trust-game transfer bundles risk preference, altruism and strategic expectation. Neurochemical proxies do not define trust.

Relationship history differs from immediate transfer choice; enduring change not inferred from a task.

Oxytocin and thermal-cue research cannot support a universal exact-person trust effect; source-trust lesson retained.

Boundary references: PSY-134, PSY-118. Sources: SRC136, SRC109, SRC-CAND-PSY-LAYER-0022.

### PSY-022 — Perceived Fairness

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Multidimensional",
  "definition": "The degree to which a specified process, treatment, or allocation is judged fair according to relevant standards.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC133; SRC137.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-022",
  "indicators": [
    "Justice ratings",
    "acceptance",
    "complaint or retaliation intention"
  ],
  "keySources": [
    "SRC133",
    "SRC137"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Shapes acceptance, trust, obligation, cooperation, and retaliatory motivation.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Fairness",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater perceived fairness.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Procedural, distributive, interpersonal, and informational justice subscales",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Judgment of fairness of a named procedure, allocation or treatment; explicitly multidimensional.

Procedural/distributive/interpersonal/informational facets are correlated but not interchangeable; acceptance and retaliation are outcomes.

Post-encounter judgment differs from long institutional history; no generic hours–years effect estimated.

Feature-specific effects cannot become whole-profile improvement; architecture escalation linked to existing feature-scope issue, not repaired.

Boundary references: PSY-023, PSY-133, SOC-096. Sources: SRC133, SRC137, SRC-503.

### PSY-023 — Perceived Legitimacy

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which an authority, institution, rule, or decision is judged rightful and entitled to voluntary deference.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC137; SRC133.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-023",
  "indicators": [
    "Legitimacy ratings",
    "felt duty",
    "voluntary compliance intention"
  ],
  "keySources": [
    "SRC137",
    "SRC133"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Supports voluntary compliance by transforming external demands into felt obligation or accepted authority.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Legitimacy",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater perceived rightfulness and entitlement to deference.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Low–high legitimacy; obligation-to-obey scale",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Rightfulness and entitlement to voluntary deference for a specified authority/rule.

Obligation-to-obey, trust, satisfaction and behavioral compliance differ; conflating them can manufacture fairness→legitimacy evidence.

Compliance intention measured with legitimacy simultaneously does not establish direction.

Policing review's specific legitimacy outcome was not statistically conclusive; no rebranding of trust benefit as legitimacy.

Boundary references: PSY-134, PSY-022, PSY-026. Sources: SRC137, SRC133, SRC-503.

### PSY-024 — Perceived Social Exclusion

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a person perceives that relevant others are ignoring, rejecting, or excluding them.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC135; SRC172.",
  "evidenceStrength": "Moderate",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-024",
  "indicators": [
    "Exclusion ratings",
    "rejection cues noticed",
    "affiliation or withdrawal response"
  ],
  "keySources": [
    "SRC135",
    "SRC172"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Threatens belonging and control, altering affiliation, withdrawal, aggression, or norm sensitivity.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "High",
  "name": "Perceived Social Exclusion",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = stronger perceived rejection or exclusion.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Low–high exclusion or ostracism intensity",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Perception of being ignored/rejected/excluded by relevant others; not actual ostracism exposure.

Ignored/excluded ratings directly align in bounded Cyberball tasks; percentage of tosses is a different manipulation check.

Immediate retrospective game rating supports transient state only, not chronic exclusion or future withdrawal.

Existing REL-SOC-062 is the exposure route; avoid duplicating it or treating this perception as experimentally isolated mediator.

Boundary references: PSY-020, SOC-031. Sources: SRC135, SRC172, SRC221, SRC-CAND-PSY-LAYER-0020, SRC-CAND-PSY-LAYER-0021.

### PSY-025 — Perceived Status

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating perceived norms, trust, or support as direct measures of what the group actually does or provides.",
  "dataType": "Ordinal",
  "definition": "The degree of rank, prestige, respect, or influence a person believes they hold in a relevant group or relationship.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC173; SRC109.",
  "evidenceStrength": "Moderate",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-025",
  "indicators": [
    "Subjective rank",
    "expected deference",
    "status-protective behavior"
  ],
  "keySources": [
    "SRC173",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Conformity",
    "cooperation",
    "help seeking",
    "compliance",
    "withdrawal",
    "collective action"
  ],
  "likelyUpstreamInfluences": [
    "Observed behavior",
    "social communication",
    "relationship history",
    "group cues",
    "institutional conduct"
  ],
  "measurementAssessmentMethods": "Perception scales; vignette and scenario tasks; social-network informed surveys; experience sampling",
  "measurementCaveats": "Perceived social conditions are not interchangeable with measured group conditions and can vary by reference group.",
  "mechanism": "Changes deference, entitlement, risk tolerance, voice, and sensitivity to status threat.",
  "moderatorsBoundaryConditions": "Reference-group identification, norm visibility, relationship stakes, power, culture, and perceived enforcement.",
  "modifiability": "Moderate",
  "name": "Perceived Status",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Can update quickly after salient evidence but often persists through selective exposure and relationship history.",
  "polarityDirection": "Higher values = greater perceived social standing or influence.",
  "primaryFamilyId": "PSY-F03",
  "relatedFamilyIds": [],
  "representationScale": "Low–high rank; ladder or comparative standing",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Hours–Days"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Social Identification Strength",
    "Perceived Legitimacy",
    "Anticipated Social Approval",
    "Perceived Fairness"
  ],
  "volatility": "Moderate"
}
```

Perceived rank/prestige/respect/influence in specified group; not objective income or cross-group status gap.

Subjective SES ladder only partly aligns; health self-report associations are stronger than biological outcomes and mostly cross-sectional.

Stable rank histories and immediate rank feedback are not the same manipulation/time scale.

No exact effect or causal health edge retained from a subjective-SES association.

Boundary references: SOC-096, PSY-133. Sources: SRC173, SRC109.

### PSY-133 — Group-Based Relative Deprivation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Do not treat Group-Based Relative Deprivation as interchangeable with PSY-022; PSY-097; SOC-096 or as a universal, context-free cause.",
  "dataType": "Magnitude / level",
  "definition": "Perceived unjust disadvantage of one's group relative to a salient comparison group or reference condition.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Group comparison plus perceived injustice is not represented by generic fairness and is a supported collective-action mediator.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-133",
  "indicators": [
    "Construct-valid indicators of group-based relative deprivation measured for the specified unit, setting, and reference period"
  ],
  "keySources": [
    "SRC-500",
    "SRC-501"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Anger",
    "collective action",
    "intergroup attitudes",
    "institutional trust"
  ],
  "likelyUpstreamInfluences": [
    "Material inequality",
    "status comparison",
    "identity salience",
    "framing"
  ],
  "measurementAssessmentMethods": "Use a validated construct-specific instrument, administrative or sensor measure, or transparent composite with explicit unit and reference period.",
  "measurementCaveats": "Feasible With Explicit Unit; proxy measures require construct-validity review.",
  "mechanism": "Comparison plus perceived injustice and affect can motivate collective action, hostility, withdrawal, or support for change.",
  "moderatorsBoundaryConditions": "Interpret only for the specified population, unit, setting, exposure, reference period, and measurement method; effects may vary across contexts.",
  "modifiability": "Moderate",
  "name": "Group-Based Relative Deprivation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Mixed / Context-dependent"
  ],
  "persistenceRecovery": "Persistence and recovery depend on exposure, baseline state, intervention, and system feedback.",
  "polarityDirection": "Higher values = greater group-based relative deprivation.",
  "primaryFamilyId": "PSY-F03",
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
    "Material inequality",
    "status comparison",
    "Anger",
    "collective action"
  ],
  "volatility": "Moderate"
}
```

Perceived unjust disadvantage of one's group relative to salient comparison; not an objective inequality statistic.

Canonical definition lacks an explicit angry-resentment item although key review's RD operationalizations often include affect. Group and individual RD must not be pooled.

Comparison, injustice and affect are often measured together; narrative mediator language is not pathway identification.

Do not repair definition or manufacture a causal anger edge partly entailed by an affect-containing measure.

Boundary references: PSY-022, SOC-096. Sources: SRC-500, SRC-501.

### PSY-134 — Institutional Trust

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Do not treat Institutional Trust as interchangeable with PSY-021; PSY-023; PSY-118 or as a universal, context-free cause.",
  "dataType": "Magnitude / level",
  "definition": "Current expectation that a specified institution will act competently, reliably, fairly, openly, and with integrity.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "The object is an institution, unlike interpersonal or source trust; it bridges institutional performance to compliance and cooperation.",
  "evidenceStrength": "Strong",
  "family": "Normative & Relational Perceptions",
  "id": "PSY-134",
  "indicators": [
    "Construct-valid indicators of institutional trust measured for the specified unit, setting, and reference period"
  ],
  "keySources": [
    "SRC-502",
    "SRC-503",
    "SRC-504"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Compliance",
    "legitimacy",
    "information acceptance",
    "participation"
  ],
  "likelyUpstreamInfluences": [
    "Service performance",
    "fairness",
    "corruption",
    "transparency",
    "experience"
  ],
  "measurementAssessmentMethods": "Use a validated construct-specific instrument, administrative or sensor measure, or transparent composite with explicit unit and reference period.",
  "measurementCaveats": "Feasible With Explicit Unit; proxy measures require construct-validity review.",
  "mechanism": "Trust changes compliance, information acceptance, cooperation, and willingness to rely on institutional action.",
  "moderatorsBoundaryConditions": "Interpret only for the specified population, unit, setting, exposure, reference period, and measurement method; effects may vary across contexts.",
  "modifiability": "Moderate",
  "name": "Institutional Trust",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Mixed / Context-dependent"
  ],
  "persistenceRecovery": "Persistence and recovery depend on exposure, baseline state, intervention, and system feedback.",
  "polarityDirection": "Higher values = greater institutional trust.",
  "primaryFamilyId": "PSY-F03",
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
    "Service performance",
    "fairness",
    "Compliance",
    "legitimacy"
  ],
  "volatility": "Moderate"
}
```

Current expectations of specified institution's competence/reliability/fairness/openness/integrity; neither person trust nor rightful authority.

OECD perception composites and coarse WGI aggregates do not independently identify real institutional changes. Survey shared method and reciprocal judgment matter.

Cross-sectional trust regressions do not establish time ordering; corruption-information experiments differ from actual corruption trajectories.

Information can reduce selected trust ratings without changing corruption or legitimacy; exact profile alignment remains unresolved.

Boundary references: PSY-021, PSY-023, PSY-118. Sources: SRC-502, SRC-503, SRC-504, SRC-CAND-PSY-LAYER-0023.
