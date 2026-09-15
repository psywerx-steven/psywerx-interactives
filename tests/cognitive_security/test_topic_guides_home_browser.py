"""Browser acceptance for Topic Guides on the Cognitive Security Explorer landing page."""
from __future__ import annotations

import functools
import http.server
import os
from pathlib import Path
import shutil
import threading
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[2]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class TopicGuidesHomeBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        executable = os.environ.get("PSYWERX_BROWSER_EXECUTABLE") or shutil.which("chromium") or shutil.which("google-chrome")
        if not sync_playwright or not executable:
            raise unittest.SkipTest("Playwright and an existing browser are required")
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1360, "height": 950})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()

    def ready(self):
        self.page.wait_for_function("document.getElementById('app-status').textContent.includes('loaded.')", timeout=15000)
        self.assertFalse(self.page.locator("#load-error").is_visible())
        self.page.locator("#topic-guides-entry-card").wait_for()

    def test_start_page_explains_analysis_and_surfaces_guides_twice(self):
        self.assertEqual(self.page.goto(self.origin + "/cognitive-security/").status, 200)
        self.ready()
        lede = self.page.locator("#landing-hero .hero__lede").inner_text()
        self.assertIn("AI-enabled qualitative analysis", lede)
        self.assertIn("public Cognitive Crucible episodes", lede)
        self.assertIn("curated Topic Guide", self.page.locator("#view-description").inner_text())

        card = self.page.locator("#topic-guides-entry-card")
        self.assertTrue(card.is_visible())
        self.assertEqual(card.locator(".entry-card__title").inner_text(), "Topic Guides")
        self.assertIn("cross-cutting takeaways", card.locator(".entry-card__description").inner_text())
        card.locator(".entry-card__count").wait_for()
        self.assertEqual(card.locator(".entry-card__count").inner_text(), "15")

        overview = self.page.locator("#topic-guides-overview-node")
        self.assertTrue(overview.is_visible())
        self.assertEqual(overview.locator("span").inner_text(), "Topic Guides")
        self.assertEqual(overview.locator("xpath=ancestor::section").locator("h4").inner_text(), "Synthesis and exploration")

        card.click()
        self.assertEqual(self.page.locator("h1").inner_text(), "Topic Guides")
        self.assertFalse(self.errors)

    def test_start_links_survive_optional_guide_data_failure(self):
        self.page.route("**/data/cognitive-security-guides/**", lambda route: route.abort())
        self.assertEqual(self.page.goto(self.origin + "/cognitive-security/").status, 200)
        self.ready()
        self.assertTrue(self.page.locator("#topic-guides-entry-card").is_visible())
        self.assertTrue(self.page.locator("#topic-guides-overview-node").is_visible())
        self.assertEqual(self.page.locator("#topic-guides-entry-card .entry-card__count").count(), 0)
        self.assertFalse(self.errors)


if __name__ == "__main__":
    unittest.main()
