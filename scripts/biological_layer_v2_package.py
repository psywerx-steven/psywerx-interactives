"""Render the advisory Biological governance package from structured registries."""

from __future__ import annotations

from collections import Counter, defaultdict

from biological_layer_v2 import DATA, DOCS, PROGRAM_ID, read, write, write_doc, validate_protection

PREFIX = "**ADVISORY — HUMAN DECISION REQUIRED. New GOVERNED = 0; new ACTIVE = 0.**\n\n"
REGISTRY_NAMES = [
    "relationship-review-registry", "triage-hypotheses", "actions-events-identity-registry",
    "actions-events-hypotheses", "evidence-assessments", "rds-review", "cross-family-issues",
    "cross-layer-findings", "architecture-escalations", "astra-escalation-queue",
    "source-overlap-registry", "negative-coverage-registry", "deep-research-ledger",
    "source-findings", "candidate-source-registry", "family-landscapes", "skeptical-review",
]


def rows(name):
    obj = read(DATA / (name + ".json"))
    if name == "family-landscapes": return obj["families"]
    return obj


def render(name, body):
    write_doc(DOCS / ("BIOLOGICAL_LAYER_" + name + ".md"), "# Biological Layer " + name.replace("_", " ").lower() + "\n\n" + PREFIX + body)


def build() -> None:
    validate_protection()
    base = read(DATA / "baseline.json")
    rel = rows("relationship-review-registry")
    triage = rows("triage-hypotheses")
    ae = rows("actions-events-hypotheses")
    ht = rows("actions-events-identity-registry")
    assessments = rows("evidence-assessments")
    coverage = rows("negative-coverage-registry")
    rds = rows("rds-review")
    deep = rows("deep-research-ledger")
    findings = rows("source-findings")
    skeptical = rows("skeptical-review")
    sources = rows("candidate-source-registry")
    landscapes = rows("family-landscapes")
    assert len(base["families"]) == len(landscapes) == 14
    assert len(rel) == 39 and len(coverage) == 77 and len(rds) == 5 and len(skeptical) == 4
    finding_classes = Counter("SUPPORT" if x["disposition"].startswith("SUPPORTS") else
                              "MIXED" if x["disposition"].startswith("MIXED") else
                              "NULL" if x["disposition"].startswith("NULL") else "OTHER" for x in findings)

    groups = [
      {"id":"GRP-BIO-001","recommendation":"APPROVE_RETAIN_V1_INCOMPLETE","recordIds":[k for k,v in rel.items() if v["disposition"] == "RETAIN_V1_INCOMPLETE" and not v["priorDecisionOrReview"]],"rationale":"Eight existing bounded propositions may be retained without a production semantic or execution change; individual caveats remain attached."},
      {"id":"GRP-BIO-002","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[k for k,v in rel.items() if v["disposition"] == "RESEARCH_NEEDED" and not v["priorDecisionOrReview"]],"rationale":"Ten existing edge claims lack exact endpoint, dose, timing or causal identification; each remains unchanged with its own rationale."},
      {"id":"GRP-BIO-003","recommendation":"ACCEPT_CATEGORY_ERROR_REJECTIONS","recordIds":[x["id"] for x in triage if x["outcome"] == "REJECT_CATEGORY_ERROR"],"rationale":"Biomarker, homeostatic drive, observational performance, frailty measurement and polygenic prediction cannot be equated with causal state claims."},
      {"id":"GRP-BIO-004","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[x["id"] for x in triage if x["outcome"] == "INSUFFICIENT_PRELIMINARY_SIGNAL"],"rationale":"Four broad heat, exercise, injury and alcohol routes lack exact dose, endpoint or construct alignment; no formal new claim is minted."},
    ]
    individual = [
      {"id":"DEC-BIO-ENDOTOXIN","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":["HYP-BIO-LAYER-006","HYP-BIO-LAYER-AE-002"],"rationale":"Acute male endotoxin experiments show immune and symptom responses, but cytokines, mood and whole BIO-030 sickness severity differ; one paper reports working-memory accuracy null and opposite reaction-time result."},
      {"id":"DEC-BIO-IRON","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":["HYP-BIO-LAYER-008","HYP-BIO-LAYER-AE-003"],"rationale":"Oral iron trials support reported general fatigue in selected low-ferritin women, while meta-analysis finds no clear objective capacity effect. Exact BIO-025 physical fatigue is not isolated."},
      {"id":"DEC-BIO-THYROID","recommendation":"REJECT_PROPOSAL","recordIds":["HYP-BIO-LAYER-009","HYP-BIO-LAYER-AE-004"],"rationale":"Older mild subclinical-hypothyroid thyroid replacement does not improve reported fatigability in the cited randomized trial; this does not prove a general hormone-to-fatigue null."},
      {"id":"DEC-BIO-CAFFEINE-IDENTITY","recommendation":"GOVERN_INACTIVE_IDENTITY","recordIds":["HT-CAND-BIO-LAYER-0001"],"rationale":"Abrupt cessation of habitual caffeine is a coherent operation identity distinct from BIO-F01 timed caffeine administration; identity governance implies no efficacy, treatment recommendation or activation."},
      {"id":"DEC-BIO-CAFFEINE-EFFECT","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":["EA-CAND-BIO-LAYER-0001","EVA-AE-CAND-BIO-LAYER-0001"],"rationale":"Blinded studies support transient symptom effects, but incidence and symptom composition vary; no exact whole-BIO-066 severity aggregation or transportable population effect is ready. MIXED remains MIXED."},
    ]
    blocked = [{"id":"BLK-BIO-RDS-001","recommendation":"BLOCKED","recordIds":["ARCH-BIO-LAYER-0001","ASTRA-BIO-LAYER-001"] + [x["id"] for x in rds],"rationale":"Five BIO-F01 RDS have no exact versioned rule in frozen entity records; BIO-003 is a causal source under heightened D10. Pilot B01 review remains unimplemented. Future architecture/definition governance is needed before a new RDS causal-source claim or constituent/aggregate representation."}]
    decision_for = {}
    for unit in groups + individual + blocked:
        for rid in unit["recordIds"]:
            assert rid not in decision_for, rid
            decision_for[rid] = unit["id"]
    index = []
    for name in REGISTRY_NAMES:
        obj = rows(name)
        sequence = list(obj.values()) if isinstance(obj, dict) else obj
        keys = list(obj) if isinstance(obj, dict) else None
        for j, val in enumerate(sequence):
            rid = keys[j] if keys is not None else val["id"]
            decision_id = decision_for.get(rid)
            prior = val.get("priorDecisionOrReview") if isinstance(val, dict) else None
            row_class = "SCIENTIFIC_VOTE_REFERENCE" if decision_id else "NONVOTING_ACKNOWLEDGEMENT"
            if name == "relationship-review-registry" and not decision_id:
                assert prior, rid
            index.append({"rowId":f"GI-BIO-LAYER-{len(index)+1:04d}","registry":name,"recordId":rid,
                          "decisionId":decision_id,"rowClass":row_class,"priorDecisionOrReview":prior})
    write(DATA / "governance-index.json", index)
    future_source_ids = ["SRC-CAND-BIO-LAYER-021","SRC-CAND-BIO-LAYER-022","SRC-CAND-BIO-LAYER-023"]
    source_recs = {sid:{"candidateSourceId":sid,"canonicalExactMatch":row["canonicalExactMatch"],
        "recommendation":"REQUIRED_IF_IDENTITY_APPROVED" if sid in future_source_ids else "RESEARCH_NEEDED_OR_LANDSCAPE_ONLY",
        "dependencyIds":["HT-CAND-BIO-LAYER-0001"] if sid in future_source_ids else [],
        "registrationNowAuthorized":False} for sid,row in sources.items()}
    write(DATA / "source-registration-recommendations.json", source_recs)
    gov = {"schemaVersion":"1.0.0","programId":PROGRAM_ID,"advisory":"ADVISORY — HUMAN DECISION REQUIRED",
       "originalGovernanceRows":len(index),"distinctScientificDecisions":len(groups)+len(individual)+len(blocked)+sum(bool(v["priorDecisionOrReview"]) for v in rel.values()),
       "groupedHumanDecisions":groups,"individualScientificDecisions":individual,"blockedDecisions":blocked,
       "nonVotingAcknowledgements":sum(x["rowClass"]=="NONVOTING_ACKNOWLEDGEMENT" for x in index),
       "priorScientificPropositionsReused":sum(bool(v["priorDecisionOrReview"]) for v in rel.values()),
       "futureMaterializationRecommendations":{"Relationships":0,"HappeningTypes":1,"EffectAssertions":0,"EvidenceAssessments":0},
       "newGoverned":0,"newActive":0}
    write(DATA / "governance-recommendations.json", gov)
    votes = len(groups)+len(individual)+len(blocked)
    assert len(set(decision_for.values())) == votes

    # Layer-level readable package. Individual rationales and source-level details remain in the registries.
    render("RELATIONSHIP_SUMMARY", "The frozen baseline has 39 incident Relationships and 32 causal propositions: 7 within-Family, 14 same-Layer cross-Family, 6 incoming and 5 outgoing. Each is reviewed exactly once.\n\n" +
       "| Disposition | Count |\n|---|---:|\n" + "\n".join(f"| {k} | {v} |" for k,v in sorted(Counter(x["disposition"] for x in rel.values()).items())) +
       "\n\nBIO-F01's 17 pilot Relationships/derivations and four exact Psychological reviews are reused without a new vote. B01–B05 remain review-only; no existing proposition is changed. See `relationship-review-registry.json` for every ID and exact rationale.\n")
    render("CONSTRUCT_BOUNDARIES", "The audit keeps biomarker separate from biological Driver, physiological state from subjective report, acute from chronic, stable susceptibility from acute state, administered drug from realized pharmacologic effect, and realized effect from behavior. Dependence, cessation and withdrawal are distinct. Chronological age does not itself specify aging mechanism. Clinical cohorts do not automatically transfer to the general population. Homeostatic feedback can be nonlinear; physiological correlation does not set causal direction; task performance is not broad capacity.\n\nSpecific unresolved cases are iron-trial general fatigue versus `BIO-025` physical fatigue, cytokine level versus `BIO-030` whole sickness response, polygenic score versus mechanism, frailty scale overlap with physical fitness, and caffeine symptom frequencies versus aggregate `BIO-066` severity. No definition, alias or ontology class is changed.\n")
    render("CROSS_FAMILY_ISSUES", "Four shared issues are recorded once in `cross-family-issues.json`: sleep/fatigue pilot reuse; inflammation, oxygen-carrying capacity and fatigue; caffeine delivery versus cessation; and hydration/heat exposure. Shared endpoints are consultations, not duplicate candidate votes.\n")
    render("CROSS_LAYER_FINDINGS", "Five BIO↔PSY edges use exact prior Psychological reviews or BIO-F01 governance. Social effects `REL-BIO-022/023` remain research-needed. Physical/Environmental exposure routes retain external ownership and distinguish exposure from achieved physiological state. The completed Informational Layer has no exact new Biological proposition to re-research.\n")
    render("ACTIONS_EVENTS_SUMMARY", "All 72 Drivers have V2 A&E coverage; five RDS are `NOT_APPLICABLE` as direct effect targets. One novel cessation identity `HT-CAND-BIO-LAYER-0001` is review-ready for inactive identity governance. It is distinct from BIO-F01 caffeine delivery. One formal effect `EA-CAND-BIO-LAYER-0001` was deep-researched and downgraded to `RESEARCH_NEEDED` after skeptical review. Three other exact routes (endotoxin, iron, thyroid) remain research-needed and did not become formal effects. No direct RDS, RelationalState or generic context target is created.\n")
    render("EVIDENCE_SUMMARY", f"The candidate bibliography has {len(sources)} PubMed-verified identities, all candidate-only and unregistered. There are {len(findings)} structured sourceFindings across four deep routes: {finding_classes['SUPPORT']} bounded-support, {finding_classes['MIXED']} mixed and {finding_classes['NULL']} null-at-the-stated-endpoint rows. One candidate EvidenceAssessment remains MIXED and non-governed; its whole-target conclusion is insufficient. The four independent skeptical checks are in `skeptical-review.json`. Oral iron synthesis includes the 2003 and 2012 primary trials; caffeine review includes older substitution studies, and the sickness review is not a third experiment. The older-adult thyroid fatigability null, endotoxin working-memory accuracy null and opposite-direction high-dose reaction-time component are explicit. Abstract-level access is stated in each finding; no unobserved effect size or full-text detail is inferred.\n")
    render("REJECTIONS", "Five category-error hypotheses (`HYP-BIO-LAYER-002/003/007/010/011`) and the broad thyroid-benefit hypothesis (`HYP-BIO-LAYER-009`) are recommended for rejection at their exact wording. The trial null does not assert a universal physiological zero. All rejected routes remain durable candidate workflow conclusions, not production records.\n")
    render("ARCHITECTURE_ESCALATIONS", "`ARCH-BIO-LAYER-0001` / `BLK-BIO-RDS-001` concerns exact BIO-F01 RDS calculation and causal-source semantics, especially `BIO-003 → BIO-001`. `ASTRA-BIO-LAYER-001` records the causal-versus-constituent interpretation of that prior B01 proposal. No rule, formula, edge, definition, Network State binding or target schema is changed. Independent Driver and A&E work is unaffected.\n")
    fam_lines = []
    for f in sorted(landscapes):
        members = [x for x in coverage.values() if x["familyId"]==f]
        fam_lines.append(f"| {f} | {len(members)} | COMPLETE | {landscapes[f]['boundaries']} |")
    render("COMPLETENESS_REPORT", "Each Family has membership, landscape, incident-edge ownership, Driver/A&E coverage, RDS review where applicable, triage, bounded deep research if warranted, skeptical review and Layer dedup. No candidate quota was used.\n\n| Family | Entities | Stage | Principal boundary |\n|---|---:|---|---|\n"+"\n".join(fam_lines)+"\n")
    recommendations = f"""## Executive summary

The {len(index)} index rows reduce to **{len(groups)} grouped decisions + {len(individual)} individual scientific decisions + {len(blocked)} blocked decision**. {gov['priorScientificPropositionsReused']} prior reviewed or governed Relationship propositions are acknowledged rather than voted again; {gov['nonVotingAcknowledgements']} rows are non-voting workflow/evidence acknowledgements. New GOVERNED = 0; new ACTIVE = 0.

## Grouped approvals recommended

`GRP-BIO-001` retains eight new-to-this-audit V1-incomplete relationships without semantic change. Earlier BIO-F01 retain and review-only decisions remain effective.

## Grouped rejection recommendations

`GRP-BIO-003` rejects five exact category errors; each hypothesis and reason remains in `triage-hypotheses.json`.

## Grouped research-needed recommendations

`GRP-BIO-002` keeps ten existing Relationships research-needed. `GRP-BIO-004` keeps four broad routes at cheap-triage research-needed.

## Existing Relationship proposals

No B01–B05 revision proposal is implemented. The four prior Psychological reviews are reused. No new retype, split, deprecation or replacement is recommended for implementation.

## New Relationship candidates

None retained. Correlation, biomarker overlap and formula dependency did not pass the causal candidate gate.

## HappeningType identities

`DEC-BIO-CAFFEINE-IDENTITY`: recommend `GOVERN_INACTIVE_IDENTITY` for `HT-CAND-BIO-LAYER-0001`, a single bounded abrupt cessation of habitual caffeine intake. Identity does not imply efficacy, actionability or activation.

## EffectAssertions

`DEC-BIO-CAFFEINE-EFFECT`: recommend `KEEP_RESEARCH_NEEDED` for `EA-CAND-BIO-LAYER-0001`. This formal candidate was downgraded after skeptical review because symptom-level data, incidence variation and a missing exact whole-target aggregation do not support governed `BIO-066` severity semantics. Endotoxin, iron and thyroid routes stay individual deferred decisions.

## EvidenceAssessment dependencies

`EVA-AE-CAND-BIO-LAYER-0001` remains candidate-only, MIXED and `NOT_ELIGIBLE`. Its support for bounded symptoms does not become evidence of one transportable whole-syndrome effect.

## Construct/ontology questions

Iron general fatigue versus physical fatigue, cytokines versus sickness intensity, and frailty/fitness measure overlap require clarification before exact new propositions. No ontology edit is proposed here.

## Architecture blockers

`BLK-BIO-RDS-001` preserves `ARCH-BIO-LAYER-0001` and `ASTRA-BIO-LAYER-001`. No RDS source architecture decision is made.

## Future source registrations

Only candidate sources 021, 022 and 023 would be provenance dependencies if the human later approves the inactive caffeine-cessation identity. Register none now. The caffeine review source 020 is background, not an independent trial.

## Proposed future materialization set

Relationships **0**; HappeningTypes **1**; EffectAssertions **0**; EvidenceAssessments **0**. These are recommendations only.

## Explicit exclusions

No production Relationship, Driver/RDS, pilot, prior Layer, canonical source, ontology, Network State, architecture or lifecycle is changed. Every deferred A&E route and category-error ledger remains candidate-only.

## Activation boundary

NO ACTIVATION is recommended or authorized by this review. Candidate identities and evidence cannot participate in active causal execution.
"""
    render("GOVERNANCE_RECOMMENDATIONS", recommendations)
    render("GOVERNANCE_REVIEW_SUMMARY", f"From **{len(index)} original governance rows**, the package proposes **{len(groups)} grouped + {len(individual)} individual + {len(blocked)} blocked** new human decisions. **{gov['nonVotingAcknowledgements']}** rows are non-voting acknowledgements; **{gov['priorScientificPropositionsReused']}** previously reviewed or governed Relationship propositions are not re-voted. The consequential reads are endotoxin, iron, thyroid, caffeine identity, caffeine effect and BIO-F01 RDS architecture. Formal caffeine effect and its MIXED assessment remain research-needed. Future materialization recommendation is 0 Relationships, 1 inactive identity, 0 effects, 0 assessments.\n")
    handoff = f"Program `{PROGRAM_ID}` completed all 14 Biological Families against main `{base['baseCommit']}`. The structured registries are authoritative. The package is advisory; human science governance is still required. One inactive identity is recommended; no Relationship, EffectAssertion or EvidenceAssessment is recommended for immediate materialization. BIO-F01 pilot decisions and Psychological reviews are reused without mutation. All production scientific hashes match the frozen baseline. No Biological record is governed or active by this Layer audit. The candidate PR must remain open and unmerged until human authorization.\n"
    if (DATA / "activation-closeout-001.json").exists():
        handoff += "\n## Subsequent governance and activation closeout\n\nThe historical paragraph above describes the candidate-audit checkpoint. Human governance decision `GOV-BIOLOGICAL-LAYER-001-2026-09-21` later materialized `HT-V1-BIO-LAYER-001` as the sole new Biological record, **GOVERNED / INACTIVE**. No new Relationship, EffectAssertion, EvidenceAssessment or ACTIVE record was created. The caffeine effect remains research-needed; the RDS blocker and Astra escalation remain unresolved. Activation closeout `AUD-BIOLOGICAL-LAYER-ACTIVATION-CLOSEOUT-V1-20260921-001` recommends `KEEP_INACTIVE` and zero activations.\n"
    render("HANDOFF", handoff)
    progress = read(DATA / "progress.json")
    for f in progress["families"]: progress["families"][f] = "COMPLETE"
    write(DATA / "progress.json", progress)
    write_doc(DOCS / "BIOLOGICAL_LAYER_PROGRESS.md", "# Biological Layer progress\n\n"+PREFIX+f"Program `{PROGRAM_ID}`; frozen main `{base['baseCommit']}`.\n\n| Family | Stage |\n|---|---|\n"+"\n".join(f"| {f} | COMPLETE |" for f in progress["families"])+"\n")
    telemetry = {"driversCovered":72,"rdsReviewed":5,"cheapNegativeAERoutes":sum(x["entityType"]=="DRIVER" and x["actionsEventsStatus"]=="INSUFFICIENT_PRELIMINARY_SIGNAL" for x in coverage.values()),
       "hypothesisRoutesGenerated":len(triage),"propositionsEnteringDeepResearch":len(deep),
       "formalRelationshipsRetained":0,"formalEffectAssertionsRetained":1,
       "formalEffectAssertionsRecommendedForGovernance":0,
       "formalEffectsReviewReadyAfterSkeptical":0,"sourceFindings":len(findings),"evidenceAssessments":len(assessments),
       "sourceFindingDispositionCounts":dict(finding_classes),
       "pilotCanonicalSourcesReusedByLineage":20,"newCandidateSources":len(sources),
       "crossFamilyIssuesReconciled":len(rows("cross-family-issues")),
       "crossFamilyDuplicateVotesPrevented":0,
       "happeningTypeIdentitiesReused":0,"astraEscalations":1,
       "creditSavings":"NOT_MEASURED","tokenSavings":"NOT_MEASURED","timeSavings":"NOT_MEASURED"}
    write(DATA / "resource-telemetry.json", telemetry)
    manifest = {"schemaVersion":"1.0.0","programId":PROGRAM_ID,"baseCommit":base["baseCommit"],
       "familiesComplete":14,"driversCovered":72,"rdsReviewed":5,"entitiesReviewed":77,
       "relationshipReviews":39,"protectedScienceHashFile":"protected-baseline.json",
       "governanceRows":len(index),"groupedVotes":len(groups),"individualVotes":len(individual),"blockedVotes":len(blocked),
       "nonVotingAcknowledgements":gov["nonVotingAcknowledgements"],"newGoverned":0,"newActive":0,
       "scientificSources":"candidate-source-registry.json","status":"ADVISORY_HUMAN_DECISION_REQUIRED"}
    write(DOCS / "BIOLOGICAL_LAYER_AUDIT_MANIFEST.json", manifest)
    print("governance",len(index),"rows",len(groups),"groups",len(individual),"individual",len(blocked),"blocked",gov["nonVotingAcknowledgements"],"acknowledgements")

if __name__ == "__main__": build()
