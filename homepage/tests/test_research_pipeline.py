"""Regression tests for publication guards, receipts, recovery, and repeat sources."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import research_pipeline as pipeline


def payload(day='2026-10-21'):
    item = dict(sourceItemNumber=1, primaryCategory='behavioral-science',
                categories=['behavioral-science'], questionAndWhy='Question?',
                whatTheyDid='Method.', whatTheyFound='Finding.', whatItMeans='Caveat.',
                streamTitle='Title', streamSummary='Summary.', attribution='Test source',
                sourceUrl='https://example.org/research/paper', sourcePublishedAt=None,
                sourceKey='https://example.org/research/paper', sourceVerified=True,
                briefDate=day, briefType='daily', streamDecision='publish')
    return dict(schemaVersion='psywerx-research-items-v1', briefDate=day, briefType='daily', items=[item])


def projection():
    manifest = dict(schemaVersion='psywerx-brief-manifest-v1', briefDate='2026-10-21',
                    briefType='daily', totalItems=1, itemIds=['a'])
    explorer = dict(schemaVersion='psywerx-research-explorer-v1', totalItems=1,
                    items=[dict(itemId='a', dateAdded='2026-10-19', latestSeenBriefDate='2026-10-21')],
                    briefs=[dict(briefDate='2026-10-21', totalItems=1, itemIds=['a'])])
    return manifest, explorer


class Guards(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(pipeline.publication_gate(payload(), '2026-10-21.json'), payload())

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):
            pipeline.strict_json('{"items":[],"items":[1]}')

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(ValueError):
            pipeline.strict_json('{"n":NaN}')

    def test_wrong_filename_rejected(self):
        with self.assertRaises(ValueError):
            pipeline.publication_gate(payload(), '2026-10-22.json')

    def test_empty_handoff_rejected(self):
        value = payload(); value['items'] = []
        with self.assertRaises(ValueError):
            pipeline.publication_gate(value, '2026-10-21.json')

    def test_unverified_rejected(self):
        value = payload(); value['items'][0]['sourceVerified'] = False
        with self.assertRaises(ValueError):
            pipeline.publication_gate(value, '2026-10-21.json')

    def test_pending_rejected(self):
        value = payload(); value['items'][0]['streamDecision'] = 'pending'
        with self.assertRaises(ValueError):
            pipeline.publication_gate(value, '2026-10-21.json')

    def test_item_date_mismatch_rejected(self):
        value = payload(); value['items'][0]['briefDate'] = '2026-10-20'
        with self.assertRaises(ValueError):
            pipeline.publication_gate(value, '2026-10-21.json')

    def test_repeated_source_with_older_date_added_is_valid(self):
        manifest, explorer = projection()
        pipeline.verify_membership('2026-10-21', ['a'], ['a'], manifest, explorer)

    def test_partial_publication_rejected(self):
        manifest, explorer = projection(); explorer['briefs'][0]['itemIds'] = []
        with self.assertRaises(ValueError):
            pipeline.verify_membership('2026-10-21', ['a'], ['a'], manifest, explorer)

    def test_fresh_timestamp_does_not_hide_stale_data(self):
        manifest, explorer = projection(); explorer['generatedAt'] = '2026-10-21'
        explorer['items'][0]['latestSeenBriefDate'] = '2026-10-19'
        with self.assertRaises(ValueError):
            pipeline.verify_membership('2026-10-21', ['a'], ['a'], manifest, explorer)

    def test_wrong_manifest_rejected(self):
        manifest, explorer = projection(); manifest['itemIds'] = ['b']
        with self.assertRaises(ValueError):
            pipeline.verify_membership('2026-10-21', ['a'], ['a'], manifest, explorer)

    def test_deadline_summer_and_winter(self):
        for stamp, expected in [('2026-10-21T13:44:00+00:00', '2026-10-20'),
                                ('2026-10-21T13:45:00+00:00', '2026-10-21'),
                                ('2026-12-21T14:44:00+00:00', '2026-12-20'),
                                ('2026-12-21T14:45:00+00:00', '2026-12-21')]:
            self.assertEqual(pipeline.expected_day(datetime.fromisoformat(stamp)), expected)

    def test_digest_ignores_key_order(self):
        self.assertEqual(pipeline.digest({'a':1,'b':2}), pipeline.digest({'b':2,'a':1}))


try:
    import research_stream
    HAS_CANONICAL = True
except ImportError:
    HAS_CANONICAL = False


@unittest.skipUnless(HAS_CANONICAL, 'canonical repository module required')
class Integration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / pipeline.STREAM
        pipeline.write_json(self.base / 'inbox/2026-10-21.json', payload())

    def test_ingest_and_idempotent_replay(self):
        self.assertTrue(pipeline.reconcile(self.root)['safeToCommit'])
        before = {str(p.relative_to(self.base)): p.read_bytes() for p in self.base.rglob('*') if p.is_file()}
        report = pipeline.reconcile(self.root)
        after = {str(p.relative_to(self.base)): p.read_bytes() for p in self.base.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(report['ingestedHandoffs'], 0)
        self.assertTrue(pipeline.check(self.root, '2026-10-21')['ok'])

    def test_bad_inbox_does_not_block_valid_day(self):
        pipeline.write_json(self.base / 'inbox/2026-10-22.json', {'broken': True})
        report = pipeline.reconcile(self.root)
        self.assertEqual(len(report['errors']), 1)
        self.assertTrue(pipeline.check(self.root, '2026-10-21')['ok'])
        self.assertFalse((self.base / 'briefs/2026-10-22.json').exists())

    def test_missing_manifest_is_repaired(self):
        pipeline.reconcile(self.root)
        (self.base / 'briefs/2026-10-21.json').unlink()
        self.assertFalse(pipeline.check(self.root, '2026-10-21')['ok'])
        pipeline.reconcile(self.root)
        self.assertTrue(pipeline.check(self.root, '2026-10-21')['ok'])

    def test_repeat_source_no_new_date_added(self):
        pipeline.write_json(self.base / 'inbox/2026-10-22.json', payload('2026-10-22'))
        pipeline.reconcile(self.root)
        self.assertTrue(pipeline.check(self.root, '2026-10-22')['ok'])
        explorer = json.loads((self.base / 'explorer.json').read_text())
        self.assertEqual(explorer['totalItems'], 1)
        self.assertEqual(explorer['items'][0]['dateAdded'], '2026-10-21')

    def test_input_edit_invalidates_receipt(self):
        pipeline.reconcile(self.root)
        changed = payload(); changed['items'][0]['streamSummary'] = 'Corrected summary.'
        pipeline.write_json(self.base / 'inbox/2026-10-21.json', changed)
        self.assertFalse(pipeline.check(self.root, '2026-10-21')['ok'])
        pipeline.reconcile(self.root)
        self.assertTrue(pipeline.check(self.root, '2026-10-21')['ok'])

    def test_editorial_override_not_republished(self):
        pipeline.reconcile(self.root)
        record = research_stream.load_database(self.base / 'research_items.jsonl')[0]
        research_stream.review_item(self.base / 'research_items.jsonl', record['itemId'], 'hold', '2026-10-21')
        pipeline.reconcile(self.root)
        report = pipeline.check(self.root, '2026-10-21')
        self.assertFalse(report['ok'])
        self.assertEqual(report['failedCheckpoint'], 'editorial-override')
        self.assertEqual(json.loads((self.base / 'explorer.json').read_text())['totalItems'], 0)


if __name__ == '__main__':
    unittest.main()
