# RDS Positive-Control & Boundary Calibration Addendum

## Purpose
Prevent over-retyping during the non-authoritative migration preview. A construct is **not** an RDS merely because it is represented by a ratio, score, average, aggregate, proportion, distribution, or index.

## Positive-control Drivers
These existing entities should remain Drivers unless a later governed adjudication explicitly changes them:

- `PSY-011 Self-Efficacy`
- `ENV-050 Relative Humidity`
- `ENV-015 Traffic Speed`
- `ENV-025 Spatial Enclosure`
- `SOC-043 Reputation Valence`
- `SOC-085 Action Publicness`
- `TEC-013 Interface Default-State Configuration`

## Governing rule
Retain Driver status when the computation is primarily a measurement/operationalization of a substantively meaningful latent, emergent, physical, social, or directly configurable state, or when the referenced audience/population/time/segment is merely a scope parameter.

Retype to RDS only when the canonical meaning is transparently reducible to explicitly represented or specified constituents and retaining both the constituents and result as peer Drivers would plausibly create semantic or causal double counting.

## Automated/Codex anti-overreach test
Before proposing any additional automatic retype, require all five:
1. Explicitly identify constituent states.
2. Confirm constituents exist or are intentionally specified at the relevant analytic level.
3. State the transparent derivation rule, denominator/reference, and update behavior.
4. Demonstrate the candidate contains no independent latent/emergent information beyond those constituents.
5. Demonstrate plausible semantic/causal double counting if candidate and constituents both remain Drivers.

If any condition is unresolved, do not retype automatically. Use:

`BLOCKED_NEEDS_GOVERNANCE_INPUT`

## Distinctions
- Measurement aggregation → `MEASURES` / `INDICATES`; underlying state can remain a Driver.
- Ontological derivation → `DERIVED_FROM`; candidate may belong in RDS.
- Scope parameter → defines where/for whom a state is measured; not automatically a constituent.
- Direct configuration → can remain Driver; lower-level implementation may `REALIZE` it.
- Emergent aggregate → may remain Driver if not transparently reducible to represented constituent entities.
- Transparent composite → usually RDS / `COMPOSITE_STATE`.

## Deferred nonblocking examples
- `INS-102 Fiscal Capacity` — future dedicated audit.
- `ENV-016 Road Congestion Level` — future Mobility-family review.
- `ENV-013 Parking Availability and Proximity` — likely compound/split review.

## Count impact
No change:
- 770 Drivers
- 41 RDS
- 811 total canonical entities
