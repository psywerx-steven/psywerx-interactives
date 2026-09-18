"""Real-browser acceptance for Topic Guides and its optional Explorer links.

Install Playwright separately; use an existing browser via
PSYWERX_BROWSER_EXECUTABLE. The application itself has no new dependencies.
"""
from __future__ import annotations
import functools
import http.server
import json
import os
from pathlib import Path
import shutil
import threading
import unittest
from urllib.parse import parse_qs,urlparse
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright=None
ROOT=Path(__file__).resolve().parents[2]

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class TopicGuidesBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        executable=os.environ.get('PSYWERX_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome')
        if not sync_playwright or not executable:raise unittest.SkipTest('Playwright and an existing browser are required')
        cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.origin=f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox'])
        cls.guides=json.loads((ROOT/'content/cognitive-security-guides/guides.json').read_text())['guides']
        cls.screens=Path(os.environ.get('PSYWERX_GUIDE_SCREENSHOT_DIR','/tmp/psywerx-guide-screenshots'));cls.screens.mkdir(parents=True,exist_ok=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop();cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1360,'height':950});self.page=self.context.new_page();self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
    def tearDown(self):
        self.context.close()
    def guide(self,slug):
        return self.page.goto(self.origin+'/cognitive-security/topic/'+slug+'/')
    def ready(self):
        self.page.wait_for_function("document.getElementById('app-status').textContent.includes('loaded.')",timeout=15000)
        self.assertFalse(self.page.locator('#load-error').is_visible())
    def test_01_all_fifteen_desktop_and_mobile(self):
        for width in (1360,390):
            self.page.set_viewport_size({'width':width,'height':900})
            for g in self.guides:
                with self.subTest(width=width,slug=g['slug']):
                    self.assertEqual(self.guide(g['slug']).status,200)
                    self.assertEqual(self.page.locator('h1').inner_text(),g['title'])
                    self.assertEqual(self.page.locator('.episode-card').count(),len(g['featuredEpisodes']))
                    self.assertEqual(self.page.locator('blockquote, q, .episode-quote').count(),0)
                    self.assertEqual(self.page.locator('.episode-card .source-citation').count(),len(g['featuredEpisodes']))
                    self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
                    self.assertEqual(self.page.locator('meta[property="og:url"]').get_attribute('content'),'https://psywerx.io/cognitive-security/topic/'+g['slug']+'/')
                    self.assertGreater(self.page.locator('.source-citation a').count(),10)
            if width==1360:self.guide('assessment');self.page.screenshot(path=str(self.screens/'assessment-desktop.png'),full_page=True)
            else:self.guide('cyber');self.page.screenshot(path=str(self.screens/'cyber-mobile.png'),full_page=True)
        self.assertFalse(self.errors)
    def test_02_directory_is_flat_three_by_five_grid(self):
        self.page.set_viewport_size({'width':1360,'height':950})
        self.page.goto(self.origin+'/cognitive-security/topic/');cards=self.page.locator('.directory-card')
        self.assertEqual(cards.count(),15);self.assertEqual(self.page.locator('.directory-group, #guide-search').count(),0)
        self.assertEqual(self.page.locator('.directory-card h3 a').count(),15);self.assertEqual(self.page.locator('.directory-card .eyebrow').count(),15)
        self.assertEqual(self.page.locator('.directory-card > p, .directory-card .text-link').count(),0)
        boxes=[cards.nth(i).bounding_box() for i in range(15)]
        self.assertEqual(len({round(box['x']) for box in boxes}),3);self.assertEqual(len({round(box['y']) for box in boxes}),5)
        self.page.screenshot(path=str(self.screens/'topic-guides-directory.png'),full_page=True)
    def test_03_finding_deep_link(self):
        self.guide('data-analytics');self.page.locator('[data-source-type="finding"] h3 a').first.click();self.ready()
        self.assertEqual(parse_qs(urlparse(self.page.url).query)['view'],['finding'])
        self.assertEqual(self.page.locator('#view-title').inner_text(), next(x['title'] for x in json.loads((ROOT/'data/cognitive-security/category_findings.json').read_text()) if x['findingId']=='CF-TTP-F01'))
        self.assertGreater(self.page.locator('a[href*="view=family"]').count(),0)
    def test_04_episode_and_reverse_guide_tag(self):
        self.guide('assessment');self.page.locator('.episode-card h3 a').first.click();self.ready()
        self.page.locator('#curated-guide-tags').wait_for();self.assertIn('Assessment',self.page.locator('#curated-guide-tags').inner_text())
        self.page.locator('#curated-guide-tags a',has_text='Assessment').click();self.assertTrue(self.page.url.endswith('/topic/assessment/'))
    def test_05_back_forward(self):
        self.guide('cyber');self.page.locator('.episode-card h3 a').first.click();self.ready();self.page.go_back();self.assertIn('/topic/cyber/',self.page.url)
        self.page.go_forward();self.ready();self.assertIn('view=episode',self.page.url)
    def test_06_optional_overlay_failure_does_not_break_app(self):
        self.page.route('**/data/cognitive-security-guides/**',lambda route:route.abort())
        self.page.goto(self.origin+'/cognitive-security/?view=cluster&id=CRB-01');self.ready()
        self.assertIn('Assessment',self.page.locator('#view-title').inner_text());self.assertEqual(self.page.locator('#curated-guide-tags').count(),0)
        self.assertFalse(self.errors)
    def test_07_copy_link_uses_canonical_url(self):
        self.page.add_init_script("window.__copied='';Object.defineProperty(navigator,'clipboard',{value:{writeText:async function(t){window.__copied=t;}}});")
        self.guide('narrative');self.page.locator('[data-copy-guide]').click()
        self.assertEqual(self.page.evaluate('window.__copied'),'https://psywerx.io/cognitive-security/topic/narrative/')
    def test_08_keyboard_focus_and_skipping(self):
        self.guide('assessment');self.page.keyboard.press('Tab');self.assertEqual(self.page.locator(':focus').inner_text(),'Skip to content')
        self.page.keyboard.press('Enter');self.assertEqual(self.page.locator(':focus').get_attribute('id'),'main')
        self.page.locator('[data-copy-guide]').focus();self.assertEqual(self.page.locator(':focus').get_attribute('data-copy-guide'),'')
    def test_09_no_js_still_has_full_content(self):
        c=self.browser.new_context(java_script_enabled=False);p=c.new_page();p.goto(self.origin+'/cognitive-security/topic/cyber/')
        self.assertEqual(p.locator('.episode-card').count(),5);self.assertGreater(p.locator('.source-card').count(),10);c.close()
    def test_10_all_actual_canonical_source_targets_render(self):
        # Representative canonical types plus every exact finding used in these guides.
        links={('cluster','KCFT-22'),('cluster','KCFT-23'),('family','CRB-F01'),('theme','TH-05'),('tension','CT-015'),('narrative','CN-03')}
        links|={(r['type'],r['id']) for g in self.guides for refs in g['sections'].values() for r in refs if r['type']=='finding'}
        for kind,identity in links:
            with self.subTest(kind=kind,id=identity):
                self.page.goto(self.origin+f'/cognitive-security/?view={kind}&id={identity}');self.ready()
                self.assertNotIn('could not be displayed',self.page.locator('#view-content').inner_text())
        self.assertFalse(self.errors)
    def test_11_unmapped_entity_has_no_guide_tags(self):
        index=json.loads((ROOT/'data/cognitive-security-guides/reverse_index.json').read_text())['entities'];clusters=json.loads((ROOT/'data/cognitive-security/clusters.json').read_text());unmapped=next(c['clusterId'] for c in clusters if 'cluster:'+c['clusterId'] not in index)
        self.page.goto(self.origin+'/cognitive-security/?view=cluster&id='+unmapped);self.ready();self.page.wait_for_timeout(100)
        self.assertEqual(self.page.locator('#curated-guide-tags').count(),0)
    def test_12_tab_integrated(self):
        self.page.goto(self.origin+'/cognitive-security/');self.ready();self.page.locator('#view-navigation a',has_text='Topic Guides').click();self.assertEqual(self.page.locator('h1').inner_text(),'Topic Guides')
    def test_13_slow_overlay_does_not_leave_stale_tags(self):
        self.page.goto(self.origin+'/cognitive-security/?view=cluster&id=CRB-01');self.ready();self.page.locator('#curated-guide-tags').wait_for()
        self.page.locator('#view-navigation a[data-route-view="methodology"]').click();self.ready();self.assertEqual(self.page.locator('#curated-guide-tags').count(),0)
    def test_14_asset_requests_succeed(self):
        failed=[];self.page.on('response',lambda r:failed.append(r.url) if r.status>=400 else None)
        self.guide('cyber');self.page.wait_for_load_state('networkidle');self.assertFalse(failed)

    def test_15_directory_icons_load_and_match_cards(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from cognitive_security.topic_guides import ICON_CELLS
        failed=[]
        self.page.on('response', lambda r: failed.append(r.url) if r.status>=400 else None)
        for width in (1360, 390, 320):
            self.page.set_viewport_size({'width':width,'height':950})
            self.page.goto(self.origin+'/cognitive-security/topic/')
            self.page.wait_for_load_state('networkidle')
            icons=self.page.locator('.directory-card .topic-guide-icon')
            self.assertEqual(icons.count(), 15)
            self.assertEqual(self.page.locator('.directory-card h3 a').count(),15)
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
            for slug, (col,row) in ICON_CELLS.items():
                icon=self.page.locator('[data-topic-icon="'+slug+'"]')
                self.assertTrue(icon.is_visible())
                self.assertEqual(icon.get_attribute('aria-hidden'),'true')
                self.assertEqual(icon.evaluate('(e)=>getComputedStyle(e).backgroundPosition'),f'{col*25}% {row*50}%')
                card=icon.locator('xpath=ancestor::article')
                self.assertEqual(card.locator('h3 a').get_attribute('href'),'/cognitive-security/topic/'+slug+'/')
            size=self.page.evaluate("""async()=>{const image=new Image(); image.src='/cognitive-security/topic/topic-icons.webp'; await image.decode(); return [image.naturalWidth,image.naturalHeight];}""")
            self.assertEqual(size,[880,528])
            if width==1360:
                self.page.screenshot(path=str(self.screens/'topic-guide-icons-desktop.png'),full_page=True)
            if width==390:
                self.page.screenshot(path=str(self.screens/'topic-guide-icons-mobile.png'),full_page=True)
        self.assertFalse(failed)
        self.assertFalse(self.errors)

    def test_16_directory_icons_need_no_javascript(self):
        context=self.browser.new_context(java_script_enabled=False)
        try:
            page=context.new_page();page.goto(self.origin+'/cognitive-security/topic/')
            self.assertEqual(page.locator('.topic-guide-icon:visible').count(),15)
            page.locator('.directory-card h3 a',has_text='Assessment').click()
            self.assertIn('/topic/assessment/',page.url)
        finally:
            context.close()

if __name__=='__main__':unittest.main()
