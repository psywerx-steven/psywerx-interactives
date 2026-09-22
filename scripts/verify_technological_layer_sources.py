"""Verify PMID/DOI identity for Technological candidate sources."""

import json
import re
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/candidates/actions-events-v1/TECHNOLOGICAL_LAYER/candidate-source-registry.json"


def norm(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def verify():
    sources = json.loads(PATH.read_text(encoding="utf-8"))
    pubmed_rows = [x for x in sources.values() if x.get("pmid")]
    query = urllib.parse.urlencode({"db":"pubmed","id":",".join(x["pmid"] for x in pubmed_rows),"retmode":"json"})
    with urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"+query, timeout=30) as response:
        result=json.load(response)["result"]
    assert set(result["uids"]) == {x["pmid"] for x in pubmed_rows}
    for row in pubmed_rows:
        live=result[row["pmid"]]
        doi=next((x["value"].lower() for x in live.get("articleids",[]) if x["idtype"]=="doi"),None)
        assert row["doi"].lower()==doi,row["id"]
        assert norm(row["title"]) == norm(live["title"]), row["id"]

    doi_rows = [x for x in sources.values() if not x.get("pmid")]
    for row in doi_rows:
        request = urllib.request.Request(
            "https://api.crossref.org/works/" + urllib.parse.quote(row["doi"], safe=""),
            headers={"User-Agent": "PSYWERX-source-verifier/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            message = json.load(response)["message"]
        live_title = " ".join(message.get("title") or [])
        similarity = SequenceMatcher(None, norm(row["title"]), norm(live_title)).ratio()
        assert similarity >= 0.70, (row["id"], row["title"], live_title)
        assert norm(message["DOI"]) == norm(row["doi"]), row["id"]

    print(
        f"Verified all {len(sources)} Technological candidate source identities: "
        f"{len(pubmed_rows)} through PubMed/NCBI E-utilities and "
        f"{len(doi_rows)} through Crossref DOI metadata"
    )


if __name__ == "__main__": verify()
