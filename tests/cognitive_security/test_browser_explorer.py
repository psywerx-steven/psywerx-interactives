"""End-to-end browser acceptance checks for the canonical static Explorer.

The test has no application runtime dependency.  Install Playwright into a
temporary test environment and point it at an already-installed Chromium
browser; Playwright must not download a browser for this suite.

Example (PowerShell)::

    $env:PYTHONPATH = 'C:\\path\\to\\temporary\\playwright'
    py -m unittest tests.cognitive_security.test_browser_explorer -v

Set ``PSYWERX_BROWSER_EXECUTABLE`` to override browser discovery and
``PSYWERX_QA_SCREENSHOT_DIR`` to retain the three responsive screenshots.
"""

from __future__ import annotations

import functools
import http.server
import json
import os
from pathlib import Path
import threading
import unittest
from urllib.parse import parse_qs, urlencode, urlparse

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError:  # The browser suite is optional in dependency-light CI.
    PlaywrightError = RuntimeError
    sync_playwright = None


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DATA_DIR = REPO_ROOT / "data" / "cognitive-security"
DISCOVERY_DATA_DIR = REPO_ROOT / "data" / "cognitive-security-discovery"
APP_PATH = "cognitive-security/"

SUPPORT_INTERPRETATION = (
    "Corpus support reflects recurrence and breadth within this practitioner "
    "discourse corpus. It does not indicate scientific validity, consensus, "
    "importance, prevalence, or real-world effect size."
)
SC04_NOTICE = (
    "Legal, privacy, civil-liberties, ethics, consent, and affected-community "
    "reviews are required before any operational use. Response options are "
    "analytical possibilities, not validated recommendations. This scenario is "
    "not a recommendation to deploy identity-linked monitoring."
)

PRIMARY_ROUTES = {
    "start": "Cognitive Security Explorer",
    "families": "Categories, subcategories, and topics",
    "themes": "Themes",
    "tensions": "Tensions",
    "narratives": "Narratives",
    "scenarios": "Scenarios",
    "episodes": "Episodes",
    "search": "Search the map",
    "methodology": "Methodology",
}

DETAIL_SPECS = (
    ("theme", "themes.json", "themeId", "theme"),
    ("tension", "tensions.json", "tensionId", "tension"),
    ("narrative", "narratives.json", "narrativeId", "narrative"),
    ("scenario", "scenarios.json", "scenarioId", "scenario"),
)

REPRESENTATIVE_DETAIL_SPECS = (
    ("category", "categories.json", "categoryId", "category"),
    ("family", "families.json", "familyId", "family"),
    ("cluster", "clusters.json", "clusterId", "cluster"),
    ("episode", "episodes.json", "episodeId", "episode"),
)

BROWSER_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)


class _QuietStaticHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


def _records(file_name: str) -> list[dict]:
    payload = json.loads((PUBLIC_DATA_DIR / file_name).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise AssertionError(f"{file_name} is not a canonical record array")
    return payload


class CanonicalExplorerBrowserTests(unittest.TestCase):
    """Browser, responsive, interaction, and accessibility release gate."""

    @classmethod
    def setUpClass(cls) -> None:
        if sync_playwright is None:
            raise unittest.SkipTest(
                "Playwright is not installed; install it into a temporary test "
                "environment and use an existing Chrome/Edge executable"
            )

        override = os.environ.get("PSYWERX_BROWSER_EXECUTABLE")
        candidates = (Path(override),) if override else BROWSER_CANDIDATES
        cls.browser_executable = next((path for path in candidates if path.is_file()), None)
        if cls.browser_executable is None:
            raise unittest.SkipTest("No existing Chrome or Edge executable was found")

        handler = functools.partial(_QuietStaticHandler, directory=str(REPO_ROOT))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.server.daemon_threads = True
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.app_url = f"{cls.origin}/{APP_PATH}"

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=str(cls.browser_executable),
            headless=True,
            args=["--disable-background-networking", "--no-first-run"],
        )
        cls.record_cache = {
            file_name: _records(file_name)
            for file_name in {
                spec[1] for spec in DETAIL_SPECS + REPRESENTATIVE_DETAIL_SPECS
            } | {"category_findings.json", "cluster_summaries.json"}
        }
        cls.discovery_records = {
            row["episodeId"]: row
            for row in json.loads((DISCOVERY_DATA_DIR / "episode_discovery.json").read_text(encoding="utf-8"))["records"]
        }
        cls.metadata_records = {
            row["episodeId"]: row
            for row in json.loads((DISCOVERY_DATA_DIR / "episode_metadata.json").read_text(encoding="utf-8"))
        }

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "browser"):
            cls.browser.close()
        if hasattr(cls, "playwright"):
            cls.playwright.stop()
        if hasattr(cls, "server"):
            cls.server.shutdown()
            cls.server.server_close()
        if hasattr(cls, "server_thread"):
            cls.server_thread.join(timeout=5)

    def setUp(self) -> None:
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 900},
            reduced_motion="no-preference",
        )
        self.context.grant_permissions(
            ["clipboard-read", "clipboard-write"], origin=self.origin
        )
        self.page = self.context.new_page()
        self.console_errors: list[str] = []
        self.page_errors: list[str] = []
        self.request_failures: list[str] = []
        self.http_errors: list[str] = []
        self.requested_paths: list[str] = []
        self.page.on("console", self._capture_console)
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        self.page.on("requestfailed", self._capture_request_failure)
        self.page.on("response", self._capture_response)
        self.page.on(
            "request", lambda request: self.requested_paths.append(urlparse(request.url).path)
        )

    def tearDown(self) -> None:
        failures = (
            [f"console: {message}" for message in self.console_errors]
            + [f"page: {message}" for message in self.page_errors]
            + [f"request: {message}" for message in self.request_failures]
            + [f"HTTP: {message}" for message in self.http_errors]
        )
        try:
            self.assertEqual([], failures, "Browser errors:\n" + "\n".join(failures))
        finally:
            self.context.close()

    def _capture_console(self, message) -> None:
        if message.type == "error":
            self.console_errors.append(message.text)

    def _capture_request_failure(self, request) -> None:
        failure = request.failure
        # A deliberate page navigation can cancel the outgoing document only.
        if failure and "ERR_ABORTED" not in failure:
            self.request_failures.append(f"{request.url}: {failure}")

    def _capture_response(self, response) -> None:
        if response.status >= 400:
            self.http_errors.append(f"{response.status} {response.url}")

    def _url(self, **route: str) -> str:
        return self.app_url + ("?" + urlencode(route) if route else "")

    def _wait_ready(self) -> None:
        # An empty-result route intentionally leaves #view-content visually
        # empty. Initialization also has a short interval between clearing
        # aria-busy and completing route canonicalization, so include the live
        # region's final loaded announcement in the readiness contract.
        self.page.wait_for_function(
            """() => {
              const content = document.querySelector('#view-content');
              const status = document.querySelector('#app-status');
              return content.getAttribute('aria-busy') === 'false' && status.textContent.trim().length > 0;
            }""",
            timeout=20_000,
        )
        self.assertTrue(self.page.locator("#load-error").is_hidden())
        self.assertTrue(self.page.locator("#loading-state").is_hidden())
        self.assertFalse(
            self.page.locator("#view-content .caution-box").filter(
                has_text="This view could not be displayed"
            ).count()
        )

    def _open(self, expected_title: str | None = None, **route: str) -> None:
        response = self.page.goto(self._url(**route), wait_until="domcontentloaded")
        self.assertIsNotNone(response)
        self.assertLess(response.status, 400)
        self._wait_ready()
        if expected_title is not None:
            self.assertEqual(expected_title, self.page.locator("#view-title").inner_text())

    def _navigate(self, route: dict[str, str], expected_title: str | None = None) -> None:
        self.page.evaluate("route => navigate(route, { focus: false })", route)
        self._wait_ready()
        if expected_title is not None:
            self.assertEqual(expected_title, self.page.locator("#view-title").inner_text())

    def _assert_detail(self, route: str, entity_id: str, entity_type: str) -> None:
        self._navigate({"view": route, "id": entity_id})
        marker = self.page.locator(
            f'.record-detail__marker[data-entity-type="{entity_type}"]'
        )
        self.assertEqual(1, marker.count(), f"Missing {route} detail for {entity_id}")
        title = self.page.locator("#view-title").inner_text().strip()
        self.assertTrue(title)
        matching_headings = self.page.locator("h1, h2, h3, h4, h5").evaluate_all(
            "(nodes, title) => nodes.filter(node => node.textContent.trim() === title).length",
            title,
        )
        self.assertEqual(1, matching_headings, f"Duplicate detail title for {entity_id}")
        self.assertNotIn(entity_id, self.page.locator("#view-content").inner_text())
        self.assertEqual("false", self.page.locator("#view-content").get_attribute("aria-busy"))

    def _assert_no_page_overflow(self) -> dict[str, int]:
        dimensions = self.page.evaluate(
            """() => ({
              viewport: document.documentElement.clientWidth,
              document: document.documentElement.scrollWidth,
              body: document.body.scrollWidth
            })"""
        )
        self.assertLessEqual(dimensions["document"], dimensions["viewport"] + 1)
        self.assertLessEqual(dimensions["body"], dimensions["viewport"] + 1)
        return dimensions

    def _save_phase_a_screenshot(self, name: str) -> None:
        directory = os.environ.get("PSYWERX_QA_SCREENSHOT_DIR")
        if not directory:
            return
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(target / name), full_page=True)

    def test_all_primary_and_required_detail_routes_render(self) -> None:
        """Visit 55 public routes, including every governed synthesis detail record."""
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        visited = 1
        for view, title in PRIMARY_ROUTES.items():
            if view == "start":
                continue
            self._navigate({"view": view}, expected_title=title)
            visited += 1

        for route, file_name, id_field, entity_type in DETAIL_SPECS:
            rows = self.record_cache[file_name]
            expected_counts = {"theme": 11, "tension": 20, "narrative": 5, "scenario": 6}
            self.assertEqual(expected_counts[route], len(rows))
            for record in rows:
                self._assert_detail(route, record[id_field], entity_type)
                visited += 1

        for route, file_name, id_field, entity_type in REPRESENTATIVE_DETAIL_SPECS:
            record = self.record_cache[file_name][0]
            self._assert_detail(route, record[id_field], entity_type)
            visited += 1

        self.assertEqual(55, visited)

    def test_startup_is_eager_only_and_evidence_paths_are_progressive(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        startup_paths = set(self.requested_paths)
        self.assertNotIn("/data/cognitive-security/relationships.json", startup_paths)
        self.assertNotIn("/data/cognitive-security/provenance.json", startup_paths)
        self.assertFalse(any("episode_relationships" in path for path in startup_paths))

        family_id = self.record_cache["families.json"][0]["familyId"]
        self._navigate({"view": "family", "id": family_id})
        # The hierarchy view may already have loaded lazy data in another flow;
        # this fresh page verifies explicit disclosure behavior on a detail route.
        load = self.page.get_by_role("button", name="Open connections & sources")
        self.assertEqual(1, load.count())
        load.click()
        self.page.locator("nav.evidence-trail").wait_for(timeout=20_000)
        self.assertIn("/data/cognitive-security/relationships.json", self.requested_paths)
        self.assertIn("/data/cognitive-security/provenance.json", self.requested_paths)
        self.assertGreater(self.page.locator("a.evidence-choice").count(), 0)

        first = self.page.locator("a.evidence-choice").first
        first.click()
        self.page.wait_for_function(
            "() => new URL(location.href).searchParams.has('path')"
        )
        self._wait_ready()
        self.assertEqual(2, self.page.locator("nav.evidence-trail .breadcrumb-current, nav.evidence-trail a").count())
        self.assertIn("no arrow or causal direction", self.page.locator(".evidence-explorer").inner_text())

    def test_public_terminology_and_entity_specific_support_panels(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        hero = self.page.locator(".hero__lede").inner_text()
        self.assertIn("categories, subcategories, and topics", hero)
        self.assertNotIn("approved", hero.casefold())

        generic = (
            "Primary support is the evidence designated as primary for this entity. "
            "Its path depends on entity type"
        )
        cases = (
            (1280, "cluster", "clusters.json", "clusterId", "retained items directly coded to that cluster"),
            (1280, "family", "families.json", "familyId", "primary support comes from its member topics"),
            (500, "theme", "themes.json", "themeId", "primary support comes from primary-support subcategories and topics"),
            (500, "tension", "tensions.json", "tensionId", "evidence directly allocated to Pole A or Pole B"),
            (390, "narrative", "narratives.json", "narrativeId", "primary evidence is inherited through integrated map constructs"),
            (390, "scenario", "scenarios.json", "scenarioId", "primary evidence is traced through relevant map constructs"),
        )
        for width, view, file_name, id_field, clarification in cases:
            with self.subTest(view=view, width=width):
                self.page.set_viewport_size({"width": width, "height": 900})
                entity_id = self.record_cache[file_name][0][id_field]
                self._open(view=view, id=entity_id)
                panel = self.page.locator(".support-panel")
                self.assertEqual(1, panel.count())
                panel.locator("summary").first.click()
                text = panel.inner_text()
                self.assertIn(generic, text)
                self.assertIn(clarification, text)
                self.assertIn("primary-support content units", text)
                self.assertNotIn("direct content units", text.casefold())
                self._assert_no_page_overflow()

    def test_tension_and_cluster_evidence_paths_use_governed_roles(self) -> None:
        provenance = json.loads(
            (PUBLIC_DATA_DIR / "provenance.json").read_text(encoding="utf-8")
        )
        tension_id, dual_link = next(
            (tension_id, link)
            for tension_id, links in provenance["tensionToReleases"].items()
            for link in links
            if len(link["relationships"]) == 2
        )
        episode_id = dual_link["episodeId"]
        episode_title = next(
            row["episodeTitle"]
            for row in self.record_cache["episodes.json"]
            if row["episodeId"] == episode_id
        )

        self._open(view="tension", id=tension_id)
        self.page.get_by_role("button", name="Open connections & sources").click()
        explorer = self.page.locator(".evidence-explorer")
        explorer.locator("nav.evidence-trail").wait_for(timeout=20_000)
        while explorer.locator(".evidence-choice-list__more button").count():
            explorer.locator(".evidence-choice-list__more button").first.click()
        matching_rows = explorer.locator("a.evidence-choice").evaluate_all(
            """(links, title) => links
              .filter(link => link.textContent.trim() === title)
              .map(link => link.closest('li').innerText)""",
            episode_title,
        )
        self.assertEqual(2, len(matching_rows), matching_rows)
        pole_text = "\n".join(matching_rows).casefold()
        self.assertIn("tension evidence pole a", pole_text)
        self.assertIn("tension evidence pole b", pole_text)
        self.assertIn("pole a analytical weight", pole_text)
        self.assertIn("pole b analytical weight", pole_text)
        self.assertNotIn("direct coded support", pole_text)

        cluster_id = self.record_cache["clusters.json"][0]["clusterId"]
        self._open(view="cluster", id=cluster_id)
        self.page.get_by_role("button", name="Open connections & sources").click()
        cluster_explorer = self.page.locator(".evidence-explorer")
        cluster_explorer.locator("nav.evidence-trail").wait_for(timeout=20_000)
        self.assertIn("direct coded support", cluster_explorer.inner_text().casefold())

    def test_heatmap_is_complete_textual_and_keyboard_actionable(self) -> None:
        self._open(expected_title="Themes", view="themes")
        self.page.get_by_text("Compare themes", exact=True).click()
        table = self.page.locator("table.heatmap-table")
        self.assertEqual(1, table.count())
        self.assertEqual(11, table.locator("tbody tr").count())
        self.assertEqual(77, table.locator("td.heatmap-cell").count())
        links = table.locator("a.heatmap-cell__link")
        self.assertEqual(77, links.count())
        for index in range(links.count()):
            link = links.nth(index)
            self.assertRegex(link.inner_text(), r"^\d+(?:\.\d+)?%$")
            accessible_name = link.get_attribute("aria-label") or ""
            self.assertIn("primary subcategories", accessible_name)
            self.assertIn("primary topics", accessible_name)
            self.assertIn("primary-support content units", accessible_name)
            self.assertIn("descriptive, not evidence strength", accessible_name)

        links.first.focus()
        self.page.keyboard.press("Enter")
        self.page.wait_for_function("() => new URL(location.href).searchParams.get('view') === 'theme'")
        self._wait_ready()
        self.assertIn("focused on", self.page.locator("#link-notice").inner_text())

    def test_tension_matrix_filters_preserve_neutral_poles(self) -> None:
        self._open(expected_title="Tensions", view="tensions")
        self.page.get_by_text("Compare tensions", exact=True).click()
        matrix = self.page.locator("table.tension-matrix")
        self.assertEqual(20, matrix.locator("tbody tr").count())
        self.assertIn("neutral two-position constructs", matrix.locator("caption").inner_text())
        self.assertEqual(20, matrix.locator("td.pole-cell--a").count())
        self.assertEqual(20, matrix.locator("td.pole-cell--b").count())
        self.assertEqual(4, matrix.locator("thead th").count())
        self._save_phase_a_screenshot("phase-a-tensions.png")

        form = self.page.get_by_role("search", name="Search and filter tensions")
        form.locator('select[name="support"]').select_option("broad")
        form.get_by_role("button", name="Apply").click()
        self._wait_ready()
        self.page.get_by_text("Compare tensions", exact=True).click()
        filtered_count = self.page.locator("table.tension-matrix tbody tr").count()
        self.assertGreater(filtered_count, 0)
        self.assertLessEqual(filtered_count, 20)
        self.assertEqual("broad", parse_qs(urlparse(self.page.url).query)["support"][0])
        self.assertIn("of 20 tensions", self.page.locator("#view-summary").inner_text())

    def test_search_global_query_facets_and_empty_state(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        global_input = self.page.locator("#global-search-input")
        self.assertFalse(global_input.is_disabled())
        global_input.fill("institutional")
        global_input.press("Enter")
        self._wait_ready()
        self.assertEqual("search", parse_qs(urlparse(self.page.url).query)["view"][0])
        self.assertGreater(self.page.locator(".search-results .map-card").count(), 0)

        self.page.locator("#search-entity-type").select_option("theme")
        self.page.wait_for_function(
            "() => new URL(location.href).searchParams.get('type') === 'theme'"
        )
        self.page.wait_for_function(
            "() => document.querySelector('#search-active-filters').textContent.replace(/\\s+/g, ' ').includes('Type: Theme')"
        )
        self.page.wait_for_function(
            """() => {
              const kickers = Array.from(document.querySelectorAll('.search-results .map-card__kicker'));
              return kickers.length > 0 && kickers.every(node => node.textContent.trim().startsWith('Theme'));
            }"""
        )
        self._wait_ready()
        result_kickers = self.page.locator(".search-results .map-card__kicker").all_inner_texts()
        self.assertTrue(result_kickers)
        self.assertTrue(
            all(text.strip().casefold().startswith("theme") for text in result_kickers),
            result_kickers,
        )

        self.page.locator("#search-input").fill("no-such-canonical-record-7f91")
        self.page.locator("#search-form").get_by_role("button", name="Search").click()
        self.page.wait_for_function(
            "() => new URL(location.href).searchParams.get('q') === 'no-such-canonical-record-7f91'"
        )
        self._wait_ready()
        self.page.locator("#empty-state").wait_for(state="visible")
        self.assertTrue(self.page.locator("#empty-state").is_visible())
        self.assertIn("No records matched", self.page.locator("#empty-state").inner_text())

    def test_sc04_carries_explicit_governance_and_rights_warning(self) -> None:
        self._open(view="scenario", id="SC-04")
        notice = self.page.locator('.scenario-governance-notice[role="note"]')
        self.assertEqual(1, notice.count())
        self.assertEqual("Governance and rights notice", notice.get_attribute("aria-label"))
        notice.locator("summary").click()
        self.assertIn(SC04_NOTICE, notice.inner_text())
        body = self.page.locator("#view-content").inner_text()
        self.assertIn("Response options are analytical possibilities, not validated recommendations.", body)
        self.assertIn("possible future, not a prediction", self.page.locator("#view-kicker").inner_text().casefold())

    def test_legacy_redirects_are_governed_and_unknown_ids_fail_safe(self) -> None:
        # These are individual formerly public URLs, not a published migration table.
        self._open(view="theme", id="XTHEME-001")
        query = parse_qs(urlparse(self.page.url).query)
        self.assertEqual(["theme"], query["view"])
        self.assertEqual(["TH-01"], query["id"])
        notice_state = self.page.locator("#link-notice").evaluate(
            "node => ({ text: node.innerText, hidden: node.hidden, html: node.outerHTML })"
        )
        self.assertTrue(notice_state["hidden"], notice_state)
        self.assertEqual("", notice_state["text"], notice_state)
        successor_title = self.page.locator("#view-title").inner_text()

        self._open(view="theme", id="XTHEME-001")
        self.assertEqual(successor_title, self.page.locator("#view-title").inner_text())
        self.assertEqual(["TH-01"], parse_qs(urlparse(self.page.url).query)["id"])

        self._open(expected_title="Tensions", view="tension", id="TD-001")
        self.assertNotIn("id", parse_qs(urlparse(self.page.url).query))
        self.assertIn(
            "This link points to content that has been reorganized.",
            self.page.locator("#link-notice").inner_text(),
        )

        self._open(expected_title="Categories, subcategories, and topics", view="meta-cluster", id="TTP-M02")
        self.assertIn("No single successor was inferred", self.page.locator("#link-notice").inner_text())

        self._open(expected_title="Themes", view="theme", id="UNKNOWN-PUBLIC-ID")
        self.assertIn("relevant index", self.page.locator("#link-notice").inner_text())
        self._open(expected_title=PRIMARY_ROUTES["start"], view="unknown-view")
        self.assertIn("not part of this public map", self.page.locator("#link-notice").inner_text())

    def test_copy_link_history_forward_back_and_refresh(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        themes_link = self.page.locator('a[data-view-link="themes"]').first
        themes_link.focus()
        self.page.keyboard.press("Enter")
        self._wait_ready()
        self.assertEqual("Themes", self.page.locator("#view-title").inner_text())
        self.page.wait_for_function("() => document.activeElement === document.querySelector('#view-title')")

        theme_link = self.page.locator(".map-card--theme a.entity-link").first
        theme_link.click()
        self._wait_ready()
        detail_url = self.page.url
        detail_title = self.page.locator("#view-title").inner_text()

        self.page.get_by_role("button", name="Copy link").click()
        self.page.locator("#link-notice").wait_for(state="visible")
        self.assertIn("Link copied", self.page.locator("#link-notice").inner_text())
        self.assertEqual(detail_url, self.page.evaluate("navigator.clipboard.readText()"))

        self.page.go_back(wait_until="domcontentloaded")
        self._wait_ready()
        self.assertEqual("Themes", self.page.locator("#view-title").inner_text())
        self.page.go_back(wait_until="domcontentloaded")
        self._wait_ready()
        self.assertEqual(PRIMARY_ROUTES["start"], self.page.locator("#view-title").inner_text())
        self.page.go_forward(wait_until="domcontentloaded")
        self._wait_ready()
        self.assertEqual("Themes", self.page.locator("#view-title").inner_text())
        self.page.go_forward(wait_until="domcontentloaded")
        self._wait_ready()
        self.assertEqual(detail_title, self.page.locator("#view-title").inner_text())
        self.page.reload(wait_until="domcontentloaded")
        self._wait_ready()
        self.assertEqual(detail_url, self.page.url)
        self.assertEqual(detail_title, self.page.locator("#view-title").inner_text())

    def test_keyboard_focus_landmarks_and_accessible_names(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        self.page.locator("body").press("Tab")
        self.assertEqual("skip-link", self.page.evaluate("document.activeElement.className"))
        self.assertTrue(self.page.locator(".skip-link").is_visible())
        self.page.keyboard.press("Enter")
        # Browsers may focus the main target itself or its already focusable view
        # heading; both land keyboard users at the beginning of the map content.
        self.assertIn(
            self.page.evaluate("document.activeElement.id"), ("map-app", "view-title", "page-title")
        )

        self.assertEqual(1, self.page.locator("main").count())
        self.assertEqual(1, self.page.locator("h1").count())
        self.assertGreaterEqual(self.page.locator("nav[aria-label]").count(), 2)
        self.assertEqual([], self.page.locator("h1:empty, h2:empty, h3:empty, h4:empty").all())

        unnamed = self.page.evaluate(
            """() => Array.from(document.querySelectorAll('a, button, input, select, summary'))
              .filter(node => {
                const style = getComputedStyle(node);
                const hiddenInDisclosure = node.closest('details:not([open])') && node.tagName !== 'SUMMARY';
                return !node.disabled && !hiddenInDisclosure && node.getClientRects().length > 0 && style.display !== 'none' && style.visibility !== 'hidden';
              })
              .filter(node => {
                const labels = node.labels ? Array.from(node.labels).map(label => label.innerText).join(' ') : '';
                const imageAlt = Array.from(node.querySelectorAll ? node.querySelectorAll('img') : [])
                  .map(image => image.alt).join(' ');
                return ![node.innerText, node.value, node.getAttribute('aria-label'),
                  node.getAttribute('title'), labels, imageAlt]
                  .some(value => value && String(value).trim());
              })
              .map(node => node.outerHTML.slice(0, 180))"""
        )
        self.assertEqual([], unnamed, "Visible interactive controls need accessible names")

        body_text = self.page.locator("body").inner_text()
        self.assertNotIn("approved canonical synthesis", body_text.casefold())

    def test_landing_icons_and_functional_overview_are_complete(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        cards = self.page.locator("a.entry-card")
        self.assertEqual(10, cards.count())
        icons = cards.locator("picture.entry-icon img")
        self.assertEqual(10, icons.count())
        image_state = icons.evaluate_all(
            "images => images.map(image => ({complete: image.complete, width: image.naturalWidth, height: image.naturalHeight, alt: image.alt}))"
        )
        self.assertTrue(all(row == {"complete": True, "width": 256, "height": 256, "alt": ""} for row in image_state), image_state)
        self.assertEqual(8, self.page.locator(".overview-map a.overview-node").count())
        self.assertEqual(0, self.page.locator('a[href*="category-finding"], a[href*="categoryFinding"]').count())
        self.assertNotIn("Findings & Open Questions", self.page.locator("#view-content").inner_text())
        alternative = self.page.locator("details.overview-text")
        alternative.locator("summary").click()
        self.assertEqual(10, alternative.locator("a").count())
        self.assertIn("do not assert causation", self.page.locator(".functional-overview").inner_text())
        self._save_phase_a_screenshot("phase-a-landing.png")

    def test_embedded_hierarchy_expands_and_search_reveals_ancestors(self) -> None:
        self._open(expected_title=PRIMARY_ROUTES["start"], view="start")
        self.page.evaluate(
            "localStorage.setItem('cognitive-security-hierarchy-expanded', "
            "JSON.stringify({categories: ['CRB'], families: ['CRB-F01']}))"
        )
        self._open(expected_title=PRIMARY_ROUTES["families"], view="families")
        categories = self.page.locator("details.hierarchy-category")
        self.assertEqual(7, categories.count())
        self.assertEqual(0, self.page.locator("details.hierarchy-category[open]").count())
        first_category = categories.first
        first_category.locator(":scope > summary").click()
        self.assertGreater(first_category.locator("details.hierarchy-family").count(), 0)
        first_family = first_category.locator("details.hierarchy-family").first
        first_family.locator(":scope > summary").click()
        self.assertGreater(first_family.locator(".hierarchy-topic-list a").count(), 0)
        self._save_phase_a_screenshot("phase-a-nested-hierarchy.png")

        self._open(expected_title=PRIMARY_ROUTES["families"], view="families", display="subcategories")
        self.assertEqual(7, self.page.locator("details.hierarchy-category[open]").count())
        self.assertEqual(0, self.page.locator("details.hierarchy-family[open]").count())

        self._open(expected_title=PRIMARY_ROUTES["families"], view="families", display="topics")
        self.assertEqual(7, self.page.locator("details.hierarchy-category[open]").count())
        self.assertEqual(7, self.page.locator("details.hierarchy-family[open]").count())

        category_id = self.record_cache["categories.json"][0]["categoryId"]
        self._open(expected_title=PRIMARY_ROUTES["families"], view="families", category=category_id)
        self.assertEqual(1, self.page.locator("details.hierarchy-category[open]").count())

        self._open(expected_title=PRIMARY_ROUTES["families"], view="families")
        topic_name = self.record_cache["clusters.json"][-1]["name"]
        form = self.page.get_by_role("search", name="Search and filter categories, subcategories, and topics")
        form.locator('input[name="q"]').fill(topic_name)
        form.get_by_role("button", name="Apply").click()
        self._wait_ready()
        self.assertGreater(self.page.locator("details.hierarchy-category[open] details.hierarchy-family[open]").count(), 0)
        self.assertIn(topic_name, self.page.locator(".hierarchy-browser").inner_text())

    def test_recurring_pattern_prose_has_no_description_label(self) -> None:
        summary = next(row for row in self.record_cache["cluster_summaries.json"] if row.get("recurringThemes"))
        pattern = summary["recurringThemes"][0]
        self._open(view="cluster", id=summary["clusterId"])
        section = self.page.locator("section.detail-section").filter(
            has=self.page.get_by_role("heading", name="Recurring patterns", exact=True)
        )
        self.assertEqual(1, section.count())
        self.assertIn(pattern["name"], section.inner_text())
        self.assertIn(pattern["description"], section.inner_text())
        self.assertEqual(0, section.locator("dt").count())
        self.assertNotIn("Description", section.inner_text())

    def test_findings_are_absent_publicly_and_legacy_urls_redirect(self) -> None:
        finding = self.record_cache["category_findings.json"][0]
        category = next(
            row for row in self.record_cache["categories.json"]
            if row["categoryId"] == finding["categoryId"]
        )

        self._open(view="category", id=category["categoryId"])
        category_text = self.page.locator("#view-content").inner_text()
        self.assertNotIn("Findings and open questions", category_text)
        self.assertNotIn("Subcategory findings", category_text)
        self.assertNotIn("Integrative category finding", category_text)
        self.page.get_by_role("button", name="Open connections & sources").click()
        self.page.locator("nav.evidence-trail").wait_for(timeout=20_000)
        self.assertEqual(0, self.page.locator('a.evidence-choice[href*="category-finding"]').count())

        family_id = self.record_cache["families.json"][0]["familyId"]
        self._open(view="family", id=family_id)
        self.assertNotIn("What the corpus says", self.page.locator("#view-content").inner_text())

        self._open(view="search")
        self.assertNotIn("categoryFinding", self.page.locator("#search-entity-type option").evaluate_all("nodes => nodes.map(node => node.value)"))
        self.assertEqual(0, self.page.locator('.search-results a[href*="category-finding"]').count())

        self._open(view="category-finding", id=finding["findingId"])
        query = parse_qs(urlparse(self.page.url).query)
        self.assertEqual(["category"], query["view"])
        self.assertEqual([category["categoryId"]], query["id"])
        self.assertEqual(category["name"], self.page.locator("#view-title").inner_text())
        self.assertEqual(0, self.page.locator('[data-entity-type="categoryFinding"]').count())

        self._open(expected_title=PRIMARY_ROUTES["families"], view="category-finding", id="UNKNOWN-FINDING")
        self.assertEqual(["families"], parse_qs(urlparse(self.page.url).query)["view"])

    def test_episode_library_ranges_sort_jump_and_context(self) -> None:
        self._open(expected_title="Episodes", view="episodes")
        self.assertEqual(242, self.page.locator("a.episode-card-link").count())
        self.assertEqual(0, self.page.locator(".episode-card-link__type").count())
        self.assertEqual(0, self.page.locator("a.episode-card-link .entity-badge").count())
        card_states = self.page.locator("a.episode-card-link").evaluate_all(
            "links => links.map(link => ({text: link.innerText, href: link.getAttribute('href'), tag: link.tagName}))"
        )
        self.assertTrue(all("EPI-" not in row["text"] for row in card_states))
        self.assertTrue(all(row["tag"] == "A" and row["href"] for row in card_states))
        self.assertEqual(1, self.page.get_by_text("The Cognitive Crucible", exact=True).count())
        self._save_phase_a_screenshot("phase-a-episode-library.png")
        form = self.page.get_by_role("search", name="Browse episodes")
        form.locator("select").nth(0).select_option("1-29")
        form.locator("select").nth(1).select_option("newest")
        form.get_by_role("button", name="Apply").click()
        self._wait_ready()
        titles = self.page.locator(".episode-card-link__title").all_inner_texts()
        self.assertEqual(29, len(titles))
        self.assertTrue(titles[0].startswith("#29"), titles[0])
        self.assertEqual("newest", self.page.evaluate("localStorage.getItem('psywerx-episode-sort')"))

        jump = self.page.get_by_role("form", name="Jump to episode number")
        jump.locator("input").fill("52")
        jump.get_by_role("button", name="Go").click()
        self.assertIn("No release is recorded as episode 52", self.page.locator("#link-notice").inner_text())

        first = self.page.locator("a.episode-card-link").first
        expected_href = first.get_attribute("href")
        first.click()
        self._wait_ready()
        self.assertIn("range=1-29", self.page.url)
        self.assertIn("sort=newest", self.page.url)
        self.page.get_by_role("link", name="Back to episode list").click()
        self._wait_ready()
        self.assertIn("range=1-29", self.page.url)
        self.assertIn("sort=newest", self.page.url)
        self.assertIsNotNone(expected_href)

    def test_episode_metadata_topics_recommendations_and_lazy_matrix(self) -> None:
        episode_id = next(
            episode_id
            for episode_id, discovery in self.discovery_records.items()
            if discovery["similarOverall"]
            and discovery["defaultMainTopicIds"]
            and self.metadata_records[episode_id]["officialEpisodeUrl"]
            and self.metadata_records[episode_id]["guests"]
        )
        episode = next(row for row in self.record_cache["episodes.json"] if row["episodeId"] == episode_id)
        self._open(view="episode", id=episode_id, range="all", sort="earliest", position="0")
        self.assertEqual(episode["episodeTitle"], self.page.locator("#view-title").inner_text())
        listen = self.page.locator('.view-header__actions a:has-text("Listen & show notes")')
        self.assertEqual(self.metadata_records[episode_id]["officialEpisodeUrl"], listen.get_attribute("href"))
        self.assertEqual("_blank", listen.get_attribute("target"))
        self.assertEqual("noopener noreferrer", listen.get_attribute("rel"))
        self.assertEqual(1, self.page.locator('a:has-text("Listen & show notes")').count())
        source = self.page.locator(".source-citation a")
        self.assertEqual("Information Professionals Association", source.inner_text())
        self.assertEqual(self.metadata_records[episode_id]["officialEpisodeUrl"], source.get_attribute("href"))
        self.assertIn(self.metadata_records[episode_id]["guests"][0], self.page.locator(".episode-metadata").inner_text())
        self.assertEqual(1, self.page.get_by_role("heading", name="Main topics in this episode", exact=True).count())
        self.assertGreater(self.page.locator(".episode-topic-list .entity-chip").count(), 0)
        self.assertGreater(self.page.locator(".similar-episode-card").count(), 0)
        default_text = self.page.locator("main").inner_text()
        self.assertIn("sustained attention", default_text)
        self.assertIn("substantial overlap", default_text)
        for advanced_phrase in (
            "documented repeated-coding",
            "prominence cutoff",
            "weighted Jaccard",
            "IDF",
            "similarity cutoff",
        ):
            self.assertNotIn(advanced_phrase, default_text)
        self.assertIn("Shared main topics", self.page.locator(".similar-episode-card").first.inner_text())
        self.assertNotIn("/data/cognitive-security-discovery/similarity_data.json", self.requested_paths)
        self._save_phase_a_screenshot("phase-a-episode.png")

        self.page.get_by_text("Compare related episodes", exact=True).click()
        matrix = self.page.locator("table.episode-similarity-matrix")
        matrix.wait_for(timeout=20_000)
        self.assertIn("normalized IDF-weighted Jaccard", self.page.locator(".episode-comparison").inner_text())
        self.assertIn("/data/cognitive-security-discovery/similarity_data.json", self.requested_paths)
        self.assertGreater(matrix.locator("tbody tr").count(), 1)
        self.assertLessEqual(matrix.locator("tbody tr").count(), 15)
        self.assertGreater(matrix.get_by_role("button").count(), 0)
        matrix_values = matrix.evaluate(
            """table => Array.from(table.tBodies[0].rows).map(row =>
              Array.from(row.cells).slice(1).map(cell => {
                const button = cell.querySelector('button');
                return button ? Number(button.textContent) : null;
              }))"""
        )
        for row_index, row in enumerate(matrix_values):
            for column_index, value in enumerate(row):
                if value is None:
                    continue
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 1)
                self.assertEqual(value, matrix_values[column_index][row_index])
        matrix.get_by_role("button").first.focus()
        self.assertIn("Topic-overlap value", self.page.locator(".matrix-pair-detail").inner_text())
        self.assertEqual(1, self.page.locator("details.matrix-list-alternative").count())
        self._assert_no_page_overflow()
        self._save_phase_a_screenshot("phase-a-similarity.png")

    def test_reduced_motion_disables_the_only_continuous_animation(self) -> None:
        reduced = self.browser.new_context(
            viewport={"width": 500, "height": 800}, reduced_motion="reduce"
        )
        page = reduced.new_page()
        try:
            page.goto(self._url(view="start"), wait_until="domcontentloaded")
            page.locator('#view-content[aria-busy="false"]').wait_for(timeout=20_000)
            self.assertEqual("reduce", page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduce' : 'other'"))
            animation = page.evaluate(
                """() => {
                  const spinner = document.querySelector('.loading-state__indicator');
                  const style = getComputedStyle(spinner);
                  return { name: style.animationName, duration: style.animationDuration };
                }"""
            )
            self.assertEqual("none", animation["name"])
        finally:
            reduced.close()

    def test_responsive_viewports_contain_wide_visualizations(self) -> None:
        screenshots = os.environ.get("PSYWERX_QA_SCREENSHOT_DIR")
        screenshot_dir = Path(screenshots) if screenshots else None
        if screenshot_dir:
            screenshot_dir.mkdir(parents=True, exist_ok=True)

        measurements = []
        cases = (
            (1280, 900, {"view": "start"}, None),
            (500, 850, {"view": "themes"}, ".heatmap-region"),
            (390, 844, {"view": "tensions"}, ".matrix-region"),
        )
        for width, height, route, contained_selector in cases:
            self.page.set_viewport_size({"width": width, "height": height})
            self._open(**route)
            dimensions = self._assert_no_page_overflow()
            dimensions.update({"width": width, "height": height, "view": route["view"]})
            measurements.append(dimensions)
            if contained_selector:
                region = self.page.locator(contained_selector)
                self.assertEqual(1, region.count())
                contained = region.evaluate(
                    "node => ({ client: node.clientWidth, scroll: node.scrollWidth, overflow: getComputedStyle(node).overflowX })"
                )
                self.assertGreater(contained["scroll"], contained["client"])
                self.assertIn(contained["overflow"], ("auto", "scroll"))
            if screenshot_dir:
                self.page.screenshot(
                    path=str(screenshot_dir / f'{width}-{route["view"]}.png'),
                    full_page=True,
                )

        self.assertEqual([1280, 500, 390], [row["width"] for row in measurements])
        print("responsive browser measurements: " + json.dumps(measurements, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
