"""Exact authorization and additive-science guard for Informational closeout."""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "236b9c6bd0642a4704f3a845454846bb13a09def"


def current(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def baseline(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


class InformationalMaterializationTests(unittest.TestCase):
    def test_exact_additive_identity_and_sources(self):
        path = "data/actions-events-v1/catalog.json"
        before, after = baseline(path), current(path)
        self.assertEqual(before["occurrences"], after["occurrences"])
        biological = (ROOT / "data/actions-events-v1/BIOLOGICAL_LAYER-materialization-manifest.json").is_file()
        environmental = (ROOT / "data/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER-materialization-manifest.json").is_file()
        technological = (ROOT / "data/actions-events-v1/TECHNOLOGICAL_LAYER-materialization-manifest.json").is_file()
        added = 4 if technological else 3 if environmental else 2 if biological else 1
        self.assertEqual(before["happeningTypes"], after["happeningTypes"][:-added])
        self.assertEqual(before["authorizations"], after["authorizations"][:-added])
        if environmental:
            effect_added = 2 if technological else 1
            self.assertEqual(before["effectAssertions"], after["effectAssertions"][:-effect_added])
            self.assertEqual(before["evidenceAssessments"], after["evidenceAssessments"][:-effect_added])
        else:
            self.assertEqual(before["effectAssertions"], after["effectAssertions"])
            self.assertEqual(before["evidenceAssessments"], after["evidenceAssessments"])
        identity = next(x for x in after["happeningTypes"] if x["id"] == "HT-V1-INF-LAYER-001")
        self.assertEqual(identity["id"], "HT-V1-INF-LAYER-001")
        self.assertEqual(identity["identitySourceIds"], ["SRC-604", "SRC-605"])
        self.assertEqual((identity["governance"]["lifecycleStatus"], identity["governance"]["activationStatus"]),
                         ("GOVERNED", "INACTIVE"))
        self.assertIn("HT-CAND-INF-LAYER-0001", identity["provenance"]["originReferences"])
        authorization = next(x for x in after["authorizations"] if x["decisionId"] == "GOV-INFORMATIONAL-LAYER-001-2026-09-20")
        self.assertEqual([x["id"] for x in authorization["authorizedObjects"]], [identity["id"]])
        path = "data/relationship-intervention-v1/source-register.json"
        before, after = baseline(path), current(path)
        source_added = 13 if technological else 9 if environmental else 5 if biological else 2
        self.assertEqual(before["sources"], after["sources"][:-source_added])
        info_sources = [x for x in after["sources"] if x["id"] in {"SRC-604", "SRC-605"}]
        self.assertEqual({x["id"] for x in info_sources}, {"SRC-604", "SRC-605"})
        self.assertEqual({x["pmid"] for x in info_sources}, {"35082145", "30975450"})

    def test_deferred_science_and_blockers(self):
        data = ROOT / "data/candidates/actions-events-v1/INFORMATIONAL_LAYER"
        candidate = json.loads((data / "candidate-proposition-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(candidate["REL-CAND-INF-LAYER-0001"]["activationStatus"], "NOT_ELIGIBLE")
        self.assertEqual(candidate["REL-CAND-INF-LAYER-0001"]["governanceDecision"], "NOT_DECIDED")
        sources = json.loads((data / "source-registration-recommendations.json").read_text(encoding="utf-8"))
        self.assertFalse(sources["SRC-CAND-INF-LAYER-014"]["canonicalRegistrationPerformed"])
        queue = json.loads((ROOT / "data/candidates/actions-events-v1/INF-F03/source-registration-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(x["registrationStatus"] == "CANDIDATE_ONLY" for x in queue), 11)
        manifest = current("data/actions-events-v1/INFORMATIONAL_LAYER-materialization-manifest.json")
        self.assertEqual(manifest["newGoverned"], {"relationships": 0, "happeningTypes": 1, "effectAssertions": 0, "evidenceAssessments": 0})
        self.assertEqual(manifest["newActive"], 0)

    def test_no_other_production_science_changes(self):
        for path in ("data/entities.json", "data/families.json", "data/relationships.json",
                     "data/relationship-intervention-v1/relationships.json",
                     "data/relationship-intervention-v1/evidence-assessments.json",
                     "data/relational-state-v1/catalog.json"):
            self.assertEqual(baseline(path), current(path), path)


if __name__ == "__main__":
    unittest.main()
