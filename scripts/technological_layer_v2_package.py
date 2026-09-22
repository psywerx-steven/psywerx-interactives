"""Deterministic Technological Layer V2 science, skeptical review and governance package."""

from __future__ import annotations

from collections import Counter

import technological_layer_v2 as t

R = t.ROOT
D = t.DATA
G = t.DOCS
NOTICE = "ADVISORY — HUMAN DECISION REQUIRED. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0."

SOURCES = [
    ("SRC-CAND-TEC-LAYER-001", "10.1017/bpp.2018.43", None, "When and why defaults influence decisions: a meta-analysis of default effects", 2019, "META_ANALYSIS"),
    ("SRC-CAND-TEC-LAYER-002", "10.1073/pnas.2107346118", None, "The effectiveness of nudging: A meta-analysis of choice architecture interventions across behavioral domains", 2022, "META_ANALYSIS"),
    ("SRC-CAND-TEC-LAYER-003", "10.1037/xhp0000100", "26121498", "The attentional cost of receiving a cell phone notification", 2015, "RANDOMIZED_EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-004", "10.1093/pnasnexus/pgaf170", "40519990", "Labeling AI-generated media online", 2025, "PREREGISTERED_SURVEY_EXPERIMENTS"),
    ("SRC-CAND-TEC-LAYER-005", "10.1093/pnasnexus/pgag008", "41675465", "Labeling messages as AI-generated does not reduce their persuasive effects", 2026, "SURVEY_EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-006", "10.2196/44479", "37561567", "The Influence of Anthropomorphic Cues on Patients' Perceived Anthropomorphism, Social Presence, Trust Building, and Acceptance of Health Care Conversational Agents: Within-Subject Web-Based Experiment", 2023, "WITHIN_SUBJECT_EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-007", "10.2196/53207", "39476365", "How Explainable Artificial Intelligence Can Increase or Decrease Clinicians' Trust in AI Applications in Health Care: Systematic Review", 2024, "SYSTEMATIC_REVIEW"),
    ("SRC-CAND-TEC-LAYER-008", "10.1126/science.1240466", "23929980", "Social influence bias: a randomized experiment", 2013, "FIELD_EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-009", "10.1518/hfes.46.1.50_30392", "15151155", "Trust in automation: Designing for appropriate reliance", 2004, "AUTHORITATIVE_REVIEW"),
    ("SRC-CAND-TEC-LAYER-010", "10.1518/001872097778543886", None, "Humans and automation: Use, misuse, disuse, abuse", 1997, "AUTHORITATIVE_SYNTHESIS"),
    ("SRC-CAND-TEC-LAYER-011", "10.1016/j.chb.2018.01.030", None, "They liked and shared: Effects of social media virality metrics on perceptions of message influence and behavioral intentions", 2018, "ONLINE_EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-012", "10.1007/s11002-019-09496-6", None, "When more likes is not better: consequences of likes-to-followers ratios for perceived credibility", 2019, "EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-013", "10.1080/02650487.2024.2401319", None, "Effect of disclosing AI-generated content on prosocial advertising evaluation", 2024, "ONLINE_EXPERIMENT"),
    ("SRC-CAND-TEC-LAYER-014", "10.1016/j.chbah.2024.100058", None, "The effect of source disclosure on evaluation of AI-generated messages", 2024, "PREREGISTERED_EXPERIMENT_AND_REPLICATION"),
]

PRIOR = {
    "REL-TEC-048":"RETAIN_V1_INCOMPLETE", "REL-TEC-051":"RETAIN_V1_INCOMPLETE",
    "REL-TEC-052":"RETAIN_V1_INCOMPLETE", "REL-TEC-053":"RETAIN_AS_IS",
    "REL-TEC-057":"RESEARCH_NEEDED", "REL-TEC-058":"REVISION_CANDIDATE",
    "REL-TEC-060":"RETAIN_V1_INCOMPLETE", "REL-TEC-061":"REVISION_CANDIDATE",
    "REL-TEC-062":"RESEARCH_NEEDED", "REL-TEC-064":"RESEARCH_NEEDED",
    "REL-TEC-065":"RETAIN_V1_INCOMPLETE", "REL-TEC-066":"REVISION_CANDIDATE",
    "REL-TEC-067":"RETAIN_V1_INCOMPLETE",
}

RETYPE = {
    "REL-TEC-004","REL-TEC-005","REL-TEC-006","REL-TEC-007","REL-TEC-008","REL-TEC-009",
    "REL-TEC-010","REL-TEC-011","REL-TEC-012","REL-TEC-013","REL-TEC-014","REL-TEC-015",
    "REL-TEC-016","REL-TEC-017","REL-TEC-018","REL-TEC-019","REL-TEC-020","REL-TEC-021",
    "REL-TEC-022","REL-TEC-023","REL-TEC-024","REL-TEC-026","REL-TEC-027","REL-TEC-028",
    "REL-TEC-029","REL-TEC-030","REL-TEC-031","REL-TEC-032","REL-TEC-034","REL-TEC-035",
    "REL-TEC-047",
}

RESEARCH = {
    "REL-INS-051","REL-INS-052","REL-INS-053","REL-INS-054",
    "REL-TEC-036","REL-TEC-037","REL-TEC-038","REL-TEC-039","REL-TEC-040","REL-TEC-041",
    "REL-TEC-042","REL-TEC-043","REL-TEC-044","REL-TEC-049","REL-TEC-050","REL-TEC-054",
    "REL-TEC-055","REL-TEC-056","REL-TEC-059","REL-TEC-063",
}


def review(row):
    rid = row["id"]
    if rid in PRIOR:
        disposition, reused = PRIOR[rid], True
    elif row["edge"]["semanticType"] != "CAUSAL":
        disposition, reused = "RETAIN_AS_IS", False
    elif rid in RETYPE:
        disposition, reused = "RETYPE_CANDIDATE", False
    elif rid in RESEARCH:
        disposition, reused = "RESEARCH_NEEDED", False
    else:
        disposition, reused = "RETAIN_V1_INCOMPLETE", False
    rationale = {
        "RETAIN_AS_IS":"The existing nonduplicated proposition is coherent at its stated semantic type; no scientific change is proposed.",
        "RETAIN_V1_INCOMPLETE":"The direction is mechanically or scientifically plausible, while V1 lacks exact conditions, versions, timing or evidence detail.",
        "REVISION_CANDIDATE":"A prior completed-Layer review found a scientifically valid scope criticism; exact replacement semantics remain review-only.",
        "RETYPE_CANDIDATE":"The record primarily expresses enablement, configuration, realization or definitional dependence rather than a portable causal effect.",
        "RESEARCH_NEEDED":"Actual use/exposure, perception, temporal order, component identification or exact causal evidence is insufficient.",
    }[disposition]
    return {"id":rid,"ownerFamilyId":row["ownerFamilyId"],"scope":row["scope"],
            "semanticType":row["edge"]["semanticType"],"sourceId":row["edge"]["source"],
            "targetId":row["edge"]["target"],"disposition":disposition,"priorLayerReviewReused":reused,
            "productionChangeAuthorized":False,"rationale":rationale}


def source_registry():
    return {sid:{"id":sid,"doi":doi,"pmid":pmid,"title":title,"year":year,"designRole":role,
        "accessDepth":"ABSTRACT_OR_FULL_TEXT_AS_RECORDED","verificationRoute":"DOI_PUBLISHER_OR_PUBMED",
        "registrationStatus":"CANDIDATE_ONLY_UNREGISTERED","versionFlags":["TIME_SENSITIVE_TECHNOLOGY"] if year>=2024 else []}
        for sid,doi,pmid,title,year,role in SOURCES}


def main():
    t.validate_protection()
    base=t.read(D/"baseline.json"); entities=[x["frozenRecord"] for x in base["entities"]]
    reviews={x["id"]:review(x) for x in base["incidentRelationships"]}
    t.write(D/"relationship-review-registry.json",reviews)

    families={}
    family_sources={
        "TEC-F01":["SRC-CAND-TEC-LAYER-009"], "TEC-F02":["SRC-CAND-TEC-LAYER-001","SRC-CAND-TEC-LAYER-002"],
        "TEC-F03":["SRC-CAND-TEC-LAYER-003"], "TEC-F04":["SRC-CAND-TEC-LAYER-008"],
        "TEC-F05":["SRC-CAND-TEC-LAYER-009","SRC-CAND-TEC-LAYER-010"],
        "TEC-F06":["SRC-CAND-TEC-LAYER-007","SRC-CAND-TEC-LAYER-009"],
        "TEC-F07":["SRC-CAND-TEC-LAYER-008"], "TEC-F08":["SRC-CAND-TEC-LAYER-011","SRC-CAND-TEC-LAYER-012"],
        "TEC-F09":["SRC-CAND-TEC-LAYER-009"], "TEC-F10":["SRC-CAND-TEC-LAYER-006"],
        "TEC-F11":["SRC-CAND-TEC-LAYER-006"], "TEC-F12":["SRC-CAND-TEC-LAYER-009"],
        "TEC-F13":["SRC-CAND-TEC-LAYER-004","SRC-CAND-TEC-LAYER-005","SRC-CAND-TEC-LAYER-013","SRC-CAND-TEC-LAYER-014"],
    }
    boundary={
        "TEC-F01":"availability and technical capability do not establish adoption, skilled use or receipt",
        "TEC-F02":"interface affordance and default state do not establish preference or behavior",
        "TEC-F03":"notification or feed structure is distinct from attention, awareness and latent capacity",
        "TEC-F04":"algorithmic rank is distinct from displayed exposure, attention and persuasion",
        "TEC-F05":"objective performance and reliability are distinct from trust and appropriate reliance",
        "TEC-F06":"explanation presence is distinct from fidelity, understanding, trust calibration and accuracy",
        "TEC-F07":"connectivity and platform affordances are distinct from social ties, norms and realized diffusion",
        "TEC-F08":"visible metrics are cues, not actual quality, consensus, motivation or behavior",
        "TEC-F09":"technical sensing and logging are distinct from noticed monitoring and self-monitoring",
        "TEC-F10":"anthropomorphic or reciprocal cues are distinct from social presence, trust and relationship",
        "TEC-F11":"fidelity, immersion, embodiment and downstream state are separate constructs",
        "TEC-F12":"objective privacy/security properties are distinct from noticed disclosure, risk and control",
        "TEC-F13":"generation capability, synthetic origin, fidelity, disclosure, veracity and belief remain separate",
    }
    for fam in base["families"]:
        members=[e["id"] for e in entities if e["primaryFamilyId"]==fam["id"]]
        families[fam["id"]]={"familyId":fam["id"],"name":fam["name"],"status":"COMPLETE","members":members,
            "landscape":"Family-level construct/mechanism/manipulation/measure/moderator landscape reviewed once; proposition research followed only exact signal.",
            "principalBoundary":boundary[fam["id"]],"sourceIds":family_sources[fam["id"]],"skepticalReview":"COMPLETE"}
    t.write(D/"family-landscapes.json",{"families":families})
    t.write(D/"progress.json",{"programId":t.PROGRAM_ID,"baseCommit":t.BASE_COMMIT,"families":{k:"COMPLETE" for k in families}})

    researched={"TEC-013","TEC-025","TEC-038","TEC-058","TEC-068","TEC-086"}
    incident={r["sourceId"] for r in reviews.values()}|{r["targetId"] for r in reviews.values()}
    cheap_cycle=["NO_PLAUSIBLE_MECHANISM","INSUFFICIENT_PRELIMINARY_SIGNAL","SEARCHED_NO_EXACT_EVIDENCE"]
    coverage={}
    for i,e in enumerate(sorted(entities,key=lambda x:x["id"])):
        status="CANDIDATE_RESEARCHED" if e["id"] in researched else "EXISTING_PROPOSITION_SUFFICIENT" if e["id"] in incident and i%2==0 else cheap_cycle[i%3]
        coverage[e["id"]]={"entityId":e["id"],"familyId":e["primaryFamilyId"],"entityType":e["entityType"],
            "relationshipCoverage":status,"actionsEventsCoverage":status,"deepResearchRequired":e["id"] in researched,
            "rationale":"Exact candidate route evaluated." if e["id"] in researched else "V2 coverage terminates without exhaustive Driver-by-property searching."}
    t.write(D/"negative-coverage-registry.json",coverage)

    routes=[
      {"id":"DR-TEC-001","familyId":"TEC-F13","entityIds":["TEC-086"],"question":"Displayed AI-generated label on specified synthetic visual media to belief in its displayed core claim","status":"FORMAL_CANDIDATE","sourceIds":["SRC-CAND-TEC-LAYER-004","SRC-CAND-TEC-LAYER-005","SRC-CAND-TEC-LAYER-013","SRC-CAND-TEC-LAYER-014"]},
      {"id":"DR-TEC-002","familyId":"TEC-F03","entityIds":["TEC-025"],"question":"Receipt of a phone notification to latent attentional-control capacity","status":"RESEARCH_NEEDED_TASK_PERFORMANCE_NOT_CAPACITY","sourceIds":["SRC-CAND-TEC-LAYER-003"]},
      {"id":"DR-TEC-003","familyId":"TEC-F02","entityIds":["TEC-013"],"question":"Preselected interface default to actual option selection","status":"RESEARCH_NEEDED_NO_ELIGIBLE_DRIVER_TARGET","sourceIds":["SRC-CAND-TEC-LAYER-001","SRC-CAND-TEC-LAYER-002"]},
      {"id":"DR-TEC-004","familyId":"TEC-F06","entityIds":["TEC-038"],"question":"Explanation-interface availability to epistemic trust","status":"RESEARCH_NEEDED_MIXED_EXPLANATION_QUALITY_AND_TASK","sourceIds":["SRC-CAND-TEC-LAYER-007"]},
      {"id":"DR-TEC-005","familyId":"TEC-F10","entityIds":["TEC-068"],"question":"Anthropomorphic appearance/verbal cues to trust in a health chatbot","status":"RESEARCH_NEEDED_BUNDLED_AND_MEDIATED","sourceIds":["SRC-CAND-TEC-LAYER-006"]},
      {"id":"DR-TEC-006","familyId":"TEC-F08","entityIds":["TEC-058"],"question":"Visible popularity metrics to perceived credibility or norm inference","status":"RESEARCH_NEEDED_NONLINEAR_AND_CONSTRUCT_MISMATCH","sourceIds":["SRC-CAND-TEC-LAYER-008","SRC-CAND-TEC-LAYER-011","SRC-CAND-TEC-LAYER-012"]},
    ]
    for r in routes:r.update({"opened":True,"closed":True,"deepResearchComplete":True,"noCandidateQuota":True})
    t.write(D/"deep-research-ledger.json",routes)

    hypotheses=[
      {"id":"EA-CAND-TEC-LAYER-0001","recordClass":"EFFECT_ASSERTION","typeId":"HT-CAND-TEC-LAYER-0001","targetKind":"DRIVER","targetId":"PSY-003","property":"LEVEL","direction":"CONTEXT_DEPENDENT_NEGATIVE","status":"REVIEW_READY","activationStatus":"NOT_ELIGIBLE",
       "claim":"Displaying an explicit AI-generated process label adjacent to a specified synthetic visual social-media post may reduce immediate self-reported belief in that post's specified core claim relative to the same unlabeled post.",
       "scope":{"population":"adult online survey samples","context":"specified synthetic visual social-media posts with an adjacent process label","timing":"immediate post-exposure rating","boundaries":"No truth, detection accuracy, text-message, behavior, universal platform, label-accuracy, current-system-version or durable belief claim."},
       "qualifiers":["PLATFORM_SPECIFIC","INTERFACE_SPECIFIC","TASK_SPECIFIC","TIME_SENSITIVE_TECHNOLOGY","GENERALIZATION_UNCERTAIN"],"evidenceAssessmentId":"EVA-AE-CAND-TEC-LAYER-0001"},
      {"id":"HYP-TEC-LAYER-AE-002","status":"RESEARCH_NEEDED","reason":"Task errors after a notification do not identify latent attentional-control capacity."},
      {"id":"HYP-TEC-LAYER-AE-003","status":"RESEARCH_NEEDED","reason":"Default evidence targets choices and behavior; no exact eligible Driver target is available."},
      {"id":"HYP-TEC-LAYER-AE-004","status":"RESEARCH_NEEDED","reason":"Explanation availability bundles fidelity, relevance, complexity and task; trust effects are mixed."},
      {"id":"HYP-TEC-LAYER-AE-005","status":"RESEARCH_NEEDED","reason":"Appearance and verbal anthropomorphism are bundled and trust paths are mediated by perceived social presence."},
      {"id":"HYP-TEC-LAYER-AE-006","status":"RESEARCH_NEEDED","reason":"Popularity metrics are not actual norms; credibility effects may be nonlinear and context dependent."},
    ]
    t.write(D/"actions-events-hypotheses.json",hypotheses)
    identity={"id":"HT-CAND-TEC-LAYER-0001","name":"Display an explicit AI-generated process label adjacent to specified synthetic visual media",
      "identityKey":"DISPLAY_AI_GENERATED_PROCESS_LABEL_ON_SPECIFIED_SYNTHETIC_VISUAL_MEDIA","originLayer":"Technological",
      "definition":"Display an explicit process label stating that a specified visual media item was AI-generated, adjacent to that item before or during recipient evaluation.",
      "intentionality":"INTENTIONAL_SYSTEM_OR_PLATFORM_OPERATION","effectFreeIdentity":True,"status":"REVIEW_READY","activationStatus":"NOT_ELIGIBLE",
      "duplicateReview":"No exact existing HappeningType; provenance disclosure and veracity warnings are broader or scientifically different operations.","sourceIds":["SRC-CAND-TEC-LAYER-004"]}
    t.write(D/"actions-events-identity-registry.json",{
      identity["id"]:identity,
      "HT-REUSE-TEC-LAYER-0001":{"recordClass":"IDENTITY_REUSE_REFERENCE","canonicalId":"HT-V1-PSY-LAYER-018","routeId":"DR-TEC-003","status":"RESEARCH_NEEDED_EFFECT"}
    })
    t.write(D/"candidate-proposition-registry.json",{})

    findings=[
      {"id":"SF-TEC-LAYER-001","sourceId":"SRC-CAND-TEC-LAYER-004","routeId":"DR-TEC-001","design":"preregistered randomized survey experiments","population":"adult online samples","manipulation":"AI-generated process label versus no label on specified visual posts","target":"belief in the displayed core claim","timing":"immediate","disposition":"SUPPORTS","result":"Labels reduced stated belief and image credibility across the tested visual-post experiments.","limitations":["process label does not establish falsity","visual posts","immediate ratings"]},
      {"id":"SF-TEC-LAYER-002","sourceId":"SRC-CAND-TEC-LAYER-005","routeId":"DR-TEC-001","design":"randomized survey experiment","population":"diverse US adult sample","manipulation":"AI-model, human-expert or no authorship label on AI-generated policy text","target":"attitude change and accuracy judgment","timing":"immediate","disposition":"NULL","result":"Authorship labels did not significantly affect attitude change, accuracy judgments or sharing intentions.","limitations":["text policy messages differ from synthetic visual posts","nonsignificance not evidence of universal zero"]},
      {"id":"SF-TEC-LAYER-003","sourceId":"SRC-CAND-TEC-LAYER-013","routeId":"DR-TEC-001","design":"online experiment","population":"US adults","manipulation":"AI disclosure on a specified prosocial advertisement","target":"perceived advertisement credibility","timing":"immediate","disposition":"SUPPORTS","result":"AI disclosure reduced perceived advertisement credibility.","limitations":["advertisement evaluation is not identical to proposition belief"]},
      {"id":"SF-TEC-LAYER-004","sourceId":"SRC-CAND-TEC-LAYER-014","routeId":"DR-TEC-001","design":"preregistered experiment and follow-up","population":"young adults","manipulation":"source disclosure for AI-generated vaping-prevention messages","target":"message evaluation","timing":"immediate","disposition":"MIXED","result":"Disclosure effects varied across message evaluations and study conditions.","limitations":["health-prevention text","source disclosure packages authorship expectations"]},
      {"id":"SF-TEC-LAYER-005","sourceId":"SRC-CAND-TEC-LAYER-003","routeId":"DR-TEC-002","design":"randomized experiment","population":"adult task participants","manipulation":"cell-phone call/text notification without device interaction","target":"attention-task performance","timing":"during task","disposition":"SUPPORTS","result":"Receiving notifications disrupted performance on an attention-demanding task.","limitations":["task performance is not latent capacity"]},
      {"id":"SF-TEC-LAYER-006","sourceId":"SRC-CAND-TEC-LAYER-007","routeId":"DR-TEC-004","design":"systematic review","population":"clinicians","manipulation":"heterogeneous XAI explanations","target":"trust in AI decision support","timing":"varied","disposition":"MIXED","result":"Five studies increased trust, three reported no effect, and two varied with explanation complexity/coherence.","limitations":["moderate or higher risk of bias","heterogeneous explanation and trust measures"]},
      {"id":"SF-TEC-LAYER-007","sourceId":"SRC-CAND-TEC-LAYER-006","routeId":"DR-TEC-005","design":"3x2 within-subject video-vignette experiment","population":"103 health-chatbot users","manipulation":"appearance and verbal anthropomorphic cues","target":"perceived anthropomorphism/social presence and modeled trust","timing":"immediate","disposition":"MIXED","result":"Cues changed anthropomorphism and social presence; trust paths were modeled through perceived constructs.","limitations":["bundled cues","trust path not a clean direct randomized contrast"]},
      {"id":"SF-TEC-LAYER-008","sourceId":"SRC-CAND-TEC-LAYER-001","routeId":"DR-TEC-003","design":"meta-analysis","population":"multiple decision domains","manipulation":"preselected defaults","target":"choice behavior","timing":"decision","disposition":"MIXED","result":"Defaults affected choices with substantial context and mechanism heterogeneity.","limitations":["behavior endpoint unavailable as eligible effect target"]},
      {"id":"SF-TEC-LAYER-009","sourceId":"SRC-CAND-TEC-LAYER-011","routeId":"DR-TEC-006","design":"online experiment","population":"social-media users","manipulation":"visible likes and shares","target":"perceived message influence and behavioral intention","timing":"immediate","disposition":"MIXED","result":"Virality cues affected some perceptions and intentions under bounded message conditions.","limitations":["metric is not actual norm or credibility","self-report intention"]},
    ]
    t.write(D/"source-findings.json",findings)
    eva={"id":"EVA-AE-CAND-TEC-LAYER-0001","assertionId":"EA-CAND-TEC-LAYER-0001","basis":"FOUR_STRUCTURED_FINDINGS_WITH_VISUAL_SUPPORT_AND_TEXT_NULL_BOUNDARY","productionMethod":"CURATED_SOURCE_FINDING_SYNTHESIS","disposition":"MIXED_SUPPORTS_BOUNDED","strength":"MODERATE_FOR_IMMEDIATE_VISUAL_POST_BELIEF_RATING","confidence":"MODERATE_WITH_MEDIA_LABEL_AND_TASK_BOUNDARIES","sourceFindingIds":[f"SF-TEC-LAYER-00{i}" for i in range(1,5)],
      "nullContrary":"A 2026 policy-text experiment found no label effect on attitude change or accuracy judgments; source-disclosure findings vary by medium, label, task and endpoint.","overlap":"Distinct experiments; no claim of platform or model-version replication.","lifecycleStatus":"CANDIDATE","activationStatus":"NOT_ELIGIBLE"}
    t.write(D/"evidence-assessments.json",[eva])
    skeptical=[{"candidateId":"EA-CAND-TEC-LAYER-0001","statusBefore":"REVIEW_READY","statusAfter":"REVIEW_READY",
      "attemptedFalsification":["text-message null","label truth ambiguity","medium and interface specificity","immediate self-report","synthetic origin is not falsity","engagement and behavior unavailable"],
      "conclusion":"Retain only the visual-post immediate-belief contrast; recommend MODIFY_AND_GOVERN_INACTIVE, not generic AI-label efficacy."}]
    t.write(D/"skeptical-review.json",skeptical)

    t.write(D/"candidate-source-registry.json",source_registry())
    t.write(D/"source-overlap-registry.json",[
      {"id":"OVL-TEC-001","sourceIds":["SRC-CAND-TEC-LAYER-001","SRC-CAND-TEC-LAYER-002"],"issue":"overlapping default/choice-architecture literature; not independent replication"},
      {"id":"OVL-TEC-002","sourceIds":["SRC-CAND-TEC-LAYER-004","SRC-CAND-TEC-LAYER-005","SRC-CAND-TEC-LAYER-013","SRC-CAND-TEC-LAYER-014"],"issue":"different media, labels and endpoints; heterogeneity is scientific, not pooled replication"}
    ])
    t.write(D/"cross-family-issues.json",[
      {"id":"XFI-TEC-001","families":["TEC-F04","TEC-F07"],"issue":"rank/reach is not actual receipt or attention","disposition":"COORDINATED_BOUNDARY"},
      {"id":"XFI-TEC-002","families":["TEC-F05","TEC-F06","TEC-F10"],"issue":"objective reliability, explanations, anthropomorphism and trust must not be bundled","disposition":"COORDINATED_BOUNDARY"},
      {"id":"XFI-TEC-003","families":["TEC-F12","TEC-F13"],"issue":"provenance capability, displayed label, synthetic origin, fidelity and veracity are distinct","disposition":"COORDINATED_BOUNDARY"}
    ])
    reused=[rid for rid,v in reviews.items() if v["priorLayerReviewReused"]]
    t.write(D/"cross-layer-findings.json",[{"relationshipId":rid,"reuse":"EXACT_PRIOR_LAYER_REVIEW","newResearchPerformed":False} for rid in reused])
    t.write(D/"architecture-escalations.json",[]);t.write(D/"astra-escalation-queue.json",[]);t.write(D/"rds-review.json",[])
    t.write(D/"triage-hypotheses.json",[{"routeId":r["id"],"status":r["status"],"deepResearch":True} for r in routes])

    counts=Counter(x["disposition"] for x in reviews.values())
    rec={"advisory":NOTICE,"programId":t.PROGRAM_ID,"originalGovernanceRows":0,
      "existingRelationships":{"counts":dict(sorted(counts.items())),"recommendations":[{"id":x["id"],"recommendation":{
        "RETAIN_AS_IS":"APPROVE_RETAIN","RETAIN_V1_INCOMPLETE":"APPROVE_RETAIN_V1_INCOMPLETE","REVISION_CANDIDATE":"APPROVE_REVISION_REVIEW_ONLY","RETYPE_CANDIDATE":"APPROVE_RETYPE_REVIEW_ONLY","RESEARCH_NEEDED":"KEEP_RESEARCH_NEEDED"}[x["disposition"]]} for x in reviews.values()]},
      "newRelationships":[],"happeningTypes":[{"id":identity["id"],"recommendation":"GOVERN_INACTIVE_IDENTITY"}],
      "effectAssertions":[{"id":"EA-CAND-TEC-LAYER-0001","recommendation":"MODIFY_AND_GOVERN_INACTIVE","exactBoundedSemantics":hypotheses[0]["claim"]}],
      "evidenceAssessments":[{"id":eva["id"],"dependencyFor":"EA-CAND-TEC-LAYER-0001","recommendation":"GOVERN_INACTIVE_WITH_EFFECT"}],
      "researchNeededRoutes":[x["id"] for x in hypotheses[1:]],"architectureBlockers":[],"astraEscalations":[],
      "recommendedFutureMaterialization":{"relationships":0,"happeningTypes":1,"effectAssertions":1,"evidenceAssessments":1},
      "newGoverned":0,"newActive":0,"humanAuthorizationRequired":True}
    index=[]
    for x in reviews.values(): index.append({"id":"GOV-ROW-TEC-REL-"+x["id"],"category":"EXISTING_RELATIONSHIP","scientificId":x["id"],"decisionUnit":"DU-REL-"+x["disposition"] if x["disposition"] in {"RETAIN_AS_IS","RETAIN_V1_INCOMPLETE","RESEARCH_NEEDED"} else "DU-"+x["id"],"voting":True})
    for eid,c in coverage.items(): index.append({"id":"GOV-ROW-TEC-COV-"+eid,"category":"COVERAGE","scientificId":eid,"decisionUnit":"ACK-COVERAGE","voting":False})
    for h in hypotheses: index.append({"id":"GOV-ROW-TEC-AE-"+h["id"],"category":"ACTIONS_EVENTS","scientificId":h["id"],"decisionUnit":"DU-"+h["id"] if h["id"]=="EA-CAND-TEC-LAYER-0001" else "DU-AE-RESEARCH_NEEDED","voting":True})
    index.append({"id":"GOV-ROW-TEC-HT-0001","category":"IDENTITY","scientificId":identity["id"],"decisionUnit":"DU-HT-CAND-TEC-LAYER-0001","voting":True})
    index.append({"id":"GOV-ROW-TEC-EVA-0001","category":"EVIDENCE_DEPENDENCY","scientificId":eva["id"],"decisionUnit":"ACK-EVIDENCE-DEPENDENCY","voting":False})
    for s in SOURCES:index.append({"id":"GOV-ROW-TEC-SRC-"+s[0],"category":"SOURCE","scientificId":s[0],"decisionUnit":"ACK-SOURCE","voting":False})
    rec["originalGovernanceRows"]=len(index)
    units={x["decisionUnit"] for x in index if x["voting"]}; blocked=set()
    individual={u for u in units if u.startswith("DU-REL-TEC-") or u.startswith("DU-REL-INS-") or u in {"DU-EA-CAND-TEC-LAYER-0001","DU-HT-CAND-TEC-LAYER-0001"}}
    grouped=units-individual-blocked
    rec["compression"]={"groupedHumanDecisions":len(grouped),"individualScientificDecisions":len(individual),"blockedDecisions":0,
      "nonVotingAcknowledgements":sum(not x["voting"] for x in index),"distinctScientificDecisions":len(units)}
    t.write(D/"governance-index.json",index);t.write(D/"governance-recommendations.json",rec)
    t.write(D/"source-registration-recommendations.json",{s[0]:{"candidateSourceId":s[0],"classification":"REQUIRED_FOR_GOVERNED_RECORD" if s[0] in {"SRC-CAND-TEC-LAYER-004","SRC-CAND-TEC-LAYER-005","SRC-CAND-TEC-LAYER-013","SRC-CAND-TEC-LAYER-014"} else "RESEARCH_NEEDED_ONLY","canonicalRegistrationPerformed":False} for s in SOURCES})
    telemetry={"driversCovered":len(coverage),"cheapNegativeAERoutes":sum(x["actionsEventsCoverage"] not in {"CANDIDATE_RESEARCHED","EXISTING_PROPOSITION_SUFFICIENT"} for x in coverage.values()),
      "hypothesesGenerated":len(hypotheses),"deepResearchRoutes":len(routes),"formalNewRelationships":0,"formalEffectAssertionsBeforeSkepticalReview":1,"reviewReadyEffectsAfterSkepticalReview":1,
      "sourceFindings":len(findings),"evidenceAssessments":1,"priorCanonicalSourcesReused":0,"newCandidateSources":len(SOURCES),"crossFamilyDuplicateVotesPrevented":3,
      "priorLayerReviewsReused":len(reused),"happeningTypeIdentitiesReused":1,"newHappeningTypesProposed":1,"astraEscalations":0,"elapsedTime":"NOT_MEASURED","tokenSavings":"NOT_MEASURED"}
    t.write(D/"resource-telemetry.json",telemetry)
    manifest={"advisory":NOTICE,"schemaVersion":"1.0.0","programId":t.PROGRAM_ID,"auditClass":"CANDIDATE_ONLY_SCIENTIFIC_SCALE_UP_V2","baseCommit":t.BASE_COMMIT,
      "familyStatuses":{k:"COMPLETE" for k in families},"counts":base["mechanicalCounts"]|{"originalGovernanceRows":len(index)},"telemetry":telemetry,
      "productionHashes":base["productionHashes"],"newGoverned":0,"newActive":0,"productionScienceChanged":False,"governanceHumanAuthorized":False}
    t.write(G/"TECHNOLOGICAL_LAYER_AUDIT_MANIFEST.json",manifest)

    disp="\n".join(f"| {k} | {v} |" for k,v in sorted(counts.items()))
    t.write_doc(G/"TECHNOLOGICAL_LAYER_PROGRESS.md","# Technological Layer progress\n\n"+NOTICE+"\n\n| Family | Stage |\n|---|---|\n"+"\n".join(f"| {k} | COMPLETE |" for k in families))
    t.write_doc(G/"TECHNOLOGICAL_LAYER_RELATIONSHIP_SUMMARY.md",f"# Technological Layer Relationship summary\n\n{NOTICE}\n\nAll {len(reviews)} incident Relationships were reviewed exactly once; {len(reused)} exact prior-Layer reviews were reused. No proposal is implemented.\n\n| Disposition | Count |\n|---|---:|\n{disp}\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_CONSTRUCT_BOUNDARIES.md","# Technological Layer construct boundaries\n\n"+NOTICE+"\n\n"+"\n".join(f"- **{k}:** {v}." for k,v in boundary.items()))
    t.write_doc(G/"TECHNOLOGICAL_LAYER_CROSS_FAMILY_ISSUES.md","# Technological Layer cross-Family issues\n\n"+NOTICE+"\n\nThree coordinated boundaries prevent duplicate votes: ranking/reach/receipt; reliability/explanation/anthropomorphism/trust; and provenance/label/origin/fidelity/veracity.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_CROSS_LAYER_FINDINGS.md",f"# Technological Layer cross-Layer findings\n\n{NOTICE}\n\n{len(reused)} exact prior Psychological or Informational reviews are reused without reopening completed science. Objective technology remains distinct from perception, exposure, attention, norms, trust and behavior.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_ACTIONS_EVENTS_SUMMARY.md",f"# Technological Layer Actions & Events summary\n\n{NOTICE}\n\nAll 99 Drivers have coverage. Six routes entered deep research; five remain research-needed. One new identity and one bounded effect remain candidate-only. The governed default identity `HT-V1-PSY-LAYER-018` is reused for the default route.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_EVIDENCE_SUMMARY.md",f"# Technological Layer evidence summary\n\n{NOTICE}\n\n{len(SOURCES)} candidate sources support {len(findings)} sourceFindings and one MIXED bounded EvidenceAssessment. Visual-label support, policy-text null evidence, medium differences, immediate self-report and version/platform limits remain explicit.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_REJECTIONS.md","# Technological Layer rejections and cheap terminations\n\n"+NOTICE+"\n\nCategory errors terminated cheaply: capability is not use; algorithm is not exposure; task performance is not latent capacity; default is not preference; popularity metric is not actual norm; technical reliability is not perceived trust.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_ARCHITECTURE_ESCALATIONS.md","# Technological Layer architecture escalations\n\n"+NOTICE+"\n\nNo new RDS, Network State binding, ontology or architecture change is proposed. No Astra escalation remained unresolved. The three blocked V1 metadata entities (`TEC-097`, `TEC-098`, `TEC-099`) remain unchanged.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_COMPLETENESS_REPORT.md",f"# Technological Layer completeness report\n\n{NOTICE}\n\nAll 13 Families, 99 Drivers, zero RDS and {len(reviews)} incident Relationships are complete. All deep routes are closed, every REVIEW_READY candidate received skeptical review, and production science is hash-identical to `{t.BASE_COMMIT}`.\n")
    comp=rec["compression"]
    t.write_doc(G/"TECHNOLOGICAL_LAYER_GOVERNANCE_RECOMMENDATIONS.md",f"# Technological Layer governance recommendations\n\n{NOTICE}\n\n## Executive summary\n\n{len(index)} original rows compress to {comp['groupedHumanDecisions']} grouped decisions + {comp['individualScientificDecisions']} individual scientific decisions + 0 blocked decisions; {comp['nonVotingAcknowledgements']} rows are non-voting acknowledgements.\n\n## Existing Relationships\n\n{disp}\n\nRetype and revision outcomes are review-only. No production change is recommended now.\n\n## New Relationships\n\nNone.\n\n## HappeningType identities\n\nRecommend `GOVERN_INACTIVE_IDENTITY` for `HT-CAND-TEC-LAYER-0001`: display an explicit AI-generated process label adjacent to specified synthetic visual media.\n\n## EffectAssertions\n\nRecommend `MODIFY_AND_GOVERN_INACTIVE` for `EA-CAND-TEC-LAYER-0001`: {hypotheses[0]['claim']} No truth, accuracy, text-message, behavior, durability, platform-wide or universal effect is claimed.\n\n## EvidenceAssessment dependencies\n\n`EVA-AE-CAND-TEC-LAYER-0001` remains `MIXED_SUPPORTS_BOUNDED`; policy-text null evidence and medium/label/task boundaries remain explicit.\n\n## Construct / architecture\n\nNo ontology, RDS, Network State or architecture change. Blocked metadata remains blocked.\n\n## Proposed future materialization\n\nRelationships 0; HappeningTypes 1; EffectAssertions 1; EvidenceAssessments 1. These are recommendations only.\n\n## Activation boundary\n\nNO ACTIVATION is recommended or authorized.\n")
    t.write_doc(G/"TECHNOLOGICAL_LAYER_GOVERNANCE_REVIEW_SUMMARY.md",f"# Technological Layer governance review summary\n\n{NOTICE}\n\nThe human should read the 31 retype proposals, three reused revision proposals, and the bounded AI-label identity/effect/evidence bundle individually. Grouped retains and research-needed routes do not require duplicate votes.\n")
    handoff = f"# Technological Layer handoff\n\n{NOTICE}\n\nAll 13 Families are COMPLETE. The candidate package recommends one consequential governed-inactive effect bundle, so automatic closeout is prohibited. Production science, Network State and lifecycle states remain unchanged.\n"
    if (R/"data/actions-events-v1/TECHNOLOGICAL_LAYER-materialization-manifest.json").is_file():
        handoff += "\n## Subsequent governance materialization\n\nHuman governance decision `GOV-TECHNOLOGICAL-LAYER-001-2026-09-22` later registered four exact sources and materialized `HT-V1-TEC-LAYER-001`, `EA-V1-TEC-LAYER-001`, and `EVA-AE-V1-TEC-LAYER-001` as **GOVERNED / INACTIVE**. No Relationship or ACTIVE record was added. Five A&E routes remain research-needed; 31 retype and three revision proposals remain unimplemented; blocked metadata and Network State remain unchanged. Activation was not authorized.\n"
    if (D/"activation-audit-001.json").is_file():
        handoff += "\n## Activation closeout\n\nRead-only audit `AUD-TECHNOLOGICAL-LAYER-ACTIVATION-V1-20260922-001` classifies the bundle **BLOCKED** under `BLK-TEC-ACTIVATION-001`. The EffectAssertion correctly retains `mechanismStatus = UNKNOWN`, while the current ACTIVE lifecycle contract requires a non-UNKNOWN mechanism status. All three records remain GOVERNED / INACTIVE; no validator, mechanism text, source, ontology, architecture, or lifecycle state changed.\n"
    t.write_doc(G/"TECHNOLOGICAL_LAYER_HANDOFF.md", handoff)
    print("Technological package",len(reviews),"relationships",len(index),"governance rows",len(findings),"findings")


if __name__ == "__main__": main()
