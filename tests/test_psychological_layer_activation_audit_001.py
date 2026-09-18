"""Read-only Psychological Layer activation-audit validation."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import build_psychological_activation_audit_001 as builder
import relationship_intervention_v1 as ri

DOC = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
AUDIT_PATH = DOC / "PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class PsychologicalLayerActivationAudit001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = read(AUDIT_PATH)
        cls.catalog = read(ROOT / "data/actions-events-v1/catalog.json")
        cls.relationships = read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]
        cls.ri_evidence = read(ROOT / "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]
        cls.records = (
            [x for x in cls.relationships if x["id"] == "REL-V1-PSY-LAYER-001"]
            + [x for x in cls.ri_evidence if x["id"] == "EVA-V1-PSY-LAYER-REL-001"]
            + [x for x in ae.all_records(cls.catalog) if "-PSY-LAYER-" in x["id"]]
        )
        cls.by_recommendation = {}
        for row in cls.audit["recommendations"]:
            cls.by_recommendation.setdefault(row["recommendation"], set()).add(row["id"])

    def test_exact_audited_set_and_no_state_change(self):
        self.assertEqual(len(self.records), 45)
        self.assertEqual({x["id"] for x in self.records}, {x["id"] for x in self.audit["recommendations"]})
        self.assertTrue(all(x["governance"]["lifecycleStatus"] == "GOVERNED" for x in self.records))
        self.assertTrue(all(x["governance"]["activationStatus"] == "INACTIVE" for x in self.records))
        self.assertTrue(self.audit["auditOnly"])
        self.assertFalse(self.audit["activationAuthorized"])
        self.assertEqual(self.audit["statusChanges"], 0)
        self.assertEqual(self.audit["counts"], {
            "audited": 45, "readyForActivationReview": 18,
            "keepInactive": 22, "blocked": 5, "newActive": 0,
        })

    def test_ready_subset_is_six_complete_bundles(self):
        ready_numbers = {2, 3, 5, 7, 12, 23}
        expected = {
            identifier
            for number in ready_numbers
            for identifier in (
                f"EA-V1-PSY-LAYER-{number:03d}",
                f"EVA-AE-V1-PSY-LAYER-{number:03d}",
            )
        }
        effect_types = {
            effect["typeId"] for effect in self.catalog["effectAssertions"]
            if effect["id"] in expected
        }
        expected |= effect_types
        self.assertEqual(self.by_recommendation[builder.READY], expected)
        self.assertEqual(len(expected), 18)
        self.assertEqual(len(self.audit["activationOrder"][1]["bundles"]), 6)

    def test_keep_inactive_is_exact_identity_only_subset(self):
        all_types = {x["id"] for x in self.catalog["happeningTypes"] if "-PSY-LAYER-" in x["id"]}
        ready_or_blocked_types = {
            "HT-V1-PSY-LAYER-001", "HT-V1-PSY-LAYER-002", "HT-V1-PSY-LAYER-003",
            "HT-V1-PSY-LAYER-004", "HT-V1-PSY-LAYER-006", "HT-V1-PSY-LAYER-011",
            "HT-V1-PSY-LAYER-022",
        }
        self.assertEqual(self.by_recommendation[builder.KEEP], all_types - ready_or_blocked_types)
        self.assertEqual(len(self.by_recommendation[builder.KEEP]), 22)
        types = {x["id"]: x for x in self.catalog["happeningTypes"]}
        self.assertTrue(all(types[x]["interventionSubset"] for x in self.by_recommendation[builder.KEEP]))

    def test_repetition_bundle_is_blocked_and_single_contribution(self):
        self.assertEqual(self.by_recommendation[builder.BLOCKED], {
            "REL-V1-PSY-LAYER-001", "EVA-V1-PSY-LAYER-REL-001",
            "HT-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001", "EVA-AE-V1-PSY-LAYER-001",
        })
        shared = self.audit["sharedContribution"]
        self.assertEqual(shared["id"], "CONTRIB-PSY-LAYER-REPETITION-001")
        self.assertTrue(shared["activationBlockedUntilExclusiveOrDeduplicated"])
        effect = next(x for x in self.catalog["effectAssertions"] if x["id"] == shared["effectAssertionId"])
        self.assertEqual(effect["contribution"]["groupId"], shared["id"])

    def test_exact_targets_and_no_rds_or_relational_state_target(self):
        entities = {x["id"]: x for x in read(ROOT / "data/entities.json")}
        expected = {
            "EA-V1-PSY-LAYER-001": "PSY-003", "EA-V1-PSY-LAYER-002": "PSY-003",
            "EA-V1-PSY-LAYER-003": "PSY-013", "EA-V1-PSY-LAYER-005": "PSY-024",
            "EA-V1-PSY-LAYER-007": "PSY-032", "EA-V1-PSY-LAYER-012": "PSY-066",
            "EA-V1-PSY-LAYER-023": "PSY-108",
        }
        effects = {x["id"]: x for x in self.catalog["effectAssertions"] if x["id"] in expected}
        self.assertEqual({identifier: row["targetId"] for identifier, row in effects.items()}, expected)
        self.assertTrue(all(row["targetKind"] == "DRIVER" for row in effects.values()))
        self.assertTrue(all(entities[row["targetId"]]["entityType"] == "DRIVER" for row in effects.values()))
        self.assertEqual(self.audit["rdsSafety"]["directTargets"], [])
        self.assertEqual(self.audit["rdsSafety"]["relationalStateTargets"], [])

    def test_evidence_semantics_sources_and_overlap_preserved(self):
        assessments = [x for x in self.catalog["evidenceAssessments"] if "-PSY-LAYER-" in x["id"]]
        self.assertEqual({x["synthesis"]["disposition"] for x in assessments}, {"MIXED", "SUPPORTS"})
        self.assertEqual(sum(x["synthesis"]["disposition"] == "SUPPORTS" for x in assessments), 1)
        self.assertTrue(all(x["synthesis"]["datasetOverlap"] for x in assessments))
        self.assertTrue(all(x["synthesis"]["conflicts"] for x in assessments))
        finding_sources = {finding["sourceId"] for x in assessments for finding in x["sourceFindings"]}
        relationship = next(x for x in self.relationships if x["id"] == "REL-V1-PSY-LAYER-001")
        self.assertEqual(set(self.audit["sourceAudit"]["canonicalSourceIds"]), finding_sources | set(relationship["sourceIds"]))
        self.assertEqual(self.audit["sourceAudit"]["unresolvedIdentities"], [])

    def test_three_blockers_preserved_without_architecture_change(self):
        blockers = {x["id"]: x for x in self.audit["blockers"]}
        self.assertEqual(set(blockers), {"BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"})
        self.assertTrue(all(x["status"] == "UNRESOLVED" for x in blockers.values()))
        self.assertEqual(blockers["BLK-PSY-001"]["affectedAuditedRecords"], [])
        self.assertEqual(blockers["BLK-PSY-002"]["affectedAuditedRecords"], [])
        self.assertEqual(set(blockers["BLK-PSY-003"]["affectedAuditedRecords"]), {
            "REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001",
        })
        self.assertFalse(self.audit["rdsSafety"]["newTargetSemantics"])

    def test_production_counts_and_validation_remain_unchanged(self):
        result = ri.validate_repository()
        self.assertEqual((result["activeRelationships"], result["activeCausalRelationships"]), (457, 436))
        self.assertEqual(self.audit["productionCounts"]["newActive"], 0)
        context = ae.Context.repository()
        self.assertEqual(ae.validate_catalog(self.catalog, context)["statusChanges"], 0)

    def test_builder_is_deterministic_and_read_only(self):
        before = {x["id"]: x for x in self.records}
        rebuilt = builder.build()
        self.assertEqual(rebuilt, self.audit)
        builder.main()
        self.assertEqual(read(AUDIT_PATH), self.audit)
        catalog = read(ROOT / "data/actions-events-v1/catalog.json")
        relationships = read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]
        evidence = read(ROOT / "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]
        after_records = (
            [x for x in relationships if x["id"] == "REL-V1-PSY-LAYER-001"]
            + [x for x in evidence if x["id"] == "EVA-V1-PSY-LAYER-REL-001"]
            + [x for x in ae.all_records(catalog) if "-PSY-LAYER-" in x["id"]]
        )
        self.assertEqual(before, {x["id"]: x for x in after_records})

    def test_only_audit_outputs_differ_from_merged_main(self):
        changed = subprocess.check_output([
            "git", "diff", "--name-only", "5e9a8ce241d7f4dc29845c50063c95530fd49a14", "--",
            "data", "docs", "schemas",
        ], cwd=ROOT, text=True).splitlines()
        self.assertEqual(set(changed), {
            "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.json",
            "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.md",
        })

    def test_human_document_states_no_activation(self):
        text = (DOC / "PSYCHOLOGICAL_LAYER_ACTIVATION_AUDIT_001.md").read_text(encoding="utf-8")
        for value in ("READ-ONLY ACTIVATION AUDIT", "READY_FOR_ACTIVATION_REVIEW", "KEEP_INACTIVE", "BLOCKED", "New `ACTIVE` = 0"):
            self.assertIn(value, text)


if __name__ == "__main__":
    unittest.main()
