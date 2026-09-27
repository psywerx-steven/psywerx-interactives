# WP-PSG-004 contribution identity prototype

This isolated namespace tests cross-class contribution identity and consumer counting policy. It is non-production, creates no scientific record, changes no graph or simulation behavior, and grants no causal, lifecycle, or activation authority.

`schemas/` contains an isolated ContributionGroup schema. `contribution_control.py` provides the immutable registry, validators, centralized resolver and deterministic receipt fingerprint. `build_reference_package.py` records the governed direction and generates the Stage E/F planning artifacts.

Run `python prototypes/contribution-identity-v1/build_reference_package.py` and `python -m unittest discover -s tests -p "test_contribution_identity_stage_e.py"`.
