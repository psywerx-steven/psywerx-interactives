"""Offline and repository-integration acceptance tests for the homepage launch."""
import copy
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "homepage"
PREVIEW = REPO / "homepage-preview"
spec = importlib.util.spec_from_file_location("builder", SOURCE / "tools/build_homepage.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def dataset():
    return tuple(
        json.loads((SOURCE / "content" / name).read_text(encoding="utf-8"))
        for name in ("site.json", "platform.json", "feed.json")
    )


def temporary_source():
    context = tempfile.TemporaryDirectory()
    root = Path(context.name)
    shutil.copytree(SOURCE / "content", root / "content")
    shutil.copytree(SOURCE / "src", root / "src")
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

    def test_no_false_public_approval(self):
        self.assertTrue(all(item["status"] == "draft" for item in dataset()[2]))

    def test_feed_has_all_four_categories(self):
        self.assertEqual(set().union(*(set(item["categories"]) for item in dataset()[2])), set(builder.EXPECTED_FEED))

    def test_feed_preserves_source_and_brief_dates(self):
        self.assertTrue(any(item["sourcePublishedAt"] != item["briefDate"] for item in dataset()[2]))

    def test_invalid_url_rejected(self):
        site, platform, feed = dataset()
        feed[0]["sourceUrl"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            builder.validate(site, platform, feed)

    def test_unverified_newsletter_action_rejected(self):
        site, platform, feed = dataset()
        site["newsletterAction"] = "https://example.com/subscribe"
        with self.assertRaises(ValueError):
            builder.validate(site, platform, feed)

    def test_duplicate_id_rejected(self):
        site, platform, feed = dataset()
        feed.append(copy.deepcopy(feed[0]))
        with self.assertRaises(ValueError):
            builder.validate(site, platform, feed)

    def test_approval_requires_source_verification(self):
        site, platform, feed = dataset()
        feed[0]["status"] = "approved"
        feed[0]["primarySourceChecked"] = False
        with self.assertRaises(ValueError):
            builder.validate(site, platform, feed)

    def test_approval_requires_review_date(self):
        site, platform, feed = dataset()
        feed[0]["status"] = "approved"
        with self.assertRaises(KeyError):
            builder.validate(site, platform, feed)

    def test_preview_has_no_cname(self):
        self.assertFalse((PREVIEW / "CNAME").exists())

    def test_no_secret_or_private_source_urls(self):
        public_files = [REPO / "index.html", REPO / "robots.txt", REPO / "sitemap.xml"] + list((REPO / "assets").glob("*"))
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in public_files
            if path.suffix in (".html", ".js", ".css", ".json", ".txt", ".xml")
        )
        self.assertNotRegex(text, r"https://(?:docs\.google\.com|drive\.google\.com)")
        self.assertNotRegex(text, r"sk-[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9]{20,}|C:\\\\Users")
        self.assertNotRegex(text, r"[Ã¢Ã‚ï¿½]")

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
            builder.build("release", "local", root)
            second = {path.relative_to(root / "site"): path.read_bytes() for path in (root / "site").rglob("*") if path.is_file()}
            self.assertEqual(first, second)

    def test_release_excludes_unapproved_feed(self):
        context, root = temporary_source()
        with context:
            report = builder.build("release", "local", root)
            page = (root / "site/index.html").read_text(encoding="utf-8")
            self.assertEqual(report["feedCount"], 0)
            self.assertIn("./drivers/", page)
            self.assertNotIn("noindex,nofollow", page)
            self.assertNotIn("data-feed-detail=", page)
            self.assertIn('<link rel="canonical" href="https://psywerx.io/">', page)
            self.assertIn('<meta name="robots" content="index,follow">', page)

    def test_public_feed_allowlist(self):
        text = (PREVIEW / "assets/home-data.js").read_text(encoding="utf-8")
        data = json.loads(text[len("window.PSYWERX_HOME = "):].strip().removesuffix(";"))
        self.assertEqual(set(data["feed"][0]), set(builder.PUBLIC_FEED_FIELDS))

    def test_verified_integrations_only(self):
        site = dataset()[0]
        self.assertEqual(site["newsletterAction"], "https://assets.mailerlite.com/jsonp/2519483/forms/195936376173102135/subscribe")
        self.assertEqual(site["linkedinUrl"], "https://www.linkedin.com/company/psywerx")

    def test_preview_excludes_editorial_control_fields(self):
        text = (PREVIEW / "assets/home-data.js").read_text(encoding="utf-8")
        data = json.loads(text[len("window.PSYWERX_HOME = "):].strip().removesuffix(";"))
        for private_field in ("primarySourceChecked", "reviewedAt", "status", "order"):
            self.assertTrue(all(private_field not in item for item in data["feed"]))

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

    def test_date_is_valid(self):
        site, platform, feed = dataset()
        feed[0]["briefDate"] = "2026-22-90"
        with self.assertRaises(ValueError):
            builder.validate(site, platform, feed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
