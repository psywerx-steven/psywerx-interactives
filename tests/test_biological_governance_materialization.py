"""Exact authorization and additive-science guard for Biological closeout."""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "85645e46b8c61b883ba5cf91674e6ffcbb90fb7b"


def current(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def baseline(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


class BiologicalMaterializationTests(unittest.TestCase):
    def test_exact_additive_identity_and_sources(self):
        path = "data/actions-events-v1/catalog.json"
        before, after = baseline(path), current(path)
        self.assertEqual(before["occurrences"], after["occurrences"])
        environmental = (ROOT / "data/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER-materialization-manifest.json").is_file()
        technological = (ROOT / "data/actions-events-v1/TECHNOLOGICAL_LAYER-materialization-manifest.json").is_file()
        added = 3 if technological else 2 if environmental else 1
        self.assertEqual(before["happeningTypes"], after["happeningTypes"][:-added])
        self.assertEqual(before["authorizations"], after["authorizations"][:-added])
        if environmental:
            effect_added = 2 if technological else 1
            self.assertEqual(before["effectAssertions"], after["effectAssertions"][:-effect_added])
            self.assertEqual(before["evidenceAssessments"], after["evidenceAssessments"][:-effect_added])
        else:
            self.assertEqual(before["effectAssertions"], after["effectAssertions"])
            self.assertEqual(before["evidenceAssessments"], after["evidenceAssessments"])
        identity = next(x for x in after["happeningTypes"] if x["id"] == "HT-V1-BIO-LAYER-001")
        self.assertEqual(identity["id"], "HT-V1-BIO-LAYER-001")
        self.assertEqual(identity["identitySourceIds"], ["SRC-606", "SRC-607", "SRC-608"])
        self.assertEqual((identity["governance"]["lifecycleStatus"], identity["governance"]["activationStatus"]),
                         ("GOVERNED", "INACTIVE"))
        self.assertIn("HT-CAND-BIO-LAYER-0001", identity["provenance"]["originReferences"])
        authorization = next(x for x in after["authorizations"] if x["decisionId"] == "GOV-BIOLOGICAL-LAYER-001-2026-09-21")
        self.assertEqual([x["id"] for x in authorization["authorizedObjects"]], [identity["id"]])
        path = "data/relationship-intervention-v1/source-register.json"
        before, after = baseline(path), current(path)
        source_added = 11 if technological else 7 if environmental else 3
        self.assertEqual(before["sources"], after["sources"][:-source_added])
        bio_sources = [x for x in after["sources"] if x["id"] in {"SRC-606", "SRC-607", "SRC-608"}]
        self.assertEqual({x["id"] for x in bio_sources}, {"SRC-606", "SRC-607", "SRC-608"})
        self.assertEqual({x["pmid"] for x in bio_sources}, {"1528206", "10586387", "2262896"})

    def test_deferred_science_and_blockers(self):
        data = ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER"
        effect = current("data/candidates/actions-events-v1/BIOLOGICAL_LAYER/actions-events-hypotheses.json")[0]
        evidence = current("data/candidates/actions-events-v1/BIOLOGICAL_LAYER/evidence-assessments.json")[0]
        self.assertEqual((effect["status"], effect["activationStatus"]), ("RESEARCH_NEEDED", "NOT_ELIGIBLE"))
        self.assertEqual((evidence["disposition"], evidence["activationStatus"]), ("MIXED", "NOT_ELIGIBLE"))
        self.assertEqual(len(current("data/candidates/actions-events-v1/BIOLOGICAL_LAYER/astra-escalation-queue.json")), 1)
        self.assertEqual(len(current("data/candidates/actions-events-v1/BIOLOGICAL_LAYER/architecture-escalations.json")), 1)
        manifest = current("data/actions-events-v1/BIOLOGICAL_LAYER-materialization-manifest.json")
        self.assertEqual(manifest["newGoverned"], {"relationships": 0, "happeningTypes": 1, "effectAssertions": 0, "evidenceAssessments": 0})
        self.assertEqual(manifest["newActive"], 0)
        self.assertTrue((data / "protected-baseline.json").exists())

    def test_no_other_production_science_changes(self):
        for path in ("data/entities.json", "data/families.json", "data/relationships.json",
                     "data/relationship-intervention-v1/relationships.json",
                     "data/relationship-intervention-v1/evidence-assessments.json",
                     "data/relationship-intervention-v1/interventions.json",
                     "data/relationship-intervention-v1/intervention-effects.json",
                     "data/relational-state-v1/catalog.json"):
            self.assertEqual(baseline(path), current(path), path)


if __name__ == "__main__":
    unittest.main()
