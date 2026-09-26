"""Materialize the bounded RDS-0006 shadow-only compatibility wrapper."""

from __future__ import annotations

import json
from pathlib import Path

import actions_events_v1 as ae
import materialize_rds_computation_phase0 as phase0

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/relational-state-v1/catalog.json"
DATA = ROOT / "data/rds-computation-v1"
GOVERNANCE = "GOV-RDS-IMPLEMENTATION-001-2026-09-25"
DECISION_RECORD = "docs/governance/post-scale-up/rds/RDS_PRODUCTION_IMPLEMENTATION_DECISION_001.md"
PROFILE_ID = "RDS-PROFILE-V1-SOC-F07-001"
BINDING_ID = "RDS-BIND-V1-SOC-F07-001"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def records():
    legacy = next(row for row in read(CATALOG)["bindings"] if row["id"] == "DER-V1-SOC-F07-001")
    legacy_hash = ae.digest(legacy)
    target = legacy["targetRds"]
    source = legacy["inputContract"]["inputEntity"]
    architecture = {"status": "GOVERNED", "decisionId": GOVERNANCE, "decisionRecord": DECISION_RECORD}
    profile = {
        "schemaVersion": "1.0.0",
        "profileId": PROFILE_ID,
        "profileVersion": "1.0.0",
        "rdsId": target["id"],
        "rdsDefinitionVersion": target["definitionVersion"],
        "rdsDefinitionHash": target["definitionHash"],
        "profileType": "DERIVATION_PROFILE",
        "displayName": "RDS-0006 Freeman degree centralization compatibility profile",
        "scientificPurpose": "Additively represent the exact governed DER-V1-SOC-F07-001 calculation for shadow equivalence only.",
        "inputContract": [{
            "inputId": source["id"],
            "role": "CONSTITUENT",
            "required": True,
            "definitionVersion": source["definitionVersion"],
            "definitionHash": source["definitionHash"],
            "collectionSubject": legacy["inputContract"]["collectionSubject"],
            "completenessRule": legacy["inputContract"]["completenessRule"],
        }],
        "minimumInputRequirements": [{"minimumNodes": legacy["minimumNodes"], "completeAlignedCollection": True}],
        "constituentMapping": [{"inputId": source["id"], "role": "CONSTITUENT", "causalConstituentInference": False}],
        "requiredContext": ["networkBoundary", "nodeSet", "tieRelation", "timeWindow"],
        "aggregationFunction": legacy["metricVariant"],
        "calculationReference": legacy["calculationReference"],
        "metricVariant": legacy["metricVariant"],
        "normalization": legacy["normalization"],
        "missingnessPolicy": legacy["inputContract"]["completenessRule"],
        "unitOfAnalysis": "NETWORK",
        "outputScale": "NORMALIZED_NETWORK_CENTRALIZATION",
        "outputInterpretation": "Degree centralization for the exact bound simple, undirected, binary network.",
        "scopeLimitations": legacy["scopeLimitations"],
        "derivationEntailed": True,
        "causalSemantics": "DEFINITIONAL_CALCULATIONAL_RECALCULATION_ONLY_NO_CAUSAL_SUM",
        "causalSourceEligible": False,
        "causalSourceGate": "WP-PSG-005_REQUIRED",
        "executionMode": "SHADOW_ONLY",
        "provenance": {
            "compatibilityWrapperFor": legacy["id"],
            "preservesLegacyId": True,
            "legacyRecordHash": legacy_hash,
            "legacyContributionIdentity": legacy["sharedContributionIdentity"],
            "legacyContributionPolicy": legacy["contributionPolicy"],
            "lineage": legacy["lineage"],
        },
        "architectureGovernance": architecture,
    }
    binding = {
        "schemaVersion": "1.0.0",
        "bindingId": BINDING_ID,
        "bindingVersion": "1.0.0",
        "rdsId": target["id"],
        "rdsDefinitionVersion": target["definitionVersion"],
        "rdsDefinitionHash": target["definitionHash"],
        "profileId": PROFILE_ID,
        "profileVersion": "1.0.0",
        "unitOfAnalysis": "NETWORK",
        "contextContract": {
            "networkBoundary": "EXACT_LEGACY_REQUEST_BOUNDARY_AND_REVISION",
            "nodeSet": legacy["inputContract"]["collectionSubject"],
            "tieRelation": "EXACT_SIMPLE_UNDIRECTED_BINARY_TIE_TYPE_AND_LAYER_FROM_REQUEST",
            "timeWindow": "EXACT_LEGACY_REQUEST_WINDOW",
            "stateAlignment": legacy["inputContract"]["alignment"],
            "minimumNodes": legacy["minimumNodes"],
        },
        "provenance": {
            "compatibilityWrapperFor": legacy["id"],
            "legacyRecordHash": legacy_hash,
            "applicationContextResolvedPerExactLegacyRequest": True,
            "shadowOnly": True,
            "feedsActiveSimulation": False,
            "rollback": "REMOVE_PROFILE_BINDING_INTEGRATION_AND_USE_UNCHANGED_LEGACY_DERIVATION_ONLY",
        },
        "architectureGovernance": architecture,
    }
    return legacy, profile, binding


def main() -> None:
    phase0.main()
    legacy, profile, binding = records()
    write(DATA / "profiles.json", {"schemaVersion": "1.0.0", "registryId": "RDS-COMPUTATION-PROFILES-V1", "profiles": [profile]})
    write(DATA / "bindings.json", {"schemaVersion": "1.0.0", "registryId": "RDS-APPLICATION-BINDINGS-V1", "bindings": [binding]})
    closeout = {
        "schemaVersion": "1.0.0",
        "phaseId": "WP-PSG-001-PHASE-1-RDS-0006-20260925-001",
        "decisionId": GOVERNANCE,
        "phase0MergeSha": "5891518de3603cc69e10638f44ba8db5862cf5df",
        "rdsId": "RDS-0006",
        "profileId": PROFILE_ID,
        "bindingId": BINDING_ID,
        "legacyDerivationId": legacy["id"],
        "legacyRecordHash": ae.digest(legacy),
        "executionMode": "SHADOW_ONLY",
        "feedsActiveSimulation": False,
        "causalSourceEligible": False,
        "causalSourceGate": "WP-PSG-005_REQUIRED",
        "remainingRdsChanged": 0,
        "rollbackState": "UNCHANGED_LEGACY_DERIVATION_ONLY",
    }
    write(ROOT / "data/governance/post-scale-up/rds/rds-0006-phase1-compatibility.json", closeout)


if __name__ == "__main__":
    main()
