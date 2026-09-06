"""Materialize BIO-F01 governance checkpoint 001 and partial activation 001."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import build_bio_f01_pilot as pilot


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "relationship-intervention-v1"
PILOT_DIR = ROOT / "docs" / "governance" / "pilots" / "BIO-F01"
DECISION_ID = "GOV-BIO-F01-001-2026-09-05"
DECISION_PATH = "docs/governance/pilots/BIO-F01/BIO_F01_GOVERNANCE_DECISION_001.md"
AUDIT_ID = "AUD-BIO-F01-RI-V1-20260905-001"
PILOT_HEAD = "0cb77c4722b0d4c474f307d8ae527b8fa6f652cf"
EFFECTIVE_DATE = "2026-09-05"
EFFECTIVE_TIMESTAMP = "2026-09-05T23:00:00Z"
ACTIVATION_DECISION_ID = "GOV-BIO-F01-ACTIVATION-001-2026-09-05"
ACTIVATION_DECISION_PATH = "docs/governance/pilots/BIO-F01/BIO_F01_ACTIVATION_DECISION_001.md"
ACTIVATION_SOURCE_COMMIT = "f3a933d09f98c08fa8c31374ed17658a660943aa"
ACTIVATION_TIMESTAMP = "2026-09-06T01:45:00Z"
ACTIVE_INTERVENTION_IDS = {
    "INT-V1-BIO-F01-001",
    "INT-V1-BIO-F01-003",
    "INT-V1-BIO-F01-006",
    "INT-V1-BIO-F01-007",
    "INT-V1-BIO-F01-008",
}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def transition(
    object_id: str,
    before: str | None,
    after: str,
    before_activation: str,
    after_activation: str,
    actor: str,
    number: int,
) -> dict:
    human = actor == "AUTHORIZED_HUMAN_GOVERNOR"
    return {
        "fromState": {
            "lifecycleStatus": before,
            "activationStatus": before_activation,
        },
        "toState": {
            "lifecycleStatus": after,
            "activationStatus": after_activation,
        },
        "actorClass": actor,
        "rationale": (
            "Exact materialization of the authorized BIO-F01 governance decision; activation was not authorized."
            if human
            else "Reconstructed non-governed candidate workflow from the authorized pilot lineage."
        ),
        "timestamp": EFFECTIVE_TIMESTAMP,
        "objectId": object_id,
        "revision": 1,
        "provenance": f"{AUDIT_ID}:{PILOT_HEAD}:transition-{number}",
        "governanceDecisionRecord": DECISION_PATH if human else None,
        "exactDecisionMaterialization": False,
    }


def governed(object_id: str) -> dict:
    transitions = [
        transition(object_id, None, "CANDIDATE", "NOT_ELIGIBLE", "NOT_ELIGIBLE", "AUTOMATED_PROCESS_OR_AI", 1),
        transition(object_id, "CANDIDATE", "RESEARCH_NEEDED", "NOT_ELIGIBLE", "NOT_ELIGIBLE", "AUTOMATED_PROCESS_OR_AI", 2),
        transition(object_id, "RESEARCH_NEEDED", "REVIEW_READY", "NOT_ELIGIBLE", "NOT_ELIGIBLE", "AUTOMATED_PROCESS_OR_AI", 3),
        transition(object_id, "REVIEW_READY", "GOVERNED", "NOT_ELIGIBLE", "INACTIVE", "AUTHORIZED_HUMAN_GOVERNOR", 4),
    ]
    return {
        "lifecycleStatus": "GOVERNED",
        "activationStatus": "INACTIVE",
        "blockStatus": "NONE",
        "decisionOutcome": "APPROVED",
        "authorityBasis": "V1_NATIVE",
        "decisionRecord": DECISION_PATH,
        "authorizedBy": "authorized human governor",
        "decisionDate": EFFECTIVE_DATE,
        "effectiveVersion": "BIO-F01-GOVERNANCE-001",
        "decisionRationale": "Approved by the exact BIO-F01 human-governance checkpoint; activation explicitly withheld.",
        "supersedesIds": [],
        "transitionProvenance": transitions,
    }


def activate(record: dict) -> None:
    """Materialize the exact authorized GOVERNED/INACTIVE -> ACTIVE transition."""
    governance = record["governance"]
    if governance["activationStatus"] != "INACTIVE":
        raise ValueError(f"Activation source state is not INACTIVE: {record['id']}")
    governance["activationStatus"] = "ACTIVE"
    governance["decisionRecord"] = ACTIVATION_DECISION_PATH
    governance["decisionDate"] = EFFECTIVE_DATE
    governance["effectiveVersion"] = "BIO-F01-PARTIAL-ACTIVATION-001"
    governance["decisionRationale"] = (
        "Exact partial activation authorized by an authorized human governor; "
        "scientific identity, proposition, effect, and scope remain unchanged."
    )
    governance["transitionProvenance"].append({
        "fromState": {
            "lifecycleStatus": "GOVERNED",
            "activationStatus": "INACTIVE",
        },
        "toState": {
            "lifecycleStatus": "GOVERNED",
            "activationStatus": "ACTIVE",
        },
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR",
        "rationale": (
            "Partial activation of the exact record was explicitly authorized "
            "after the BIO-F01 activation-readiness audit."
        ),
        "timestamp": ACTIVATION_TIMESTAMP,
        "objectId": record["id"],
        "revision": record["revision"],
        "provenance": f"{AUDIT_ID}:{ACTIVATION_SOURCE_COMMIT}:activation-001",
        "governanceDecisionRecord": ACTIVATION_DECISION_PATH,
        "exactDecisionMaterialization": False,
    })


def source(
    identifier: str,
    supplemental_id: str,
    title: str,
    authors: list[str],
    year: int,
    publication: str,
    doi: str,
    pmid: str,
    source_type: str,
    supports: list[str],
) -> tuple[dict, dict]:
    record = {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "citationText": f"{'; '.join(authors)}. {title} {publication}. {year}. doi:{doi}. PMID:{pmid}.",
        "title": title,
        "authors": authors,
        "year": year,
        "publication": publication,
        "doi": doi,
        "pmid": pmid,
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "sourceType": source_type,
        "verification": {
            "status": "VERIFIED",
            "system": "PUBMED_NCBI_EUTILITIES",
            "verifiedDate": EFFECTIVE_DATE,
            "identifierChecked": f"PMID:{pmid}; DOI:{doi}",
        },
        "governanceDecisionRecord": DECISION_PATH,
        "auditId": AUDIT_ID,
    }
    registration = {
        "supplementalReferenceId": supplemental_id,
        "canonicalSourceId": identifier,
        "deduplicationOutcome": "NEW_CANONICAL_RECORD",
        "scientificRecordsSupported": supports,
        "verificationStatus": "VERIFIED",
        "pmid": pmid,
        "doi": doi,
        "verificationUrl": record["url"],
    }
    return record, registration


SOURCE_SPECS = [
    ("SRC-530", "BIOF01-EXT-001", "WHO Environmental Noise Guidelines for the European Region: A Systematic Review on Environmental Noise and Effects on Sleep.", ["Basner M", "McGuire S"], 2018, "International Journal of Environmental Research and Public Health", "10.3390/ijerph15030519", "29538344", "SYSTEMATIC_REVIEW_META_ANALYSIS", ["REL-V1-BIO-F01-004", "REL-REV-BIO-F01-B05"]),
    ("SRC-531", "BIOF01-EXT-002", "Environmental Noise and Effects on Sleep: An Update to the WHO Systematic Review and Meta-Analysis.", ["Smith MG", "Cordoza M", "Basner M"], 2022, "Environmental Health Perspectives", "10.1289/EHP10197", "35857401", "SYSTEMATIC_REVIEW_META_ANALYSIS", ["REL-V1-BIO-F01-004", "REL-REV-BIO-F01-B05"]),
    ("SRC-532", "BIOF01-EXT-003", "The bidirectional relationship between sleep problems and chronic musculoskeletal pain: a systematic review with meta-analysis.", ["Runge N", "Ahmed I", "Saueressig T", "Perea J", "Labie C", "Mairesse O", "Nijs J", "Malfliet A", "Verschueren S", "Van Assche D", "de Vlam K", "Van Waeyenberg T", "Van Haute J", "De Baets L"], 2024, "Pain", "10.1097/j.pain.0000000000003279", "38809241", "SYSTEMATIC_REVIEW_META_ANALYSIS", ["REL-REV-BIO-F01-B03"]),
    ("SRC-533", "BIOF01-EXT-004", "The bidirectional association between chronic musculoskeletal pain and sleep-related problems: a systematic review and meta-analysis.", ["Santos M", "Gabani FL", "de Andrade SM", "Bizzozero-Peroni B", "Martínez-Vizcaíno V", "González AD", "Mesas AE"], 2023, "Rheumatology (Oxford)", "10.1093/rheumatology/kead190", "37104741", "SYSTEMATIC_REVIEW_META_ANALYSIS", ["REL-REV-BIO-F01-B03"]),
    ("SRC-534", "BIOF01-EXT-005", "The effect of sleep fragmentation on daytime function.", ["Martin SE", "Engleman HM", "Deary IJ", "Douglas NJ"], 1996, "American Journal of Respiratory and Critical Care Medicine", "10.1164/ajrccm.153.4.8616562", "8616562", "CONTROLLED_EXPERIMENT", ["REL-REV-BIO-F01-B02"]),
    ("SRC-535", "BIOF01-EXT-006", "Sleep inertia.", ["Tassi P", "Muzet A"], 2000, "Sleep Medicine Reviews", "10.1053/smrv.2000.0098", "12531174", "REVIEW", ["REL-V1-BIO-F01-001", "REL-V1-BIO-F01-002"]),
    ("SRC-536", "BIOF01-EXT-007", "Chronic sleep restriction greatly magnifies performance decrements immediately after awakening.", ["McHill AW", "Hull JT", "Cohen DA", "Wang W", "Czeisler CA", "Klerman EB"], 2019, "Sleep", "10.1093/sleep/zsz032", "30722039", "CONTROLLED_EXPERIMENT", ["REL-V1-BIO-F01-001", "REL-V1-BIO-F01-002"]),
    ("SRC-537", "BIOF01-EXT-009", "A novel bedtime pulsatile-release caffeine formula ameliorates sleep inertia symptoms immediately upon awakening.", ["Dornbierer DA", "Yerlikaya F", "Wespi R", "Boxler MI", "Voegel CD", "Schnider L", "Arslan A", "Baur DM", "Baumgartner MR", "Binz TM", "Kraemer T", "Landolt HP"], 2021, "Scientific Reports", "10.1038/s41598-021-98376-z", "34611208", "RANDOMIZED_CROSSOVER_TRIAL", ["INT-V1-BIO-F01-010"]),
    ("SRC-538", "BIOF01-EXT-010", "The dim light melatonin onset across ages, methodologies, and sex and its relationship with morningness/eveningness.", ["Kennaway DJ"], 2023, "Sleep", "10.1093/sleep/zsad033", "36799668", "OBSERVATIONAL_ANALYSIS", ["REL-V1-BIO-F01-005"]),
    ("SRC-539", "BIOF01-EXT-011", "Human responses to bright light of different durations.", ["Chang AM", "Santhi N", "St Hilaire M", "Gronfier C", "Bradstreet DS", "Duffy JF", "Lockley SW", "Kronauer RE", "Czeisler CA"], 2012, "The Journal of Physiology", "10.1113/jphysiol.2011.226555", "22526883", "RANDOMIZED_CONTROLLED_EXPERIMENT", ["INT-V1-BIO-F01-007", "IE-V1-BIO-F01-005"]),
    ("SRC-540", "BIOF01-EXT-012", "The use of exogenous melatonin in delayed sleep phase disorder: a meta-analysis.", ["van Geijlswijk IM", "Korzilius HP", "Smits MG"], 2010, "Sleep", "10.1093/sleep/33.12.1605", "21120122", "META_ANALYSIS", ["INT-V1-BIO-F01-008", "IE-V1-BIO-F01-006"]),
    ("SRC-541", "BIOF01-EXT-013", "Light therapy for the treatment of delayed sleep-wake phase disorder in adults: a systematic review.", ["Gomes JN", "Dias C", "Brito RS", "Lopes JR", "Oliveira IA", "Silva AN", "Salles C"], 2021, "Sleep Science", "10.5935/1984-0063.20200074", "34381579", "SYSTEMATIC_REVIEW", ["INT-V1-BIO-F01-007", "IE-V1-BIO-F01-005"]),
    ("SRC-542", "BIOF01-EXT-014", "Is Cognitive Behavioral Therapy for Insomnia Effective for Improving Sleep Duration in Individuals with Insomnia? A Meta-Analysis of Randomized Controlled Trials.", ["Chan WS", "McCrae CS", "Ng AS"], 2023, "Annals of Behavioral Medicine", "10.1093/abm/kaac061", "36461882", "META_ANALYSIS", ["INT-V1-BIO-F01-004", "INT-V1-BIO-F01-005", "INT-V1-BIO-F01-006", "IE-V1-BIO-F01-004"]),
    ("SRC-543", "BIOF01-EXT-015", "The impact of cognitive behavioural therapy for insomnia on objective sleep parameters: A meta-analysis and systematic review.", ["Mitchell LJ", "Bisdounis L", "Ballesio A", "Omlin X", "Kyle SD"], 2019, "Sleep Medicine Reviews", "10.1016/j.smrv.2019.06.002", "31377503", "SYSTEMATIC_REVIEW_META_ANALYSIS", ["INT-V1-BIO-F01-004", "INT-V1-BIO-F01-005", "INT-V1-BIO-F01-006", "IE-V1-BIO-F01-004"]),
    ("SRC-544", "BIOF01-EXT-016", "Cognitive and behavioral therapies in the treatment of insomnia: A meta-analysis.", ["van Straten A", "van der Zweerde T", "Kleiboer A", "Cuijpers P", "Morin CM", "Lancee J"], 2018, "Sleep Medicine Reviews", "10.1016/j.smrv.2017.02.001", "28392168", "META_ANALYSIS", ["INT-V1-BIO-F01-004", "INT-V1-BIO-F01-005", "INT-V1-BIO-F01-006", "IE-V1-BIO-F01-004"]),
    ("SRC-545", "BIOF01-EXT-017", "Behavioral interventions to extend sleep duration: A systematic review and meta-analysis.", ["Baron KG", "Duffecy J", "Reutrakul S", "Levenson JC", "McFarland MM", "Lee S", "Qeadan F"], 2021, "Sleep Medicine Reviews", "10.1016/j.smrv.2021.101532", "34507028", "SYSTEMATIC_REVIEW_META_ANALYSIS", ["INT-V1-BIO-F01-001", "IE-V1-BIO-F01-001"]),
    ("SRC-546", "BIOF01-EXT-018", "Delayed school start times and adolescent sleep: A systematic review of the experimental evidence.", ["Minges KE", "Redeker NS"], 2016, "Sleep Medicine Reviews", "10.1016/j.smrv.2015.06.002", "26545246", "SYSTEMATIC_REVIEW", ["INT-V1-BIO-F01-003", "IE-V1-BIO-F01-003"]),
    ("SRC-547", "BIOF01-EXT-019", "Adapting shift work schedules for sleep quality, sleep duration, and sleepiness in shift workers.", ["Hulsegge G", "Coenen P", "Gascon GM", "Pahwa M", "Greiner B", "Bohane C", "Wong IS", "Liira J", "Riera R", "Pachito DV"], 2023, "Cochrane Database of Systematic Reviews", "10.1002/14651858.CD010639.pub2", "37694838", "COCHRANE_SYSTEMATIC_REVIEW", ["INT-V1-BIO-F01-002", "REL-REV-BIO-F01-B01"]),
    ("SRC-548", "BIOF01-EXT-022", "Validity of the Japanese version of the Munich ChronoType Questionnaire.", ["Kitamura S", "Hida A", "Aritake S", "Higuchi S", "Enomoto M", "Kato M", "Vetter C", "Roenneberg T", "Mishima K"], 2014, "Chronobiology International", "10.3109/07420528.2014.914035", "24824747", "VALIDATION_STUDY", ["REL-V1-BIO-F01-005"]),
    ("SRC-549", "BIOF01-EXT-024", "Efficacy of melatonin with behavioural sleep-wake scheduling for delayed sleep-wake phase disorder: A double-blind, randomised clinical trial.", ["Sletten TL", "Magee M", "Murray JM", "Gordon CJ", "Lovato N", "Kennaway DJ", "Gwini SM", "Bartlett DJ", "Lockley SW", "Lack LC", "Grunstein RR", "Rajaratnam SMW", "Delayed Sleep on Melatonin (DelSoM) Study Group"], 2018, "PLoS Medicine", "10.1371/journal.pmed.1002587", "29912983", "RANDOMIZED_CONTROLLED_TRIAL", ["INT-V1-BIO-F01-008", "IE-V1-BIO-F01-006"]),
]


RELATIONSHIP_MAP = {
    "REL-CAND-BIO-F01-001": ("REL-V1-BIO-F01-001", "EVA-V1-BIO-F01-REL-001", ["SRC010", "SRC-535", "SRC-536"]),
    "REL-CAND-BIO-F01-002": ("REL-V1-BIO-F01-002", "EVA-V1-BIO-F01-REL-002", ["SRC010", "SRC-535", "SRC-536"]),
    "REL-CAND-BIO-F01-003": ("REL-V1-BIO-F01-003", "EVA-V1-BIO-F01-REL-003", ["SRC086"]),
    "REL-CAND-BIO-F01-004": ("REL-V1-BIO-F01-004", "EVA-V1-BIO-F01-REL-004", ["SRC-530", "SRC-531"]),
    "REL-CAND-BIO-F01-006": ("REL-V1-BIO-F01-005", "EVA-V1-BIO-F01-REL-006", ["SRC009", "SRC011", "SRC-538", "SRC-548"]),
    "REL-CAND-BIO-F01-009": ("REL-V1-BIO-F01-006", "EVA-V1-BIO-F01-REL-009", ["SRC009", "SRC011"]),
}

INTERVENTION_MAP = {
    "INT-CAND-BIO-F01-001": ("INT-V1-BIO-F01-001", ["SRC-545"]),
    "INT-CAND-BIO-F01-002": ("INT-V1-BIO-F01-002", ["SRC-547"]),
    "INT-CAND-BIO-F01-003": ("INT-V1-BIO-F01-003", ["SRC-546"]),
    "INT-CAND-BIO-F01-004": ("INT-V1-BIO-F01-004", ["SRC-542", "SRC-543", "SRC-544"]),
    "INT-CAND-BIO-F01-005": ("INT-V1-BIO-F01-005", ["SRC-542", "SRC-543", "SRC-544"]),
    "INT-CAND-BIO-F01-006": ("INT-V1-BIO-F01-006", ["SRC-542", "SRC-543", "SRC-544"]),
    "INT-CAND-BIO-F01-007": ("INT-V1-BIO-F01-007", ["SRC-539", "SRC-541"]),
    "INT-CAND-BIO-F01-008": ("INT-V1-BIO-F01-008", ["SRC-540", "SRC-549"]),
    "INT-CAND-BIO-F01-010": ("INT-V1-BIO-F01-010", ["SRC-537"]),
}

EFFECT_MAP = {
    "IE-CAND-BIO-F01-001": ("IE-V1-BIO-F01-001", "EVA-V1-BIO-F01-IE-001", ["SRC-545"]),
    "IE-CAND-BIO-F01-003": ("IE-V1-BIO-F01-003", "EVA-V1-BIO-F01-IE-003", ["SRC-546"]),
    "IE-CAND-BIO-F01-004": ("IE-V1-BIO-F01-004", "EVA-V1-BIO-F01-IE-004", ["SRC-542", "SRC-543", "SRC-544"]),
    "IE-CAND-BIO-F01-005": ("IE-V1-BIO-F01-005", "EVA-V1-BIO-F01-IE-005", ["SRC-539", "SRC-541"]),
    "IE-CAND-BIO-F01-006": ("IE-V1-BIO-F01-006", "EVA-V1-BIO-F01-IE-006", ["SRC-540", "SRC-549"]),
}


def materialize() -> None:
    workspace = pilot.build_workspace()
    candidate_relationships = {row["id"]: row for row in workspace["relationships"]}
    candidate_evidence = {row["id"]: row for row in workspace["evidenceAssessments"]}
    candidate_interventions = {row["id"]: row for row in workspace["interventions"]}
    candidate_effects = {row["id"]: row for row in workspace["interventionEffects"]}

    source_records: list[dict] = []
    source_registrations: list[dict] = []
    for spec in SOURCE_SPECS:
        record, registration = source(*spec)
        source_records.append(record)
        source_registrations.append(registration)

    relationships = []
    evidence_assessments = []
    lineage = []
    for candidate_id, (canonical_id, evidence_id, source_ids) in RELATIONSHIP_MAP.items():
        record = copy.deepcopy(candidate_relationships[candidate_id])
        old_evidence_id = record["evidenceAssessmentIds"][0]
        record["id"] = canonical_id
        record["evidenceAssessmentIds"] = [evidence_id]
        record["sourceIds"] = source_ids
        record["governance"] = governed(canonical_id)
        record["compatibility"].update({
            "migrationCompleteness": "COMPLETE",
            "v1Executability": "NOT_EXECUTABLE",
            "blockedFields": [],
        })
        if candidate_id == "REL-CAND-BIO-F01-002":
            record["polarity"] = "CONTEXT_DEPENDENT"
            record["functionalForm"] = {
                "kind": "CYCLIC_STATE_DEPENDENT",
                "specification": "Effect direction and severity depend on biological phase at awakening; no global monotonic ordering of phase is asserted.",
            }
            record["mechanism"] = "Biological circadian phase at awakening changes the physiological state from which alert performance emerges; sleep inertia is typically greater near the biological night/trough, but phase is cyclic rather than a monotonic exposure."
            record["boundaryConditions"] = "Interpret phase relative to a physiological marker, not wall-clock time. Scope is post-awakening assessment and depends on awakening phase, prior sleep amount, sleep stage, task, and assessment window."
            record["applicability"]["context"] = record["boundaryConditions"]
        if candidate_id == "REL-CAND-BIO-F01-004":
            record["mechanism"] = "Discrete nighttime noise events can trigger cortical arousals, awakenings, or sleep-stage changes, reducing continuity independently of a simple average-level description."
            record["boundaryConditions"] = "Evidence is strongest for transportation-noise events in adults and does not generalize to every sound source. Event maximum level, timing, background level, habituation, and individual sensitivity matter; this proposition is distinct from ENV-039 average ambient noise level."
            record["applicability"]["context"] = record["boundaryConditions"]
        if candidate_id == "REL-CAND-BIO-F01-006":
            record["associationSpecification"]["qualitativeStatement"] = "Physiological circadian phase markers are associated with chronotype instrument scores or sleep-timing preferences within the validated instrument and collection protocol; chronotype is not asserted to directly measure phase."
            record["boundaryConditions"] = "Association depends on the chronotype instrument, physiological phase marker, sampling protocol, age, sex, light exposure, and schedule context."
            record["applicability"] = {
                "analyticUnit": "PERSON",
                "populationOrSystem": "Humans assessed with a named chronotype instrument and physiological phase protocol",
                "context": record["boundaryConditions"],
            }
        if candidate_id == "REL-CAND-BIO-F01-009":
            record["boundaryConditions"] = "Endogenous phase is one required input only; external timing or schedule requirements remain mandatory and are not represented as a new ontology entity."
            record["applicability"] = {
                "analyticUnit": "PERSON_OR_GROUP_WITH_ALIGNED_TIME_BASIS",
                "populationOrSystem": "Any scope with a governed endogenous-phase estimate and external timing requirement",
                "context": record["boundaryConditions"],
            }
        relationships.append(record)

        assessment = copy.deepcopy(candidate_evidence[old_evidence_id])
        assessment["id"] = evidence_id
        assessment["assertion"] = {"objectType": "RELATIONSHIP", "objectId": canonical_id}
        assessment["sourceIds"] = source_ids
        assessment["governance"] = governed(evidence_id)
        assessment["reviewProvenance"].update({
            "reviewedAt": EFFECTIVE_TIMESTAMP,
            "reviewedBy": "authorized human governor",
            "sourceSchema": f"{AUDIT_ID}:governance-checkpoint-001",
        })
        if candidate_id == "REL-CAND-BIO-F01-001":
            assessment["evidenceRationale"] = assessment["evidenceRationale"].replace(
                "candidate source BIOF01-EXT-007", "SRC-536"
            )
        if candidate_id == "REL-CAND-BIO-F01-002":
            assessment["evidenceRationale"] = "SRC010, SRC-535, and SRC-536 support a phase-at-awakening effect on sleep inertia and greater impairment near biological night. They do not support a universal positive or negative phase polarity."
            assessment["uncertainty"].append("Circadian phase is cyclic and cannot be interpreted as a universally ordered high-to-low exposure")
        if candidate_id == "REL-CAND-BIO-F01-004":
            assessment["evidenceRationale"] = "SRC-530 directly synthesizes acute nighttime transportation-noise events and objective awakening or sleep-stage responses; SRC-531 updates the broader sleep-disturbance evidence. The claim is limited to event/intermittency semantics and is distinct from average ambient level."
            assessment["limitations"] = [
                "Strongest evidence concerns transportation noise and adults",
                "Event maximum level, background level, timing, and habituation are intertwined",
                "Evidence does not imply that all intermittent sounds reduce continuity",
            ]
        if candidate_id == "REL-CAND-BIO-F01-006":
            assessment["evidenceRationale"] = "SRC009, SRC011, SRC-538, and SRC-548 support an instrument- and protocol-qualified association between chronotype measures and physiological circadian phase. The evidence does not make chronotype a direct measurement of phase."
        evidence_assessments.append(assessment)
        lineage.append({
            "objectType": "RELATIONSHIP",
            "candidateId": candidate_id,
            "canonicalId": canonical_id,
            "status": "MATERIALIZED_AS_GOVERNED_INACTIVE",
            "evidenceCandidateId": old_evidence_id,
            "evidenceCanonicalId": evidence_id,
        })

    interventions = []
    for candidate_id, (canonical_id, source_ids) in INTERVENTION_MAP.items():
        record = copy.deepcopy(candidate_interventions[candidate_id])
        record["id"] = canonical_id
        record["identitySourceIds"] = source_ids
        record["componentInterventionIds"] = [
            INTERVENTION_MAP[item][0] for item in record["componentInterventionIds"]
        ]
        record["governance"] = governed(canonical_id)
        if candidate_id == "INT-CAND-BIO-F01-006":
            record["description"] = "A multicomponent cognitive behavioral therapy for insomnia package. The current model names stimulus-control therapy and sleep-restriction therapy as included known/core components, not as an exhaustive scientific definition; other CBT-I components and variants may exist, and package effects require separate evidence."
        interventions.append(record)
        lineage.append({
            "objectType": "INTERVENTION",
            "candidateId": candidate_id,
            "canonicalId": canonical_id,
            "status": "MATERIALIZED_AS_GOVERNED_INACTIVE",
        })

    effects = []
    for candidate_id, (canonical_id, evidence_id, source_ids) in EFFECT_MAP.items():
        record = copy.deepcopy(candidate_effects[candidate_id])
        old_evidence_id = record["evidenceAssessmentIds"][0]
        record["id"] = canonical_id
        record["interventionId"] = INTERVENTION_MAP[record["interventionId"]][0]
        record["evidenceAssessmentIds"] = [evidence_id]
        record["sourceIds"] = source_ids
        record["governance"] = governed(canonical_id)
        if candidate_id == "IE-CAND-BIO-F01-001":
            record["boundaryConditions"] = "Applies to habitually short-sleeping people when additional sleep opportunity is feasible. Protocol descriptions and achieved sleep vary substantially; opportunity does not guarantee sleep, and chronic insomnia or another sleep disorder requires separate assessment rather than indiscriminate time-in-bed expansion."
        if candidate_id == "IE-CAND-BIO-F01-004":
            record["mechanismOfAction"] = "In adults with chronic insomnia, CBT-I changes sleep-related behaviors and cognitions and can consolidate clinically or subjectively assessed sleep; objective PSG or actigraphy measures need not improve in parallel."
            record["boundaryConditions"] = "Adults with appropriately assessed chronic insomnia using a defined CBT-I package. Subjective or clinical continuity improvement must not be encoded as uniform objective continuity improvement; package variant, delivery, adherence, comorbidity, and measurement method matter."
        if candidate_id == "IE-CAND-BIO-F01-005":
            record["boundaryConditions"] = "Direction depends on the light phase-response curve and biological timing. Intensity, spectrum, duration, prior light history, population, ocular safety, photosensitizing medication, and psychiatric vulnerability constrain application."
        if candidate_id == "IE-CAND-BIO-F01-006":
            record["boundaryConditions"] = "Phase-shifting interpretation requires administration timing relative to biological phase. Dose, formulation, product quality, population, age, comorbidity, and interactions matter; nonspecific sleep-promoting effects are not evidence of phase shift."
        effects.append(record)

        assessment = copy.deepcopy(candidate_evidence[old_evidence_id])
        assessment["id"] = evidence_id
        assessment["assertion"] = {"objectType": "INTERVENTION_EFFECT", "objectId": canonical_id}
        assessment["sourceIds"] = source_ids
        assessment["governance"] = governed(evidence_id)
        assessment["reviewProvenance"].update({
            "reviewedAt": EFFECTIVE_TIMESTAMP,
            "reviewedBy": "authorized human governor",
            "sourceSchema": f"{AUDIT_ID}:governance-checkpoint-001",
        })
        if candidate_id == "IE-CAND-BIO-F01-001":
            assessment["evidenceRationale"] = "SRC-545 supports increased sleep duration from behavioral sleep-extension interventions while documenting substantial heterogeneity and incomplete intervention descriptions. The assertion is limited to short-sleeper/opportunity contexts and excludes indiscriminate extension for chronic insomnia."
        if candidate_id == "IE-CAND-BIO-F01-003":
            assessment["evidenceRationale"] = "SRC-546 supports longer sleep following delayed school starts in adolescent education settings, primarily from natural or quasi-experimental designs. It does not support generalization to adult work schedules."
        if candidate_id == "IE-CAND-BIO-F01-004":
            assessment["evidenceRationale"] = "SRC-542, SRC-543, and SRC-544 support CBT-I benefits for clinical and subjectively assessed continuity in adults with insomnia while showing smaller, mixed, or nonparallel objective PSG and actigraphy changes."
            assessment["conflictingEvidence"] = {
                "sourceIds": ["SRC-542", "SRC-543"],
                "summary": "Objective PSG and actigraphy findings are smaller, mixed, or not parallel to subjective improvement; actigraphy-assessed duration may decrease in some syntheses.",
            }
            assessment["limitations"] = [
                "Package composition, delivery, adherence, and measurement methods vary",
                "Evidence is scoped to adults with chronic insomnia",
                "Sleep-restriction components can produce transient sleepiness and initially reduce time in bed or total sleep time",
            ]
        if candidate_id == "IE-CAND-BIO-F01-005":
            assessment["evidenceDisposition"] = "MIXED"
            assessment["evidenceRationale"] = "SRC-539 supports controlled human circadian phase resetting by appropriately timed light. SRC-541 provides mixed clinical evidence in delayed sleep-wake phase disorder: most included studies did not demonstrate significant between-group differences, although within-group clinical or laboratory phase advances were reported. Timed light can alter endogenous circadian phase under appropriately timed and specified exposure conditions, but findings are heterogeneous, advance versus delay is phase-response dependent, and persistence and generalization evidence are limited."
            assessment["conflictingEvidence"] = {
                "sourceIds": ["SRC-541"],
                "summary": "Most studies in the clinical systematic review did not demonstrate significant between-group differences; controlled clinical findings were not uniformly positive and longer-term persistence evidence was limited.",
            }
            assessment["limitations"] = [
                "Small studies",
                "Protocols differ in intensity, spectrum, duration, and timing",
                "Most SRC-541 studies did not show significant between-group differences",
                "Advance versus delay depends on biological phase and exposure timing",
                "Persistence and generalization evidence are limited",
            ]
        if candidate_id == "IE-CAND-BIO-F01-006":
            assessment["evidenceDisposition"] = "MIXED"
            assessment["evidenceRationale"] = "SRC-540 supports circadian phase advancement from appropriately timed melatonin in relevant delayed-phase populations. SRC-549 found no significant post-treatment DLMO difference for its studied comparison and reported benefits that may have operated primarily through sleep-promoting effects combined with behavioral scheduling. Timed melatonin can alter endogenous circadian phase under appropriately timed and specified conditions, but the phase evidence is mixed and must remain distinct from nonspecific sleep promotion."
            assessment["conflictingEvidence"] = {
                "sourceIds": ["SRC-549"],
                "summary": "SRC-549 found no significant DLMO difference between groups; observed benefits were described as arising largely through sleep-promoting effects combined with behavioral sleep-wake scheduling rather than demonstrated phase shifting.",
            }
            assessment["limitations"] = [
                "Population-specific",
                "Administration timing, dose, and formulation are critical",
                "Product quality, comorbidity, and interactions constrain generalization",
                "Sleep-promoting benefit is not evidence of endogenous phase shifting",
                "SRC-549 reported a null between-group DLMO result",
            ]
        evidence_assessments.append(assessment)
        lineage.append({
            "objectType": "INTERVENTION_EFFECT",
            "candidateId": candidate_id,
            "canonicalId": canonical_id,
            "status": "MATERIALIZED_AS_GOVERNED_INACTIVE",
            "evidenceCandidateId": old_evidence_id,
            "evidenceCanonicalId": evidence_id,
        })

    for record in relationships:
        record["compatibility"]["v1Executability"] = "EXECUTABLE"
        activate(record)
    for record in evidence_assessments:
        activate(record)
    for record in interventions:
        if record["id"] in ACTIVE_INTERVENTION_IDS:
            activate(record)
    for record in effects:
        activate(record)
    active_ids = {
        record["id"]
        for record in relationships + evidence_assessments + interventions + effects
        if record["governance"]["activationStatus"] == "ACTIVE"
    }
    for item in lineage:
        if item["canonicalId"] in active_ids:
            item["status"] = "MATERIALIZED_AS_GOVERNED_ACTIVE"

    store_files = {
        "source-register.json": {"schemaVersion": "1.0.0", "sources": source_records},
        "relationships.json": {"schemaVersion": "1.0.0", "relationships": relationships},
        "evidence-assessments.json": {"schemaVersion": "1.0.0", "evidenceAssessments": evidence_assessments},
        "causal-pathways.json": {"schemaVersion": "1.0.0", "causalPathways": []},
        "interventions.json": {"schemaVersion": "1.0.0", "interventions": interventions},
        "intervention-effects.json": {"schemaVersion": "1.0.0", "interventionEffects": effects},
    }
    for filename, payload in store_files.items():
        write_json(DATA_DIR / filename, payload)

    materialization_manifest = {
        "schemaVersion": "1.0.0",
        "materializationId": "BIO-F01-GOVERNANCE-MATERIALIZATION-001",
        "governanceDecisionId": DECISION_ID,
        "governanceDecisionRecord": DECISION_PATH,
        "activationDecisionId": ACTIVATION_DECISION_ID,
        "activationDecisionRecord": ACTIVATION_DECISION_PATH,
        "activationSourceCommit": ACTIVATION_SOURCE_COMMIT,
        "auditId": AUDIT_ID,
        "frozenScientificBaseline": pilot.BASELINE,
        "pilotHeadBeforeGovernance": PILOT_HEAD,
        "effectiveDate": EFFECTIVE_DATE,
        "activationAuthorized": True,
        "productionGraphEligible": True,
        "candidateLineage": lineage,
        "remainingNonGoverned": {
            "relationships": ["REL-CAND-BIO-F01-005", "REL-CAND-BIO-F01-007", "REL-CAND-BIO-F01-008"],
            "interventions": ["INT-CAND-BIO-F01-009", "INT-CAND-BIO-F01-011"],
            "interventionEffects": ["IE-CAND-BIO-F01-002", "IE-CAND-BIO-F01-007", "IE-CAND-BIO-F01-008", "IE-CAND-BIO-F01-009"],
            "existingRelationshipRevisionProposals": ["REL-REV-BIO-F01-B01", "REL-REV-BIO-F01-B02", "REL-REV-BIO-F01-B03", "REL-REV-BIO-F01-B04", "REL-REV-BIO-F01-B05"],
        },
        "acousticIdentityReview": {
            "originalCandidateId": "INT-CAND-BIO-F01-009",
            "status": "RESEARCH_NEEDED",
            "reason": "The umbrella conflates source, transmission/path, and receiver mechanisms.",
            "newCandidateIds": ["INT-CAND-BIO-F01-011"],
            "newCandidateScope": "Receiver-level personal protection only",
            "sourceAndPathIdentityStatus": "NOT_CREATED_INSUFFICIENT_DIRECT_INTERVENTION_EVIDENCE",
            "effectCandidateId": "IE-CAND-BIO-F01-007",
        },
        "rejectedHypotheses": [
            {"decisionId": "BIOF01-D-H01", "status": "REJECTED_CAUSAL_REPRESENTATION"},
            {"decisionId": "BIOF01-D-H02", "status": "REJECTED_CAUSAL_REPRESENTATION"},
            {"decisionId": "BIOF01-D-H03", "status": "REJECTED_CAUSAL_REPRESENTATION"},
            {"decisionId": "BIOF01-D-H04", "status": "REJECTED_TEMPORAL_TRANSITION_REPRESENTATION"},
            {"decisionId": "BIOF01-D-H05", "status": "REJECTED_DUPLICATE"},
        ],
        "governedInactiveCounts": {
            "relationships": 0,
            "causalRelationships": 0,
            "noncausalRelationships": 0,
            "interventions": sum(row["governance"]["activationStatus"] == "INACTIVE" for row in interventions),
            "interventionEffects": 0,
            "evidenceAssessments": 0,
            "totalScientificRecords": sum(
                row["governance"]["activationStatus"] == "INACTIVE"
                for row in relationships + interventions + effects + evidence_assessments
            ),
        },
        "governedActiveCounts": {
            "relationships": len(relationships),
            "causalRelationships": sum(row["relationFamily"] == "CAUSAL" for row in relationships),
            "noncausalRelationships": sum(row["relationFamily"] != "CAUSAL" for row in relationships),
            "interventions": sum(row["governance"]["activationStatus"] == "ACTIVE" for row in interventions),
            "interventionEffects": len(effects),
            "evidenceAssessments": len(evidence_assessments),
            "totalScientificRecords": len(active_ids),
        },
        "newActiveRecords": len(active_ids),
    }
    write_json(DATA_DIR / "materialization-manifest.json", materialization_manifest)

    source_manifest = {
        "schemaVersion": "1.0.0",
        "auditId": AUDIT_ID,
        "governanceDecisionId": DECISION_ID,
        "verificationDate": EFFECTIVE_DATE,
        "currentLegacySourceCount": 529,
        "supplementalSourcesReviewedForRegistration": 20,
        "registeredCount": len(source_records),
        "duplicateCount": 0,
        "rejectedOrUnverifiedCount": 0,
        "registrations": source_registrations,
        "notRegistered": [
            {"supplementalReferenceId": "BIOF01-EXT-008", "reason": "Supports a research-needed sleep-inertia countermeasure question only."},
            {"supplementalReferenceId": "BIOF01-EXT-020", "reason": "Acoustic Intervention identity and effect remain research-needed."},
            {"supplementalReferenceId": "BIOF01-EXT-021", "reason": "Moderation assertion remains research-needed."},
            {"supplementalReferenceId": "BIOF01-EXT-023", "reason": "Background for a non-promoted nap hypothesis."},
            {"supplementalReferenceId": "BIOF01-EXT-025", "reason": "Pathway non-creation; no governed pathway assertion."},
        ],
    }
    write_json(PILOT_DIR / "BIO_F01_SOURCE_REGISTRATION_MANIFEST.json", source_manifest)

    audit_manifest = pilot.build_manifest(workspace)
    audit_manifest.update({
        "status": "PARTIALLY_ACTIVATED",
        "governanceCheckpoint": {
            "decisionId": DECISION_ID,
            "decisionRecord": "BIO_F01_GOVERNANCE_DECISION_001.md",
            "effectiveDate": EFFECTIVE_DATE,
            "pilotHeadBeforeGovernance": PILOT_HEAD,
            "activationAuthorized": False,
        },
        "activationCheckpoint": {
            "decisionId": ACTIVATION_DECISION_ID,
            "decisionRecord": "BIO_F01_ACTIVATION_DECISION_001.md",
            "effectiveDate": EFFECTIVE_DATE,
            "preActivationHead": ACTIVATION_SOURCE_COMMIT,
            "activationAuthorized": True,
            "scope": "PARTIAL_EXACT_SET",
        },
        "newGovernedRecords": 31,
        "newInactiveRecords": materialization_manifest["governedInactiveCounts"]["totalScientificRecords"],
        "newActiveRecords": materialization_manifest["governedActiveCounts"]["totalScientificRecords"],
        "sourceRegistration": {
            "reviewedForRegistration": 20,
            "registered": 20,
            "duplicates": 0,
            "rejectedOrUnverified": 0,
            "manifest": "BIO_F01_SOURCE_REGISTRATION_MANIFEST.json",
        },
    })
    audit_manifest["evidenceSummary"].update({
        "supplementalSourceRegistrationStatus": "SELECTIVELY_CANONICALIZED_FOR_GOVERNED_ASSERTIONS",
        "supplementalSourcesRegistered": 20,
        "governedEvidenceAssessments": len(evidence_assessments),
        "nonGovernedEvidenceAssessments": len(candidate_evidence) - len(evidence_assessments),
        "assessmentsWithCanonicalSourceIds": len(evidence_assessments),
        "assessmentsPendingCanonicalSourceRegistration": 0,
    })
    audit_manifest["openItems"] = [
        item
        for item in audit_manifest["openItems"]
        if not item.startswith("Register supplemental pilot sources")
    ]
    audit_manifest["openItems"].append(
        "Five supplemental references used only for research-needed, background, or non-created assertions remain audit-log references and were not canonically registered."
    )
    audit_manifest["openItems"].append(
        "INT-V1-BIO-F01-002, INT-V1-BIO-F01-004, INT-V1-BIO-F01-005, and INT-V1-BIO-F01-010 remain governed inactive pending their own governed active effects."
    )
    audit_manifest["canonicalIntegrity"].update({
        "activeRelationships": 456,
        "activeCausalRelationships": 435,
    })
    audit_manifest["documents"].extend([
        "BIO_F01_GOVERNANCE_DECISION_001.md",
        "BIO_F01_EXISTING_RELATIONSHIP_REVISION_PROPOSALS.md",
        "BIO_F01_SOURCE_REGISTRATION_MANIFEST.json",
        "BIO_F01_ACTIVATION_DECISION_001.md",
    ])
    write_json(pilot.WORKSPACE, workspace)
    write_json(pilot.MANIFEST, audit_manifest)


def main() -> None:
    materialize()
    print(f"Materialized {DECISION_ID} and {ACTIVATION_DECISION_ID}")
    print("  Governed active Relationships: 6 (4 causal, 2 noncausal)")
    print("  Governed active Interventions: 5; governed inactive Interventions: 4")
    print("  Governed active InterventionEffects: 5")
    print("  Governed active EvidenceAssessments: 11")
    print("  New active records: 27")
    print("  Registered native V1 sources: 20")


if __name__ == "__main__":
    main()
