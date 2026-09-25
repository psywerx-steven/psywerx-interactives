"""WP-PSG-001 Stage E reference implementation and Stage F dry-run tests."""

from __future__ import annotations

import copy
import importlib.util
import json
import hashlib
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "prototypes/rds-computation-v1"
DATA = ROOT / "data/governance/post-scale-up/rds"
runtime_path = PROTO / "runtime/rds_runtime.py"
spec = importlib.util.spec_from_file_location("rds_runtime_prototype", runtime_path)
rt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rt
spec.loader.exec_module(rt)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RdsComputationPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = read(PROTO / "registry/profiles.json")["profiles"]
        cls.bindings = read(PROTO / "registry/bindings.json")["bindings"]
        cls.profile = next(row for row in cls.profiles if row["rdsId"] == "RDS-0006")
        cls.binding = next(row for row in cls.bindings if row["bindingId"] == "PROTO-BIND-RDS-0006-STAR-4")
        cls.execution = read(PROTO / "runtime/reference-execution.json")
        cls.dry_run = read(DATA / "rds-migration-dry-run.json")

    def test_json_schemas_and_concrete_objects(self):
        pairs = [
            ("rds-computation-profile.schema.json", self.profile),
            ("rds-application-binding.schema.json", self.binding),
            ("rds-execution-request.schema.json", self.execution["request"]),
            ("rds-execution-provenance.schema.json", self.execution["result"]),
            ("rds-execution-eligibility.schema.json", {"state": "EXECUTABLE"}),
        ]
        for name, value in pairs:
            validator = Draft202012Validator(read(PROTO / "schemas" / name))
            self.assertEqual(list(validator.iter_errors(value)), [], name)

    def test_all_profile_types_and_input_roles(self):
        self.assertEqual({row["profileType"] for row in self.profiles}, rt.PROFILE_TYPES)
        taxonomy = read(PROTO / "registry/input-role-taxonomy.json")["roles"]
        self.assertEqual({row["role"] for row in taxonomy}, rt.INPUT_ROLES)
        self.assertEqual({row["role"] for row in taxonomy if row["causalConstituentByRole"]}, {"CONSTITUENT"})
        used = {spec["role"] for profile in self.profiles for spec in profile["inputContract"]}
        self.assertTrue({"CONSTITUENT", "MEASUREMENT_INPUT", "PARAMETER", "REFERENCE_VALUE"} <= used)
        for profile in self.profiles:
            rt.validate_computation_profile(profile)
            self.assertFalse(profile["causalSourceEligible"])
            self.assertEqual(profile["causalSourceGate"], "WP-PSG-005_REQUIRED")

    def test_measurement_and_estimation_semantics(self):
        measurement = next(row for row in self.profiles if row["profileId"] == "PROTO-SYNTHETIC-MEASUREMENT-001" and row["profileVersion"] == "1.0.0")
        estimation = next(row for row in self.profiles if row["profileType"] == "ESTIMATION_PROFILE")
        self.assertFalse(measurement["derivationEntailed"])
        self.assertIn("scoringRule", measurement["measurementProcedure"])
        self.assertFalse(estimation["derivationEntailed"])
        self.assertIn("diagnosticExpectations", estimation["estimationProcedure"])
        self.assertIn("NOT A PROPOSED CUL-088 MEASUREMENT MODEL", estimation["scopeLimitations"])
        bad = copy.deepcopy(estimation)
        bad["calculationReference"] = "FALSE_DETERMINISM"
        with self.assertRaises(rt.ContractError):
            rt.validate_computation_profile(bad)
        measurement_binding = next(row for row in self.bindings if row["bindingId"] == "PROTO-BIND-SYNTHETIC-MEASUREMENT-001")
        rt.validate_profile_binding_compatibility(measurement, measurement_binding)
        wrong_instrument = copy.deepcopy(measurement_binding); wrong_instrument["measurementInstrument"] = "WRONG"
        with self.assertRaises(rt.ContractError):
            rt.validate_profile_binding_compatibility(measurement, wrong_instrument)

    def test_exact_binding_and_profile_compatibility(self):
        rt.validate_profile_binding_compatibility(self.profile, self.binding)
        bad = copy.deepcopy(self.binding)
        bad["rdsId"] = "CUL-088"
        with self.assertRaises(rt.ContractError):
            rt.validate_profile_binding_compatibility(self.profile, bad)
        bad = copy.deepcopy(self.binding)
        bad["unitOfAnalysis"] = "INDIVIDUAL"
        with self.assertRaises(rt.ContractError):
            rt.validate_profile_binding_compatibility(self.profile, bad)
        bad = copy.deepcopy(self.binding)
        bad["networkBoundary"] = None
        with self.assertRaises(rt.ContractError):
            rt.validate_profile_binding_compatibility(self.profile, bad)

    def test_no_profile_incomplete_binding_and_definition_mismatch(self):
        request = self.execution["request"]
        no_profile = rt.resolve_execution_eligibility({**request, "rdsId": "RDS-NONE"}, self.profiles, self.bindings, "x")
        self.assertEqual(no_profile["state"], "NON_EXECUTABLE_NO_PROFILE")
        incomplete = dict(request); incomplete.pop("bindingVersion")
        self.assertEqual(rt.resolve_execution_eligibility(incomplete, self.profiles, self.bindings, self.profile["rdsDefinitionHash"])["state"], "NON_EXECUTABLE_INCOMPLETE_BINDING")
        self.assertEqual(rt.resolve_execution_eligibility(request, self.profiles, self.bindings, "changed")["state"], "NON_EXECUTABLE_DEFINITION_MISMATCH")

    def test_no_latest_default_or_implicit_resolution(self):
        for selector in rt.FORBIDDEN_SELECTORS:
            request = {**self.execution["request"], "profileVersion": selector}
            state = rt.resolve_execution_eligibility(request, self.profiles, self.bindings, self.profile["rdsDefinitionHash"])["state"]
            self.assertEqual(state, "NON_EXECUTABLE_VERSION_MISMATCH", selector)

    def test_input_hash_mismatch_and_missing_input(self):
        request = copy.deepcopy(self.execution["request"])
        request["inputs"] = {}
        self.assertEqual(rt.resolve_execution_eligibility(request, self.profiles, self.bindings, self.profile["rdsDefinitionHash"])["state"], "NON_EXECUTABLE_INPUT_MISMATCH")
        request = copy.deepcopy(self.execution["request"])
        request["inputs"]["SOC-049"]["definitionHash"] = "stale"
        self.assertEqual(rt.resolve_execution_eligibility(request, self.profiles, self.bindings, self.profile["rdsDefinitionHash"])["state"], "NON_EXECUTABLE_INPUT_MISMATCH")

    def test_immutable_versions_and_multiple_bindings(self):
        rt.validate_registry_immutability(self.profiles)
        rt.validate_registry_immutability(self.bindings)
        collision = copy.deepcopy(self.profile); collision["displayName"] = "mutated"
        with self.assertRaises(rt.ContractError):
            rt.validate_registry_immutability([self.profile, collision])
        revised = copy.deepcopy(self.profile); revised["profileVersion"] = "1.0.1"; revised["displayName"] = "compatible correction test"
        rt.validate_registry_immutability([self.profile, revised])
        self.assertEqual(len([b for b in self.bindings if b["profileId"] == self.profile["profileId"]]), 2)
        synthetic_versions = [p for p in self.profiles if p["profileId"] == "PROTO-SYNTHETIC-MEASUREMENT-001"]
        self.assertEqual({p["profileVersion"] for p in synthetic_versions}, {"1.0.0", "1.0.1"})
        synthetic_profiles = [p for p in self.profiles if p["rdsId"] == "TEST-RDS-MEASUREMENT-001"]
        self.assertEqual(len({p["profileId"] for p in synthetic_profiles}), 2)

    def test_profile_identity_and_proliferation_rules(self):
        context_only = copy.deepcopy(self.profile); context_only["displayName"] = self.profile["displayName"]
        self.assertEqual(rt.classify_profile_change(self.profile, context_only), "NEW_OR_REVISED_BINDING")
        true_method = copy.deepcopy(self.profile); true_method["normalization"] = "OTHER"
        self.assertEqual(rt.classify_profile_change(self.profile, true_method), "NEW_PROFILE_IDENTITY")
        metadata = copy.deepcopy(self.profile); metadata["displayName"] = "presentation change"
        self.assertEqual(rt.classify_profile_change(self.profile, metadata), "METADATA_ONLY")

    def test_rds0006_numeric_equivalence_provenance_and_lineage(self):
        result = self.execution["result"]
        self.assertEqual(result["output"], 1.0)
        self.assertEqual(result["executionFingerprint"], rt.execution_fingerprint(self.execution["request"], self.profile, self.binding))
        self.assertEqual(self.profile["provenance"]["compatibilityWrapperFor"], "DER-V1-SOC-F07-001")
        self.assertTrue(self.profile["provenance"]["preservesLegacyId"])
        self.assertEqual(self.profile["causalSemantics"], "DEFINITIONAL_CALCULATIONAL_RECALCULATION_ONLY_NO_CAUSAL_SUM")
        self.assertFalse(result["causalSourceAuthorized"])

    def test_causal_firewall_even_when_computable(self):
        with self.assertRaises(rt.ContractError):
            rt.validate_causal_firewall(self.profile, True)
        request = copy.deepcopy(self.execution["request"]); request["causalSourceRequested"] = True
        with self.assertRaises(rt.ContractError):
            rt.execute_reference(request, self.profiles, self.bindings, self.profile["rdsDefinitionHash"])

    def test_all_41_dry_run_rows_and_categories(self):
        self.assertEqual(self.dry_run["totalRds"], 41)
        self.assertEqual(len(self.dry_run["records"]), 41)
        self.assertEqual(len({row["rdsId"] for row in self.dry_run["records"]}), 41)
        self.assertEqual(self.dry_run["counts"], {
            "READY_FOR_PROFILE_MATERIALIZATION": 1, "PROFILE_DEFINITION_REQUIRED": 13,
            "MULTIPLE_PROFILE_REVIEW_REQUIRED": 12, "LATENT_ESTIMATION_DESIGN_REQUIRED": 0,
            "NON_EXECUTABLE_PENDING_SCIENCE": 13, "BLOCKED_BY_ONTOLOGY": 2,
        })
        self.assertTrue(all(not row["productionMutationAuthorized"] for row in self.dry_run["records"]))
        self.assertTrue(all(not row["causalSourceEligible"] for row in self.dry_run["records"]))
        ready = [row for row in self.dry_run["records"] if row["currentMigrationCategory"] == "READY_FOR_PROFILE_MATERIALIZATION"]
        self.assertEqual([row["rdsId"] for row in ready], ["RDS-0006"])

    def test_non_ready_categories_do_not_fabricate_profiles(self):
        for row in self.dry_run["records"]:
            if row["rdsId"] != "RDS-0006":
                self.assertEqual(row["proposedProfileRecords"], [], row["rdsId"])
            if row["currentMigrationCategory"] == "BLOCKED_BY_ONTOLOGY":
                self.assertEqual(row["ontologyDependencies"], ["WP-PSG-007_CONSTRUCT_ONTOLOGY_GOVERNANCE"])

    def test_production_files_hash_protected(self):
        protected = read(PROTO / "migration/protected-production-hashes.json")
        for relative, expected in protected["sha256"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_decision_packet_and_phase_boundaries(self):
        delta = read(DATA / "rds-production-delta-preview.json")
        packet = read(DATA / "rds-production-implementation-decision-packet.json")
        self.assertEqual(delta["decisionPacketId"], "DP-PSG-001-IMPLEMENTATION")
        self.assertEqual(packet["decisionPacketId"], "DP-PSG-001-IMPLEMENTATION")
        self.assertEqual(packet["status"], "HUMAN_ARCHITECTURE_GOVERNANCE_REQUIRED")
        self.assertEqual(delta["phase0"]["migratedRds"], [])
        self.assertEqual(delta["phase1"]["migratedRds"], ["RDS-0006"])
        self.assertEqual(delta["excluded"]["remainingRds"], 40)
        self.assertFalse(delta["productionMutationAuthorized"])


if __name__ == "__main__":
    unittest.main()
