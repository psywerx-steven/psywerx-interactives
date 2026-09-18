"""Site-wide regression checks for canonical homepage navigation."""

import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SITE_CONFIG = json.loads(
    (REPO / "homepage/content/site.json").read_text(encoding="utf-8")
)
CANONICAL_HOME = SITE_CONFIG["targetOrigin"].rstrip("/") + "/"
PUBLIC_PAGES = {
    "/": REPO / "index.html",
    "/homepage-preview/": REPO / "homepage-preview/index.html",
    "/drivers/": REPO / "drivers/index.html",
    "/drivers/codebook/": REPO / "drivers/codebook/index.html",
    "/cognitive-security/": REPO / "cognitive-security/index.html",
}
GLOBAL_LABELS = ("Home", "Explore", "Research", "Learn", "About", "Live tools")


def header_markup(page: str) -> str:
    match = re.search(r"<header\b.*?</header>", page, flags=re.DOTALL)
    if match is None:
        raise AssertionError("Public page has no header")
    return match.group(0)


def is_home_target(value: str) -> bool:
    return value in {CANONICAL_HOME, "/"}


class SiteNavigationTests(unittest.TestCase):
    def test_canonical_home_comes_from_existing_site_configuration(self):
        self.assertEqual("https://psywerx.io/", CANONICAL_HOME)
        builder = (REPO / "homepage/tools/build_homepage.py").read_text(encoding="utf-8")
        template = (REPO / "homepage/src/homepage.template.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('home_url = site["targetOrigin"].rstrip("/") + "/"', builder)
        self.assertEqual(4, template.count('href="{{HOME_URL}}"'))

    def test_every_public_header_uses_psywerx_home_and_global_menu(self):
        for route, path in PUBLIC_PAGES.items():
            with self.subTest(route=route):
                page = path.read_text(encoding="utf-8")
                header = header_markup(page)

                brand_links = re.findall(
                    r'<a\b[^>]*class="[^"]*(?:brand|wordmark|psywerx-global-brand)[^"]*"[^>]*href="([^"]+)"[^>]*aria-label="PSYWERX home"[^>]*>.*?<img\b[^>]*alt="PSYWERX"',
                    page,
                    flags=re.DOTALL,
                )
                self.assertGreaterEqual(len(brand_links), 1)
                self.assertTrue(all(is_home_target(link) for link in brand_links))

                home_links = re.findall(
                    r'<a\b[^>]*href="([^"]+)"[^>]*>\s*Home\s*</a>', header
                )
                self.assertGreaterEqual(len(home_links), 1)
                self.assertTrue(all(is_home_target(link) for link in home_links))

                for label in GLOBAL_LABELS:
                    self.assertIn(label, header)

    def test_public_tools_load_the_shared_header_contract(self):
        expected = {
            "/drivers/": '../shared/site-header.css',
            "/drivers/codebook/": '../../shared/site-header.css',
            "/cognitive-security/": '../shared/site-header.css',
        }
        for route, stylesheet in expected.items():
            with self.subTest(route=route):
                page = PUBLIC_PAGES[route].read_text(encoding="utf-8")
                self.assertIn(f'href="{stylesheet}"', page)
                self.assertIn('class="psywerx-global-header"', page)
                self.assertIn('class="psywerx-product-bar"', page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
