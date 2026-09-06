"""Mechanical inventory and safe-output tests; no Family scientific audit."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_family as af
import actions_events_v1 as ae


class FamilyRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory=af.enriched_inventory()
        cls.scratch=af.ROOT/"reports/actions-events-v1/_scratch"
        cls.scratch.mkdir(parents=True,exist_ok=True)

    def test_exact_partition(self):
        s=self.inventory["summary"]
        self.assertEqual((s["drivers"],s["rds"],s["entities"],s["families"],s["layers"]),(770,41,811,105,8))
        self.assertEqual(sum(f["entities"] for f in self.inventory["families"]),811)

    def test_legacy_native_projection_deduplication(self):
        s=self.inventory["summary"]
        self.assertEqual((s["legacy"]["active"],s["native"]["relationships"],s["projections"]["count"]),(450,7,450))
        self.assertEqual((s["combinedActiveRelationships"],s["combinedActiveCausal"]),(457,436))
        self.assertEqual(s["projections"]["additionalPropositions"],0)

    def test_scope_and_family_matrices_reconcile(self):
        for kind,count in self.inventory["summary"]["combinedBySemantic"].items():
            for name in ("scopeMatrices","familyMatrix","matrices"):
                self.assertEqual(sum(r["count"] for r in self.inventory[name] if r["semanticType"]==kind),count,(name,kind))
        causal={}
        for row in self.inventory["scopeMatrices"]:
            if row["semanticType"]=="CAUSAL":causal[row["scope"]]=causal.get(row["scope"],0)+row["count"]
        self.assertEqual(causal,{"WITHIN_FAMILY":200,"SAME_LAYER_CROSS_FAMILY":146,"CROSS_LAYER":90})

    def test_105_queue_rows_not_scientific_decisions(self):
        queue=self.inventory["auditQueue"]
        self.assertEqual(len(queue),105)
        self.assertTrue(all(r["governanceDecision"]=="PENDING" for r in queue))
        self.assertTrue(all(r["priorityScore"]==sum(r["scoreComponents"].values()) for r in queue))

    def test_bio_compatibility(self):
        f=next(f for f in self.inventory["families"] if f["id"]=="BIO-F01")
        self.assertEqual((f["drivers"],f["rds"],f["causalIncident"],f["internal"],f["sameLayerCrossFamily"],f["crossLayer"],f["causallyIsolatedEntities"]),(6,5,10,3,4,3,6))
        self.assertEqual(self.inventory["summary"]["actionsEvents"]["additionalScientificPropositionsFromBridge"],0)

    def test_isolation_and_rds_flags(self):
        self.assertEqual(self.inventory["summary"]["causallyIsolatedEntities"],297)
        self.assertEqual(len(self.inventory["summary"]["rdsCausalSourceIds"]),18)
        self.assertEqual(len(self.inventory["summary"]["familiesWithNoCrossLayerCausal"]),37)
        self.assertEqual(len(self.inventory["projectionIncompleteFields"]),450)

    def test_canonical_paths_and_prefix_traps_rejected(self):
        for path in (af.ROOT,af.ROOT/"data",af.ROOT/"schemas",af.ROOT/"reports/actions-events-v1-escape",af.ROOT/"reports/actions-events-v1"):
            with self.assertRaises(ValueError):af.output_dir(path)

    def test_output_file_escape_rejected(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            with self.assertRaises(ValueError):af.write_json(Path(directory),"../../../../data/forbidden.json",{})

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            link=Path(directory)/"redirect"
            try:os.symlink(af.ROOT/"data",link,target_is_directory=True)
            except OSError as exc:self.skipTest("Symlink privilege unavailable: "+str(exc))
            with self.assertRaises(ValueError):af.output_dir(link/"invalid")

    def test_deterministic_original_family_export_and_blank_workspace(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            af.emit("BIO-F01",directory)
            first={f.name:f.read_bytes() for f in Path(directory).iterdir()}
            af.emit("BIO-F01",directory)
            self.assertEqual(first,{f.name:f.read_bytes() for f in Path(directory).iterdir()})
            baseline=json.loads(first["BIO-F01_baseline.json"])
            original=ae.read(af.ROOT/"data/relationship-intervention-v1/relationships.json")["relationships"]
            entities={e["id"]:e for e in af.inventory()["entities"]}
            bio_original=[r for r in original if entities[r["sourceEntityId"]]["familyId"]=="BIO-F01"
                          or entities[r["targetEntityId"]]["familyId"]=="BIO-F01"]
            self.assertEqual(baseline["nativeIncident"],bio_original)
            self.assertTrue(baseline["aliases"]);self.assertTrue(baseline["crosswalks"])
            workspace=json.loads(first["BIO-F01_research_template.json"])
            ae.validate_workspace(workspace)
            self.assertEqual(workspace["passB"]["effectAssertions"],[])
            self.assertEqual(workspace["passA"]["relationshipCandidates"],[])

    def test_unknown_family_never_writes(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            output=Path(directory)/"unknown"
            with self.assertRaises(ValueError):af.emit("SYN-FAMILY",output)
            self.assertFalse(output.exists())

    def test_allowlisted_root_itself_cannot_redirect_to_data(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            root=Path(directory).resolve();(root/"reports").mkdir();(root/"data").mkdir()
            try:os.symlink(root/"data",root/"reports/actions-events-v1",target_is_directory=True)
            except OSError as exc:self.skipTest("Symlink privilege unavailable: "+str(exc))
            with patch.object(af,"ROOT",root):
                with self.assertRaises(ValueError):af.output_dir(root/"reports/actions-events-v1/escape")
            self.assertFalse((root/"data/escape").exists())

    def test_cross_family_ownership_and_symmetry(self):
        entities={"A":{"primaryFamilyId":"SOC-F07"},"B":{"primaryFamilyId":"BIO-F01"}}
        self.assertEqual(af.ownership("A","B","CAUSAL",entities),"SOC-F07")
        self.assertEqual(af.ownership("A","B","ASSOCIATION",entities),"BIO-F01")
        self.assertEqual(af.ownership("B","A","ASSOCIATION",entities),"BIO-F01")

    def test_scientific_data_unchanged(self):
        comparison=af.scientific_integrity()
        self.assertTrue(comparison["passed"],comparison["changed"])
        self.assertEqual(comparison["filesCompared"],45)


if __name__=="__main__":unittest.main()
