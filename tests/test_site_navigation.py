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
    "/": (REPO / "index.html", 2),
    "/homepage-preview/": (REPO / "homepage-preview/index.html", 2),
    "/drivers/": (REPO / "drivers/index.html", 1),
    "/drivers/codebook/": (REPO / "drivers/codebook/index.html", 1),
    "/cognitive-security/": (REPO / "cognitive-security/index.html", 1),
}


def header_markup(page: str) -> str:
    match = re.search(r"<header\b.*?</header>", page, flags=re.DOTALL)
    if match is None:
        raise AssertionError("Public page has no header")
    return match.group(0)


class SiteNavigationTests(unittest.TestCase):
    def test_canonical_home_comes_from_existing_site_configuration(self):
        self.assertEqual("https://psywerx.io/", CANONICAL_HOME)
        builder = (REPO / "homepage/tools/build_homepage.py").read_text(encoding="utf-8")
        template = (REPO / "homepage/src/homepage.template.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('home_url = site["targetOrigin"].rstrip("/") + "/"', builder)
        self.assertEqual(4, template.count('href="{{HOME_URL}}"'))

    def test_every_public_wordmark_and_top_navigation_has_home(self):
        for route, (path, expected_home_links) in PUBLIC_PAGES.items():
            with self.subTest(route=route):
                page = path.read_text(encoding="utf-8")
                header = header_markup(page)
                self.assertRegex(
                    header,
                    rf'<a class="(?:brand|wordmark)" href="{re.escape(CANONICAL_HOME)}" aria-label="PSYWERX home">',
                )
                home_links = re.findall(
                    r'<a\b[^>]*href="([^"]+)"[^>]*>\s*Home\s*</a>', header
                )
                self.assertEqual([CANONICAL_HOME] * expected_home_links, home_links)

                wordmark_links = re.findall(
                    r'<a\b[^>]*class="[^"]*(?:brand|wordmark)[^"]*"[^>]*href="([^"]+)"[^>]*aria-label="PSYWERX home"[^>]*>\s*<img\b[^>]*alt="PSYWERX"',
                    page,
                    flags=re.DOTALL,
                )
                self.assertGreaterEqual(len(wordmark_links), 1)
                self.assertEqual(
                    [CANONICAL_HOME] * len(wordmark_links), wordmark_links
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
