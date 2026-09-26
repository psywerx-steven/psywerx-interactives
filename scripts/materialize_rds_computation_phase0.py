"""Deterministically install governed RDS computation architecture with empty registries."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
DATA = ROOT / "data/rds-computation-v1"


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def base(title: str, required: list[str], properties: dict, additional: bool = False) -> dict:
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"https://psywerx.org/schemas/{title}.schema.json", "title": title, "type": "object", "additionalProperties": additional, "required": required, "properties": properties}


def main() -> None:
    string = {"type": "string", "minLength": 1}
    hash_value = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
    governance = {"type": "object", "additionalProperties": False, "required": ["status", "decisionId", "decisionRecord"], "properties": {"status": {"const": "GOVERNED"}, "decisionId": string, "decisionRecord": string}}
    profile = base("rds-computation-profile", ["schemaVersion", "profileId", "profileVersion", "rdsId", "rdsDefinitionVersion", "rdsDefinitionHash", "profileType", "displayName", "scientificPurpose", "inputContract", "requiredContext", "unitOfAnalysis", "outputScale", "outputInterpretation", "scopeLimitations", "derivationEntailed", "causalSemantics", "causalSourceEligible", "causalSourceGate", "executionMode", "provenance", "architectureGovernance"], {
        "schemaVersion": {"const": "1.0.0"}, "profileId": string, "profileVersion": string, "rdsId": string, "rdsDefinitionVersion": string, "rdsDefinitionHash": hash_value,
        "profileType": {"enum": ["DERIVATION_PROFILE", "MEASUREMENT_PROFILE", "ESTIMATION_PROFILE"]}, "displayName": string, "scientificPurpose": string,
        "inputContract": {"type": "array", "items": {"type": "object", "additionalProperties": True, "required": ["inputId", "role", "required"], "properties": {"inputId": string, "role": {"enum": ["CONSTITUENT", "MEASUREMENT_INPUT", "PARAMETER", "NORMALIZER", "BOUNDARY_INPUT", "REFERENCE_VALUE", "EXTERNAL_CONTEXT", "DATA_SOURCE"]}, "required": {"type": "boolean"}, "definitionVersion": string, "definitionHash": hash_value}}},
        "minimumInputRequirements": {"type": "array", "items": {"type": "object"}}, "constituentMapping": {"type": "array", "items": {"type": "object"}}, "requiredContext": {"type": "array", "items": string, "uniqueItems": True},
        "aggregationFunction": string, "calculationReference": string, "measurementProcedure": {"type": "object"}, "estimationProcedure": {"type": "object"}, "metricVariant": string, "normalization": string, "missingnessPolicy": string,
        "unitOfAnalysis": string, "outputScale": string, "outputInterpretation": string, "scopeLimitations": {"type": "array", "items": string}, "derivationEntailed": {"type": "boolean"}, "causalSemantics": string,
        "causalSourceEligible": {"const": False}, "causalSourceGate": {"const": "WP-PSG-005_REQUIRED"}, "executionMode": {"enum": ["NON_EXECUTABLE", "SHADOW_ONLY"]}, "provenance": {"type": "object"}, "architectureGovernance": governance,
    })
    binding = base("rds-application-binding", ["schemaVersion", "bindingId", "bindingVersion", "rdsId", "rdsDefinitionVersion", "rdsDefinitionHash", "profileId", "profileVersion", "unitOfAnalysis", "contextContract", "provenance", "architectureGovernance"], {
        "schemaVersion": {"const": "1.0.0"}, "bindingId": string, "bindingVersion": string, "rdsId": string, "rdsDefinitionVersion": string, "rdsDefinitionHash": hash_value, "profileId": string, "profileVersion": string, "unitOfAnalysis": string,
        "contextContract": {"type": "object"}, "provenance": {"type": "object"}, "architectureGovernance": governance,
    })
    request = base("rds-execution-request", ["schemaVersion", "requestId", "rdsId", "profileId", "profileVersion", "bindingId", "bindingVersion", "inputs", "parameters", "causalSourceRequested", "simulationFeedRequested"], {
        "schemaVersion": {"const": "1.0.0"}, "requestId": string, "rdsId": string, "profileId": string, "profileVersion": string, "bindingId": string, "bindingVersion": string,
        "inputs": {"type": "object", "additionalProperties": {"type": "object", "required": ["definitionHash", "valueHash"], "properties": {"definitionHash": hash_value, "valueHash": hash_value, "value": {}}}}, "parameters": {"type": "object"}, "causalSourceRequested": {"const": False}, "simulationFeedRequested": {"const": False},
    })
    provenance = base("rds-execution-provenance", ["schemaVersion", "executionState", "rdsId", "rdsDefinitionHash", "profileId", "profileVersion", "bindingId", "bindingVersion", "inputHashes", "parameterHash", "output", "executionFingerprint", "shadowMode", "feedsActiveSimulation", "causalSourceAuthorized"], {
        "schemaVersion": {"const": "1.0.0"}, "executionState": {"const": "EXECUTABLE"}, "rdsId": string, "rdsDefinitionHash": hash_value, "profileId": string, "profileVersion": string, "bindingId": string, "bindingVersion": string, "inputHashes": {"type": "object", "additionalProperties": hash_value}, "parameterHash": hash_value, "output": {}, "executionFingerprint": hash_value, "shadowMode": {"const": True}, "feedsActiveSimulation": {"const": False}, "causalSourceAuthorized": {"const": False}, "legacyDerivationId": string, "legacyReceiptHash": hash_value, "equivalence": {"type": "object"},
    })
    eligibility = base("rds-execution-eligibility", ["schemaVersion", "state", "reason", "causalSourceAuthorized"], {"schemaVersion": {"const": "1.0.0"}, "state": {"enum": ["EXECUTABLE", "NON_EXECUTABLE_NO_PROFILE", "NON_EXECUTABLE_NO_ELIGIBLE_PROFILE", "NON_EXECUTABLE_INCOMPLETE_BINDING", "NON_EXECUTABLE_VERSION_MISMATCH", "NON_EXECUTABLE_DEFINITION_MISMATCH", "NON_EXECUTABLE_INPUT_MISMATCH", "NON_EXECUTABLE_PROFILE_TYPE_UNSUPPORTED", "NON_EXECUTABLE_BLOCKED_BY_SCIENCE", "NON_EXECUTABLE_BLOCKED_BY_ONTOLOGY"]}, "reason": string, "causalSourceAuthorized": {"const": False}})
    for name, value in {"rds-computation-profile.schema.json": profile, "rds-application-binding.schema.json": binding, "rds-execution-request.schema.json": request, "rds-execution-provenance.schema.json": provenance, "rds-execution-eligibility.schema.json": eligibility}.items():
        write(SCHEMAS / name, value)
    write(DATA / "profiles.json", {"schemaVersion": "1.0.0", "registryId": "RDS-COMPUTATION-PROFILES-V1", "profiles": []})
    write(DATA / "bindings.json", {"schemaVersion": "1.0.0", "registryId": "RDS-APPLICATION-BINDINGS-V1", "bindings": []})


if __name__ == "__main__":
    main()
