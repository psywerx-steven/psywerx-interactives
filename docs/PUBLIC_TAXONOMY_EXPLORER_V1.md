# PSYWERX Public Taxonomy Explorer v1

## Purpose

The public PSYWERX Driver Explorer is a taxonomy knowledge product organized as
`Layer → Family → Driver`. It supports governed browsing, filtering, canonical
definitions, reviewed explanations, observation guidance, evidence context,
and source links. It is not currently a causal-network product.

## Canonical naming rule

The visible name of every Driver is the canonical `name` from
`data/drivers.json`. This applies to cards, search results, Family lists,
breadcrumbs, detail titles, document titles, and deep links.

`plainLanguageLabel` remains an editorial retrieval synonym. It may improve a
search match, but it is never rendered in place of the canonical ontology node
name.

## Public information architecture

### Family view

The public Family view contains the canonical Family name and definition,
Driver count, and all canonical Drivers assigned to the Family. Inclusion
rules, exclusion/boundary rules, and representative Drivers remain governed
data but are not public presentation fields.

### Driver view

Every Driver opens with clickable Layer and Family breadcrumbs, its permanent
Driver ID, and canonical name. Nonempty aliases may appear beneath the name.
The public sections are:

1. Definition — the unchanged canonical scientific definition.
2. In brief — the approved explanation, or a neutral notice that an additional
   explanatory description is not yet available.
3. Question to investigate — the approved analytic question when available.
4. How it operates — governed Mechanism content and exact structured dynamics.
5. Context and conditions — governed moderators and boundary conditions.
6. How to observe it — indicators, assessment approaches, observability, and
   measurement considerations.
7. Evidence — Driver-level Evidence Strength and Evidence Notes.
8. Key sources — governed citations with direct or labeled search links.
9. Applied to this scenario — a separate, user-triggered illustrative layer
   when a scenario is active.

The following remain in canonical/backend data but are not shown in normal
public Driver detail: Representation / Scale; provenance/workbook metadata;
duplicate identity fields; Common Misinterpretations as a raw column; Likely
Upstream Influences; Likely Downstream Influences; Typical Interaction
Candidates; and relationship graph/path output.

## Search and filtering

Search prioritizes canonical name, aliases, canonical definition, approved
explanation, analytic question, Family, Layer, and finally the hidden
plain-language label synonym.

Public facets are Layer, Family, Data Type, Modifiability, Volatility, Time
Scale, Observability, and Evidence Strength. Values are ORed within a facet and
facets are ANDed across the query. Family choices adapt to active Layers.

Time Scale uses Codebook ordering. Multi-band values are indexed as individual
canonical bands, so a Driver matches when any selected band occurs in
`timeScaleOfChange`.

## Codebook help

Technical concepts use a reusable accessible information button backed by
`data/codebook.json`. The nonmodal explanation links to the permanent Codebook
entry. It works by click/tap and keyboard activation; Escape closes it and
restores focus. Definitions and IDs remain owned by the Codebook dataset.

## Source links

`scripts/build_sources.py` produces `data/sources.json` from the governed
Evidence Library worksheets. Resolution uses explicit DOI, explicit stable
URL, explicit safe scholarly identifier, then a labeled scholarly-search
fallback. The application never invents a DOI or source URL. External links
use `target="_blank"` with `rel="noopener noreferrer"`.

## Causal-feature policy

Causal relationship features are intentionally disabled in the public taxonomy
release pending systematic graph-completeness review. Normal startup does not
fetch `data/relationships.json`, and no graph, path, edge, upstream, or
downstream UI is presented.

The Relationship dataset, schemas, builders, research artifacts, and
`drivers/causal.js` remain preserved. `drivers/config.js` keeps the public
boundary explicitly disabled.

## Deployment boundary

The Explorer remains a dependency-free static GitHub Pages application.
Scenario operationalization is a separate optional service and is disabled on
the production static configuration until a secure endpoint is deployed. The
same public control presents an intentional coming-soon state while disabled;
enabling `scenarioAiEnabled` with a secure endpoint activates the existing
Scenario experience without a UI redesign. The browser never contains an AI
API secret.
