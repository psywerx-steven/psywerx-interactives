"""Layer Scale-Up V2 process, benchmark, and scope checks."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import layer_scale_up_v2 as v2

DOC = ROOT / "docs/governance/LAYER_SCALE_UP_V2.md"
ROUTING = ROOT / "docs/governance/LAYER_SCALE_UP_V2_MODEL_ROUTING.md"
TEMPLATES = ROOT / "docs/governance/templates/layer-scale-up-v2"
REPORT = ROOT / "reports/layer-scale-up-v2/psychological-benchmark.json"


class LayerScaleUpV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = v2.psychological_benchmark()
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.routing = ROUTING.read_text(encoding="utf-8")

    def test_seven_stage_funnel_is_complete(self):
        for stage in range(7):
            self.assertIn(f"STAGE {stage}", self.doc)
        self.assertLess(self.doc.index("STAGE 0"), self.doc.index("STAGE 6"))

    def test_negative_coverage_and_no_exhaustive_deep_search(self):
        for outcome in (
            "NOT_APPLICABLE", "NO_PLAUSIBLE_MECHANISM",
            "INSUFFICIENT_PRELIMINARY_SIGNAL", "SEARCHED_NO_EXACT_EVIDENCE",
        ):
            self.assertIn(outcome, self.doc)
        self.assertIn("no candidate quotas", self.doc.casefold())
        self.assertIn("does not create a duty to conduct deep research for every cell", self.doc)

    def test_scientific_safeguards_are_preserved(self):
        lower = self.doc.casefold()
        for phrase in (
            "null and contrary", "cross-family", "rds", "source", "human authority",
            "activation", "protected science", "unknown", "practitioner actionability",
        ):
            self.assertIn(phrase, lower)

    def test_model_routing_is_bounded_and_outside_science_data(self):
        self.assertIn("GPT-5.6 Sol High", self.routing)
        self.assertIn("Astra XHigh", self.routing)
        for reason in (
            "ontology", "RDS causal-source", "architecture", "conflicting high-quality evidence",
            "high-consequence", "final small-set skeptical review",
        ):
            self.assertIn(reason.casefold(), self.routing.casefold())
        for routine in ("inventories", "deduplication", "routine source extraction", "test generation", "Git", "documentation"):
            self.assertIn(routine.casefold(), self.routing.casefold())
        search = subprocess.run([
            "git", "grep", "-l", "GPT-5.6\\|Astra XHigh", "--", "data", "schemas",
        ], cwd=ROOT, text=True, capture_output=True)
        self.assertIn(search.returncode, (0, 1), search.stderr)
        data_hits = search.stdout.splitlines()
        self.assertEqual(data_hits, [])

    def test_all_prompt_templates_exist_and_preserve_authority(self):
        expected = {
            "LAYER_KICKOFF.md", "FAMILY_RESEARCH.md", "ESCALATION.md",
            "GOVERNANCE_COMPRESSION.md", "ACTIVATION_AUDIT.md",
        }
        self.assertEqual({x.name for x in TEMPLATES.glob("*.md")}, expected)
        combined = "\n".join((TEMPLATES / name).read_text(encoding="utf-8") for name in expected)
        for phrase in ("no governance", "No record becomes governed or active", "Do not change scientific records", "Do not govern", "activation is not authorized"):
            self.assertIn(phrase.casefold(), combined.casefold())

    def test_psychological_inventory_benchmark(self):
        inventory = self.benchmark["inventory"]
        self.assertEqual((inventory["families"], inventory["familiesComplete"]), (14, 14))
        self.assertEqual((inventory["entities"], inventory["drivers"], inventory["rds"]), (135, 134, 1))
        self.assertEqual(inventory["rdsIds"], ["PSY-078"])
        self.assertEqual(inventory["existingRelationships"], 111)

    def test_psychological_candidate_blocker_and_dedup_benchmark(self):
        self.assertEqual(self.benchmark["formalCandidates"], {
            "relationshipCandidates": 1, "happeningTypes": 29,
            "effectAssertions": 30, "evidenceAssessments": 31,
        })
        signals = self.benchmark["reviewSignals"]
        self.assertEqual(signals["reviewReadyLifecycleRecords"], 45)
        self.assertEqual(signals["highPriorityGovernanceRows"], 82)
        self.assertEqual(signals["sourceOverlapIssues"], 64)
        self.assertEqual(signals["preservedBlockers"], 3)
        self.assertTrue(self.benchmark["validation"]["passed"])

    def test_benchmark_is_deterministic_and_claims_no_fake_savings(self):
        self.assertEqual(self.benchmark, self.report)
        self.assertEqual(self.benchmark["resourceAssessment"]["tokenOrCreditSavings"], "NOT_MEASURED")
        self.assertIn("Not numerically estimated", self.benchmark["resourceAssessment"]["modelEscalationRate"])

    def test_process_only_diff_scope(self):
        changed = subprocess.check_output([
            "git", "diff", "--name-only", "5e9a8ce241d7f4dc29845c50063c95530fd49a14", "--",
        ], cwd=ROOT, text=True).splitlines()
        self.assertTrue(changed)
        allowed = (".github/", "docs/governance/", "reports/layer-scale-up-v2/", "scripts/layer_scale_up_v2.py", "tests/test_layer_scale_up_v2.py")
        self.assertTrue(all(path.startswith(allowed) for path in changed), changed)
        self.assertFalse(any(path.startswith(("data/", "schemas/")) for path in changed))


if __name__ == "__main__":
    unittest.main()
