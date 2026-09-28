"""Non-production WP-PSG-005 causal-source eligibility evaluator."""
from __future__ import annotations

from typing import Any


ADVISORY_MODES = {
    "DERIVATION_ONLY",
    "ALTERNATE_CAUSAL_ABSTRACTION",
    "INDEPENDENT_AGGREGATE_CAUSAL_SOURCE",
    "CONTEXTUAL_AGGREGATE_CAUSAL_SOURCE",
}


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    """Apply the advisory gate sequence without granting production authority."""
    failures: list[str] = []
    if not case.get("exactConstruct"):
        failures.append("BLOCKED_EXACT_CONSTRUCT_UNDEFINED")
    if case.get("targetContaminated"):
        failures.append("BLOCKED_TARGET_CONTAMINATION")
    elif case.get("definitionalOverlap"):
        failures.append("BLOCKED_DEFINITIONAL_OVERLAP")
    if case.get("multipleVersionsUnresolved"):
        failures.append("BLOCKED_MULTIPLE_VERSIONS")
    if case.get("contributionOverlap") == "UNRESOLVED":
        failures.append("BLOCKED_CONTRIBUTION_OVERLAP")
    if case.get("independentMechanismClaimed") and not case.get("distinctMechanism"):
        failures.append("BLOCKED_NO_DISTINCT_MECHANISM")
    if not case.get("temporalOrder"):
        failures.append("BLOCKED_TEMPORAL_ORDER")
    if case.get("crossLevel") and not case.get("exposureMapping"):
        failures.append("BLOCKED_EXPOSURE_MAPPING")
    if case.get("networkDerived") and not case.get("networkStateBinding"):
        failures.append("BLOCKED_NETWORK_STATE")
    if case.get("evidenceClass") in {None, "INSUFFICIENT", "CONSTITUENT_ONLY", "DEFINITIONAL_CALCULATIONAL", "CROSS_SECTIONAL_ASSOCIATIONAL", "MULTILEVEL_ASSOCIATIONAL"}:
        failures.append("INSUFFICIENT_CAUSAL_EVIDENCE")

    if case.get("derivationOnly"):
        mode = "DERIVATION_ONLY"
        status = "DERIVATION_ONLY"
    elif case.get("alternateAbstraction"):
        mode = "ALTERNATE_CAUSAL_ABSTRACTION"
        status = "ALTERNATE_ABSTRACTION_ONLY" if not failures else failures[0]
    elif case.get("contextual"):
        mode = "CONTEXTUAL_AGGREGATE_CAUSAL_SOURCE"
        status = "ELIGIBLE_FOR_CONTEXTUAL_CAUSAL_REVIEW" if not failures else failures[0]
    else:
        mode = "INDEPENDENT_AGGREGATE_CAUSAL_SOURCE"
        status = "ELIGIBLE_FOR_INDEPENDENT_CAUSAL_REVIEW" if not failures else failures[0]

    return {
        "advisoryMode": mode,
        "advisoryStatus": status,
        "gateFailures": failures,
        "scientificSourceClassCoherent": not any(x in failures for x in {
            "BLOCKED_EXACT_CONSTRUCT_UNDEFINED", "BLOCKED_TARGET_CONTAMINATION",
            "BLOCKED_DEFINITIONAL_OVERLAP", "BLOCKED_MULTIPLE_VERSIONS",
        }),
        "relationshipEvidenceAdequate": "INSUFFICIENT_CAUSAL_EVIDENCE" not in failures,
        "computationallyExecutable": bool(case.get("profileAvailable")),
        "causalSourceEligible": False,
        "executionAuthorized": False,
        "activationAuthorized": False,
        "humanGovernanceRequired": True,
    }
