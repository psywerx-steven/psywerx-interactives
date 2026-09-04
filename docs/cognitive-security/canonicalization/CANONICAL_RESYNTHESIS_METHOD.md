# Cognitive Security Canonical Re-synthesis Method

**Status:** Draft governance specification for analytical review

**Scope:** Deduplicated reconstruction of the Cognitive Security practitioner
discourse map. This specification does not authorize a public-interface or
live-data change.

The canonical re-synthesis corrects the weighting and higher-order structure
of the historical analysis without rerunning transcript extraction. Historical
records remain preserved as provenance. Canonical records are produced through
an explicit selection and adjudication overlay rather than by deleting or
rewriting source records.

## Governed corpus units

The method keeps three corpus concepts separate:

| Unit | Count | Use |
| --- | ---: | --- |
| Historical source identities | 269 | Complete private provenance and reproducibility |
| Public-feed releases | 242 | Public catalog and discoverability |
| Unique recording/content units | 241 | Primary analytical weighting |

The historical analysis contains 14,397 extracted items. Excluding the 27
confirmed alias identities leaves 12,978 items before the content-reuse
adjustment. Item-level lineage confirms that excluding the 45 items attached
to the episode-83 re-release produces 12,933 canonical items: 9,822 focal and
3,111 contextual. This result is enumerated from retained lineage, not assumed
from the target corpus-unit count.

The public release that reuses the episode-83 recording remains a catalog
record. One representation of the shared recording is selected as the
analytical content unit. The other release may inherit public relationships
through `shared-content-inheritance`, but contributes zero additional item or
content-unit weight.

## Canonical selection overlay

The selection layer records, without destroying history:

1. every historical source identity and its public-release relationship;
2. the selected identity or representation for each analytical content unit;
3. confirmed aliases excluded from canonical weighting;
4. the shared-content decision for the episode-83 releases;
5. every retained item and the content unit through which it contributes; and
6. an explicit reason and analytical weight for every inclusion or exclusion.

Only confirmed identity decisions may remove analytical weight. Similar
titles, fuzzy matches, desired totals, or overlapping subject matter are not
sufficient. A public release and an analytical content unit must never be
treated as interchangeable counts.

## Reconstruction sequence

The reconstruction is ordered so that higher-order conclusions cannot be
calculated from duplicate-weighted evidence.

### 1. Select canonical evidence

- Apply the confirmed-alias exclusions.
- Apply the episode-83 shared-content rule.
- Verify 269 retained historical identities, 242 public releases, and 241
  weighted content units.
- Calculate the exact retained-item count.
- Fail if an excluded identity or inherited relationship contributes weight.

### 2. Recompute cluster support

The existing 127 clusters and their substantive definitions remain fixed for
this work package. For each cluster, recompute:

- primary- and secondary-item counts;
- the governed weighted count;
- unique content-unit and public-release coverage;
- focal-category membership;
- concentration and effective content-unit breadth; and
- historical-to-corrected sensitivity.

Review any cluster that loses all support, loses substantial breadth, becomes
dominated by one or two content units, or changes interpretation after
deduplication.

### 3. Adjudicate canonical families

A family is a within-category grouping of clusters with a coherent conceptual
or functional role. Every cluster receives exactly one primary family.
Secondary family relationships are optional and require explicit evidence;
they cannot repair a vague primary family definition.

Each proposed assignment is tested against:

- the cluster definition;
- family inclusion and exclusion rules;
- retained canonical item evidence;
- neighboring families; and
- the cluster's primary functional or conceptual role.

All medium-confidence proposals require item-level review. Semantic similarity
alone is insufficient. Empty families are prohibited, and singleton families
require an explicit finding that the distinction is analytically useful.

### 4. Rebuild themes at one public level

A theme is a recurring pattern spanning multiple families and focal
categories. All public themes appear at the same level. Internal metadata may
describe different analytical roles, but the public model has no core themes,
transversal themes, or subthemes.

Theme adjudication must establish primary and secondary family and cluster
support, category breadth, support concentration, boundary conditions, and
limitations. Key Concepts and Future Trends are legitimate contributors and
must be actively assessed rather than omitted because of historical mapping
gaps. Because `conceptual-framing` and `future-extension` are not primary theme
evidence, they contribute to traceability and total support but not to a
theme's primary-support category-breadth count.

### 5. Allocate and adjudicate tensions

A canonical tension is a recurring tradeoff, competing assumption, dual-use
paradox, prioritization problem, ethical dilemma, or portfolio balance. It must
have evidence for both poles or evidence of a genuine internal contradiction.

Broad historical candidates are allocated at source-candidate and, where
needed, item level before canonical tensions are assembled. The allocation
preserves provenance and historical pole orientation, records any normalized
orientation, and prevents the same evidence from being counted repeatedly
because a historical candidate covered several different questions.

Five ignored, governed adjudication tables make those decisions reproducible.
They (1) map tension evidence attached to excluded alias identities onto a
reviewed retained counterpart, (2) allocate every source-pole occurrence from
the four over-broad historical tensions, (3) resolve every cross-tension item
collision to one positive-weight use, (4) allocate one unit of weight across
repeated lineage within a tension, and (5) independently adjudicate every final
tension construct, its poles, boundary from neighboring tensions, conditions,
limitations, and review state. The builder validates the tables against item,
identity, candidate, pole, and final evidence-summary lineage and fails closed
on missing, stale, or conflicting records. Lexical similarity, keyword scores,
and identifier ordering are not allocation authority.

The design package is a proposal rather than an evidence constraint. An
item-level adjudication may therefore route evidence outside a proposed legacy
target when the surviving proposition supports a different canonical tension;
the departure remains explicit in private lineage. Construct records distinguish
design-proposal ancestry from the historical tensions that retain positive-weight
evidence after allocation. The affected historical pole's
orientation is reversed deterministically when translated to its canonical
tension.

Each final tension states its poles and assumptions, conditions favoring each
pole, any false-dichotomy caveat, evidence balance, limitations, and
adjudication status. A tension describes a discourse conflict; it does not
endorse either pole. Independent review retained 20 constructs because all had
direct evidence for both poles and distinguishable boundaries; the design
package's proposed count was not treated as binding.

### 6. Re-synthesize narratives and category findings

A narrative integrates multiple themes, families, focal categories, and at
least one canonical tension. It also states an unresolved issue and carries
traceable lower-level support. A longer restatement of a single theme is not a
narrative.

Historical category findings are provenance inputs, not a required output
count. Corrected findings are classified as:

- family findings;
- integrative category findings; or
- open questions.

Historical drafting artifacts and generation-process caveats are not carried
into canonical prose.

### 7. Rebuild the scenario portfolio

Scenarios are conditional plausibility exercises, not predictions. Each
scenario is reconstructed from canonical themes, tensions, relevant Future
Trend and Key Concept families, trigger conditions, branch points, pathways,
indicators, counter-signposts, mitigating conditions, implications, response
options, and research questions.

Relationships between scenarios are conditional analytical connections. They
must not be presented as demonstrated causal effects.

## Governed relationship vocabulary

Every relationship has a semantic role and resolvable endpoints. The minimum
vocabulary is:

| Role | Meaning |
| --- | --- |
| `direct-coded-support` | A retained item was directly coded to the cluster. |
| `direct-content-representation` | A public release directly represents the selected analytical content unit. |
| `primary-family-membership` | The cluster's one principal within-category family. |
| `secondary-family-relationship` | An evidence-reviewed, meaningful nonprimary family relationship. |
| `primary-theme-support` | A cluster or family is central to defining the theme. |
| `secondary-theme-support` | A cluster or family supports but does not define the theme. |
| `conceptual-framing` | A Key Concept explains an entity but is not direct evidence for it. |
| `future-extension` | A Future Trend extends a present pattern into a future proposition. |
| `tension-evidence-pole-a` | Evidence illustrates pole A without implying endorsement. |
| `tension-evidence-pole-b` | Evidence illustrates pole B without implying endorsement. |
| `integrates` | A narrative synthesizes the referenced canonical entities. |
| `activated-tension` | A scenario makes a tension consequential or changes its pole balance. |
| `scenario-amplifies` | One scenario may conditionally intensify another. |
| `scenario-mitigates` | One scenario may conditionally reduce another's likelihood or effects. |
| `contextual-connection` | A relevant association that is neither direct evidence nor a causal claim. |
| `shared-content-inheritance` | A release displays relationships from shared content without adding analytical weight. |

More specific scenario qualifiers may be retained as metadata, but they do not
override the governed semantic role or establish causation.

`direct-coded-support` is reserved for direct item-to-cluster coding
provenance. Episode-to-tension provenance uses
`tension-evidence-pole-a` for positive Pole A weight and
`tension-evidence-pole-b` for positive Pole B weight. When an episode carries
positive weight for both poles, both noncausal semantic relationships are
preserved with their respective analytical weights.

## Corpus support profiles

Corpus support is reported as dimensions, not a composite evidence-quality
score. Where applicable, each higher-order entity reports:

- distinct canonical content-unit support;
- public-release coverage;
- retained-item support;
- cluster and family breadth;
- focal-category breadth;
- top-five content-unit share and effective content-unit count;
- direct-versus-derived support;
- pole balance for tensions;
- historical-to-corrected sensitivity;
- adjudication status; and
- entity-specific limitations.

Inherited shared-content relationships affect discoverability but do not
increase item support or content-unit support.

In the public projection, primary support means the governed evidence
designated as primary for the entity; it does not mean that every entity was
directly coded at item level. Clusters trace to directly coded items; families
to member clusters; themes to primary-support families and clusters; tensions
to directly allocated pole evidence; narratives to integrated constructs;
findings to supporting families and clusters; and scenarios to relevant
canonical constructs. The public content-unit breadth field is named
`primaryContentUnitCount`.

Every public interpretation of these measures must preserve this caveat:

> Corpus support reflects recurrence and breadth within this practitioner
> discourse corpus. It does not indicate scientific validity, consensus,
> importance, prevalence, or real-world effect size.

## Privacy and publication boundary

Private analytical artifacts may retain complete lineage needed for
reproducibility and review. Public-safe artifacts use aggregate provenance and
canonical entity relationships.

Public artifacts and documentation must not expose:

- raw transcript text or hashes;
- item text, excerpts, or private item identifiers;
- source filenames, worksheet details, or local paths;
- identity-comparison evidence or internal review notes;
- credentials, secrets, or operational metadata; or
- historical-to-canonical migration tables.

The public product is ultimately canonical-only. Historical records remain
private and reproducible; they are not deleted.

## Determinism and quality gates

Generated artifacts must be byte-stable for identical governed inputs:

- derive identifiers from stable semantic keys;
- use UTF-8 JSON, stable record ordering, stable object-key ordering, and a
  documented newline policy;
- omit generated timestamps and machine-specific paths;
- sort set-like arrays and preserve only semantically meaningful list order;
- reject duplicate primary keys, dangling endpoints, and unrecognized roles;
  and
- run the complete build twice and compare hashes.

The builder's analytical gates verify:

- all corpus-unit counts and the exact corrected-item count;
- zero analytical weight from confirmed aliases and reused content;
- all 127 clusters accounted for exactly once at primary-family level;
- no empty families or orphan clusters;
- evidence review for every medium-confidence family assignment;
- complete governed counterpart coverage for excluded alias tension evidence;
- explicit coverage of every split-tension source-pole occurrence;
- no lexical counterpart selection or keyword-based split routing;
- no duplicate allocation of split-tension evidence;
- cross-level inclusion of Key Concepts and Future Trends;
- traceable support for every retained higher-order entity;
- redundancy review across themes, tensions, narratives, and scenarios;
- no change to current public Explorer behavior.

The checkpoint procedure additionally runs the builder twice and compares all
artifact hashes, scans the proposed tracked diff for private material and
secrets, and runs the complete Cognitive Security regression suite. Those are
release checks around the deterministic builder, not claims made by a single
build invocation.

## Reproducing the private checkpoint

Run the tracked builder from the repository root and supply the governed input
directories explicitly. The arguments are intentionally required so the tool
cannot silently substitute a different private corpus:

```text
python scripts/build_canonical_resynthesis.py --normalized-dir <governed-normalized-directory> --reconciliation-dir <governed-reconciliation-directory> --transcript-summary-dir <governed-transcript-summary-directory> --source-workbook-dir <governed-source-workbook-directory>
```

The default design and output directories are beneath the ignored
`analysis/cognitive-security/canonical-resynthesis/` tree. The builder hashes
its governed inputs before and after execution and hashes the live Explorer
surface before and after execution. It fails if either boundary changes.
It also rejects an output directory outside that private tree or inside its
governed `inputs/` subtree.
The ignored design directory must include the canonical architecture,
cluster-to-family mapping, and working package, plus governed adjudications for
the final family mapping; alias tension counterparts; split-tension allocation;
cross-tension collisions; repeated lineage within one tension; final tension
constructs; theme/narrative lineage; and scenarios. None of those private
working inputs are published or committed by this phase. Before writing, the
builder also asks Git to confirm that the output directory is ignored.

## Human approval checkpoint

The analytical package, reproducibility tooling, public-safe specifications,
review queue, tests, and audit results may be committed and pushed to the
feature branch. The process then stops for human review.

No canonical draft may replace live public data, and no public-interface
implementation may begin, until the analytical checkpoint has been explicitly
frozen.
