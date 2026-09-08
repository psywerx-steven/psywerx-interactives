#!/usr/bin/env python3
"""Browser acceptance checks for the Ontology Explorer and Sources projection."""
from __future__ import annotations

import argparse
import json
import tempfile
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


DRIVERS = Path(__file__).resolve().parents[1]
REPO = DRIVERS.parent


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@contextmanager
def serve(directory: Path):
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(directory), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def check(checks, name, value):
    checks.append({"name": name, "pass": bool(value)})
    if not value:
        raise AssertionError(name)


def observe_errors(page, origin):
    script_errors, http_errors = [], []
    page.on("pageerror", lambda error: script_errors.append(str(error)))
    page.on(
        "response",
        lambda response: http_errors.append(f"{response.status} {response.url}")
        if response.url.startswith(origin) and response.status >= 400 else None,
    )
    return script_errors, http_errors


def load(page, url):
    page.goto(url, wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('#source-result-summary')?.textContent.includes('Sources (')"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", default=None, help="Installed Chrome/Edge executable")
    parser.add_argument(
        "--screenshots", type=Path,
        default=Path(tempfile.gettempdir()) / "psywerx-drivers-source-qa",
    )
    args = parser.parse_args()
    checks = []
    args.screenshots.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        launch = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if args.chromium:
            launch["executable_path"] = args.chromium
        browser = playwright.chromium.launch(**launch)
        with serve(REPO) as origin:
            url = origin + "drivers/"
            for width, height in ((1440, 1000), (1024, 768), (768, 1024), (390, 844), (320, 760)):
                page = browser.new_page(viewport={"width": width, "height": height})
                script_errors, http_errors = observe_errors(page, origin)
                load(page, url + "?view=sources")
                if width == 320:
                    page.screenshot(path=str(args.screenshots / "sources-320.png"), full_page=True)
                check(checks, f"{width}px Sources view has no horizontal overflow",
                      page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
                check(checks, f"{width}px Sources controls fit their containers", page.evaluate("""
                  [...document.querySelectorAll('#sources-panel input, #sources-panel button, .source-card')]
                    .every(e => e.getBoundingClientRect().right <= innerWidth + 1)
                """))
                check(checks, f"{width}px has no script errors", not script_errors)
                check(checks, f"{width}px has no local HTTP errors", not http_errors)
                if width in (1440, 390):
                    page.screenshot(
                        path=str(args.screenshots / ("sources-desktop.png" if width == 1440 else "sources-mobile.png")),
                        full_page=True,
                    )
                page.close()

            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            script_errors, http_errors = observe_errors(page, origin)
            load(page, url)
            check(checks, "PSYWERX wordmark resolves to canonical homepage",
                  page.locator("a.wordmark").get_attribute("href") == "https://psywerx.io/")
            check(checks, "Explorer retains three ordered mode controls", page.locator(".mode-switch__button").all_inner_texts()
                  == ["Browse Taxonomy", "Search & Filter", "Sources"])
            check(checks, "Browse Taxonomy remains visible by default", page.locator("#browse-panel").is_visible())
            page.locator("#search-mode-button").click()
            check(checks, "Search & Filter still activates", page.locator("#search-panel").is_visible()
                  and "view=search" in page.url)
            page.locator("#sources-mode-button").click()
            check(checks, "Sources activates in the same Explorer route", page.locator("#sources-panel").is_visible()
                  and "view=sources" in page.url)
            check(checks, "Unfiltered normalized source total is live",
                  page.locator("#source-result-summary").inner_text() == "Sources (510) · Showing 24")

            page.locator('[data-source-facet="layerIds"] input[value="Psychological"]').check()
            psychological_count = int(page.locator("#source-result-summary").inner_text().split("(")[1].split(")")[0])
            check(checks, "Layer facet filters sources", 0 < psychological_count < 510)
            check(checks, "Layer selection narrows Family choices",
                  page.locator('[data-source-facet="familyIds"] input[value^="BIO-"]').count() == 0)
            page.locator('[data-source-facet="layerIds"] input[value="Social"]').check()
            union_count = int(page.locator("#source-result-summary").inner_text().split("(")[1].split(")")[0])
            check(checks, "Layer values combine with OR", union_count > psychological_count)

            page.locator("#clear-source-filters").click()
            page.locator("#source-search").fill("SRC161")
            page.wait_for_timeout(120)
            check(checks, "Keyword search includes stable Source ID", page.locator("#source-result-summary").inner_text() == "Sources (1)")
            page.locator('[data-source-facet="layerIds"] input[value="Psychological"]').check()
            page.locator('[data-source-facet="familyIds"] input[value="PSY-F11"]').check()
            page.locator('[data-source-facet="driverIds"] > summary').click()
            page.locator('[data-source-facet="driverIds"] input[value="PSY-097"]').check()
            check(checks, "Keyword plus Layer, Family, and Driver use AND", page.locator("#source-result-summary").inner_text() == "Sources (1)")
            page.locator('[data-source-facet="driverIds"] > summary').click()
            page.locator('[data-source-facet="driverIds"] input[value="PSY-097"]').uncheck()
            page.locator('[data-source-facet="driverIds"] > summary').click()
            page.locator('[data-source-facet="driverIds"] input[value="PSY-098"]').check()
            check(checks, "Driver facet selects explicit Driver backlinks", page.locator("#source-result-summary").inner_text() == "Sources (1)")
            page.locator('[data-source-facet="layerIds"] input[value="Psychological"]').uncheck()
            check(checks, "Selections remain valid when broadening a parent facet",
                  page.locator('[data-source-facet="familyIds"] input[value="PSY-F11"]').is_checked()
                  and page.locator('[data-source-facet="driverIds"] input[value="PSY-098"]').is_checked())

            page.locator("#clear-source-filters").click()
            page.locator("#source-search").fill("no-such-source-7f91")
            page.wait_for_timeout(120)
            check(checks, "Zero-result source state is useful",
                  "No sources match the current search and filters." in page.locator("#source-list").inner_text())
            page.locator("#clear-source-filters").click()
            check(checks, "Clear restores source corpus", page.locator("#source-result-summary").inner_text().startswith("Sources (510)"))

            page.locator("#source-search").fill("SRC-501")
            page.wait_for_timeout(120)
            relationship = page.locator(".source-relationships-detail")
            if relationship.get_attribute("open") is None:
                relationship.locator("summary").click()
            relationship_text = relationship.inner_text()
            check(checks, "Multi-Driver source spans derived Layers and Families",
                  all(value in relationship_text for value in (
                      "Cultural", "Psychological", "Social",
                      "Shared Values & Moral Priorities", "Normative & Relational Perceptions",
                      "Coordination, Accountability & Collective Capacity",
                  ))
                  and page.locator("[data-source-driver-id]").count() == 3)
            driver_link = page.locator('[data-source-driver-id="CUL-091"]')
            driver_link.click()
            check(checks, "Source to Driver navigation opens canonical Driver detail",
                  page.locator("#driver-dialog").is_visible()
                  and "Civic-Duty Norm Strength" in page.locator("#driver-detail").inner_text())
            page.locator("#close-detail").click()
            page.wait_for_function("!document.querySelector('#driver-dialog').open")
            check(checks, "Closing linked Driver restores Sources view", page.locator("#sources-panel").is_visible())

            first_external = page.locator(".source-card__external-link").first
            check(checks, "External source links use secure isolated behavior",
                  first_external.get_attribute("target") == "_blank"
                  and "noopener" in first_external.get_attribute("rel"))
            check(checks, "Interaction suite has no script errors", not script_errors)
            check(checks, "Interaction suite has no local HTTP errors", not http_errors)
            page.close()

            fallback_page = browser.new_page(viewport={"width": 1024, "height": 768})
            fallback_errors, _ = observe_errors(fallback_page, origin)
            fallback_page.route("**/data/sources.json", lambda route: route.abort())
            fallback_page.goto(url, wait_until="networkidle")
            fallback_page.wait_for_function(
                "!document.querySelector('#browse-summary')?.textContent.includes('Loading')"
            )
            check(checks, "Browse remains available if optional Source data cannot load",
                  fallback_page.locator("#browse-panel").is_visible()
                  and "Taxonomy unavailable" not in fallback_page.locator("#browse-summary").inner_text())
            fallback_page.locator("#search-mode-button").click()
            check(checks, "Search remains available if optional Source data cannot load",
                  fallback_page.locator("#search-panel").is_visible()
                  and "Entities found" in fallback_page.locator("#result-summary").inner_text())
            fallback_page.locator("#sources-mode-button").click()
            check(checks, "Sources degrades to a scoped unavailable state",
                  fallback_page.locator("#source-result-summary").inner_text() == "Sources unavailable"
                  and "Browse Taxonomy and Search & Filter remain available."
                  in fallback_page.locator("#source-list").inner_text()
                  and fallback_page.locator("#load-error").is_hidden())
            check(checks, "Optional Source failure causes no script error", not fallback_errors)
            fallback_page.close()
        browser.close()

    print(json.dumps({"checks": len(checks), "passed": sum(item["pass"] for item in checks)}, indent=2))


if __name__ == "__main__":
    main()
