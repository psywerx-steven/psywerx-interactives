"""Exact authorization and additive-science guard for ENV governance."""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "f75d99b326d9065c1e97ba89a3d5e395d52c0bb0"


def current(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def baseline(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


class PhysicalEnvironmentalMaterializationTests(unittest.TestCase):
    def test_exact_additive_bundle_and_sources(self):
        path = "data/actions-events-v1/catalog.json"
        before, after = baseline(path), current(path)
        self.assertEqual(before["occurrences"], after["occurrences"])
        self.assertEqual(before["happeningTypes"], after["happeningTypes"][:-1])
        self.assertEqual(before["effectAssertions"], after["effectAssertions"][:-1])
        self.assertEqual(before["evidenceAssessments"], after["evidenceAssessments"][:-1])
        self.assertEqual(before["authorizations"], after["authorizations"][:-1])
        ht, ea, eva = after["happeningTypes"][-1], after["effectAssertions"][-1], after["evidenceAssessments"][-1]
        self.assertEqual((ht["id"], ea["id"], eva["id"]),
                         ("HT-V1-ENV-LAYER-001", "EA-V1-ENV-LAYER-001", "EVA-AE-V1-ENV-LAYER-001"))
        for record in (ht, ea, eva):
            self.assertEqual((record["governance"]["lifecycleStatus"], record["governance"]["activationStatus"]),
                             ("GOVERNED", "INACTIVE"))
        self.assertEqual(ht["identitySourceIds"], ["SRC-609", "SRC-610", "SRC-611"])
        authorization = after["authorizations"][-1]
        self.assertEqual(authorization["decisionId"], "GOV-PHYSICAL-ENVIRONMENTAL-LAYER-001-2026-09-21")
        self.assertEqual([x["id"] for x in authorization["authorizedObjects"]], [ht["id"], ea["id"], eva["id"]])

        path = "data/relationship-intervention-v1/source-register.json"
        before, after = baseline(path), current(path)
        self.assertEqual(before["sources"], after["sources"][:-4])
        sources = after["sources"][-4:]
        self.assertEqual({x["id"] for x in sources}, {"SRC-609", "SRC-610", "SRC-611", "SRC-612"})
        self.assertEqual({x["pmid"] for x in sources}, {"39516236", "38250104", "35726335", "34900906"})

    def test_bounded_effect_and_mixed_evidence(self):
        catalog = current("data/actions-events-v1/catalog.json")
        ea = next(x for x in catalog["effectAssertions"] if x["id"] == "EA-V1-ENV-LAYER-001")
        eva = next(x for x in catalog["evidenceAssessments"] if x["id"] == "EVA-AE-V1-ENV-LAYER-001")
        self.assertEqual((ea["typeId"], ea["targetKind"], ea["targetId"]),
                         ("HT-V1-ENV-LAYER-001", "DRIVER", "PSY-050"))
        self.assertEqual((ea["property"], ea["change"]), ("LEVEL", "INCREASE"))
        self.assertIn("multisensory package", ea["scope"]["context"])
        self.assertIn("No enduring mood", ea["scope"]["boundaryConditions"])
        self.assertEqual(eva["synthesis"]["disposition"], "MIXED")
        joined = json.dumps(eva)
        for phrase in ("cognition null", "Both walking groups improved", "overlap", "heterogeneity"):
            self.assertIn(phrase.lower(), joined.lower())
        self.assertEqual({x["disposition"] for x in eva["sourceFindings"]}, {"SUPPORTS", "MIXED"})

    def test_deferred_science_and_no_other_production_changes(self):
        effects = current("data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER/actions-events-hypotheses.json")
        self.assertEqual(sum(x["status"] == "RESEARCH_NEEDED" for x in effects), 3)
        manifest = current("data/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER-materialization-manifest.json")
        self.assertEqual(manifest["newGoverned"], {"relationships": 0, "happeningTypes": 1,
                                                    "effectAssertions": 1, "evidenceAssessments": 1})
        self.assertEqual(manifest["newActive"], 0)
        for path in ("data/entities.json", "data/families.json", "data/relationships.json",
                     "data/relationship-intervention-v1/relationships.json",
                     "data/relationship-intervention-v1/evidence-assessments.json",
                     "data/relationship-intervention-v1/interventions.json",
                     "data/relationship-intervention-v1/intervention-effects.json",
                     "data/relational-state-v1/catalog.json"):
            self.assertEqual(baseline(path), current(path), path)


if __name__ == "__main__":
    unittest.main()
