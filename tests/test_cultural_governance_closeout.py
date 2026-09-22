"""Exact zero-materialization Cultural governance and closeout checks."""

import json
import subprocess
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "add22dce5ebae8f26c6ebf9b1d302ceebbf992e9"
DATA = ROOT / "data/candidates/actions-events-v1/CULTURAL_LAYER"


def current(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def baseline(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


class CulturalGovernanceCloseoutTests(unittest.TestCase):
    def test_exact_human_decision_and_zero_materialization(self):
        decision = current("data/candidates/actions-events-v1/CULTURAL_LAYER/governance-decision-001.json")
        manifest = current("data/actions-events-v1/CULTURAL_LAYER-materialization-manifest.json")
        self.assertEqual(decision["decisionId"], "GOV-CULTURAL-LAYER-001-2026-09-21")
        self.assertEqual(decision["materialization"], {"relationships":0,"happeningTypes":0,"effectAssertions":0,"evidenceAssessments":0,"canonicalSources":0})
        self.assertEqual((decision["newGoverned"], decision["newActive"]), (0,0))
        self.assertFalse(decision["activationAuditRequired"])
        self.assertEqual(manifest["newGoverned"], {"relationships":0,"happeningTypes":0,"effectAssertions":0,"evidenceAssessments":0})
        self.assertEqual((manifest["newActive"], manifest["canonicalSources"]), (0, []))

    def test_review_dispositions_and_blocker_unchanged(self):
        reviews = current("data/candidates/actions-events-v1/CULTURAL_LAYER/relationship-review-registry.json")
        self.assertEqual(Counter(x["disposition"] for x in reviews.values()), {
            "RETAIN_AS_IS":1, "RETAIN_V1_INCOMPLETE":7, "REVISION_CANDIDATE":6,
            "RETYPE_CANDIDATE":5, "RESEARCH_NEEDED":36,
        })
        self.assertTrue(all(x["productionChangeAuthorized"] is False for x in reviews.values()))
        self.assertEqual(reviews["REL-CUL-042"]["disposition"], "RESEARCH_NEEDED")
        self.assertEqual([x["id"] for x in current("data/candidates/actions-events-v1/CULTURAL_LAYER/architecture-escalations.json")], ["ARCH-CUL-LAYER-0001"])
        self.assertEqual([x["id"] for x in current("data/candidates/actions-events-v1/CULTURAL_LAYER/astra-escalation-queue.json")], ["ASTRA-CUL-LAYER-001"])

    def test_complete_coverage_and_no_candidate_materialization(self):
        progress = current("data/candidates/actions-events-v1/CULTURAL_LAYER/progress.json")
        coverage = current("data/candidates/actions-events-v1/CULTURAL_LAYER/negative-coverage-registry.json")
        rds = current("data/candidates/actions-events-v1/CULTURAL_LAYER/rds-review.json")
        self.assertEqual(len(progress["families"]), 13)
        self.assertEqual(set(progress["families"].values()), {"COMPLETE"})
        self.assertEqual(len(coverage), 91)
        self.assertEqual(sum(x["entityType"] == "DRIVER" for x in coverage.values()), 90)
        self.assertEqual([x["id"] for x in rds], ["CUL-088"])
        self.assertEqual(current("data/candidates/actions-events-v1/CULTURAL_LAYER/actions-events-identity-registry.json"), {})
        self.assertEqual(current("data/candidates/actions-events-v1/CULTURAL_LAYER/candidate-proposition-registry.json"), {})
        self.assertEqual(current("data/candidates/actions-events-v1/CULTURAL_LAYER/evidence-assessments.json"), [])

    def test_all_production_science_matches_frozen_baseline(self):
        for path in (
            "data/entities.json", "data/families.json", "data/relationships.json",
            "data/relationship-intervention-v1/relationships.json",
            "data/relationship-intervention-v1/evidence-assessments.json",
            "data/relationship-intervention-v1/interventions.json",
            "data/relationship-intervention-v1/intervention-effects.json",
            "data/relational-state-v1/catalog.json",
        ):
            self.assertEqual(baseline(path), current(path), path)
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import cultural_layer_v2
        cultural_layer_v2.validate_protection()


if __name__ == "__main__":
    unittest.main()
