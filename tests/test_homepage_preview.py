"""Offline and repository-integration acceptance tests for the homepage launch."""
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "homepage"
PREVIEW = REPO / "homepage-preview"
sys.path.insert(0, str(SOURCE / "tools"))
import research_stream as stream

spec = importlib.util.spec_from_file_location("builder", SOURCE / "tools/build_homepage.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def dataset():
    return tuple(
        json.loads((SOURCE / "content" / name).read_text(encoding="utf-8"))
        for name in ("site.json", "platform.json")
    )


def temporary_source():
    context = tempfile.TemporaryDirectory()
    root = Path(context.name)
    shutil.copytree(SOURCE / "content", root / "content")
    shutil.copytree(SOURCE / "src", root / "src")
    shutil.copytree(REPO / "data/research-stream", root / "data/research-stream")
    return context, root


class HomepageTests(unittest.TestCase):
    def test_approved_taxonomies(self):
        self.assertTrue(builder.validate(*dataset()))

    def test_exact_single_brand_line(self):
        self.assertEqual(dataset()[0]["brandLine"], "exploring the human condition from theory to practice")

    def test_only_two_live_explorers(self):
        live = [tool for area in dataset()[1] for tool in area["tools"] if tool["status"] == "live"]
        self.assertEqual({tool["path"] for tool in live}, {"/drivers/", "/cognitive-security/"})

    def test_training_is_coming_soon(self):
        self.assertTrue(all(tool["status"] == "soon" for tool in dataset()[1][-1]["tools"]))

    def test_all_four_stream_categories(self):
        self.assertEqual({category["id"] for category in dataset()[0]["feedCategories"]}, set(builder.EXPECTED_FEED))

    def test_invalid_site_url_rejected(self):
        site, platform = dataset()
        site["targetOrigin"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            builder.validate(site, platform)

    def test_unverified_newsletter_action_rejected(self):
        site, platform = dataset()
        site["newsletterAction"] = "https://example.com/subscribe"
        with self.assertRaises(ValueError):
            builder.validate(site, platform)

    def test_preview_has_no_cname(self):
        self.assertFalse((PREVIEW / "CNAME").exists())

    def test_no_secret_or_private_source_urls(self):
        public_files = [REPO / "index.html", REPO / "robots.txt", REPO / "sitemap.xml", REPO / "data/research-stream/public_feed.json"] + list((REPO / "assets").glob("*"))
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in public_files
            if path.suffix in (".html", ".js", ".css", ".json", ".txt", ".xml")
        )
        self.assertNotRegex(text, r"https://(?:docs\.google\.com|drive\.google\.com)")
        self.assertNotRegex(text, r"sk-[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9]{20,}|C:\\\\Users")
        self.assertNotRegex(text, r"[ÃƒÂ¢Ãƒâ€šÃ¯Â¿Â½]")

    def test_verified_mailerlite_signup_form(self):
        page = (REPO / "index.html").read_text(encoding="utf-8")
        self.assertIn('action="https://assets.mailerlite.com/jsonp/2519483/forms/195936376173102135/subscribe"', page)
        self.assertIn('name="fields[email]"', page)
        self.assertIn('name="ml-submit" value="1"', page)
        self.assertIn('name="anticsrf" value="true"', page)
        self.assertIn('target="_blank"', page)
        self.assertNotIn("groot.mailerlite.com", page)

    def test_no_search_or_ai_control(self):
        page = (REPO / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('type="search"', page)
        self.assertNotIn("Ask PSYWERX", page)

    def test_all_root_assets_exist(self):
        page = (REPO / "index.html").read_text(encoding="utf-8")
        for asset in re.findall(r'(?:src|href)="(assets/[^\"]+)"', page):
            self.assertTrue((REPO / asset).is_file(), asset)

    def test_release_build_is_deterministic(self):
        context, root = temporary_source()
        with context:
            builder.build("release", "local", root)
            first = {path.relative_to(root / "site"): path.read_bytes() for path in (root / "site").rglob("*") if path.is_file()}
            first_public = (root / "data/research-stream/public_feed.json").read_bytes()
            builder.build("release", "local", root)
            second = {path.relative_to(root / "site"): path.read_bytes() for path in (root / "site").rglob("*") if path.is_file()}
            self.assertEqual(first, second)
            self.assertEqual(first_public, (root / "data/research-stream/public_feed.json").read_bytes())

    def test_release_excludes_pending_database_records(self):
        context, root = temporary_source()
        with context:
            report = builder.build("release", "local", root)
            page = (root / "site/index.html").read_text(encoding="utf-8")
            data_text = (root / "site/assets/home-data.js").read_text(encoding="utf-8")
            self.assertEqual(report["feedCount"], 0)
            self.assertEqual(report["feedTotal"], 0)
            self.assertIn("./drivers/", page)
            self.assertNotIn("noindex,nofollow", page)
            self.assertNotIn("questionAndWhy", data_text)
            self.assertIn('<link rel="canonical" href="https://psywerx.io/">', page)
            self.assertIn('<meta name="robots" content="index,follow">', page)

    def test_release_renders_only_public_projection_fields(self):
        context, root = temporary_source()
        with context:
            database = root / "data/research-stream/research_items.jsonl"
            records = stream.load_database(database)
            stream.review_item(database, records[0]["itemId"], "publish", "2026-09-08")
            builder.build("release", "local", root)
            page = (root / "site/index.html").read_text(encoding="utf-8")
            data_text = (root / "site/assets/home-data.js").read_text(encoding="utf-8")
            data = json.loads(data_text[len("window.PSYWERX_HOME = "):].strip().removesuffix(";"))
            self.assertEqual(len(data["feed"]), 1)
            self.assertEqual(set(data["feed"][0]), set(stream.PUBLIC_FIELDS))
            self.assertIn(records[0]["streamTitle"], page)
            self.assertIn(records[0]["attribution"], page)
            self.assertNotIn(records[0]["questionAndWhy"], page + data_text)

    def test_public_stream_allowlist_matches_builder(self):
        self.assertEqual(
            set(builder.PUBLIC_FEED_FIELDS),
            {"itemId", "streamTitle", "streamSummary", "attribution", "sourceUrl", "categories", "publishedAt"},
        )

    def test_preview_excludes_canonical_research_notes(self):
        text = (PREVIEW / "assets/home-data.js").read_text(encoding="utf-8")
        data = json.loads(text[len("window.PSYWERX_HOME = "):].strip().removesuffix(";"))
        self.assertEqual(data["feed"], [])
        for private_field in ("questionAndWhy", "whatTheyDid", "whatTheyFound", "whatItMeans", "sourceVerified", "decisionDate"):
            self.assertNotIn(private_field, text)

    def test_verified_integrations_only(self):
        site = dataset()[0]
        self.assertEqual(site["newsletterAction"], "https://assets.mailerlite.com/jsonp/2519483/forms/195936376173102135/subscribe")
        self.assertEqual(site["linkedinUrl"], "https://www.linkedin.com/company/psywerx")

    def test_launch_root_replaces_redirect_but_defers_cname_cutover(self):
        page = (REPO / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('http-equiv="refresh"', page)
        self.assertNotIn("window.location.replace", page)
        self.assertEqual((REPO / "CNAME").read_text(encoding="utf-8").strip(), "drivers.psywerx.io")

    def test_production_discovery_files(self):
        self.assertEqual((REPO / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nAllow: /\nSitemap: https://psywerx.io/sitemap.xml\n")
        sitemap = (REPO / "sitemap.xml").read_text(encoding="utf-8")
        for url in ("https://psywerx.io/", "https://psywerx.io/drivers/", "https://psywerx.io/drivers/codebook/", "https://psywerx.io/cognitive-security/"):
            self.assertIn(f"<loc>{url}</loc>", sitemap)

    def test_production_social_metadata(self):
        page = (REPO / "index.html").read_text(encoding="utf-8")
        self.assertIn('property="og:title"', page)
        self.assertIn('name="twitter:card" content="summary_large_image"', page)
        self.assertIn('property="og:image" content="https://psywerx.io/assets/brand-banner.webp"', page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
