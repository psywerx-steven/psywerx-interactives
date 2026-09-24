"""Verify DOI identity for Institutional / Structural candidate sources."""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/candidates/actions-events-v1/INSTITUTIONAL_STRUCTURAL_LAYER/candidate-source-registry.json"


def norm(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def crossref(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="") + "?mailto=research@example.com"
    request = urllib.request.Request(url, headers={"User-Agent": "PSYWERX-source-verifier/1.0 (mailto:research@example.com)"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)["message"]
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("Crossref retry loop exhausted")


def verify():
    sources = json.loads(PATH.read_text(encoding="utf-8"))
    for row in sources.values():
        message = crossref(row["doi"])
        live_title = " ".join(message.get("title") or [])
        similarity = SequenceMatcher(None, norm(row["title"]), norm(live_title)).ratio()
        assert similarity >= 0.67, (row["id"], row["title"], live_title, similarity)
        assert norm(message["DOI"]) == norm(row["doi"]), row["id"]
    print(f"Verified all {len(sources)} Institutional / Structural candidate source identities through Crossref DOI metadata")


if __name__ == "__main__":
    verify()
