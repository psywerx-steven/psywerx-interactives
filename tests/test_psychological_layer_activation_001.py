"""Exact gates for Psychological Layer partial activation 001."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRE_ACTIVATION = "d7bb61b0e139e93b874c6aa9844dbfffb94bc97a"
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import materialize_psychological_layer_activation_001 as activation
import relationship_intervention_v1 as ri


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def frozen(relative: str):
    return json.loads(subprocess.check_output(["git", "show", f"{PRE_ACTIVATION}:{relative}"], cwd=ROOT))


def without_governance(record: dict) -> dict:
    result = copy.deepcopy(record)
    result.pop("governance", None)
    return result


class PsychologicalLayerActivation001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read(activation.CATALOG_PATH)
        cls.manifest = read(activation.MANIFEST_PATH)
        cls.decision = read(activation.DECISION_DATA_PATH)
        cls.records = {
            row["id"]: row
            for key in ("happeningTypes", "effectAssertions", "evidenceAssessments")
            for row in cls.catalog[key]
            if "-PSY-LAYER-" in row["id"]
        }

    def test_exact_six_bundles_and_eighteen_active_records(self):
        active = {identifier for identifier, row in self.records.items() if row["governance"]["activationStatus"] == "ACTIVE"}
        self.assertEqual(active, activation.ACTIVE_IDS)
        self.assertEqual(len(self.manifest["atomicBundles"]), 6)
        self.assertEqual(self.manifest["activatedCounts"], {
            "relationships": 0, "evidenceAssessments": 6,
            "happeningTypes": 6, "effectAssertions": 6, "total": 18,
        })
        self.assertEqual(active & activation.ACTIVE_EVIDENCE_IDS, activation.ACTIVE_EVIDENCE_IDS)
        self.assertEqual(active & activation.ACTIVE_TYPE_IDS, activation.ACTIVE_TYPE_IDS)
        self.assertEqual(active & activation.ACTIVE_EFFECT_IDS, activation.ACTIVE_EFFECT_IDS)

    def test_lifecycle_transitions_and_exact_authorization(self):
        authorization = next(x for x in self.catalog["authorizations"] if x["decisionId"] == activation.DECISION_ID)
        authorized = {x["id"]: x for x in authorization["authorizedObjects"]}
        self.assertEqual(set(authorized), activation.ACTIVE_IDS)
        for identifier in activation.ACTIVE_IDS:
            record = self.records[identifier]
            governance = record["governance"]
            self.assertEqual((governance["lifecycleStatus"], governance["activationStatus"]), ("GOVERNED", "ACTIVE"))
            self.assertEqual(governance["decisionRecord"], activation.DECISION_PATH)
            transition = governance["transitionProvenance"][-1]
            self.assertEqual(transition["fromState"], {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"})
            self.assertEqual(transition["toState"], {"lifecycleStatus": "GOVERNED", "activationStatus": "ACTIVE"})
            self.assertEqual(transition["governanceDecisionRecord"], activation.DECISION_PATH)
            self.assertTrue(transition["exactDecisionMaterialization"])
            self.assertEqual(authorized[identifier]["recordHash"], ae.digest(record))

    def test_active_effect_dependencies_are_atomic(self):
        for _, evidence_id, type_id, effect_id in activation.BUNDLES:
            effect = self.records[effect_id]
            self.assertEqual(effect["typeId"], type_id)
            self.assertIn(evidence_id, effect["evidenceAssessmentIds"])
            self.assertTrue(all(self.records[x]["governance"]["activationStatus"] == "ACTIVE" for x in (evidence_id, type_id, effect_id)))
        validated = ae.validate_catalog(self.catalog, ae.Context.repository())
        self.assertEqual(validated["statusChanges"], 0)

    def test_no_relationship_and_repetition_bundle_remains_inactive(self):
        relationships = read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]
        evidence = read(ROOT / "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]
        relationship = next(x for x in relationships if x["id"] == "REL-V1-PSY-LAYER-001")
        relationship_evidence = next(x for x in evidence if x["id"] == "EVA-V1-PSY-LAYER-REL-001")
        self.assertEqual(relationship["governance"]["activationStatus"], "INACTIVE")
        self.assertEqual(relationship_evidence["governance"]["activationStatus"], "INACTIVE")
        for identifier in activation.BLOCKED_REPETITION_IDS & self.records.keys():
            self.assertEqual(self.records[identifier]["governance"]["activationStatus"], "INACTIVE")
        effect = self.records["EA-V1-PSY-LAYER-001"]
        self.assertEqual(effect["contribution"]["groupId"], "CONTRIB-PSY-LAYER-REPETITION-001")
        self.assertIn("never sum", effect["contribution"]["reconciliation"])

    def test_twenty_two_identity_only_records_stay_inactive(self):
        self.assertEqual(len(activation.KEEP_INACTIVE_TYPE_IDS), 22)
        for identifier in activation.KEEP_INACTIVE_TYPE_IDS:
            self.assertEqual(self.records[identifier]["governance"]["activationStatus"], "INACTIVE")

    def test_scientific_content_is_identical_to_audited_baseline(self):
        old = frozen("data/actions-events-v1/catalog.json")
        old_records = {
            row["id"]: row
            for key in ("happeningTypes", "effectAssertions", "evidenceAssessments")
            for row in old[key]
            if "-PSY-LAYER-" in row["id"]
        }
        self.assertEqual(set(old_records), set(self.records))
        for identifier in self.records:
            self.assertEqual(without_governance(self.records[identifier]), without_governance(old_records[identifier]), identifier)
            if identifier not in activation.ACTIVE_IDS:
                self.assertEqual(self.records[identifier], old_records[identifier], identifier)

    def test_sources_relationships_ontology_and_architecture_unchanged(self):
        paths = (
            "data/relationship-intervention-v1/source-register.json",
            "data/relationship-intervention-v1/relationships.json",
            "data/relationship-intervention-v1/evidence-assessments.json",
            "data/entities.json",
            "data/relationships.json",
            "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER/architecture-escalations.json",
        )
        for relative in paths:
            self.assertEqual(read(ROOT / relative), frozen(relative), relative)

    def test_research_deferred_and_blockers_preserved(self):
        recommendations = read(ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER/governance-recommendations.json")
        research_effects = [x for x in recommendations["effectAssertionRecommendations"] if x["recommendation"] == "KEEP_RESEARCH_NEEDED"]
        self.assertEqual(len(research_effects), 23)
        self.assertTrue(all(x["candidateLifecycle"]["activationStatus"] == "NOT_ELIGIBLE" for x in research_effects))
        self.assertEqual({x["id"] for x in recommendations["architectureBlockers"]}, {"BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"})
        self.assertTrue(all(not x["architectureChangeAuthorized"] for x in recommendations["architectureBlockers"]))
        self.assertEqual(self.manifest["deferred"], {
            "revisionReview": 57, "retypeReview": 5, "splitReview": 2,
            "existingRelationshipResearchNeeded": 36, "effectAssertionsResearchNeeded": 23,
            "rejectedHypotheses": 151, "researchNeededHypotheses": 209,
        })
        progress = read(ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER/progress.json")
        self.assertEqual(len(progress["families"]), 14)
        self.assertTrue(all(stages["COMPLETE"] == "DONE" for stages in progress["families"].values()))

    def test_no_rds_target_and_bounded_evidence_semantics_preserved(self):
        entities = {x["id"]: x for x in read(ROOT / "data/entities.json")}
        for identifier in activation.ACTIVE_EFFECT_IDS:
            effect = self.records[identifier]
            self.assertEqual(effect["targetKind"], "DRIVER")
            self.assertEqual(entities[effect["targetId"]]["entityType"], "DRIVER")
        dispositions = {self.records[x]["synthesis"]["disposition"] for x in activation.ACTIVE_EVIDENCE_IDS}
        self.assertEqual(dispositions, {"MIXED", "SUPPORTS"})
        self.assertTrue(all(self.records[x]["synthesis"]["conflicts"] for x in activation.ACTIVE_EVIDENCE_IDS))

    def test_prior_pilots_and_network_state_are_unchanged(self):
        changed = subprocess.check_output([
            "git", "diff", "--name-only", PRE_ACTIVATION, "--",
            "data/relational-state-v1", "schemas/relational-state-v1", "scripts/relational_state_v1.py",
            "docs/governance/pilots/BIO-F01", "docs/governance/pilots/INF-F03", "docs/governance/pilots/SOC-F07",
        ], cwd=ROOT, text=True).strip()
        self.assertEqual(changed, "")

    def test_historical_audit_unchanged(self):
        for relative in (
            "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.json",
            "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.md",
        ):
            self.assertEqual((ROOT / relative).read_bytes().replace(b"\r\n", b"\n"), subprocess.check_output(["git", "show", f"{PRE_ACTIVATION}:{relative}"], cwd=ROOT).replace(b"\r\n", b"\n"))

    def test_materializer_is_deterministic(self):
        outputs = (activation.CATALOG_PATH, activation.MANIFEST_PATH, activation.DECISION_DATA_PATH, activation.DECISION_DOC)
        before = {path: path.read_bytes().replace(b"\r\n", b"\n") for path in outputs}
        activation.materialize()
        self.assertEqual(before, {path: path.read_bytes().replace(b"\r\n", b"\n") for path in outputs})

    def test_relationship_and_network_validation(self):
        result = ri.validate_repository()
        self.assertEqual((result["activeRelationships"], result["activeCausalRelationships"]), (457, 436))


if __name__ == "__main__":
    unittest.main()
