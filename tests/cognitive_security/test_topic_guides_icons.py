"""Approved Topic Guide artwork does not change analysis or guide membership."""
import hashlib
import json
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from cognitive_security.topic_guides import (
    ICON_CELLS, ICON_SPRITE, ICON_SPRITE_SHA256, SITE,
    compile_outputs, render_directory, render_topic_icon,
)

class Icons(HTMLParser):
    def __init__(self):
        super().__init__()
        self.icons = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'topic-guide-icon' in attrs.get('class', '').split():
            self.icons.append(attrs)

class TopicGuideIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guides = json.loads((ROOT / 'content/cognitive-security-guides/guides.json').read_text())['guides']

    def test_all_fifteen_approved_cells_have_the_correct_slug(self):
        approved = [
            'assessment', 'narrative', 'cognitive-warfare', 'influence-psychology', 'ai-synthetic-media',
            'disinformation', 'resilience', 'deterrence', 'campaign-planning', 'audience-analysis',
            'data-analytics', 'ethics-law', 'workforce', 'strategic-communication', 'cyber',
        ]
        self.assertEqual(ICON_CELLS, {slug: (i % 5, i // 5) for i, slug in enumerate(approved)})
        self.assertEqual(set(ICON_CELLS), {g['slug'] for g in self.guides})

    def test_asset_fingerprint_dimensions_and_small_size(self):
        data = (ROOT / ICON_SPRITE).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), ICON_SPRITE_SHA256)
        self.assertEqual(data[:4], b'RIFF')
        self.assertEqual(data[8:16], b'WEBPVP8 ')
        self.assertEqual(data[23:26], b'\x9d\x01\x2a')
        width, height = struct.unpack('<HH', data[26:30])
        self.assertEqual((width & 0x3fff, height & 0x3fff), (880, 528))
        self.assertLess(len(data), 40000)

    def test_cards_include_static_decorative_icons(self):
        parser = Icons(); parser.feed(render_directory(self.guides))
        self.assertEqual(len(parser.icons), 15)
        for attrs in parser.icons:
            slug = attrs['data-topic-icon']; col, row = ICON_CELLS[slug]
            self.assertEqual(attrs['style'], f'--icon-x:{col * 25}%;--icon-y:{row * 50}%;')
            self.assertEqual(attrs['aria-hidden'], 'true')
            self.assertNotIn('tabindex', attrs)

    def test_reordering_guides_does_not_reassign_icons(self):
        normal = Icons(); normal.feed(render_directory(self.guides))
        reverse = Icons(); reverse.feed(render_directory(list(reversed(self.guides))))
        select = lambda p: {a['data-topic-icon']: a['style'] for a in p.icons}
        self.assertEqual(select(normal), select(reverse))

    def test_future_guide_without_art_remains_valid(self):
        self.assertEqual(render_topic_icon('future-guide'), '')
        self.assertEqual(render_topic_icon('<unsafe>'), '')

    def test_icon_changes_are_presentation_only(self):
        outputs, report = compile_outputs(ROOT)
        self.assertEqual(report['guideCount'], 15)
        self.assertEqual(report['featuredEpisodePlacements'], 63)
        self.assertEqual(report['selectedSourceCards'], 236)
        for path, data in outputs.items():
            if path != SITE / 'index.html' and path.suffix == '.html':
                self.assertNotIn(b'data-topic-icon=', data)
        self.assertTrue(report['protectedFilesUnchanged'])

if __name__ == '__main__':
    unittest.main()
