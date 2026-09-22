"""Verify Physical / Environmental candidate source identities with PubMed."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER/candidate-source-registry.json"


def verify() -> None:
    sources = json.loads(PATH.read_text(encoding="utf-8"))
    pmids = [row["pmid"] for row in sources.values()]
    query = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json"})
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + query
    with urllib.request.urlopen(url, timeout=30) as response:
        result = json.load(response)["result"]
    assert set(result["uids"]) == set(pmids)
    for row in sources.values():
        live = result[row["pmid"]]
        live_doi = next(
            (item["value"].lower() for item in live.get("articleids", []) if item["idtype"] == "doi"),
            None,
        )
        assert row["doi"] == live_doi, row["id"]
        assert row["title"] == live["title"], row["id"]
    print(f"Verified {len(sources)} Physical / Environmental candidate source identities through PubMed/NCBI Eutilities")


if __name__ == "__main__":
    verify()
