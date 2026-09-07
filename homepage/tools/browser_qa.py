#!/usr/bin/env python3
"""Exercise the integrated homepage through local HTTP with an installed Chromium browser."""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import tempfile
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

SOURCE = Path(__file__).resolve().parents[1]
REPO = SOURCE.parent
SITE = REPO / "homepage-preview"
SCREENSHOTS = SOURCE / "qa" / "screenshots"


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


parser = argparse.ArgumentParser()
parser.add_argument("--chromium", default=None, help="Installed Chrome/Edge executable")
args = parser.parse_args()
checks = []


def check(name, value):
    checks.append({"name": name, "pass": bool(value)})
    if not value:
        raise AssertionError(name)


def browser_errors(page, local_origin):
    errors, local_http_errors, remote_requests = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "response",
        lambda response: local_http_errors.append(f"{response.status} {response.url}")
        if response.url.startswith(local_origin) and response.status >= 400
        else None,
    )
    page.on(
        "request",
        lambda request: remote_requests.append(request.url)
        if not request.url.startswith(local_origin) and not request.url.startswith("data:")
        else None,
    )
    return errors, local_http_errors, remote_requests


def load(page, url):
    page.goto(url, wait_until="networkidle")
    page.wait_for_function("window.PSYWERX_HOME && document.querySelectorAll('.area-card').length === 6")
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)", timeout=5000)
    page.evaluate("window.scrollTo(0, 0)")


with sync_playwright() as playwright:
    launch = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
    if args.chromium:
        launch["executable_path"] = args.chromium
    browser = playwright.chromium.launch(**launch)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    with serve(REPO) as origin:
        url = origin + "homepage-preview/"
        for width, height in [(1440, 1000), (1280, 900), (1024, 768), (768, 1024), (500, 900), (390, 844), (320, 760)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors, http_errors, remote = browser_errors(page, origin)
            load(page, url)
            check(f"Layout {width}px: no horizontal overflow", page.evaluate("document.documentElement.scrollWidth<=innerWidth"))
            check(f"Layout {width}px: brand line not clipped", page.evaluate("document.querySelector('h1>span').getBoundingClientRect().right <= document.querySelector('.hero').getBoundingClientRect().right - 15"))
            check(f"Layout {width}px: all supplied images decode", page.evaluate("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)"))
            check(f"Layout {width}px: no script errors", not errors)
            check(f"Layout {width}px: no local HTTP errors", not http_errors)
            check(f"Layout {width}px: no external runtime requests", not remote)
            if width == 1440:
                page.screenshot(path=str(SCREENSHOTS / "desktop.png"), full_page=True)
                page.screenshot(path=str(SCREENSHOTS / "desktop-first-screen.png"))
            if width == 390:
                page.screenshot(path=str(SCREENSHOTS / "mobile.png"), full_page=True)
                page.screenshot(path=str(SCREENSHOTS / "mobile-first-screen.png"))
            page.close()

        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors, http_errors, remote = browser_errors(page, origin)
        load(page, url)
        check("Exactly one homepage H1", page.locator("h1").count() == 1)
        check("Three supplied brand-image treatments render", page.locator('img[src^="assets/"]').count() == 4 and page.evaluate("new Set(Array.from(document.images).map(i=>i.getAttribute('src'))).size") == 2 and "brand-banner.webp" in page.locator(".about-panel").evaluate("e=>getComputedStyle(e,'::after').backgroundImage"))
        check("Mission is visible in the hero", page.locator(".hero-mission").is_visible() and "nonprofit initiative" in page.locator(".hero-mission").inner_text())
        check("Exact brand line appears once", page.evaluate("document.body.innerText.replace(/\\s+/g,' ').split('exploring the human condition from theory to practice').length - 1") == 1)
        check("Six platform cards", page.locator(".area-card").count() == 6)
        check("Six map nodes", page.locator("[data-area]").count() == 6)
        check("Four approved filters plus All", page.locator("[data-filter]").count() == 5)
        check("No search/AI control", page.locator('input[type="search"]').count() == 0 and page.get_by_text("Ask PSYWERX", exact=True).count() == 0)
        check("Two live tool cards use current public explorer URLs", page.locator('a.featured-card[href^="https://drivers.psywerx.io/"]').count() == 2)
        check("Newsletter has no fake input", page.locator('input[type="email"]').count() == 0)
        check("LinkedIn uses the verified company page", page.evaluate("window.PSYWERX_HOME.links.linkedinUrl") == "https://www.linkedin.com/company/psywerx")

        status_labels = {"live": "Live", "progress": "Work in progress", "soon": "Coming soon"}
        platform = page.evaluate("window.PSYWERX_HOME.platform")
        for area in platform:
            card = page.locator(f'#area-{area["id"]}')
            if card.get_attribute("open") is None:
                card.locator("summary").click()
            for tool in area["tools"]:
                item = card.locator("li").filter(has_text=tool["name"])
                check(f'{tool["name"]} displays {status_labels[tool["status"]]} status', item.count() == 1 and status_labels[tool["status"]] in item.inner_text())

        page.locator("#explore-menu>summary").click()
        check("Explore menu opens", page.locator("#explore-menu").get_attribute("open") is not None)
        page.locator(".hero").click(position={"x": 20, "y": 20})
        check("Outside click closes Explore", page.locator("#explore-menu").get_attribute("open") is None)
        page.locator("#explore-menu>summary").click()
        page.keyboard.press("Escape")
        check("Escape closes Explore and restores its trigger", page.locator("#explore-menu").get_attribute("open") is None and page.locator("#explore-menu>summary").evaluate("e=>e===document.activeElement"))
        page.locator("#explore-menu>summary").click()
        page.locator('.mega-link[href="#area-methods"]').click()
        check("Explicit area anchor opens the requested card", page.url.endswith("#area-methods") and page.locator("#area-methods").get_attribute("open") is not None)

        expected_questions = {item["id"]: item["question"] for item in page.evaluate("window.PSYWERX_HOME.platform")}
        for area_id, question in expected_questions.items():
            page.locator(f'[data-area="{area_id}"]').click()
            check(f"Map node {area_id} updates its own content", question in page.locator("#map-detail").inner_text())
            check(f"Map node {area_id} links to its own area", page.locator("#map-detail a").get_attribute("href") == f"#area-{area_id}")
        check("Map selection is exposed accessibly", page.locator('[data-area="learning"]').get_attribute("aria-pressed") == "true")

        page.locator('[data-filter="operations-strategy"]').click()
        check("Operations filter yields the tagged selection", page.locator(".feed-item:visible").count() == 1)
        page.locator('[data-filter="behavioral-science"]').click()
        check("Multi-select filters use union", page.locator(".feed-item:visible").count() == 4)
        check("Filter state is announced", page.locator('[data-filter="behavioral-science"]').get_attribute("aria-pressed") == "true")
        page.locator('[data-filter="all"]').click()
        check("All resets the feed", page.locator(".feed-item:visible").count() == 6)

        trigger = page.locator("[data-feed-detail]").first
        trigger.click()
        check("Feed item opens a native modal dialog", page.locator("#detail-dialog").is_visible() and page.locator("#detail-dialog").get_attribute("open") is not None)
        check("Source and brief dates remain distinct", "Selected in the daily brief" in page.locator("#dialog-body").inner_text() and "Source publication:" in page.locator("#dialog-body").inner_text())
        check("Source link is isolated in a new tab", page.locator("#dialog-body a").get_attribute("target") == "_blank" and "noopener" in page.locator("#dialog-body a").get_attribute("rel"))
        page.keyboard.press("Escape")
        check("Dialog Escape restores focus", not page.locator("#detail-dialog").is_visible() and trigger.evaluate("e=>e===document.activeElement"))
        page.locator('[data-open-dialog="newsletter"]').click()
        check("Unconnected newsletter is explained honestly", "does not collect or submit" in page.locator("#dialog-body").inner_text() and page.locator('input[type="email"]').count() == 0)
        page.keyboard.press("Escape")

        page.emulate_media(reduced_motion="reduce")
        check("Reduced motion disables smooth scrolling", page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto")
        page.emulate_media(forced_colors="active")
        check("Forced colors retains selected state", page.locator('[data-area="learning"]').get_attribute("aria-pressed") == "true")
        page.emulate_media(forced_colors="none", reduced_motion="no-preference")
        page.keyboard.press("Home")
        page.keyboard.press("Tab")
        check("Keyboard focus enters a visible control", page.evaluate("document.activeElement !== document.body && document.activeElement.getBoundingClientRect().width > 0"))
        check("Interaction suite has no script errors", not errors)
        check("Interaction suite has no local HTTP errors", not http_errors)
        check("Interaction suite has no external runtime requests", not remote)
        page.close()

        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors, http_errors, remote = browser_errors(page, origin)
        load(page, url)
        page.locator("#mobile-menu>summary").click()
        check("Mobile menu expands", page.locator("#mobile-menu[open] nav").is_visible())
        page.keyboard.press("Escape")
        check("Mobile Escape closes and restores trigger", page.locator("#mobile-menu").get_attribute("open") is None and page.locator("#mobile-menu>summary").evaluate("e=>e===document.activeElement"))
        check("Mobile feed follows main content", page.evaluate("document.querySelector('aside').getBoundingClientRect().top>=document.querySelector('main').getBoundingClientRect().bottom"))
        check("Mobile interactions have no errors", not errors and not http_errors and not remote)
        page.close()

    spec = importlib.util.spec_from_file_location("homepage_builder", SOURCE / "tools" / "build_homepage.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory() as temp:
        release_root = Path(temp)
        shutil.copytree(SOURCE / "content", release_root / "content")
        shutil.copytree(SOURCE / "src", release_root / "src")
        shutil.copytree(SITE / "assets", release_root / "site" / "assets")
        builder.build("release", "local", release_root)
        with serve(release_root / "site") as release_origin:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            errors, http_errors, remote = browser_errors(page, release_origin)
            page.goto(release_origin, wait_until="networkidle")
            check("Release build excludes every draft selection", page.locator("[data-feed-detail]").count() == 0)
            check("Release build exposes a genuine empty state", "Research selections are on the way" in page.locator(".feed-scroll").inner_text())
            check("Release build removes preview and noindex labels", page.locator(".preview-badge").count() == 0 and page.locator('meta[name="robots"]').count() == 0)
            check("Release build uses same-site explorer paths", page.locator('a.featured-card[href="./drivers/"]').count() == 1 and page.locator('a.featured-card[href="./cognitive-security/"]').count() == 1)
            check("Release browser run has no errors", not errors and not http_errors and not remote)
            page.close()

    browser.close()

report = {
    "scope": "Integrated homepage preview and release editorial behavior, exercised through local HTTP in an installed Chromium browser.",
    "passed": sum(item["pass"] for item in checks),
    "checks": checks,
    "viewports": [1440, 1280, 1024, 768, 500, 390, 320],
}
(SOURCE / "docs" / "BROWSER_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"{report['passed']}/{len(checks)} homepage browser checks passed")
