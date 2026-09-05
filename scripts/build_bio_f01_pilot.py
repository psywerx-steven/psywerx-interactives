"""Materialize the non-governed BIO-F01 Relationship + Intervention V1 pilot.

The curated scientific judgments in this file are candidate audit outputs only.
The builder never modifies canonical entities, relationships, or source records.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "data" / "candidates" / "relationship-intervention-v1" / "workspace.json"
PILOT_DIR = ROOT / "docs" / "governance" / "pilots" / "BIO-F01"
MANIFEST = PILOT_DIR / "BIO_F01_AUDIT_MANIFEST.json"
BASELINE = "5001611852107f2b95b8f722c71224dc7a538d47"
AUDIT_ID = "AUD-BIO-F01-RI-V1-20260905-001"
CREATED_AT = "2026-09-05T12:00:00Z"


def _read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _canonical_lf_sha256(path: str) -> str:
    """Hash governed JSON text without platform checkout line-ending variance."""
    payload = (ROOT / path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _transition(object_id: str, lifecycle: str) -> list[dict]:
    transitions = []
    states = [None, "CANDIDATE"]
    if lifecycle in {"RESEARCH_NEEDED", "REVIEW_READY"}:
        states.append("RESEARCH_NEEDED")
    if lifecycle == "REVIEW_READY":
        states.append("REVIEW_READY")
    for index, (before, after) in enumerate(zip(states, states[1:]), start=1):
        transitions.append({
            "fromState": {"lifecycleStatus": before, "activationStatus": "NOT_ELIGIBLE"},
            "toState": {"lifecycleStatus": after, "activationStatus": "NOT_ELIGIBLE"},
            "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "rationale": (
                "Created as a non-governed BIO-F01 pilot candidate."
                if after == "CANDIDATE"
                else "Structured evidence audit indicated additional research or qualification was required."
                if after == "RESEARCH_NEEDED"
                else "Structured evidence audit completed the candidate packet for human scientific review."
            ),
            "timestamp": CREATED_AT,
            "objectId": object_id,
            "revision": 1,
            "provenance": f"{AUDIT_ID}:transition-{index}",
            "governanceDecisionRecord": None,
            "exactDecisionMaterialization": False,
        })
    return transitions


def governance(object_id: str, lifecycle: str = "REVIEW_READY", blocked: bool = False) -> dict:
    return {
        "lifecycleStatus": lifecycle,
        "activationStatus": "NOT_ELIGIBLE",
        "blockStatus": "NEEDS_GOVERNANCE_INPUT" if blocked else "NONE",
        "decisionOutcome": "NOT_DECIDED",
        "authorityBasis": "V1_NATIVE",
        "decisionRecord": None,
        "authorizedBy": None,
        "decisionDate": None,
        "effectiveVersion": None,
        "decisionRationale": None,
        "supersedesIds": [],
        "transitionProvenance": _transition(object_id, lifecycle),
    }


def compatibility(lifecycle: str, blocked_fields: list[str] | None = None) -> dict:
    return {
        "sourceSchema": "RELATIONSHIP_V1",
        "authorityStatus": "V1_LIFECYCLE",
        "migrationCompleteness": "COMPLETE" if lifecycle == "REVIEW_READY" else "INCOMPLETE",
        "v1Executability": "NOT_EXECUTABLE",
        "blockedFields": blocked_fields or [],
        "legacyRelationFamily": None,
        "legacyScientificFields": None,
        "legacyRecordHash": None,
        "legacyRecord": None,
    }


def relationship(
    identifier: str,
    family: str,
    predicate: str,
    source: str | None,
    source_type: str | None,
    target: str | None,
    target_type: str | None,
    *,
    lifecycle: str = "REVIEW_READY",
    polarity: str | None = None,
    mechanism: str | None = None,
    boundaries: str | None = None,
    evidence_id: str,
    source_ids: list[str],
    association: dict | None = None,
    moderated_relationship: str | None = None,
    moderators: list[dict] | None = None,
    moderation_direction: str | None = None,
) -> dict:
    causal = family == "CAUSAL"
    moderation = family == "MODERATION"
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "relationFamily": family,
        "predicate": predicate,
        "symmetry": "SYMMETRIC" if predicate == "ASSOCIATED_WITH" else "DIRECTED",
        "causalClaim": causal,
        "sourceEntityId": None if moderation else source,
        "sourceEntityType": None if moderation else source_type,
        "targetEntityId": None if moderation else target,
        "targetEntityType": None if moderation else target_type,
        "causalClaimRole": "MODELED_LOCAL_LINK" if causal else None,
        "legacyDirectness": None,
        "polarity": polarity if causal else None,
        "mechanism": mechanism,
        "boundaryConditions": boundaries,
        "applicability": ({
            "analyticUnit": "PERSON",
            "populationOrSystem": "Humans within the population and protocol stated by the evidence",
            "context": boundaries,
        } if causal else None),
        "associationSpecification": association,
        "temporalSpecification": None,
        "moderatedRelationshipId": moderated_relationship,
        "moderatorSpecifications": moderators or [],
        "combinationRule": "INDIVIDUAL" if moderation else None,
        "moderationDirection": moderation_direction,
        "causalReviewGate": "STANDARD_CAUSAL" if causal else None,
        "rdsSafeguards": None,
        "functionalForm": None,
        "exposurePattern": None,
        "causalLag": None,
        "persistence": None,
        "evidenceAssessmentIds": [evidence_id],
        "sourceIds": source_ids,
        "governance": governance(identifier, lifecycle),
        "compatibility": compatibility(
            lifecycle,
            ["canonicalSourceRegistration"] if not source_ids else [],
        ),
    }


def evidence(
    identifier: str,
    object_id: str,
    object_type: str,
    lifecycle: str,
    source_ids: list[str],
    rationale: str,
    strength: str,
    confidence: str,
    disposition: str,
    designs: list[tuple[str, str]],
    limitations: list[str],
    uncertainty: list[str],
    conflicts: str | None = None,
) -> dict:
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "assertion": {"objectType": object_type, "objectId": object_id},
        "sourceIds": source_ids,
        "evidenceRationale": rationale,
        "evidenceStrength": strength,
        "confidence": confidence,
        "evidenceDisposition": disposition,
        "population": "Human participants; exact populations are enumerated in the BIO-F01 evidence summary.",
        "context": "Scope is limited to the exposures, interventions, timing, and settings stated in the cited evidence.",
        "studyDesignCharacterizations": [
            {"designType": design_type, "specification": specification}
            for design_type, specification in designs
        ],
        "quantitativeEstimate": None,
        "uncertainty": uncertainty,
        "conflictingEvidence": {"sourceIds": [], "summary": conflicts},
        "limitations": limitations,
        "reviewProvenance": {
            "createdAt": CREATED_AT,
            "createdByActorClass": "AUTOMATED_PROCESS_OR_AI",
            "reviewedAt": None,
            "reviewedBy": None,
            "sourceSchema": f"{AUDIT_ID}:structured-evidence-search",
        },
        "governance": governance(identifier, lifecycle),
    }


def intervention(
    identifier: str,
    name: str,
    category: str,
    description: str,
    *,
    kind: str = "ATOMIC",
    components: list[str] | None = None,
    lifecycle: str = "REVIEW_READY",
) -> dict:
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "canonicalName": name,
        "aliases": [],
        "interventionKind": kind,
        "category": category,
        "categorySpecification": None,
        "description": description,
        "componentInterventionIds": components or [],
        "identitySourceIds": [],
        "externalCrosswalks": [],
        "governance": governance(identifier, lifecycle),
    }


def effect(
    number: int,
    intervention_id: str,
    driver_id: str,
    mode: str,
    direction: str,
    mechanism: str,
    population: str,
    context: str,
    boundaries: str,
    modalities: list[str],
    evidence_sources: list[str],
    outcome_ids: list[str],
    *,
    lifecycle: str = "REVIEW_READY",
    scale: str = "PERSON",
    implementers: list[str] | None = None,
    prerequisites: list[str] | None = None,
    risks: list[str] | None = None,
    unintended: list[str] | None = None,
) -> dict:
    identifier = f"IE-CAND-BIO-F01-{number:03d}"
    evidence_id = f"EVA-CAND-BIO-F01-IE-{number:03d}"
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "interventionId": intervention_id,
        "targetKind": "DRIVER",
        "targetDriverId": driver_id,
        "targetRelationshipId": None,
        "mechanisticDriverIds": [],
        "effectMode": mode,
        "intendedDirection": direction,
        "mechanismOfAction": mechanism,
        "targetPopulationOrAudience": population,
        "populationScope": "SUBGROUP_TARGETED",
        "context": context,
        "contextScope": "CONTEXT_DEPENDENT",
        "scale": scale,
        "boundaryConditions": boundaries,
        "implementers": implementers or [],
        "deliveryModalities": modalities,
        "deliveryModalitySpecification": None,
        "channels": [],
        "prerequisites": prerequisites or [],
        "moderatorEntityIds": [],
        "outcomeEntityIds": outcome_ids,
        "measureOfEffectIds": [],
        "unintendedEffects": unintended or [],
        "risks": risks or [],
        "ethicalLegalConstraints": ["Use must respect informed consent, clinical scope, and applicable workplace or education law."],
        "evidenceAssessmentIds": [evidence_id],
        "sourceIds": evidence_sources,
        "governance": governance(identifier, lifecycle),
    }


def build_workspace() -> dict:
    rel_specs = [
        # identifier, family, predicate, source, source type, target, target type,
        # lifecycle, polarity, mechanism, boundaries, evidence, canonical sources
        ("REL-CAND-BIO-F01-001", "CAUSAL", "CAUSES", "BIO-001", "DRIVER", "BIO-005", "DRIVER", "REVIEW_READY", "NEGATIVE",
         "Greater obtained sleep, within an individually relevant range, reduces homeostatic sleep pressure that otherwise magnifies post-awakening impairment.",
         "Applies to post-awakening assessment; effect varies by prior restriction, sleep stage at awakening, circadian phase, task, and individual vulnerability.",
         "EVA-CAND-BIO-F01-REL-001", ["SRC010"]),
        ("REL-CAND-BIO-F01-002", "CAUSAL", "CAUSES", "BIO-004", "DRIVER", "BIO-005", "DRIVER", "REVIEW_READY", "CONTEXT_DEPENDENT",
         "Circadian phase at awakening changes the magnitude and dissipation of sleep inertia through circadian regulation of arousal.",
         "Phase is cyclic rather than better/worse; the claim is conditional on awakening phase, prior sleep, sleep stage, and task.",
         "EVA-CAND-BIO-F01-REL-002", ["SRC010"]),
        ("REL-CAND-BIO-F01-003", "CAUSAL", "CONSTRAINS", "BIO-061", "DRIVER", "BIO-001", "DRIVER", "REVIEW_READY", "NEGATIVE",
         "Caffeine exposure sufficiently near planned sleep can delay sleep initiation and reduce obtained sleep duration through adenosine-receptor antagonism and increased alerting.",
         "Depends on dose, formulation, metabolism, tolerance, administration time, habitual use, and available sleep opportunity.",
         "EVA-CAND-BIO-F01-REL-003", ["SRC086"]),
        ("REL-CAND-BIO-F01-004", "CAUSAL", "CONSTRAINS", "ENV-041", "DRIVER", "BIO-002", "DRIVER", "REVIEW_READY", "NEGATIVE",
         "Intermittent nighttime sound events provoke cortical arousals and awakenings that fragment an ongoing sleep episode.",
         "Evidence is strongest for transportation-noise events in adults; habituation, event level, sound meaning, insulation, hearing, and setting modify response.",
         "EVA-CAND-BIO-F01-REL-004", []),
        ("REL-CAND-BIO-F01-005", "CAUSAL", "CAUSES", "BIO-002", "DRIVER", "BIO-028", "DRIVER", "RESEARCH_NEEDED", "NEGATIVE",
         "More continuous sleep may reduce subsequent persistent pain burden through nociceptive, inflammatory, affective, and attentional processes.",
         "Most available evidence concerns broad sleep problems and pain, is observational, and does not isolate canonical Sleep Continuity; causal specificity remains unresolved.",
         "EVA-CAND-BIO-F01-REL-005", []),
    ]
    relationships = [
        relationship(
            identifier, family, predicate, source, source_type, target, target_type,
            lifecycle=lifecycle, polarity=polarity, mechanism=mechanism,
            boundaries=boundaries, evidence_id=evidence_id, source_ids=source_ids,
        )
        for (identifier, family, predicate, source, source_type, target, target_type,
             lifecycle, polarity, mechanism, boundaries, evidence_id, source_ids) in rel_specs
    ]
    relationships.extend([
        relationship(
            "REL-CAND-BIO-F01-006", "EMPIRICAL_NONCAUSAL", "ASSOCIATED_WITH",
            "BIO-004", "DRIVER", "BIO-073", "DRIVER",
            mechanism="Chronotype instruments covary with physiological circadian phase markers but are not interchangeable measurements.",
            boundaries="Instrument, age, sleep schedule, light history, and phase-marker protocol must be stated.",
            evidence_id="EVA-CAND-BIO-F01-REL-006", source_ids=["SRC009", "SRC011"],
            association={
                "temporalScope": "REPEATED_MIXED",
                "qualitativeStatement": "Earlier chronotype measures are associated with earlier endogenous circadian phase markers under aligned protocols.",
                "strengthEstimate": None,
                "constituentOverlapCheck": "Chronotype is partly shaped by phase but is not calculated from the canonical Endogenous Circadian Phase entity; instrument overlap and schedule contamination must be reported.",
            },
        ),
        relationship(
            "REL-CAND-BIO-F01-007", "EMPIRICAL_NONCAUSAL", "ASSOCIATED_WITH",
            "BIO-001", "DRIVER", "BIO-002", "DRIVER", lifecycle="RESEARCH_NEEDED",
            mechanism="Sleep episodes with reduced duration often also have reduced continuity, but shared sleep-opportunity and measurement components can induce covariance.",
            boundaries="The duration metric must exclude or explicitly account for wake-after-sleep-onset and time-in-bed overlap.",
            evidence_id="EVA-CAND-BIO-F01-REL-007", source_ids=["SRC005", "SRC006"],
            association={
                "temporalScope": "REPEATED_MIXED",
                "qualitativeStatement": "Sleep Duration and Sleep Continuity commonly covary within sleep-health studies, without a generic causal direction being established.",
                "strengthEstimate": None,
                "constituentOverlapCheck": "Present: total sleep time and sleep-efficiency/fragmentation measures can share the same scored epochs or denominator; effect estimates require non-overlapping operationalizations or explicit correction.",
            },
        ),
        relationship(
            "REL-CAND-BIO-F01-008", "MODERATION", "MODERATES",
            None, None, None, None, lifecycle="RESEARCH_NEEDED",
            mechanism="The performance consequences of restricted sleep vary by biological night versus day, but available experiments do not yet map cleanly to the governed Cognitive Fatigue endpoint.",
            boundaries="Requires aligned sleep-dose, circadian-phase, outcome, and population definitions; performance is not automatically Cognitive Fatigue.",
            evidence_id="EVA-CAND-BIO-F01-REL-008", source_ids=["SRC001", "SRC010"],
            moderated_relationship="REL-BIO-002",
            moderators=[{
                "entityId": "BIO-004",
                "entityType": "DRIVER",
                "stateOrRange": "Endogenous phase at the time post-sleep-loss fatigue is assessed",
                "scaleInterpretation": "Cyclic phase; biological-night versus biological-day regions must be protocol-defined",
            }],
            moderation_direction="CONTEXT_DEPENDENT",
        ),
        relationship(
            "REL-CAND-BIO-F01-009", "DERIVATIONAL", "DERIVED_FROM",
            "BIO-003", "RELATIONAL_DERIVED_STATE", "BIO-004", "DRIVER",
            mechanism="Endogenous Circadian Phase is the internal-timing constituent used to calculate Circadian Timing Alignment.",
            boundaries="The external timing requirement, phase measure, interval, alignment convention, and update rule must also be supplied.",
            evidence_id="EVA-CAND-BIO-F01-REL-009", source_ids=["SRC009", "SRC011"],
        ),
    ])

    rel_evidence = [
        evidence("EVA-CAND-BIO-F01-REL-001", "REL-CAND-BIO-F01-001", "RELATIONSHIP", "REVIEW_READY", ["SRC010"],
                 "SRC010 and candidate source BIOF01-EXT-007 synthesize and experimentally demonstrate that prior sleep restriction magnifies sleep inertia after awakening.",
                 "MODERATE", "MODERATE", "SUPPORTS", [("SYNTHESIS", "Narrative review"), ("EXPERIMENTAL", "Controlled laboratory protocols")],
                 ["Outcome and protocol heterogeneity", "Evidence emphasizes restriction rather than a universal monotonic duration effect"], ["Exact dose-response and persistence are not established"]),
        evidence("EVA-CAND-BIO-F01-REL-002", "REL-CAND-BIO-F01-002", "RELATIONSHIP", "REVIEW_READY", ["SRC010"],
                 "SRC010 and BIOF01-EXT-006/007 report worse post-awakening impairment near the biological-night trough and interactions with prior sleep loss.",
                 "MODERATE", "MODERATE", "SUPPORTS", [("SYNTHESIS", "Narrative review"), ("EXPERIMENTAL", "Forced-desynchrony laboratory protocols")],
                 ["Circadian phase is cyclic", "Small controlled samples"], ["Polarity cannot be expressed as universally positive or negative"]),
        evidence("EVA-CAND-BIO-F01-REL-003", "REL-CAND-BIO-F01-003", "RELATIONSHIP", "REVIEW_READY", ["SRC086"],
                 "SRC086 reviews controlled evidence that caffeine timing can delay sleep and reduce sleep duration while improving wake performance.",
                 "MODERATE", "MODERATE", "SUPPORTS", [("SYNTHESIS", "Review of caffeine, sleep, and performance")],
                 ["Substantial interindividual variation", "Dose and administration timing are identity-defining exposure details"], ["Tolerance and metabolism limit generalization"]),
        evidence("EVA-CAND-BIO-F01-REL-004", "REL-CAND-BIO-F01-004", "RELATIONSHIP", "REVIEW_READY", [],
                 "BIOF01-EXT-001/002 synthesize polysomnographic and field evidence: discrete transportation-noise events increase cortical awakenings; supplemental sources await canonical source registration.",
                 "MODERATE", "MODERATE", "SUPPORTS", [("SYNTHESIS", "Systematic reviews and meta-analyses including polysomnographic studies")],
                 ["Evidence strongest for transportation noise", "Self-report estimates depend on question wording"], ["Generalization to all intermittent sounds is uncertain"]),
        evidence("EVA-CAND-BIO-F01-REL-005", "REL-CAND-BIO-F01-005", "RELATIONSHIP", "RESEARCH_NEEDED", [],
                 "BIOF01-EXT-003/004 show prospective bidirectional associations between broad sleep problems and chronic musculoskeletal pain; continuity-specific causal isolation is incomplete.",
                 "MIXED", "LOW", "MIXED", [("SYNTHESIS", "Systematic reviews/meta-analyses of prospective cohorts")],
                 ["Residual confounding", "Broad sleep-problem exposure is not identical to Sleep Continuity", "Pain phenotypes vary"],
                 ["Directionality is supported prospectively but intervention evidence for the exact endpoint remains limited"],
                 "Different reviews rate certainty and direction-specific support differently."),
        evidence("EVA-CAND-BIO-F01-REL-006", "REL-CAND-BIO-F01-006", "RELATIONSHIP", "REVIEW_READY", ["SRC009", "SRC011"],
                 "SRC009/SRC011 and BIOF01-EXT-022 report association between validated chronotype measures and physiological circadian phase while warning that measures are not equivalent.",
                 "MODERATE", "MODERATE", "SUPPORTS", [("SYNTHESIS", "Pooled physiological reference data and reviews"), ("OBSERVATIONAL_CROSS_SECTIONAL", "Instrument validation studies")],
                 ["Chronotype measures incorporate preference or observed sleep timing", "Age and schedule affect both measures"], ["Strength depends on instrument and protocol"]),
        evidence("EVA-CAND-BIO-F01-REL-007", "REL-CAND-BIO-F01-007", "RELATIONSHIP", "RESEARCH_NEEDED", ["SRC005", "SRC006"],
                 "The governed sources routinely measure duration and continuity together, but do not establish a stable non-overlapping association parameter for the canonical pair.",
                 "LIMITED", "LOW", "INSUFFICIENT", [("SYNTHESIS", "Mixed sleep-problem reviews")],
                 ["Shared epochs and denominators", "Construct definitions differ across studies"], ["Association may be partly mathematical"]),
        evidence("EVA-CAND-BIO-F01-REL-008", "REL-CAND-BIO-F01-008", "MODERATION", "RESEARCH_NEEDED", ["SRC001", "SRC010"],
                 "BIOF01-EXT-021 reports a sleep-dose by circadian-phase interaction for vigilance; mapping that outcome to governed Cognitive Fatigue is not yet justified.",
                 "MODERATE", "LOW", "INSUFFICIENT", [("EXPERIMENTAL", "Forced-desynchrony controlled laboratory study")],
                 ["Small healthy-male sample", "Vigilance performance is not identical to Cognitive Fatigue"], ["Endpoint alignment is unresolved"]),
        evidence("EVA-CAND-BIO-F01-REL-009", "REL-CAND-BIO-F01-009", "RELATIONSHIP", "REVIEW_READY", ["SRC009", "SRC011"],
                 "The governed RDS derivation specification explicitly names BIO-004 as a required constituent; cited circadian sources support the distinction between internal phase and alignment.",
                 "STRONG", "HIGH", "SUPPORTS", [("THEORETICAL", "Governed derivation specification")],
                 ["External timing requirements remain an unmodeled parameter"], ["Derivation convention must be selected at analysis time"]),
    ]

    interventions = [
        intervention("INT-CAND-BIO-F01-001", "Behavioral sleep-extension protocol", "TRAINING_OR_SKILL", "A structured protocol that expands planned sleep opportunity and supports adherence long enough to increase obtained sleep."),
        intervention("INT-CAND-BIO-F01-002", "Protected sleep-opportunity scheduling", "POLICY_RULE_OR_STANDARD", "A schedule or rule that protects a defined sleep opportunity from work, duty, or avoidable interruption.", lifecycle="RESEARCH_NEEDED"),
        intervention("INT-CAND-BIO-F01-003", "Delayed school start-time policy", "POLICY_RULE_OR_STANDARD", "A policy that moves mandatory school start time later while retaining an evaluable implementation schedule."),
        intervention("INT-CAND-BIO-F01-004", "Stimulus-control therapy for insomnia", "TRAINING_OR_SKILL", "A behavioral treatment component that reassociates bed and bedroom cues with sleep and limits wakeful activity in bed."),
        intervention("INT-CAND-BIO-F01-005", "Sleep-restriction therapy for insomnia", "TRAINING_OR_SKILL", "A clinician-guided behavioral treatment component that initially limits time in bed and titrates it as sleep efficiency changes."),
        intervention("INT-CAND-BIO-F01-006", "Cognitive behavioral therapy for insomnia package", "SERVICE_OR_SUPPORT", "A multicomponent insomnia treatment package containing at least stimulus control and sleep-restriction therapy.", kind="PACKAGE", components=["INT-CAND-BIO-F01-004", "INT-CAND-BIO-F01-005"]),
        intervention("INT-CAND-BIO-F01-007", "Timed bright-light exposure", "BIOLOGICAL_OR_CLINICAL", "Exposure to controlled bright light at a specified circadian time, intensity, spectrum, and duration."),
        intervention("INT-CAND-BIO-F01-008", "Timed exogenous melatonin administration", "BIOLOGICAL_OR_CLINICAL", "Administration of exogenous melatonin at a specified dose and circadian/clock time."),
        intervention("INT-CAND-BIO-F01-009", "Nighttime acoustic attenuation", "ENVIRONMENTAL_OR_CHOICE_ARCHITECTURE", "Umbrella candidate spanning source control, transmission/path attenuation, and receiver protection; the identity boundary remains unresolved and cannot support a governed effect.", lifecycle="RESEARCH_NEEDED"),
        intervention("INT-CAND-BIO-F01-010", "Pre-awakening timed caffeine delivery", "BIOLOGICAL_OR_CLINICAL", "A formulation or delivery schedule designed to produce caffeine exposure shortly before planned awakening."),
        intervention("INT-CAND-BIO-F01-011", "Nighttime personal acoustic protection", "ENVIRONMENTAL_OR_CHOICE_ARCHITECTURE", "Receiver-level reduction of sound reaching a sleeper through personal hearing protection; evidence and safety boundaries remain under review.", lifecycle="RESEARCH_NEEDED"),
    ]

    effects = [
        effect(1, "INT-CAND-BIO-F01-001", "BIO-001", "CHANGE_LEVEL", "INCREASE",
               "Expanded planned opportunity plus adherence permits additional sleep to be obtained.",
               "Adolescents and adults with habitually short sleep", "Home or operational schedules in which sleep opportunity can be expanded",
               "Large heterogeneity; opportunity does not guarantee sleep and clinical sleep disorders require separate assessment.",
               ["HUMAN_DELIVERED", "DIGITAL_OR_AUTOMATED"], [], ["RDS-0003", "RDS-0004"],
               prerequisites=["A feasible expansion of sleep opportunity"], risks=["Excess time in bed may worsen insomnia in susceptible people"]),
        effect(2, "INT-CAND-BIO-F01-002", "BIO-001", "CHANGE_LEVEL", "INCREASE",
               "Protected off-duty time reduces external truncation of sleep opportunity.",
               "Shift workers and duty personnel", "Work systems able to change duty/rest schedules",
               "Cochrane evidence is low or very low certainty for most schedule adaptations and differs by roster.",
               ["ORGANIZATIONAL_OR_POLICY_PROCESS"], [], ["RDS-0003", "RDS-0004"], lifecycle="RESEARCH_NEEDED", scale="INSTITUTIONAL_FIELD",
               implementers=["Organization or scheduling authority"], prerequisites=["Operational coverage and enforceable rest protection"],
               risks=["Compression elsewhere in the roster can offset benefits"]),
        effect(3, "INT-CAND-BIO-F01-003", "BIO-001", "CHANGE_LEVEL", "INCREASE",
               "Later mandatory start time permits later wake time and, on average, longer school-night sleep.",
               "Middle- and high-school students", "Schools changing mandatory morning start time",
               "Most evidence is quasi-experimental; transport, extracurricular, employment, and family schedules can attenuate effects.",
               ["ORGANIZATIONAL_OR_POLICY_PROCESS"], [], ["RDS-0003", "RDS-0004", "BIO-006"], scale="INSTITUTIONAL_FIELD",
               implementers=["School or education authority"], prerequisites=["Coordinated transport and activity schedules"]),
        effect(4, "INT-CAND-BIO-F01-006", "BIO-002", "CHANGE_LEVEL", "INCREASE",
               "Stimulus control and titrated time-in-bed consolidate sleep and reduce wake after sleep onset in chronic insomnia.",
               "Adults with chronic insomnia disorder", "Clinical or validated digital CBT-I delivery",
               "Subjective improvements are more consistent than objective polysomnography/actigraphy changes; initial sleep restriction can cause sleepiness.",
               ["HUMAN_DELIVERED", "DIGITAL_OR_AUTOMATED"], [], [], implementers=["Trained clinician or validated program"],
               prerequisites=["Insomnia assessment and safety screening"], risks=["Transient sleepiness during sleep-restriction component"],
               unintended=["Total sleep time may initially decrease"]),
        effect(5, "INT-CAND-BIO-F01-007", "BIO-004", "CHANGE_LEVEL", "CONTEXT_DEPENDENT",
               "Light resets the circadian pacemaker; timing on the phase-response curve determines advance versus delay.",
               "Adults requiring a governed circadian phase shift", "Controlled light exposure with phase and timing assessment",
               "Wrong timing can shift phase in the undesired direction; ocular/psychiatric risks and medication photosensitivity require screening.",
               ["PHYSICAL_ENVIRONMENT", "HUMAN_DELIVERED"], [], ["BIO-003"],
               implementers=["Clinician, occupational program, or trained individual"], prerequisites=["Phase/timing assessment"],
               risks=["Unwanted phase shift", "Eye discomfort", "Mood activation in susceptible individuals"]),
        effect(6, "INT-CAND-BIO-F01-008", "BIO-004", "CHANGE_LEVEL", "CONTEXT_DEPENDENT",
               "Exogenous melatonin shifts circadian phase according to administration timing and can also promote sleep.",
               "People with delayed or otherwise mistimed circadian phase", "Clinically supervised or protocol-governed timed dosing",
               "Dose, formulation, timing, product quality, age, comorbidity, and concurrent medicines affect benefit and risk.",
               ["HUMAN_DELIVERED"], [], ["BIO-003"], implementers=["Clinician or protocol-trained individual"],
               prerequisites=["Medication and timing review"], risks=["Daytime sleepiness", "Drug interactions", "Product-quality variation"]),
        effect(7, "INT-CAND-BIO-F01-011", "BIO-002", "CHANGE_LEVEL", "INCREASE",
               "Receiver-level personal protection may reduce sound reaching the sleeper and thereby reduce noise-triggered arousals and awakenings.",
               "Noise-exposed sleepers", "Nighttime environmental or care-setting noise",
               "Identity and evidence are receiver-specific; do not generalize to source or transmission controls. Evidence is strongest in ICU settings, intervention components and objective outcomes vary, and alarm audibility is safety-critical.",
               ["PHYSICAL_ENVIRONMENT"], [], [], lifecycle="RESEARCH_NEEDED", scale="PHYSICAL_SETTING",
               implementers=["Facility, household, or individual"], risks=["Missed alarms or warning signals", "Discomfort"]),
        effect(8, "INT-CAND-BIO-F01-010", "BIO-005", "CHANGE_LEVEL", "DECREASE",
               "Pre-awakening caffeine antagonizes adenosine receptors near waking and may accelerate restoration of alert performance.",
               "Sleep-restricted healthy adults with planned awakening", "Controlled planned awakening where delayed-release timing is feasible",
               "Evidence includes a small crossover trial; carryover can impair subsequent sleep and the formulation is not a generic recommendation.",
               ["HUMAN_DELIVERED"], [], [], lifecycle="RESEARCH_NEEDED",
               prerequisites=["Known awakening time and caffeine safety screening"], risks=["Subsequent sleep disruption", "Cardiovascular or anxiety effects"]),
        effect(9, "INT-CAND-BIO-F01-007", "BIO-005", "CHANGE_LEVEL", "DECREASE",
               "Post-awakening bright light may increase subjective alertness during sleep inertia, but objective performance effects are not established.",
               "Adults awakening for immediate activity", "Post-awakening setting with safe light delivery",
               "The reactive-countermeasure literature is small and mixed; subjective alertness must not be substituted for performance.",
               ["PHYSICAL_ENVIRONMENT"], [], [], lifecycle="RESEARCH_NEEDED",
               risks=["Glare", "Unwanted circadian phase shift if repeatedly mistimed"]),
    ]

    effect_rationales = [
        (1, "BIOF01-EXT-017 synthesizes behavioral sleep-extension studies and finds increased duration with substantial heterogeneity.", "MODERATE", "MODERATE", "SUPPORTS", "SYNTHESIS", "Systematic review/meta-analysis of sleep extension", ["High heterogeneity", "Intervention descriptions were often incomplete"]),
        (2, "BIOF01-EXT-019 and related workplace reviews find uncertain, roster-specific effects of schedule adaptation.", "MIXED", "LOW", "MIXED", "SYNTHESIS", "Cochrane systematic review", ["Low/very-low certainty for most comparisons", "Complex multicomponent schedules"]),
        (3, "BIOF01-EXT-018 and later meta-analyses report longer sleep after delayed school starts, mainly from natural experiments.", "MODERATE", "MODERATE", "SUPPORTS", "SYNTHESIS", "Systematic review/meta-analysis", ["Predominantly nonrandomized designs", "Adolescent context only"]),
        (4, "BIOF01-EXT-015/016 and component network meta-analysis show improved subjective continuity, with less consistent objective change.", "STRONG", "HIGH", "SUPPORTS", "SYNTHESIS", "Meta-analyses of randomized trials", ["Objective and subjective sleep measures diverge", "Package components and delivery vary"]),
        (5, "BIOF01-EXT-011/013 provide experimental phase-resetting evidence and a clinical systematic review; direction depends on timing.", "MODERATE", "MODERATE", "SUPPORTS", "EXPERIMENTAL", "Controlled light-exposure studies and systematic review", ["Small studies", "Protocols differ in intensity, spectrum, duration, and timing"]),
        (6, "BIOF01-EXT-012/024 support timed melatonin for phase advance in delayed sleep-wake phase disorder; sleep-promoting and phase-shifting effects can differ.", "MODERATE", "MODERATE", "SUPPORTS", "SYNTHESIS", "Meta-analysis and randomized clinical trial", ["Population-specific", "Timing and formulation are critical"]),
        (7, "BIOF01-EXT-001/002/020 support reduced arousals or improved sleep when sound exposure is attenuated, with strongest intervention evidence in ICUs.", "MODERATE", "MODERATE", "SUPPORTS", "SYNTHESIS", "Systematic reviews/meta-analyses and randomized ICU trials", ["Context-specific", "Subjective outcomes predominate in some reviews"]),
        (8, "BIOF01-EXT-008/009 find caffeine the most plausible countermeasure but the direct evidence base is small and formulation-specific.", "LIMITED", "LOW", "SUPPORTS", "EXPERIMENTAL", "Small placebo-controlled crossover trial plus structured review", ["Small healthy-adult sample", "Novel formulation", "Carryover risk"]),
        (9, "BIOF01-EXT-008 reports promising subjective-alertness effects but no convincing evidence of objective performance benefit.", "LIMITED", "LOW", "INSUFFICIENT", "SYNTHESIS", "Structured review", ["Few studies", "Subjective/objective outcome divergence"]),
    ]
    effect_evidence = []
    for number, rationale, strength, confidence, disposition, design, specification, limitations in effect_rationales:
        lifecycle = effects[number - 1]["governance"]["lifecycleStatus"]
        effect_evidence.append(evidence(
            f"EVA-CAND-BIO-F01-IE-{number:03d}", f"IE-CAND-BIO-F01-{number:03d}",
            "INTERVENTION_EFFECT", lifecycle, [], rationale, strength, confidence,
            disposition, [(design, specification)], limitations,
            ["No quantitative estimate is promoted because protocols and outcomes are not harmonized."],
        ))

    return {
        "schemaVersion": "1.0.0",
        "workspaceStatus": "NON_GOVERNED_CANDIDATE_WORKSPACE",
        "productionGraphEligible": False,
        "relationships": relationships,
        "evidenceAssessments": rel_evidence + effect_evidence,
        "causalPathways": [],
        "interventions": interventions,
        "interventionEffects": effects,
    }


def build_manifest(workspace: dict) -> dict:
    entities = _read("data/entities.json")
    families = _read("data/families.json")["families"]
    relationships = _read("data/relationships.json")["relationships"]
    family = next(row for row in families if row["id"] == "BIO-F01")
    members = [row for row in entities if row.get("primaryFamilyId") == "BIO-F01"]
    member_ids = {row["id"] for row in members}
    incident = [
        row for row in relationships
        if row.get("subjectEntityId") in member_ids or row.get("objectEntityId") in member_ids
    ]
    lifecycle_counts: dict[str, int] = {}
    blocked = 0
    for key in ("relationships", "evidenceAssessments", "causalPathways", "interventions", "interventionEffects"):
        for row in workspace[key]:
            status = row["governance"]["lifecycleStatus"]
            lifecycle_counts[status] = lifecycle_counts.get(status, 0) + 1
            blocked += row["governance"]["blockStatus"] == "NEEDS_GOVERNANCE_INPUT"
    rds = [row for row in members if row["entityType"] == "RELATIONAL_DERIVED_STATE"]
    return {
        "schemaVersion": "1.0.0",
        "auditId": AUDIT_ID,
        "auditType": "GOVERNED_FAMILY_PILOT_CANDIDATES_ONLY",
        "family": {"id": family["id"], "name": family["name"], "layer": family["layer"]},
        "status": "AWAITING_HUMAN_SCIENTIFIC_GOVERNANCE",
        "productionGraphEligible": False,
        "baseline": {
            "commit": BASELINE,
            "entityContracts": ["DRIVER_SCHEMA_V1_1", "RELATIONAL_DERIVED_STATE_SCHEMA_V0_1"],
            "relationshipSchema": "RELATIONSHIP_V1_1.0.0",
            "interventionSchema": "INTERVENTION_V1_1.0.0",
            "sourceRegister": {"schemaVersion": _read("data/sources.json")["schemaVersion"], "recordCount": len(_read("data/sources.json")["sources"]), "canonicalLfSha256": _canonical_lf_sha256("data/sources.json")},
            "entityDatasetCanonicalLfSha256": _canonical_lf_sha256("data/entities.json"),
            "relationshipDatasetCanonicalLfSha256": _canonical_lf_sha256("data/relationships.json"),
        },
        "membership": {
            "driverIds": [row["id"] for row in members if row["entityType"] == "DRIVER"],
            "rdsIds": [row["id"] for row in rds],
            "driverCount": sum(row["entityType"] == "DRIVER" for row in members),
            "rdsCount": len(rds),
            "total": len(members),
        },
        "rdsDerivations": [{
            "entityId": row["id"],
            "derivationSchemaVersion": "0.1",
            "derivationBaselineCommit": BASELINE,
            "derivationType": row.get("derivationType"),
            "inputEntityIds": [spec["entityId"] for spec in row.get("constituentSpecifications", []) if spec.get("entityId")],
            "externalParameterTypes": [spec["externalParameterType"] for spec in row.get("constituentSpecifications", []) if spec.get("externalParameterType")],
        } for row in rds],
        "incidentRelationshipIds": [row["id"] for row in incident],
        "incidentRelationshipCounts": {
            "total": len(incident),
            "causal": sum(row["relationFamily"] == "CAUSAL" for row in incident),
            "derivational": sum(row["relationFamily"] == "DERIVATIONAL" for row in incident),
        },
        "existingRelationshipAudit": {
            "RETAIN_AS_IS": ["REL-RDS-0016", "REL-RDS-0017", "REL-RDS-0018", "REL-RDS-0019", "REL-RDS-0020"],
            "RETAIN_BUT_V1_INCOMPLETE": ["REL-BIO-002"],
            "REVISION_CANDIDATE": ["REL-BIO-001", "REL-BIO-003", "REL-BIO-009", "REL-BIO-021", "REL-ENV-040"],
            "RETYPE_CANDIDATE": [],
            "SPLIT_CANDIDATE": [],
            "MERGE_OR_DUPLICATE_CANDIDATE": [],
            "DEPRECATION_CANDIDATE": [],
            "RESEARCH_NEEDED": [],
            "BLOCKED": [],
        },
        "relationshipResearch": {
            "hypothesesTriaged": 20,
            "causalCandidates": 5,
            "associationCandidates": 2,
            "temporalCandidates": 0,
            "moderationCandidates": 1,
            "pathwayCandidates": 0,
            "otherNoncausalCandidates": 1,
            "rejected": 5,
            "researchNeeded": 9,
            "blocked": 0,
        },
        "candidateCounts": {key: len(workspace[key]) for key in ("relationships", "evidenceAssessments", "causalPathways", "interventions", "interventionEffects")},
        "candidateLifecycleCounts": lifecycle_counts,
        "governanceBlockedCount": blocked,
        "interventionResearch": {
            "driversSearched": 6,
            "interventionIdentities": len(workspace["interventions"]),
            "interventionEffects": len(workspace["interventionEffects"]),
            "deliveryModalitiesRepresented": ["HUMAN_DELIVERED", "DIGITAL_OR_AUTOMATED", "ORGANIZATIONAL_OR_POLICY_PROCESS", "PHYSICAL_ENVIRONMENT"],
            "driversWithNoSupportedDirectIntervention": ["BIO-073", "BIO-074"],
            "rdsDirectTargetViolations": 0,
            "distinctRdsOutcomeIds": ["BIO-003", "BIO-006", "RDS-0003", "RDS-0004"],
            "rdsOutcomeReferenceCount": 9,
        },
        "evidenceSummary": {
            "governedSourcesReviewed": 16,
            "supplementalSourcesReviewed": 25,
            "distinctSourcesReviewed": 41,
            "supplementalSourceLog": "BIO_F01_RESEARCH_LOG.md",
            "supplementalSourceRegistrationStatus": "NON_GOVERNED_AUDIT_REFERENCES",
            "evidenceAssessments": len(workspace["evidenceAssessments"]),
            "assessmentsWithCanonicalSourceIds": sum(bool(row["sourceIds"]) for row in workspace["evidenceAssessments"]),
            "assessmentsPendingCanonicalSourceRegistration": sum(not row["sourceIds"] for row in workspace["evidenceAssessments"]),
        },
        "newGovernedRecords": 0,
        "newActiveRecords": 0,
        "canonicalIntegrity": {"drivers": 770, "rds": 41, "entities": 811, "activeRelationships": 450, "activeCausalRelationships": 431},
        "researchMethod": "Structured evidence search/audit; not a formal systematic review",
        "researchDate": "2026-09-05",
        "documents": [
            "BIO_F01_BASELINE.md",
            "BIO_F01_EXISTING_RELATIONSHIP_AUDIT.md",
            "BIO_F01_RELATIONSHIP_CANDIDATES.md",
            "BIO_F01_INTERVENTION_CANDIDATES.md",
            "BIO_F01_EVIDENCE_SUMMARY.md",
            "BIO_F01_COMPLETENESS_REPORT.md",
            "BIO_F01_GOVERNANCE_DECISION_PACKAGE.md",
            "BIO_F01_RESEARCH_LOG.md",
        ],
        "openItems": [
            "Register supplemental pilot sources canonically only after source-governance review.",
            "Resolve endpoint alignment for the proposed circadian-phase moderation of REL-BIO-002.",
            "Determine whether continuity-specific evidence justifies BIO-002 to BIO-028 causality.",
            "No CausalPathway met pathway-specific evidence requirements in this pilot pass.",
        ],
    }


def main() -> None:
    workspace = build_workspace()
    PILOT_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE.write_text(json.dumps(workspace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(build_manifest(workspace), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {WORKSPACE.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
