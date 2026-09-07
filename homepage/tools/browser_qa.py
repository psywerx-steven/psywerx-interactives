#!/usr/bin/env python3
"""Exercise the root launch candidate and editorial preview through local HTTP."""
from __future__ import annotations

import argparse
import json
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

SOURCE = Path(__file__).resolve().parents[1]
REPO = SOURCE.parent
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
        for width, height in [(1440, 1000), (1280, 900), (1024, 768), (768, 1024), (500, 900), (390, 844), (320, 760)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors, http_errors, remote = browser_errors(page, origin)
            load(page, origin)
            check(f"Root {width}px: no horizontal overflow", page.evaluate("document.documentElement.scrollWidth<=innerWidth"))
            check(f"Root {width}px: brand line is not clipped", page.evaluate("document.querySelector('h1>span').getBoundingClientRect().right <= document.querySelector('.hero').getBoundingClientRect().right - 15"))
            check(f"Root {width}px: all supplied images decode", page.evaluate("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)"))
            check(f"Root {width}px: newsletter remains within viewport", page.evaluate("document.querySelector('.footer-newsletter').getBoundingClientRect().right <= innerWidth"))
            check(f"Root {width}px: no script errors", not errors)
            check(f"Root {width}px: no local HTTP errors", not http_errors)
            check(f"Root {width}px: no unexpected runtime requests", not remote)
            if width == 1440:
                page.screenshot(path=str(SCREENSHOTS / "desktop.png"), full_page=True)
                page.screenshot(path=str(SCREENSHOTS / "desktop-first-screen.png"))
            if width == 390:
                page.screenshot(path=str(SCREENSHOTS / "mobile.png"), full_page=True)
                page.screenshot(path=str(SCREENSHOTS / "mobile-first-screen.png"))
            page.close()

        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors, http_errors, remote = browser_errors(page, origin)
        load(page, origin)
        check("Production has exactly one H1", page.locator("h1").count() == 1)
        check("Production title is specific", page.title() == "PSYWERX | Behavioral & Social Science in Practice")
        check("Production canonical is exact", page.locator('link[rel="canonical"]').get_attribute("href") == "https://psywerx.io/")
        check("Production is indexable", page.locator('meta[name="robots"]').get_attribute("content") == "index,follow")
        check("Open Graph title is present", page.locator('meta[property="og:title"]').count() == 1)
        check("Social image uses supplied branding", page.locator('meta[property="og:image"]').get_attribute("content") == "https://psywerx.io/assets/brand-banner.webp")
        check("Mission is visible near the top", page.locator(".hero-mission").is_visible() and "nonprofit initiative" in page.locator(".hero-mission").inner_text())
        check("Exact brand line appears once", page.evaluate("document.body.innerText.replace(/\\s+/g,' ').split('exploring the human condition from theory to practice').length - 1") == 1)
        check("Six platform cards are present", page.locator(".area-card").count() == 6)
        check("Six connected-knowledge controls are present", page.locator("[data-area]").count() == 6)
        check("Four approved filters plus All are present", page.locator("[data-filter]").count() == 5)
        check("No Ask PSYWERX control", page.locator('input[type="search"]').count() == 0 and page.get_by_text("Ask PSYWERX", exact=True).count() == 0)
        check("Release excludes all non-published database entries", page.locator(".feed-item").count() == 0)
        check("Release feed has an honest empty state", "Research selections are on the way" in page.locator(".feed-scroll").inner_text())
        check("Release has no older-page request when stream is empty", page.locator("#load-older").is_hidden())
        check("Same-site Driver link", page.locator('a.featured-card[href="./drivers/"]').count() == 1)
        check("Same-site Cognitive Security link", page.locator('a.featured-card[href="./cognitive-security/"]').count() == 1)
        check("Driver route responds", page.request.get(origin + "drivers/").status == 200)
        check("Cognitive Security route responds", page.request.get(origin + "cognitive-security/").status == 200)

        form = page.locator(".footer-newsletter form")
        email = page.locator("#newsletter-email")
        check("Verified MailerLite endpoint is wired", form.get_attribute("action") == "https://assets.mailerlite.com/jsonp/2519483/forms/195936376173102135/subscribe")
        check("Newsletter submits in a new tab", form.get_attribute("target") == "_blank")
        check("Newsletter email is required", email.get_attribute("required") is not None and not email.evaluate("e=>e.checkValidity()"))
        email.fill("not-an-email")
        check("Newsletter rejects malformed email locally", not email.evaluate("e=>e.checkValidity()"))
        email.fill("launch-review@example.com")
        check("Newsletter accepts valid email syntax without submitting", email.evaluate("e=>e.checkValidity()"))
        check("MailerLite hidden fields are preserved", page.locator('input[name="ml-submit"][value="1"]').count() == 1 and page.locator('input[name="anticsrf"][value="true"]').count() == 1)
        linkedin = page.locator('a[href="https://www.linkedin.com/company/psywerx"]')
        check("LinkedIn uses verified company page", linkedin.count() == 1 and linkedin.get_attribute("target") == "_blank" and "noopener" in linkedin.get_attribute("rel"))

        page.locator("#explore-menu>summary").click()
        check("Explore menu opens", page.locator("#explore-menu").get_attribute("open") is not None)
        page.keyboard.press("Escape")
        check("Escape closes Explore and restores trigger", page.locator("#explore-menu").get_attribute("open") is None and page.locator("#explore-menu>summary").evaluate("e=>e===document.activeElement"))
        expected_questions = {item["id"]: item["question"] for item in page.evaluate("window.PSYWERX_HOME.platform")}
        for area_id, question in expected_questions.items():
            page.locator(f'[data-area="{area_id}"]').click()
            check(f"Map node {area_id} updates content", question in page.locator("#map-detail").inner_text())
            check(f"Map node {area_id} links to its area", page.locator("#map-detail a").get_attribute("href") == f"#area-{area_id}")
        check("Map selection is exposed accessibly", page.locator('[data-area="learning"]').get_attribute("aria-pressed") == "true")
        page.emulate_media(reduced_motion="reduce")
        check("Reduced motion disables smooth scrolling", page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto")
        page.emulate_media(forced_colors="active")
        check("Forced colors retains selected state", page.locator('[data-area="learning"]').get_attribute("aria-pressed") == "true")
        page.emulate_media(forced_colors="none", reduced_motion="no-preference")
        page.keyboard.press("Home")
        page.keyboard.press("Tab")
        check("Keyboard focus enters a visible control", page.evaluate("document.activeElement !== document.body && document.activeElement.getBoundingClientRect().width > 0"))
        check("Production interaction suite has no errors", not errors and not http_errors and not remote)
        page.close()

        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors, http_errors, remote = browser_errors(page, origin)
        load(page, origin)
        page.locator("#mobile-menu>summary").click()
        check("Mobile menu expands", page.locator("#mobile-menu[open] nav").is_visible())
        page.keyboard.press("Escape")
        check("Mobile Escape closes and restores trigger", page.locator("#mobile-menu").get_attribute("open") is None and page.locator("#mobile-menu>summary").evaluate("e=>e===document.activeElement"))
        check("Mobile feed follows main content", page.evaluate("document.querySelector('aside').getBoundingClientRect().top>=document.querySelector('main').getBoundingClientRect().bottom"))
        check("Mobile interactions have no errors", not errors and not http_errors and not remote)
        page.close()

        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors, http_errors, remote = browser_errors(page, origin)
        load(page, origin + "homepage-preview/")
        check("Preview remains noindex", page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow")
        check("Preview does not expose pending database records", page.locator(".feed-item").count() == 0 and page.locator(".preview-badge").count() == 1)
        page.evaluate(
            """() => {
              const container = document.querySelector('#feed-items');
              container.replaceChildren();
              [
                ['research-00000000000000000001', 'operations-strategy'],
                ['research-00000000000000000002', 'behavioral-science technology-modeling'],
                ['research-00000000000000000003', 'application-analysis']
              ].forEach(([id, categories]) => {
                const article = document.createElement('article');
                article.className = 'feed-item';
                article.dataset.feedId = id;
                article.dataset.categories = categories;
                article.innerHTML = '<h3>Filter fixture</h3><p>Browser-only public stream fixture.</p>';
                container.append(article);
              });
            }"""
        )
        page.locator('[data-filter="operations-strategy"]').click()
        check("Operations filter yields its loaded selection", page.locator(".feed-item:visible").count() == 1)
        page.locator('[data-filter="behavioral-science"]').click()
        check("Multi-select filters use union", page.locator(".feed-item:visible").count() == 2)
        check("Filter state is announced", page.locator('[data-filter="behavioral-science"]').get_attribute("aria-pressed") == "true")
        page.locator('[data-filter="all"]').click()
        check("All resets the loaded stream", page.locator(".feed-item:visible").count() == 3)
        trigger = page.locator('[data-open-dialog="feed-info"]')
        trigger.click()
        check("Stream explanation opens a native modal dialog", page.locator("#detail-dialog").is_visible() and page.locator("#detail-dialog").get_attribute("open") is not None)
        check("Stream explanation describes explicit owner selection", "owner explicitly chooses to publish" in page.locator("#dialog-body").inner_text())
        page.keyboard.press("Escape")
        check("Dialog Escape restores focus", not page.locator("#detail-dialog").is_visible() and trigger.evaluate("e=>e===document.activeElement"))
        check("Preview interaction suite has no errors", not errors and not http_errors and not remote)
        page.close()

        for width, height in [(1280, 900), (390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors, http_errors, remote = browser_errors(page, origin)
            page.goto(origin + "drivers/", wait_until="networkidle")
            page.wait_for_function("!document.querySelector('#browse-summary').textContent.includes('Loading')")
            check(f"Driver Explorer {width}px: loads its governed taxonomy", page.locator("#browse-content button").count() == 8)
            check(f"Driver Explorer {width}px: no horizontal overflow", page.evaluate("document.documentElement.scrollWidth<=innerWidth"))
            page.locator("#search-mode-button").click()
            page.wait_for_function("document.querySelectorAll('.driver-card').length > 0")
            check(f"Driver Explorer {width}px: search mode renders records", page.locator(".driver-card").count() > 0)
            page.locator("#driver-search").fill("motivation")
            page.wait_for_function("Array.from(document.querySelectorAll('.driver-card')).some(card=>card.textContent.toLowerCase().includes('motivation'))")
            check(f"Driver Explorer {width}px: search remains functional", page.locator(".driver-card").count() > 0)
            check(f"Driver Explorer {width}px: no runtime or HTTP errors", not errors and not http_errors and not remote)
            page.close()

    browser.close()

report = {
    "scope": "Root launch candidate, public-stream controls, and both Explorer routes exercised through local HTTP in Chromium.",
    "passed": sum(item["pass"] for item in checks),
    "checks": checks,
    "viewports": [1440, 1280, 1024, 768, 500, 390, 320],
}
(SOURCE / "docs" / "BROWSER_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"{report['passed']}/{len(checks)} homepage browser checks passed")
