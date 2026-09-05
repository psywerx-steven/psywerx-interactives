# PSYWERX Relationship + Intervention schemas V1

These are the production contracts for the governed V1 infrastructure:

- `governance-v1.schema.json` — orthogonal lifecycle, activation, block,
  decision outcome, authority, and transition provenance;
- `evidence-assessment-v1.schema.json` — normalized scientific evidence;
- `relationship-v1.schema.json` — seven relationship families and their
  predicates, including normalized moderation;
- `causal-pathway-v1.schema.json` — explicit ordered causal pathways;
- `intervention-v1.schema.json` — reusable action identity and packages;
- `intervention-effect-v1.schema.json` — one contextual effect on one exact
  Driver or causal Relationship target; and
- `candidate-workspace-v1.schema.json` — the physically separated,
  non-production-eligible candidate envelope.

JSON Schema validates record shape. Cross-record and governance semantics are
enforced by `scripts/relationship_intervention_v1.py`.

```powershell
py scripts/relationship_intervention_v1.py --validate-repository
py -m unittest discover -s tests -p "test_relationship_intervention_v1.py"
```

The schemas are production-capable but no native V1 scientific record has been
populated or activated. Relationship Schema V3 remains the compatibility source
for the existing corpus.
