"""Research database, Morning Brief ingestion, and public-stream tests."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "homepage/tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("research_stream", TOOLS / "research_stream.py")
stream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stream)


def sample_handoff(
    *,
    brief_date="2026-09-07",
    source_key="10.1234/example.1",
    source_url="https://doi.org/10.1234/example.1",
    source_verified=True,
    summary="A clear public summary explains the finding and why it matters while preserving the most important limitation for readers who need a concise and appropriately cautious account of the source.",
):
    return {
        "schemaVersion": "psywerx-research-items-v1",
        "briefDate": brief_date,
        "briefType": "daily",
        "items": [
            {
                "sourceItemNumber": 1,
                "primaryCategory": "behavioral-science",
                "categories": ["behavioral-science", "application-analysis"],
                "questionAndWhy": "What question was tested, and why does it matter for understanding the issue?",
                "whatTheyDid": "The researchers used a clearly described method to examine the question.",
                "whatTheyFound": "They reported a bounded finding supported by the source.",
                "whatItMeans": "The result is useful for practice, but it does not establish effects beyond the measured setting.",
                "streamTitle": "A concise descriptive takeaway",
                "streamSummary": summary,
                "attribution": "Example et al. — Example Journal",
                "sourceUrl": source_url,
                "sourcePublishedAt": "2026-09-01",
                "sourceKey": source_key,
                "sourceVerified": source_verified,
                "briefDate": brief_date,
                "briefType": "daily",
                "streamDecision": "pending",
            }
        ],
    }


class ResearchStreamTests(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        self.root = Path(self.context.name)
        self.database = self.root / "research_items.jsonl"
        self.public = self.root / "public_feed.json"

    def tearDown(self):
        self.context.cleanup()

    def ingest(self, payload=None, *, dry_run=False):
        return stream.ingest_handoff(payload or sample_handoff(), self.database, dry_run=dry_run)

    def test_valid_research_items_schema(self):
        normalized = stream.validate_handoff(sample_handoff())
        self.assertEqual(normalized["schemaVersion"], stream.HANDOFF_SCHEMA)
        self.assertEqual(normalized["items"][0]["streamDecision"], "pending")

    def test_malformed_input_rejected_transactionally(self):
        payload = sample_handoff()
        del payload["items"][0]["whatTheyDid"]
        with self.assertRaises(stream.ResearchStreamError):
            self.ingest(payload)
        self.assertFalse(self.database.exists())

    def test_invalid_category_rejected(self):
        payload = sample_handoff()
        payload["items"][0]["categories"] = ["not-a-category"]
        with self.assertRaises(stream.ResearchStreamError):
            self.ingest(payload)

    def test_non_https_source_rejected(self):
        payload = sample_handoff(source_key="http://example.com/report", source_url="http://example.com/report")
        with self.assertRaises(stream.ResearchStreamError):
            self.ingest(payload)

    def test_private_drive_source_rejected(self):
        payload = sample_handoff(
            source_key="https://drive.google.com/file/d/private-id/view",
            source_url="https://drive.google.com/file/d/private-id/view",
        )
        with self.assertRaises(stream.ResearchStreamError):
            self.ingest(payload)

    def test_json_extraction_from_full_morning_brief(self):
        text = "# Morning Brief\n\nHuman-readable analysis.\n\n```json\n" + json.dumps(sample_handoff()) + "\n```\n"
        extracted = stream.extract_handoff(text)
        self.assertEqual(extracted["items"][0]["sourceKey"], "doi:10.1234/example.1")

    def test_duplicate_doi_normalization(self):
        variants = (
            "10.1234/EXAMPLE.1",
            "doi:10.1234/example.1",
            "https://doi.org/10.1234/example.1",
        )
        self.assertEqual(
            {stream.normalize_source_identity(value, "https://doi.org/10.1234/example.1")[0] for value in variants},
            {"doi:10.1234/example.1"},
        )

    def test_duplicate_url_normalization(self):
        first = stream.normalize_source_identity(
            "https://EXAMPLE.com/report/?utm_source=brief&b=2&a=1#section",
            "https://example.com/report/?b=2&a=1",
        )[0]
        second = stream.normalize_source_identity(
            "https://example.com/report?a=1&b=2",
            "https://example.com/report?a=1&b=2",
        )[0]
        self.assertEqual(first, second)

    def test_repeat_source_tracks_first_and_latest_seen(self):
        self.ingest(sample_handoff(brief_date="2026-09-06"))
        report = self.ingest(sample_handoff(brief_date="2026-09-08"))
        record = stream.load_database(self.database)[0]
        self.assertEqual(report["updated"], 1)
        self.assertEqual(record["firstSeenBriefDate"], "2026-09-06")
        self.assertEqual(record["latestSeenBriefDate"], "2026-09-08")
        self.assertEqual(len(stream.load_database(self.database)), 1)

    def test_exact_repeat_is_unchanged_duplicate(self):
        self.ingest()
        report = self.ingest()
        self.assertEqual(report["unchanged"], 1)
        self.assertEqual(report["added"], 0)

    def test_newer_pending_content_updates_deterministically(self):
        self.ingest(sample_handoff(brief_date="2026-09-06"))
        changed = sample_handoff(brief_date="2026-09-08", summary="A materially updated public summary retains the same source identity and is accepted because the existing item is pending and this brief is newer than the prior appearance.")
        self.ingest(changed)
        record = stream.load_database(self.database)[0]
        self.assertEqual(record["streamSummary"], changed["items"][0]["streamSummary"])
        self.assertEqual(record["streamDecision"], "pending")

    def test_existing_human_decision_is_preserved_on_material_repeat(self):
        self.ingest(sample_handoff(brief_date="2026-09-06"))
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "publish", "2026-09-07")
        changed = sample_handoff(brief_date="2026-09-08", summary="A later brief supplies materially different wording that must not overwrite content associated with a prior explicit human publishing decision without review.")
        report = self.ingest(changed)
        record = stream.load_database(self.database)[0]
        self.assertEqual(report["conflicts"], 1)
        self.assertEqual(record["streamDecision"], "publish")
        self.assertNotEqual(record["streamSummary"], changed["items"][0]["streamSummary"])
        self.assertEqual(record["latestSeenBriefDate"], "2026-09-08")
        self.assertTrue(record["reviewRequired"])

    def test_dry_run_reports_without_writing(self):
        report = self.ingest(dry_run=True)
        self.assertTrue(report["dryRun"])
        self.assertEqual(report["added"], 1)
        self.assertFalse(self.database.exists())

    def test_ingestion_cli_accepts_raw_json_and_reports_counts(self):
        input_path = self.root / "handoff.json"
        input_path.write_text(json.dumps(sample_handoff()), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "ingest_research_items.py"),
                "--input",
                str(input_path),
                "--database",
                str(self.database),
                "--public-feed",
                str(self.public),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["added"], 1)
        self.assertEqual(report["rejected"], 0)
        self.assertEqual(len(stream.load_database(self.database)), 1)

    def test_publish_review_command_contract(self):
        self.ingest()
        item_id = stream.load_database(self.database)[0]["itemId"]
        result = stream.review_item(self.database, item_id, "publish", "2026-09-08")
        record = stream.load_database(self.database)[0]
        self.assertEqual(result["streamDecision"], "publish")
        self.assertEqual(record["publishedAt"], "2026-09-08")
        self.assertIs(stream.validate_record(record), record)

    def test_unverified_publish_is_rejected_without_database_change(self):
        self.ingest(sample_handoff(source_verified=False))
        item_id = stream.load_database(self.database)[0]["itemId"]
        before = self.database.read_bytes()
        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "review_research_item.py"),
                item_id,
                "publish",
                "--date",
                "2026-09-08",
                "--database",
                str(self.database),
                "--public-feed",
                str(self.public),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("sourceVerified must be true", result.stderr)
        self.assertEqual(self.database.read_bytes(), before)
        self.assertFalse(self.public.exists())
        record = stream.load_database(self.database)[0]
        self.assertEqual(record["streamDecision"], "pending")
        self.assertFalse(record["reviewRequired"])

    def test_unverified_hold_and_reject_remain_allowed(self):
        self.ingest(sample_handoff(source_verified=False))
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "hold", "2026-09-08")
        self.assertEqual(stream.load_database(self.database)[0]["streamDecision"], "hold")
        stream.review_item(self.database, item_id, "reject", "2026-09-09")
        record = stream.load_database(self.database)[0]
        self.assertEqual(record["streamDecision"], "reject")
        self.assertFalse(record["sourceVerified"])

    def test_failed_unverified_publish_preserves_review_required_conflict(self):
        self.ingest(sample_handoff(brief_date="2026-09-06", source_verified=False))
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "hold", "2026-09-07")
        changed = sample_handoff(
            brief_date="2026-09-08",
            source_verified=False,
            summary="A materially revised summary triggers owner review while the existing decision and unverified publication gate remain unchanged.",
        )
        report = self.ingest(changed)
        self.assertEqual(report["conflicts"], 1)
        before = self.database.read_bytes()
        with self.assertRaisesRegex(stream.ResearchStreamError, "sourceVerified must be true"):
            stream.review_item(self.database, item_id, "publish", "2026-09-09")
        self.assertEqual(self.database.read_bytes(), before)
        record = stream.load_database(self.database)[0]
        self.assertEqual(record["streamDecision"], "hold")
        self.assertTrue(record["reviewRequired"])

    def test_unverified_published_record_fails_canonical_validation(self):
        self.ingest(sample_handoff(source_verified=False))
        record = stream.load_database(self.database)[0]
        record["streamDecision"] = "publish"
        record["decisionDate"] = "2026-09-08"
        record["publishedAt"] = "2026-09-08"
        with self.assertRaisesRegex(stream.ResearchStreamError, "sourceVerified: true"):
            stream.validate_record(record)

    def test_hold_review_command_retains_item(self):
        self.ingest()
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "hold", "2026-09-08")
        records = stream.load_database(self.database)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["streamDecision"], "hold")
        self.assertIsNone(records[0]["publishedAt"])

    def test_reject_review_command_retains_item(self):
        self.ingest()
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "reject", "2026-09-08")
        records = stream.load_database(self.database)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["streamDecision"], "reject")

    def test_only_publish_items_enter_public_feed(self):
        first = sample_handoff(source_key="10.1234/example.1", source_url="https://doi.org/10.1234/example.1")
        second = sample_handoff(source_key="10.1234/example.2", source_url="https://doi.org/10.1234/example.2")
        second["items"][0]["sourceItemNumber"] = 2
        first["items"].append(second["items"][0])
        self.ingest(first)
        records = stream.load_database(self.database)
        stream.review_item(self.database, records[0]["itemId"], "publish", "2026-09-08")
        stream.review_item(self.database, records[1]["itemId"], "hold", "2026-09-08")
        page = stream.generate_public_feed(self.database, self.public)
        self.assertEqual(page["totalItems"], 1)
        self.assertEqual(page["items"][0]["itemId"], records[0]["itemId"])

    def test_public_field_allowlist_and_no_private_metadata_leakage(self):
        self.ingest()
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "publish", "2026-09-08")
        page = stream.generate_public_feed(self.database, self.public)
        item = page["items"][0]
        self.assertEqual(set(item), set(stream.PUBLIC_FIELDS))
        text = self.public.read_text(encoding="utf-8")
        for field in ("questionAndWhy", "whatTheyDid", "whatTheyFound", "whatItMeans", "sourceVerified", "decisionDate"):
            self.assertNotIn(field, text)
        self.assertNotRegex(text, r"docs\.google\.com|drive\.google\.com|C:\\Users|ghp_|sk-")

    def test_public_generation_is_deterministic_and_newest_first(self):
        payload = sample_handoff(brief_date="2026-09-06")
        second = sample_handoff(brief_date="2026-09-07", source_key="10.1234/example.2", source_url="https://doi.org/10.1234/example.2")
        second["items"][0]["sourceItemNumber"] = 2
        payload["items"].append(second["items"][0])
        payload["briefDate"] = "2026-09-07"
        payload["items"][0]["briefDate"] = "2026-09-07"
        self.ingest(payload)
        records = stream.load_database(self.database)
        stream.review_item(self.database, records[0]["itemId"], "publish", "2026-09-08")
        stream.review_item(self.database, records[1]["itemId"], "publish", "2026-09-09")
        stream.generate_public_feed(self.database, self.public)
        first_bytes = self.public.read_bytes()
        stream.generate_public_feed(self.database, self.public)
        self.assertEqual(first_bytes, self.public.read_bytes())
        page = json.loads(first_bytes)
        self.assertEqual([item["publishedAt"] for item in page["items"]], ["2026-09-09", "2026-09-08"])

    def test_multi_category_values_survive_public_projection(self):
        self.ingest()
        item_id = stream.load_database(self.database)[0]["itemId"]
        stream.review_item(self.database, item_id, "publish", "2026-09-08")
        page = stream.generate_public_feed(self.database, self.public)
        self.assertEqual(page["items"][0]["categories"], ["behavioral-science", "application-analysis"])

    def test_synthetic_large_database_is_paged_and_bounded(self):
        records = []
        for index in range(3000):
            source_key = f"https://example.org/research/{index}"
            item = stream.validate_handoff(
                sample_handoff(source_key=source_key, source_url=source_key)
            )["items"][0]
            record = stream._incoming_record(item)
            record["streamDecision"] = "publish"
            record["decisionDate"] = f"2026-09-{(index % 28) + 1:02d}"
            record["publishedAt"] = record["decisionDate"]
            records.append(record)
        stream.write_database(self.database, records)
        started = time.perf_counter()
        page = stream.generate_public_feed(self.database, self.public, page_size=24)
        elapsed = time.perf_counter() - started
        self.assertEqual(page["totalItems"], 3000)
        self.assertEqual(len(page["items"]), 24)
        self.assertEqual(page["nextPage"], "public_feed_pages/page-0002.json")
        self.assertTrue((self.root / "public_feed_pages/page-0125.json").is_file())
        self.assertLess(elapsed, 15.0)


class RepositoryResearchStateTests(unittest.TestCase):
    def test_machine_handoff_schema_document_matches_runtime_contract(self):
        schema = json.loads((REPO / "homepage/schemas/psywerx-research-items-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], stream.HANDOFF_SCHEMA)
        self.assertEqual(set(schema["$defs"]["category"]["enum"]), set(stream.CATEGORIES))
        self.assertEqual(set(schema["$defs"]["item"]["required"]), stream.HANDOFF_ITEM_FIELDS)

    def test_six_seed_items_are_pending_canonical_records(self):
        records = stream.load_database(REPO / "data/research-stream/research_items.jsonl")
        self.assertEqual(len(records), 6)
        self.assertTrue(all(record["streamDecision"] == "pending" for record in records))
        self.assertTrue(all(record["decisionDate"] is None and record["publishedAt"] is None for record in records))

    def test_checked_in_public_stream_is_empty(self):
        page = json.loads((REPO / "data/research-stream/public_feed.json").read_text(encoding="utf-8"))
        self.assertEqual(page["schemaVersion"], stream.PUBLIC_SCHEMA)
        self.assertEqual(page["totalItems"], 0)
        self.assertEqual(page["items"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
