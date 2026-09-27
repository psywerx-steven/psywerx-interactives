# Contribution production implementation plan

Phase 0 would install schemas, empty registry, validators, resolver, adapters and receipt/fingerprint contracts with zero groups, migrations, graph changes or simulation changes. Rollback removes this unused architecture.

After Phase 0 validation, Phase 1 would materialize only `CONTRIB-PSY-LAYER-REPETITION-001@1.0.0` in shadow/validation mode. Both source records remain unchanged, selection is explicit, count-once is proven, and no graph, simulation, lifecycle or activation behavior changes. Aggregates are excluded.
