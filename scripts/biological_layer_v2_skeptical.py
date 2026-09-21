"""Independent, fail-closed skeptical pass over bounded deep routes."""

from biological_layer_v2 import DATA, read, write, validate_protection


def review() -> None:
    validate_protection()
    findings = read(DATA / "source-findings.json")
    by_claim = {}
    for row in findings: by_claim.setdefault(row["claimId"], []).append(row)
    overlaps = read(DATA / "source-overlap-registry.json")
    deep = read(DATA / "deep-research-ledger.json")
    effect = next(x for x in read(DATA / "actions-events-hypotheses.json") if x["id"] == "EA-CAND-BIO-LAYER-0001")
    eva = read(DATA / "evidence-assessments.json")[0]
    assert len(deep) == 4 and len(overlaps) >= 4
    assert effect["status"] == "RESEARCH_NEEDED" and eva["disposition"] == "MIXED"
    checks = [
      {"id":"SK-BIO-001","claimId":"HYP-BIO-LAYER-006","findingIds":[x["id"] for x in by_claim["HYP-BIO-LAYER-006"]],
       "attemptedFalsification":["Cytokines and mood are not a whole sickness-intensity scale", "Small male-only samples", "Working-memory accuracy null and high-dose reaction-time improvement"],
       "result":"KEEP_RESEARCH_NEEDED", "reason":"Acute response exists but exact BIO-030 state, measure, population and dose transfer remain unresolved."},
      {"id":"SK-BIO-002","claimId":"HYP-BIO-LAYER-008","findingIds":[x["id"] for x in by_claim["HYP-BIO-LAYER-008"]],
       "attemptedFalsification":["General self-rated fatigue is not exact physical fatigue", "Objective capacity shows no clear change", "2018 meta-analysis includes the 2003 and 2012 primary trials"],
       "result":"KEEP_RESEARCH_NEEDED", "reason":"Trial support cannot be generalized to the exact BIO-025 target or counted twice."},
      {"id":"SK-BIO-003","claimId":"HYP-BIO-LAYER-009","findingIds":[x["id"] for x in by_claim["HYP-BIO-LAYER-009"]],
       "attemptedFalsification":["Randomized fatigability null in older mild subclinical hypothyroidism", "Separate cognition trial is a different endpoint", "Hormone status is not administered treatment"],
       "result":"REJECT_BROAD_PROPOSAL", "reason":"No universal thyroid-therapy fatigue benefit can be inferred; no universal hormone-to-fatigue null is asserted."},
      {"id":"SK-BIO-004","claimId":"EA-CAND-BIO-LAYER-0001","findingIds":[x["id"] for x in by_claim["EA-CAND-BIO-LAYER-0001"]],
       "attemptedFalsification":["1999 selected pilot has 11/18 without reported symptoms", "1990 prolonged phase has 3/7 nonresponders but later repeated short substitution detects effects in all seven", "Review contains the primary studies and is not independent replication", "Headache/fatigue frequencies do not define one whole BIO-066 severity aggregation"],
       "result":"DOWNGRADE_TO_KEEP_RESEARCH_NEEDED", "reason":"Cessation identity is coherent, but whole-target effect and population transfer are not governance-ready."},
    ]
    assert all(x["findingIds"] for x in checks)
    assert {x["claimId"] for x in checks} == {x["hypothesisId"] for x in deep}
    write(DATA / "skeptical-review.json", checks)
    print("Skeptical routes", len(checks), "formal effects downgraded", 1)


if __name__ == "__main__": review()
