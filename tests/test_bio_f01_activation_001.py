import importlib.util
import json
import sys
import unittest
from collections import defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "relationship-intervention-v1"
WORKSPACE = ROOT / "data" / "candidates" / "relationship-intervention-v1" / "workspace.json"
PILOT = ROOT / "docs" / "governance" / "pilots" / "BIO-F01"
ACTIVATION_DECISION = PILOT / "BIO_F01_ACTIVATION_DECISION_001.md"

ACTIVE_RELATIONSHIPS = {f"REL-V1-BIO-F01-{number:03d}" for number in range(1, 7)}
ACTIVE_CAUSAL_RELATIONSHIPS = {f"REL-V1-BIO-F01-{number:03d}" for number in range(1, 5)}
ACTIVE_INTERVENTIONS = {
    "INT-V1-BIO-F01-001",
    "INT-V1-BIO-F01-003",
    "INT-V1-BIO-F01-006",
    "INT-V1-BIO-F01-007",
    "INT-V1-BIO-F01-008",
}
INACTIVE_INTERVENTIONS = {
    "INT-V1-BIO-F01-002",
    "INT-V1-BIO-F01-004",
    "INT-V1-BIO-F01-005",
    "INT-V1-BIO-F01-010",
}
ACTIVE_EFFECTS = {
    "IE-V1-BIO-F01-001",
    "IE-V1-BIO-F01-003",
    "IE-V1-BIO-F01-004",
    "IE-V1-BIO-F01-005",
    "IE-V1-BIO-F01-006",
}
ACTIVE_EVIDENCE = {
    "EVA-V1-BIO-F01-REL-001",
    "EVA-V1-BIO-F01-REL-002",
    "EVA-V1-BIO-F01-REL-003",
    "EVA-V1-BIO-F01-REL-004",
    "EVA-V1-BIO-F01-REL-006",
    "EVA-V1-BIO-F01-REL-009",
    "EVA-V1-BIO-F01-IE-001",
    "EVA-V1-BIO-F01-IE-003",
    "EVA-V1-BIO-F01-IE-004",
    "EVA-V1-BIO-F01-IE-005",
    "EVA-V1-BIO-F01-IE-006",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load(path: Path, key: str | None = None):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload[key] if key else payload


V1 = load_module(
    "relationship_intervention_v1_for_bio_f01_activation",
    ROOT / "scripts" / "relationship_intervention_v1.py",
)


class BioF01Activation001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = V1.Catalog.from_repository()
        cls.relationships = load(DATA / "relationships.json", "relationships")
        cls.interventions = load(DATA / "interventions.json", "interventions")
        cls.effects = load(DATA / "intervention-effects.json", "interventionEffects")
        cls.evidence = load(DATA / "evidence-assessments.json", "evidenceAssessments")
        cls.pathways = load(DATA / "causal-pathways.json", "causalPathways")
        cls.workspace = load(WORKSPACE)

    def test_exact_relationship_activation_set_and_counts(self):
        active = {row["id"] for row in self.relationships if V1.governed_active(row)}
        self.assertEqual(active, ACTIVE_RELATIONSHIPS)
        traversed = {row["id"] for row in V1.causal_traversal(self.relationships)}
        self.assertEqual(traversed, ACTIVE_CAUSAL_RELATIONSHIPS)
        counts = V1.validate_repository()
        self.assertEqual(counts["legacyActiveRelationships"], 450)
        self.assertEqual(counts["legacyActiveCausalRelationships"], 431)
        self.assertEqual(counts["activeRelationships"], 456)
        self.assertEqual(counts["activeCausalRelationships"], 435)

    def test_exact_intervention_and_effect_activation_sets(self):
        active_interventions = {row["id"] for row in self.interventions if V1.governed_active(row)}
        inactive_interventions = {
            row["id"] for row in self.interventions
            if row["governance"]["lifecycleStatus"] == "GOVERNED"
            and row["governance"]["activationStatus"] == "INACTIVE"
        }
        active_effects = {row["id"] for row in self.effects if V1.governed_active(row)}
        self.assertEqual(active_interventions, ACTIVE_INTERVENTIONS)
        self.assertEqual(inactive_interventions, INACTIVE_INTERVENTIONS)
        self.assertEqual(active_effects, ACTIVE_EFFECTS)
        self.assertEqual(
            {row["id"] for row in V1.recommendation_eligible_effects(self.interventions, self.effects)},
            ACTIVE_EFFECTS,
        )
        effect_interventions = {row["interventionId"] for row in self.effects if V1.governed_active(row)}
        self.assertEqual(effect_interventions, ACTIVE_INTERVENTIONS)

    def test_all_eleven_evidence_assessments_are_active_and_scoped(self):
        active = {row["id"] for row in self.evidence if V1.governed_active(row)}
        self.assertEqual(active, ACTIVE_EVIDENCE)
        targets = {
            (row["assertion"]["objectType"], row["assertion"]["objectId"])
            for row in self.evidence if V1.governed_active(row)
        }
        expected_targets = (
            {("RELATIONSHIP", identifier) for identifier in ACTIVE_RELATIONSHIPS}
            | {("INTERVENTION_EFFECT", identifier) for identifier in ACTIVE_EFFECTS}
        )
        self.assertEqual(targets, expected_targets)

    def test_authorized_evidence_corrections_are_exact(self):
        by_id = {row["id"]: row for row in self.evidence}
        rel = by_id["EVA-V1-BIO-F01-REL-001"]
        self.assertIn("SRC-536", rel["evidenceRationale"])
        self.assertNotIn("BIOF01-EXT-007", rel["evidenceRationale"])
        for identifier, conflict_source in (
            ("EVA-V1-BIO-F01-IE-005", "SRC-541"),
            ("EVA-V1-BIO-F01-IE-006", "SRC-549"),
        ):
            assessment = by_id[identifier]
            self.assertEqual(assessment["evidenceDisposition"], "MIXED")
            self.assertEqual(assessment["evidenceStrength"], "MODERATE")
            self.assertEqual(assessment["confidence"], "MODERATE")
            self.assertIn(conflict_source, assessment["sourceIds"])
            self.assertEqual(assessment["conflictingEvidence"]["sourceIds"], [conflict_source])
        self.assertIn("between-group", by_id["EVA-V1-BIO-F01-IE-005"]["conflictingEvidence"]["summary"])
        melatonin_text = (
            by_id["EVA-V1-BIO-F01-IE-006"]["evidenceRationale"]
            + " "
            + by_id["EVA-V1-BIO-F01-IE-006"]["conflictingEvidence"]["summary"]
        ).casefold()
        self.assertIn("no significant", melatonin_text)
        self.assertIn("dlmo", melatonin_text)
        self.assertIn("sleep-promoting", melatonin_text)

    def test_no_supplemental_alias_remains_in_active_evidence_rationale(self):
        for assessment in self.evidence:
            self.assertNotIn("BIOF01-EXT-", assessment["evidenceRationale"])
            self.assertTrue(set(assessment["sourceIds"]) <= self.catalog.source_ids)
            self.assertTrue(
                set(assessment["conflictingEvidence"]["sourceIds"])
                <= self.catalog.source_ids
            )
            self.assertIsNone(assessment["quantitativeEstimate"])
            self.assertNotIn("graphWeight", assessment)

    def test_activation_provenance_is_exact(self):
        active_records = [
            *[row for row in self.relationships if row["id"] in ACTIVE_RELATIONSHIPS],
            *[row for row in self.interventions if row["id"] in ACTIVE_INTERVENTIONS],
            *[row for row in self.effects if row["id"] in ACTIVE_EFFECTS],
            *[row for row in self.evidence if row["id"] in ACTIVE_EVIDENCE],
        ]
        self.assertEqual(len(active_records), 27)
        for record in active_records:
            transition = record["governance"]["transitionProvenance"][-1]
            self.assertEqual(transition["actorClass"], "AUTHORIZED_HUMAN_GOVERNOR")
            self.assertEqual(transition["fromState"]["activationStatus"], "INACTIVE")
            self.assertEqual(transition["toState"]["activationStatus"], "ACTIVE")
            self.assertEqual(
                transition["governanceDecisionRecord"],
                "docs/governance/pilots/BIO-F01/BIO_F01_ACTIVATION_DECISION_001.md",
            )
            self.assertIn("f3a933d09f98c08fa8c31374ed17658a660943aa", transition["provenance"])
        self.assertTrue(ACTIVATION_DECISION.is_file())

    def test_noncausal_and_cyclic_semantics_are_preserved(self):
        by_id = {row["id"]: row for row in self.relationships}
        self.assertEqual(by_id["REL-V1-BIO-F01-005"]["predicate"], "ASSOCIATED_WITH")
        self.assertEqual(by_id["REL-V1-BIO-F01-005"]["symmetry"], "SYMMETRIC")
        self.assertFalse(by_id["REL-V1-BIO-F01-005"]["causalClaim"])
        self.assertEqual(by_id["REL-V1-BIO-F01-006"]["predicate"], "DERIVED_FROM")
        self.assertFalse(by_id["REL-V1-BIO-F01-006"]["causalClaim"])
        self.assertIn("external", by_id["REL-V1-BIO-F01-006"]["boundaryConditions"].casefold())
        cyclic = by_id["REL-V1-BIO-F01-002"]
        self.assertEqual(cyclic["polarity"], "CONTEXT_DEPENDENT")
        self.assertEqual(cyclic["functionalForm"]["kind"], "CYCLIC_STATE_DEPENDENT")

    def test_no_rds_causal_endpoint_or_direct_effect_target(self):
        rds = {
            identifier for identifier, row in self.catalog.entities.items()
            if row["entityType"] == "RELATIONAL_DERIVED_STATE"
        }
        for relationship in V1.causal_traversal(self.relationships):
            self.assertNotIn(relationship["sourceEntityId"], rds)
            self.assertNotIn(relationship["targetEntityId"], rds)
        for effect in self.effects:
            self.assertEqual(effect["targetKind"], "DRIVER")
            self.assertNotIn(effect["targetDriverId"], rds)
        target_ids = {row["targetDriverId"] for row in self.effects}
        self.assertNotIn("BIO-073", target_ids)  # Chronotype
        self.assertNotIn("BIO-074", target_ids)  # Physiological Sleep Need

    def test_excluded_records_remain_nonactive(self):
        relationship_candidates = {row["id"]: row for row in self.workspace["relationships"]}
        effect_candidates = {row["id"]: row for row in self.workspace["interventionEffects"]}
        intervention_candidates = {row["id"]: row for row in self.workspace["interventions"]}
        for identifier in {"REL-CAND-BIO-F01-005", "REL-CAND-BIO-F01-007", "REL-CAND-BIO-F01-008"}:
            self.assertEqual(relationship_candidates[identifier]["governance"]["activationStatus"], "NOT_ELIGIBLE")
        for identifier in {"IE-CAND-BIO-F01-002", "IE-CAND-BIO-F01-007", "IE-CAND-BIO-F01-008", "IE-CAND-BIO-F01-009"}:
            self.assertEqual(effect_candidates[identifier]["governance"]["activationStatus"], "NOT_ELIGIBLE")
        for identifier in {"INT-CAND-BIO-F01-009", "INT-CAND-BIO-F01-011"}:
            self.assertEqual(intervention_candidates[identifier]["governance"]["activationStatus"], "NOT_ELIGIBLE")
        self.assertEqual(self.pathways, [])
        self.assertFalse(any(row["relationFamily"] == "MODERATION" for row in self.relationships))

    def test_graph_metrics_and_no_new_cycles_reciprocals_or_duplicates(self):
        family = {
            identifier for identifier, entity in self.catalog.entities.items()
            if entity.get("primaryFamilyId") == "BIO-F01"
        }
        legacy = [
            row for row in self.catalog.legacy_relationships.values()
            if row["governanceStatus"] == "ACTIVE" and row["relationFamily"] == "CAUSAL"
        ]
        new = V1.causal_traversal(self.relationships)

        def endpoints(row):
            if "subjectEntityId" in row:
                return row["subjectEntityId"], row["objectEntityId"]
            return row["sourceEntityId"], row["targetEntityId"]

        def metrics(edges):
            incident = [row for row in edges if family & set(endpoints(row))]
            internal = [row for row in incident if set(endpoints(row)) <= family]
            same_layer = []
            cross_layer = []
            for row in incident:
                source, target = endpoints(row)
                if source in family and target in family:
                    continue
                other = target if source in family else source
                if self.catalog.entities[other]["layer"] == "Biological":
                    same_layer.append(row)
                else:
                    cross_layer.append(row)
            degree = defaultdict(int)
            for row in incident:
                source, target = endpoints(row)
                degree[source] += 1
                degree[target] += 1
            isolated = sum(degree[identifier] == 0 for identifier in family)
            return len(incident), len(internal), len(same_layer), len(cross_layer), isolated

        self.assertEqual(metrics(legacy), (6, 1, 3, 2, 8))
        self.assertEqual(metrics(legacy + new), (10, 3, 4, 3, 6))

        adjacency = defaultdict(set)
        for row in legacy:
            source, target = endpoints(row)
            adjacency[source].add(target)

        def reachable(start, goal):
            queue = deque([start])
            seen = {start}
            while queue:
                node = queue.popleft()
                for nxt in adjacency[node]:
                    if nxt == goal:
                        return True
                    if nxt not in seen:
                        seen.add(nxt)
                        queue.append(nxt)
            return False

        for row in new:
            source, target = endpoints(row)
            self.assertFalse(reachable(target, source), row["id"])
            self.assertNotIn(source, adjacency[target], row["id"])
            adjacency[source].add(target)

        propositions = defaultdict(list)
        for row in [*self.catalog.legacy_relationships.values(), *self.relationships]:
            source, target = endpoints(row)
            propositions[(source, row["predicate"], target)].append(row["id"])
        self.assertFalse(any(len(ids) > 1 and set(ids) & ACTIVE_RELATIONSHIPS for ids in propositions.values()))

    def test_existing_revisions_and_rejections_remain_non_governed(self):
        revisions = (PILOT / "BIO_F01_EXISTING_RELATIONSHIP_REVISION_PROPOSALS.md").read_text(encoding="utf-8")
        self.assertIn("Nothing in this document mutates, supersedes, or deactivates", revisions)
        for number in range(1, 6):
            self.assertIn(f"REL-REV-BIO-F01-B0{number}", revisions)
        manifest = load(DATA / "materialization-manifest.json")
        self.assertEqual(
            [row["decisionId"] for row in manifest["rejectedHypotheses"]],
            [f"BIOF01-D-H0{number}" for number in range(1, 6)],
        )


if __name__ == "__main__":
    unittest.main()
