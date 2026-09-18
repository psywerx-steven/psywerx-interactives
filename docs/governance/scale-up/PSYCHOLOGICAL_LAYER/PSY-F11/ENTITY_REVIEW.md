# PSY-F11 — Self-Concept, Identity & Consistency

Audit `AUD-PSY-F11-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All ten complete canonical Driver records,20 RELATED_SEARCH aliases and empty crosswalk read. Definitions, mechanisms, scales, direction, modifiability/volatility, timing, measurement, caveats, sources, narratives, interactions and missingness retained. No canonical fields repaired.

No Family RDS; identity profiles are not automatically RDS or freely scalar. No direct RDS or RelationalState target.

### PSY-094 — Behavioral Self-Identity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which performing a specified behavior is represented as part of who the person is.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC194; SRC130.",
  "evidenceStrength": "Moderate",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-094",
  "indicators": [
    "Self-description",
    "identity-consistent choices",
    "distress after inconsistency"
  ],
  "keySources": [
    "SRC194",
    "SRC130"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Increases value and consistency pressure for identity-congruent action.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "Low",
  "name": "Behavioral Self-Identity",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = stronger incorporation of the behavior into self-concept.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high behavior-specific identity scale",
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
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Low"
}
```

Behavior incorporated into self-definition, not the behavior, demographic membership or an assigned noun label.

Self-report identity and behavioral frequency/turnout differ; common method and past behavior can explain associations.

Canonical weeks/months-years change; brief cue onset does not prove lasting identity content.

Voter-wording positive and null field results do not establish independent durable Behavioral Self-Identity change.

Boundary references: PSY-095, PSY-096, PSY-026, PSY-070. Sources: SRC194, SRC130, SRC-CAND-PSY-LAYER-0125, SRC-CAND-PSY-LAYER-0132, SRC-CAND-PSY-LAYER-0135.

### PSY-095 — Identity Salience

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a particular identity is currently active and accessible in self-representation.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC159; SRC160.",
  "evidenceStrength": "Strong",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-095",
  "indicators": [
    "Identity-language accessibility",
    "self-categorization",
    "priming response"
  ],
  "keySources": [
    "SRC159",
    "SRC160"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Increases the weight of identity-linked norms, goals, and interpretations in current choice.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "High",
  "name": "Identity Salience",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater current activation of the identity.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high momentary salience; activation or accessibility index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Moderate"
}
```

Current identity accessibility, not enduring importance, fusion or group membership.

Manipulation assignment, self-categorization and independent accessibility measure separate; changed downstream behavior is not a manipulation check.

Minutes-hours, potentially reversible; no assumed durable trait effect.

No exact salience effect retained from turnout/vigilance alone; cue operation and psychological uptake differ.

Boundary references: PSY-094, PSY-096, PSY-097, PSY-056. Sources: SRC159, SRC160, SRC-CAND-PSY-LAYER-0125, SRC-CAND-PSY-LAYER-0126.

### PSY-096 — Identity Centrality

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a specified identity occupies a central and important position in a person's overall self-concept.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC159; SRC194.",
  "evidenceStrength": "Moderate",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-096",
  "indicators": [
    "Importance ratings",
    "cross-context identity use",
    "identity-protective choice"
  ],
  "keySources": [
    "SRC159",
    "SRC194"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Raises the stakes of identity-relevant outcomes and supports consistent action across contexts.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "Low",
  "name": "Identity Centrality",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = greater enduring importance to self-definition.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high identity-centrality scale",
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
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Low"
}
```

Enduring centrality of specified identity in overall self-concept, not momentary salience.

Centrality already a component of social-identification profile; shared items/definition could drive REL-PSY-065.

Weeks/months-years; generic source lag minutes does not establish rapid durable change.

Retype-review proposal for profile→component relation; no automatic noncausal replacement.

Boundary references: PSY-095, PSY-097, PSY-103. Sources: SRC159, SRC194, SRC-CAND-PSY-LAYER-0120.

### PSY-097 — Social Identification Strength

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Multidimensional",
  "definition": "The degree of cognitive and affective identification with a specified social group.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC160; SRC161.",
  "evidenceStrength": "Strong",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-097",
  "indicators": [
    "Identification scale",
    "group-referent self-description",
    "collective action intent"
  ],
  "keySources": [
    "SRC160",
    "SRC161"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Makes group norms and outcomes self-relevant and increases group-oriented motivation.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "Low",
  "name": "Social Identification Strength",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = stronger identification with the specified group.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Centrality, solidarity, satisfaction, and self-stereotyping profile",
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
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Low"
}
```

Cognitive/affective social identification profile, not mere membership, solidarity alone or identity fusion.

Canonical centrality/solidarity/satisfaction/self-stereotyping dimensions; Leach additionally distinguishes group homogeneity. Do not fill/change canonical definition.

Enduring profile versus cue salience; repeated measures needed for durable change.

Feature-scope architecture issue reused; no uniform profile effect or profile-component causal shortcut.

Boundary references: PSY-096, PSY-098, PSY-021. Sources: SRC160, SRC161, SRC-CAND-PSY-LAYER-0120, SRC-CAND-PSY-LAYER-0134.

### PSY-098 — Identity Fusion

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of visceral alignment and perceived oneness between personal identity and a specified group.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC159; SRC161.",
  "evidenceStrength": "Moderate",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-098",
  "indicators": [
    "Fusion scale",
    "sacrifice endorsement",
    "group-defense behavior"
  ],
  "keySources": [
    "SRC159",
    "SRC161"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Links personal agency to group outcomes and can motivate unusually costly pro-group action.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "Low",
  "name": "Identity Fusion",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = stronger perceived oneness of personal and group identity.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high verbal or pictorial fusion scale",
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
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Low"
}
```

Perceived personal-group oneness; not all identification, actual ties or observed costly behavior.

Verbal/pictorial fusion and sacrifice endorsement differ. New recall experiment measures7item score; reported F inconsistent with reported group means/SD/N.

Canonical slow-changing state versus immediate activation score; repeated cross-sectional country changes not within-person persistence.

EA0022 RN: reporting reconciliation and state/time-scale alignment required; no invented correction or universal permanent fusion.

Boundary references: PSY-095, PSY-097, PSY-024. Sources: SRC159, SRC161, SRC-CAND-PSY-LAYER-0123, SRC-CAND-PSY-LAYER-0124.

### PSY-099 — Self-Concept Clarity

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which beliefs about the self are clearly defined, internally consistent, and stable.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC195; SRC194.",
  "evidenceStrength": "Moderate",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-099",
  "indicators": [
    "Clarity scale",
    "self-description consistency",
    "stability over time"
  ],
  "keySources": [
    "SRC195",
    "SRC194"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Provides a stable basis for goals and interpretation while reducing uncertainty about identity-congruent action.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "Low",
  "name": "Self-Concept Clarity",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = clearer, more coherent, and stable self-beliefs.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high self-concept clarity scale",
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
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Low"
}
```

Clarity, consistency and stability of self-beliefs, not self-esteem or positivity of content.

SCC scale/culture boundaries and breakup-related change differ from independent manipulation; shared negative-report style can confound.

Weeks/months-years versus transient certainty; longitudinal breakup not random breakup.

No exact self-concept-clarity effect retained; cross-cultural scale interpretation and reverse causality remain.

Boundary references: PSY-001, PSY-096, PSY-100. Sources: SRC195, SRC194, SRC-CAND-PSY-LAYER-0130.

### PSY-100 — Self-Integrity Threat

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which information or events are perceived as threatening the person's global sense of being adequate, moral, or coherent.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC129; SRC158.",
  "evidenceStrength": "Strong",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-100",
  "indicators": [
    "Defensive dismissal",
    "threat rating",
    "compensatory affirmation"
  ],
  "keySources": [
    "SRC129",
    "SRC158"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Motivates defensive processing or compensatory affirmation to restore an adequate self-image.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "High",
  "name": "Self-Integrity Threat",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived threat to global self-integrity.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high threat; event-specific defensiveness index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Moderate"
}
```

Perceived threat to global adequacy/morality/coherence, not threat to one group or any stress response.

Defensiveness, message acceptance, self-compassion and well-being are not direct identical measures of global integrity threat.

Event-specific minutes/hours; downstream educational/health benefits do not establish persistent threat reduction.

EA0020 values writing RN; preserve health null and individual/group affirmation differences; PSY-045 revision only.

Boundary references: PSY-101, PSY-102, PSY-115. Sources: SRC129, SRC158, SRC-CAND-PSY-LAYER-0119, SRC-CAND-PSY-LAYER-0122, SRC-CAND-PSY-LAYER-0127, SRC-CAND-PSY-LAYER-0128.

### PSY-101 — Perceived Identity Threat

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Magnitude / level",
  "definition": "The degree to which a situation is perceived as devaluing, constraining, or endangering a specified identity and its standing.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC160; SRC161.",
  "evidenceStrength": "Moderate",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-101",
  "indicators": [
    "Threat rating",
    "identity defense",
    "withdrawal or collective-action intent"
  ],
  "keySources": [
    "SRC160",
    "SRC161"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Mobilizes identity defense, withdrawal, confrontation, or collective action depending on efficacy and norms.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "High",
  "name": "Perceived Identity Threat",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater perceived threat to the specified identity.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high identity-threat rating",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Moderate"
}
```

Perceived devaluation/endangerment of a specified identity, not cultural honor norms themselves or global adequacy.

Identity-specific reputation/threat versus vigilance, physiology, belonging and anger need exact alignment.

Situational cue/insult before appraisal; regional cultural exposure is not randomized individual norm strength.

CUL-055 revision review: insult×regional upbringing not direct randomized community honor-strength effect; F05 anger review reused.

Boundary references: PSY-100, PSY-043, PSY-021. Sources: SRC160, SRC161, SRC286, SRC-CAND-PSY-LAYER-0126.

### PSY-102 — Dissonance Magnitude

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Magnitude / level",
  "definition": "The intensity of aversive inconsistency experienced among behavior, beliefs, attitudes, commitments, or self-concept.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC127; SRC196.",
  "evidenceStrength": "Strong",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-102",
  "indicators": [
    "Discomfort",
    "justification",
    "belief or behavior change"
  ],
  "keySources": [
    "SRC127",
    "SRC196"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Motivates change in attitudes, beliefs, behavior, or interpretation to reduce inconsistency.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "High",
  "name": "Dissonance Magnitude",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually reversible as cues, resources, or interpretations change; repeated appraisal can stabilize.",
  "polarityDirection": "Higher values = greater experienced inconsistency and discomfort.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "None–high dissonance; discrepancy and discomfort ratings",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Minutes–Hours"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Moderate"
}
```

Experienced aversive inconsistency/discomfort, not algebraic contradiction or postchoice preference spread alone.

Negative-affect ratings after high-choice statements support scoped discomfort; operational attribution and free-choice measurement artifacts differ.

Immediate induced-compliance response versus later attitude change; do not infer mediated path or persistence.

EA0021 RN pending full task/measure alignment; positive discomfort retained, artifact critique not universal dissonance rejection.

Boundary references: PSY-001, PSY-047, PSY-092, PSY-100. Sources: SRC127, SRC196, SRC-CAND-PSY-LAYER-0121, SRC-CAND-PSY-LAYER-0129.

### PSY-103 — Moral Identity Centrality

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating demographic membership as an identity driver or assuming a salient identity has one fixed behavioral implication.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which moral traits and values are central to a person's self-definition.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC130.",
  "evidenceStrength": "Strong",
  "family": "Self-Concept, Identity & Consistency",
  "id": "PSY-103",
  "indicators": [
    "Moral-identity scale",
    "moral self-description",
    "consistency behavior"
  ],
  "keySources": [
    "SRC130"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Identity-congruent choice",
    "defensiveness",
    "affiliation",
    "group action",
    "consistency restoration"
  ],
  "likelyUpstreamInfluences": [
    "Self-reflection",
    "group cues",
    "social feedback",
    "values",
    "role expectations",
    "threat or affirmation"
  ],
  "measurementAssessmentMethods": "Validated identity scales; salience manipulations; narrative or content coding; experience sampling",
  "measurementCaveats": "Identity is multidimensional and context-sensitive; group labels do not reveal identification strength, content, or fusion.",
  "mechanism": "Raises the value of moral consistency and can motivate prosocial or principled action when moral content is salient.",
  "moderatorsBoundaryConditions": "Identity content, context, competing identities, group norms, threat intensity, culture, and perceived efficacy.",
  "modifiability": "Low",
  "name": "Moral Identity Centrality",
  "observability": "Low",
  "onsetCausalLag": [
    "Minutes–Hours"
  ],
  "persistenceRecovery": "Salience changes quickly; centrality and fusion may persist for months or years and can be path-dependent.",
  "polarityDirection": "Higher values = greater centrality of moral self-definition.",
  "primaryFamilyId": "PSY-F11",
  "relatedFamilyIds": [],
  "representationScale": "Low–high moral-identity internalization scale",
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
    "Identity Salience",
    "Identity Centrality",
    "Social Identification Strength",
    "Self-Integrity Threat"
  ],
  "volatility": "Low"
}
```

Moral self-definition centrality/internalization, not all moral behavior, displayed virtue or temporary salience.

Internalization versus symbolization and implicit/primed measures differ; self-report studies show larger associations.

Canonical enduring centrality; a short moral cue is not enduring trait/identity change.

No universal moral-cause effect or causal edge from correlation; cultural/measurement boundaries unresolved.

Boundary references: PSY-096, PSY-111, PSY-112. Sources: SRC130, SRC-CAND-PSY-LAYER-0131.
