"""Fictional structural fixtures only. Never scientific knowledge or authority."""
import copy
import json
import actions_events_v1 as ae


def provenance():
    return {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Fictional structural fixture",
            "recordedAt": "2026-09-06T00:00:00Z", "originReferences": ["SYN-FIXTURE-ONLY"],
            "limitations": ["SYNTHETIC / NON_PRODUCTION; no empirical or real scientific claim"]}


def governance(identifier):
    previous = {"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}
    transitions = []
    for status in ("CANDIDATE", "RESEARCH_NEEDED", "REVIEW_READY"):
        after = {"lifecycleStatus": status, "activationStatus": "NOT_ELIGIBLE"}
        transitions.append({"fromState": previous, "toState": after,
                            "actorClass": "AUTOMATED_PROCESS_OR_AI", "rationale": "Synthetic workflow only",
                            "timestamp": "2026-09-06T00:00:00Z", "objectId": identifier, "revision": 1,
                            "provenance": "SYN-FIXTURE-ONLY", "governanceDecisionRecord": None,
                            "exactDecisionMaterialization": False})
        previous = after
    return {"lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE", "blockStatus": "NONE",
            "decisionOutcome": "NOT_DECIDED", "authorityBasis": "V1_NATIVE", "decisionRecord": None,
            "authorizedBy": None, "decisionDate": None, "effectiveVersion": None, "decisionRationale": None,
            "supersedesIds": [], "transitionProvenance": transitions}


def base(identifier):
    return {"schemaVersion": "1.0.0", "id": identifier, "revision": 1,
            "recordClass": ae.SYNTHETIC, "provenance": provenance(), "governance": governance(identifier)}


def make_active(catalog):
    """Build a distinct fictional active-state simulation; no real status changes."""
    result = copy.deepcopy(catalog)
    for row in ae.all_records(result):
        g = row["governance"]
        for status in ("INACTIVE", "ACTIVE"):
            before = {"lifecycleStatus": g["lifecycleStatus"], "activationStatus": g["activationStatus"]}
            after = {"lifecycleStatus": "GOVERNED", "activationStatus": status}
            g["transitionProvenance"].append({"fromState": before, "toState": after,
                "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "rationale": "Fictional approval; never real authority",
                "timestamp": "2026-09-06T00:00:00Z", "objectId": row["id"], "revision": 1,
                "provenance": "SYN-FIXTURE-ONLY", "governanceDecisionRecord": "SYN-DECISION-001",
                "exactDecisionMaterialization": False})
            g.update(lifecycleStatus="GOVERNED", activationStatus=status)
        g.update(decisionOutcome="APPROVED", decisionRecord="SYN-DECISION-001", authorizedBy="SYNTHETIC authorized human governor",
                 decisionDate="2026-09-06", effectiveVersion="SYN-1", decisionRationale="Fictional simulation only")
    refresh_authorization(result)
    return result


def refresh_authorization(catalog):
    catalog["authorizations"] = [{"decisionId": "SYN-DECISION-001", "decisionRecord": "SYN-DECISION-001",
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "effectiveDate": "2026-09-06", "recordClass": ae.SYNTHETIC,
        "authorizedObjects": [{"id": r["id"], "revision": r["revision"], "recordHash": ae.digest(r)} for r in ae.all_records(catalog)]}]


def fixture(active=False):
    layers = ("BIO", "PSY", "SOC", "CUL", "ENV", "INS", "INF", "TEC")
    entities = {"SYN-DRIVER-" + l: {"id": "SYN-DRIVER-" + l, "entityType": "DRIVER", "layer": l,
                                   "primaryFamilyId": l + "-F-SYN"} for l in layers}
    entities["SYN-DRIVER-SOC2"] = {"id": "SYN-DRIVER-SOC2", "entityType": "DRIVER", "layer": "SOC", "primaryFamilyId": "SOC-F-SYN"}
    entities["SYN-RDS"] = {"id": "SYN-RDS", "entityType": "RELATIONAL_DERIVED_STATE", "layer": "BIO", "primaryFamilyId": "BIO-F-SYN"}
    edges = {"SYN-REL-001": {"id": "SYN-REL-001", "relationFamily": "CAUSAL", "sourceEntityId": "SYN-DRIVER-SOC",
                            "targetEntityId": "SYN-DRIVER-SOC2", "governance": {"lifecycleStatus": "GOVERNED", "activationStatus": "ACTIVE"}}}
    context = ae.Context(entities, edges, {"SYN-SOURCE-001", "SYN-SOURCE-002"}, synthetic=True)
    catalog = ae.empty_catalog()
    scope = {k: "SYNTHETIC closed laboratory universe" for k in ("population", "context", "boundaryConditions", "timing", "measurement")}
    profile = {k: None for k in ("timing", "doseIntensity", "duration", "frequency", "reach")}
    cases = [
        ("institutional scheduling", ["INS"], "BIO", "LEVEL", "INCREASE", True, "DELIBERATE_INTERVENTION"),
        ("environmental shock", ["ENV"], "INS", "VARIABILITY", "DESTABILIZE", False, "EXTERNAL_SHOCK"),
        ("technological outage", ["TEC"], "INF", "RATE", "DECELERATE", False, "TECHNOLOGICAL_CHANGE"),
        ("informational disclosure", ["INF"], "PSY", "THRESHOLD", "LOWER", True, "INFORMATIONAL_EXPOSURE"),
        ("network process", ["SOC"], "EDGE", "RELATIONSHIP_STRENGTH", "ATTENUATE", False, "SOCIAL_NETWORK_PROCESS"),
        ("gradual physiological process", ["BIO"], "BIO", "PERSISTENCE", "PROLONG", False, "BIOLOGICAL_PHYSIOLOGICAL_PROCESS"),
        ("cultural process", ["CUL"], "PSY", "TIMING", "LATER", False, "SOCIAL_NETWORK_PROCESS"),
        ("event changes moderator", ["PSY"], "EDGE", "RELATIONSHIP_DIRECTION", "STATE_DEPENDENT", True, "DELIBERATE_INTERVENTION"),
        ("institutional enablement", ["INS"], "TEC", "ENABLEMENT", "ENABLE", True, "INSTITUTIONAL_STRUCTURAL_CHANGE"),
        ("cyclic exposure", ["BIO", "ENV"], "BIO", "FUNCTIONAL_SHAPE", "CYCLIC", False, "ENVIRONMENTAL_EXPOSURE"),
        ("routine unintended configuration", ["TEC", "ENV"], "SOC", "STRUCTURE", "RECONFIGURE", False, "ROUTINE_UNINTENDED_ACTIVITY"),
    ]
    for i, (name, origins, target, prop, change, action, domain) in enumerate(cases, 1):
        suffix = f"{i:03}"
        tid, oid, eid, aid = [f"SYN-{kind}-{suffix}" for kind in ("TYPE", "OCC", "EFFECT", "EVIDENCE")]
        pattern = ["CYCLIC"] if i == 10 else ["GRADUAL", "CUMULATIVE"] if i == 6 else ["DISCRETE", "REPEATED"]
        catalog["happeningTypes"].append({**base(tid), "name": "SYNTHETIC " + name, "aliases": [], "identityKey": "SYN-IDENTITY-" + suffix,
            "description": "Fictional contract example only. Do not infer any real effect.",
            "kindTags": ["ACTION", "PROCESS"] if action else ["EVENT", "EXPOSURE", "PROCESS"],
            "domainTags": [domain], "originLayers": origins, "interventionSubset": action, "packageKind": "ATOMIC",
            "components": [], "componentEnumeration": "NOT_APPLICABLE", "actorOrSourceSystem": "SYN-SYSTEM",
            "intentionality": "DELIBERATE" if action else "NON_AGENTIC", "controlProfiles": [], "pattern": pattern,
            "identityDefiningProfile": copy.deepcopy(profile), "identitySourceIds": ["SYN-SOURCE-001"]})
        catalog["occurrences"].append({**base(oid), "typeId": tid, "episodeKey": "SYN-EPISODE-" + suffix,
            "epistemicStatus": "HYPOTHETICAL", "originLayers": origins, "actorsOrSourceSystems": ["SYN-SYSTEM"],
            "populationOrSystem": scope["population"], "placeOrSystem": "SYN-UNIVERSE", "timeWindow": "SYN-TIME", "scope": copy.deepcopy(scope),
            "boundary": {"system": "SYN-RECEIVING-SYSTEM", "position": "EXTERNAL", "causalExogeneity": "NOT_INFERRED_FROM_EXTERNALITY"},
            "intentionality": "DELIBERATE" if action else "NON_AGENTIC", "controlProfiles": [], "pattern": pattern,
            "exposureProfile": copy.deepcopy(profile), "evidenceAssessmentIds": []})
        is_edge = target == "EDGE"
        catalog["effectAssertions"].append({**base(eid), "typeId": tid, "occurrenceId": oid,
            "targetKind": "RELATIONSHIP" if is_edge else "DRIVER", "targetId": "SYN-REL-001" if is_edge else "SYN-DRIVER-" + target,
            "targetLayers": ["SOC"] if is_edge else [target], "claimSemantics": "MODERATION" if is_edge else "CAUSAL",
            "productionMethod": "SOURCE_EXTRACTION", "property": prop, "change": change, "otherSpecified": None,
            "intendedChange": change if action else None, "observedChange": change, "knowledgeStatus": "SUPPORTED_EFFECT",
            "scope": copy.deepcopy(scope), "exposureProfile": copy.deepcopy(profile), "mechanism": "SYNTHETIC mechanism, no real proposition",
            "mechanismStatus": "SPECIFIED", "mechanisticDriverIds": ["SYN-DRIVER-CUL"] if is_edge else [],
            "grounding": {"causalIdentificationRationale": "Fictional randomized universe", "derivationEntailed": "NO", "representedDriverId": None, "duplicatePropagationControl": None},
            "contribution": {"groupId": "SYN-CONTRIBUTION-" + suffix, "role": "PRIMARY", "relatedAssertionIds": [], "reconciliation": None},
            "moderatorLinks": [], "interaction": {"mode": "NONE", "otherEffectIds": [], "evidenceAssessmentIds": []},
            "qualifiers": {"reach": None, "distribution": None, "subgroups": [], "unintendedConsequences": [], "risks": ["Never use synthetic evidence for real decisions"], "prerequisites": [],
                "evaluation": {"valence": "NOT_EVALUATED", "stakeholder": None, "criterion": None}},
            "outcomes": [], "evidenceAssessmentIds": [aid], "uncertainty": ["Entire example fictional"], "inferenceProvenance": None})
        fid = "SYN-FINDING-" + suffix
        catalog["evidenceAssessments"].append({**base(aid), "assertion": {"objectType": "EFFECT_ASSERTION", "objectId": eid},
            "sourceFindings": [{"id": fid, "sourceId": "SYN-SOURCE-001", "locator": "Fictional passage, not a citation", "accessDepth": "SYNTHETIC",
                "population": scope["population"], "context": scope["context"], "basis": ["EXPERIMENTAL"], "supportedSemantics": ["MODERATION" if is_edge else "CAUSAL"],
                "inputRole": "DIRECT_FINDING", "design": "Fictional experimental design", "exposure": "Fictional input", "comparator": "Fictional contrast",
                "measurement": scope["measurement"], "timing": scope["timing"], "result": "Fictional supporting result", "disposition": "SUPPORTS",
                "quantitativeEstimate": None, "uncertainty": ["Synthetic"], "limitations": ["No real external validity"], "datasetIds": ["SYN-DATASET-001"],
                "overlapNotes": "Shared fictional dataset; never independent replication", "nullInterpretation": None, "provenance": provenance()}],
            "synthesis": {"sourceFindingIds": [fid], "disposition": "SUPPORTS", "evidenceStrength": "LIMITED", "confidence": "LOW",
                "rationale": "Fictional synthesis", "confidenceRationale": "Fixture only", "conflicts": [], "contraryEvidenceSearch": "ASSESSED",
                "generalizationLimits": ["No generalization outside synthetic universe"], "datasetOverlap": "All fixtures share fictional dataset unless explicitly separate"},
            "completeness": {k: "SPECIFIED" for k in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")}})
    modifier = catalog["effectAssertions"][7]
    direct = copy.deepcopy(modifier)
    direct.update(base("SYN-EFFECT-012"))
    direct.update(targetKind="DRIVER", targetId="SYN-DRIVER-CUL", targetLayers=["CUL"], claimSemantics="CAUSAL",
                  property="LEVEL", change="INCREASE", intendedChange="INCREASE", observedChange="INCREASE",
                  mechanisticDriverIds=[], evidenceAssessmentIds=["SYN-EVIDENCE-012"])
    direct["contribution"].update(role="PRIMARY", relatedAssertionIds=[modifier["id"]], reconciliation="One event-to-moderator contribution; edge description is non-additive")
    modifier["contribution"].update(role="DESCRIPTIVE_ONLY", relatedAssertionIds=[direct["id"]], reconciliation="Describes same contribution; never add to primary")
    modifier["moderatorLinks"] = [{"driverId": "SYN-DRIVER-CUL", "driverEffectId": direct["id"], "moderationRelationshipId": None, "stateOrRange": "Fictional qualified state"}]
    catalog["effectAssertions"].append(direct)
    evidence = copy.deepcopy(catalog["evidenceAssessments"][7])
    evidence.update(base("SYN-EVIDENCE-012"))
    evidence["assertion"]["objectId"] = direct["id"]
    finding = evidence["sourceFindings"][0]
    finding.update(id="SYN-FINDING-012", sourceId="SYN-SOURCE-002", supportedSemantics=["CAUSAL"], datasetIds=["SYN-DATASET-002"], overlapNotes="Separate fictional segment study")
    evidence["synthesis"]["sourceFindingIds"] = [finding["id"]]
    catalog["evidenceAssessments"].append(evidence)
    return (make_active(catalog) if active else catalog), context


def actor_context(effect):
    return {"effectId": effect["id"], "revision": effect["revision"], "actorId": "SYN-ACTOR",
            "population": effect["scope"]["population"], "context": effect["scope"]["context"],
            "control": {"actorId": "SYN-ACTOR", "extent": "PARTIAL", "capabilities": ["INITIATE"], "provenance": "SYN-CONTROL-ASSESSMENT"},
            "checks": {k: {"status": "ASSESSED_PASS", "rationale": "Fictional check", "provenance": "SYN-USE-ASSESSMENT"}
                       for k in ("prerequisites", "feasibility", "legalConstraints", "ethicalRiskConstraints", "applicability")}}


def report():
    candidate, context = fixture()
    active, _ = fixture(active=True)
    before = copy.deepcopy(active)
    validation = ae.validate_catalog(active, context)
    uses = [ae.use_eligibility(e["id"], active, context, actor_context(e)) for e in active["effectAssertions"]]
    return {"label": ae.SYNTHETIC, "candidateValidation": ae.validate_catalog(candidate, context, candidate=True),
            "hypotheticalActiveValidation": validation, "unchanged": before == active,
            "originLayers": sorted({l for t in active["happeningTypes"] for l in t["originLayers"]}),
            "effectProperties": sorted({e["property"] for e in active["effectAssertions"]}),
            "uses": uses, "newRealScientificRecords": 0, "realStatusChanges": 0}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
