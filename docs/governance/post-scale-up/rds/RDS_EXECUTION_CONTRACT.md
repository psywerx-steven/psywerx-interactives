# RDS prototype execution contract

An execution request must explicitly name `rdsId`, `profileId`, `profileVersion`, `bindingId` and `bindingVersion`. `LATEST`, `DEFAULT`, `FIRST`, `MOST_RECENT`, `ACTIVE_PROFILE`, `AUTO_SELECT` and `BEST_MATCH` are rejected. The runtime returns explicit executability states and never interprets missing profile/binding as zero or null.

Definition and input hashes, units, boundaries, metric variant and normalization must match. Provenance records method, context, inputs, output and a deterministic fingerprint. Computability does not imply active status, causal source eligibility, simulation-node eligibility, intervention eligibility or effect-target eligibility. Every prototype profile carries `causalSourceEligible=false` and `WP-PSG-005_REQUIRED`.
