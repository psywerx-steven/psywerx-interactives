"""Read-only post-scale-up dependency roadmap validation."""

import hashlib
import json
import unittest
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/governance/post-scale-up"
DOCS = ROOT / "docs/governance/post-scale-up"
SOURCE = ROOT / "reports/layer-scale-up-v2/post-scale-up-blocker-backlog.json"
COMPLETE = ROOT / "reports/layer-scale-up-v2/layer-scale-up-final-completeness.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class PostScaleUpGovernanceRoadmapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(SOURCE)
        cls.dep = read(DATA / "blocker-dependency-map.json")
        cls.roots = read(DATA / "root-issues.json")
        cls.packages = read(DATA / "work-packages.json")
        cls.packets = read(DATA / "decision-packets.json")

    def test_final_scale_up_baseline_is_exact(self):
        complete = read(COMPLETE)
        self.assertEqual(complete["totals"], {"layers": 8, "families": 105, "drivers": 770, "rds": 41, "entities": 811})
        self.assertEqual(complete["completedCandidateAudits"], 8)
        self.assertEqual(complete["completedHumanGovernance"], 8)

    def test_all_original_items_and_flags_are_preserved(self):
        original = {row["id"]: row for row in self.source["items"]}
        mapped = {row["id"]: row for row in self.dep["items"]}
        self.assertEqual(len(original), 44)
        self.assertEqual(set(original), set(mapped))
        for identifier, row in original.items():
            normalized = mapped[identifier]
            self.assertEqual(normalized["class"], row["category"])
            self.assertEqual(normalized["layer"], row["layer"])
            self.assertEqual(normalized["affectedRecords"], row["affectedRecords"])
            self.assertEqual(normalized["blocksActiveExecution"], row["blocksActiveExecution"])
            self.assertEqual(normalized["currentSafeState"], row["currentSafeState"])
        self.assertEqual(sum(row["blocksActiveExecution"] for row in mapped.values()), 24)

    def test_normalization_counts_and_roots(self):
        self.assertEqual(self.dep["trueRootIssueCount"], 10)
        self.assertEqual(self.dep["normalizationCounts"], {
            "DEPENDENT_BLOCKER": 20, "DOWNSTREAM_MANIFESTATION": 4,
            "INACTIVE_BUT_SAFE": 2, "SCIENTIFIC_RESEARCH_QUEUE": 8,
            "SEMANTIC_DEBT": 8, "SOURCE_DEBT": 2,
        })
        root_ids = {row["id"] for row in self.roots["roots"]}
        self.assertEqual(len(root_ids), 10)
        self.assertTrue(all(row["rootIssueId"] in root_ids for row in self.dep["items"]))
        downstream = [row for row in self.dep["items"] if row["normalizedType"] == "DOWNSTREAM_MANIFESTATION"]
        self.assertEqual({row["id"] for row in downstream}, {
            "HYP-SOC-F07-H12", "HYP-SOC-F07-H20", "INACTIVE-ENV-BUNDLE-001", "INACTIVE-TEC-BUNDLE-001"})
        self.assertTrue(all(row["duplicateOrDerivativeOf"] for row in downstream))

    def test_dependency_graph_is_acyclic_and_explained(self):
        root_ids = {row["id"] for row in self.roots["roots"]}
        item_ids = {row["id"] for row in self.dep["items"]}
        nodes = root_ids | item_ids
        edges = []
        for row in self.roots["roots"]:
            edges.extend((dependency, row["id"]) for dependency in row["dependencies"])
        for row in self.dep["items"]:
            edges.extend((dependency, row["id"]) for dependency in row["dependsOn"])
        self.assertTrue(all(source in nodes and target in nodes for source, target in edges))
        outgoing, indegree = defaultdict(list), Counter({node: 0 for node in nodes})
        for source, target in edges:
            outgoing[source].append(target)
            indegree[target] += 1
        queue = deque(node for node in nodes if indegree[node] == 0)
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for target in outgoing[node]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)
        self.assertEqual(visited, len(nodes), "Dependency graph contains an unexplained cycle")

    def test_rds_definition_and_causality_are_separate(self):
        roots = {row["id"]: row for row in self.roots["roots"]}
        definition = roots["ROOT-RDS-DEFINITION-DERIVATION-001"]
        causal = roots["ROOT-RDS-CAUSAL-SOURCE-001"]
        self.assertNotEqual(definition["id"], causal["id"])
        self.assertIn(definition["id"], causal["dependencies"])
        self.assertEqual(definition["directOriginalItems"], 5)
        self.assertEqual(causal["directOriginalItems"], 5)

    def test_semantic_debt_is_deduplicated(self):
        debt = self.roots["relationshipSemanticDebt"]
        self.assertEqual(debt["layerReviewRows"], 172)
        self.assertEqual(debt["uniqueRelationships"], 141)
        self.assertEqual(debt["duplicateCrossLayerReviewRowsCollapsed"], 31)
        self.assertEqual(sum(debt["workstreamCounts"].values()), 141)
        self.assertEqual(debt["architectureDependentRelationships"] + debt["architectureIndependentRelationships"], 141)
        self.assertTrue(all(not row["productionMutationAuthorized"] for row in debt["records"]))

    def test_work_packages_and_packets_stop_before_governance(self):
        self.assertEqual(len(self.packages["workPackages"]), 10)
        self.assertEqual(len(self.packets["decisionPackets"]), 6)
        for package in self.packages["workPackages"]:
            self.assertEqual(package["stages"]["D_humanGovernanceDecision"], "NOT_STARTED")
            self.assertEqual(package["stages"]["E_implementation"], "NOT_STARTED")
            self.assertEqual(package["stages"]["F_migrationRevalidation"], "NOT_STARTED")
            self.assertEqual(package["stages"]["G_scientificReadjudication"], "NOT_STARTED")
        self.assertEqual({row["humanDecisionStatus"] for row in self.packets["decisionPackets"]}, {"REQUIRED_NOT_TAKEN"})

    def test_protected_science_ontology_lifecycle_sources_and_network_state(self):
        protected = read(DATA / "protected-baseline.json")
        for relative, expected in protected["productionHashes"].items():
            self.assertEqual(digest(ROOT / relative), expected, relative)
        required = {
            "data/entities.json", "data/drivers.json", "data/relationships.json", "data/sources.json",
            "data/actions-events-v1/catalog.json", "data/relational-state-v1/catalog.json",
            "data/relationship-intervention-v1/relationships.json",
        }
        self.assertTrue(required.issubset(protected["productionHashes"]))

    def test_documents_and_authoritative_json_exist(self):
        for name in ["blocker-dependency-map.json", "root-issues.json", "work-packages.json", "decision-packets.json"]:
            self.assertTrue((DATA / name).is_file())
        for name in ["POST_SCALE_UP_DEPENDENCY_ANALYSIS.md", "POST_SCALE_UP_GOVERNANCE_ROADMAP.md",
                     "ROOT_DECISION_PACKAGES.md", "RDS_GOVERNANCE_PROGRAM.md",
                     "CROSS_LEVEL_AND_NETWORK_ARCHITECTURE_OPTIONS.md", "ACTIVATION_CONTRACT_OPTIONS.md"]:
            self.assertTrue((DOCS / name).is_file())


if __name__ == "__main__":
    unittest.main()
