# Contribution control Phase 1 validation

The production registry contains exactly one immutable group with two exact hash-bound members. Validation proves:

- no selection returns `SELECT_ONE_REQUIRED`;
- selecting either representation returns `COUNT_ONCE` and excludes the other;
- selecting both, wrong hashes, wrong group version, or native EA mismatch fails closed;
- an independent same-target contribution remains included;
- `DER-V1-SOC-F07-001` contributes zero causal sum;
- synthetic duplicate `0.2 + 0.2` resolves to `0.2`, and an independent `0.1` produces `0.3`;
- receipts and fingerprints regenerate deterministically;
- source records and all protected science remain unchanged;
- graph, simulation, scenario, RDS, Network State, and cross-level behavior remain unchanged.

The canonical receipts are `data/contribution-control-v1/repetition-shadow-receipts.json`.
