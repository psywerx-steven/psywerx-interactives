"""Repository integration checks for the Ontology Explorer Sources update."""

import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRIVERS = ROOT / "drivers"


class _ExplorerParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a":
            self.links.append(values)
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])


class DriversSourcesIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = json.loads((ROOT / "homepage/content/site.json").read_text(encoding="utf-8"))
        cls.parser = _ExplorerParser()
        cls.parser.feed((DRIVERS / "index.html").read_text(encoding="utf-8"))

    def test_wordmarks_use_canonical_psywerx_home(self):
        expected = self.site["targetOrigin"].rstrip("/") + "/"
        for page in (DRIVERS / "index.html", DRIVERS / "codebook/index.html"):
            parser = _ExplorerParser()
            parser.feed(page.read_text(encoding="utf-8"))
            wordmark = next(link for link in parser.links if "wordmark" in link.get("class", "").split())
            self.assertEqual(wordmark["href"], expected)
            self.assertEqual(wordmark["aria-label"], "PSYWERX home")

    def test_three_integrated_modes_and_source_controls_exist(self):
        for element_id in (
            "browse-mode-button", "search-mode-button", "sources-mode-button",
            "browse-panel", "search-panel", "sources-panel", "source-search",
            "source-facet-filters", "source-list", "clear-source-filters",
        ):
            self.assertIn(element_id, self.parser.ids)
        self.assertEqual(self.parser.scripts[-2:], ["./source-index.js", "./app.js"])

    def test_source_index_unit_contract(self):
        result = subprocess.run(
            ["node", "--test", "tests/source_index.test.js"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
