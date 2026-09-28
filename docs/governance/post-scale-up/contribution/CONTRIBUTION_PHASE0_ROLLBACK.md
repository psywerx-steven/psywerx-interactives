# Contribution control Phase 0 rollback

Remove the three contribution-control schemas, `data/contribution-control-v1/groups.json`, `scripts/contribution_control_v1.py`, and their tests/documentation. No scientific or operational record requires restoration because Phase 0 migrates nothing and no existing consumer calls the service.

Phase 1 rollback, if later needed, removes its single group and shadow receipts while preserving native EffectAssertion metadata and both source records unchanged.
