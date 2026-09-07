# Psychological Layer — candidate-only closeout

Program `AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260907-001`; frozen main `de38b3948f511602af7aa94a9cd80b78e1a00298`.

All14 bounded Family audits complete. Human scientific governance remains PENDING. No new GOVERNED/ACTIVE, source registration, canonical modification, external Family audit or PR merge.

Required validation results are recorded in validation-results.json and exact-head GitHub Linux/Windows checks. No test success confers scientific authority.

```json
{
  "ci": "Final pushed head must independently pass both repository Linux and Windows jobs; local results are not CI results.",
  "javascriptFilesParsed": 21,
  "localLinks": {
    "checkedLocalLinks": 686,
    "errors": []
  },
  "noncanonicalCatchAllDiscoveryRun": false,
  "protectedScience": {
    "changed": [],
    "filesCompared": 191,
    "passed": true
  },
  "pythonTests": 610,
  "recordedAt": "2026-09-07T22:09:19.066079+00:00",
  "requiredSteps": [
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "scripts/build_migration_preview_v0_3.py"
      ],
      "exitCode": 0,
      "name": "migration deterministic regeneration",
      "seconds": 0.585,
      "tests": 0
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_migration_v0_3.py"
      ],
      "exitCode": 0,
      "name": "test_migration_v0_3.py",
      "seconds": 1.921,
      "tests": 19
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_relationship_intervention_v1.py"
      ],
      "exitCode": 0,
      "name": "test_relationship_intervention_v1.py",
      "seconds": 1.696,
      "tests": 38
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_bio_f01_pilot.py"
      ],
      "exitCode": 0,
      "name": "test_bio_f01_pilot.py",
      "seconds": 1.297,
      "tests": 13
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_bio_f01_governance_001.py"
      ],
      "exitCode": 0,
      "name": "test_bio_f01_governance_001.py",
      "seconds": 1.791,
      "tests": 15
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_bio_f01_activation_001.py"
      ],
      "exitCode": 0,
      "name": "test_bio_f01_activation_001.py",
      "seconds": 0.863,
      "tests": 11
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_actions_events_v1.py"
      ],
      "exitCode": 0,
      "name": "test_actions_events_v1.py",
      "seconds": 7.206,
      "tests": 65
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_audit_family.py"
      ],
      "exitCode": 0,
      "name": "test_audit_family.py",
      "seconds": 14.492,
      "tests": 14
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_inf_f03_pilot.py"
      ],
      "exitCode": 0,
      "name": "test_inf_f03_pilot.py",
      "seconds": 13.319,
      "tests": 29
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_inf_f03_governance_001.py"
      ],
      "exitCode": 0,
      "name": "test_inf_f03_governance_001.py",
      "seconds": 1.945,
      "tests": 17
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_inf_f03_activation_audit_001.py"
      ],
      "exitCode": 0,
      "name": "test_inf_f03_activation_audit_001.py",
      "seconds": 1.407,
      "tests": 14
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_inf_f03_activation_001.py"
      ],
      "exitCode": 0,
      "name": "test_inf_f03_activation_001.py",
      "seconds": 1.74,
      "tests": 14
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_soc_f07_pilot.py"
      ],
      "exitCode": 0,
      "name": "test_soc_f07_pilot.py",
      "seconds": 20.654,
      "tests": 36
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_soc_f07_governance_001.py"
      ],
      "exitCode": 0,
      "name": "test_soc_f07_governance_001.py",
      "seconds": 7.693,
      "tests": 19
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_network_state_vnext.py"
      ],
      "exitCode": 0,
      "name": "test_network_state_vnext.py",
      "seconds": 0.991,
      "tests": 43
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_relational_state_v1.py"
      ],
      "exitCode": 0,
      "name": "test_relational_state_v1.py",
      "seconds": 9.014,
      "tests": 52
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_source_verification_v1.py"
      ],
      "exitCode": 0,
      "name": "test_source_verification_v1.py",
      "seconds": 4.522,
      "tests": 18
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_psychological_layer*.py"
      ],
      "exitCode": 0,
      "name": "test_psychological_layer*.py",
      "seconds": 79.241,
      "tests": 181
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_soc_f07_completion.py"
      ],
      "exitCode": 0,
      "name": "test_soc_f07_completion.py",
      "seconds": 10.174,
      "tests": 12
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "scripts/relationship_intervention_v1.py",
        "--validate-repository"
      ],
      "exitCode": 0,
      "name": "relationship_intervention_v1.py",
      "seconds": 0.828,
      "tests": 0
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "scripts/actions_events_v1.py",
        "--validate-repository"
      ],
      "exitCode": 0,
      "name": "actions_events_v1.py",
      "seconds": 1.983,
      "tests": 0
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "scripts/actions_events_synthetic.py"
      ],
      "exitCode": 0,
      "name": "actions_events_synthetic.py",
      "seconds": 1.266,
      "tests": 0
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "scripts/network_state_integrity.py"
      ],
      "exitCode": 0,
      "name": "network_state_integrity.py",
      "seconds": 22.808,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\npm.CMD",
        "test"
      ],
      "exitCode": 0,
      "name": "scenario-service",
      "seconds": 4.02,
      "tests": 0
    },
    {
      "command": [
        "C:\\Users\\davic\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "-m",
        "compileall",
        "-q",
        "scripts",
        "tests",
        "experiments/network-state-vnext"
      ],
      "exitCode": 0,
      "name": "Python compilation",
      "seconds": 0.234,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "cognitive-security/app.js"
      ],
      "exitCode": 0,
      "name": "JavaScript cognitive-security/app.js",
      "seconds": 0.1,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "drivers/app.js"
      ],
      "exitCode": 0,
      "name": "JavaScript drivers/app.js",
      "seconds": 0.079,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "drivers/causal.js"
      ],
      "exitCode": 0,
      "name": "JavaScript drivers/causal.js",
      "seconds": 0.08,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "drivers/codebook/app.js"
      ],
      "exitCode": 0,
      "name": "JavaScript drivers/codebook/app.js",
      "seconds": 0.078,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "drivers/config.js"
      ],
      "exitCode": 0,
      "name": "JavaScript drivers/config.js",
      "seconds": 0.079,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "homepage-preview/assets/home-data.js"
      ],
      "exitCode": 0,
      "name": "JavaScript homepage-preview/assets/home-data.js",
      "seconds": 0.075,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "homepage-preview/assets/home.js"
      ],
      "exitCode": 0,
      "name": "JavaScript homepage-preview/assets/home.js",
      "seconds": 0.1,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/catalog.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/catalog.js",
      "seconds": 0.065,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/config.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/config.js",
      "seconds": 0.062,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/contracts.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/contracts.js",
      "seconds": 0.062,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/http-app.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/http-app.js",
      "seconds": 0.064,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/openai-service.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/openai-service.js",
      "seconds": 0.138,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/prompt.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/prompt.js",
      "seconds": 0.062,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/rate-limit.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/rate-limit.js",
      "seconds": 0.067,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/src/server.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/src/server.js",
      "seconds": 0.06,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/test/catalog.test.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/test/catalog.test.js",
      "seconds": 0.056,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/test/contracts.test.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/test/contracts.test.js",
      "seconds": 0.069,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/test/current-catalogs.test.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/test/current-catalogs.test.js",
      "seconds": 0.062,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/test/fixtures.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/test/fixtures.js",
      "seconds": 0.056,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/test/http-app.test.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/test/http-app.test.js",
      "seconds": 0.056,
      "tests": 0
    },
    {
      "command": [
        "C:\\Program Files\\nodejs\\node.EXE",
        "--check",
        "scenario-service/test/openai-service.test.js"
      ],
      "exitCode": 0,
      "name": "JavaScript scenario-service/test/openai-service.test.js",
      "seconds": 0.055,
      "tests": 0
    },
    {
      "command": [
        "git",
        "diff",
        "--check"
      ],
      "exitCode": 0,
      "name": "git diff check",
      "seconds": 0.125,
      "tests": 0
    }
  ],
  "scientificGovernanceAuthorized": false,
  "status": "PASS",
  "validatedWorkingTreeBasedOn": "d43a2c0c422ed19d310c01380813982a9959f890"
}
```
