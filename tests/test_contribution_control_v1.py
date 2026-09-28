"""Production contribution-control Phase 0/1 safety tests."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import contribution_control_v1 as cc


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ContributionControlProductionTests(unittest.TestCase):
    def group(self):
        rel = cc.native_control("RELATIONSHIP", "REL-V1-PSY-LAYER-001")
        ea = cc.native_control("EFFECT_ASSERTION", "EA-V1-PSY-LAYER-001")
        return {
            "schemaVersion": "1.0.0", "groupId": "CONTRIB-PSY-LAYER-REPETITION-001", "groupVersion": "1.0.0",
            "objectKind": "CONTRIBUTION_IDENTITY_CONTROL", "scientificContributionDefinition": "One repetition-exposure contribution to specified belief confidence",
            "scope": {"mode": "SHADOW_VALIDATION_ONLY"},
            "identityDimensions": {"causalExposureOrChange": "Repeated encounter with one specified claim", "targetChange": "Belief confidence in that claim", "causalContrast": "Repeated versus non-repeated encounter", "unitOfAnalysis": "Person x claim x protocol", "timeScope": "Exposure before judgment", "pathwayScope": "Bounded total contribution", "intendedContribution": "One repetition contribution", "underlyingRepresentedQuantity": "Exposure-induced belief-confidence change"},
            "memberRepresentations": [
                {"recordClass": "RELATIONSHIP", "recordId": rel["recordId"], "recordRevision": rel["recordRevision"], "recordHash": rel["recordHash"], "memberRole": "PRIMARY_CAUSAL_CONTRIBUTION", "representationRelationship": "SAME_UNDERLYING_CONTRIBUTION", "nativeContributionId": None, "nativeContributionPolicy": None},
                {"recordClass": "EFFECT_ASSERTION", "recordId": ea["recordId"], "recordRevision": ea["recordRevision"], "recordHash": ea["recordHash"], "memberRole": "ALTERNATE_CAUSAL_REPRESENTATION", "representationRelationship": "SAME_UNDERLYING_CONTRIBUTION", "nativeContributionId": ea["nativeContributionId"], "nativeContributionPolicy": ea["nativeContributionPolicy"]},
            ],
            "countingPolicy": "MUTUALLY_EXCLUSIVE_REPRESENTATIONS", "propagationPolicy": "COUNT_ONCE_NO_ADDITIVE_PROPAGATION", "selectionPolicy": "EXACT_EXPLICIT_REPRESENTATION_REQUIRED", "derivationPolicy": "NOT_APPLICABLE", "causalIndependenceStatus": "SAME_CONTRIBUTION_CONFIRMED", "evidenceOverlapStatus": "SEPARATE_FROM_CONTRIBUTION_IDENTITY", "constituentOverlapStatus": "NOT_APPLICABLE", "crossLevelRouteReferences": [], "stateRouteReferences": [], "rdsProfileReferences": [], "limitations": ["Shadow validation only"], "provenance": {"implementationDecisionId": cc.DECISION_ID}, "governanceReference": cc.DECISION_ID, "shadowOnly": True,
            "causalEvidence": False, "executionAuthority": False, "hasWeight": False, "hasPolarity": False, "hasLifecycle": False, "hasActivation": False, "hasPropagationState": False,
        }

    def request(self, group=None, selection=None):
        group = group or self.group()
        candidates = [{"recordClass": m["recordClass"], "recordId": m["recordId"], "recordRevision": m["recordRevision"], "recordHash": m["recordHash"]} for m in group["memberRepresentations"]]
        return {"schemaVersion": "1.0.0", "candidateRepresentations": candidates, "groupReferences": [{"groupId": group["groupId"], "groupVersion": group["groupVersion"]}], "explicitSelections": selection or {}, "context": {"mode": "SHADOW_VALIDATION_ONLY"}}

    def test_repository_registry_is_phase_bounded(self):
        state = cc.validate_repository()
        self.assertIn(state["groups"], (0, 1))
        self.assertEqual({k: v for k, v in state.items() if k != "groups"}, {"recordMigrations": 0, "relationshipChanges": 0, "effectAssertionChanges": 0, "graphBehaviorChanges": 0, "simulationBehaviorChanges": 0, "lifecycleChanges": 0, "activationChanges": 0, "rdsCausalSourceChanges": 0})

    def test_phase0_registry_is_empty_or_phase1_exactly_one(self):
        groups = cc.load_registry().all()
        if groups:
            self.assertEqual([(g["groupId"], g["groupVersion"]) for g in groups], [("CONTRIB-PSY-LAYER-REPETITION-001", "1.0.0")])
        else:
            self.assertEqual(read("data/contribution-control-v1/groups.json")["groups"], [])

    def test_phase1_exact_group_and_shadow_receipts(self):
        groups = cc.load_registry().all()
        if not groups:
            self.skipTest("Phase 0 empty registry")
        group = groups[0]
        self.assertEqual((group["groupId"], group["groupVersion"]), ("CONTRIB-PSY-LAYER-REPETITION-001", "1.0.0"))
        self.assertTrue(group["shadowOnly"])
        self.assertEqual([(m["recordId"], m["memberRole"]) for m in group["memberRepresentations"]], [("REL-V1-PSY-LAYER-001", "PRIMARY_CAUSAL_CONTRIBUTION"), ("EA-V1-PSY-LAYER-001", "ALTERNATE_CAUSAL_REPRESENTATION")])
        receipts = read("data/contribution-control-v1/repetition-shadow-receipts.json")
        expected = {"BOTH_NO_SELECTION": "SELECT_ONE_REQUIRED", "RELATIONSHIP_SELECTED": "COUNT_ONCE", "EA_SELECTED": "COUNT_ONCE", "BOTH_SELECTED": "FAIL_CONTRADICTORY_GROUP", "WRONG_RELATIONSHIP_HASH": "FAIL_NATIVE_CONTROL_MISMATCH", "WRONG_EA_HASH": "FAIL_NATIVE_CONTROL_MISMATCH", "WRONG_GROUP_VERSION": "BLOCK_PENDING_IDENTITY", "EA_NATIVE_CONTRIBUTION_MISMATCH": "FAIL_NATIVE_CONTROL_MISMATCH", "INDEPENDENT_SAME_TARGET": "COUNT_ONCE", "DERIVATION_ADDED": "COUNT_ONCE"}
        self.assertEqual({row["caseId"]: row["receipt"]["resolutionOutcome"] for row in receipts["cases"]}, expected)
        self.assertEqual(receipts["numericControl"]["resolvedCountOnceTotal"], 0.2)
        self.assertEqual(receipts["numericControl"]["resolvedWithIndependentTotal"], 0.3)
        for row in receipts["cases"]:
            receipt = row["receipt"]
            self.assertFalse(receipt["causalAuthorityGranted"] or receipt["graphAuthorityGranted"] or receipt["simulationAuthorityGranted"] or receipt["activationAuthorityGranted"])
            self.assertEqual(len(receipt["deterministicFingerprint"]), 64)

    def test_phase1_receipts_regenerate_deterministically(self):
        if not cc.load_registry().all():
            self.skipTest("Phase 0 empty registry")
        import materialize_contribution_repetition_phase1 as materializer
        self.assertEqual(materializer.build(), read("data/contribution-control-v1/repetition-shadow-receipts.json"))

    def test_aggregate_firewall_and_wp5_readiness(self):
        groups = cc.load_registry().all()
        self.assertEqual({group["groupId"] for group in groups}, {"CONTRIB-PSY-LAYER-REPETITION-001"} if groups else set())
        forbidden = {"INS-039", "INS-103", "SOC-024", "SOC-041", "SOC-052", "SOC-053", "SOC-054", "SOC-055", "SOC-056", "SOC-074", "SOC-076", "SOC-096"}
        self.assertFalse(forbidden & {member["recordId"] for group in groups for member in group["memberRepresentations"]})
        readiness = read("data/governance/post-scale-up/contribution/contribution-wp-psg-005-readiness.json")
        self.assertEqual(readiness["wpPsg005Status"], "NOT_STARTED")
        self.assertEqual(readiness["causalSourceAuthorizations"], 0)
        self.assertTrue(all(row["causalSourceEligible"] is False for row in readiness["records"]))

    def test_phase1_rollback_requires_no_source_rewrite(self):
        before_rel = cc.digest(cc.native_record("RELATIONSHIP", "REL-V1-PSY-LAYER-001"))
        before_ea = cc.digest(cc.native_record("EFFECT_ASSERTION", "EA-V1-PSY-LAYER-001"))
        with patch.object(cc, "load_registry", return_value=cc.ContributionRegistry([])):
            independent = {"recordClass": "SYNTHETIC_CAUSAL_ROUTE", "recordId": "SYN-ROLLBACK-001", "recordRevision": 1, "recordHash": "b" * 64}
            receipt = cc.resolve_for_causal_consumption({"schemaVersion": "1.0.0", "candidateRepresentations": [independent], "groupReferences": [], "explicitSelections": {}, "context": {}})
        self.assertEqual(receipt["resolutionOutcome"], "ALLOW_ALL_INDEPENDENT")
        self.assertEqual(cc.digest(cc.native_record("RELATIONSHIP", "REL-V1-PSY-LAYER-001")), before_rel)
        self.assertEqual(cc.digest(cc.native_record("EFFECT_ASSERTION", "EA-V1-PSY-LAYER-001")), before_ea)

    def test_exact_group_schema_and_authority_firewall(self):
        self.assertTrue(cc.validate_group(self.group()))
        for selector in cc.IMPLICIT_SELECTORS:
            invalid = copy.deepcopy(self.group()); invalid["groupVersion"] = selector
            with self.assertRaises(cc.ValidationError): cc.validate_group(invalid)
        for field in ("causalEvidence", "executionAuthority", "hasWeight", "hasPolarity", "hasLifecycle", "hasActivation", "hasPropagationState"):
            invalid = copy.deepcopy(self.group()); invalid[field] = True
            with self.assertRaises(cc.ValidationError): cc.validate_group(invalid)
        for field, value in (("weight", 1), ("polarity", "POSITIVE"), ("lifecycleStatus", "ACTIVE"), ("activationStatus", "ACTIVE"), ("propagationState", 1)):
            invalid = copy.deepcopy(self.group()); invalid[field] = value
            with self.assertRaises(cc.ValidationError): cc.validate_group(invalid)

    def test_native_adapters_are_read_only_and_exact(self):
        rel = cc.native_control("RELATIONSHIP", "REL-V1-PSY-LAYER-001")
        ea = cc.native_control("EFFECT_ASSERTION", "EA-V1-PSY-LAYER-001")
        der = cc.native_control("DERIVATION", "DER-V1-SOC-F07-001")
        rds = cc.native_control("RDS_PROFILE", "RDS-PROFILE-V1-SOC-F07-001")
        xle = cc.native_control("CROSS_LEVEL_MAPPING", "XLEM-V1-INSTITUTION-IMPLEMENTATION-PERCEPTION-001")
        self.assertTrue(rel["causalContribution"] and ea["causalContribution"])
        self.assertEqual(ea["nativeContributionId"], "CONTRIB-PSY-LAYER-REPETITION-001")
        self.assertEqual(der["nativeContributionPolicy"], "RECALCULATION_ONLY_NO_CAUSAL_SUM")
        self.assertFalse(der["causalContribution"] or rds["causalContribution"] or xle["causalContribution"] or cc.network_state_control()["causalContribution"])
        self.assertTrue(all(row["sourceRecordMutated"] is False for row in (rel, ea, der, rds, xle)))

    def test_exact_members_and_native_mismatch_fail_closed(self):
        self.assertTrue(cc.validate_group_members(self.group()))
        for member_index, field, value in ((0, "recordRevision", 2), (0, "recordHash", "0" * 64), (1, "nativeContributionId", "CONTRIB-WRONG")):
            invalid = copy.deepcopy(self.group()); invalid["memberRepresentations"][member_index][field] = value
            with self.assertRaises(cc.ValidationError): cc.validate_group_members(invalid)
        invalid = copy.deepcopy(self.group()); invalid["identityDimensions"]["targetChange"] = "Different target"
        invalid["memberRepresentations"].append(copy.deepcopy(invalid["memberRepresentations"][0]))
        with self.assertRaises(cc.ValidationError): cc.validate_group(invalid)

    def test_external_relationship_binding_needs_no_record_mutation(self):
        before = cc.native_record("RELATIONSHIP", "REL-V1-PSY-LAYER-001")
        before_hash = cc.digest(before)
        self.assertTrue(cc.validate_group_members(self.group()))
        self.assertEqual(cc.digest(cc.native_record("RELATIONSHIP", "REL-V1-PSY-LAYER-001")), before_hash)

    def test_empty_registry_keeps_independent_records_independent(self):
        candidate = {"recordClass": "SYNTHETIC_CAUSAL_ROUTE", "recordId": "SYN-INDEPENDENT-001", "recordRevision": 1, "recordHash": "a" * 64}
        request = {"schemaVersion": "1.0.0", "candidateRepresentations": [candidate], "groupReferences": [], "explicitSelections": {}, "context": {}}
        receipt = cc.resolve_for_causal_consumption(request)
        self.assertEqual(receipt["resolutionOutcome"], "ALLOW_ALL_INDEPENDENT")
        self.assertEqual(receipt["includedRepresentations"], ["SYN-INDEPENDENT-001"])

    def test_shadow_count_once_and_no_automatic_selection(self):
        group = self.group(); registry = cc.ContributionRegistry([group])
        with patch.object(cc, "load_registry", return_value=registry):
            no_selection = cc.resolve_for_causal_consumption(self.request(group))
            self.assertEqual(no_selection["resolutionOutcome"], "SELECT_ONE_REQUIRED")
            rel = cc.resolve_for_causal_consumption(self.request(group, {group["groupId"]: "REL-V1-PSY-LAYER-001"}))
            ea = cc.resolve_for_causal_consumption(self.request(group, {group["groupId"]: "EA-V1-PSY-LAYER-001"}))
            self.assertEqual(rel["includedRepresentations"], ["REL-V1-PSY-LAYER-001"])
            self.assertEqual(ea["includedRepresentations"], ["EA-V1-PSY-LAYER-001"])
            self.assertEqual(rel["resolutionOutcome"], ea["resolutionOutcome"], "COUNT_ONCE")
            invalid = self.request(group); invalid["explicitSelections"][group["groupId"]] = ["REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001"]
            with self.assertRaises(cc.ValidationError): cc.resolve_for_causal_consumption(invalid)

    def test_noncausal_records_resolve_to_zero_and_fingerprint_is_deterministic(self):
        der = cc.native_control("DERIVATION", "DER-V1-SOC-F07-001")
        candidate = {k: der[k] for k in ("recordClass", "recordId", "recordRevision", "recordHash")}
        request = {"schemaVersion": "1.0.0", "candidateRepresentations": [candidate], "groupReferences": [], "explicitSelections": {}, "context": {"nativeControls": {candidate["recordId"]: der}}}
        first = cc.resolve_for_causal_consumption(request); second = cc.resolve_for_causal_consumption(request)
        self.assertEqual(first["resolutionOutcome"], "NO_CAUSAL_CONTRIBUTION")
        self.assertEqual(first["deterministicFingerprint"], second["deterministicFingerprint"])
        self.assertFalse(first["causalAuthorityGranted"] or first["graphAuthorityGranted"] or first["simulationAuthorityGranted"] or first["activationAuthorityGranted"])

    def test_protected_science_hashes_unchanged(self):
        phase1 = ROOT / "data/governance/post-scale-up/contribution/contribution-phase1-protected-hashes.json"
        manifest = read(phase1 if phase1.exists() else ROOT / "data/governance/post-scale-up/contribution/contribution-phase0-protected-hashes.json")
        for relative, expected in manifest["files"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            self.assertEqual(actual, expected, relative)
        self.assertEqual(len(read("data/drivers.json")), 770)
        self.assertEqual(sum(row["entityType"] == "RELATIONAL_DERIVED_STATE" for row in read("data/entities.json")), 41)


if __name__ == "__main__":
    unittest.main()
