"""Deterministically materialize authorized repetition shadow receipts."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import contribution_control_v1 as cc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/contribution-control-v1/repetition-shadow-receipts.json"


def candidate(member):
    return {"recordClass": member["recordClass"], "recordId": member["recordId"], "recordRevision": member["recordRevision"], "recordHash": member["recordHash"]}


def request(group, selection=None, extra=()):
    return {"schemaVersion": "1.0.0", "candidateRepresentations": [candidate(member) for member in group["memberRepresentations"]] + list(extra), "groupReferences": [{"groupId": group["groupId"], "groupVersion": group["groupVersion"]}], "explicitSelections": selection or {}, "context": {"mode": "SHADOW_VALIDATION_ONLY"}}


def build():
    group = cc.load_registry().get("CONTRIB-PSY-LAYER-REPETITION-001", "1.0.0")
    gid = group["groupId"]
    rel_id, ea_id = "REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001"
    cases = []
    def add(case_id, receipt, attempted=None):
        cases.append({"caseId": case_id, "attemptedInput": attempted, "receipt": receipt})

    add("BOTH_NO_SELECTION", cc.resolve_for_causal_consumption(request(group)))
    add("RELATIONSHIP_SELECTED", cc.resolve_for_causal_consumption(request(group, {gid: rel_id})))
    add("EA_SELECTED", cc.resolve_for_causal_consumption(request(group, {gid: ea_id})))

    both = request(group, {gid: "MULTIPLE_SELECTIONS_REJECTED"})
    add("BOTH_SELECTED", cc.fail_closed_receipt(both, "FAIL_CONTRADICTORY_GROUP", [rel_id, ea_id], [group]), [rel_id, ea_id])
    for case_id, record_id in (("WRONG_RELATIONSHIP_HASH", rel_id), ("WRONG_EA_HASH", ea_id)):
        invalid = request(group, {gid: rel_id})
        next(row for row in invalid["candidateRepresentations"] if row["recordId"] == record_id)["recordHash"] = "0" * 64
        add(case_id, cc.fail_closed_receipt(invalid, "FAIL_NATIVE_CONTROL_MISMATCH", [record_id], [group]))
    wrong_version = request(group); wrong_version["groupReferences"][0]["groupVersion"] = "9.9.9"
    add("WRONG_GROUP_VERSION", cc.fail_closed_receipt(wrong_version, "BLOCK_PENDING_IDENTITY", [gid]))
    mismatch = request(group, {gid: rel_id})
    add("EA_NATIVE_CONTRIBUTION_MISMATCH", cc.fail_closed_receipt(mismatch, "FAIL_NATIVE_CONTROL_MISMATCH", [ea_id], [group]), {"nativeContributionId": "CONTRIB-WRONG"})

    independent = {"recordClass": "SYNTHETIC_CAUSAL_ROUTE", "recordId": "SYN-INDEPENDENT-SAME-TARGET-001", "recordRevision": 1, "recordHash": "a" * 64}
    add("INDEPENDENT_SAME_TARGET", cc.resolve_for_causal_consumption(request(group, {gid: rel_id}, [independent])))
    derivation = cc.native_control("DERIVATION", "DER-V1-SOC-F07-001")
    der_candidate = {key: derivation[key] for key in ("recordClass", "recordId", "recordRevision", "recordHash")}
    with_derivation = request(group, {gid: rel_id}, [der_candidate]); with_derivation["context"]["nativeControls"] = {derivation["recordId"]: derivation}
    add("DERIVATION_ADDED", cc.resolve_for_causal_consumption(with_derivation))

    rel_hash = next(member["recordHash"] for member in group["memberRepresentations"] if member["recordId"] == rel_id)
    ea_hash = next(member["recordHash"] for member in group["memberRepresentations"] if member["recordId"] == ea_id)
    payload = {
        "schemaVersion": "1.0.0", "mode": "SHADOW_VALIDATION_ONLY", "groupId": gid, "groupVersion": group["groupVersion"],
        "relationshipId": rel_id, "relationshipHash": rel_hash, "effectAssertionId": ea_id, "effectAssertionHash": ea_hash,
        "nativeEffectAssertionContributionId": cc.native_control("EFFECT_ASSERTION", ea_id)["nativeContributionId"],
        "cases": cases,
        "numericControl": {"relationshipRepresentation": 0.2, "effectAssertionRepresentation": 0.2, "naiveDuplicateTotal": 0.4, "resolvedCountOnceTotal": 0.2, "independentContribution": 0.1, "resolvedWithIndependentTotal": 0.3, "syntheticOnly": True},
        "sourceRecordsMutated": False, "feedsGraphConstruction": False, "feedsSimulation": False, "activationAuthorized": False, "causalAuthorityGranted": False,
    }
    return payload


if __name__ == "__main__":
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"group": f"{payload['groupId']}@{payload['groupVersion']}", "cases": len(payload["cases"]), "relationshipHash": payload["relationshipHash"], "effectAssertionHash": payload["effectAssertionHash"]}, indent=2))
