"""Build the complete candidate-only Cultural Layer V2 package."""

from __future__ import annotations

from collections import Counter, defaultdict

from cultural_layer_v2 import DATA, DOCS, PROGRAM_ID, read, write, write_doc, validate_protection

S = lambda n: f"SRC-CAND-CUL-LAYER-{n:03d}"
PREFIX = "**ADVISORY — HUMAN DECISION REQUIRED. New GOVERNED = 0 and ACTIVE = 0.**\n\n"

SOURCES = [
    ("8656339", "10.1037//0022-3514.70.5.945", 'Insult, aggression, and the southern culture of honor: an "experimental ethnography".', 1996),
    ("15631579", "10.1037/0022-3514.88.1.121", "Ethnic group identification and group evaluation among minority and majority groups: testing the multiculturalism hypothesis.", 2005),
    ("16004647", "10.1348/014466604X23482", "Immigration discourses and their impact on multiculturalism: a discursive and experimental study.", 2005),
    ("17100480", "10.1037/0021-9010.91.6.1225", "On the nature and importance of cultural tightness-looseness.", 2006),
    ("21617077", "10.1126/science.1197754", "Differences between tight and loose cultures: a 33-nation study.", 2011),
    ("32605518", "10.1098/rspb.2020.1036", "A global analysis of cultural tightness in non-industrial societies.", 2020),
    ("38000175", "10.1016/j.socscimed.2023.116431", "Cultural tightness-looseness and normative social influence in eight Asian countries: Associations of individual and collective norms with vaccination intentions.", 2024),
    ("42423728", "10.1037/pspi0000524", "Tightening up under threat: Social class shapes the strength of norms.", 2026),
    ("29317675", "10.1038/s41598-017-18023-4", "Synchrony and Physiological Arousal Increase Cohesion and Cooperation in Large Naturalistic Groups.", 2018),
    ("27540276", "10.1016/j.evolhumbehav.2016.02.004", "Silent disco: dancing in synchrony leads to elevated pain thresholds and social closeness.", 2016),
    ("39653120", "10.1016/j.bbr.2024.115369", "Multimodal interpersonal synchrony: Systematic review and meta-analysis.", 2025),
    ("18469303", "10.1177/1088868308316892", "Narrative and the cultural psychology of identity.", 2008),
    ("36167445", "10.1016/bs.pbr.2022.07.004", "Neural, psychological, and social foundations of collective memory: Implications for common mnemonic processes, agency, and identity.", 2022),
    ("25078868", "10.1007/s11873-014-0258-7", "Collective Memory, A Fusion of cognitive Mechanisms and cultural Processes.", 2015),
    ("31358645", "10.1073/pnas.1820146116", "Parochialism, social norms, and discrimination against immigrants.", 2019),
]

LANDSCAPES = {
    "CUL-F01": ("Shared value prominence is a cultural aggregate, not an individual's value score.", "Transmission, selection and institutions can stabilize shared priorities.", "Value framing or salience manipulations measure individual responses, not immediate cultural change.", "Aggregation, measurement invariance and referent specification are required.", "Cross-national mean differences do not identify causal value effects.", [4, 5]),
    "CUL-F02": ("Autonomous, interdependent, relational and collective selfhood models differ from individual self-construal.", "Socialization and institutions may sustain agency norms over time.", "Priming an individual self-description does not manipulate population prevalence.", "Level and referent must be explicit.", "State primes cannot establish durable shared models.", [4]),
    "CUL-F03": ("Tightness, deviance tolerance, entrenchment, scope and content-specific norms are distinct.", "Sanctioning and coordination can stabilize norms under threat.", "Threat or constraint primes are not equivalent to a culture-level tightness intervention.", "Multi-level surveys and behavioral sanctions measure different components.", "Country association, individual perception and shared norm must not be collapsed.", [4, 5, 6, 7, 8]),
    "CUL-F04": ("Honor, face, dignity, hierarchy, prestige and reputation-defense obligations are related but non-identical.", "Norms can condition reputation-relevant responses.", "Insult experiments expose a person to provocation; they do not manipulate culture-level honor strength.", "Regional comparison and physiological/aggressive responses require level separation.", "Selection, gender and regional transfer limit causal inference.", [1]),
    "CUL-F05": ("Kinship, filial, lineage, family, hospitality and resource-sharing obligations require a specified referent.", "Socialization and sanctioning may transmit obligations.", "No single family vignette changes a shared cultural obligation.", "Individual endorsement differs from community prevalence.", "Household and society levels cannot be inferred from one another.", [4]),
    "CUL-F06": ("Conformist, prestige, success, elder and vertical transmission are mechanisms, not observed outcomes alone.", "Learning biases can affect diffusion conditional on networks and payoffs.", "Model exposure packages often vary source status and content together.", "Transmission fidelity requires repeated measures and content identity.", "Laboratory copying is not population-level cultural persistence.", [4]),
    "CUL-F07": ("Collective memory, narrative centrality, schema consensus and symbolic meaning span individual and collective levels.", "Narratives can organize identity and recall through repeated social practice.", "Narrative exposure is not collective-memory change without shared uptake.", "Recall, narrative endorsement and archival prevalence are distinct.", "Reviews are theoretical context, not experimental evidence of a specific edge.", [12, 13, 14]),
    "CUL-F08": ("Ritual expectation, significance, cost, synchronization and custom entrenchment are distinct.", "Coordinated action can affect individual cohesion while ritual institutions persist at group level.", "Synchrony, exertion, music and arousal are often bundled.", "Behavioral synchrony does not itself measure a cultural synchronization norm.", "Social closeness/cooperation findings do not establish cultural Driver change.", [9, 10, 11]),
    "CUL-F09": ("Sacred commitment, taboo, purity, moralization, boundary rigidity and violence legitimacy are distinct.", "Moralization and sanctions may protect symbolic boundaries.", "Sacred-value elicitation is measurement, not a direct culture-level manipulation.", "Individual conviction differs from shared prevalence.", "No universal pathway from sacredness to violence is inferred.", [4]),
    "CUL-F10": ("Ideal affect, expression legitimacy, display rules, restraint and shame regulation differ.", "Social learning and anticipated sanctions shape expression.", "Emotion induction does not manipulate the display rule itself.", "Reported emotion, expression and perceived norm require separate measures.", "State emotion cannot stand for cultural convention.", [4]),
    "CUL-F11": ("Attention, dialectical reasoning, causal explanation, epistemic authority, future orientation and fatalism differ.", "Institutions and learned conventions may shape knowledge practices.", "Task performance is not prevalence of a cultural convention.", "Cross-language task differences require invariance and exposure controls.", "Cognitive style and culture-level convention remain separate.", [4]),
    "CUL-F12": ("Directness, explicitness, politeness, honorifics, euphemism and silence norms are separate message conventions.", "Audience design and sanctions condition communication choices.", "Wording manipulation changes a message, not necessarily a cultural convention.", "Message feature, speaker behavior and shared norm must be separated.", "Prior Informational review is reused for euphemism-to-metaphor scope.", [4]),
    "CUL-F13": ("Identity narrative, prototype, boundary, assimilation, accommodation, heritage, reconciliation and generational distance differ.", "Institutions and discourse can shape individual endorsement over time, but shared norms require aggregation.", "Multiculturalism framing can shift individual evaluation; it does not directly establish culture-level accommodation norm strength.", "Individual attitude, group identification and collective prevalence require distinct measures.", "Generational distance needs a versioned profile and distance metric before causal-source use.", [2, 3, 15]),
}

RETYPE = {"REL-CUL-001", "REL-CUL-009", "REL-CUL-027", "REL-CUL-035", "REL-CUL-040"}
RETAIN = {"REL-CUL-008", "REL-CUL-010", "REL-CUL-012", "REL-CUL-016", "REL-CUL-021", "REL-CUL-024", "REL-CUL-026"}
RETYPE_REASONS = {
    "REL-CUL-001": "Tightness and deviance tolerance are partly inverse definitional/measurement dimensions; causal type needs review.",
    "REL-CUL-009": "Kinship and family obligation have nested referents and may be compositional rather than causal.",
    "REL-CUL-027": "Display-rule strength and restraint norm may overlap at definition and measurement rather than form an identified causal edge.",
    "REL-CUL-035": "Communication directness and explicitness overlap but are not interchangeable; causal versus semantic relation needs review.",
    "REL-CUL-040": "Assimilation expectation and accommodation norm are conceptually opposed policy/norm dimensions; a universal negative causal edge is not identified.",
}


def sf(i, source, claim, design, population, exposure, target, result, disposition, limits, overlap=None):
    return {"id": f"SF-CUL-LAYER-{i:03d}", "sourceId": S(source), "claimId": claim,
            "locator": "PubMed abstract; source identity independently verified through NCBI Eutilities",
            "accessDepth": "PUBMED_ABSTRACT", "design": design, "population": population,
            "exposure": exposure, "target": target, "result": result, "disposition": disposition,
            "limitations": limits, "datasetGroup": f"PMID_{SOURCES[source-1][0]}", "reviewOverlap": overlap or []}


def render(name: str, body: str) -> None:
    write_doc(DOCS / f"CULTURAL_LAYER_{name}.md", f"# Cultural Layer {name.replace('_', ' ').lower()}\n\n{PREFIX}{body}")


def build() -> None:
    validate_protection()
    base = read(DATA / "baseline.json")
    entities = {x["frozenRecord"]["id"]: {**x["frozenRecord"], "familyId": x["mechanical"]["familyId"]} for x in base["entities"]}
    sources = {S(i): {"id": S(i), "pmid": pmid, "doi": doi.lower(), "title": title, "year": year,
                 "accessDepth": "PUBMED_ABSTRACT", "verificationRoute": "NCBI_EUTILITIES_PUBMED_ESUMMARY",
                 "canonicalExactMatch": None, "registrationStatus": "CANDIDATE_ONLY_UNREGISTERED"}
               for i, (pmid, doi, title, year) in enumerate(SOURCES, 1)}
    write(DATA / "candidate-source-registry.json", sources)
    landscapes = {fid: {"constructs": v[0], "mechanisms": v[1], "operations": v[2], "measurement": v[3],
                         "boundaries": v[4], "sourceIds": [S(n) for n in v[5]], "researchDepth": "FAMILY_LANDSCAPE_ONLY"}
                  for fid, v in LANDSCAPES.items()}
    write(DATA / "family-landscapes.json", {"schemaVersion": "1.0.0", "programId": PROGRAM_ID,
          "method": "Bounded Family landscape; source identities checked via PubMed. Not a systematic review per Driver.", "families": landscapes})

    psy = read(DATA.parent / "PSYCHOLOGICAL_LAYER/relationship-review-registry.json")
    inf = read(DATA.parent / "INFORMATIONAL_LAYER/relationship-review-registry.json")
    reviews = {}
    for row in base["incidentRelationships"]:
        rid, e = row["id"], row["edge"]
        prior = None
        if rid in psy:
            p = psy[rid]
            disposition = p["primaryDisposition"]
            reason = "Prior Psychological review reused: " + p["review"]["rationale"]
            prior = "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260917-001"
        elif rid in inf:
            p = inf[rid]
            disposition, reason = p["disposition"], "Prior Informational review reused: " + p["rationale"]
            prior = "AUD-INFORMATIONAL-LAYER-AE-V1-20260919-001"
        elif rid in RETYPE:
            disposition, reason = "RETYPE_CANDIDATE", RETYPE_REASONS[rid]
        elif rid in RETAIN:
            disposition, reason = "RETAIN_V1_INCOMPLETE", "Plausible bounded cultural mechanism; retain current proposition while exact exposure, aggregation, timing and evidence metadata remain V1-incomplete."
        else:
            disposition, reason = "RESEARCH_NEEDED", "Culture-level causal direction is not identified at the exact endpoints; shared prevalence, individual endorsement, selection, reciprocal reinforcement and aggregation remain unresolved."
        reviews[rid] = {"id": rid, "ownerFamilyId": row["ownerFamilyId"], "consultedFamilyIds": row["consultedFamilyIds"],
            "scope": row["scope"], "semanticType": e["semanticType"], "sourceId": e["source"], "targetId": e["target"],
            "disposition": disposition, "rationale": reason, "priorDecisionOrReview": prior,
            "v1IncompleteFields": row["v1IncompleteFields"], "productionChangeAuthorized": False}
    assert len(reviews) == 55
    write(DATA / "relationship-review-registry.json", reviews)

    by_entity = defaultdict(list)
    for row in base["incidentRelationships"]:
        for eid in (row["edge"]["source"], row["edge"]["target"]):
            if eid in entities: by_entity[eid].append(row["id"])
    deep_targets = {"CUL-017", "CUL-040", "CUL-065", "CUL-086"}
    coverage = {}
    for eid, ent in sorted(entities.items()):
        rds = ent["entityType"] != "DRIVER"
        sufficient = any(reviews[r]["disposition"] in {"RETAIN_AS_IS", "RETAIN_V1_INCOMPLETE"} for r in by_entity[eid])
        coverage[eid] = {"id": eid, "familyId": ent["familyId"], "entityType": ent["entityType"],
            "relationshipStatus": "BLOCKED" if rds else "EXISTING_PROPOSITION_SUFFICIENT" if sufficient else "INSUFFICIENT_PRELIMINARY_SIGNAL",
            "actionsEventsStatus": "NOT_APPLICABLE" if rds else "CANDIDATE_RESEARCHED" if eid in deep_targets else "INSUFFICIENT_PRELIMINARY_SIGNAL",
            "incidentCausalRelationshipIds": sorted(by_entity[eid]), "landscapeSourceIds": landscapes[ent["familyId"]]["sourceIds"],
            "reason": "Direct EffectAssertion target prohibited; causal-source semantics reviewed separately." if rds else
                      "Exact A&E route received proposition-level research and remained research-needed." if eid in deep_targets else
                      "Family landscape found no exact operation-to-Driver claim strong enough for deep research; this is not a null finding."}
    write(DATA / "negative-coverage-registry.json", coverage)

    rds = [{"id": "CUL-088", "familyId": "CUL-F13", "definition": entities["CUL-088"]["definition"],
            "derivationType": entities["CUL-088"].get("derivationType"), "declaredInputs": entities["CUL-088"].get("constituentSpecifications"),
            "derivationLogic": entities["CUL-088"].get("derivationLogic"), "units": "MULTIPLE_ALLOWED_SCALES_NO_SELECTED_VERSION",
            "measurementWindow": "REQUIRED_BUT_NOT_SELECTED", "reference": "ADJACENT_GENERATION_PROFILES_NOT_VERSIONED",
            "aggregation": "PROFILE_VARIABLES_AND_DISTANCE_METRIC_NOT_SELECTED", "externalInputs": ["GENERATION_A_CULTURAL_PROFILE", "GENERATION_B_CULTURAL_PROFILE"],
            "incomingCausalIds": [], "outgoingCausalIds": ["REL-CUL-042"], "d10Disposition": "HEIGHTENED_BLOCKED_CAUSAL_SOURCE_REVIEW",
            "doubleCountRisk": "PROFILE_CONSTITUENTS_AND_DISTANCE_MAY_BOTH_ENTER_MODEL", "directEffectTargetAllowed": False, "productionChanged": False}]
    write(DATA / "rds-review.json", rds)

    triage_spec = [
      ("CUL-F01", "An individual value-scale score is a shared cultural value", "REJECT_CATEGORY_ERROR", [4]),
      ("CUL-F02", "A temporary self-construal prime changes shared selfhood prevalence", "REJECT_CATEGORY_ERROR", [4]),
      ("CUL-F03", "A threat prime increases culture-level tightness", "DEEP_RESEARCHED_RESEARCH_NEEDED", [4,5,6,7,8]),
      ("CUL-F04", "Insulting a participant increases cultural honor norm strength", "DEEP_RESEARCHED_RESEARCH_NEEDED", [1]),
      ("CUL-F05", "Family obligation endorsement proves a community obligation", "REJECT_CATEGORY_ERROR", [4]),
      ("CUL-F06", "Laboratory model copying establishes durable transmission prevalence", "INSUFFICIENT_PRELIMINARY_SIGNAL", [4]),
      ("CUL-F07", "Narrative exposure changes collective memory salience", "INSUFFICIENT_PRELIMINARY_SIGNAL", [12,13,14]),
      ("CUL-F08", "Synchronous movement increases cultural ritual-synchronization degree", "DEEP_RESEARCHED_RESEARCH_NEEDED", [9,10,11]),
      ("CUL-F09", "Individual sacred-value endorsement is shared sacred commitment prevalence", "REJECT_CATEGORY_ERROR", [4]),
      ("CUL-F10", "Induced anger changes anger-expression legitimacy", "REJECT_CATEGORY_ERROR", [4]),
      ("CUL-F11", "Task performance is prevalence of a cultural reasoning convention", "REJECT_CATEGORY_ERROR", [4]),
      ("CUL-F12", "A direct wording treatment changes communication-directness convention", "INSUFFICIENT_PRELIMINARY_SIGNAL", [4]),
      ("CUL-F13", "Multiculturalism framing increases cultural accommodation norm strength", "DEEP_RESEARCHED_RESEARCH_NEEDED", [2,3,15]),
    ]
    triage = [{"id": f"HYP-CUL-LAYER-{i:03d}", "familyId": f, "proposition": p, "semanticType": "CAUSAL",
               "outcome": o, "reason": "Construct level or causal contrast does not support the broad proposition." if o == "REJECT_CATEGORY_ERROR" else
                                      "Preliminary signal did not isolate an exact culture-level causal endpoint." if o == "INSUFFICIENT_PRELIMINARY_SIGNAL" else
                                      "Deep evidence retained a consequential boundary but not a governance-ready culture-level effect.",
               "sourceIds": [S(n) for n in nums]} for i,(f,p,o,nums) in enumerate(triage_spec,1)]
    write(DATA / "triage-hypotheses.json", triage)
    deep = [
      {"id":"DEEP-CUL-001","familyId":"CUL-F03","hypothesisId":"HYP-CUL-LAYER-003","question":"Threat/constraint context to culture-level tightness","sourceIds":[S(n) for n in (4,5,6,7,8)],"outcome":"RESEARCH_NEEDED","stopReason":"Cross-national and individual-level studies do not identify a portable intervention on aggregate cultural tightness."},
      {"id":"DEEP-CUL-002","familyId":"CUL-F04","hypothesisId":"HYP-CUL-LAYER-004","question":"Honor-relevant insult to reputation-defense obligation strength","sourceIds":[S(1)],"outcome":"RESEARCH_NEEDED","stopReason":"Insult is randomized, region/cultural norm is not; measured reactions are individual outcomes rather than shared obligation."},
      {"id":"DEEP-CUL-003","familyId":"CUL-F08","hypothesisId":"HYP-CUL-LAYER-008","question":"Synchronous movement to ritual synchronization degree","sourceIds":[S(n) for n in (9,10,11)],"outcome":"RESEARCH_NEEDED","stopReason":"Manipulations bundle synchrony, arousal, music or exertion and measure social outcomes, not the cultural Driver."},
      {"id":"DEEP-CUL-004","familyId":"CUL-F13","hypothesisId":"HYP-CUL-LAYER-013","question":"Multiculturalism discourse to accommodation norm strength","sourceIds":[S(n) for n in (2,3,15)],"outcome":"RESEARCH_NEEDED","stopReason":"Experiments measure individual evaluation/endorsement; no shared culture-level norm change or stable aggregation is identified."},
    ]
    write(DATA / "deep-research-ledger.json", deep)
    findings = [
      sf(1,5,"HYP-CUL-LAYER-003","33-nation multilevel observational study","Participants across 33 nations","Observed national tightness and ecological/institutional correlates","Cultural tightness and individual outcomes","Substantial cross-national differences and multi-level associations.","MIXED_ASSOCIATIONAL","No randomized culture-level exposure; national aggregate and individual perceptions differ."),
      sf(2,8,"HYP-CUL-LAYER-003","Multi-study observational and experimental program","Adults across social-class contexts","Threat/context manipulation in a bounded study","Norm strength or tightness-related response","Threat-related effects vary by social class and study context.","MIXED_BOUNDED","A bounded individual/context experiment does not materialize an enduring aggregate Cultural Driver."),
      sf(3,1,"HYP-CUL-LAYER-004","Three laboratory experiments with regional comparison","White male US college participants from South and North","Standardized insult","Physiological, cognitive and aggressive reputation-relevant responses","Southern participants showed stronger selected insult responses.","SUPPORTS_MODERATION_NOT_DRIVER_CHANGE","Region/upbringing was not randomized; male student sample; outcomes are responses, not shared honor norm strength."),
      sf(4,9,"HYP-CUL-LAYER-008","Naturalistic group experiment","Large groups performing coordinated movement","Synchrony and arousal manipulation","Cohesion and cooperation","Synchrony combined with arousal increased selected cohesion/cooperation outcomes.","MIXED_BUNDLED","Arousal interaction and social outcomes do not isolate cultural ritual synchronization."),
      sf(5,10,"HYP-CUL-LAYER-008","Dance synchrony experiment","Adult dance participants","Synchronous versus asynchronous dance conditions","Pain threshold, social closeness and cooperation","Synchrony increased closeness and pain threshold but did not increase cooperation.","MIXED_WITH_NULL","Different outcome directions and exercise/music context; no cultural Driver endpoint."),
      sf(6,11,"HYP-CUL-LAYER-008","Systematic review and meta-analysis","Multimodal interpersonal synchrony studies","Heterogeneous synchrony modalities","Multiple interpersonal outcomes","Synthesis reports heterogeneous modalities and outcomes.","MIXED_SYNTHESIS","Includes diverse manipulations and may include relevant primary paradigms; not independent exact replication.",[S(9),S(10)]),
      sf(7,2,"HYP-CUL-LAYER-013","Four correlational and experimental studies","Dutch majority and Turkish-Dutch minority participants","Multiculturalism endorsement or framing","Group identification and evaluation","Results support bounded relationships among multiculturalism, identification and evaluation.","SUPPORTS_INDIVIDUAL_LEVEL","Individual endorsement/evaluation is not community accommodation norm strength."),
      sf(8,3,"HYP-CUL-LAYER-013","Discursive and experimental study","Participants exposed to immigration discourse","Multiculturalism/assimilation discourse","Individual multiculturalism attitudes","Discourse condition changed individual evaluations in the bounded study.","SUPPORTS_INDIVIDUAL_LEVEL","Message package and individual attitude endpoint do not establish durable culture-level norm change."),
    ]
    write(DATA / "source-findings.json", findings)
    ae = [
      {"id":"HYP-CUL-LAYER-AE-001","originFamilyId":"CUL-F03","targetKind":"DRIVER","targetId":"CUL-017","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":["SF-CUL-LAYER-001","SF-CUL-LAYER-002"],"reason":deep[0]["stopReason"]},
      {"id":"HYP-CUL-LAYER-AE-002","originFamilyId":"CUL-F04","targetKind":"DRIVER","targetId":"CUL-065","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":["SF-CUL-LAYER-003"],"reason":deep[1]["stopReason"]},
      {"id":"HYP-CUL-LAYER-AE-003","originFamilyId":"CUL-F08","targetKind":"DRIVER","targetId":"CUL-040","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":["SF-CUL-LAYER-004","SF-CUL-LAYER-005","SF-CUL-LAYER-006"],"reason":deep[2]["stopReason"]},
      {"id":"HYP-CUL-LAYER-AE-004","originFamilyId":"CUL-F13","targetKind":"DRIVER","targetId":"CUL-086","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":["SF-CUL-LAYER-007","SF-CUL-LAYER-008"],"reason":deep[3]["stopReason"]},
    ]
    write(DATA / "actions-events-hypotheses.json", ae)
    write(DATA / "actions-events-identity-registry.json", {})
    write(DATA / "candidate-proposition-registry.json", {})
    write(DATA / "evidence-assessments.json", [])
    overlaps = [
      {"id":"OV-CUL-001","sources":[S(4),S(5),S(6),S(7),S(8)],"issue":"Tightness theory, cross-national studies and bounded experiments differ in level and cannot be counted as independent intervention replications."},
      {"id":"OV-CUL-002","sources":[S(9),S(10),S(11)],"issue":"Synchrony synthesis overlaps primary paradigms; modalities and social outcomes are heterogeneous."},
      {"id":"OV-CUL-003","sources":[S(2),S(3)],"issue":"Related author/program and constructs; discourse experiments are not independent evidence of aggregate cultural change."},
      {"id":"OV-CUL-004","sources":[S(12),S(13),S(14)],"issue":"Narrative and collective-memory reviews are conceptual context, not experimental evidence for a specific causal edge."},
    ]
    write(DATA / "source-overlap-registry.json", overlaps)
    skeptical = [
      {"id":"SK-CUL-001","claimId":"HYP-CUL-LAYER-003","attemptedFalsification":["Aggregate versus individual level","Nonrandom national exposure","Threat prime versus durable culture"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[0]["stopReason"]},
      {"id":"SK-CUL-002","claimId":"HYP-CUL-LAYER-004","attemptedFalsification":["Culture not randomized","Individual responses not shared norm","Restricted sample"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[1]["stopReason"]},
      {"id":"SK-CUL-003","claimId":"HYP-CUL-LAYER-008","attemptedFalsification":["Bundled synchrony/arousal","Social endpoint mismatch","Cooperation null"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[2]["stopReason"]},
      {"id":"SK-CUL-004","claimId":"HYP-CUL-LAYER-013","attemptedFalsification":["Individual endorsement versus shared norm","Message-package bundling","No durable aggregation"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[3]["stopReason"]},
    ]
    write(DATA / "skeptical-review.json", skeptical)
    write(DATA / "cross-family-issues.json", [
      {"id":"XF-CUL-001","families":["CUL-F01","CUL-F03"],"issue":"Shared values and norm strength can covary; neither is a constituent of the other without a specified model."},
      {"id":"XF-CUL-002","families":["CUL-F04","CUL-F09"],"issue":"Honor, sacredness and violence legitimacy must not be collapsed into one moralization pathway."},
      {"id":"XF-CUL-003","families":["CUL-F07","CUL-F13"],"issue":"Collective narrative content, memory and identity are distinct constructs with shared measurements."},
      {"id":"XF-CUL-004","families":["CUL-F08","CUL-F03"],"issue":"Ritual synchrony and norm entrenchment share group context but no additive duplicate effect is created."},
    ])
    write(DATA / "cross-layer-findings.json", [
      {"id":"XL-CUL-001","relationshipIds":[f"REL-CUL-{i:03d}" for i in (45,46,47,48,49,55)],"reusedFrom":"PSYCHOLOGICAL_LAYER/relationship-review-registry.json","issue":"Six exact Cultural-to-Psychological reviews reused; Psychological science not reopened."},
      {"id":"XL-CUL-002","relationshipIds":["REL-CUL-054"],"reusedFrom":"INFORMATIONAL_LAYER/relationship-review-registry.json","issue":"Governed euphemism-to-metaphor segment review reused; Informational science not reopened."},
      {"id":"XL-CUL-003","relationshipIds":["REL-CUL-050","REL-CUL-051","REL-CUL-052","REL-CUL-053"],"issue":"Social endpoints remain externally owned and research-needed; shared cultural norms are not actual network structure or individual social state."},
    ])
    write(DATA / "architecture-escalations.json", [{"id":"ARCH-CUL-LAYER-0001","issue":"CUL-088 permits multiple profile variables, aggregation levels and distance metrics but is already the source of REL-CUL-042.","affectedIds":["CUL-088","REL-CUL-042"],"resolution":"Future versioned RDS definition and causal-source governance; no production change.","blocksIndependentLayerAudit":False,"blocksNewRdsCausalMaterialization":True}])
    write(DATA / "astra-escalation-queue.json", [{"id":"ASTRA-CUL-LAYER-001","question":"Can CUL-088 be an independent causal source of CUL-061, or is the edge a summary of profile constituents that also determine entrenchment?","availableEvidence":"Frozen derivation is a distance over unspecified generation profiles; REL-CUL-042 asserts a negative direct causal edge with unspecified functional form.","conflictingInterpretations":["Distance as explanatory predictor","Distance as summary measurement sharing constituents with outcome"],"whySolShouldNotResolve":"The choice changes RDS causal-source architecture and scientific meaning.","consequence":"Keep REL-CUL-042 research-needed and block new RDS causal materialization."}])

    groups = [
      {"id":"GRP-CUL-001","recommendation":"APPROVE_RETAIN_V1_INCOMPLETE","recordIds":[k for k,v in reviews.items() if v["disposition"]=="RETAIN_V1_INCOMPLETE" and not v["priorDecisionOrReview"]],"rationale":"Seven bounded existing propositions may remain unchanged while exposure, aggregation, timing and evidence fields stay V1-incomplete."},
      {"id":"GRP-CUL-002","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[k for k,v in reviews.items() if v["disposition"]=="RESEARCH_NEEDED" and not v["priorDecisionOrReview"] and k != "REL-CUL-042"],"rationale":"New-to-this-audit existing causal edges lack exact culture-level identification; production remains unchanged."},
      {"id":"GRP-CUL-003","recommendation":"ACCEPT_CATEGORY_ERROR_REJECTIONS","recordIds":[x["id"] for x in triage if x["outcome"]=="REJECT_CATEGORY_ERROR"],"rationale":"Individual measure, state or task performance cannot substitute for shared cultural prevalence or convention."},
      {"id":"GRP-CUL-004","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[x["id"] for x in triage if x["outcome"]=="INSUFFICIENT_PRELIMINARY_SIGNAL"],"rationale":"Three broad routes ended at cheap triage because no exact culture-level causal contrast was isolated."},
    ]
    individual = [{"id":f"DEC-CUL-RETYPE-{i:02d}","recommendation":"APPROVE_RETYPE_REVIEW_ONLY","recordIds":[rid],"rationale":RETYPE_REASONS[rid]} for i,rid in enumerate(sorted(RETYPE),1)]
    for i,(hyp,aeid,label) in enumerate(zip(["HYP-CUL-LAYER-003","HYP-CUL-LAYER-004","HYP-CUL-LAYER-008","HYP-CUL-LAYER-013"], [x["id"] for x in ae], ["TIGHTNESS","HONOR","SYNCHRONY","MULTICULTURALISM"]),1):
        individual.append({"id":f"DEC-CUL-{label}","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[hyp,aeid],"rationale":deep[i-1]["stopReason"]})
    blocked = [{"id":"BLK-CUL-RDS-001","recommendation":"BLOCKED","recordIds":["ARCH-CUL-LAYER-0001","ASTRA-CUL-LAYER-001","CUL-088","REL-CUL-042"],"rationale":"Generational Cultural Distance has no selected versioned profile, aggregation or distance metric, yet is a causal source. No architecture or production change is authorized."}]

    registry_names = ["relationship-review-registry", "negative-coverage-registry", "rds-review", "triage-hypotheses", "deep-research-ledger", "candidate-source-registry", "source-findings", "source-overlap-registry", "actions-events-hypotheses", "cross-family-issues", "cross-layer-findings", "architecture-escalations", "astra-escalation-queue", "skeptical-review"]
    decision_for = {}
    for unit in groups + individual + blocked:
        for rid in unit["recordIds"]:
            assert rid not in decision_for, rid
            decision_for[rid] = unit["id"]
    index = []
    for name in registry_names:
        obj = read(DATA / f"{name}.json")
        seq = list(obj.values()) if isinstance(obj, dict) else obj
        keys = list(obj) if isinstance(obj, dict) else None
        for j,val in enumerate(seq):
            rid = keys[j] if keys is not None else val["id"]
            prior = val.get("priorDecisionOrReview") if isinstance(val, dict) else None
            decision = decision_for.get(rid)
            if name == "relationship-review-registry" and not decision:
                assert prior, rid
            index.append({"rowId":f"GI-CUL-LAYER-{len(index)+1:04d}","registry":name,"recordId":rid,"decisionId":decision,
                          "rowClass":"SCIENTIFIC_VOTE_REFERENCE" if decision else "NONVOTING_ACKNOWLEDGEMENT","priorDecisionOrReview":prior})
    write(DATA / "governance-index.json", index)
    source_recs = {sid:{"candidateSourceId":sid,"canonicalExactMatch":None,"recommendation":"RESEARCH_NEEDED_OR_LANDSCAPE_ONLY","dependencyIds":[],"registrationNowAuthorized":False} for sid in sources}
    write(DATA / "source-registration-recommendations.json", source_recs)
    gov = {"schemaVersion":"1.0.0","programId":PROGRAM_ID,"advisory":"ADVISORY — HUMAN DECISION REQUIRED",
           "originalGovernanceRows":len(index),"distinctScientificDecisions":len(groups)+len(individual)+len(blocked)+sum(bool(v["priorDecisionOrReview"]) for v in reviews.values()),
           "groupedHumanDecisions":groups,"individualScientificDecisions":individual,"blockedDecisions":blocked,
           "nonVotingAcknowledgements":sum(x["rowClass"]=="NONVOTING_ACKNOWLEDGEMENT" for x in index),
           "priorScientificPropositionsReused":sum(bool(v["priorDecisionOrReview"]) for v in reviews.values()),
           "futureMaterializationRecommendations":{"Relationships":0,"HappeningTypes":0,"EffectAssertions":0,"EvidenceAssessments":0},"newGoverned":0,"newActive":0}
    write(DATA / "governance-recommendations.json", gov)

    write(DATA / "resource-telemetry.json", {"driversCovered":90,"rdsReviewed":1,
      "cheapNegativeAERoutes":sum(x["entityType"]=="DRIVER" and x["actionsEventsStatus"]=="INSUFFICIENT_PRELIMINARY_SIGNAL" for x in coverage.values()),
      "hypothesisRoutesGenerated":len(triage),"propositionsEnteringDeepResearch":len(deep),"formalRelationshipsRetained":0,
      "formalEffectAssertionsRetained":0,"sourceFindings":len(findings),"evidenceAssessments":0,"priorLayerRelationshipReviewsReused":7,
      "sourcesReusedAcrossFamilies":sum(len(row["sourceIds"]) for row in landscapes.values())-len({s for row in landscapes.values() for s in row["sourceIds"]}),
      "newCandidateSources":len(sources),"crossFamilyDuplicateVotesPrevented":4,"happeningTypeIdentitiesReused":0,"astraEscalations":1,
      "creditSavings":"NOT_MEASURED","tokenSavings":"NOT_MEASURED","timeSavings":"NOT_MEASURED"})
    for f in read(DATA / "progress.json")["families"]: pass
    progress = read(DATA / "progress.json"); progress["families"] = {f:"COMPLETE" for f in progress["families"]}; write(DATA / "progress.json", progress)
    write_doc(DOCS / "CULTURAL_LAYER_PROGRESS.md", "# Cultural Layer progress\n\n"+PREFIX+f"Program `{PROGRAM_ID}`; frozen main `{base['baseCommit']}`.\n\n| Family | Stage |\n|---|---|\n"+"\n".join(f"| {f} | COMPLETE |" for f in progress["families"]) + "\n")

    counts = Counter(x["disposition"] for x in reviews.values())
    render("RELATIONSHIP_SUMMARY", f"All 55 incident active causal Relationships were reviewed exactly once: 23 within-Family, 21 same-Layer cross-Family and 11 outgoing cross-Layer. No incoming Cultural causal edge exists.\n\n| Disposition | Count |\n|---|---:|\n"+"\n".join(f"| {k} | {v} |" for k,v in sorted(counts.items()))+"\n\nSix Psychological and one Informational exact prior reviews are reused. Five retype proposals are review-only. No production Relationship is changed.\n")
    render("CONSTRUCT_BOUNDARIES", "The audit keeps shared cultural prevalence separate from individual endorsement; message, prime or insult exposure separate from cultural change; cultural norm separate from Social network state; narrative exposure separate from collective memory; synchrony manipulation separate from ritual convention; and task performance separate from shared cognitive convention. Cross-national association does not identify a manipulable causal direction. No definition, alias, family or ontology class changes.\n")
    render("CROSS_FAMILY_ISSUES", "Four shared issues are reconciled once: values versus norms, honor/sacredness/violence, narrative-memory-identity overlap, and ritual synchrony versus norm entrenchment. No duplicate candidate contribution is created.\n")
    render("CROSS_LAYER_FINDINGS", "Six exact Cultural-to-Psychological reviews and the Informational euphemism review are reused. Four Cultural-to-Social edges remain research-needed with external ownership preserved. Individual psychological response, informational message property and Social structure are not substituted for a Cultural Driver.\n")
    render("ACTIONS_EVENTS_SUMMARY", "All 90 Drivers have V2 coverage; the one RDS is not an eligible direct effect target. Four exact operation routes entered deep research: threat/tightness, honor insult, synchrony, and multiculturalism discourse. All remain research-needed after skeptical review. No HappeningType identity, formal EffectAssertion or EvidenceAssessment is retained.\n")
    fcounts = Counter("SUPPORT" if x["disposition"].startswith("SUPPORTS") else "MIXED" for x in findings)
    render("EVIDENCE_SUMMARY", f"The shared candidate bibliography contains {len(sources)} PubMed-verified source identities and {len(findings)} sourceFindings. Findings classify as {fcounts['SUPPORT']} bounded support and {fcounts['MIXED']} mixed/associational rows. Null cooperation in the dance study is explicit. Reviews and included paradigms are not counted as independent replication. All access depth is PubMed abstract. No candidate source is canonically registered.\n")
    rejected = [x for x in triage if x["outcome"]=="REJECT_CATEGORY_ERROR"]
    render("REJECTIONS", f"Six exact category-error hypotheses are recommended for rejection: {', '.join(x['id'] for x in rejected)}. They reject only the stated level or construct substitution; they do not assert absence of cultural mechanisms. Three cheap-triage routes remain research-needed rather than rejected.\n")
    render("ARCHITECTURE_ESCALATIONS", "`ARCH-CUL-LAYER-0001`, `BLK-CUL-RDS-001` and `ASTRA-CUL-LAYER-001` preserve the unresolved meaning of `CUL-088 → CUL-061`. A selected profile, aggregation and distance metric are absent, and constituent overlap may defeat independent causal-source interpretation. No RDS, edge, Network State binding or architecture is changed.\n")
    fam_lines = [f"| {fid} | {sum(x['familyId']==fid for x in coverage.values())} | COMPLETE | {landscapes[fid]['boundaries']} |" for fid in sorted(landscapes)]
    render("COMPLETENESS_REPORT", "All 13 Families have membership, landscape, incident-edge ownership, Driver/A&E coverage, RDS review where applicable, triage, bounded deep research, skeptical review and deduplication. No candidate quota was used.\n\n| Family | Entities | Stage | Principal boundary |\n|---|---:|---|---|\n"+"\n".join(fam_lines)+"\n")
    recommendations = f"""## Executive summary

The {len(index)} governance-index rows reduce to **{len(groups)} grouped decisions + {len(individual)} individual scientific decisions + {len(blocked)} blocked decision**. Seven prior Layer reviews are acknowledgements rather than new votes; {gov['nonVotingAcknowledgements']} rows are non-voting workflow/evidence acknowledgements. New GOVERNED = 0; new ACTIVE = 0.

## Grouped approvals recommended

`GRP-CUL-001` recommends retaining seven bounded V1-incomplete existing Relationships without semantic change.

## Grouped rejection recommendations

`GRP-CUL-003` rejects six exact individual-to-cultural or task-to-convention category errors.

## Grouped research-needed recommendations

`GRP-CUL-002` keeps new-to-this-audit existing edges research-needed. `GRP-CUL-004` keeps three broad routes at cheap triage.

## Existing Relationship proposals

Five individual retype proposals are review-only. Six Psychological revision reviews and one Informational retain review are reused. No production edge is implemented, revised or retyped.

## New Relationship candidates

None retained.

## HappeningType identities

None recommended. Deep routes used bundled or context-bound operations without a governance-ready reusable Cultural identity.

## EffectAssertions

Four serious A&E routes remain `KEEP_RESEARCH_NEEDED`; no formal EffectAssertion is recommended.

## EvidenceAssessment dependencies

No EvidenceAssessment is created because no formal candidate survived exact construct and level review.

## Construct/ontology questions

Shared prevalence versus individual endorsement, message versus norm, and ritual behavior versus cultural convention need claim-specific clarification. No ontology edit is proposed.

## Architecture blockers

`BLK-CUL-RDS-001` preserves the CUL-088 causal-source question and Astra escalation.

## Future source registrations

None. All 15 sources support landscape or research-needed work only.

## Proposed future materialization set

Relationships **0**; HappeningTypes **0**; EffectAssertions **0**; EvidenceAssessments **0**.

## Explicit exclusions

No production Relationship, Driver/RDS, prior Layer, source registry, ontology, Network State, architecture or lifecycle changes.

## Activation boundary

NO ACTIVATION is recommended or authorized.
"""
    render("GOVERNANCE_RECOMMENDATIONS", recommendations)
    render("GOVERNANCE_REVIEW_SUMMARY", f"From **{len(index)} original rows**, the package proposes **{len(groups)} grouped + {len(individual)} individual + {len(blocked)} blocked** decisions. **{gov['nonVotingAcknowledgements']}** rows are non-voting acknowledgements and seven prior reviews are reused. The human should read the five retype proposals, four deep routes and the CUL-088 RDS blocker most closely. Future materialization is zero in every record class.\n")
    handoff = f"Program `{PROGRAM_ID}` completed all 13 Cultural Families against main `{base['baseCommit']}`. The structured registries are authoritative. No new Relationship, HappeningType, EffectAssertion or EvidenceAssessment is recommended for materialization. Production hashes match the frozen baseline. The candidate PR must remain open and unmerged until human governance.\n"
    if (DATA / "governance-decision-001.json").exists():
        handoff += "\n## Human governance and closeout\n\nHuman decision `GOV-CULTURAL-LAYER-001-2026-09-21` approved the conservative recommendations. Materialization is **NONE**: zero new governed records, zero active records, and zero canonical source registrations. No activation audit is needed. `CUL-088`, `REL-CUL-042`, `ARCH-CUL-LAYER-0001`, `BLK-CUL-RDS-001`, and `ASTRA-CUL-LAYER-001` remain unresolved for later dedicated governance.\n"
    render("HANDOFF", handoff)
    manifest = {"schemaVersion":"1.0.0","programId":PROGRAM_ID,"baseCommit":base["baseCommit"],"familiesComplete":13,"driversCovered":90,"rdsReviewed":1,"entitiesReviewed":91,"relationshipReviews":55,"protectedScienceHashFile":"protected-baseline.json","governanceRows":len(index),"groupedVotes":len(groups),"individualVotes":len(individual),"blockedVotes":len(blocked),"nonVotingAcknowledgements":gov["nonVotingAcknowledgements"],"newGoverned":0,"newActive":0,"status":"ADVISORY_HUMAN_DECISION_REQUIRED"}
    write(DOCS / "CULTURAL_LAYER_AUDIT_MANIFEST.json", manifest)
    print("Cultural package", len(reviews), "relationships", len(index), "governance rows", len(findings), "findings")


if __name__ == "__main__":
    build()
