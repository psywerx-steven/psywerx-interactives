"""Incremental audit gates. An unfinished program must not pass closeout."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import psychological_layer_v1 as p
import build_psychological_family_v1 as b


class PsychologicalBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = p.read(p.STORE / "baseline.json")
        cls.registry = p.read(p.STORE / "relationship-review-registry.json")

    def test_actual_membership_and_rds(self):
        b = self.baseline
        entities = p.read(p.ROOT / "data/entities.json")
        members = [e for e in entities if e["layer"] == "Psychological"]
        self.assertEqual(set(b["entityIds"]), {e["id"] for e in members})
        self.assertEqual((len(members), sum(e["entityType"] == "DRIVER" for e in members)), (135, 134))
        self.assertEqual(b["summary"]["rdsIds"], ["PSY-078"])
        self.assertEqual([f["id"] for f in b["familyInventory"]], p.FAMILIES)

    def test_each_family_uses_generic_frozen_membership(self):
        for family in self.baseline["familyInventory"]:
            d = p.read(p.STORE / family["id"] / "BASELINE.json")
            self.assertEqual(set(family["memberIds"]), {e["id"] for e in d["entities"]})
            self.assertEqual(d["baselineCommit"], p.BASELINE)
            self.assertEqual(d["scienceOrigin"], "PRODUCTION_BASELINE")

    def test_unique_relationship_registry_not_incident_sum(self):
        edges = self.baseline["activeEdges"]
        self.assertEqual(len(edges), 111)
        self.assertEqual(len({r["id"] for r in edges}), 111)
        self.assertEqual({e["id"] for e in edges}, set(self.registry))
        self.assertGreater(sum(len(r["psychologicalFamilyIds"]) for r in self.registry.values()), len(self.registry))
        self.assertEqual(self.baseline["summary"]["projectionAdditionalPropositions"], 0)

    def test_no_baseline_scaffold_claims_research_complete(self):
        progress = p.read(p.STORE / "progress.json")
        for family, stages in progress["families"].items():
            if stages["COMPLETE"] == "DONE":
                self.assertTrue(all(s == "DONE" for s in stages.values()), family)
                self.assertTrue((p.STORE / family / "research.json").exists(), family)
            else:
                self.assertEqual(stages["BASELINE"], "DONE")

    def test_candidate_workspaces_remain_isolated(self):
        for family in p.FAMILIES:
            w = p.read(p.STORE / family / "workspace.json")
            self.assertEqual(w["activationStatus"], "NOT_ELIGIBLE")
            self.assertFalse(w["productionEligible"])
            for row in w["passB"]["effectAssertions"]:
                self.assertIn(row["targetKind"], ("DRIVER", "RELATIONSHIP"))
                if row["targetKind"] == "DRIVER":
                    self.assertNotEqual(row["targetId"], "PSY-078")
            for bucket in p.ae.COLLECTIONS:
                for row in w["passB"][bucket]:
                    self.assertIn(row["governance"]["lifecycleStatus"], ("CANDIDATE", "RESEARCH_NEEDED", "REVIEW_READY"))
                    self.assertEqual(row["governance"]["activationStatus"], "NOT_ELIGIBLE")

    def test_protected_science(self):
        self.assertTrue(p.check_protected()["passed"])
        counts = self.baseline["productionCounts"]
        self.assertEqual((counts["combinedActiveRelationships"], counts["combinedActiveCausal"]), (457, 436))

    def test_output_guard(self):
        with self.assertRaises(ValueError):
            p.write(p.ROOT / "data/entities.json", [])

    def test_cannot_accidentally_refreeze(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            p.freeze()


class FirstFamilyResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.family = "PSY-F01"
        cls.research = p.read(p.STORE / cls.family / "research.json")
        cls.workspace = p.read(p.STORE / cls.family / "workspace.json")
        cls.ledgers = p.read(p.STORE / cls.family / "actions-events-search-ledger.json")

    def test_all_seven_actual_entities_reviewed(self):
        self.assertEqual({r["id"] for r in self.research["entityReviews"]}, {f"PSY-{i:03d}" for i in range(1,8)})
        for row in self.research["entityReviews"]:
            for key in ("constructReview", "measurementReview", "timeReview", "unresolved", "sources"):
                self.assertTrue(row[key])

    def test_all_existing_incident_propositions_once(self):
        reviews = self.research["existingReviews"]
        ids = [r["id"] for r in reviews]
        frozen = p.read(p.STORE / self.family / "BASELINE.json")
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {r["id"] for r in frozen["legacyIncidentByBucket"]["relationships"]})
        self.assertEqual(len(ids), 9)

    def test_production_contracts_validate_candidates(self):
        self.assertFalse(p.ae.validate_workspace(self.workspace, b.context())["productionEligible"])
        for sidecar in p.read(p.STORE / self.family / "relationship-evidence-sidecars.json"):
            for f in sidecar["sourceFindings"]:
                p.ae.schema_set().validate("source-finding", f)

    def test_each_driver_has_eight_nine_eleven_dimensions(self):
        self.assertEqual(len(self.ledgers["drivers"]), 7)
        for row in self.ledgers["drivers"]:
            self.assertEqual(len(row["originLayerSearch"]), 8)
            self.assertEqual(len(row["domainSearch"]), 9)
            self.assertEqual(set(row["effectProperties"]), set(b.PROPERTIES))
            self.assertTrue(row["queries"])
            self.assertTrue(row["noFinding"])
            self.assertFalse(row["scientificUseEligibility"])
            self.assertFalse(row["modelEligibility"])
            self.assertFalse(row["practitionerActionEligibility"])

    def test_no_fabricated_supported_null(self):
        for ev in self.workspace["passB"]["evidenceAssessments"]:
            for f in ev["sourceFindings"]:
                if f["disposition"] == "NULL_FINDING":
                    self.assertEqual(f["nullInterpretation"]["interpretation"], "NO_DETECTED_DIFFERENCE")
        self.assertTrue(all(e["knowledgeStatus"] != "SUPPORTED_NULL" for e in self.workspace["passB"]["effectAssertions"]))

    def test_repetition_mixed_context_dependent_not_monotonic(self):
        r = self.workspace["passA"]["relationshipCandidates"][0]
        self.assertEqual((r["sourceEntityId"], r["targetEntityId"]), ("INF-041", "PSY-003"))
        self.assertEqual(r["polarity"], "CONTEXT_DEPENDENT")
        self.assertEqual(r["causalClaimRole"], "TOTAL_EFFECT")
        self.assertEqual(self.workspace["passA"]["evidence"][0]["evidenceDisposition"], "MIXED")
        self.assertIn("accuracy", r["boundaryConditions"])

    def test_refutation_week_day_and_source_overlap_preserved(self):
        ev = self.workspace["passB"]["evidenceAssessments"][1]
        findings = ev["sourceFindings"]
        self.assertEqual([f["disposition"] for f in findings], ["SUPPORTS", "NULL_FINDING", "MIXED"])
        self.assertEqual(ev["synthesis"]["disposition"], "MIXED")
        self.assertTrue(all(f["overlapNotes"] for f in findings))

    def test_no_direct_effect_on_multidimensional_strength(self):
        self.assertNotIn("PSY-002", {r["targetId"] for r in self.workspace["passB"]["effectAssertions"]})
        escalations = p.read(p.STORE / "architecture-escalations.json")
        self.assertTrue(any("PSY-002" in x["entityIds"] and not x["productionChangeAuthorized"] for x in escalations))

    def test_shared_contribution_not_summed(self):
        rows = p.read(p.STORE / "candidate-proposition-registry.json")
        ids = {r["id"]:r for r in rows}
        self.assertEqual(ids["REL-CAND-PSY-LAYER-0001"]["sharedContributionId"], ids["EA-CAND-PSY-LAYER-0001"]["sharedContributionId"])
        self.assertEqual(ids["REL-CAND-PSY-LAYER-0001"]["ownerFamilyId"], "INF-F07")

    def test_canonical_source_dedup_and_no_registration(self):
        self.assertGreater(b.validate_sources(), 0)
        sources = p.read(p.STORE / "candidate-source-registry.json")
        ids = {s["id"] for s in sources}
        self.assertIn("SRC-433", ids)
        self.assertIn("SRC112", ids)
        self.assertNotIn("SRC-CAND-PSY-LAYER-0006", ids)
        self.assertNotIn("SRC-CAND-PSY-LAYER-0008", ids)
        hofmann = next(s for s in sources if s["id"] == "SRC-CAND-PSY-LAYER-0004")
        self.assertIn("Geert Crombez", hofmann["authors"])
        self.assertTrue(p.check_protected()["passed"])

    def test_pending_human_authority_and_nonimplemented_proposals(self):
        for r in p.read(p.STORE / self.family / "revision-proposals.json"):
            self.assertFalse(r["implementationAuthorized"])
            self.assertEqual(r["governance"]["lifecycleStatus"], "RESEARCH_NEEDED")
            self.assertEqual(r["governance"]["activationStatus"], "NOT_ELIGIBLE")
        self.assertFalse(any(r["governance"]["lifecycleStatus"] == "GOVERNED" for k in p.ae.COLLECTIONS for r in self.workspace["passB"][k]))

    def test_no_moderation_pathway_or_occurrence_inference(self):
        self.assertFalse(self.workspace["passB"]["occurrences"])
        self.assertEqual(len(self.workspace["passA"]["relationshipCandidates"]), 1)
        for record in self.workspace["passB"]["effectAssertions"]:
            self.assertFalse(record["moderatorLinks"])

    def test_deterministic_candidate_render(self):
        roots = [p.STORE / self.family, p.DOCS / self.family]
        before = {path: p.digest(path) for root in roots for path in root.rglob("*") if path.is_file()}
        b.render(self.family)
        after = {path: p.digest(path) for root in roots for path in root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_research_and_ledger_references_resolve(self):
        source_ids = b.context().source_ids
        for row in self.research['entityReviews'] + self.research['existingReviews'] + self.research['hypotheses']:
            self.assertTrue(set(row['sources']) <= source_ids, row['id'])
        queries = {q['id'] for q in self.research['searchLog']}
        for ledger in self.ledgers['drivers']:
            self.assertTrue(set(ledger['queries']) <= queries, ledger['driverId'])
            self.assertTrue(set(ledger['sources']) <= source_ids, ledger['driverId'])

    def test_generated_markdown_local_links(self):
        import re
        from urllib.parse import unquote
        for path in (p.DOCS / self.family).glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((path.parent / unquote(target.split('#')[0])).exists(), (path, target))


if __name__ == "__main__":
    unittest.main()
