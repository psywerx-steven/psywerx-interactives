"""Final eight-Layer checkpoint and backlog completeness tests."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports/layer-scale-up-v2"
sys.path.insert(0, str(ROOT / "scripts"))
import layer_scale_up_final_closeout as final


class LayerScaleUpFinalCloseoutTests(unittest.TestCase):
    def test_all_eight_layers_and_105_families(self):
        report = json.loads((REPORTS / "layer-scale-up-final-completeness.json").read_text(encoding="utf-8"))
        self.assertEqual(report["totals"], {"layers": 8, "families": 105, "drivers": 770, "rds": 41, "entities": 811})
        self.assertEqual(report["completedCandidateAudits"], 8)
        self.assertEqual(report["completedHumanGovernance"], 8)
        self.assertEqual({x["candidateAudit"] for x in report["layers"]}, {"COMPLETE"})
        self.assertEqual({x["humanGovernance"] for x in report["layers"]}, {"COMPLETE"})

    def test_layer_counts_sum_and_match_current_ontology(self):
        report, _ = final.build()
        self.assertEqual(sum(x["families"] for x in report["layers"]), 105)
        self.assertEqual(sum(x["drivers"] for x in report["layers"]), 770)
        self.assertEqual(sum(x["rds"] for x in report["layers"]), 41)
        self.assertEqual(sum(x["entities"] for x in report["layers"]), 811)

    def test_backlog_has_all_required_classes_and_fields(self):
        backlog = json.loads((REPORTS / "post-scale-up-blocker-backlog.json").read_text(encoding="utf-8"))
        prefixes = {x[0] for x in backlog["countsByCategory"]}
        self.assertEqual(prefixes, set("ABCDEFGHIJ"))
        required = {"id", "category", "layer", "affectedRecords", "scientificProblem", "architectureProblem", "currentSafeState", "consequenceOfLeavingUnresolved", "blocksActiveExecution", "recommendedFutureWorkType"}
        self.assertTrue(all(set(x) == required for x in backlog["items"]))
        ids = {x["id"] for x in backlog["items"]}
        for identifier in ["BLK-ENV-ACTIVATION-001", "BLK-TEC-ACTIVATION-001", "BLK-PSY-003", "BLK-BIO-RDS-001", "BLK-CUL-RDS-001", "HYP-INF-F03-H20", "HYP-SOC-F07-H12", "HYP-SOC-F07-H20", "BLK-INS-RDS-001"]:
            self.assertIn(identifier, ids)

    def test_checkpoint_is_process_only(self):
        report = json.loads((REPORTS / "layer-scale-up-program-status.json").read_text(encoding="utf-8"))
        self.assertFalse(report["productionScienceChangedByFinalCloseout"])
        self.assertEqual(report["openCandidateLayerPRsAfterCloseout"], 0)
        env = next(x for x in report["layers"] if x["layer"] == "Physical / Environmental")
        tech = next(x for x in report["layers"] if x["layer"] == "Technological")
        self.assertEqual((env["activationStatus"], tech["activationStatus"]), ("BLOCKED", "BLOCKED"))

    def test_documents_exist(self):
        for name in ["LAYER_SCALE_UP_PROGRAM_STATUS.md", "LAYER_SCALE_UP_FINAL_COMPLETENESS.md", "POST_SCALE_UP_BLOCKER_BACKLOG.md"]:
            self.assertTrue((ROOT / "docs/governance" / name).is_file())


if __name__ == "__main__":
    unittest.main()
