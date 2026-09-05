import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

APPROVED_RETYPES = {
    "BIO-003", "BIO-006", "CUL-088", "INF-004", "INF-010", "INF-011",
    "INF-014", "INF-053", "INF-068", "INS-024", "INS-039", "INS-103",
    "INS-113", "PSY-078", "SOC-018", "SOC-022", "SOC-024", "SOC-035",
    "SOC-041", "SOC-046", "SOC-047", "SOC-049", "SOC-050", "SOC-051",
    "SOC-052", "SOC-053", "SOC-054", "SOC-055", "SOC-056", "SOC-057",
    "SOC-074", "SOC-076", "SOC-090", "SOC-096",
}
POSITIVE_CONTROLS = {
    "PSY-011", "ENV-050", "ENV-015", "ENV-025", "SOC-043", "SOC-085",
    "TEC-013",
}
REQUIRED_DRIVERS = POSITIVE_CONTROLS | {"SOC-036", "INS-102"}
BLOCKED_STATUS = "BLOCKED_NEEDS_GOVERNANCE_INPUT"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class GovernedMigrationV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drivers = load("drivers.json")
        cls.rds = load("relational-derived-states.json")
        cls.entities = load("entities.json")
        cls.families = load("families.json")["families"]
        cls.relationships = load("relationships.json")
        cls.aliases = load("aliases.json")["aliases"]
        cls.crosswalks = load("crosswalks.json")["crosswalks"]
        cls.manifest = load("migration-manifest.json")

    def test_exact_governed_counts_and_partition(self):
        self.assertEqual(len(self.drivers), 770)
        self.assertEqual(len(self.rds), 41)
        self.assertEqual(len(self.entities), 811)
        driver_ids = {row["id"] for row in self.drivers}
        rds_ids = {row["id"] for row in self.rds}
        entity_ids = [row["id"] for row in self.entities]
        self.assertFalse(driver_ids & rds_ids)
        self.assertEqual(driver_ids | rds_ids, set(entity_ids))
        self.assertEqual(len(entity_ids), len(set(entity_ids)))
        self.assertTrue(all(row["entityType"] == "DRIVER" for row in self.drivers))
        self.assertTrue(all(
            row["entityType"] == "RELATIONAL_DERIVED_STATE" for row in self.rds
        ))

    def test_only_approved_baseline_ids_were_retyped(self):
        rds_ids = {row["id"] for row in self.rds}
        migrated = {
            row["legacyId"]
            for row in self.crosswalks
            if row["resourceType"] == "ENTITY" and row["migrationType"] == "RETYPE"
        }
        self.assertEqual(migrated, APPROVED_RETYPES)
        self.assertEqual(set(self.manifest["retypedEntityIds"]), APPROVED_RETYPES)
        new_rds_ids = {
            row["id"]
            for row in self.manifest["idAssignments"]["newRelationalDerivedStates"]
        }
        self.assertEqual(rds_ids - new_rds_ids, APPROVED_RETYPES)

    def test_governed_driver_exceptions_remain_drivers(self):
        driver_ids = {row["id"] for row in self.drivers}
        self.assertTrue(REQUIRED_DRIVERS <= driver_ids)
        self.assertTrue(APPROVED_RETYPES.isdisjoint(driver_ids))

    def test_family_counts_reconcile_by_entity_type(self):
        counts = defaultdict(Counter)
        for entity in self.entities:
            counts[entity["primaryFamilyId"]][entity["entityType"]] += 1
        self.assertEqual(sum(family["driverCount"] for family in self.families), 770)
        self.assertEqual(
            sum(family["relationalDerivedStateCount"] for family in self.families), 41
        )
        self.assertEqual(sum(family["totalEntityCount"] for family in self.families), 811)
        for family in self.families:
            family_counts = counts[family["id"]]
            self.assertEqual(family["driverCount"], family_counts["DRIVER"])
            self.assertEqual(
                family["relationalDerivedStateCount"],
                family_counts["RELATIONAL_DERIVED_STATE"],
            )
            self.assertEqual(family["totalEntityCount"], sum(family_counts.values()))

    def test_relationships_have_unique_ids_and_no_dangling_endpoints(self):
        entity_ids = {row["id"] for row in self.entities}
        relationship_ids = []
        for bucket in (
            "relationships", "deprecatedRelationships", "relationshipCandidates"
        ):
            for relationship in self.relationships[bucket]:
                relationship_ids.append(relationship["id"])
                self.assertIn(relationship["subjectEntityId"], entity_ids)
                self.assertIn(relationship["objectEntityId"], entity_ids)
        self.assertEqual(len(relationship_ids), len(set(relationship_ids)))

    def test_noncausal_relationships_do_not_carry_causal_fields(self):
        causal_fields = (
            "polarity", "lagLowerBound", "lagUpperBound", "lagUnit",
            "lagNarrative", "exposurePattern", "effectPersistence",
        )
        for bucket in (
            "relationships", "deprecatedRelationships", "relationshipCandidates"
        ):
            for relationship in self.relationships[bucket]:
                if relationship["relationFamily"] != "CAUSAL":
                    self.assertTrue(all(
                        relationship.get(field) in (None, [], "")
                        for field in causal_fields
                    ))

    def test_aliases_resolve_without_ambiguous_exact_synonyms(self):
        entity_ids = {row["id"] for row in self.entities}
        alias_ids = [row["aliasId"] for row in self.aliases]
        self.assertEqual(len(alias_ids), len(set(alias_ids)))
        for alias in self.aliases:
            self.assertTrue(set(alias["entityIds"]) <= entity_ids)
            if alias["aliasType"] == "EXACT_SYNONYM":
                self.assertEqual(len(alias["entityIds"]), 1)

    def test_all_reported_open_items_are_mechanically_blocked(self):
        blocked = self.manifest["blockedItems"]
        self.assertTrue(blocked)
        self.assertTrue(all(item["status"] == BLOCKED_STATUS for item in blocked))
        self.assertEqual(
            {item["itemId"] for item in blocked},
            {
                "INS-102", "REL-SOC-028", "REL-TEC-049",
                "REL-MIG-CAND-0001", "REL-MIG-CAND-0002",
                "REL-MIG-CAND-0003", "NEW-ENTITIES-V0.3",
            },
        )
        candidate_statuses = {
            row["id"]: row.get("reviewStatus")
            for row in self.relationships["relationshipCandidates"]
        }
        for identifier in {
            "REL-SOC-028", "REL-TEC-049", "REL-MIG-CAND-0001",
            "REL-MIG-CAND-0002", "REL-MIG-CAND-0003",
        }:
            self.assertEqual(candidate_statuses[identifier], BLOCKED_STATUS)


if __name__ == "__main__":
    unittest.main()
