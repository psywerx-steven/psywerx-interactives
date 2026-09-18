"""Deterministic Layer Scale-Up V2 process checks and read-only benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PSY = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"


def read(name: str):
    return json.loads((PSY / name).read_text(encoding="utf-8"))


def psychological_benchmark():
    summary = read("layer-summary.json")
    baseline = read("baseline.json")["summary"]
    governance = read("governance-recommendations.json")
    index = read("governance-index.json")
    overlaps = read("source-overlap-registry.json")
    architecture = read("architecture-escalations.json")
    family_ids = sorted(row["familyId"] for row in summary["families"])
    review_ready = summary["allLifecycleBearingCandidateRecords"]["REVIEW_READY"]
    formal = {
        "relationshipCandidates": summary["newRelationships"],
        "happeningTypes": summary["happeningTypes"],
        "effectAssertions": summary["effectAssertions"],
        "evidenceAssessments": summary["evidenceAssessments"],
    }
    result = {
        "schemaVersion": "1.0.0",
        "benchmark": "PSYCHOLOGICAL_LAYER_READ_ONLY",
        "programId": "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260907-001",
        "sourceState": "COMPLETED_LAYER_PACKAGE; NO_RESEARCH_RERUN",
        "inventory": {
            "families": len(family_ids),
            "familyIds": family_ids,
            "familiesComplete": summary["familiesCompleted"],
            "entities": baseline["entities"],
            "drivers": baseline["drivers"],
            "rds": baseline["rds"],
            "rdsIds": baseline["rdsIds"],
            "existingRelationships": summary["existingReviewedOnce"],
        },
        "formalCandidates": formal,
        "reviewSignals": {
            "reviewReadyLifecycleRecords": review_ready,
            "highPriorityGovernanceRows": summary["decisionPriority"]["HIGH"],
            "governanceRows": len(index),
            "sourceOverlapIssues": len(overlaps),
            "architectureEscalations": len(architecture),
            "preservedBlockers": len(governance["architectureBlockers"]),
        },
        "governanceCompression": governance["compression"],
        "observedStageLoad": {
            "stage0InventoryEntities": baseline["entities"],
            "stage1FamilyLandscapes": len(family_ids),
            "stage2GovernanceRowsAvailableForTriage": len(index),
            "stage3FormalRelationshipAndEffectClaims": formal["relationshipCandidates"] + formal["effectAssertions"],
            "stage4EvidenceAssessments": formal["evidenceAssessments"],
            "stage5CompletedFamilySkepticalReviews": summary["familiesCompleted"],
            "stage6HumanDecisionUnits": governance["compression"]["totalHumanDecisionUnits"],
        },
        "resourceAssessment": {
            "largestObservedWork": [
                "Family-level literature landscape and source extraction",
                "Candidate-specific evidence alignment and null/contrary reconciliation",
                "Cross-Family source, dataset and proposition deduplication",
            ],
            "v2Avoids": [
                "Mandatory deep searches for Driver-domain-property cells with no plausible mechanism",
                "Repeated source extraction before a proposition survives cheap triage",
                "Human votes on duplicated Family references and routine search ledgers",
            ],
            "humanReviewBurden": "Use grouped low-risk decisions plus individual high-consequence science and blockers; the Psychological reference compressed 595 rows to 146 human decision units plus 14 workflow acknowledgements.",
            "modelEscalationRate": "Not numerically estimated. Escalation is limited by recorded reason to ontology, RDS, architecture, conflicting high-quality evidence, high-consequence REVIEW_READY science, or a justified final small-set skeptical review.",
            "tokenOrCreditSavings": "NOT_MEASURED",
        },
    }
    expected = {
        "families": 14, "familiesComplete": 14, "entities": 135,
        "drivers": 134, "rds": 1, "existingRelationships": 111,
    }
    result["validation"] = {
        "expectedInventory": expected,
        "inventoryMatches": all(result["inventory"][key] == value for key, value in expected.items()),
        "soleRdsSurfaced": result["inventory"]["rdsIds"] == ["PSY-078"],
        "formalCandidatesSurfaced": formal == {
            "relationshipCandidates": 1, "happeningTypes": 29,
            "effectAssertions": 30, "evidenceAssessments": 31,
        },
        "threeBlockersSurfaced": result["reviewSignals"]["preservedBlockers"] == 3,
        "reviewReadySurfaced": review_ready == 45,
        "dedupSurfaced": len(overlaps) == 64,
    }
    result["validation"]["passed"] = all(result["validation"].values())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-psychological", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.benchmark_psychological:
        parser.error("Use --benchmark-psychological")
    result = psychological_benchmark()
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if not result["validation"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
