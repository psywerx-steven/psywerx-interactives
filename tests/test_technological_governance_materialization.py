"""Exact human authorization and additive-science guard for Technological governance."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import relationship_intervention_v1 as ri
import source_verification_v1 as sv

BASE = "1fdc5c01f7be9003c4a17b23ed3be1e4a19c9761"
IDS = ("HT-V1-TEC-LAYER-001", "EA-V1-TEC-LAYER-001", "EVA-AE-V1-TEC-LAYER-001")
SOURCE_IDS = {"SRC-613", "SRC-614", "SRC-615", "SRC-616"}


def current(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def baseline(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


class TechnologicalMaterializationTests(unittest.TestCase):
    def test_exact_additive_bundle_and_sources(self):
        path = "data/actions-events-v1/catalog.json"
        before, after = baseline(path), current(path)
        self.assertEqual(before["occurrences"], after["occurrences"])
        for collection, identifier in zip(
            ("happeningTypes", "effectAssertions", "evidenceAssessments"), IDS
        ):
            self.assertEqual(before[collection], after[collection][:-1])
            record = after[collection][-1]
            self.assertEqual(record["id"], identifier)
            self.assertEqual(
                (record["governance"]["lifecycleStatus"], record["governance"]["activationStatus"]),
                ("GOVERNED", "INACTIVE"),
            )
        self.assertEqual(before["authorizations"], after["authorizations"][:-1])
        authorization = after["authorizations"][-1]
        self.assertEqual(authorization["decisionId"], "GOV-TECHNOLOGICAL-LAYER-001-2026-09-22")
        self.assertEqual([x["id"] for x in authorization["authorizedObjects"]], list(IDS))

        path = "data/relationship-intervention-v1/source-register.json"
        before_sources, after_sources = baseline(path), current(path)
        self.assertEqual(before_sources["sources"], after_sources["sources"][:-4])
        sources = after_sources["sources"][-4:]
        self.assertEqual({x["id"] for x in sources}, SOURCE_IDS)
        self.assertEqual({x["doi"] for x in sources}, {
            "10.1093/pnasnexus/pgaf170", "10.1093/pnasnexus/pgag008",
            "10.1080/02650487.2024.2401319", "10.1016/j.chbah.2024.100058",
        })
        for source in sources:
            sv.validate_source(source)

    def test_exact_bounded_effect_and_mixed_evidence(self):
        catalog = current("data/actions-events-v1/catalog.json")
        ht = next(x for x in catalog["happeningTypes"] if x["id"] == IDS[0])
        ea = next(x for x in catalog["effectAssertions"] if x["id"] == IDS[1])
        eva = next(x for x in catalog["evidenceAssessments"] if x["id"] == IDS[2])
        self.assertEqual(ht["identitySourceIds"], ["SRC-613"])
        self.assertEqual((ea["typeId"], ea["targetKind"], ea["targetId"]), (IDS[0], "DRIVER", "PSY-003"))
        self.assertEqual((ea["property"], ea["change"]), ("LEVEL", "DECREASE"))
        self.assertEqual(ea["mechanismStatus"], "UNKNOWN")
        self.assertEqual(ea["knowledgeStatus"], "SUPPORTED_EFFECT")
        joined = json.dumps(ea)
        for qualifier in (
            "PLATFORM_SPECIFIC", "INTERFACE_SPECIFIC", "TASK_SPECIFIC",
            "TIME_SENSITIVE_TECHNOLOGY", "GENERALIZATION_UNCERTAIN",
        ):
            self.assertIn(qualifier, joined)
        for boundary in ("truth", "detection accuracy", "text-message", "behavior", "durable belief"):
            self.assertIn(boundary, joined.lower())
        self.assertEqual(eva["synthesis"]["disposition"], "MIXED")
        self.assertEqual(eva["synthesis"]["evidenceStrength"], "MODERATE")
        self.assertEqual(eva["synthesis"]["confidence"], "MODERATE")
        self.assertIn("policy-text", json.dumps(eva).lower())
        self.assertIn("NULL_FINDING", {x["disposition"] for x in eva["sourceFindings"]})

    def test_deferred_science_and_protected_records(self):
        hypotheses = current("data/candidates/actions-events-v1/TECHNOLOGICAL_LAYER/actions-events-hypotheses.json")
        deferred = {f"HYP-TEC-LAYER-AE-{number:03d}" for number in range(2, 7)}
        self.assertEqual({x["id"] for x in hypotheses if x["status"] == "RESEARCH_NEEDED"}, deferred)
        recommendations = current("data/candidates/actions-events-v1/TECHNOLOGICAL_LAYER/governance-recommendations.json")
        self.assertEqual(recommendations["existingRelationships"]["counts"], {
            "RETAIN_AS_IS": 3, "RETAIN_V1_INCOMPLETE": 13,
            "RETYPE_CANDIDATE": 31, "REVISION_CANDIDATE": 3,
            "RESEARCH_NEEDED": 22,
        })
        manifest = current("data/actions-events-v1/TECHNOLOGICAL_LAYER-materialization-manifest.json")
        self.assertEqual(manifest["newGoverned"], {
            "relationships": 0, "happeningTypes": 1, "effectAssertions": 1, "evidenceAssessments": 1,
        })
        self.assertEqual(manifest["newActive"], 0)
        self.assertEqual(manifest["preservedBlockedMetadata"], ["TEC-097", "TEC-098", "TEC-099"])
        for path in (
            "data/entities.json", "data/drivers.json", "data/families.json", "data/aliases.json",
            "data/relationships.json", "data/relationship-intervention-v1/relationships.json",
            "data/relationship-intervention-v1/evidence-assessments.json",
            "data/relationship-intervention-v1/interventions.json",
            "data/relationship-intervention-v1/intervention-effects.json",
            "data/relational-state-v1/catalog.json",
        ):
            self.assertEqual(baseline(path), current(path), path)

    def test_repository_contracts(self):
        ae.validate_catalog(current("data/actions-events-v1/catalog.json"), ae.Context.repository())
        ri.validate_repository()


if __name__ == "__main__":
    unittest.main()
