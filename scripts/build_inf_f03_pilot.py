"""Render the explicitly authorized INF-F03 candidate audit; never production science.

No search, activation, source registration, or ontology mutation. Scientific judgments
are reviewed inputs in research.json, not inferred from degree or narrative fields.
"""
import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import actions_events_v1 as ae
import audit_family as af
import relationship_intervention_v1 as ri

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "data/candidates/actions-events-v1/INF-F03"
DOCS = ROOT / "docs/governance/pilots/INF-F03"
BASE = ROOT / "reports/actions-events-v1/INF-F03-pilot-baseline"
R = ae.read(STORE / "research.json")
AUDIT = R["auditId"]
STAMP = "2026-09-06T13:48:47Z"
DECISION = "PENDING — APPROVE / MODIFY / REJECT"


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def emit(path, value):
    path = path.resolve()
    if not any(path.is_relative_to(p.resolve()) for p in (STORE, DOCS)):
        raise ValueError("Pilot renderer may write only its own candidate/document directories")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n" if isinstance(value, str) else encode(value), encoding="utf-8", newline="\n")


def provenance():
    return {"actorClass": "AUTOMATED_PROCESS_OR_AI", "method": "Structured evidence search and candidate-only synthesis",
            "recordedAt": STAMP, "originReferences": [AUDIT, R["baseline"], "research.json"],
            "limitations": ["No human scientific decision or activation; accessed sections only; not an exhaustive systematic review"]}


def governance(identifier, status="RESEARCH_NEEDED", blocked=False):
    previous = {"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}
    transitions = []
    states = ["CANDIDATE", "RESEARCH_NEEDED"] + (["REVIEW_READY"] if status == "REVIEW_READY" else [])
    for state in states:
        after = {"lifecycleStatus": state, "activationStatus": "NOT_ELIGIBLE"}
        transitions.append({"fromState": previous, "toState": after, "actorClass": "AUTOMATED_PROCESS_OR_AI",
            "rationale": "Prepared exact scope/evidence for human review" if state == "REVIEW_READY" else "Record audit question and evidence limitations",
            "timestamp": STAMP, "objectId": identifier, "revision": 1, "provenance": AUDIT,
            "governanceDecisionRecord": None, "exactDecisionMaterialization": False})
        previous = after
    return {"lifecycleStatus": status, "activationStatus": "NOT_ELIGIBLE",
        "blockStatus": "NEEDS_GOVERNANCE_INPUT" if blocked else "NONE", "decisionOutcome": "NOT_DECIDED",
        "authorityBasis": "V1_NATIVE", "decisionRecord": None, "authorizedBy": None, "decisionDate": None,
        "effectiveVersion": None, "decisionRationale": None, "supersedesIds": [], "transitionProvenance": transitions}


def base(identifier, status="RESEARCH_NEEDED"):
    return {"schemaVersion": "1.0.0", "id": identifier, "revision": 1, "recordClass": "SCIENTIFIC_RECORD",
            "provenance": provenance(), "governance": governance(identifier, status)}


def source_id(n):
    return "SRC-CAND-INF-F03-" + n


def finding(n, assertion_id):
    s = next(s for s in R["sources"] if s["id"] == source_id(n))
    result = {"id": "FND-" + assertion_id + "-" + n, "sourceId": s["id"], "locator": s["locator"],
        "accessDepth": s["accessDepth"], "population": s["population"], "context": s["exposure"],
        "basis": [s["basis"]], "supportedSemantics": ["CAUSAL"] if s["basis"] == "EXPERIMENTAL" else [],
        "inputRole": "DIRECT_FINDING", "design": s["basis"] + "; " + s["population"],
        "exposure": s["exposure"], "comparator": s["exposure"], "measurement": s["measurement"],
        "timing": "Within the reported task/assessment; no numeric causal lag or persistence inferred",
        "result": s["result"], "disposition": s["disposition"], "quantitativeEstimate": None,
        "uncertainty": ["No pooled effect size or quantitative precision inferred for this ontology assertion"],
        "limitations": [s["limitations"]], "datasetIds": ["STUDY-INF-F03-" + n],
        "overlapNotes": "Same publication reused for distinct claims is not independent replication; review-primary overlap unresolved",
        "nullInterpretation": None, "provenance": provenance()}
    if s["disposition"] == "NULL_FINDING":
        result["nullInterpretation"] = {"contrast": s["exposure"], "precisionAssessment": "No equivalence margin/precision conclusion extracted",
            "interpretation": "NO_DETECTED_DIFFERENCE", "rationale": "Ratio-based complexity nonsignificance is not a supported zero effect"}
    return result


def synthesis(findings, rationale, ready):
    return {"sourceFindingIds": [f["id"] for f in findings],
        "disposition": "MIXED" if ready and any(f["disposition"] in {"MIXED", "NULL_FINDING", "CONTRADICTED"} for f in findings) else "SUPPORTS" if ready else "INSUFFICIENT",
        "evidenceStrength": "MODERATE" if ready else "LIMITED", "confidence": "MODERATE" if ready else "LOW",
        "rationale": rationale, "confidenceRationale": "Confidence concerns the exact scoped assertion, not prose certainty or source prestige",
        "conflicts": [{"findingId": f["id"], "dispositionRationale": "Retained explicitly; exact-target support must be distinguished from other outcomes in the source"}
                      for f in findings if f["disposition"] in {"MIXED", "NULL_FINDING", "CONTRADICTED"}],
        "contraryEvidenceSearch": "ASSESSED", "generalizationLimits": ["No source-wide efficacy transfer; accessed sections only; no ontology-wide generalization"],
        "datasetOverlap": "Primary studies reused across assertions; SUP-013 synthesis may include SUP-002/003. No independent-replication count inferred."}


def relationship(spec, entities):
    identifier = "REL-CAND-INF-F03-" + spec["n"]
    schema = ae.read(ROOT / "schemas/relationship-intervention/v1/relationship-v1.schema.json")
    r = dict.fromkeys(schema["required"])
    r.update(schemaVersion="1.0.0", id=identifier, revision=1, relationFamily="CAUSAL", predicate="CAUSES",
        symmetry="DIRECTED", causalClaim=True, sourceEntityId=spec["source"], targetEntityId=spec["target"],
        sourceEntityType=entities[spec["source"]]["entityType"], targetEntityType=entities[spec["target"]]["entityType"],
        causalClaimRole="MODELED_LOCAL_LINK", polarity=spec["polarity"], mechanism=spec["mechanism"],
        boundaryConditions=spec["boundary"], applicability={"analyticUnit": "Specified message/exposure and recipient or producer",
            "populationOrSystem": spec["boundary"], "context": spec["boundary"]},
        causalReviewGate=ri.expected_causal_review_gate(entities[spec["source"]]["entityType"], entities[spec["target"]]["entityType"]),
        moderatorSpecifications=[], sourceIds=[source_id(n) for n in spec["sources"]],
        evidenceAssessmentIds=["EVA-" + identifier], governance=governance(identifier, spec["status"]),
        compatibility={"sourceSchema": "RELATIONSHIP_V1", "authorityStatus": "V1_LIFECYCLE",
            "migrationCompleteness": "INCOMPLETE", "v1Executability": "NOT_EXECUTABLE",
            "blockedFields": ["humanScientificGovernance", "activation", "quantitativeExecutionNotAuthorized"] + ([] if spec["status"] == "REVIEW_READY" else ["exactConstructAlignment"]),
            "legacyRelationFamily": None, "legacyScientificFields": None, "legacyRecordHash": None, "legacyRecord": None})
    fs = [finding(n, identifier) for n in spec["sources"]]
    syn = synthesis(fs, spec["rationale"], spec["status"] == "REVIEW_READY")
    ev = {"schemaVersion": "1.0.0", "id": "EVA-" + identifier, "revision": 1,
        "assertion": {"objectType": "RELATIONSHIP", "objectId": identifier}, "sourceIds": r["sourceIds"],
        "evidenceRationale": spec["rationale"], "evidenceStrength": syn["evidenceStrength"], "confidence": syn["confidence"],
        "evidenceDisposition": syn["disposition"], "population": spec["boundary"], "context": spec["boundary"],
        "studyDesignCharacterizations": [{"designType": "SYNTHESIS" if f["basis"] == ["EVIDENCE_SYNTHESIS"] else f["basis"][0], "specification": f["design"]} for f in fs],
        "quantitativeEstimate": None, "uncertainty": ["No quantitative coefficient, lag, persistence or mediator inferred"],
        "conflictingEvidence": {"sourceIds": [f["sourceId"] for f in fs if f["disposition"] in {"MIXED", "NULL_FINDING", "CONTRADICTED"}], "summary": spec["rationale"]},
        "limitations": [f["limitations"][0] for f in fs], "reviewProvenance": {"createdAt": STAMP,
            "createdByActorClass": "AUTOMATED_PROCESS_OR_AI", "reviewedAt": None, "reviewedBy": None,
            "sourceSchema": "RI_V1_WITH_AE_SOURCE_FINDING_CANDIDATE_SIDECAR"}, "governance": governance("EVA-" + identifier, spec["status"])}
    sidecar = {"evidenceAssessmentId": ev["id"], "assertionId": identifier, "productionMethod": "SOURCE_SYNTHESIS",
        "sourceFindings": fs, "synthesis": syn, "governance": ev["governance"],
        "note": "Candidate-only normalization sidecar. RI evidence retained; AE assessment target enum is not extended."}
    return r, ev, sidecar


def action(spec):
    tid, eid, aid = [p + "-CAND-INF-F03-" + spec["n"] for p in ("HT", "EA", "EVA-AE")]
    profile = {k: None for k in ("timing", "doseIntensity", "duration", "frequency", "reach")}
    control = {"actorId": "ROLE-MESSAGE-EDITOR" if spec["action"] else "ROLE-EXPOSED-COMMUNICATOR",
        "extent": "PARTIAL" if spec["action"] else "UNKNOWN", "capabilities": ["INITIATE", "TUNE"] if spec["action"] else [],
        "population": spec["scope"], "context": spec["scope"], "conditions": "Proposed role only; no real actor capability, legal permission or feasibility certified",
        "provenance": provenance()}
    typ = {**base(tid, spec["status"]), "name": spec["name"], "aliases": [], "identityKey": "INF-F03-" + spec["n"],
        "description": spec["description"], "kindTags": ["ACTION"] if spec["action"] else ["EXPOSURE", "PROCESS"],
        "domainTags": [spec["domain"]], "originLayers": spec["origins"], "interventionSubset": spec["action"],
        "packageKind": "ATOMIC", "components": [], "componentEnumeration": "NOT_APPLICABLE",
        "actorOrSourceSystem": control["actorId"], "intentionality": "DELIBERATE" if spec["action"] else "UNKNOWN",
        "controlProfiles": [control], "pattern": ["DISCRETE"] if spec["action"] else ["CONTINUOUS"],
        "identityDefiningProfile": profile, "identitySourceIds": [source_id(n) for n in spec["sources"]]}
    fs = [finding(n, eid) for n in spec["sources"]]
    ready = spec["effectStatus"] == "REVIEW_READY"
    syn = synthesis(fs, "Scoped message-property manipulation only; downstream efficacy not inherited. " + spec["risk"], ready)
    scope = {"population": spec["scope"], "context": spec["scope"], "boundaryConditions": spec["risk"],
             "timing": "Compared message versions or reported exposure-task window; no numeric lag/persistence inferred",
             "measurement": "Specified target feature/profile, not a reader performance score; exact protocol needs human review"}
    effect = {**base(eid, spec["effectStatus"]), "typeId": tid, "occurrenceId": None, "targetKind": "DRIVER",
        "targetId": spec["target"], "targetLayers": ["INF"], "claimSemantics": "CAUSAL",
        "productionMethod": "SYNTHESIS" if ready else "HYPOTHESIS", "property": "LEVEL", "change": spec["change"],
        "otherSpecified": None, "intendedChange": spec["change"] if spec["action"] and ready else None,
        "observedChange": spec["change"] if ready else None, "knowledgeStatus": "SUPPORTED_EFFECT" if ready else "INSUFFICIENT_EVIDENCE",
        "scope": scope, "exposureProfile": copy.deepcopy(profile), "mechanism": spec["mechanism"],
        "mechanismStatus": "PARTIAL", "mechanisticDriverIds": [],
        "grounding": {"causalIdentificationRationale": "Controlled message construction supports only changed content features" if ready else "Exact target effect unresolved",
            "derivationEntailed": "NO", "representedDriverId": None, "duplicatePropagationControl": None},
        "contribution": {"groupId": "CONTRIB-INF-F03-" + spec["n"], "role": "PRIMARY", "relatedAssertionIds": [], "reconciliation": None},
        "moderatorLinks": [], "interaction": {"mode": "NONE", "otherEffectIds": [], "evidenceAssessmentIds": []},
        "qualifiers": {"reach": None, "distribution": None, "subgroups": [], "unintendedConsequences": [spec["risk"]],
            "risks": [spec["risk"]], "prerequisites": ["Exact text/exposure protocol; legitimate actor control; subject-matter review; applicability, feasibility, legal and ethical checks NOT_ASSESSED"],
            "evaluation": {"valence": "NOT_EVALUATED", "stakeholder": None, "criterion": None}},
        "outcomes": [], "evidenceAssessmentIds": [aid], "uncertainty": [spec["risk"]], "inferenceProvenance": None}
    evidence = {**base(aid, spec["effectStatus"]), "assertion": {"objectType": "EFFECT_ASSERTION", "objectId": eid},
        "sourceFindings": fs, "synthesis": syn,
        "completeness": {k: "SPECIFIED" for k in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")}}
    if not ready:
        evidence["completeness"]["direction"] = "MISSING"
    return typ, effect, evidence


def context():
    c = ae.Context.repository()
    return ae.Context(c.entities, c.relationships, c.source_ids | {s["id"] for s in R["sources"]})


def protected():
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", R["baseline"], "--", "data", "schemas", "_migration_handoff_v0.3", "scenario-service", "docs/governance/pilots/BIO-F01"], cwd=ROOT).decode().splitlines()
    result = {}
    for p in paths:
        original = subprocess.check_output(["git", "show", R["baseline"] + ":" + p], cwd=ROOT)
        current = (ROOT/p).read_bytes()
        # Git checkout EOLs are not scientific change; freeze raw bytes separately.
        normalized = lambda b: b.replace(b"\r\n", b"\n")
        result[p] = {"baselineBlobSha256": hashlib.sha256(normalized(original)).hexdigest(),
            "currentNormalizedSha256": hashlib.sha256(normalized(current)).hexdigest(),
            "currentRawSha256": hashlib.sha256(current).hexdigest(), "unchanged": normalized(original) == normalized(current)}
    return result


def build():
    c = context()
    baseline = ae.read(BASE / "INF-F03_baseline.json")
    members = set(baseline["family"]["memberIds"])
    legacy = ae.read(ROOT / "data/relationships.json")
    incident = [(bucket, row) for bucket in ("relationships", "deprecatedRelationships", "relationshipCandidates")
                for row in legacy[bucket] if row.get("subjectEntityId") in members or row.get("objectEntityId") in members]
    w = ae.empty_workspace("INF-F03", R["baseline"])
    # Readiness means understood and limitations recorded, NOT scientifically resolved.
    w["readiness"] = {k: True for k in w["readiness"]}
    sidecars = []
    for spec in R["relationshipCandidates"]:
        rel, ev, side = relationship(spec, c.entities)
        w["passA"]["relationshipCandidates"].append(rel)
        w["passA"]["evidence"].append(ev)
        sidecars.append(side)
        owner = af.ownership(spec["source"], spec["target"], "CAUSAL", c.entities)
        w["passA"]["ownership"].append({"id": "OWN-" + rel["id"], "questionOrDisposition": spec["proposition"],
            "ownerFamilyId": owner, "consultedFamilyIds": sorted({c.entities[x]["primaryFamilyId"] for x in (spec["source"], spec["target"])} - {owner}),
            "recordIds": [rel["id"]], "rationale": "Directed source-Family ownership; this pilot prepares but does not imply endpoint-Family consultation occurred", "status": spec["status"]})
    audits = []
    revisions = []
    registered = {s['id']: s for s in ae.read(ROOT/'data/sources.json')['sources']}
    for bucket, row in incident:
        entry = next((x for x in R["existing"] if x[0] == row["id"]), None)
        causal = row["relationFamily"] == "CAUSAL"
        disposition = entry[1] if entry else "retain as-is"
        projected = ri.project_v3_relationship(row)
        if bucket != "relationships":
            # The production adapter's input contract is the active V3 corpus.
            # Do not apply its assumed active authority to archived records.
            projected = None
        audit = {"id": row["id"], "bucket": bucket, "primaryDisposition": disposition,
            "governanceDecision": DECISION, "currentRecord": row, "currentV1Projection": projected,
            "assessment": entry[2:] if entry else ["Retain existing noncausal dependency or prior deprecation; no new proposition and no causal traversal"],
            "fieldReview": {k: {"recordedValue": v, "assessment": "Preserved; absent is not inferred" if v in (None, [], "UNSPECIFIED", "NOT_SPECIFIED") else "Read in current record; scope/source caveats govern interpretation"} for k, v in row.items()},
            "ownerFamilyId": c.entities[row["subjectEntityId"]]["primaryFamilyId"],
            "revisionIdentity": "New proposition ID required if endpoint/semantic identity changes; qualifier-only revision needs exact later human decision" if entry else "No identity change proposed",
            "executableInV1": False, "preserveV3Authority": True,
            "rdfCausalGate": ri.expected_causal_review_gate(row["subjectEntityType"], row["objectEntityType"]) if causal else None}
        audits.append(audit)
        if entry:
            # Evaluate the existing assertion without modifying or superseding it.
            evid = 'EVA-AUD-INF-F03-' + row['id']
            supplementary = {'REL-INF-006': ['008'], 'REL-INF-041': ['004','005'],
                'REL-INF-046': ['002','003','013']}.get(row['id'], [])
            fs = [finding(n, evid) for n in supplementary]
            for sid in row['supportingEvidenceIds']:
                src = registered[sid]
                fs.append({'id': 'FND-'+evid+'-'+sid, 'sourceId': sid, 'locator': src.get('href') or src.get('sourceUrl'),
                    'accessDepth': 'METADATA', 'population': None, 'context': 'Existing source-to-edge alignment audit',
                    'basis': ['EVIDENCE_SYNTHESIS'], 'supportedSemantics': [], 'inputRole': 'DIRECT_FINDING',
                    'design': 'Bibliographic/topic screening only; no direct-effect evidence asserted', 'exposure': None,
                    'comparator': None, 'measurement': None, 'timing': None, 'result': entry[4],
                    'disposition': 'INSUFFICIENT', 'quantitativeEstimate': None,
                    'uncertainty': ['Full source-to-proposition adequacy requires exact passages, not title matching'],
                    'limitations': ['Canonical citation is preserved; no new bibliographic authority or source registration'],
                    'datasetIds': [], 'overlapNotes': 'Do not treat review and primary studies as independent',
                    'nullInterpretation': None, 'provenance': provenance()})
            syn = synthesis(fs, entry[2]+' '+entry[4], False)
            ev = {'schemaVersion':'1.0.0','id':evid,'revision':1,
                'assertion':{'objectType':'RELATIONSHIP','objectId':row['id']},
                'sourceIds': sorted({f['sourceId'] for f in fs}), 'evidenceRationale': syn['rationale'],
                'evidenceStrength':'LIMITED','confidence':'LOW','evidenceDisposition':'INSUFFICIENT',
                'population':row.get('generalizabilityContext'), 'context':row.get('conditionsModerators'),
                'studyDesignCharacterizations':[{'designType':'OTHER_SPECIFIED','specification':'Candidate audit of source alignment; not a new supportive scientific assessment'}],
                'quantitativeEstimate':None,'uncertainty':['Current scientific authority is preserved; V1 completeness is separate'],
                'conflictingEvidence':{'sourceIds':sorted({f['sourceId'] for f in fs if f['disposition'] in {'MIXED','NULL_FINDING','CONTRADICTED'}}), 'summary':entry[2]},
                'limitations':[entry[4],entry[5]],'reviewProvenance':{'createdAt':STAMP,'createdByActorClass':'AUTOMATED_PROCESS_OR_AI',
                    'reviewedAt':None,'reviewedBy':None,'sourceSchema':'RI_V1_WITH_AE_SOURCE_FINDING_CANDIDATE_SIDECAR'},
                'governance':governance(evid)}
            w['passA']['evidence'].append(ev)
            sidecars.append({'evidenceAssessmentId':evid,'assertionId':row['id'],'sourceFindings':fs,
                'productionMethod':'SYNTHESIS','synthesis':syn,'governance':ev['governance'],
                'note':'Assessment of preserved existing assertion; no revision or approval materialized'})
            if disposition in {'revision candidate','retype candidate'}:
                rid = 'REV-CAND-INF-F03-' + row['id']
                revisions.append({'id':rid,'revision':1,'recordClass':'NON_GOVERNED_REVISION_PROPOSAL',
                    'currentRelationshipId':row['id'],'currentRecordHash':ae.digest(row),
                    'proposedDisposition':disposition,'proposedProposition':entry[3],
                    'proposedFields':{'sourceEntityId':row['subjectEntityId'],'targetEntityId':row['objectEntityId'],
                        'polarity':None,'boundaryConditions':entry[2],'mechanism':entry[3],
                        'causalClaimRole':None,'functionalForm':None,'causalLag':None,'persistence':None},
                    'notAReplacementRelationshipRecord':True,'sourceChanges':'Retain old source provenance; proposed assessment '+evid,
                    'evidenceAssessmentIds':[evid],'sourceIds':ev['sourceIds'],'rdsSafeguards':entry[5],
                    'endpointDecision': 'No endpoint silently substituted; alternate semantics/endpoint require exact later human proposition',
                    'identityPolicy':audit['revisionIdentity'],'unresolved':entry[2],
                    'governance':governance(rid,blocked=entry[6]),'governanceDecision':DECISION})
        w["passA"]["existingDispositions"].append({"id": "AUD-" + row["id"], "questionOrDisposition": disposition,
            "ownerFamilyId": audit["ownerFamilyId"], "consultedFamilyIds": [], "recordIds": [row["id"]],
            "rationale": entry[2] if entry else audit["assessment"][0], "status": "RESEARCH_NEEDED" if entry else "REVIEW_READY"})
    for h in R["hypotheses"]:
        item = {"id": "HYP-INF-F03-" + h[0], "questionOrDisposition": h[1], "ownerFamilyId": "INF-F03",
            "consultedFamilyIds": [], "recordIds": [], "rationale": h[4], "status": h[3]}
        w["passA"]["gapQuestions"].append(item)
        if h[3] in {"RESEARCH_NEEDED", "BLOCKED_NEEDS_GOVERNANCE_INPUT"}:
            w["passA"]["unresolved"].append(item)
    for spec in R["actions"]:
        typ, effect, evidence = action(spec)
        w["passB"]["happeningTypes"].append(typ)
        w["passB"]["effectAssertions"].append(effect)
        w["passB"]["evidenceAssessments"].append(evidence)
    ae.validate_workspace(w, c)
    findings = [f for s in sidecars for f in s["sourceFindings"]] + [f for e in w["passB"]["evidenceAssessments"] for f in e["sourceFindings"]]
    for f in findings:
        ae.schema_set().validate("source-finding", f)
    canonical = ae.read(ROOT / "data/sources.json")["sources"]
    source_queue = []
    for s in R["sources"]:
        needle = s["title"].casefold()
        matches = [v["id"] for v in canonical if needle in v.get("citationText", "").casefold() or
                   s["doi"] and s["doi"].casefold() in json.dumps(v).casefold() or s["url"] in json.dumps(v)]
        source_queue.append({**s, "canonicalDuplicateIds": matches, "registrationPerformed": False,
            "supportsAssertionIds": sorted({e["assertionId"] for e in sidecars if any(f["sourceId"] == s["id"] for f in e["sourceFindings"])} |
                                           {e["assertion"]["objectId"] for e in w["passB"]["evidenceAssessments"] if any(f["sourceId"] == s["id"] for f in e["sourceFindings"])}),
            "laterRegistrationGate": "Only after exact human approval; repeat identifier/title deduplication and full bibliographic verification"})
    ledgers = []
    vocab = ae.read(ROOT / "schemas/actions-events/v1/vocabulary.json")
    layer_queries = {"BIO": [10], "PSY": [6,8], "SOC": [12,16], "CUL": [15,24], "ENV": [11,18], "INS": [13,17,23], "INF": [1,4,5,7,14,19,20,21], "TEC": [9]}
    for driver in sorted(x for x in members if c.entities[x]["entityType"] == "DRIVER"):
        effects = [e for e in w["passB"]["effectAssertions"] if e["targetId"] == driver]
        supported_types = {e["typeId"] for e in effects if e["knowledgeStatus"] == "SUPPORTED_EFFECT"}
        supported_origins = {l for t in w["passB"]["happeningTypes"] if t["id"] in supported_types for l in t["originLayers"]}
        supported_domains = {d for t in w["passB"]["happeningTypes"] if t["id"] in supported_types for d in t["domainTags"]}
        ledgers.append({"driverId": driver, "completedSearchLedger": True, "scope": "Bounded structured search; no claim of exhaustive literature coverage",
            "queryIds": list(range(1, len(R["queries"])+1)), "effectIds": [e["id"] for e in effects],
            "originReview": [{"layer": l, "queryIds": qs, "status": "SUPPORTED_EFFECT" if l in supported_origins else "INSUFFICIENT_EVIDENCE",
                "note": "Search-screened origin route; affected reader is not changed message content. Candidate origin tags are hypotheses/scope, not a causal Layer graph."} for l, qs in layer_queries.items()],
            "domainReview": [{"domain": d, "status": "SUPPORTED_EFFECT" if d in supported_domains else "INSUFFICIENT_EVIDENCE", "rationale": "See screened query log and exact candidates; no blanket category efficacy. Ordinary production, shocks, policy and biological effects need content-level evidence."} for d in vocab["domainTags"]],
            "propertyReview": [{"property": p, "status": "SUPPORTED_EFFECT" if p == "LEVEL" and any(e["knowledgeStatus"] == "SUPPORTED_EFFECT" for e in effects) else "INSUFFICIENT_EVIDENCE",
                "rationale": "Scoped candidate only" if p == "LEVEL" else "Considered during search/synthesis; no exact target-specific estimate. Timing/reach/context are qualifiers, not established changes of this property."} for p in vocab["propertyChanges"]],
            "relationshipTargetedEffects": [], "noFindings": "No supported exact relationship-targeted effect, synergy, pathway, cyclic shape, persistence or threshold claim; unknown is not zero",
            "actionability": {k: False for k in ("scientificUseEligibility", "modelEligibility", "practitionerActionEligibility")}})
    files = protected()
    assert all(v["unchanged"] for v in files.values()), "Protected baseline changed"
    all_records = w["passA"]["relationshipCandidates"] + w["passA"]["evidence"] + ae.all_records(w["passB"]) + revisions
    inventory = ae.read(BASE / "inventory.json")
    active = [(b,r) for b,r in incident if b == "relationships"]
    def scope_bucket(row):
        a,b = (c.entities[row[k]]['primaryFamilyId'] for k in ('subjectEntityId','objectEntityId'))
        return 'INTERNAL' if a == b else 'SAME_LAYER_CROSS_FAMILY' if a[:3] == b[:3] else 'CROSS_LAYER'
    causal_edges = [e for e in inventory['edges'] if e['semanticType'] == 'CAUSAL']
    degrees = {x:{'in':sum(e['target']==x for e in causal_edges),'out':sum(e['source']==x for e in causal_edges)} for x in sorted(members)}
    signatures = [(e['source'],e['target'],e['predicate']) for e in inventory['edges']]
    canonical_reused = sorted({s for _,r in incident for s in r['supportingEvidenceIds']} | {s for x in members for s in c.entities[x]['keySources']})
    summary = {"auditId": AUDIT, "baselineCommit": R["baseline"], "date": R["date"],
        "schemaVersions": {"Driver": "1.1", "RDS": "0.1 + governed migration v0.3", "RelationshipV1": "1.0.0", "ActionsEventsV1": "1.0.0", "sources": "1.0"},
        "sourceRegisterSha256": files["data/sources.json"]["baselineBlobSha256"],
        "family": baseline["family"], "activeIncidentIds": [r["id"] for _,r in active],
        "deprecatedIncidentIds": [r["id"] for b,r in incident if b == "deprecatedRelationships"],
        "existingDispositions": dict(Counter(x["primaryDisposition"] for x in audits)),
        "productionCounts": {"drivers": len(ae.read(ROOT/"data/drivers.json")), "rds": len(ae.read(ROOT/"data/relational-derived-states.json")), "entities": len(c.entities), "activeRelationships": len(inventory["edges"]), "activeCausal": sum(e["semanticType"] == "CAUSAL" for e in inventory["edges"])},
        "newCounts": {"relationships": len(w["passA"]["relationshipCandidates"]), "revisionProposals":len(revisions), "happeningTypes": len(w["passB"]["happeningTypes"]), "effects": len(w["passB"]["effectAssertions"]), "evidenceAssessments": len(w["passA"]["evidence"])+len(w["passB"]["evidenceAssessments"]), "sourceFindings": len(findings), "supplementalSources": len(source_queue), "occurrences": 0, "moderation": 0, "pathways": 0},
        'canonicalSourcesReusedForAudit':canonical_reused, 'canonicalSourcesAdded':0,
        'graphMetrics':{'causalDegrees':degrees,'allActiveIncidentScopes':dict(Counter(scope_bucket(r) for _,r in active)),
            'activeSemanticCounts':dict(Counter(r['relationFamily'] for _,r in active)),
            'isolatedIds':[x for x,d in degrees.items() if d['in']+d['out']==0],
            'suspiciousHubs': [x for x,d in degrees.items() if d['in']+d['out']>=10],
            'hubFlagThreshold':'Recorded causal degree >=10; review flag only, no scientific threshold',
            'duplicateSignaturesIncident': [list(s) for s,n in Counter(signatures).items() if n>1 and (s[0] in members or s[1] in members)],
            'newGraphEdges':0,'candidateCrossLayer':len(R['relationshipCandidates'])},
        "lifecycleCounts": dict(Counter(r["governance"]["lifecycleStatus"] for r in all_records)),
        "newGoverned": 0, "newActive": 0, 'blockedRecordCount':sum(r['governance']['blockStatus']=='NEEDS_GOVERNANCE_INPUT' for r in all_records), "allActivationNotEligible": all(r["governance"]["activationStatus"] == "NOT_ELIGIBLE" for r in all_records),
        "hypothesisDispositions": dict(Counter(h[3] for h in R["hypotheses"])),
        "evidenceFindingDispositions": dict(Counter(f["disposition"] for f in findings)),
        "protectedFiles": {p: {k:v for k,v in checks.items() if k != "currentRawSha256"} for p,checks in files.items()},
        "workspaceHash": ae.digest(w), "candidateIds": [r["id"] for r in all_records],
        "noScientificHumanDecision": True, "governanceDecision": DECISION}
    emit(STORE/"workspace.json", w)
    emit(STORE/"relationship-source-findings.json", sidecars)
    emit(STORE/"source-registration-queue.json", source_queue)
    emit(STORE/"existing-relationship-audit.json", audits)
    emit(STORE/'revision-proposals.json',revisions)
    emit(STORE/"driver-search-ledger.json", ledgers)
    emit(DOCS/"INF_F03_AUDIT_MANIFEST.json", summary)
    render_docs(w, audits, sidecars, ledgers, summary, baseline)
    return summary


def render_docs(w, audits, sidecars, ledgers, summary, baseline):
    header = f"Audit {AUDIT}; frozen main `{R['baseline']}`. Candidate-only recommendations; no scientific approval or activation.\n\n"
    lines = ["# INF-F03 entity and RDS review\n\n", header,
        "All canonical fields, aliases/crosswalks and incident records are frozen in the [generalized baseline](../../../../reports/actions-events-v1/INF-F03-pilot-baseline/INF-F03_baseline.json). Nulls remain null.\n\n"]
    c = context()
    for identifier, note in R["entityFlags"].items():
        row = c.entities[identifier]
        lines += [f"## {identifier} — {row['name']}\n\n{note}\n\n", "```json\n" + encode(row) + "```\n\n"]
        if row["entityType"] == "RELATIONAL_DERIVED_STATE":
            lines += ["Derivation version: no per-record version identifier; freeze by baseline record hash, not an invented formula version. Calculation window is a scope requirement, not a supplied numeric window. Temporal and mechanistic independence of causal use are NOT_CONFIRMED. Uncertainty propagation remains as governed; operationalization is not selected.\n\n"]
    emit(DOCS/"INF_F03_ENTITY_RDS_REVIEW.md", "".join(lines))
    lines = ["# Existing relationship audit and exact revision proposals\n\n", header,
        "Every active and deprecated incident record has one primary disposition. Machine-readable current fields and their V1 projection are in `existing-relationship-audit.json`; projection is not a second proposition. No current candidate/native-inactive/deprecated V1 incident proposition was found outside these buckets.\n\n"]
    for a in audits:
        lines += [f"## {a['id']} — {a['primaryDisposition']}\n\n", f"Bucket: {a['bucket']}; owner {a['ownerFamilyId']}; decision **{DECISION}**.\n\n"]
        lines += [str(x) + "\n\n" for x in a["assessment"] if not isinstance(x,bool)]
        if a["primaryDisposition"] not in {"retain as-is", "retain but V1 incomplete"}:
            lines += ["Field-level proposal: replace unsupported universal interpretation with the exact qualification above; preserve endpoints pending named construct decision; replace/add evidence only after human source registration and adjudication. Lag, persistence, exposure and functional form remain unspecified; no inferred numeric or mediator content. " + a["revisionIdentity"] + ". Status RESEARCH_NEEDED / NOT_ELIGIBLE; no supersession.\n\n"]
    emit(DOCS/"INF_F03_EXISTING_RELATIONSHIP_AUDIT.md", "".join(lines))
    lines = ["# Evidence and source summary\n\n", header,
        "Source findings precede synthesis. RI evidence uses a candidate-only AE SourceFinding sidecar because the AE EvidenceAssessment enum does not include Relationship. Production schemas are unchanged. Candidate sources enter only a transient validation context; they are not canonical registration.\n\n",
        "Primary search systems: public web search, PubMed abstracts, publisher pages, author/institutional repositories. Review depth is recorded per source. Some PubMed pages returned CAPTCHA/empty text; publisher/author alternatives were used without bypass. The meta-analysis full text was restricted. Numeric estimates are deliberately null when no exact comparable estimand was extracted.\n\n"]
    for s in R["sources"]:
        lines += [f"## {s['id']}\n\n[{s['title']}]({s['url']}) — {s['authors']}; {s['year']}; {s['venue']}. DOI: {s['doi'] or 'not verified; durable URL retained'}. Access: {s['accessDepth']}, {s['locator']}.\n\n{s['result']} {s['limitations']}\n\n"]
    lines += ["## Existing source alignment\n\n",
        "Canonical references were reused for audit provenance, not counted as direct new evidence. SRC-425/426 discuss risk presentation, not an independent readability-fit effect. SRC-428 is an uncertainty review. SRC-429's register label names Kasperson, while its linked article identifies Balog-Way, McComas and Besley: correction requires later source governance. SRC-444 lists Hollands first; the linked article lists Carter first (Hollands is a coauthor). SRC-496 (COM-B), SRC-498 (cultural tightness), SRC-505 (misinformation synthesis), SRC-512/513 (NIST frameworks), and SRC-515 (RDoC assessment) cannot substitute for direct endpoint evidence. No register entry was repaired.\n\n",
        "Null/mixed evidence: ambiguity advantage under superficial questions; noise quantity versus ratio-complexity divergence; small/null numeric-disclosure source-trust effects; context-dependent syntax effects; sleep-loss role reversal and null speech results; automated simplification information loss. Shared datasets/review inclusion are not independent replications.\n"]
    emit(DOCS/"INF_F03_EVIDENCE_SUMMARY.md", "".join(lines))
    lines = ["# Structured research log\n\n", header,
        "Search date 2026-09-06. This is a bounded structured evidence audit, not a formal systematic review. Questions were grouped; one query may cover multiple Drivers. Search-screened records not extracted into the source queue are not counted as reviewed scientific evidence.\n\n"]
    for i,q in enumerate(R["queries"],1):
        lines.append(f"- Q{i:02}: `{q}` — public web search with primary-source selection; source inclusion judged against exact target definition, not generic usefulness.\n")
    lines += ["\n## Screened but not promoted\n\n",
        "Crisis-language observational paper (npj Digital Medicine, s41746-021-00554-w): possible association, full construct/confounding extraction deferred. High/low-context advertising (10.1080/08911762.2017.1296985): perceived complexity is not objective message complexity. Plain Writing Act implementation pages: establish policy, not compliance/effects. Model/network studies: model basis only. Recent broad health/AI communication results: screen only, no verified exact-effect promotion. No private/paid search or full-text access claimed.\n\n",
        "## Pass B readiness and coverage\n\nMembership, definitions and incident dispositions were reviewed first. RDS input structures are understood but operational versions remain unresolved; this permits scoped Driver research, not RDS execution. The four Driver ledgers explicitly consider eight origins, nine domains and eleven properties. Only LEVEL claims are represented; remaining cells are insufficient evidence, not zero. Grouped screening does not establish that every possible study was retrieved.\n\n",
        "Origins searched: BIO sleep/production; PSY processing/capacity; SOC transmission/network; CUL uncertainty/cultural context; ENV noise/shocks; INS laws/policy/economic communication; INF wording/disclosure; TEC rewriting/display. Relationship-modification routes examined for REL-INF-041/046/TEC-060; exact moderated evidence/linkage insufficient. No inferred pathway, moderation or real Occurrence was created.\n"]
    emit(DOCS/"INF_F03_RESEARCH_LOG.md", "".join(lines))
    lines = ["# Human governance decision package\n\n", header,
        "No row is approved. REVIEW_READY means prepared for review, not completeness, executability or authority. Read the evidence source-level limitations before adjudication.\n\n",
        "## A–B. Existing propositions\n\nSee [exact existing-edge audit](INF_F03_EXISTING_RELATIONSHIP_AUDIT.md). Each record has one disposition and PENDING field. Prior deprecated records remain excluded.\n\n",
        "## C. New causal candidates\n\n"]
    for s in R["relationshipCandidates"]:
        lines += [f"### REL-CAND-INF-F03-{s['n']} — {s['status']}\n\n{s['proposition']}\n\n{s['rationale']}\n\nBoundaries: {s['boundary']} Sources: {', '.join(source_id(n) for n in s['sources'])}. Risk if approved incorrectly: proxy/construct mismatch or scope-generalized causal propagation. Evidence/confidence: {'MODERATE/MODERATE' if s['status']=='REVIEW_READY' else 'LIMITED/LOW'}. Recommendation: {'review bounded causal proposition' if s['status']=='REVIEW_READY' else 'retain research-needed'}. **{DECISION}**\n\n"]
    lines += ["## D–F. Noncausal, moderation and pathways\n\nNo new formal record met exact operationalization/edge/pathway requirements. See H07–H09/H13/H16/H17; none are silently treated as edges. **" + DECISION + "**\n\n", "## G–H. Actions & Events identities and effects\n\n"]
    for s in R["actions"]:
        lines += [f"### HT-CAND-INF-F03-{s['n']} / EA-CAND-INF-F03-{s['n']}\n\n{s['name']}; identity {s['status']}, effect {s['effectStatus']}. Exact target: {s['target']}; LEVEL/{s['change']}; origins {','.join(s['origins'])}.\n\n{s['description']} {s['scope']}\n\nRisk/contrary boundaries: {s['risk']} Sources: {', '.join(source_id(n) for n in s['sources'])}. Evidence/confidence: {'MODERATE/MODERATE' if s['effectStatus']=='REVIEW_READY' else 'LIMITED/LOW'}. Recommendation: review identity separately; {'review scoped content manipulation only' if s['effectStatus']=='REVIEW_READY' else 'retain effect research-needed'}. **{DECISION}**\n\n"]
    lines += ["## I–K. Rejections, research-needed and governance-blocked\n\n"]
    for h in R["hypotheses"]:
        lines += [f"- {h[0]} ({h[2]}): {h[1]} — {h[3]}. {h[4]} Sources: {', '.join(h[5]) or 'definitional triage; no empirical claim'}. **{DECISION}**\n"]
    lines += ["\n## Activation simulation\n\nNo activation is authorized. Candidate default scientific/model/practitioner eligibility is false. Production stays 456 active /435 causal. Rejections are research triage dispositions, not AI-created canonical REJECTED lifecycle transitions. Cross-Family owner does not imply consultation already occurred.\n"]
    emit(DOCS/"INF_F03_GOVERNANCE_DECISION_PACKAGE.md", "".join(lines))
    lines = ["# INF-F03 completeness and skeptical review\n\n", header,
        "```json\n"+encode({k:v for k,v in summary.items() if k not in {"protectedFiles","candidateIds"}})+"```\n\n",
        "## Recorded coverage, not scientific completeness\n\n14 active incident propositions: 9 causal (4 internal, 2 same-Layer cross-Family, 3 cross-Layer), 5 noncausal. Two deprecated are separately reviewed. No legacy/V1 projection double count. Incoming/outgoing degrees and full Layer matrices are frozen in the generalized baseline. Two isolated members and two outgoing RDS sources are flags, not missing-edge instructions.\n\n",
        "Four new causal hypotheses all cross-Layer: three INF→PSY, one ENV→INF. Only the scoped uncertainty/credibility claim is REVIEW_READY. Four Drivers searched; seven type/effect pairs, two scoped content-property effects REVIEW_READY. No exact relationship-targeted effect, no direct RDS target, no occurrence/pathway/moderation. All three eligibility dimensions remain false.\n\n",
        "RDS: INF-010 ratio denominator/requirements must align; INF-011 contradiction depends on a claim set and rule; INF-014 has surface/language/audience inputs; RDS-0001 cohesion depends on message element relations. No per-record operational version/window invented. INF-010/011 outgoing causal uses remain heightened-review flags. No new RDS causal agency or duplicate aggregate propagation.\n\n",
        "Skeptical pass: downgraded noise→surface complexity because normalized measures were null; kept simplification→complexity broad claims research-needed due meaning loss; kept load and source-sentiment proxies research-needed; no confidence-calibration claim from source-trust findings; no moderation from study-level culture or trait span; no pathway from reachability. No universal monotonic sign assigned to multidimensional profile hypotheses.\n\n",
        "No-found support is scoped to this search, not a claim that interventions do not exist. Non-level properties were considered but not given invented records. Timeline, intensity, reach, subgroups and synergy remain null/uncertain where not directly extracted. Candidate source deduplication must be repeated before any later canonical registration.\n\n",
        "## Human priorities\n\nResolve source alignment and construct choices for existing edges without replacing them here. Review INF-013/077 overlap and missing metadata under separate ontology authority. Decide whether source-trust measures adequately operationalize PSY-113 in REL-CAND-INF-F03-001. Confirm exact selected-feature scope of editing and quantified-disclosure action effects. Do not generalize these to comprehension, RDS fit, or all users.\n"]
    emit(DOCS/"INF_F03_COMPLETENESS_REPORT.md", "".join(lines))


def validate():
    w = ae.read(STORE/"workspace.json")
    result = ae.validate_workspace(w, context())
    for side in ae.read(STORE/"relationship-source-findings.json"):
        for f in side["sourceFindings"]:
            ae.schema_set().validate("source-finding", f)
        assert set(side["synthesis"]["sourceFindingIds"]) == {f["id"] for f in side["sourceFindings"]}
    assert ri.causal_traversal(w["passA"]["relationshipCandidates"]) == []
    assert all(v["unchanged"] for v in protected().values())
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--validate", action="store_true")
    args = p.parse_args()
    output = validate() if args.validate else build()
    print(encode({k:v for k,v in output.items() if k not in {"protectedFiles", "candidateIds"}}))
