"""Build the curated Biological candidate audit from the frozen baseline.

Scientific text below is an advisory interpretation of cited, existing sources.
It never writes production files or changes a lifecycle state.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from biological_layer_v2 import DATA, DOCS, PROGRAM_ID, read, write, write_doc, validate_protection


LANDSCAPES = {
    "BIO-F01": ("Sleep amount, continuity, phase, chronotype and derived sufficiency are distinct.", "Sleep and circadian phase influence waking performance with timing and baseline dependence.", "Reuse governed sleep scheduling, CBT-I, light, melatonin and caffeine pilot operations.", "Sleep measures, actigraphy and specified next-day endpoints must be separated.", "The governed BIO-F01 pilot is the scientific source of record; B01-B05 remain review proposals.", [], "GOV-BIO-F01-001-2026-09-05"),
    "BIO-F02": ("HPA/SAM activation, autonomic arousal, recovery, reactivity and multisystem allostatic load differ.", "Acute responses and cumulative biomarker composites operate on different time scales.", "Bounded stressor exposure and recovery observation are plausible routes.", "Biomarker batteries and autonomic measures are not interchangeable with felt stress.", "Allostatic-load component selection varies; response-to-burden causal direction is not fixed by a biomarker correlation.", ["001"]),
    "BIO-F03": ("Hunger, satiety, thirst, hydration, glucose and visceral signals are separate states.", "Homeostatic feedback can be anticipatory, compensatory and nonlinear.", "Hydration, nutritional or glucose perturbations require dose, baseline and objective state verification.", "Osmolality, volume, glucose and reports measure different levels.", "Thirst intensity is not hydration status; the controlled hypoglycemia task result in diabetes does not establish a generic fatigue Driver effect.", ["002", "024", "025"]),
    "BIO-F04": ("Oxygen availability, intermittent desaturation, CO2 burden, heat and cold strain differ.", "Acute environmental exposure can alter physiology, with acclimation and task-specific responses.", "Controlled hypoxia or thermal exposure is plausible but requires measured tissue state.", "Inspired gas or ambient temperature is exposure, not achieved tissue oxygen or heat strain.", "Acute hypoxia and heat-acclimation reviews show task, physiological-marker and risk-of-bias heterogeneity; chronic transfer is unsupported.", ["003", "026"]),
    "BIO-F05": ("Physical and cognitive fatigue, acute and persistent pain, capacity and reserve differ.", "Exertion and recovery can alter fatigue while pain and capacity have distinct measurements.", "Exercise/recovery or pain induction are plausible only at exact dose and endpoint.", "Subjective fatigue is not objective capacity; task failure is not a latent trait.", "Exercise trials differ by chronicity and population; experimental pain can change motor strategy while task performance often remains intact.", ["004", "027"]),
    "BIO-F06": ("Systemic inflammatory signaling, sickness response and pathogen burden are distinct.", "Controlled inflammatory challenge can generate acute cytokine and symptom responses.", "Experimental endotoxin is a bounded research exposure, not a practitioner action.", "A cytokine change alone does not measure the entire sickness response.", "Endotoxin findings vary by dose and time; reviews and included challenge studies are not independent replications.", ["005", "006", "007"]),
    "BIO-F07": ("Hearing, vision, olfaction, vestibular and somatosensory capacity differ from symptoms such as tinnitus.", "Sensory loss can change input and task access; compensation may mediate performance.", "Sensory deprivation or aid manipulation requires an exact recipient and measure.", "Hearing threshold and cognitive test scores do not by themselves identify cognitive causation.", "Most hearing-cognition evidence is observational and vulnerable to common causes and test-access artifacts.", ["008", "009"]),
    "BIO-F08": ("Energy sufficiency, oxygen carrying, iron, B12 and glycemic regulation are separable.", "Deficiency correction may alter fatigue within selected low-ferritin adults.", "Iron supplementation trials offer a bounded route; treatment and achieved status remain distinct.", "Ferritin, hemoglobin, subjective fatigue and physical capacity are different endpoints.", "Oral trials show reported-fatigue benefit; physical-capacity findings and IV routes are heterogeneous and should not be pooled as independent exact claims.", ["010", "011", "012", "013"]),
    "BIO-F09": ("Thyroid, puberty, pregnancy, menopause, reproductive hormones and sexual arousal span distinct populations and scales.", "Endocrine perturbations can have context-specific physiological and behavioral effects across life stages.", "Replacement therapy evidence is clinical and condition-specific.", "TSH and free T4 are indicators; fatigue and cognition are different outcomes.", "Thyroid RCT reports show no general fatigue/cognition benefit in older mild subclinical hypothyroidism; life-course synthesis does not identify one universal hormone effect.", ["014", "015", "028"]),
    "BIO-F10": ("Maturation, aging burden and frailty are not chronological age itself.", "Reserve and vulnerability can alter response to stressors, but measured fitness overlaps frailty scoring.", "Exercise in older adults is an operation, not a direct aging-mechanism intervention.", "Frailty, physical fitness and DNA methylation age measurements can share correlates or constituents.", "Meta-analytic associations among frailty, fitness and methylation clocks do not identify independent causal directions; puberty-related white matter maturation is separate.", ["016", "029", "030"]),
    "BIO-F11": ("Polygenic liability is a predictive susceptibility profile, not an acute state.", "Variants may contribute to risk through many downstream mechanisms.", "No routine acute manipulation of the profile is scientifically coherent.", "Portability and ancestry affect score calibration and meaning.", "Prediction, ancestry transfer and mechanism cannot be collapsed into a manipulable causal Driver claim.", ["017"]),
    "BIO-F12": ("Traumatic injury, encephalopathy, postictal, focal and neurodegenerative impairment differ.", "Injury and disease may impair domain-specific function with severity and recovery dependence.", "Clinical exposure is not a reusable recommended operation.", "Cognitive tests measure outcomes, not the whole neurological state.", "TBI longitudinal syntheses show heterogeneous courses; Alzheimer biological subtypes further warn against a single neurodegenerative trajectory.", ["018", "031"]),
    "BIO-F13": ("Alcohol, THC, nicotine, caffeine, sedative, opioid, stimulant and medication burdens are realized effects, not administered doses.", "Pharmacology depends on dose, tolerance, timing, formulation and interactions.", "Administration identities must be distinct from realized biological effect.", "Working-memory and driving-related task impairment are not broad functional capacity.", "Alcohol and THC syntheses show dose, task, timing and user-history moderation; neither licenses a universal capacity edge.", ["019", "032"]),
    "BIO-F14": ("Dependence, cessation and each substance-specific withdrawal syndrome are distinct.", "Abrupt caffeine cessation after regular intake can produce time-bounded withdrawal with variable incidence.", "Blinded placebo substitution is a coherent research operation; it cannot stand for nicotine, cannabis, alcohol or opioid cessation.", "Syndrome severity requires symptoms over a window; headache alone is only a component.", "Caffeine, cannabis, nicotine and opioid withdrawal have different populations and measurement; selected symptomatic samples and general samples yield different incidence.", ["020", "021", "022", "023", "033", "034", "035"]),
}

RELATIONSHIP_REASONS = {
    "REL-BIO-004": ("RETAIN_V1_INCOMPLETE", "Acute physiological activation and autonomic arousal are plausibly linked, but mediator and time window remain V1-incomplete."),
    "REL-BIO-005": ("RESEARCH_NEEDED", "Recovery rate and accumulated allostatic load require repeated exposure, an explicit time integral and non-overlapping measurement."),
    "REL-BIO-006": ("RESEARCH_NEEDED", "Hydration status and heat strain depend on environmental load, dose and thermoregulation; universal constraint is unbounded."),
    "REL-BIO-007": ("RETAIN_V1_INCOMPLETE", "Severe oxygen deficit can constrain cognitive functioning, but task, dose, and tissue measurement must remain bounded."),
    "REL-BIO-008": ("RETAIN_V1_INCOMPLETE", "Acute nociceptive activation can recruit autonomic arousal; chronic pain and appraisal are separate."),
    "REL-BIO-010": ("RETAIN_V1_INCOMPLETE", "Inflammatory signaling can produce acute sickness response; cytokines alone are not the full state."),
    "REL-BIO-011": ("RESEARCH_NEEDED", "Oxygen-carrying capacity and reported fatigue are not directly equated by iron-treatment trials; other pathways remain."),
    "REL-BIO-012": ("RETAIN_V1_INCOMPLETE", "Iron availability contributes to erythropoiesis over time; ferritin is an indicator rather than the entire state."),
    "REL-BIO-013": ("RESEARCH_NEEDED", "Blood glucose availability and cognitive fatigue require exact glucose range, timing and task controls."),
    "REL-BIO-014": ("RESEARCH_NEEDED", "Alcohol effect and physical capacity depend on dose and task; working-memory findings do not establish the stated capacity endpoint."),
    "REL-BIO-015": ("RETAIN_V1_INCOMPLETE", "Sedative effects can alter cognitive fatigue-like experience, but sedation and fatigue require separate measures."),
    "REL-BIO-016": ("RESEARCH_NEEDED", "Medication cognitive-sedative burden is composite; ingredient, dose and physical-capacity endpoint are unresolved."),
    "REL-BIO-017": ("RESEARCH_NEEDED", "Nicotine withdrawal may change cognitive task outcomes; exact cognitive-fatigue state and timing are not isolated."),
    "REL-BIO-018": ("RESEARCH_NEEDED", "Caffeine withdrawal produces fatigue reports, but BIO-026 cognitive fatigue is broader and not isolated by symptom incidence."),
    "REL-BIO-022": ("RESEARCH_NEEDED", "Hearing capacity and Social outcome can share access, age and context causes; no exact causal contrast."),
    "REL-BIO-023": ("RESEARCH_NEEDED", "Sickness response to Social participation requires context, time and direct construct-aligned outcome evidence."),
    "REL-ENV-039": ("RETAIN_V1_INCOMPLETE", "Heat exposure can produce heat strain, conditional on dose, acclimation and physiology."),
    "REL-ENV-041": ("RETAIN_V1_INCOMPLETE", "Environmental water availability can influence hydration only through uptake and loss; exposure mediation remains incomplete."),
}

PILOT_IDS = {"REL-BIO-001", "REL-BIO-002", "REL-BIO-003", "REL-BIO-009", "REL-BIO-021", "REL-ENV-040", *(f"REL-RDS-{i:04d}" for i in range(16, 21)), *(f"REL-V1-BIO-F01-{i:03d}" for i in range(1, 7))}
PSY_IDS = {"REL-BIO-019", "REL-BIO-020", "REL-PSY-057", "REL-PSY-058"}


def build() -> None:
    validate_protection()
    b = read(DATA / "baseline.json")
    source_registry = read(DATA / "candidate-source-registry.json")
    assert len(source_registry) == 35 and all(x["verificationRoute"] == "NCBI_EUTILITIES_PUBMED_ESUMMARY" for x in source_registry.values())
    entities = {x["frozenRecord"]["id"]: {**x["frozenRecord"], "familyId": x["mechanical"]["familyId"]} for x in b["entities"]}
    psy = read(Path(__file__).resolve().parents[1] / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER/relationship-review-registry.json")
    landscapes = {}
    for f, (constructs, mechanism, operations, measurement, boundaries, nums, *prior) in LANDSCAPES.items():
        landscapes[f] = {"constructs": constructs, "mechanisms": mechanism, "operations": operations,
                         "measurement": measurement, "boundaries": boundaries,
                         "sourceIds": ["SRC-CAND-BIO-LAYER-" + n for n in nums],
                         "priorPilot": prior[0] if prior else None, "researchDepth": "FAMILY_LANDSCAPE_ONLY"}
    write(DATA / "family-landscapes.json", {"schemaVersion": "1.0.0", "programId": PROGRAM_ID,
           "method": "Bounded Family landscape; source metadata checked via PubMed. This is not a systematic review per Driver.", "families": landscapes})
    reviews = {}
    for x in b["incidentRelationships"]:
        e = x["edge"]
        rid = e["id"]
        prior = None
        if rid in PILOT_IDS:
            prior = "GOV-BIO-F01-001-2026-09-05"
            if rid in {"REL-BIO-002"}: disposition, reason = "RETAIN_V1_INCOMPLETE", "Prior governed BIO-F01 disposition; unchanged."
            elif rid in {"REL-BIO-001", "REL-BIO-003", "REL-BIO-009", "REL-BIO-021", "REL-ENV-040"}:
                disposition, reason = "REVISION_CANDIDATE", "Prior governed BIO-F01 B01-B05 review proposal; production proposition unchanged."
            else: disposition, reason = "RETAIN_AS_IS", "Prior governed BIO-F01 science reused unchanged."
        elif rid in PSY_IDS:
            p = psy[rid]
            disposition = p["primaryDisposition"]
            reason = "Prior Psychological review reused: " + p["review"]["rationale"]
            prior = "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260917-001"
        else:
            disposition, reason = RELATIONSHIP_REASONS[rid]
        reviews[rid] = {"id": rid, "ownerFamilyId": x["ownerFamilyId"], "consultedFamilyIds": x["consultedFamilyIds"],
             "scope": x["scope"], "semanticType": e["semanticType"], "sourceId": e["source"], "targetId": e["target"],
             "disposition": disposition, "rationale": reason, "priorDecisionOrReview": prior,
             "v1IncompleteFields": x["v1IncompleteFields"], "productionChangeAuthorized": False}
    assert len(reviews) == len(b["incidentRelationships"]) == 39
    write(DATA / "relationship-review-registry.json", reviews)
    by_entity = defaultdict(list)
    for x in b["incidentRelationships"]:
        if x["edge"]["semanticType"] == "CAUSAL":
            for eid in (x["edge"]["source"], x["edge"]["target"]): by_entity[eid].append(x["id"])
    coverage = {}
    deep_targets = {"BIO-025", "BIO-030", "BIO-031", "BIO-066"}
    for eid, ent in sorted(entities.items()):
        family = ent["familyId"]
        rds = ent["entityType"] != "DRIVER"
        sufficient = any(reviews[rid]["disposition"] in {"RETAIN_AS_IS", "RETAIN_V1_INCOMPLETE"} for rid in by_entity[eid])
        status = ("BLOCKED" if eid == "BIO-003" else "EXISTING_PROPOSITION_SUFFICIENT" if rds
                  else "EXISTING_PROPOSITION_SUFFICIENT" if family == "BIO-F01" or sufficient
                  else "INSUFFICIENT_PRELIMINARY_SIGNAL")
        ae = ("NOT_APPLICABLE" if rds else "CANDIDATE_RESEARCHED" if eid in deep_targets
              else "EXISTING_PROPOSITION_SUFFICIENT" if family == "BIO-F01"
              else "INSUFFICIENT_PRELIMINARY_SIGNAL")
        reason = ("RDS derivation and heightened causal-source risk are reviewed separately; no direct EffectAssertion target." if rds else
                  "Inflammatory markers were measured in the endotoxin deep route, but no separate whole-BIO-031 effect was retained." if eid == "BIO-031" else
                  "Exact A&E candidate route received proposition-level research; existing Relationship status is assessed independently." if eid in deep_targets else
                  "Governed BIO-F01 pilot operations and effects are reused." if family == "BIO-F01" else
                  "Bounded Family landscape did not isolate an exact operation-to-this-Driver effect with enough preliminary signal; absence of deep research is not a null finding.")
        coverage[eid] = {"id": eid, "familyId": family, "entityType": ent["entityType"],
              "relationshipStatus": status, "actionsEventsStatus": ae,
              "incidentCausalRelationshipIds": sorted(set(by_entity[eid])),
              "landscapeSourceIds": landscapes[family]["sourceIds"], "reason": reason}
    write(DATA / "negative-coverage-registry.json", coverage)
    rds_rows = []
    for eid, ent in entities.items():
        if ent["entityType"] == "DRIVER": continue
        incoming = [x for x in b["incidentRelationships"] if x["edge"]["semanticType"] == "CAUSAL" and x["edge"]["target"] == eid]
        outgoing = [x for x in b["incidentRelationships"] if x["edge"]["semanticType"] == "CAUSAL" and x["edge"]["source"] == eid]
        deriv = [x for x in b["incidentRelationships"] if x["edge"]["semanticType"] == "DERIVATIONAL" and eid in (x["edge"]["source"], x["edge"]["target"])]
        rds_rows.append({"id": eid, "familyId": ent["familyId"], "definition": ent["definition"],
             "derivation": "NO_VERSIONED_EXACT_RULE_IN_FROZEN_ENTITY", "declaredInputsFromDerivationalEdges": [x["id"] for x in deriv],
             "units": "NOT_EXACTLY_DECLARED", "measurementWindow": "NOT_EXACTLY_DECLARED", "reference": "NOT_EXACTLY_DECLARED",
             "aggregation": "NOT_EXACTLY_DECLARED", "externalInputs": "NOT_EXACTLY_DECLARED",
             "blockedFields": ent.get("blockedFields") or [],
             "incomingCausalIds": [x["id"] for x in incoming], "outgoingCausalIds": [x["id"] for x in outgoing],
             "d10Disposition": "HEIGHTENED_CAUSAL_SOURCE_REVIEW_NEEDED" if outgoing else "DERIVATIONAL_ONLY_OR_NO_CAUSAL_USE",
             "doubleCountRisk": "YES_CONSTITUENT_OVERLAP_REVIEW" if outgoing else "POTENTIAL_IF_CONSTITUENTS_AND_AGGREGATE_BOTH_MODELED",
             "directEffectTargetAllowed": False, "productionChanged": False})
    assert len(rds_rows) == 5
    write(DATA / "rds-review.json", sorted(rds_rows, key=lambda x: x["id"]))
    p = read(DATA / "progress.json")
    for f in p["families"]: p["families"][f] = "TRIAGE"
    write(DATA / "progress.json", p)
    write_doc(DOCS / "BIOLOGICAL_LAYER_PROGRESS.md", "# Biological Layer progress\n\n**ADVISORY — HUMAN DECISION REQUIRED. New GOVERNED = 0 and ACTIVE = 0.**\n\n" +
              f"Program `{PROGRAM_ID}`; frozen main `{b['baseCommit']}`.\n\n| Family | Stage |\n|---|---|\n" +
              "\n".join(f"| {f} | TRIAGE |" for f in p["families"]) + "\n")
    print("Family landscapes", len(landscapes), "relationship reviews", len(reviews),
          "coverage", len(coverage), "RDS", len(rds_rows), "dispositions", dict(Counter(x["disposition"] for x in reviews.values())))


if __name__ == "__main__":
    build()
