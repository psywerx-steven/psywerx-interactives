# PSY-F06 — Attention & Cognitive Processing

Audit `AUD-PSY-F06-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

Candidate research only. Human decisions pending. No production science changed.

## Complete entity review

All8 canonical Driver records,16 RELATED_SEARCH aliases and empty crosswalk reviewed. Frozen definitions, mechanisms, source references, scales, data types, polarity/direction, modifiability, volatility, onset/time/persistence, indicators, methods, observability, caveats and narrative/interactions preserved. Zero local blocked fields; no fields repaired.

No local RDS and no RDS endpoint among15incident edges. PSY-078 remains F09 protected RDS. Conceptual resource complement in PSY-057/058 is a scientific issue, not authorization to reclassify either Driver or encode formula causation.

### PSY-055 — Selective Attention Allocation

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Proportion",
  "definition": "The proportion of available attention directed toward a specified stimulus, location, feature, or task.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC148; SRC109.",
  "evidenceStrength": "Strong",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-055",
  "indicators": [
    "Dwell time",
    "probe performance",
    "recall",
    "gaze allocation"
  ],
  "keySources": [
    "SRC148",
    "SRC109"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Changes which information is encoded, elaborated, and available for downstream appraisal and choice.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Selective Attention Allocation",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = greater attention allocated to the specified target.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "0–1 share of attention; dwell time proportion; probe-based bias",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Proportion of available attention allocated to a specified target; not attention capacity or total task duration.

Dwell-time proportion requires an explicit denominator and relevant region/window; fixation count, first-fixation latency and covert allocation are different measures.

Seconds/minutes within a specified display/task, not enduring attention ability.

Cueing and social/cultural viewing effects are promising but no exact proportion contrast extracted; no signed whole-attention effect.

Boundary references: PSY-056, PSY-058, PSY-080. Sources: SRC-CAND-PSY-LAYER-0062, SRC-CAND-PSY-LAYER-0063, SRC-CAND-PSY-LAYER-0067, SRC-CAND-PSY-LAYER-0068.

### PSY-056 — Attentional Salience

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Unipolar continuous",
  "definition": "The degree to which a represented stimulus or feature stands out and attracts priority in attention.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC148; SRC125.",
  "evidenceStrength": "Moderate",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-056",
  "indicators": [
    "Detection speed",
    "gaze capture",
    "salience rating"
  ],
  "keySources": [
    "SRC148",
    "SRC125"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Raises the probability and speed of attention and increases the weight of associated information.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Attentional Salience",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = greater psychological prominence and capture priority.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Low–high subjective salience; attentional capture index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Psychological prominence/capture priority, not objective visual contrast or the emotional intensity of content.

Orienting latency, gaze capture and prominence ratings need separate operational alignment; salient is not necessarily attended voluntarily.

Momentary priority conditional on goals, task and competing stimuli.

Emotional-content→salience sources do not supply exact manipulation/priority evidence; source misinformation/dehumanization findings cannot substitute.

Boundary references: PSY-055, INF-044, PSY-007. Sources: SRC-CAND-PSY-LAYER-0063, SRC-505, SRC-506.

### PSY-057 — Cognitive Load

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Magnitude / level",
  "definition": "The amount of limited cognitive-processing capacity currently occupied by task demands and concurrent mental operations.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC149; SRC147.",
  "evidenceStrength": "Strong",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-057",
  "indicators": [
    "Dual-task cost",
    "workload rating",
    "error/latency increase"
  ],
  "keySources": [
    "SRC149",
    "SRC147"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Reduces resources available for elaboration, working memory, inhibition, and complex choice.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Cognitive Load",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = more occupied cognitive capacity.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Low–high workload; task-load manipulation; performance-derived estimate",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Occupied limited processing resources under a task and concurrent operations; not objective difficulty itself.

Mental-effort, perceived-difficulty and NASA-TLX composites are not interchangeable measures. Shared resource definitions with available WM can create conceptual inverse dependence.

During-task occupancy separated from retrospective ratings, chronic fatigue and learning outcomes.

Cueing load claim retained RESEARCH_NEEDED because synthesis combines perceived effort/difficulty. Existing BIO/INF revision paths linked, never repaired.

Boundary references: PSY-058, PSY-054, BIO-025, BIO-001, ENV-039, INF-012. Sources: SRC-CAND-PSY-LAYER-0062, SRC-CAND-PSY-LAYER-0063, SRC340, SRC149, SRC-494, SRC-499.

### PSY-058 — Working Memory Availability

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Magnitude / level",
  "definition": "The amount of working-memory capacity currently available for maintaining and manipulating task-relevant information.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC147; SRC148; SRC149.",
  "evidenceStrength": "Strong",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-058",
  "indicators": [
    "Span performance",
    "n-back or complex-task accuracy",
    "interference cost"
  ],
  "keySources": [
    "SRC147",
    "SRC148",
    "SRC149"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Supports integration, planning, inhibition, and resistance to distraction.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Working Memory Availability",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = more capacity available for current processing.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Low–high available capacity; residual span/performance estimate",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Currently available maintenance/manipulation resources; not a stable trait capacity or score on one practiced task.

N-back, span and transfer accuracy depend on strategy, skill and stimulus domain. Improved trained score does not uniquely identify greater available resources.

Training transfer/durability and momentary availability are separate; sleep/fatigue timing preserved.

N-back practice effect remains research-needed/UNKNOWN on exact Driver; task-specific transfer and active-control nulls preserved.

Boundary references: PSY-057, PSY-062, PSY-080, PSY-042. Sources: SRC-CAND-PSY-LAYER-0059, SRC-CAND-PSY-LAYER-0060, SRC-CAND-PSY-LAYER-0064, SRC-CAND-PSY-LAYER-0069, SRC147, SRC148, SRC149.

### PSY-059 — Elaboration Depth

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Unipolar continuous",
  "definition": "The degree of effortful, issue-relevant cognitive processing applied to information or a decision.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC117; SRC162.",
  "evidenceStrength": "Strong",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-059",
  "indicators": [
    "Thought-listing",
    "argument recall",
    "processing time",
    "need-consistent cognition"
  ],
  "keySources": [
    "SRC117",
    "SRC162"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Increases integration with prior knowledge and can produce more durable, confidence-linked judgments.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Elaboration Depth",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = deeper and more effortful issue-relevant processing.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Low–high elaboration; thought count/quality; processing-time index",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Effortful issue-relevant processing, not any slow response, recall score or reflective-test success.

Thought listing can index relevant processing but amount, valence and quality differ; font difficulty manipulates presentation not elaboration directly.

Within message/task, contingent on relevance, ability and motivation; no enduring change in need for cognition.

Replicated failure of font→CRT benefit blocks inferring deeper elaboration from slowness. No new duplicate of REL-PSY-007/030.

Boundary references: PSY-007, PSY-129, PSY-058, PSY-061. Sources: SRC117, SRC162, SRC171, SRC-CAND-PSY-LAYER-0061, SRC-CAND-PSY-LAYER-0003.

### PSY-060 — Construal Frame

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Nominal categorical",
  "definition": "The currently active representation that organizes which aspects, comparisons, or meanings of a situation are foregrounded.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC113; SRC183.",
  "evidenceStrength": "Strong",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-060",
  "indicators": [
    "Frame endorsement",
    "language coding",
    "attribute weighting"
  ],
  "keySources": [
    "SRC113",
    "SRC183"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Changes which attributes and reference comparisons enter appraisal and valuation.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Construal Frame",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Categories identify alternative construals and have no inherent universal ordering.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Frame category; gain/loss; concrete/abstract; diagnostic coding",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Nominal categorical active construal frame, not an ordinal quantity or a valenced amount.

Gain/loss wording is external content; an internally adopted frame needs a qualified category and a valid manipulation check, not choice alone.

Task-specific adoption and replacement, not one construct transforming into another.

No LEVEL/INCREASE claim on a nominal frame. Category-specific state representation requires an exact scoped proposal; no architecture change inferred merely from a lack of evidence.

Boundary references: PSY-086, PSY-088, PSY-094. Sources: SRC113, SRC183, SRC-405.

### PSY-061 — Processing Fluency

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Unipolar continuous",
  "definition": "The experienced ease with which a stimulus or thought is perceived, retrieved, or processed.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Supported by established theory, validated measures, and converging review, meta-analytic, experimental, or longitudinal evidence. Magnitude and behavioral direction remain conditional on context. Representative records: SRC125; SRC171.",
  "evidenceStrength": "Strong",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-061",
  "indicators": [
    "Ease rating",
    "response time",
    "subjective familiarity",
    "effort report"
  ],
  "keySources": [
    "SRC125",
    "SRC171"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Functions as a metacognitive cue that can affect familiarity, truth, confidence, liking, and effort allocation.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Processing Fluency",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Usually task-bound and rapidly reversible, although learning and fatigue can produce longer effects.",
  "polarityDirection": "Higher values = greater subjective ease of processing.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Low–high ease rating; response latency or disfluency manipulation",
  "source": {
    "sheet": "Drivers",
    "workbook": "PSYWERX_Layer_2_Psychological_Driver_Ontology_v1.0.xlsx"
  },
  "timeScaleOfChange": [
    "Seconds–Minutes"
  ],
  "timeScaleQualifier": null,
  "typicalInteractionCandidates": [
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "High"
}
```

Experienced ease of perceiving/retrieving/thinking; not reading speed, factual accuracy, familiarity or confidence itself.

Objective font readability/response time needs subjective-ease alignment; ease attribution and prior expectations can reverse interpretation.

Trial/message-specific processing and later judgment must be temporally distinguished.

SRC171 title/year and PMID disagree; its URL duplicates SRC125. No independent replication counted or canonical correction made.

Boundary references: PSY-067, PSY-116, PSY-059. Sources: SRC125, SRC171, SRC169, SRC-CAND-PSY-LAYER-0061.

### PSY-062 — Cognitive Flexibility

Canonical snapshot (including all available fields):

```json
{
  "aliases": [],
  "associatedLayers": [
    "Psychological"
  ],
  "commonMisinterpretations": "Treating a single laboratory task or response-time difference as a pure measure of a broad cognitive construct.",
  "dataType": "Magnitude / level",
  "definition": "The capacity currently available to shift perspectives, rules, or strategies in response to changing demands.",
  "entitySubtype": null,
  "entityType": "DRIVER",
  "evidenceNotes": "Scientifically defensible with substantial supporting literature, while causal identification, construct boundaries, measurement, or transferability remain context dependent. Representative records: SRC150; SRC149.",
  "evidenceStrength": "Moderate",
  "family": "Attention & Cognitive Processing",
  "id": "PSY-062",
  "indicators": [
    "Switch cost",
    "perseverative errors",
    "flexibility ratings"
  ],
  "keySources": [
    "SRC150",
    "SRC149"
  ],
  "layer": "Psychological",
  "likelyDownstreamInfluences": [
    "Encoding",
    "recall",
    "appraisal",
    "judgment quality",
    "learning",
    "action selection"
  ],
  "likelyUpstreamInfluences": [
    "Task demands",
    "goals",
    "stimulus features",
    "information density",
    "fatigue",
    "affective arousal"
  ],
  "measurementAssessmentMethods": "Cognitive tasks; eye tracking or attention probes; workload scales; response-time and accuracy measures",
  "measurementCaveats": "Task measures often have low cross-task reliability and can reflect strategy, motivation, speed-accuracy tradeoffs, or sensory limits.",
  "mechanism": "Supports updating, perspective change, and strategy switching when the environment changes.",
  "moderatorsBoundaryConditions": "Expertise, task complexity, time pressure, fatigue, motivation, modality, and environmental distraction.",
  "modifiability": "Moderate",
  "name": "Cognitive Flexibility",
  "observability": "Moderate",
  "onsetCausalLag": [
    "Seconds–Minutes"
  ],
  "persistenceRecovery": "Momentary deployment recovers with rest or context change; trained capacity may persist longer.",
  "polarityDirection": "Higher values = greater ability to adapt cognitive set or strategy.",
  "primaryFamilyId": "PSY-F06",
  "relatedFamilyIds": [],
  "representationScale": "Low–high flexibility; switch cost; validated flexibility measure",
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
    "Working Memory Availability",
    "Cognitive Load",
    "Domain Knowledge",
    "Attentional Control Capacity"
  ],
  "volatility": "Moderate"
}
```

Available ability to shift perspective, rule or strategy; not psychological acceptance/flexibility or intelligence.

Switch-cost latency, shifting accuracy, perseveration and self-report are task-dependent; speed/accuracy effects cannot be pooled as one latent capacity.

Short task state versus acquired transferable skill over weeks/months requires durability and transfer evidence.

Mindfulness reviews disagree by comparator and outcome; accuracy benefits and latency nondetection do not establish uniform cognitive-flexibility change.

Boundary references: PSY-058, PSY-080, PSY-079. Sources: SRC149, SRC150, SRC-CAND-PSY-LAYER-0064, SRC-CAND-PSY-LAYER-0069, SRC-CAND-PSY-LAYER-0060.
