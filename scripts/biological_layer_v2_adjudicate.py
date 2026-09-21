"""Deterministic Biological Layer candidate-only scientific reconciliation."""

from __future__ import annotations

from collections import Counter

from biological_layer_v2 import DATA, DOCS, PROGRAM_ID, read, write, write_doc, validate_protection

S = lambda n: f"SRC-CAND-BIO-LAYER-{n:03d}"

TRIAGE = [
    ("BIO-F01", "Existing governed pilot sleep and circadian candidates", "PRIOR_PILOT_REUSE", "BIO-F01 science and B01-B05 were already governed; no new exact route is needed.", []),
    ("BIO-F02", "A single cortisol marker is equivalent to allostatic load", "REJECT_CATEGORY_ERROR", "Multisystem cumulative construct cannot be replaced by one acute biomarker.", [1]),
    ("BIO-F03", "Subjective thirst is equivalent to objective hydration status", "REJECT_CATEGORY_ERROR", "Homeostatic drive and body-fluid state are different levels.", [2]),
    ("BIO-F04", "Ambient heat universally increases heat strain", "INSUFFICIENT_PRELIMINARY_SIGNAL", "Exposure, achieved strain, acclimation and dose differ; exact controlled contrast not extracted.", [3]),
    ("BIO-F05", "Chronic exercise universally reduces physical fatigue", "INSUFFICIENT_PRELIMINARY_SIGNAL", "Exercise packages, baseline health and measured energy/fatigue differ.", [4]),
    ("BIO-F06", "Controlled endotoxin increases acute sickness response intensity", "DEEP_RESEARCHED_RESEARCH_NEEDED", "Small male laboratory studies and scale/biomarker alignment prevent broad BIO-030 assertion.", [5,6,7]),
    ("BIO-F07", "Age-related hearing loss causally reduces broad cognitive capacity", "REJECT_CATEGORY_ERROR", "Observational association and test-access differences do not identify causal direction.", [8,9]),
    ("BIO-F08", "Oral iron supplementation reduces BIO-025 physical fatigue in low-ferritin nonanemic adults", "DEEP_RESEARCHED_RESEARCH_NEEDED", "Trials measure reported general fatigue; BIO-025 physical fatigue is not isolated, while objective capacity differs.", [10,11,12,13]),
    ("BIO-F09", "Thyroid replacement universally reduces fatigue in older adults", "DEEP_RESEARCHED_REJECTED_BROAD_CLAIM", "Controlled trials in mild subclinical hypothyroidism show no clear fatigability benefit; no universal direction.", [14,15]),
    ("BIO-F10", "Measured frailty causes measured physical fitness decline", "REJECT_CATEGORY_ERROR", "Frailty scoring shares constituents with fitness measures; direction not identified by association.", [16]),
    ("BIO-F11", "Polygenic risk score directly causes an acute biological state", "REJECT_CATEGORY_ERROR", "Predictive aggregate profile is not a direct acute mechanism or manipulation.", [17]),
    ("BIO-F12", "Any traumatic brain injury causes uniform persistent cognitive impairment", "INSUFFICIENT_PRELIMINARY_SIGNAL", "Severity, domain, course and recovery vary; no exact uniform endpoint.", [18]),
    ("BIO-F13", "Any alcohol effect universally reduces bodily capacity", "INSUFFICIENT_PRELIMINARY_SIGNAL", "Working-memory task meta-analysis does not identify broad physical capacity and has dose/task moderation.", [19]),
    ("BIO-F14", "Abrupt blinded cessation of habitual caffeine raises time-bounded withdrawal severity", "FORMAL_CANDIDATE_RESEARCH_NEEDED_AFTER_SKEPTICAL_REVIEW", "Controlled substitution studies establish symptom changes but do not establish one exact, transportable BIO-066 whole-syndrome severity metric; incidence and symptom composition vary.", [20,21,22,23]),
]

def sf(i, source, claim, design, population, exposure, comparator, target, time, result, disposition, limits, overlap=None):
    return {"id": f"SF-BIO-LAYER-{i:03d}", "sourceId": S(source), "claimId": claim,
            "locator": "PubMed abstract; source title and PMID independently verified via NCBI Eutilities",
            "accessDepth": "PUBMED_ABSTRACT", "design": design, "population": population,
            "exposure": exposure, "comparator": comparator, "target": target, "time": time,
            "result": result, "disposition": disposition, "limitations": limits,
            "datasetGroup": f"PMID_{read(DATA / 'candidate-source-registry.json')[S(source)]['pmid']}",
            "reviewOverlap": overlap or []}

def build() -> None:
    validate_protection()
    source_reg = read(DATA / "candidate-source-registry.json")
    triage = []
    for i, (family, proposition, outcome, reason, nums) in enumerate(TRIAGE, 1):
        triage.append({"id": f"HYP-BIO-LAYER-{i:03d}" if i != 14 else "EA-CAND-BIO-LAYER-0001",
                       "familyId": family, "proposition": proposition, "semanticType": "CAUSAL",
                       "outcome": outcome, "reason": reason, "sourceIds": [S(n) for n in nums]})
    write(DATA / "triage-hypotheses.json", triage)
    deep = [
        {"id": "DEEP-BIO-001", "familyId": "BIO-F06", "hypothesisId": "HYP-BIO-LAYER-006", "question": "Endotoxin challenge to BIO-030 sickness intensity", "sourceIds": [S(n) for n in (5,6,7)], "outcome": "RESEARCH_NEEDED", "stopReason": "Biomarker and subjective sickness response differ; adult male acute sample and measurement rule are not broad BIO-030 semantics."},
        {"id": "DEEP-BIO-002", "familyId": "BIO-F08", "hypothesisId": "HYP-BIO-LAYER-008", "question": "Oral iron in low-ferritin nonanemic adults to BIO-025 physical fatigue", "sourceIds": [S(n) for n in (10,11,12,13)], "outcome": "RESEARCH_NEEDED", "stopReason": "General reported fatigue is not exact physical fatigue; capacity evidence is mixed and reviews overlap primaries."},
        {"id": "DEEP-BIO-003", "familyId": "BIO-F09", "hypothesisId": "HYP-BIO-LAYER-009", "question": "Levothyroxine in older mild subclinical hypothyroidism to fatigue", "sourceIds": [S(n) for n in (14,15)], "outcome": "REJECT_BROAD_CLAIM", "stopReason": "Trial nulls block a universal positive claim; clinical status and treatment are not a general hormone-level edge."},
        {"id": "DEEP-BIO-004", "familyId": "BIO-F14", "hypothesisId": "EA-CAND-BIO-LAYER-0001", "question": "Blinded abrupt caffeine cessation to BIO-066 withdrawal severity over 1-2 days in regular adult consumers", "sourceIds": [S(n) for n in (20,21,22,23)], "outcome": "RESEARCH_NEEDED_AFTER_SKEPTICAL_REVIEW", "stopReason": "Symptom-specific effects and nonresponse are documented; a whole-BIO-066 severity aggregation and transportable population are not exact enough for governance."},
    ]
    write(DATA / "deep-research-ledger.json", deep)
    findings = [
      sf(1,6,"HYP-BIO-LAYER-006","Double-blind crossover experiment","Healthy adult men, 18 at 0.4 and 16 at 0.8 ng/kg groups","IV endotoxin","Placebo","Temperature, cytokines, mood and neurobehavioral outcomes","1-24 hours","Dose-related inflammatory physiology and mood/anxiety changes; working-memory accuracy did not change and high-dose reaction time improved. No direct full sickness-intensity score.","MIXED_INDIRECT","Biomarker and response construct differ; small male groups; contrary task findings explicit."),
      sf(2,7,"HYP-BIO-LAYER-006","Controlled experiment","29 healthy young men; 14 endotoxin, 15 placebo","IV endotoxin 2 ng/kg","Saline","Cytokines and sickness symptoms","Hourly through 8 h","Transient cytokine, sickness symptom, temperature and fatigue increases versus baseline and placebo.","SUPPORTS_BOUNDED","Male sample; questionnaire-specific sickness and acute laboratory task only."),
      sf(3,11,"HYP-BIO-LAYER-008","Multicentre randomized observer-blinded trial","198 menstruating women 18-53 with ferritin <50 ug/L, Hb >12 g/dL and unexplained fatigue","Oral ferrous sulfate 80 mg elemental daily for 12 weeks","Placebo","Reported general fatigue CAPPS","12 weeks","Fatigue score decline 47.7% versus 28.8%; between-group difference -18.9 percentage points (95% CI -34.5 to -3.2).","SUPPORTS_REPORTED_FATIGUE","CAPPS general fatigue does not isolate physical fatigue or objective functional capacity."),
      sf(4,12,"HYP-BIO-LAYER-008","Double-blind randomized trial","144 nonanemic women aged 18-55 with unexplained fatigue","Oral ferrous sulfate 80 mg elemental daily for four weeks","Placebo","Self-rated fatigue visual analogue scale","Four weeks","Mean fatigue decline 1.82 versus 0.85 points; between-group difference 0.95 (95% CI 0.32 to 1.62); apparent benefit concentrated at ferritin <=50 ug/L.","SUPPORTS_REPORTED_FATIGUE","Baseline ferritin subgroup and subjective fatigue; not broad physical capacity."),
      sf(5,10,"HYP-BIO-LAYER-008","Systematic review and meta-analysis","Nonanaemic iron-deficient adults in included trials","Iron supplementation, mixed route","Control","Fatigue and physical capacity","Variable","Synthesis reports reduced subjective fatigue but no clear improvement in objective physical capacity in included trials.","MIXED_ENDPOINTS","Includes earlier primary trials including source 011/012 where eligible; do not count as independent replication.",[S(11),S(12)]),
      sf(6,14,"HYP-BIO-LAYER-009","Randomized placebo-controlled TRUST nested analysis","230 older adults >=65 with mild subclinical hypothyroidism","Levothyroxine with titration","Placebo","Physical and mental fatigability scales","One year","No between-group physical fatigability difference 0.2 (95% CI -1.8 to 2.1) or mental -1.0 (-2.8 to 0.8).","NULL_BOUNDED","Nested in TRUST, not independent replication; clinical population and one-year endpoint."),
      sf(7,15,"HYP-BIO-LAYER-009","Randomized controlled trial","Community-living adults >=65 with subclinical hypothyroidism","Thyroxine replacement","Placebo","Multiple cognitive function tests","6 and 12 months","No significant cognitive test benefit in the reported tests.","NULL_DIFFERENT_ENDPOINT","Cognition is not fatigue; do not treat as direct fatigue null."),
      sf(8,21,"EA-CAND-BIO-LAYER-0001","Double-blind crossover study","62 normal adults with low/moderate daily caffeine use; mean intake 235 mg/day","Two days caffeine-free diet with placebo capsules","Same diet with caffeine-equivalent capsules","Withdrawal symptoms including headache and fatigue","End of two-day period","Moderate/severe headache 52% during placebo versus 6% on caffeine and 2% baseline; high fatigue score 8% versus 0% caffeine.","SUPPORTS_BOUNDED","Symptom-specific frequencies, not a numeric effect size for entire BIO-066 state; 48-hour adult exposure."),
      sf(9,22,"EA-CAND-BIO-LAYER-0001","Community survey plus randomized double-blind controlled pilot","11,112 survey respondents; selected 57 prior-symptom regular caffeine users, 18 abrupt arm","Abrupt or gradual caffeine cessation","Maintained caffeine level","Self-reported withdrawal symptoms/function","Short withdrawal interval","Only 6/18 abrupt-arm participants reported symptoms and 7/18 including functional decrement; gradual group minimal; clinically significant symptoms uncommon in general survey.","MIXED_LOW_INCIDENCE","Selected pilot sample and survey are separate evidence roles; survey not randomized efficacy evidence."),
      sf(10,23,"EA-CAND-BIO-LAYER-0001","Double-blind placebo substitution","7 regular 100 mg/day caffeine users","Placebo substitution for 12 days and repeated one-day periods","Maintained caffeine","Withdrawal syndrome ratings","Peak days 1-2 then decline about one week","First prolonged phase showed orderly withdrawal in 4/7 and no evidence in 3/7; repeated one-day substitutions in the second phase showed a significant effect in all seven, with varied symptoms and magnitude.","MIXED_SUBGROUP","Very small sample; first-phase nonresponse and second-phase effects both explicit; not universal syndrome severity."),
    ]
    write(DATA / "source-findings.json", findings)
    effects = [{"id":"EA-CAND-BIO-LAYER-0001", "originFamilyId":"BIO-F14", "happeningTypeId":"HT-CAND-BIO-LAYER-0001",
        "targetKind":"DRIVER", "targetId":"BIO-066", "property":"LEVEL", "direction":"CONTEXT_DEPENDENT_INCREASE_IN_SUBSET",
        "timing":"Onset and peak within approximately 1-2 days after abrupt cessation in studied adults; recovery may take several days.",
        "population":"Regular adult caffeine consumers under blinded substitution; no general population incidence assertion.",
        "operation":"Abrupt cessation or matched placebo substitution of habitual dietary caffeine, compared with maintaining usual caffeine intake.",
        "scope":"Transient measured withdrawal symptom severity; headache and fatigue are components, not a universal complete syndrome.",
        "limitations":"Incidence depends on baseline intake and selection; 1999 controlled pilot and 1990 small sample include nonresponders. No medical advice, broad dose-response, or behavior outcome.",
        "status":"RESEARCH_NEEDED", "activationStatus":"NOT_ELIGIBLE", "lifecycleStatus":"CANDIDATE",
        "sourceFindingIds":["SF-BIO-LAYER-008","SF-BIO-LAYER-009","SF-BIO-LAYER-010"],
        "evidenceAssessmentId":"EVA-AE-CAND-BIO-LAYER-0001"}]
    write(DATA / "actions-events-hypotheses.json", effects + [
        {"id":"HYP-BIO-LAYER-AE-002","originFamilyId":"BIO-F06","targetKind":"DRIVER","targetId":"BIO-030","property":"LEVEL","status":"RESEARCH_NEEDED","reason":"Endotoxin challenge result is acute and male-only; biomarker response cannot substitute for exact sickness-intensity measurement; no independent generalization.","sourceIds":[S(6),S(7)]},
        {"id":"HYP-BIO-LAYER-AE-003","originFamilyId":"BIO-F08","targetKind":"DRIVER","targetId":"BIO-025","property":"LEVEL","status":"RESEARCH_NEEDED","reason":"Oral iron trial fatigue scales do not isolate physical fatigue; no broad target-level direction.","sourceIds":[S(10),S(11),S(12)]},
        {"id":"HYP-BIO-LAYER-AE-004","originFamilyId":"BIO-F09","targetKind":"DRIVER","targetId":"BIO-025","property":"LEVEL","status":"RESEARCH_NEEDED","reason":"Clinical thyroid replacement null does not prove hormone-status-to-physical-fatigue causal null in other populations.","sourceIds":[S(14),S(15)]}
    ])
    write(DATA / "actions-events-identity-registry.json", {"HT-CAND-BIO-LAYER-0001": {
         "id":"HT-CAND-BIO-LAYER-0001", "originFamilyId":"BIO-F14", "name":"Abrupt cessation of habitual caffeine intake",
         "identity":"A bounded operation replacing an adult's usual daily caffeine intake with caffeine-free matched intake or placebo substitution over a specified interval.",
         "intentionality":"DELIBERATE_EXPERIMENTAL_OPERATION", "efficacyImplied":False,
         "status":"REVIEW_READY", "lifecycleStatus":"CANDIDATE", "activationStatus":"NOT_ELIGIBLE",
         "duplicateReview":"Distinct from BIO-F01 timed caffeine administration INT-V1-BIO-F01-010: cessation versus delivery; no matching Psychological/Informational HappeningType found.",
         "sourceIds":[S(21),S(22),S(23)]}})
    assessment = {"id":"EVA-AE-CAND-BIO-LAYER-0001", "assertionId":"EA-CAND-BIO-LAYER-0001",
       "basis":"BLINDED_CAFFEINE_SUBSTITUTION", "productionMethod":"CURATED_SOURCE_FINDING_SYNTHESIS",
       "disposition":"MIXED", "strength":"MODERATE_FOR_BOUNDED_SYMPTOMS_INSUFFICIENT_FOR_WHOLE_TARGET", "confidence":"MODERATE_WITH_INCIDENCE_HETEROGENEITY",
       "sourceFindingIds":["SF-BIO-LAYER-008","SF-BIO-LAYER-009","SF-BIO-LAYER-010"],
       "nullContrary":"Low-dose study had 3/7 without observed withdrawal; selected pilot 11/18 abrupt participants did not report symptoms. These are explicit nonresponse findings, not proof of zero population effect.",
       "overlap":"Review PMID 15448977 synthesizes these primary studies and is not independent replication.",
       "lifecycleStatus":"CANDIDATE", "activationStatus":"NOT_ELIGIBLE", "use":"RESEARCH_NEEDED_ONLY"}
    write(DATA / "evidence-assessments.json", [assessment])
    write(DATA / "candidate-proposition-registry.json", {"EA-CAND-BIO-LAYER-0001": effects[0]})
    write(DATA / "source-overlap-registry.json", [
      {"id":"OV-BIO-001","sources":[S(10),S(11),S(12)],"issue":"Iron systematic review includes earlier oral primary trials; review and trials are not independent replication."},
      {"id":"OV-BIO-002","sources":[S(5),S(6),S(7)],"issue":"Sickness-behavior review discusses experimental endotoxin studies; review is contextual and not a third independent experiment."},
      {"id":"OV-BIO-003","sources":[S(20),S(21),S(22),S(23)],"issue":"Caffeine-withdrawal review includes earlier substitution trials; count underlying study populations once. Survey and selected pilot within PMID 10586387 are different evidence roles."},
      {"id":"OV-BIO-004","sources":[S(14),S(15)],"issue":"Different thyroid trial reports and endpoints; TRUST nested fatigability analysis must not be counted independently from parent TRUST trial."}
    ])
    write(DATA / "cross-family-issues.json", [
      {"id":"XF-BIO-001","families":["BIO-F01","BIO-F05"],"issue":"Sleep and cognitive fatigue links already have pilot science; avoid a second sleep-restriction contribution."},
      {"id":"XF-BIO-002","families":["BIO-F06","BIO-F08"],"issue":"Inflammation, hemoglobin and fatigue can share symptoms and biomarkers; no independent pathways inferred."},
      {"id":"XF-BIO-003","families":["BIO-F13","BIO-F14"],"issue":"Caffeine effect level, exposure cessation and withdrawal severity are distinct; do not reuse caffeine-administration identity for cessation."},
      {"id":"XF-BIO-004","families":["BIO-F03","BIO-F04"],"issue":"Hydration and heat strain depend on dose and environment; no deterministic hydration-to-strain edge."}
    ])
    write(DATA / "cross-layer-findings.json", [
      {"id":"XL-BIO-001","relationshipIds":["REL-BIO-019","REL-BIO-020","REL-BIO-021","REL-PSY-057","REL-PSY-058"],"reusedFrom":"PSYCHOLOGICAL_LAYER/relationship-review-registry.json", "issue":"Exact Psychological endpoint reviews reused; no Psychological audit reopened."},
      {"id":"XL-BIO-002","relationshipIds":["REL-BIO-022","REL-BIO-023"],"issue":"Social outcomes need independent construct-aligned evidence; biological status does not entail participation or Social state."},
      {"id":"XL-BIO-003","relationshipIds":["REL-ENV-039","REL-ENV-041"],"issue":"Environmental exposure differs from achieved heat strain or hydration state; external ownership preserved."}
    ])
    write(DATA / "architecture-escalations.json", [
      {"id":"ARCH-BIO-LAYER-0001","issue":"BIO-003 and four BIO-F01 derived states lack a versioned exact calculation/aggregation rule in frozen entity records; one RDS is a causal source.","affectedIds":["BIO-003","BIO-006","RDS-0002","RDS-0003","RDS-0004","REL-BIO-001"],"resolution":"Future architecture/definition governance; no repair in candidate audit.","blocksNewCandidateMaterialization":False,"productionChanged":False}
    ])
    write(DATA / "astra-escalation-queue.json", [
      {"id":"ASTRA-BIO-LAYER-001","recordId":"REL-BIO-001","question":"Can circadian alignment as an RDS be an independent causal source of sleep duration rather than a definitional/shared-constituent relation?","evidence":"BIO-F01 governed B01 review proposal and frozen RDS/derivational structure.","interpretations":["Causal at heightened D10 scope","Constituent/derivational overlap"],"whySolDefers":"Resolving changes representation semantics or an existing production edge.","consequence":"Human architecture review; production unchanged.","conservativeDisposition":"BLOCKED_NEEDS_GOVERNANCE_INPUT"}
    ])
    print("Deep",len(deep),"findings",len(findings),"formal effects",len(effects),"assessments",1)

if __name__ == "__main__": build()
