# Layer Scale-Up V2 — escalation prompt

Escalation IDs: `[CANDIDATE_OR_ISSUE_IDS]`

Allowed reason: `[ONTOLOGY | RDS_CAUSAL_SOURCE | ARCHITECTURE | CONFLICTING_HIGH_QUALITY_EVIDENCE | HIGH_CONSEQUENCE_REVIEW_READY | FINAL_SMALL_SET_SKEPTICAL_REVIEW]`

Resolve this bounded question: `[QUESTION]`.

Use only the supplied record definitions, evidence, source findings, counterevidence, and architecture constraints. State competing interpretations, consequence of error, and whether the item is:

- resolved within current contracts;
- `KEEP_RESEARCH_NEEDED`;
- blocked for human ontology/architecture governance; or
- ready for an individual human scientific decision.

Do not change scientific records, ontology, architecture, lifecycle, activation, or source identity. Do not broaden the question or redo the Layer search.
