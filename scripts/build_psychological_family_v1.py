"""Render authored Family judgments and evidence, never generate science from coverage.

All writes use the Layer output guard. No production imports/mutation/activation.
"""
from __future__ import annotations
import argparse
import copy
import re
from collections import Counter
import psychological_layer_v1 as p
import actions_events_v1 as ae
import relationship_intervention_v1 as ri

STAMP = "2026-09-07T16:54:31Z"
DECISION = "PENDING — APPROVE / MODIFY / REJECT"


def provenance(family):
    return {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Authored evidence extraction followed by candidate-only synthesis",
        "recordedAt": STAMP, "originReferences": [p.PROGRAM, p.BASELINE, family + "/research.json", family + "/evidence-inputs.json"],
        "limitations": ["No human scientific governance; selected accessed material only; not a formal systematic review"]}


def governance(identifier, family, status="REVIEW_READY"):
    transitions, previous = [], {"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}
    for state in ["CANDIDATE", "RESEARCH_NEEDED"] + (["REVIEW_READY"] if status == "REVIEW_READY" else []):
        after = {"lifecycleStatus": state, "activationStatus": "NOT_ELIGIBLE"}
        transitions.append({"fromState": previous, "toState": after, "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "rationale": "Candidate packet prepared for human review; no scientific authority granted", "timestamp": STAMP,
            "objectId": identifier, "revision": 1, "provenance": p.PROGRAM + "/" + family,
            "governanceDecisionRecord": None, "exactDecisionMaterialization": False})
        previous = after
    return {"lifecycleStatus": status, "activationStatus": "NOT_ELIGIBLE", "blockStatus": "NONE",
        "decisionOutcome": "NOT_DECIDED", "authorityBasis": "V1_NATIVE", "decisionRecord": None,
        "authorizedBy": None, "decisionDate": None, "effectiveVersion": None, "decisionRationale": None,
        "supersedesIds": [], "transitionProvenance": transitions}


def base(identifier, family, status="REVIEW_READY"):
    return {"schemaVersion": "1.0.0", "id": identifier, "revision": 1, "recordClass": "SCIENTIFIC_RECORD",
        "provenance": provenance(family), "governance": governance(identifier, family, status)}


def finding(row, assertion, family):
    f = {"id": "FND-" + assertion + "-" + row["key"], "sourceId": row["sourceId"], "locator": row["locator"],
        "accessDepth": row["accessDepth"], "population": row["population"], "context": row["context"],
        "basis": [row["basis"]], "supportedSemantics": ["CAUSAL"], "inputRole": "DIRECT_FINDING",
        "design": row["design"] + "; sample: " + (row["sample"] or "NOT_EXTRACTED"),
        **{k: row[k] for k in ("exposure", "comparator", "measurement", "timing", "result", "disposition")},
        "quantitativeEstimate": None, "uncertainty": ["No comparable numerical estimand or causal coefficient extracted"],
        "limitations": [row["limitations"]], "datasetIds": [row["dataset"]],
        "overlapNotes": "Same dataset reused across records/contrasts is one evidence contribution. Review-primary overlap is possible; no replication count or pooled weight inferred.",
        "nullInterpretation": None, "provenance": provenance(family)}
    if row["disposition"] == "NULL_FINDING":
        f["nullInterpretation"] = {"contrast": row["exposure"] + " versus " + row["comparator"],
            "precisionAssessment": "No equivalence margin/precision guarantee extracted", "interpretation": "NO_DETECTED_DIFFERENCE",
            "rationale": "Nonsignificance is preserved, not encoded as SUPPORTED_NULL or a zero effect"}
    return f


def synthesis(spec, findings):
    return {"sourceFindingIds": [f["id"] for f in findings], "disposition": spec["disposition"],
        "evidenceStrength": spec["strength"], "confidence": spec["confidence"], "rationale": spec["rationale"],
        "confidenceRationale": "Exact scoped claim only; construct transfer, method, access and heterogeneity limit certainty",
        "conflicts": [{"findingId": f["id"], "dispositionRationale": "Retain contrast and scope; do not pool distinct estimands or discard null findings"}
                      for f in findings if f["disposition"] in {"MIXED", "NULL_FINDING", "CONTRADICTED"}],
        "contraryEvidenceSearch": "ASSESSED", "generalizationLimits": [spec["scope"]],
        "datasetOverlap": "Shared publication components and synthesis-primary overlap are not independent replication; no pooled estimate computed"}


def context():
    c = ae.Context.repository()
    return ae.Context(c.entities, c.relationships, c.source_ids | {s["id"] for s in p.read(p.STORE / "candidate-source-registry.json")})


def relationship(spec, family, findings, c):
    schema = ae.read(p.ROOT / "schemas/relationship-intervention/v1/relationship-v1.schema.json")
    r = dict.fromkeys(schema["required"])
    r.update(schemaVersion="1.0.0", id=spec["id"], revision=1, relationFamily="CAUSAL", predicate="CAUSES",
        symmetry="DIRECTED", causalClaim=True, sourceEntityId=spec["source"], targetEntityId=spec["target"],
        sourceEntityType=c.entities[spec["source"]]["entityType"], targetEntityType=c.entities[spec["target"]]["entityType"],
        causalClaimRole="TOTAL_EFFECT", polarity=spec["polarity"], mechanism=spec["mechanism"],
        boundaryConditions=spec["scope"], applicability={"analyticUnit": "Person × specified claim × exposure protocol", "populationOrSystem": spec["scope"], "context": spec["scope"]},
        causalReviewGate=ri.expected_causal_review_gate(c.entities[spec["source"]]["entityType"], c.entities[spec["target"]]["entityType"]),
        moderatorSpecifications=[], sourceIds=sorted({f["sourceId"] for f in findings}), evidenceAssessmentIds=["EVA-" + spec["id"]],
        governance=governance(spec["id"], family, spec["status"]),
        compatibility={"sourceSchema": "RELATIONSHIP_V1", "authorityStatus": "V1_LIFECYCLE", "migrationCompleteness": "INCOMPLETE",
            "v1Executability": "NOT_EXECUTABLE", "blockedFields": ["humanScientificGovernance", "activation", "quantitativeExecutionNotAuthorized"],
            "legacyRelationFamily": None, "legacyScientificFields": None, "legacyRecordHash": None, "legacyRecord": None})
    syn = synthesis(spec, findings)
    ev = {"schemaVersion": "1.0.0", "id": "EVA-" + spec["id"], "revision": 1,
        "assertion": {"objectType": "RELATIONSHIP", "objectId": spec["id"]}, "sourceIds": r["sourceIds"],
        "evidenceRationale": spec["rationale"], "evidenceStrength": syn["evidenceStrength"], "confidence": syn["confidence"],
        "evidenceDisposition": syn["disposition"], "population": spec["scope"], "context": spec["scope"],
        "studyDesignCharacterizations": [{"designType": "SYNTHESIS" if f["basis"] == ["EVIDENCE_SYNTHESIS"] else f["basis"][0], "specification": f["design"]} for f in findings],
        "quantitativeEstimate": None, "uncertainty": ["No numerical weight, universal sign, causal mediation or transfer beyond stated scope"],
        "conflictingEvidence": {"sourceIds": sorted({f["sourceId"] for f in findings if f["disposition"] != "SUPPORTS"}), "summary": spec["scope"]},
        "limitations": [f["limitations"][0] for f in findings], "reviewProvenance": {"createdAt": STAMP, "createdByActorClass": "AUTOMATED_PROCESS_OR_AI",
            "reviewedAt": None, "reviewedBy": None, "sourceSchema": "RI_V1_WITH_AE_SOURCE_FINDING_CANDIDATE_SIDECAR"},
        "governance": governance("EVA-" + spec["id"], family, spec["status"])}
    sidecar = {"evidenceAssessmentId": ev["id"], "assertionId": spec["id"], "productionMethod": "SYNTHESIS",
        "sourceFindings": findings, "synthesis": syn, "governance": ev["governance"]}
    return r, ev, sidecar


def happening(spec, family):
    return {**base(spec["id"], family, spec.get("status", "REVIEW_READY")), **{k: spec[k] for k in ("name", "identityKey", "description")}, "aliases": [],
        "kindTags": ["ACTION"], "domainTags": [spec["domain"]], "originLayers": spec["origins"], "interventionSubset": True,
        "packageKind": "ATOMIC", "components": [], "componentEnumeration": "NOT_APPLICABLE",
        "actorOrSourceSystem": spec["actor"], "intentionality": "DELIBERATE", "pattern": ["DISCRETE"],
        "identityDefiningProfile": {k: None for k in ("timing", "doseIntensity", "duration", "frequency", "reach")},
        "identitySourceIds": spec["sources"], "controlProfiles": [{"actorId": spec["actor"], "extent": "UNKNOWN", "capabilities": [],
            "population": "Specified research/communication setting", "context": spec["constraints"], "conditions": spec["constraints"], "provenance": provenance(family)}]}


def effect(spec, family, findings):
    eid = "EVA-" + spec["id"]
    scope = {"population": spec["scope"], "context": spec["scope"], "boundaryConditions": spec["risk"],
             "timing": spec["timing"], "measurement": spec["measurement"]}
    row = {**base(spec["id"], family, spec["status"]), "typeId": spec["typeId"], "occurrenceId": None,
        "targetKind": "DRIVER", "targetId": spec["target"], "targetLayers": ["PSY"], "claimSemantics": "CAUSAL",
        "productionMethod": "SYNTHESIS", "property": spec["property"], "change": spec["change"], "otherSpecified": None,
        "intendedChange": None, "observedChange": spec["change"], "knowledgeStatus": spec.get("knowledgeStatus", "SUPPORTED_EFFECT"), "scope": scope,
        "exposureProfile": {k: None for k in ("timing", "doseIntensity", "duration", "frequency", "reach")},
        "mechanism": spec["mechanism"], "mechanismStatus": "PARTIAL", "mechanisticDriverIds": [],
        "grounding": {"causalIdentificationRationale": spec["rationale"], "derivationEntailed": "NO", "representedDriverId": None, "duplicatePropagationControl": None},
        "contribution": {"groupId": spec["sharedContributionId"], "role": spec.get("contributionRole", "PRIMARY"), "relatedAssertionIds": spec.get("relatedEffectIds", []),
            "reconciliation": spec.get("contributionReconciliation", "No automatic summation; Layer contribution registry links alternate Relationship description")},
        "moderatorLinks": [], "interaction": {"mode": "NONE", "otherEffectIds": [], "evidenceAssessmentIds": []},
        "qualifiers": {"reach": None, "distribution": None, "subgroups": [], "unintendedConsequences": [spec["risk"]],
            "risks": [spec["risk"]], "prerequisites": ["Actor control, prerequisites, feasibility, legality, ethics/risk and context applicability NOT_ASSESSED"],
            "evaluation": {"valence": "NOT_EVALUATED", "stakeholder": None, "criterion": None}},
        "outcomes": [], "evidenceAssessmentIds": [eid], "uncertainty": [spec["risk"]], "inferenceProvenance": None}
    ev = {**base(eid, family, spec["status"]), "assertion": {"objectType": "EFFECT_ASSERTION", "objectId": spec["id"]},
        "sourceFindings": findings, "synthesis": synthesis(spec, findings),
        "completeness": {k: "MISSING" if k in spec.get("incompleteFields", []) else "SPECIFIED" for k in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")}}
    return row, ev


def build(family):
    global STAMP
    if family not in p.FAMILIES:
        raise ValueError("Only authorized Psychological Families")
    p.check_protected()
    research = p.read(p.STORE / family / "research.json")
    STAMP = research.get("recordedAtTime", "2026-09-07T16:54:31Z")
    evidence = p.read(p.STORE / family / "evidence-inputs.json")
    w = ae.empty_workspace(family, p.BASELINE)
    c, sidecars = context(), []
    for spec in evidence["happeningTypes"]:
        w["passB"]["happeningTypes"].append(happening(spec, family))
    lookup = {f["key"]: f for f in evidence["findings"]}
    for spec in evidence["assertions"]:
        findings = [finding(lookup[k], spec["id"], family) for k in spec["findingKeys"]]
        for f in findings:
            ae.schema_set().validate("source-finding", f)
        if spec["type"] == "RELATIONSHIP":
            rel, ev, sidecar = relationship(spec, family, findings, c)
            w["passA"]["relationshipCandidates"].append(rel)
            w["passA"]["evidence"].append(ev)
            sidecars.append(sidecar)
        else:
            eff, ev = effect(spec, family, findings)
            w["passB"]["effectAssertions"].append(eff)
            w["passB"]["evidenceAssessments"].append(ev)
    registry = p.read(p.STORE / "relationship-review-registry.json")
    for review in research["existingReviews"]:
        current = registry[review["id"]]
        if current["processingFamilyId"] != family:
            raise ValueError("Do not duplicate another Family's primary review")
        current.update(primaryDisposition=review["disposition"], reviewStatus="REVIEWED_CANDIDATE_RECOMMENDATION", review=review)
        w["passA"]["existingDispositions"].append({"id": "AUDIT-" + review["id"], "questionOrDisposition": review["disposition"],
            "ownerFamilyId": current["ownerFamilyId"], "consultedFamilyIds": current["endpointFamilyIds"], "recordIds": [review["id"]],
            "rationale": review["rationale"], "status": "RESEARCH_NEEDED" if review["proposal"] or review["evidence"] == "INSUFFICIENT" else "REVIEW_READY"})
    for question in research["hypotheses"]:
        w["passA"]["gapQuestions"].append({"id": question["id"], "questionOrDisposition": question["question"],
            "ownerFamilyId": family, "consultedFamilyIds": [], "recordIds": [i for i in (question["source"],question["target"]) if i],
            "rationale": question["reason"], "status": question["status"]})
    w["readiness"] = dict.fromkeys(w["readiness"], True)
    ae.validate_workspace(w, c)
    p.write(p.STORE / family / "workspace.json", w)
    p.write(p.STORE / family / "relationship-evidence-sidecars.json", sidecars)
    p.write(p.STORE / "relationship-review-registry.json", registry)
    print({"family": family, "relationshipCandidates": len(w["passA"]["relationshipCandidates"]),
           "happeningTypes": len(w["passB"]["happeningTypes"]), "effectAssertions": len(w["passB"]["effectAssertions"]),
           "productionEligible": False, "complete": False})


PROPERTIES = ["LEVEL", "VARIABILITY", "RATE", "THRESHOLD", "TIMING", "PERSISTENCE", "RELATIONSHIP_STRENGTH",
              "RELATIONSHIP_DIRECTION", "ENABLEMENT", "FUNCTIONAL_SHAPE", "STRUCTURE"]


def normalize_title(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def validate_sources():
    sources = p.read(p.STORE / "candidate-source-registry.json")
    canonical = ae.read(p.ROOT / "data/sources.json")["sources"] + ae.read(p.ROOT / "data/relationship-intervention-v1/source-register.json")["sources"]
    seen = set()
    for s in sources:
        key = s["doi"].lower()
        if key in seen:
            raise ValueError("Duplicate Layer DOI: " + key)
        seen.add(key)
        for c in canonical:
            if c["id"] == s["id"]:
                continue  # Exact canonical reuse; supplemental registry also indexes researched existing sources.
            text = p.encode(c).lower()
            title = c.get("title", c.get("citationText", ""))
            if key in text or (s.get("pmid") and "pubmed.ncbi.nlm.nih.gov/" + s["pmid"] in text) or normalize_title(s["title"]) in normalize_title(title):
                raise ValueError("Use existing canonical source, not duplicate: " + s["id"] + "/" + c["id"])
    return len(sources)


def render_source_queue():
    """A future human-review queue, never a canonical registration request."""
    uses = {}
    for family in p.FAMILIES:
        path = p.STORE / family / "evidence-inputs.json"
        if not path.exists():
            continue
        data = p.read(path)
        findings = {f['key']: f for f in data['findings']}
        for assertion in data['assertions']:
            for key in assertion['findingKeys']:
                uses.setdefault(findings[key]['sourceId'], set()).add(assertion['id'])
        for identity in data['happeningTypes']:
            for source in identity['sources']:
                uses.setdefault(source, set()).add(identity['id'])
    queue = [{"candidateSourceId": s['id'], "candidateAssertionOrIdentityIds": sorted(uses.get(s['id'], [])),
              "canonicalRegistrationAuthorized": False, "humanDecision": DECISION,
              "disposition": "FUTURE_REVIEW_IF_SCIENCE_APPROVED" if uses.get(s['id']) else "RESEARCH_BACKGROUND_ONLY_NOT_QUEUED"}
             for s in p.read(p.STORE / 'candidate-source-registry.json') if s['id'].startswith('SRC-CAND-')]
    p.write(p.STORE / 'source-registration-candidate-queue.json', queue)


def render(family):
    """Generate local documents/registries; does not mark a Family complete."""
    validate_sources()
    build(family)
    research = p.read(p.STORE / family / "research.json")
    coverage = p.read(p.STORE / family / "coverage-review.json")
    inputs = p.read(p.STORE / family / "evidence-inputs.json")
    frozen = p.read(p.STORE / family / "BASELINE.json")
    w = p.read(p.STORE / family / "workspace.json")
    registry = p.read(p.STORE / "relationship-review-registry.json")
    canonical = {e["id"]: e for e in frozen["entities"]}
    if {e["id"] for e in research["entityReviews"]} != canonical.keys():
        raise ValueError("Incomplete entity reviews")
    if {e["driverId"] for e in coverage["driverLedgers"]} != {i for i,e in canonical.items() if e["entityType"] == "DRIVER"}:
        raise ValueError("Incomplete Driver search ledgers")
    incident = [v for v in registry.values() if family in v["psychologicalFamilyIds"]]
    if any(v["primaryDisposition"] is None for v in incident):
        raise ValueError("Existing incident proposition not yet reviewed")
    ledgers = []
    for entry in coverage["driverLedgers"]:
        row = copy.deepcopy(entry)
        row["originLayerSearch"] = {layer: {"outcome": "INSUFFICIENT_EVIDENCE" if layer in row["originsWithRelevantLiterature"] else "NOT_INVESTIGATED",
            "considered": True, "rationale": reason, "exactDriverLimit": row["noFinding"]} for layer,reason in coverage["layersConsidered"].items()}
        row["domainSearch"] = {domain: {"outcome": "INSUFFICIENT_EVIDENCE" if domain in row["domainsWithRelevantLiterature"] else "NOT_INVESTIGATED",
            "considered": True, "rationale": reason, "exactDriverLimit": row["noFinding"]} for domain,reason in coverage["domainsConsidered"].items()}
        row["effectProperties"] = {prop: entry["properties"].get(prop, "NOT_APPLICABLE" if prop == "STRUCTURE" else "NOT_INVESTIGATED") for prop in PROPERTIES}
        row["scientificUseEligibility"] = row["modelEligibility"] = row["practitionerActionEligibility"] = False
        row["activationStatus"] = "NOT_ELIGIBLE"
        if row["candidateEffectIds"] and row["properties"].get("LEVEL") == "SUPPORTED_EFFECT":
            for layer in row.get("supportedOriginLayers", ["INF"]):
                row["originLayerSearch"][layer]["outcome"] = "SUPPORTED_EFFECT"
            for domain in row.get("supportedDomains", ["DELIBERATE_INTERVENTION", "INFORMATIONAL_EXPOSURE"]):
                row["domainSearch"][domain]["outcome"] = "SUPPORTED_EFFECT"
        ledgers.append(row)
    edge_ledgers = [{"relationshipId": r["id"], "reviewedAfterPassA": True,
        "properties": {prop: "INSUFFICIENT_EVIDENCE" if prop in {"RELATIONSHIP_STRENGTH", "RELATIONSHIP_DIRECTION", "ENABLEMENT", "FUNCTIONAL_SHAPE", "STRUCTURE"} else "NOT_INVESTIGATED" for prop in PROPERTIES},
        "candidateEffectIds": [], "rationale": coverage["relationshipPropertyReview"]} for r in incident]
    p.write(p.STORE / family / "actions-events-search-ledger.json", {"drivers": ledgers, "relationships": edge_ledgers})
    # Upsert once by stable identity, permitting deterministic regeneration but no
    # second Family authoring conflicting copies of the same proposition.
    cr = p.read(p.STORE / "candidate-proposition-registry.json")
    for spec in inputs["assertions"]:
        old = next((r for r in cr if r["id"] == spec["id"]), None)
        semantic_key = [spec.get("source", spec.get("typeId")), spec["type"], spec["target"], spec["scope"]]
        if any(r["semanticKey"] == semantic_key and r["id"] != spec["id"] for r in cr):
            raise ValueError("Duplicate scientific proposition")
        row = {"id": spec["id"], "familyWorkspace": family, "semanticKey": semantic_key,
            "ownerFamilyId": spec.get("ownerFamilyId", family), "consultedFamilyIds": spec.get("consultedFamilyIds", [family]),
            "consultationStatus": "CANDIDATE_REVIEW_ONLY_HUMAN_PENDING", "sharedContributionId": spec["sharedContributionId"],
            "activationStatus": "NOT_ELIGIBLE", "humanDecision": DECISION}
        if old and old["familyWorkspace"] != family:
            raise ValueError("Cross-Family candidate collision")
        if old: cr.remove(old)
        cr.append(row)
    p.write(p.STORE / "candidate-proposition-registry.json", sorted(cr, key=lambda x:x["id"]))
    identities = p.read(p.STORE / "actions-events-identity-registry.json")
    existing = ae.read(ae.DATA)["happeningTypes"] + ae.source_catalog()["INTERVENTION"]
    for spec in inputs["happeningTypes"]:
        if any(normalize_title(spec["name"]) == normalize_title(t.get("name", t.get("canonicalName", ""))) for t in existing):
            raise ValueError("Existing production identity must be reused")
        old = next((r for r in identities if r["id"] == spec["id"]), None)
        if any(r["identityKey"] == spec["identityKey"] and r["id"] != spec["id"] for r in identities):
            raise ValueError("Layer action identity duplicate")
        if old: identities.remove(old)
        identities.append({"id": spec["id"], "identityKey": spec["identityKey"], "familyWorkspace": family,
            "name": spec["name"], "comparedProductionIdentityIds": sorted(t["id"] for t in existing),
            "manualIdentityReview": "No material operation match among current production identities; target/outcome differences were not used to mint duplicates",
            "activationStatus": "NOT_ELIGIBLE"})
    p.write(p.STORE / "actions-events-identity-registry.json", sorted(identities,key=lambda x:x["id"]))
    p.write(p.STORE / family / "revision-proposals.json", [{"id": "PROPOSAL-"+r["id"], "existingId": r["id"],
        "proposal": r["proposal"], "governance": governance("PROPOSAL-"+r["id"], family, "RESEARCH_NEEDED"),
        "implementationAuthorized": False, "humanDecision": DECISION} for r in research["existingReviews"] if r["proposal"]])
    doc = p.DOCS / family
    header = [f"# {family} — {frozen['family']['name']}", "", f"Audit `{research['auditId']}`; frozen main `{p.BASELINE}`.", "",
              "Candidate research only. Human decisions pending. No production science changed.", ""]
    p.write(doc / "README.md", "\n".join(header + ["See [entity review](ENTITY_REVIEW.md), [existing audit](EXISTING_RELATIONSHIP_AUDIT.md),", "[evidence](EVIDENCE_SUMMARY.md) and [decision package](GOVERNANCE_DECISION_PACKAGE.md).", "", "Machine-readable source of truth is the corresponding Layer candidate Family directory.", ""]))
    lines = header + ["## Complete entity review", "", coverage["entityFieldPolicy"], "", coverage["rdsReview"], ""]
    for review in research["entityReviews"]:
        e = canonical[review["id"]]
        lines += [f"### {e['id']} — {e['name']}", "", "Canonical snapshot (including all available fields):", "", "```json", p.encode(e).strip(), "```", ""]
        lines += [review[k] + "\n" for k in ("constructReview", "measurementReview", "timeReview", "unresolved")]
        lines += ["Boundary references: " + ", ".join(review["boundaryLinks"]) + ". Sources: " + ", ".join(review["sources"]) + ".", ""]
    p.write(doc / "ENTITY_REVIEW.md", "\n".join(lines))
    endpoint_gate = "All F01 endpoints are Drivers: STANDARD_CAUSAL; no RDS formula input." if family == "PSY-F01" else coverage["causalGateReview"]
    lines = header + ["## Existing propositions — one Layer review per ID", "", "All current endpoints, semantics, legacy directness, population/context, lag, persistence, exposure, moderators and sources remain unchanged in BASELINE.json. " + endpoint_gate + " Null legacy fields stay null. Recommendations do not change V1 executability.", ""]
    for r in incident:
        rev = r["review"]
        lines += [f"### {r['id']} — {r['primaryDisposition']}", "", f"Owner {r['ownerFamilyId']}; endpoints {', '.join(p.endpoints(r['frozenRecord']))}; Families {', '.join(r['endpointFamilyIds'])}.", "",
                  rev["rationale"], "", "Contrary/limitations: " + rev["nullContrary"], "", "Evidence " + rev["evidence"] + "/" + rev["strength"] + "/" + rev["confidence"] + "; sources " + ", ".join(rev["sources"]) + ".", "",
                  "Proposal: " + (rev["proposal"] or "None; no existing proposition altered."), "", DECISION, ""]
    p.write(doc / "EXISTING_RELATIONSHIP_AUDIT.md", "\n".join(lines))
    discovery_note = "H01's formal candidate is separately scoped in evidence-inputs.json; do not vote twice on its discovery and resulting record." if family == "PSY-F01" else "Discovery paths linking an assertion are not additional propositions; do not count or approve them twice."
    lines = header + ["## Hypothesis funnel", "", "Every hypothesis below is a research disposition, not a governed lifecycle rejection. " + discovery_note, "", "| ID | Semantics | Disposition | Question / rationale |", "|---|---|---|---|"]
    lines += [f"| {h['id']} | {h['semantics']} | {h['status']} | {h['question']} {h['reason']} |" for h in research["hypotheses"]]
    lines += ["", "No formal moderation, pathway, semantic, temporal, compositional or derivational record met the current evidence/representation threshold. Qualified-state transitions are not transformations of one psychological construct into another.", ""]
    p.write(doc / "RELATIONSHIP_RESEARCH.md", "\n".join(lines))
    p.write(doc / "REJECTIONS_RESEARCH_NEEDED.md", "\n".join(header + ["See [single hypothesis funnel](RELATIONSHIP_RESEARCH.md). Rejections, research-needed and blocked hypotheses are retained there without duplicated scientific propositions.", ""]))
    lines = header + ["## Driver action/event search", "", coverage["propertyPolicy"], "", "All eight origins and nine domains were considered; NOT_INVESTIGATED marks no exact Driver-specific evidence extraction in that cell, not an assertion of no possible effect. The bounded Family search is complete only when reviewed at closeout.", ""]
    for row in ledgers:
        lines += [f"### {row['driverId']}", "", row["noFinding"], "", "Gaps: " + row["gaps"], "", "Effects: " + (", ".join(row["candidateEffectIds"]) or "None retained") + ".", "", row["qualifiers"], "", "| Property | Search outcome |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k,v in row["effectProperties"].items()] + [""]
    lines += ["## Exact-edge effects", "", coverage["relationshipPropertyReview"], "", "No actor/context assessment grants practitioner eligibility. Model eligibility remains false; no numerical execution contract.", ""]
    p.write(doc / "ACTIONS_EVENTS_RESEARCH.md", "\n".join(lines))
    lines = header + ["## Source findings before synthesis", "", "Access depths below are extraction limits, not claims to have reviewed every page. Canonical bibliography-only records are not counted as evidence-extracted sources.", ""]
    for finding_input in inputs["findings"]:
        lines += [f"### {finding_input['key']} — {finding_input['sourceId']}", "", f"{finding_input['accessDepth']}; {finding_input['basis']}; {finding_input['disposition']}.", "", finding_input["locator"], "", finding_input["result"], "", finding_input["limitations"], ""]
    for spec in inputs["assertions"]:
        lines += [f"### {spec['id']}", "", f"{spec['disposition']} / {spec['strength']} / {spec['confidence']} — {spec['status']} + NOT_ELIGIBLE.", "", spec["scope"], "", spec["rationale"], ""]
    lines += ["## Canonical source alignment", "", "| Source | Actual access | Status | Finding |", "|---|---|---|---|"]
    lines += [f"| [{r['id']}]({r['url']}) | {r['access']} | {r['status']} | {r['finding']} |" for r in research["canonicalSourceReviews"]]
    lines += ["", "Supplemental bibliography: shared candidate-source-registry.json. No canonical registration.", ""]
    p.write(doc / "EVIDENCE_SUMMARY.md", "\n".join(lines))
    lines = header + [research["researchDepth"], ""]
    for query in research["searchLog"]:
        lines += [f"## {query['id']} — {query['stage']} ({query['date']})", "", *["- " + q for q in query["queries"]], "", query["depth"], ""]
    lines += ["## Skeptical second pass", "", coverage["skepticalReview"]["method"], "", *["- " + t for t in coverage["skepticalReview"]["checks"]], "", coverage["skepticalReview"]["remainingRisks"], ""]
    p.write(doc / "RESEARCH_LOG.md", "\n".join(lines))
    lines = header + ["## Human decision package", "", "Existing-edge records and proposals are not implemented. Scientific approval requires a separate human decision; passing validation is not evidence approval.", "", "| Group | ID | Recommendation | Evidence / confidence | Key risk | Human decision |", "|---|---|---|---|---|---|"]
    for r in incident:
        rev=r["review"]
        lines.append(f"| Existing | {r['id']} | {rev['disposition']} | {rev['evidence']} / {rev['strength']} / {rev['confidence']} | {rev['rationale']} | {DECISION} |")
    for s in inputs["assertions"]:
        lines.append(f"| {s['type']} | {s['id']} | {s['status']} | {s['disposition']} / {s['strength']} / {s['confidence']} | {s['scope']} | {DECISION} |")
    for s in inputs["happeningTypes"]:
        lines.append(f"| Identity only | {s['id']} | REVIEW_READY | Operation provenance, not efficacy | {s['constraints']} | {DECISION} |")
    for h in research["hypotheses"]:
        lines.append(f"| Hypothesis | {h['id']} | {h['status']} | No formal assertion unless separately listed | {h['reason']} | {DECISION} |")
    lines += ["", "Exact targets, owners, sources, supporting/null/contrary findings and boundaries resolve through the structured workspace, Layer candidate registry and linked local evidence/research reports. Do not interpret two descriptions sharing a contribution as two causal inputs.", ""]
    p.write(doc / "GOVERNANCE_DECISION_PACKAGE.md", "\n".join(lines))
    manifest = {"programId": p.PROGRAM, "familyId": family, "baselineCommit": p.BASELINE,
        "entitiesReviewed": len(canonical), "driversSearched": len(ledgers), "existingIncidentReviewed": len(incident),
        "dispositions": dict(Counter(r["primaryDisposition"] for r in incident)), "newRelationships": len(w["passA"]["relationshipCandidates"]),
        "happeningTypes": len(w["passB"]["happeningTypes"]), "effectAssertions": len(w["passB"]["effectAssertions"]),
        "evidenceAssessments": len(inputs["assertions"]), "sourceFindings": sum(len(a["findingKeys"]) for a in inputs["assertions"]),
        "supplementalSourcesInFamily": len([s for s in p.read(p.STORE / "candidate-source-registry.json") if family in s["families"] and s["id"].startswith("SRC-CAND-")]),
        "newGoverned": 0, "newActive": 0, "humanGovernance": "PENDING", "localComplete": research["status"] == "LOCAL_COMPLETE",
        "layerReconciliation": "PENDING", "protectedComparison": p.check_protected()}
    p.write(p.STORE / family / "AUDIT_MANIFEST.json", manifest)
    p.write(doc / "AUDIT_MANIFEST.json", manifest)
    p.write(doc / "COMPLETENESS_REPORT.md", "\n".join(header + ["```json", p.encode(manifest).strip(), "```", "", "Local completion must be separately validated; shared boundary questions remain pending for later endpoint Family consultation and final Layer reconciliation. Coverage is not scientific completeness.", ""]))
    render_source_queue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    render(args.family) if args.render else build(args.family)
