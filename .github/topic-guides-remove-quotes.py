"""One-time, scoped migration of Topic Guides to citation-only episode cards."""
from pathlib import Path
import hashlib
import json
import re
import sys

root = Path(sys.argv[1]).resolve()
module = root / 'scripts/cognitive_security/topic_guides.py'

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError(f'Expected one source match for: {old[:120]!r}')
    return text.replace(old, new, 1)

text = module.read_text(encoding='utf-8')
text = replace_once(text, 'QUOTE_FIELDS = {"quoteId", "episodeId", "speaker", "text", "sourceUrl", "timestamp", "verificationBasis"}\n', '')
text = replace_once(text, '"topicIds", "quoteId", "summarySha256"', '"topicIds", "summarySha256"')
start, end = text.index('def validate_quotes('), text.index('def validate_guides(')
text = text[:start] + text[end:]
text = replace_once(text, 'def validate_guides(corpus: Corpus, payload: dict[str, Any], quotes: dict[str, Any]) -> None:', 'def validate_guides(corpus: Corpus, payload: dict[str, Any]) -> None:')
text = replace_once(text, '    require(payload.get("membershipMethod") == MEMBERSHIP, "Explicit canonical curation required")', '    require(payload.get("schemaVersion") == "1.1", "Citation-only guide schema 1.1 required")\n    require(payload.get("membershipMethod") == MEMBERSHIP, "Explicit canonical curation required")')
text = replace_once(text, '            if e["quoteId"] is not None:\n                require(e["quoteId"] in quotes and quotes[e["quoteId"]]["episodeId"] == e["episodeId"], "Quote belongs to a different episode")\n', '')
text = replace_once(text, 'def render_episode(corpus: Corpus, e: dict[str, Any], quotes: dict[str, Any], order: int) -> str:', 'def render_episode(corpus: Corpus, e: dict[str, Any], order: int) -> str:')
start = text.index('    if e["quoteId"]:')
end = text.index('    head += \'<p class="source-citation">Listening notes:', start)
text = text[:start] + text[end:]
text = replace_once(text, 'def render_guide(corpus: Corpus, g: dict[str, Any], quotes: dict[str, Any]) -> str:', 'def render_guide(corpus: Corpus, g: dict[str, Any]) -> str:')
text = replace_once(text, 'render_episode(corpus,e,quotes,i)', 'render_episode(corpus,e,i)')
text = replace_once(text, 'def compile_outputs(root: Path, payload: dict[str, Any] | None = None, quote_payload: dict[str, Any] | None = None, approvals: dict[str, Any] | None = None)', 'def compile_outputs(root: Path, payload: dict[str, Any] | None = None)')
text = replace_once(text, "    quote_payload = quote_payload if quote_payload is not None else load(root / AUTHORING / 'quote_excerpts.json')\n    approvals = approvals if approvals is not None else load(root / AUTHORING / 'quote_approvals.json')\n    quotes = validate_quotes(corpus, quote_payload, approvals)\n    validate_guides(corpus, payload, quotes)", "    require({p.name for p in (root / AUTHORING).glob('*.json')} == {'guides.json', 'source_lock.json'}, 'Unexpected guide authoring files')\n    validate_guides(corpus, payload)")
text = replace_once(text, '    directory = []; quote_missing = []', '    directory = []')
text = replace_once(text, 'render_guide(corpus,g,quotes)', 'render_guide(corpus,g)')
text = replace_once(text, "        for e in g['featuredEpisodes']:\n            if not e['quoteId']:\n                quote_missing.append({'guideId':g['guideId'],'episodeNumber':e['expectedEpisodeNumber'],'reason':'No excerpt approved for publication in this build; listening notes are cited separately.'})\n", '')
text = replace_once(text, "    out[PUBLIC / 'quote_excerpts.json'] = encode(quote_payload)\n", '')
text = replace_once(text, "encode({'schemaVersion':'1.0','membershipMethod':MEMBERSHIP", "encode({'schemaVersion':'1.1','membershipMethod':MEMBERSHIP")
text = replace_once(text, "manifest = {'schemaVersion':'1.0'", "manifest = {'schemaVersion':'1.1'")
text = replace_once(text, ",'quoteCount':len(quotes)", '')
text = replace_once(text, "'approvedQuoteCount':len(quotes),'quoteOmissions':quote_missing,", '')
text = replace_once(text, ", {report['approvedQuoteCount']} approved excerpts; canonical sources unchanged.", "; citation-only episode cards; canonical sources unchanged.")
module.write_text(text, encoding='utf-8')

path = root / 'content/cognitive-security-guides/guides.json'
payload = json.loads(path.read_text(encoding='utf-8'))
payload['schemaVersion'] = '1.1'
count = 0
for g in payload['guides']:
    for e in g['featuredEpisodes']:
        e.pop('quoteId')
        count += 1
assert count == 63
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
for rel in ['content/cognitive-security-guides/quote_excerpts.json', 'content/cognitive-security-guides/quote_approvals.json', 'data/cognitive-security-guides/quote_excerpts.json']:
    (root / rel).unlink()

path = root / 'cognitive-security/topic/guides.css'
text = path.read_text(encoding='utf-8')
text, n = re.subn(r'\.(?:episode-quote(?: blockquote| figcaption)?|quote-basis)\{[^{}]*\}', '', text)
assert n == 4
path.write_text(text, encoding='utf-8')

path = root / 'tests/cognitive_security/test_topic_guides.py'
text = path.read_text(encoding='utf-8')
text = replace_once(text, 'compile_outputs, validate_guides, validate_quotes, field_sha, load)', 'compile_outputs, validate_guides, field_sha, load)')
text = replace_once(text, ";cls.q=load(ROOT/AUTHORING/'quote_excerpts.json');cls.a=load(ROOT/AUTHORING/'quote_approvals.json')", '')
text = text.replace('validate_guides(self.c,x,validate_quotes(self.c,self.q,self.a))', 'validate_guides(self.c,x)').replace('validate_guides(self.c,x,{})', 'validate_guides(self.c,x)')
start, end = text.index('    def test_26_'), text.index('    def test_29_')
text = text[:start] + '''    def test_26_all_pages_are_quote_free(self):
        for path, data in self.out.items():
            if path.suffix == '.html':
                parser = Links(); parser.feed(data.decode())
                self.assertFalse(any(tag in ('blockquote', 'q') for tag, attrs in parser.tags), str(path))
                self.assertNotIn('episode-quote', data.decode())
                self.assertNotIn('Transcript excerpt;', data.decode())

    def test_27_quote_fields_cannot_be_reintroduced(self):
        for field in ('quoteId', 'quote', 'quoteText', 'transcriptPath'):
            payload = copy.deepcopy(self.g)
            payload['guides'][0]['featuredEpisodes'][0][field] = 'not allowed'
            with self.assertRaisesRegex(GuideError, 'allowlisted'):
                validate_guides(self.c, payload)

    def test_28_episode_citations_and_takeaways_remain(self):
        for guide in self.g['guides']:
            page = self.out[SITE/guide['slug']/'index.html'].decode()
            self.assertEqual(page.count('Listening notes:'), len(guide['featuredEpisodes']))
            for episode in guide['featuredEpisodes']:
                self.assertEqual(len(episode['takeaways']), 2)
                self.assertIn(episode['episodeId'], page)

''' + text[end:]
start, end = text.index('    def test_30_'), text.index('    def test_31_')
text = text[:start] + '''    def test_30_quote_payload_and_assets_are_absent(self):
        manifest = json.loads(self.out[PUBLIC/'manifest.json'])
        self.assertEqual(manifest['schemaVersion'], '1.1')
        self.assertEqual(set(manifest['files']), {'guide_directory.json', 'reverse_index.json', 'topic_guides.json'})
        self.assertNotIn('quoteCount', manifest)
        self.assertNotIn('quoteOmissions', self.report)
        for path in (AUTHORING/'quote_excerpts.json', AUTHORING/'quote_approvals.json', PUBLIC/'quote_excerpts.json'):
            self.assertFalse((ROOT/path).exists())
        for path, data in self.out.items():
            if path.is_relative_to(PUBLIC):
                self.assertNotIn('quoteId', data.decode())
                self.assertNotIn('verificationBasis', data.decode())

''' + text[end:]
path.write_text(text, encoding='utf-8')

path = root / 'tests/cognitive_security/test_topic_guides_browser.py'
text = replace_once(path.read_text(encoding='utf-8'), "self.assertEqual(self.page.locator('.episode-quote').count(),sum(bool(e['quoteId']) for e in g['featuredEpisodes']))", "self.assertEqual(self.page.locator('blockquote, q, .episode-quote').count(),0)\n                    self.assertEqual(self.page.locator('.episode-card .source-citation').count(),len(g['featuredEpisodes']))")
path.write_text(text, encoding='utf-8')

path = root / 'docs/cognitive-security/topic-guides/README.md'
text = path.read_text(encoding='utf-8')
start, end = text.index('## Public quotation boundary'), text.index('## Files and build')
text = text[:start] + '''## Citation-only episode cards

Per the accepted design revision, episode cards have no quotations. The quote
collections, approval records, quote identifiers, rendering code, CSS, and
omission counters have been removed rather than hidden. Guide schema 1.1 rejects
quote fields, and the closed authoring/generated inventories reject reintroduced
quote files. Browser tests check every guide for the absence of quote blocks.

The two listening takeaways, canonical topic tags, reviewed-summary citations,
and verified publisher listening links remain intact. Public episode links are
resolved from existing metadata, not guessed from guest names. The ordinary
build does not read or publish transcripts, raw items, or private locators.

''' + text[end:]
text = replace_once(text, 'reverse index, the narrow quote projection, a manifest, and a build report.', 'reverse index, a manifest, and a build report.')
text = replace_once(text, 'Each quote appears inside its episode card. Source titles, citations, and tags\nare links', 'Episode cards contain cited listening notes without quotations. Source titles,\ncitations, and tags are links')
path.write_text(text, encoding='utf-8')

path = root / 'docs/cognitive-security/topic-guides/IMPLEMENTATION_REPORT.md'
text = path.read_text(encoding='utf-8')
text = replace_once(text, '- 15 verified archived-transcript excerpts, used in 16 episode cards.\n- 47 episode-card placements have no quote. Their cited listening notes remain present; absent quotations were not fabricated or reconstructed from summaries.\n- Quotes are inside episode listings. There is no separate Voices section and no Continue Exploring section.', '- All 63 episode-card placements are quote-free and retain their cited listening notes.\n- Quote collections, identifiers, rendering code, styling, and omission counters are removed. There is no separate Voices section and no Continue Exploring section.')
text = replace_once(text, 'Public provenance still ends at episode releases; the separate small quote collection exposes only approved public fields, not raw items, private source paths, or verification notes.', 'Public provenance still ends at episode releases. The guides publish no transcript quotations, raw items, private source paths, or verification notes.')
text = replace_once(text, '## Executed validation', '## Original implementation validation (before quote removal)')
text = replace_once(text, 'Transcript excerpts were verified against archived text and speaker context, not independently against audio. Timestamps remain absent when unavailable. ', '')
text += '''\n## Citation-only revision\n\nOn 2026-09-14 the user approved the design, requested removal of the quotations,
and authorized continuation. The quote feature is removed completely, not hidden.
Source selection, all 127 ID/name locks, reviewed primary-family assignments,
source citations, featured listening takeaways, and core/discovery data are unchanged.
The original four quote tests are replaced with quote-absence, forbidden-field,
asset-removal, and citation-preservation tests. Desktop/mobile acceptance now
asserts zero quotation blocks on all 15 guides. The schema for changed guide
records is 1.1; the unchanged directory/reverse-index formats remain 1.0.
\nThe existing run above documents the original implementation. The final PR's
checks and subsequent deployment record establish validation/publication of this
revision; the original run is not presented as a test of later changes.
'''
path.write_text(text, encoding='utf-8')
print('Removed quote functionality; preserved 63 episode placements and canonical sources.')
