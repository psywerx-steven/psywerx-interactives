#!/usr/bin/env python3
"""Validated, restartable research ingestion and end-to-end publication checks.

Only GitHub Actions calls reconcile. Assistants write inbox files, never projections.
The existing research_stream module remains the sole canonical ingestion implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
STREAM = Path('data/research-stream')
CUTOVER = '2026-10-21'
LIVE = 'https://raw.githubusercontent.com/psywerx-steven/psywerx-interactives/research-data/data/research-stream/explorer.json'
GENERATED = ('research_items.jsonl', 'archive', 'briefs', 'public_feed.json',
             'public_feed_pages', 'explorer.json', 'receipts')


def strict_json(text):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f'non-finite JSON number: {value}')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def digest(payload):
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def publication_gate(raw, filename):
    if not isinstance(raw, dict) or raw.get('schemaVersion') != 'psywerx-research-items-v1':
        raise ValueError('invalid handoff schema')
    day = raw.get('briefDate')
    if not isinstance(day, str) or date.fromisoformat(day).isoformat() != day:
        raise ValueError('briefDate must be YYYY-MM-DD')
    if raw.get('briefType') != 'daily' or not isinstance(raw.get('items'), list) or not raw['items']:
        raise ValueError('a nonempty daily handoff is required')
    if day >= CUTOVER:
        if filename != day + '.json':
            raise ValueError('inbox filename does not match briefDate')
        for item in raw['items']:
            if (item.get('briefDate') != day or item.get('briefType') != 'daily'
                    or item.get('streamDecision') != 'publish' or item.get('sourceVerified') is not True):
                raise ValueError('every item must be verified, publish, and match daily provenance')
    return raw


def load_handoff(path):
    from ingest_research_items import decode_input
    from research_stream import validate_handoff
    text = path.read_text(encoding='utf-8-sig')
    raw = strict_json(text)
    if isinstance(raw, dict) and raw.get('encoding') == 'gzip-base64':
        raw = strict_json(decode_input(text))
        if raw.get('briefDate', '') >= CUTOVER:
            raise ValueError('new handoffs must be plain JSON, not compressed envelopes')
    publication_gate(raw, path.name)
    return validate_handoff(raw)


def verify_membership(day, ids, public_ids, manifest, explorer):
    if (manifest.get('schemaVersion') != 'psywerx-brief-manifest-v1'
            or manifest.get('briefDate') != day or manifest.get('briefType') != 'daily'
            or manifest.get('itemIds') != ids or manifest.get('totalItems') != len(ids)):
        raise ValueError('manifest missing, mismatched, or incomplete')
    if explorer.get('schemaVersion') != 'psywerx-research-explorer-v1':
        raise ValueError('invalid explorer schema')
    items = explorer.get('items', [])
    lookup = {item['itemId']: item for item in items}
    if len(lookup) != len(items) or explorer.get('totalItems') != len(items):
        raise ValueError('explorer item count/identity mismatch')
    briefs = [b for b in explorer.get('briefs', []) if b.get('briefDate') == day]
    if public_ids:
        if (len(briefs) != 1 or briefs[0].get('itemIds') != public_ids
                or briefs[0].get('totalItems') != len(public_ids)):
            raise ValueError('explorer brief membership missing or incomplete')
    elif briefs:
        raise ValueError('explorer exposes an editorially blocked brief')
    for item_id in public_ids:
        item = lookup.get(item_id)
        if not item or not item.get('dateAdded') or not item.get('latestSeenBriefDate'):
            raise ValueError(f'explorer item missing: {item_id}')
        if item['dateAdded'] > day or item['latestSeenBriefDate'] < day:
            raise ValueError(f'explorer provenance is stale: {item_id}')


def inspect_payload(base, payload, explorer=None):
    from research_stream import load_database, item_id_for, is_public, explorer_item
    records = {x['itemId']: x for x in load_database(base / 'research_items.jsonl')}
    ids = [item_id_for(x['sourceKey']) for x in payload['items']]
    if any(item_id not in records for item_id in ids):
        raise ValueError('canonical ingestion is incomplete')
    public_ids = [item_id for item_id in ids if is_public(records[item_id])]
    day = payload['briefDate']
    manifest = strict_json((base / 'briefs' / f'{day}.json').read_text())
    if explorer is None:
        explorer = strict_json((base / 'explorer.json').read_text())
    verify_membership(day, ids, public_ids, manifest, explorer)
    lookup = {x['itemId']: x for x in explorer['items']}
    for item_id in public_ids:
        if lookup[item_id] != explorer_item(records[item_id]):
            raise ValueError(f'explorer content differs from canonical item: {item_id}')
    return {'schemaVersion': 'psywerx-ingestion-receipt-v1', 'briefDate': day,
            'handoffSha256': digest(payload), 'itemIds': ids,
            'publishedItemIds': public_ids,
            'blockedItemIds': [item_id for item_id in ids if item_id not in public_ids]}


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def reconcile(root):
    from research_stream import ingest_handoff, generate_public_feed, generate_explorer_data
    source = root / STREAM
    good, errors = [], []
    for path in sorted((source / 'inbox').glob('*.json')):
        try:
            good.append((path, load_handoff(path)))
        except (ValueError, OSError, TypeError, KeyError) as exc:
            errors.append({'checkpoint': 'inbox-validation', 'file': path.name, 'error': str(exc)})
    good.sort(key=lambda pair: pair[1]['briefDate'])
    ingested = 0
    with tempfile.TemporaryDirectory(prefix='psywerx-reconcile-') as directory:
        stage = Path(directory) / 'stream'
        shutil.copytree(source, stage)
        for path, payload in good:
            receipt_path = stage / 'receipts' / f"{payload['briefDate']}.json"
            try:
                receipt = strict_json(receipt_path.read_text())
                complete = receipt == inspect_payload(stage, payload)
            except (ValueError, OSError, TypeError, KeyError):
                complete = False
            if not complete:
                report = ingest_handoff(payload, stage / 'research_items.jsonl')
                ingested += 1
                if report['conflicts']:
                    errors.append({'checkpoint': 'editorial-conflict', 'file': path.name,
                                   'details': report['details']['conflicts']})
        generate_public_feed(stage / 'research_items.jsonl', stage / 'public_feed.json')
        generate_explorer_data(stage / 'research_items.jsonl', stage / 'explorer.json')
        for _, payload in good:
            receipt = inspect_payload(stage, payload)
            write_json(stage / 'receipts' / f"{payload['briefDate']}.json", receipt)
        # Promote only fully verified generated outputs. Never modify the inbox or website.
        for name in GENERATED:
            src, dst = stage / name, source / name
            if dst.is_dir():
                shutil.rmtree(dst)
            if src.is_dir():
                shutil.copytree(src, dst)
            elif src.exists():
                shutil.copy2(src, dst)
    return {'safeToCommit': True, 'validatedHandoffs': len(good), 'ingestedHandoffs': ingested,
            'errors': errors, 'latestBriefDate': max((p['briefDate'] for _, p in good), default=None)}


def expected_day(now=None):
    now = now or datetime.now(ZoneInfo('America/Chicago'))
    now = now.astimezone(ZoneInfo('America/Chicago'))
    # Do not call today's source late before its 08:45 Central publication deadline.
    return (now.date() if (now.hour, now.minute) >= (8, 45) else now.date() - timedelta(days=1)).isoformat()


def check(root, day, live=False):
    base = root / STREAM
    checkpoint = 'inbox'
    report = {'briefDate': day, 'latestInboxDate': max((p.stem for p in (base / 'inbox').glob('????-??-??.json')), default=None),
              'latestManifestDate': max((p.stem for p in (base / 'briefs').glob('????-??-??.json')), default=None)}
    try:
        try:
            projection = strict_json((base / 'explorer.json').read_text())
            report['latestExplorerDate'] = max((b['briefDate'] for b in projection.get('briefs', [])), default=None)
        except (ValueError, OSError, TypeError, KeyError):
            projection = None
            report['latestExplorerDate'] = None
        payload = load_handoff(base / 'inbox' / f'{day}.json')
        checkpoint = 'manifest'
        from research_stream import item_id_for
        manifest = strict_json((base / 'briefs' / f'{day}.json').read_text())
        ids = [item_id_for(x['sourceKey']) for x in payload['items']]
        if manifest.get('itemIds') != ids or manifest.get('totalItems') != len(ids) or manifest.get('briefDate') != day:
            raise ValueError('manifest does not match the complete handoff')
        checkpoint = 'explorer-propagation'
        expected = inspect_payload(base, payload, projection)
        checkpoint = 'ingestion-receipt'
        if strict_json((base / 'receipts' / f'{day}.json').read_text()) != expected:
            raise ValueError('receipt is missing or does not match the validated handoff')
        if live:
            checkpoint = 'live-explorer'
            for attempt in range(4):
                try:
                    request = Request(LIVE + f'?publication-check={time.time_ns()}', headers={'Cache-Control': 'no-cache', 'User-Agent': 'PSYWERX-Publication-Check'})
                    with urlopen(request, timeout=30) as response:
                        remote = strict_json(response.read().decode('utf-8'))
                    report['latestLiveExplorerDate'] = max((b['briefDate'] for b in remote.get('briefs', [])), default=None)
                    inspect_payload(base, payload, remote)
                    break
                except (ValueError, OSError, TypeError, KeyError):
                    if attempt == 3:
                        raise
                    time.sleep(5 * (attempt + 1))
        if expected['blockedItemIds']:
            checkpoint = 'editorial-override'
            raise ValueError(f"Publication excluded held/rejected items: {expected['blockedItemIds']}")
        return {**report, 'ok': True, 'publishedItems': len(expected['publishedItemIds'])}
    except (ValueError, OSError, TypeError, KeyError) as exc:
        return {**report, 'ok': False, 'failedCheckpoint': checkpoint, 'error': str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('reconcile', 'check', 'validate'))
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--date')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'reconcile':
            result = reconcile(args.root)
            code = 2 if result['errors'] else 0
        elif args.command == 'check':
            today = datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
            target = today if (args.root / STREAM / 'inbox' / f'{today}.json').exists() else expected_day()
            result = check(args.root, args.date or target, args.live)
            code = 0 if result['ok'] else 1
        else:
            if not args.input:
                raise ValueError('--input is required for validate')
            payload = load_handoff(args.input)
            if args.date and payload['briefDate'] != args.date:
                raise ValueError('briefDate does not match requested date')
            result = {'ok': True, 'briefDate': payload['briefDate'], 'items': len(payload['items']), 'handoffSha256': digest(payload)}
            code = 0
    except Exception as exc:
        result, code = {'safeToCommit': False, 'error': str(exc)}, 1
    if args.report:
        write_json(args.report, result)
    print(json.dumps(result, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
