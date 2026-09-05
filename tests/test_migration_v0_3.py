import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPT = ROOT / "scripts" / "build_migration_preview_v0_3.py"
SEED = ROOT / "_migration_handoff_v0.3" / "migration_manifest_seed.json"

MODULE_SPEC = importlib.util.spec_from_file_location("migration_v0_3", SCRIPT)
MIGRATION = importlib.util.module_from_spec(MODULE_SPEC)
assert MODULE_SPEC.loader is not None
MODULE_SPEC.loader.exec_module(MIGRATION)

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
FROZEN_BASELINE_COMMIT = "580d59c451765e9f4d65b517f538a495fa93bda5"
SPECIFICATION_STATUS = "GOVERNED_MIGRATION_SPECIFICATION"
BASELINE_STATUS = "GOVERNED_MIGRATION_BASELINE"
AUTHORITY_DECISION_RECORD = "docs/governance/MIGRATION_BASELINE_ADOPTION_V0_3.md"
EFFECTIVE_COMMIT = "6cf34a029a9dc6e099628e86dfb9f42b53bd8d13"
EFFECTIVE_DATE = "2026-09-05"
OPEN_GOVERNANCE_ITEMS = [
    "INS-102",
    "REL-SOC-028",
    "REL-TEC-049",
    "REL-MIG-CAND-0001",
    "REL-MIG-CAND-0002",
    "REL-MIG-CAND-0003",
    "NEW-ENTITIES-V0.3",
]


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def baseline_bytes(name):
    return subprocess.run(
        ["git", "show", f"{FROZEN_BASELINE_COMMIT}:data/{name}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def baseline_json(name):
    return json.loads(baseline_bytes(name).decode("utf-8"))


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
        cls.sources = load("sources.json")["sources"]
        cls.plain_language = load("plain_language.json")["drivers"]

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

    def test_adopted_migration_authority_is_exact_and_resolvable(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        self.assertEqual(seed["status"], SPECIFICATION_STATUS)
        self.assertEqual(self.manifest["specificationStatus"], SPECIFICATION_STATUS)
        self.assertEqual(self.manifest["status"], BASELINE_STATUS)
        self.assertEqual(self.manifest["baselineGitCommit"], FROZEN_BASELINE_COMMIT)
        for record in (seed, self.manifest):
            self.assertEqual(record["authorityDecisionRecord"], AUTHORITY_DECISION_RECORD)
            self.assertEqual(record["effectiveCommit"], EFFECTIVE_COMMIT)
            self.assertEqual(record["effectiveDate"], EFFECTIVE_DATE)
            self.assertEqual(record["openGovernanceItems"], OPEN_GOVERNANCE_ITEMS)
        decision_path = ROOT / AUTHORITY_DECISION_RECORD
        self.assertTrue(decision_path.is_file())
        decision_text = decision_path.read_text(encoding="utf-8")
        self.assertIn("MIGRATION_BASELINE_ADOPTION_V0_3-2026-09-05", decision_text)
        self.assertIn(EFFECTIVE_COMMIT, decision_text)
        self.assertIn(AUTHORITY_DECISION_RECORD, self.manifest["governanceDecisionRecords"])

    def test_preview_authority_labels_cannot_return(self):
        seed_text = SEED.read_text(encoding="utf-8")
        manifest_text = (DATA / "migration-manifest.json").read_text(encoding="utf-8")
        for retired_label in (
            "NON_AUTHORITATIVE_PREVIEW_SEED",
            "NON_AUTHORITATIVE_MIGRATION_PREVIEW",
        ):
            self.assertNotIn(retired_label, seed_text)
            self.assertNotIn(retired_label, manifest_text)

    def test_governance_seed_rejects_authority_tampering(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        tampered_values = {
            "status": "NON_AUTHORITATIVE_PREVIEW_SEED",
            "authorityDecisionRecord": "docs/governance/UNKNOWN.md",
            "effectiveCommit": "580d59c451765e9f4d65b517f538a495fa93bda5",
            "effectiveDate": "2026-09-06",
            "openGovernanceItems": OPEN_GOVERNANCE_ITEMS[:-1],
        }
        for field, value in tampered_values.items():
            with self.subTest(field=field):
                tampered = copy.deepcopy(seed)
                tampered[field] = value
                with self.assertRaisesRegex(
                    ValueError, f"migration authority field {field}"
                ):
                    MIGRATION.validate_governance_seed(tampered)

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

    def test_generator_rejects_an_unauthorized_35th_retype(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        tampered = copy.deepcopy(seed)
        tampered["retypes"].append({
            "id": "SOC-036",
            "new_entity_type": "RELATIONAL_DERIVED_STATE",
            "new_name": "Repeated Interaction Probability",
        })
        with self.assertRaisesRegex(ValueError, "exact 34-ID retype set"):
            MIGRATION.validate_governance_seed(tampered)

    def test_governance_seed_rejects_duplicate_or_changed_metadata(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(seed)
        duplicate["retypes"].append(copy.deepcopy(duplicate["retypes"][0]))
        with self.assertRaisesRegex(ValueError, "exact 34-ID retype set"):
            MIGRATION.validate_governance_seed(duplicate)
        changed = copy.deepcopy(seed)
        changed["retypes"][0]["new_name"] = "Unauthorized replacement"
        with self.assertRaisesRegex(ValueError, "governed name"):
            MIGRATION.validate_governance_seed(changed)

    def test_baseline_entity_fields_are_preserved_except_governed_names(self):
        baseline = baseline_json("drivers.json")
        current = {row["id"]: row for row in self.entities}
        renamed = {
            row["id"]: row["newName"] for row in self.manifest["renames"]
        }
        self.assertEqual(len(baseline), 793)
        for original in baseline:
            migrated = current[original["id"]]
            for field, value in original.items():
                if field == "aliases":
                    continue
                expected = renamed.get(original["id"], value) if field == "name" else value
                self.assertEqual(
                    migrated[field], expected,
                    f"Unauthorized baseline field change: {original['id']}.{field}",
                )

        alias_texts = defaultdict(set)
        for alias in self.aliases:
            for entity_id in alias["entityIds"]:
                alias_texts[entity_id].add(MIGRATION.normalized_text(alias["text"]))
        for original in baseline:
            self.assertTrue(
                {
                    MIGRATION.normalized_text(alias)
                    for alias in original["aliases"]
                } <= alias_texts[original["id"]],
                f"Legacy aliases were not preserved for {original['id']}",
            )

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

    def test_exact_431_active_causal_relationships_preserve_identity(self):
        baseline = baseline_json("relationships.json")["relationships"]
        baseline_by_id = {row["id"]: row for row in baseline}
        inactive_ids = {
            row["id"] for row in self.relationships["deprecatedRelationships"]
        } | {
            "REL-SOC-028", "REL-TEC-049",
        }
        active = [
            row for row in self.relationships["relationships"]
            if row["relationFamily"] == "CAUSAL"
        ]
        self.assertEqual(len(self.relationships["relationships"]), 450)
        self.assertEqual(len(active), 431)
        self.assertEqual({row["id"] for row in active}, set(baseline_by_id) - inactive_ids)
        for row in active:
            original = baseline_by_id[row["id"]]
            field_map = {
                "subjectEntityId": "sourceDriverId",
                "objectEntityId": "targetDriverId",
                "predicate": "causalRole",
                "polarity": "polarity",
                "directness": "directness",
                "mechanism": "mechanism",
                "conditionsModerators": "conditionsModerators",
                "moderatorEntityIds": "moderatorDriverIds",
                "subjectLevel": "sourceLevel",
                "objectLevel": "targetLevel",
                "levelTransitionMechanism": "levelTransitionMechanism",
                "lagProfile": "lagProfile",
                "lagLowerBound": "lagLowerBound",
                "lagUpperBound": "lagUpperBound",
                "lagUnit": "lagUnit",
                "lagNarrative": "lagNarrative",
                "exposurePattern": "exposurePattern",
                "effectPersistence": "effectPersistence",
                "evidenceStrength": "evidenceStrength",
                "confidence": "confidence",
                "generalizabilityContext": "generalizabilityContext",
                "reciprocalProcessId": "reciprocalProcessId",
                "governanceClass": "governanceClass",
                "supportingEvidenceIds": "supportingEvidenceIds",
                "notesCaveats": "notesCaveats",
                "source": "source",
            }
            for current_field, baseline_field in field_map.items():
                self.assertEqual(
                    row[current_field], original[baseline_field],
                    f"Relationship field changed: {row['id']}.{current_field}",
                )

    def test_all_entity_relationship_source_and_family_references_resolve(self):
        entity_ids = {row["id"] for row in self.entities}
        family_ids = {row["id"] for row in self.families}
        source_ids = {row["id"] for row in self.sources}
        all_relationships = [
            row
            for bucket in (
                "relationships", "deprecatedRelationships", "relationshipCandidates"
            )
            for row in self.relationships[bucket]
        ]
        relationship_ids = {row["id"] for row in all_relationships}
        for entity in self.entities:
            self.assertIn(entity["primaryFamilyId"], family_ids)
            self.assertTrue(set(entity["relatedFamilyIds"]) <= family_ids)
            for constituent in entity.get("constituentSpecifications", []):
                if constituent["entityId"] is not None:
                    self.assertIn(constituent["entityId"], entity_ids)
        for family in self.families:
            self.assertTrue(set(family["representativeDriverIds"]) <= {
                row["id"] for row in self.drivers
            })
            self.assertTrue(set(family["representativeEntityIds"]) <= entity_ids)
        for relationship in all_relationships:
            self.assertTrue(set(relationship["moderatorEntityIds"]) <= entity_ids)
            self.assertTrue(set(relationship["supportingEvidenceIds"]) <= source_ids)
        for source in self.sources:
            self.assertTrue(set(source["driverIds"]) <= entity_ids)
            self.assertTrue(set(source["relationshipIds"]) <= relationship_ids)
        for record in self.plain_language:
            self.assertIn(record["driverId"], entity_ids)
        crosswalk_ids = [row["crosswalkId"] for row in self.crosswalks]
        self.assertEqual(len(crosswalk_ids), len(set(crosswalk_ids)))
        for crosswalk in self.crosswalks:
            if crosswalk["resourceType"] == "ENTITY":
                self.assertIn(crosswalk["legacyId"], entity_ids)
                self.assertTrue(set(crosswalk["successorIds"]) <= entity_ids)
            elif crosswalk["resourceType"] == "RELATIONSHIP":
                self.assertIn(crosswalk["legacyId"], relationship_ids)
                self.assertTrue(set(crosswalk["successorIds"]) <= relationship_ids)
            else:
                self.fail(
                    f"Unsupported crosswalk resource type: "
                    f"{crosswalk['resourceType']}"
                )

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

    def test_new_entity_ungoverned_scientific_metadata_remains_empty(self):
        new_ids = {
            row["id"]
            for group in self.manifest["idAssignments"].values()
            for row in group
        }
        new_entities = [row for row in self.entities if row["id"] in new_ids]
        self.assertEqual(len(new_entities), 18)
        peripheral = {
            "mechanism", "likelyUpstreamInfluences", "likelyDownstreamInfluences",
            "moderatorsBoundaryConditions", "typicalInteractionCandidates",
            "modifiability", "volatility", "timeScaleOfChange", "timeScaleQualifier",
            "onsetCausalLag", "persistenceRecovery", "indicators",
            "measurementAssessmentMethods", "observability", "evidenceStrength",
            "evidenceNotes", "commonMisinterpretations", "keySources",
        }
        for entity in new_entities:
            for field in peripheral:
                self.assertIn(entity[field], (None, [], ""), f"{entity['id']}.{field}")

    def test_manifest_hashes_reproduce_baseline_inputs_and_outputs(self):
        for name, expected in self.manifest["baselineArtifactSha256"].items():
            self.assertEqual(hashlib.sha256(baseline_bytes(name)).hexdigest(), expected)
        for path, expected in self.manifest["governedInputSha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        implementation = self.manifest["migrationImplementation"]
        self.assertEqual(implementation["path"], "scripts/build_migration_preview_v0_3.py")
        self.assertEqual(
            hashlib.sha256((ROOT / implementation["path"]).read_bytes()).hexdigest(),
            implementation["sha256"],
        )
        for name, expected in self.manifest["generatedArtifactSha256"].items():
            self.assertEqual(hashlib.sha256((DATA / name).read_bytes()).hexdigest(), expected)

    def test_two_clean_migration_runs_are_byte_identical(self):
        governed_names = (
            "drivers.json", "relational-derived-states.json", "entities.json",
            "families.json", "relationships.json", "aliases.json", "crosswalks.json",
            "migration-manifest.json",
        )
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True)
        first = {name: (DATA / name).read_bytes() for name in governed_names}
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True)
        second = {name: (DATA / name).read_bytes() for name in governed_names}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
