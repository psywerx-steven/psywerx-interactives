# Network State operation taxonomy

**READ-ONLY INVENTORY — PRODUCTION SCHEMAS UNCHANGED**

| Operation | State meaning | Does not establish |
|---|---|---|
| ADD_NODE | add a stipulated node, optionally to boundary | empirical entry mechanism |
| DEACTIVATE_NODE | deactivate node; remove boundary membership, incident ties/opportunities | real-world intervention effectiveness |
| ADD_TIE / REMOVE_TIE | stipulate adjacency | observed tie formation/dissolution |
| UPDATE_TIE_WEIGHT | stipulate an explicit weight meaning/unit | observed measurement |
| CHANGE_MEMBERSHIP | change group membership metadata | node existence, boundary inclusion, tie, exposure |
| CHANGE_BOUNDARY | change analytic selection only; must occur alone | physical network change |
| CHANGE_CONTACT_OPPORTUNITY | change potential opportunity | realized tie or encounter |
| CHANGE_ACCESS | enable/disable an opportunity | receipt, contact or exposure |

Operation order is explicit. IDs are immutable; removed tie IDs are retired. No operation advances an implicit clock or produces evidence, causal contribution, ontology edits, or EffectAssertions.
