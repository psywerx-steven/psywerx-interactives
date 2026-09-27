# Contribution option comparison

> **READ-ONLY / NON-PRODUCTION PRE-GOVERNANCE DECISION TEST**

Baseline: `24a406468180a35af5beb74df427053cc1536090`. No production mutation or governance decision is made.

| Design | Result | Main strength | Decisive limit |
|---|---|---|---|
| A | Viable but incomplete alone | Cross-class identity | Registry without enforcement remains advisory |
| B | Rejected standalone | Small migration surface | Distributed consumers can omit exclusion; lineage is not identity |
| C | Safe but fragmented | Preserves native controls | Cannot reconcile cross-class duplicates |
| A+B | Viable | Central truth and enforcement | Replacing native policies causes migration |
| A+C | Viable | Compatibility and cross-class identity | Lacks mandatory consumer gate |
| A+B+C | Recommended advisory | Explicit group, native controls, central enforcement | Must prohibit inferred grouping and fail closed |

The bounded hybrid best preserves scientific distinctions and rollback. It adds only explicit cross-class membership; it does not globalize every native contribution field.
