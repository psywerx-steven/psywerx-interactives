# RDS causal-source case reviews

These are advisory architecture/evidence findings. Production records and dispositions remain unchanged.

## Blocker and route findings

- `BIO-003` → `BIO-001` (`REL-BIO-001`): **BLOCKED_MULTIPLE_VERSIONS**. Source class: The alignment construct can support a coherent phase/schedule contrast, but the current broad aggregate does not bind one version. Evidence: Forced-desynchrony evidence supports circadian phase effects on sleep propensity and consolidation; current Relationship sources do not isolate the exact BIO-003 to sleep-duration proposition. Execution: NO_EXACT_PROFILE_BINDING.
- `CUL-088` → `CUL-061` (`REL-CUL-042`): **BLOCKED_MULTIPLE_VERSIONS**. Source class: Distance is a many-to-one summary; equal distance can encode directionally different profile changes. Evidence: Canonical reviews support cultural dynamics generally, not the exact distance-to-entrenchment causal contrast. Execution: NO_EXACT_PROFILE_BINDING.
- `INS-039` → `INS-063` (`REL-INS-017`): **BLOCKED_TARGET_CONTAMINATION**. Source class: Caseload pressure uses staffing capacity, while the target explicitly includes staffing as part of service-delivery capacity. Evidence: Canonical sources support workload/coping theory, but do not identify an independent aggregate effect at these exact endpoints. Execution: NO_EXACT_PROFILE_BINDING.
- `INS-103` → `INS-107` (`REL-INS-036`): **BLOCKED_MULTIPLE_VERSIONS**. Source class: Equal adequacy ratios can arise from more staff, less workload, or different skill/labor-time composition. Evidence: Staffing interventions can have causal effects, but existing evidence does not identify the broad adequacy-ratio effect on territorial reach. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-024` → `SOC-026` (`REL-SOC-017`): **BLOCKED_TARGET_CONTAMINATION**. Source class: Network size and provider availability can share the same alter/provider membership and require exact Network State identity. Evidence: No exact causal contrast separates additional eligible alters from realized support availability. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-041` → `SOC-070` (`REL-SOC-029`): **BLOCKED_DEFINITIONAL_OVERLAP**. Source class: Hierarchy steepness and participation equality can be co-summaries of the same interaction distribution. Evidence: General hierarchy evidence does not identify this exact aggregate-to-aggregate-like participation contrast. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-052` → `SOC-053` (`REL-SOC-031`): **DERIVATION_ONLY**. Source class: Density and clustering are same-state topology summaries; changing one statistic is not a state intervention. Evidence: The route is already a retype candidate and lacks an independent causal mechanism. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-053` → `SOC-061` (`REL-SOC-035`): **BLOCKED_NETWORK_STATE**. Source class: Clustering can be a contextual abstraction only after a topology transformation, exposure route, and contribution identity are exact. Evidence: A randomized network experiment supports effects of topology on adoption, but does not isolate the current scalar clustering-to-reinforcement claim. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-054` → `SOC-057` (`REL-SOC-032`): **DERIVATION_ONLY**. Source class: Assortativity and segregation reuse a mixing structure and baseline; metric-to-metric causality is not identified. Evidence: Canonical causal-inference review warns selection and influence are confounded. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-055` → `SOC-056` (`REL-SOC-033`): **DERIVATION_ONLY**. Source class: Constraint and cross-cluster ties reuse adjacency/partition information. Evidence: No separately identified aggregate mechanism is present. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-056` → `SOC-057` (`REL-SOC-034`): **DERIVATION_ONLY**. Source class: Cross-cluster tie prevalence and segregation are alternate summaries of the same bounded graph/partition. Evidence: No independent temporal causal proposition is supported. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-074` → `SOC-034` (`REL-SOC-046`): **INSUFFICIENT_CAUSAL_EVIDENCE**. Source class: Goal alignment could be a contextual group state, but its versions, episode, and contribution overlap need binding. Evidence: Team-process reviews and goal experiments support plausibility, not the exact aggregate source claim as currently represented. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-076` → `SOC-077` (`REL-SOC-075`): **BLOCKED_DEFINITIONAL_OVERLAP**. Source class: Expectation alignment and collective efficacy may share member expectation/judgment content. Evidence: Current review evidence does not separate measurement overlap from causal effect. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-096` → `SOC-089` (`REL-SOC-060`): **INSUFFICIENT_CAUSAL_EVIDENCE**. Source class: Status inequality could be contextual, but its difference versions and contact mechanism require exact specification. Evidence: Current reviews support hierarchy/threat broadly, not the exact inequality-to-contact-quality effect. Execution: NO_EXACT_PROFILE_BINDING.
- `SOC-096` → `PSY-022` (`REL-SOC-067`): **BLOCKED_EXPOSURE_MAPPING**. Source class: Status inequality is group context; person fairness requires actual contextual exposure semantics. Evidence: No exact contextual causal identification or production mapping exists for this route. Execution: NO_EXACT_PROFILE_BINDING.

## Social ten-source review

- `SOC-024`: `REL-SOC-017` → **BLOCKED_TARGET_CONTAMINATION**
- `SOC-041`: `REL-SOC-029` → **BLOCKED_DEFINITIONAL_OVERLAP**
- `SOC-052`: `REL-SOC-031` → **DERIVATION_ONLY**
- `SOC-053`: `REL-SOC-035` → **BLOCKED_NETWORK_STATE**
- `SOC-054`: `REL-SOC-032` → **DERIVATION_ONLY**
- `SOC-055`: `REL-SOC-033` → **DERIVATION_ONLY**
- `SOC-056`: `REL-SOC-034` → **DERIVATION_ONLY**
- `SOC-074`: `REL-SOC-046` → **INSUFFICIENT_CAUSAL_EVIDENCE**
- `SOC-076`: `REL-SOC-075` → **BLOCKED_DEFINITIONAL_OVERLAP**
- `SOC-096`: `REL-SOC-060` → **INSUFFICIENT_CAUSAL_EVIDENCE**; `REL-SOC-067` → **BLOCKED_EXPOSURE_MAPPING**

Deep external review was bounded to `BIO-003`, `CUL-088`, `INS-039`, `INS-103`, `SOC-053`, and `SOC-074`. Other Social routes received corpus-grounded gap classification. `SOC-096` has two causal Relationships, so the ten sources produce eleven Social causal routes.
