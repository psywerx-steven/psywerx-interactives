"""Build the governed Driver/RDS migration baseline v0.3.

The existing XLSX importers first recreate the 793-Driver baseline. This
post-generation step then atomically emits the governed 770 Driver / 41 RDS /
811 entity baseline. The historical filename is retained for compatibility.
Generated JSON is never hand-edited.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HANDOFF = ROOT / "_migration_handoff_v0.3"
SEED = HANDOFF / "migration_manifest_seed.json"
VERSION = "0.3"
BASELINE_COMMIT = "580d59c451765e9f4d65b517f538a495fa93bda5"
BASELINE_COUNTS = {"drivers": 793, "families": 105, "relationships": 439}
TARGET_COUNTS = {
    "drivers": 770,
    "relationalDerivedStates": 41,
    "totalCanonicalEntities": 811,
}
SPECIFICATION_STATUS = "GOVERNED_MIGRATION_SPECIFICATION"
BASELINE_STATUS = "GOVERNED_MIGRATION_BASELINE"
AUTHORITY_DECISION_RECORD = "docs/governance/MIGRATION_BASELINE_ADOPTION_V0_3.md"
EFFECTIVE_COMMIT = "6cf34a029a9dc6e099628e86dfb9f42b53bd8d13"
EFFECTIVE_DATE = "2026-09-05"
OPEN_GOVERNANCE_ITEMS = (
    "INS-102",
    "REL-SOC-028",
    "REL-TEC-049",
    "REL-MIG-CAND-0001",
    "REL-MIG-CAND-0002",
    "REL-MIG-CAND-0003",
    "NEW-ENTITIES-V0.3",
)

ARCHITECTURE_DECISION = "https://app.notion.com/p/3cdf827a3d158103b02efcf83c197519"
RDS_SCHEMA_DECISION = "https://app.notion.com/p/3cdf827a3d1581329f44cb36344c0409"
RELATIONSHIP_SCHEMA_DECISION = "https://app.notion.com/p/3cdf827a3d1581a08906ebe4ab9feded"
ALIAS_STANDARD_DECISION = "https://app.notion.com/p/3cdf827a3d1581ca8fa8ff0fd5520103"
CROSS_FAMILY_DECISION = "https://app.notion.com/p/3cdf827a3d1581e49a9ac152355b1caa"
GAP_DECISION = "https://app.notion.com/p/3cdf827a3d15815897b1fb28cfa20fe5"
TIE_DECISION = "https://app.notion.com/p/3cdf827a3d1581ad9d14fdac9e859818"
SECONDARY_DECISION = "https://app.notion.com/p/3cdf827a3d15819cbba3e6a60464ef38"
POSITIVE_CONTROL_DECISION = "https://app.notion.com/p/3d2f827a3d1581ad8e1cf403ed02198d"

APPROVED_RETYPES = frozenset({
    "INF-010", "INF-011", "INF-014", "INS-024", "BIO-003", "BIO-006",
    "SOC-049", "SOC-050", "SOC-051", "SOC-052", "SOC-053", "SOC-054",
    "SOC-055", "SOC-056", "SOC-057", "INF-053", "INF-068", "SOC-024",
    "SOC-090", "INF-004", "INS-113", "SOC-022", "SOC-018", "SOC-035",
    "SOC-041", "SOC-046", "SOC-047", "SOC-074", "SOC-076", "SOC-096",
    "CUL-088", "PSY-078", "INS-039", "INS-103",
})

POSITIVE_CONTROL_DRIVERS = frozenset({
    "PSY-011", "ENV-050", "ENV-015", "ENV-025", "SOC-043", "SOC-085",
    "TEC-013",
})
REQUIRED_DRIVER_IDS = POSITIVE_CONTROL_DRIVERS | {"SOC-036", "INS-102"}

GOVERNED_HANDOFF_FILES = (
    "CODEX_START_PROMPT.md",
    "GOVERNANCE_SOURCE_INDEX.md",
    "MIGRATION_DECISIONS_SUMMARY.md",
    "RDS_POSITIVE_CONTROL_CALIBRATION.md",
    "README_CODEX_HANDOFF.md",
    "SECONDARY_BOUNDARY_AUDIT_ADDENDUM.md",
    "VALIDATION_CHECKLIST.md",
    "migration_manifest_seed.json",
)

RENAME_MAP = {
    "INF-010": "Decision-Relevant Information Completeness",
    "INF-011": "Information-Set Contradiction",
    "INF-014": "Message–Audience Readability",
    "INS-024": "Administrative Compliance Burden",
    "BIO-003": "Circadian Timing Alignment",
    "BIO-006": "Chronotype–Schedule Fit",
    "INF-053": "Message–Audience Language Accessibility",
    "INF-068": "Material Selective-Omission Degree",
    "SOC-024": "Active Personal Network Size",
    "SOC-090": "Member-Level Cross-Group Friendship Prevalence",
    "INF-004": "Information-Item Prominence",
    "INS-113": "Policy/Rule Implementation Fidelity",
    "SOC-022": "Tie Survival Probability",
    "SOC-018": "Tie Age / Relationship Duration",
    "SOC-035": "Reciprocity Balance",
    "SOC-041": "Status Hierarchy Steepness",
    "SOC-046": "Resource Control Asymmetry",
    "SOC-047": "Dependence Asymmetry",
    "SOC-074": "Goal Alignment",
    "SOC-076": "Mutual Expectation Alignment",
    "SOC-096": "Intergroup Status Inequality",
    "CUL-088": "Generational Cultural Distance",
    "PSY-078": "Perceived Goal–State Discrepancy",
    "INS-039": "Caseload Pressure",
    "INS-103": "Staffing Adequacy",
    "TEC-018": "Interface Task Complexity",
    "BIO-001": "Sleep Duration",
    "BIO-004": "Endogenous Circadian Phase",
    "INF-013": "Message Conceptual Complexity",
    "INF-015": "Claim Uncertainty Disclosure",
    "INF-033": "Methodological & Applicability Limitation Disclosure",
    "INS-028": "Institutional Default Rule",
    "TEC-013": "Interface Default-State Configuration",
}

NEW_DRIVER_SPECS = (
    {
        "id": "INF-077",
        "name": "Message Surface-Linguistic Complexity",
        "layer": "Informational",
        "familyId": "INF-F03",
        "dataType": "Multidimensional",
        "definition": (
            "The degree of objective surface-language complexity in a specified "
            "message arising from vocabulary rarity or specialization, syntactic "
            "depth, morphological complexity, sentence structure, and comparable "
            "linguistic decoding features, independent of the audience’s resulting "
            "comprehension."
        ),
        "representationScale": (
            "Multidimensional profile of lexical frequency or familiarity, "
            "syntactic depth, dependency length, morphological complexity, "
            "sentence structure, and related features."
        ),
        "polarityDirection": (
            "Multidimensional representation; no universal high–low behavioral "
            "interpretation."
        ),
        "measurementCaveats": (
            "Do not substitute one grade-level formula for the full construct. "
            "Keep conceptual complexity, audience-language fit, readability, "
            "comprehension, and cognitive load distinct."
        ),
    },
    {
        "id": "BIO-073",
        "name": "Chronotype",
        "layer": "Biological",
        "familyId": "BIO-F01",
        "dataType": "Bipolar continuous",
        "definition": (
            "A relatively stable individual timing phenotype reflecting "
            "earlier-versus-later propensity or preference for sleep and activity, "
            "shaped by circadian phase, homeostatic sleep processes, age, genetics, "
            "and habitual environmental timing."
        ),
        "representationScale": (
            "Continuous morningness–eveningness score, corrected midsleep timing, "
            "or another validated timing-phenotype measure with instrument and "
            "reference period specified."
        ),
        "polarityDirection": (
            "Earlier and later values indicate timing phenotype; no universal "
            "better/worse polarity."
        ),
        "measurementCaveats": (
            "Not identical to endogenous circadian phase, habitual clock time, "
            "current sleep schedule, or Chronotype–Schedule Fit; instruments may "
            "measure different timing dimensions."
        ),
    },
    {
        "id": "BIO-074",
        "name": "Physiological Sleep Need",
        "layer": "Biological",
        "familyId": "BIO-F01",
        "dataType": "Magnitude / level",
        "definition": (
            "The individual amount and composition of sleep biologically required "
            "over a specified interval to maintain defined physiological or "
            "functional outcomes under stated conditions."
        ),
        "representationScale": (
            "Estimated amount and composition with estimation method, uncertainty, "
            "outcome criterion, and reference period stated."
        ),
        "polarityDirection": (
            "Higher values = greater estimated sleep requirement for the stated "
            "interval and outcome criterion."
        ),
        "measurementCaveats": (
            "Not directly measurable as one universally valid number; may be "
            "outcome-specific and multidimensional. Population recommendations must "
            "not be substituted silently for an individual estimate."
        ),
    },
    {
        "id": "TEC-097",
        "name": "Presented Choice-Set Size",
        "layer": "Technological",
        "familyId": "TEC-F02",
        "dataType": "Count",
        "definition": (
            "The number of selectable alternatives concurrently or immediately "
            "presented to a user within a specified interface decision state."
        ),
        "representationScale": (
            "Count with focal decision state, eligibility or filtering rules, "
            "concurrent versus sequential presentation, and no-choice option stated."
        ),
        "polarityDirection": (
            "Higher values = more selectable alternatives presented in the "
            "specified decision state."
        ),
        "measurementCaveats": (
            "Distinct from total inventory, physically available options, ordering, "
            "defaults, grouping, interaction friction, task complexity, and the "
            "user’s subjective consideration set."
        ),
    },
    {
        "id": "TEC-098",
        "name": "Interface Option Grouping Configuration",
        "layer": "Technological",
        "familyId": "TEC-F02",
        "dataType": "Other structured type",
        "definition": (
            "The configuration by which alternatives in a specified interface "
            "choice set are grouped, partitioned, nested, categorized, paginated, "
            "or staged for presentation."
        ),
        "representationScale": (
            "Partition and grouping structure, nesting depth, initial versus "
            "secondary group, pagination or staging rules, and category-assignment "
            "logic."
        ),
        "polarityDirection": (
            "Structured configuration; no universal high–low interpretation."
        ),
        "measurementCaveats": (
            "Grouping is independent of option count and ordering. Exclude semantic "
            "category quality unless it is represented explicitly."
        ),
    },
    {
        "id": "TEC-099",
        "name": "System-Gated Interaction Delay",
        "layer": "Technological",
        "familyId": "TEC-F03",
        "dataType": "Duration",
        "definition": (
            "Waiting time deliberately imposed by a technological system between "
            "initiation and permitted continuation or completion of a specified "
            "action, excluding delays caused by system performance limitations."
        ),
        "representationScale": (
            "Duration with trigger point, bypass availability, focal action, "
            "repeated versus one-time gate, and fixed versus adaptive rule stated."
        ),
        "polarityDirection": (
            "Higher values = a longer system-imposed wait before the specified "
            "action may continue or complete."
        ),
        "measurementCaveats": (
            "Distinct from network latency, user-action friction, institutional "
            "processing delay, and an informational countdown that does not gate "
            "continuation."
        ),
    },
    {
        "id": "INS-115",
        "name": "Administrative Scheduling Flexibility",
        "layer": "Institutional / Structural",
        "familyId": "INS-F03",
        "dataType": "Magnitude / level",
        "definition": (
            "The degree to which an institutional process permits an actor to "
            "choose, self-initiate, reschedule, or asynchronously complete a "
            "required appointment, interview, or checkpoint within the governing "
            "action window."
        ),
        "representationScale": (
            "Actor-initiated versus assigned scheduling; rescheduling rights; "
            "permissible changes; synchronous or asynchronous completion; available "
            "slots; and schedule-control share."
        ),
        "polarityDirection": (
            "Higher values = greater actor control over scheduling within the "
            "governing action window."
        ),
        "measurementCaveats": (
            "Distinct from response-window duration, permitted communication "
            "channels, institutional processing delay, and technological capability "
            "that institutional rules do not permit."
        ),
    },
    {
        "id": "INS-116",
        "name": "Administrative Recovery Opportunity",
        "layer": "Institutional / Structural",
        "familyId": "INS-F03",
        "dataType": "Other structured type",
        "definition": (
            "The formally permitted opportunity to cure a missed deadline, "
            "incomplete submission, failed checkpoint, or procedural defect before "
            "final denial, lapse, closure, or other adverse disposition."
        ),
        "representationScale": (
            "Availability, cure-period duration, automatic versus requested offer, "
            "attempt count, covered defect types, reopening or reinstatement rule, "
            "and interim status."
        ),
        "polarityDirection": (
            "More extensive values = broader or more usable formally permitted "
            "recovery opportunity."
        ),
        "measurementCaveats": (
            "Distinct from appeal or review rights, the original response window, "
            "and discretionary informal assistance not established as a recognized "
            "opportunity."
        ),
    },
    {
        "id": "SOC-101",
        "name": "Social Tie Formation Rate",
        "layer": "Social",
        "familyId": "SOC-F03",
        "relatedFamilyIds": ["SOC-F07"],
        "dataType": "Rate",
        "definition": (
            "The rate or conditional probability at which new ties of a specified "
            "type form among eligible actor pairs during a specified interval."
        ),
        "representationScale": (
            "New ties per eligible dyad per interval; formation hazard or "
            "probability; or count with an explicit opportunity denominator."
        ),
        "polarityDirection": (
            "Higher values = faster or more likely formation of the specified tie "
            "among eligible dyads."
        ),
        "measurementCaveats": (
            "Requires tie type, eligible dyads, observation interval, and risk set. "
            "Distinct from the number of ties already present and from network "
            "summary metrics."
        ),
    },
    {
        "id": "SOC-102",
        "name": "Triadic Closure Rate",
        "layer": "Social",
        "familyId": "SOC-F07",
        "dataType": "Rate",
        "definition": (
            "The rate or conditional probability that an open triad closes through "
            "formation of a specified tie between two actors who share one or more "
            "common neighbors during a specified interval."
        ),
        "representationScale": (
            "Closed open triads divided by open triads at risk; event hazard; or "
            "model coefficient with its specification retained."
        ),
        "polarityDirection": (
            "Higher values = faster or more likely closure of eligible open triads."
        ),
        "measurementCaveats": (
            "Requires open-triad risk set, tie type, interval, direction convention, "
            "and treatment of multiple shared neighbors. It is not Local Clustering "
            "and is narrower than all tie formation."
        ),
    },
    {
        "id": "SOC-103",
        "name": "Tie Dissolution Rate",
        "layer": "Social",
        "familyId": "SOC-F03",
        "relatedFamilyIds": ["SOC-F07"],
        "dataType": "Rate",
        "definition": (
            "The conditional rate or probability that a specified active social tie "
            "transitions to an inactive or dissolved state per unit time or "
            "observation interval, among ties at risk of dissolution."
        ),
        "representationScale": (
            "Discrete-time dissolution probability per active tie per interval; "
            "continuous-time dissolution hazard per active tie-time; or event count "
            "with explicit at-risk denominator and exposure duration."
        ),
        "polarityDirection": (
            "Higher values = faster or more likely dissolution of active ties under "
            "the stated tie definition and interval."
        ),
        "measurementCaveats": (
            "Specify tie type, active-tie risk set, interval or tie-time, event "
            "definition, censoring, missingness, competing risks, reactivation, "
            "covariates, and network boundary. Do not treat one minus survival as a "
            "universal rate."
        ),
    },
)

NEW_RDS_SPECS = (
    {
        "id": "RDS-0001",
        "name": "Message Cohesion",
        "layer": "Informational",
        "familyId": "INF-F03",
        "entitySubtype": "RELATIONAL_DERIVED_STATE",
        "dataType": "Magnitude / level",
        "definition": (
            "The degree to which explicit lexical, referential, logical, causal, "
            "and discourse links connect propositions or sections within a "
            "specified non-narrative message so that relationships among ideas are "
            "recoverable from the information object."
        ),
        "representationScale": (
            "Multidimensional cohesion profile over a specified message and "
            "relation set."
        ),
        "polarityDirection": (
            "Higher values = stronger recoverable linkage among the specified "
            "message elements."
        ),
        "derivationType": "CLAIM_RELATION",
        "logic": (
            "Compute or assess the governed pattern and strength of lexical, "
            "referential, logical, causal, and discourse relations among the "
            "specified message elements."
        ),
        "constituents": ["MESSAGE_ELEMENTS", "MESSAGE_ELEMENT_RELATIONS"],
        "scope": (
            "Specify message boundary, element segmentation, relation types, "
            "weighting, normalization, missing-link treatment, and update rule."
        ),
    },
    {
        "id": "RDS-0002",
        "name": "Sleep Architecture Composition",
        "layer": "Biological",
        "familyId": "BIO-F01",
        "entitySubtype": "TEMPORAL_PATTERN_STATE",
        "dataType": "Multidimensional",
        "definition": (
            "The composition and organization of sleep across stages and cycles "
            "during a specified sleep episode, including stage proportions, "
            "sequencing, transitions, and cycling structure."
        ),
        "representationScale": (
            "Stage proportions, sequence, transitions, and cycle structure over a "
            "specified sleep episode."
        ),
        "polarityDirection": (
            "Multidimensional temporal composition; no universal high–low "
            "interpretation."
        ),
        "derivationType": "TEMPORAL_PATTERN",
        "logic": (
            "Derive stage proportions, ordering, transitions, and cycle structure "
            "from the time-indexed sleep-stage classification sequence."
        ),
        "constituents": ["SLEEP_STAGE_TIME_SERIES"],
        "scope": (
            "Specify sleep episode boundary, scoring convention, epoch length, "
            "missing epochs, stage categories, and update rule."
        ),
    },
    {
        "id": "RDS-0003",
        "name": "Sleep Sufficiency",
        "layer": "Biological",
        "familyId": "BIO-F01",
        "entitySubtype": "RELATIONAL_DERIVED_STATE",
        "dataType": "Proportion",
        "definition": (
            "The degree to which obtained sleep meets estimated Physiological "
            "Sleep Need over a specified interval and outcome criterion."
        ),
        "representationScale": (
            "Obtained sleep relative to estimated sleep need, with interval, "
            "outcome criterion, estimation method, uncertainty, and included sleep "
            "characteristics stated."
        ),
        "polarityDirection": (
            "Higher values = a greater share of estimated physiological sleep need "
            "met over the specified interval."
        ),
        "derivationType": "RATIO",
        "logic": (
            "Divide obtained sleep by estimated Physiological Sleep Need for the "
            "aligned interval and outcome criterion; state any multidimensional "
            "extension."
        ),
        "constituents": ["BIO-001", "BIO-074"],
        "scope": (
            "Specify interval, outcome criterion, need-estimation method, "
            "uncertainty, and whether duration alone or additional sleep "
            "characteristics are included."
        ),
        "ratio": {"numerator": "BIO-001", "denominator": "BIO-074"},
    },
    {
        "id": "RDS-0004",
        "name": "Cumulative Sleep Deficit",
        "layer": "Biological",
        "familyId": "BIO-F01",
        "entitySubtype": "TEMPORAL_PATTERN_STATE",
        "dataType": "Duration",
        "definition": (
            "The accumulated shortfall between estimated Physiological Sleep Need "
            "and obtained sleep across a specified sequence of intervals under an "
            "explicit accumulation and recovery rule."
        ),
        "representationScale": (
            "Accumulated sleep shortfall with recovery, decay, oversleep-credit, "
            "uncertainty, and reference-window rules stated."
        ),
        "polarityDirection": (
            "Higher values = greater accumulated shortfall under the specified "
            "temporal rule."
        ),
        "derivationType": "TEMPORAL_PATTERN",
        "logic": (
            "For each aligned interval, calculate the shortfall between estimated "
            "need and obtained sleep, then apply the declared accumulation, "
            "recovery, decay, and oversleep-credit rule across the observation "
            "sequence."
        ),
        "constituents": [
            "BIO-001",
            "BIO-074",
            "ACCUMULATION_RECOVERY_RULE",
        ],
        "scope": (
            "Specify interval sequence, reference window, need estimate, recovery "
            "and decay behavior, oversleep credit, missing intervals, and "
            "uncertainty."
        ),
    },
    {
        "id": "RDS-0005",
        "name": "Distance-Based Closeness Centrality",
        "layer": "Social",
        "familyId": "SOC-F07",
        "entitySubtype": "DERIVED_STRUCTURAL_STATE",
        "dataType": "Magnitude / level",
        "definition": (
            "An actor-position score based on the shortest-path distances from a "
            "specified actor to other actors in a specified network, using a named "
            "standard, harmonic, or other governed closeness formulation."
        ),
        "representationScale": (
            "Named standard, harmonic, or other governed closeness formulation."
        ),
        "polarityDirection": (
            "Higher values = greater distance-based closeness under the selected "
            "formulation."
        ),
        "derivationType": "NETWORK_METRIC",
        "logic": (
            "Apply the named closeness formula to shortest-path distances from the "
            "focal actor, including the declared treatment of unreachable nodes and "
            "normalization."
        ),
        "constituents": [
            "NETWORK_CONFIGURATION",
            "FOCAL_ACTOR",
            "PATH_DISTANCE_MATRIX",
        ],
        "scope": (
            "Specify network boundary, tie type, direction, weighting, unreachable-"
            "node treatment, normalization, time window, and selected closeness "
            "variant."
        ),
    },
    {
        "id": "RDS-0006",
        "name": "Network Centralization",
        "layer": "Social",
        "familyId": "SOC-F07",
        "entitySubtype": "DERIVED_STRUCTURAL_STATE",
        "dataType": "Magnitude / level",
        "definition": (
            "The degree to which a specified node-centrality distribution is "
            "concentrated in one or a small number of actors relative to an "
            "explicitly stated benchmark or maximum for that network size and "
            "centrality measure."
        ),
        "representationScale": (
            "Named network-centralization statistic with node-centrality measure "
            "and benchmark stated."
        ),
        "polarityDirection": (
            "Higher values = greater concentration of the selected node-centrality "
            "distribution."
        ),
        "derivationType": "NETWORK_METRIC",
        "logic": (
            "Compare the observed distribution of the selected node-centrality "
            "measure with the stated benchmark or theoretical maximum for the "
            "network size."
        ),
        "constituents": [
            "NODE_CENTRALITY_DISTRIBUTION",
            "NETWORK_BOUNDARY",
            "BENCHMARK_OR_MAXIMUM",
        ],
        "scope": (
            "Specify network boundary, tie type, direction, weighting, time window, "
            "node-centrality measure, normalization, and benchmark."
        ),
    },
    {
        "id": "RDS-0007",
        "name": "Network Component Fragmentation",
        "layer": "Social",
        "familyId": "SOC-F07",
        "entitySubtype": "DERIVED_STRUCTURAL_STATE",
        "dataType": "Magnitude / level",
        "definition": (
            "The degree to which a specified network is divided into disconnected "
            "components or mutually unreachable actor pairs under an explicit "
            "component or fragmentation measure."
        ),
        "representationScale": (
            "Number of components, giant-component share, isolate prevalence, "
            "unreachable-pair proportion, or a named fragmentation index."
        ),
        "polarityDirection": (
            "Higher values = greater fragmentation under the selected measure and "
            "direction convention."
        ),
        "derivationType": "NETWORK_METRIC",
        "logic": (
            "Apply the named component or fragmentation measure to the specified "
            "network configuration and reachability convention."
        ),
        "constituents": [
            "NETWORK_CONFIGURATION",
            "CONNECTED_COMPONENT_STRUCTURE",
        ],
        "scope": (
            "Specify network boundary, tie type, direction, weighting, time window, "
            "reachability convention, and selected fragmentation measure."
        ),
    },
)

RDS_CLASSIFICATION = {
    "BIO-003": ("RELATIONAL_DERIVED_STATE", "ALIGNMENT"),
    "BIO-006": ("RELATIONAL_DERIVED_STATE", "FIT"),
    "INF-004": ("RELATIONAL_STATE", "CONFIGURATION_RELATION"),
    "INF-010": ("RELATIONAL_DERIVED_STATE", "RATIO"),
    "INF-011": ("RELATIONAL_DERIVED_STATE", "CLAIM_RELATION"),
    "INF-014": ("RELATIONAL_STATE", "FIT"),
    "INF-053": ("RELATIONAL_STATE", "FIT"),
    "INF-068": ("RELATIONAL_DERIVED_STATE", "RATIO"),
    "INS-024": ("COMPOSITE_STATE", "AGGREGATE"),
    "INS-039": ("COMPOSITE_STATE", "RATIO"),
    "INS-103": ("RELATIONAL_DERIVED_STATE", "RATIO"),
    "INS-113": ("RELATIONAL_STATE", "FIT"),
    "SOC-018": ("TEMPORAL_PATTERN_STATE", "DIFFERENCE"),
    "SOC-022": ("TEMPORAL_PATTERN_STATE", "TEMPORAL_PATTERN"),
    "SOC-024": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-035": ("RELATIONAL_DERIVED_STATE", "DIFFERENCE"),
    "SOC-041": ("DERIVED_STRUCTURAL_STATE", "DISPERSION"),
    "SOC-046": ("RELATIONAL_STATE", "DIFFERENCE"),
    "SOC-047": ("RELATIONAL_DERIVED_STATE", "DIFFERENCE"),
    "SOC-049": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-050": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-051": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-052": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-053": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-054": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-055": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-056": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-057": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-074": ("RELATIONAL_STATE", "FIT"),
    "SOC-076": ("RELATIONAL_STATE", "FIT"),
    "SOC-090": ("DERIVED_STRUCTURAL_STATE", "NETWORK_METRIC"),
    "SOC-096": ("RELATIONAL_DERIVED_STATE", "DIFFERENCE"),
    "CUL-088": ("RELATIONAL_DERIVED_STATE", "DISTANCE"),
    "PSY-078": ("RELATIONAL_DERIVED_STATE", "DIFFERENCE"),
}

NETWORK_RDS_IDS = frozenset({
    "SOC-024", "SOC-049", "SOC-050", "SOC-051", "SOC-052", "SOC-053",
    "SOC-054", "SOC-055", "SOC-056", "SOC-057", "SOC-090",
})
RATIO_RDS_IDS = frozenset({"INF-010", "INF-068", "INS-039", "INS-103"})
TEMPORAL_RDS_IDS = frozenset({"SOC-018", "SOC-022"})
DIFFERENCE_RDS_IDS = frozenset({
    "SOC-018", "SOC-035", "SOC-046", "SOC-047", "SOC-096", "PSY-078",
})

RDS_DERIVATIONS = {
    "BIO-003": (
        "Compare endogenous circadian phase with the timing of sleep, work, "
        "meals, light exposure, and required behavior under an explicit alignment "
        "convention.",
        ["BIO-004", "EXTERNAL_TIMING_REQUIREMENTS"],
        "Specify internal phase measure, external timing requirements, interval, "
        "alignment convention, and update behavior.",
    ),
    "BIO-006": (
        "Compare the individual Chronotype with the required schedule using the "
        "declared fit or mismatch rule.",
        ["BIO-073", "REQUIRED_SCHEDULE"],
        "Specify chronotype instrument, schedule, reference period, time zone, and "
        "fit convention.",
    ),
    "INF-004": (
        "Compare the focal information item with competing information in the "
        "defined channel and exposure window using the declared prominence "
        "configuration.",
        ["FOCAL_INFORMATION_ITEM", "COMPETING_INFORMATION", "CHANNEL_CONFIGURATION"],
        "Specify channel, competing set, exposure window, perceptual dimensions, "
        "and aggregation rule.",
    ),
    "INF-010": (
        "Calculate coverage of the specified decision-information requirement set, "
        "including weighting and missing-information treatment.",
        ["PRESENT_INFORMATION", "DECISION_INFORMATION_REQUIREMENT_SET"],
        "Specify requirement set, evidence universe, weights, denominator, scope, "
        "and update behavior.",
    ),
    "INF-011": (
        "Evaluate contradiction relations among the specified claims or information "
        "items using an explicit logical or semantic rule.",
        ["CLAIM_SET", "CONTRADICTION_RULE"],
        "Specify claim set, contradiction relation, scope, uncertainty treatment, "
        "and update behavior.",
    ),
    "INF-014": (
        "Evaluate audience-relative decoding and initial-interpretation fit from "
        "surface-linguistic demand, representation, language accessibility, reading "
        "capabilities, and relevant prior knowledge.",
        [
            "INF-077",
            "INF-053",
            "MESSAGE_REPRESENTATION",
            "AUDIENCE_READING_CAPABILITY",
            "AUDIENCE_PRIOR_KNOWLEDGE",
        ],
        "Specify message, audience, channel and layout, reading capability, prior "
        "knowledge, and fit rule.",
    ),
    "INF-053": (
        "Compare message language, translation, vocabulary, register, and syntax "
        "with the intended audience’s usable language proficiency.",
        ["MESSAGE_LANGUAGE_PROFILE", "AUDIENCE_LANGUAGE_PROFICIENCY"],
        "Specify message, intended audience, language dimensions, proficiency "
        "measure, and fit rule.",
    ),
    "INF-068": (
        "Compare materially relevant available information with the information "
        "included in the message, preserving weighting and impression-changing "
        "asymmetry.",
        ["AVAILABLE_MATERIAL_INFORMATION", "PRESENTED_INFORMATION"],
        "Specify evidence or context universe, materiality rule, weighting, message "
        "boundary, denominator, and update behavior.",
    ),
    "INS-024": (
        "Aggregate the specified time, effort, documentation, procedural, and "
        "coordination demands imposed by the administrative process under declared "
        "weights.",
        ["ADMINISTRATIVE_REQUIREMENTS", "TIME_EFFORT_AND_DOCUMENTATION_DEMANDS"],
        "Specify process, actor, components, units, weights, observation window, and "
        "missing-component treatment.",
    ),
    "INS-039": (
        "Relate workload or caseload demand to qualified staffing capacity and "
        "available labor time for the declared service window.",
        ["WORKLOAD_OR_CASELOAD_DEMAND", "STAFFING_CAPACITY", "AVAILABLE_LABOR_TIME"],
        "Specify workload unit, staffing qualification, labor-time denominator, "
        "service window, weighting, and update rule.",
    ),
    "INS-103": (
        "Divide or compare qualified staffing and deployable labor-time capacity "
        "with formally assigned workload for the aligned unit and window.",
        ["QUALIFIED_STAFFING_CAPACITY", "ASSIGNED_WORKLOAD"],
        "Specify staffing qualifications, labor-time capacity, workload unit, time "
        "window, and fit or ratio convention.",
    ),
    "INS-113": (
        "Compare intended policy or rule specifications with realized "
        "implementation across content, process, dosage, timing, coverage, "
        "operating conditions, organizations, places, populations, and time.",
        ["INTENDED_POLICY_OR_RULE_SPECIFICATION", "REALIZED_IMPLEMENTATION"],
        "Specify policy or rule, implementation dimensions, units, responsible "
        "actors, population, place, time window, and fit rule.",
    ),
    "SOC-018": (
        "Subtract the tie-formation or activation timestamp from the observation "
        "timestamp for a tie that satisfies the declared active-state rule.",
        ["TIE_FORMATION_TIMESTAMP", "OBSERVATION_TIMESTAMP", "TIE_STATE_RULE"],
        "Specify tie type, formation event, observation time, active-state rule, "
        "dormancy, reactivation, censoring, and survivor selection.",
    ),
    "SOC-022": (
        "Derive horizon-specific survival probability from the stated Tie "
        "Dissolution Rate or transition process and tie-state model. Do not use a "
        "generic one-minus-rate rule outside aligned discrete binary conditions.",
        ["SOC-103", "BASELINE_ACTIVE_TIE", "PREDICTION_HORIZON", "TIE_STATE_MODEL"],
        "Specify baseline tie state, horizon, tie definition, discrete or continuous "
        "model, censoring, competing states, reactivation, covariates, and "
        "uncertainty.",
    ),
    "SOC-035": (
        "Subtract partner-to-focal resource flow from focal-to-partner resource flow, "
        "or apply the declared signed balance convention, over the aligned interval "
        "and unit.",
        ["FOCAL_TO_PARTNER_RESOURCE_FLOW", "PARTNER_TO_FOCAL_RESOURCE_FLOW"],
        "Specify resource type, common valuation or unit, time window, focal "
        "direction, and sign convention.",
    ),
    "SOC-041": (
        "Apply the named dispersion or steepness statistic to member status scores "
        "within the specified group.",
        ["MEMBER_STATUS_SCORES", "GROUP_BOUNDARY"],
        "Specify group boundary, status measure, dispersion or index formula, "
        "normalization, time window, and uncertainty.",
    ),
    "SOC-046": (
        "Compare directional control of resources needed by each counterpart, "
        "including alternatives, using the declared asymmetry convention.",
        ["A_TO_B_RESOURCE_CONTROL", "B_TO_A_RESOURCE_CONTROL", "ALTERNATIVES"],
        "Specify actors, resource domain, alternatives, valuation, direction, time "
        "window, and difference convention.",
    ),
    "SOC-047": (
        "Subtract one actor’s dependence on the relationship from the other actor’s "
        "dependence using the declared focal-direction sign convention.",
        ["ACTOR_A_DEPENDENCE_ON_B", "ACTOR_B_DEPENDENCE_ON_A"],
        "Specify valued outcomes, alternatives, switching costs, time window, focal "
        "actor, and sign convention.",
    ),
    "SOC-074": (
        "Compare member goal or priority profiles for the specified collective "
        "episode using the declared overlap, agreement, or fit rule.",
        ["MEMBER_GOAL_PROFILES", "COLLECTIVE_EPISODE"],
        "Specify members, episode, goal representation, weights, comparison rule, "
        "and update behavior.",
    ),
    "SOC-076": (
        "Compare actor-specific expectations about one another’s likely actions "
        "using the declared mutual-consistency rule.",
        ["ACTOR_EXPECTATION_PROFILES"],
        "Specify actors, situation, predicted actions, perspective, confidence, "
        "agreement rule, and update behavior.",
    ),
    "SOC-096": (
        "Calculate the magnitude of the status difference between the specified "
        "groups in a common social field using the declared gap or distance rule.",
        ["GROUP_A_STATUS", "GROUP_B_STATUS", "COMMON_SOCIAL_FIELD"],
        "Specify groups, field or domain, status measure, direction, distance rule, "
        "time window, and uncertainty.",
    ),
    "CUL-088": (
        "Calculate the distance between adjacent-generation cultural profiles using "
        "the declared variables, aggregation, and distance metric.",
        ["GENERATION_A_CULTURAL_PROFILE", "GENERATION_B_CULTURAL_PROFILE"],
        "Specify cohorts, cultural domain, profile variables, aggregation, distance "
        "metric, time window, and uncertainty.",
    ),
    "PSY-078": (
        "Subtract perceived current state from the desired or reference state using "
        "the declared sign convention.",
        ["DESIRED_OR_REFERENCE_STATE", "PERCEIVED_CURRENT_STATE"],
        "Specify person, goal domain, reference state, perceived current state, "
        "units, sign convention, and update behavior.",
    ),
}

EXPLICIT_ALIAS_ACTIONS = (
    (
        "INF-077",
        "Readability formula",
        "MEASUREMENT_OR_INDICATOR",
        "Formula is an indicator, not the construct.",
    ),
    (
        "INF-077",
        "Grade level",
        "MEASUREMENT_OR_INDICATOR",
        "Grade level is an indicator, not the construct.",
    ),
    (
        "TEC-097",
        "Choice overload",
        "RELATED_SEARCH",
        "Downstream phenomenon, not an exact alias for the count.",
    ),
    ("TEC-099", "Temporal friction", "RELATED_SEARCH", "Qualified related term."),
    (
        "TEC-099",
        "Cooling-off delay",
        "INTERVENTION_OR_EXPOSURE",
        "Qualified intervention or exposure term.",
    ),
    (
        "INS-116",
        "Grace period",
        "RELATED_SEARCH",
        "Exact fit depends on the represented recovery rule.",
    ),
    (
        "INS-116",
        "Cure period",
        "RELATED_SEARCH",
        "Exact fit depends on the represented recovery rule.",
    ),
    (
        "INS-116",
        "Reopening opportunity",
        "RELATED_SEARCH",
        "Exact fit depends on the represented recovery rule.",
    ),
    (
        "INS-116",
        "Reinstatement opportunity",
        "RELATED_SEARCH",
        "Exact fit depends on the represented recovery rule.",
    ),
    (
        "RDS-0004",
        "Sleep debt",
        "RELATED_SEARCH",
        "Does not imply a conserved or universally linear quantity.",
    ),
    (
        "RDS-0007",
        "Network connectedness",
        "LEGACY_UMBRELLA",
        "Ambiguous graph-theoretic umbrella; not an exact synonym.",
    ),
    (
        "RDS-0005",
        "Closeness",
        "RELATED_SEARCH",
        "Ambiguous with relational closeness unless qualified.",
    ),
    (
        "INS-113",
        "Implementation fidelity",
        "RELATED_SEARCH",
        "Requires a governed operationalization before exact-synonym use.",
    ),
    (
        "INS-113",
        "Adherence",
        "RELATED_SEARCH",
        "Requires a governed operationalization before exact-synonym use.",
    ),
    (
        "INS-113",
        "Dose delivered",
        "MEASUREMENT_OR_INDICATOR",
        "Implementation-fidelity indicator.",
    ),
    (
        "INS-113",
        "Quality of delivery",
        "MEASUREMENT_OR_INDICATOR",
        "Implementation-fidelity indicator.",
    ),
    (
        "SOC-022",
        "Tie persistence probability",
        "EXACT_SYNONYM",
        "Exact when future horizon and tie-state definition are explicit.",
    ),
    (
        "SOC-022",
        "Relationship stability",
        "LEGACY_UMBRELLA",
        "Broader legacy term unless operationalized as survival probability over "
        "a stated horizon.",
    ),
    (
        "SOC-022",
        "Relationship continuity",
        "RELATED_SEARCH",
        "Broader term unless scope is probability over a stated horizon.",
    ),
    (
        "SOC-022",
        "Tie durability",
        "RELATED_SEARCH",
        "Broader term unless scope is probability over a stated horizon.",
    ),
    (
        "SOC-022",
        "Retention rate",
        "MEASUREMENT_OR_INDICATOR",
        "Normally a measurement or indicator term.",
    ),
    (
        "SOC-103",
        "Tie dissolution hazard",
        "RELATED_SEARCH",
        "Requires qualification by risk set, interval, and state definition.",
    ),
    (
        "SOC-103",
        "Tie termination rate",
        "RELATED_SEARCH",
        "Requires qualification by risk set, interval, and state definition.",
    ),
)

DEPRECATED_RELATIONSHIP_IDS = frozenset({
    "REL-INF-023",
    "REL-INF-029",
    "REL-SOC-056",
    "REL-SOC-013",
    "REL-SOC-014",
    "REL-SOC-015",
})
BLOCKED_RELATIONSHIP_IDS = frozenset({"REL-SOC-028", "REL-TEC-049"})


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def baseline_bytes(name: str) -> bytes:
    """Read a frozen baseline artifact from the governed Git commit."""
    try:
        completed = subprocess.run(
            ["git", "show", f"{BASELINE_COMMIT}:data/{name}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"")
        message = detail.decode("utf-8", errors="replace").strip()
        raise ValueError(
            f"Could not read governed baseline artifact data/{name} from "
            f"commit {BASELINE_COMMIT}: {message or exc}"
        ) from exc
    return completed.stdout


def load_baseline_json(name: str) -> Any:
    return json.loads(baseline_bytes(name).decode("utf-8"))


def validate_governance_seed(seed: dict[str, Any]) -> None:
    expected_authority = {
        "status": SPECIFICATION_STATUS,
        "authorityDecisionRecord": AUTHORITY_DECISION_RECORD,
        "effectiveCommit": EFFECTIVE_COMMIT,
        "effectiveDate": EFFECTIVE_DATE,
        "openGovernanceItems": list(OPEN_GOVERNANCE_ITEMS),
    }
    for field, expected in expected_authority.items():
        if seed.get(field) != expected:
            raise ValueError(
                f"The handoff seed changes governed migration authority field {field}"
            )
    decision_path = ROOT / AUTHORITY_DECISION_RECORD
    if not decision_path.is_file():
        raise ValueError(
            f"The migration authority decision record does not resolve: "
            f"{AUTHORITY_DECISION_RECORD}"
        )

    retypes = seed.get("retypes")
    if not isinstance(retypes, list):
        raise ValueError("The handoff seed has no governed retype list")
    retype_ids = [row.get("id") for row in retypes]
    if (
        len(retype_ids) != len(APPROVED_RETYPES)
        or len(set(retype_ids)) != len(retype_ids)
        or set(retype_ids) != APPROVED_RETYPES
    ):
        raise ValueError("The handoff seed does not contain the exact 34-ID retype set")
    for row in retypes:
        identifier = row["id"]
        if row.get("new_entity_type") != "RELATIONAL_DERIVED_STATE":
            raise ValueError(f"The handoff seed changes the governed type for {identifier}")
        expected_name = RENAME_MAP.get(identifier)
        if row.get("new_name") != expected_name:
            raise ValueError(f"The handoff seed changes the governed name for {identifier}")

    expected_new_drivers = {
        (row["name"], row["layer"], row["familyId"])
        for row in NEW_DRIVER_SPECS
    }
    actual_new_drivers = {
        (row.get("name"), row.get("layer"), row.get("family"))
        for row in seed.get("newDrivers", [])
    }
    if (
        len(seed.get("newDrivers", [])) != len(expected_new_drivers)
        or actual_new_drivers != expected_new_drivers
    ):
        raise ValueError("The handoff seed changes the governed new-Driver identities")

    expected_new_rds = {
        (row["name"], row["entitySubtype"])
        for row in NEW_RDS_SPECS
    }
    actual_new_rds = {
        (row.get("name"), row.get("subtype"))
        for row in seed.get("newRDS", [])
    }
    if (
        len(seed.get("newRDS", [])) != len(expected_new_rds)
        or actual_new_rds != expected_new_rds
    ):
        raise ValueError("The handoff seed changes the governed new-RDS identities")

    if (
        seed.get("baseline") != BASELINE_COUNTS
        or seed.get("preview_target") != TARGET_COUNTS
    ):
        raise ValueError("The handoff seed changes governed baseline or target counts")


def normalized_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def family_indexes(
    envelope: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], str]]:
    families = envelope.get("families")
    if envelope.get("schemaVersion") != "1.0" or not isinstance(families, list):
        raise ValueError("Baseline data/families.json must use Family Schema v1.0")
    by_id = {row["id"]: row for row in families}
    by_identity = {(row["layer"], row["name"]): row["id"] for row in families}
    if len(by_id) != len(families) or len(by_identity) != len(families):
        raise ValueError("Baseline Families contain duplicate IDs or identities")
    return by_id, by_identity


def empty_entity_fields() -> dict[str, Any]:
    return {
        "aliases": [],
        "mechanism": None,
        "likelyUpstreamInfluences": [],
        "likelyDownstreamInfluences": [],
        "moderatorsBoundaryConditions": None,
        "typicalInteractionCandidates": [],
        "modifiability": None,
        "volatility": None,
        "timeScaleOfChange": [],
        "timeScaleQualifier": None,
        "onsetCausalLag": [],
        "persistenceRecovery": None,
        "indicators": [],
        "measurementAssessmentMethods": None,
        "observability": None,
        "measurementCaveats": None,
        "evidenceStrength": None,
        "evidenceNotes": None,
        "commonMisinterpretations": None,
        "keySources": [],
    }


def common_entity(
    record: dict[str, Any],
    family_id: str,
    entity_type: str,
    subtype: str | None,
    related_family_ids: list[str] | None = None,
) -> dict[str, Any]:
    old = deepcopy(record)
    result = {
        "id": old.pop("id"),
        "entityType": entity_type,
        "entitySubtype": subtype,
        "name": old.pop("name"),
        "aliases": old.pop("aliases", []),
        "layer": old.pop("layer"),
        "family": old.pop("family"),
        "associatedLayers": [record["layer"]],
        "primaryFamilyId": family_id,
        "relatedFamilyIds": list(related_family_ids or []),
    }
    source = old.pop("source", None)
    result.update(old)
    result["source"] = source
    return result


def governed_new_entity(
    spec: dict[str, Any],
    family: dict[str, Any],
    entity_type: str,
    decision: str,
) -> dict[str, Any]:
    base = empty_entity_fields()
    base.update({
        "id": spec["id"],
        "name": spec["name"],
        "layer": spec["layer"],
        "family": family["name"],
        "definition": spec["definition"],
        "dataType": spec["dataType"],
        "representationScale": spec["representationScale"],
        "polarityDirection": spec["polarityDirection"],
        "measurementCaveats": spec.get("measurementCaveats"),
        "evidenceNotes": None,
        "source": {
            "decisionRecord": decision,
            "specification": "_migration_handoff_v0.3",
            "status": "GOVERNED_PREVIEW",
        },
    })
    result = common_entity(
        base,
        spec["familyId"],
        entity_type,
        spec.get("entitySubtype"),
        spec.get("relatedFamilyIds", []),
    )
    result["metadataStatus"] = "PARTIAL_GOVERNED_PREVIEW"
    result["blockedFields"] = [
        "mechanism",
        "modifiability",
        "volatility",
        "timeScaleOfChange",
        "onsetCausalLag",
        "persistenceRecovery",
        "measurementAssessmentMethods",
        "observability",
        "evidenceStrength",
        "evidenceNotes",
        "keySources",
    ]
    return result


def constituent_specifications(values: list[str]) -> list[dict[str, Any]]:
    canonical_pattern = re.compile(
        r"(?:BIO|SOC|INF|INS|CUL|PSY|TEC|ENV|RDS)-\d{3,4}"
    )
    result = []
    for value in values:
        canonical = bool(canonical_pattern.fullmatch(value))
        result.append({
            "entityId": value if canonical else None,
            "externalParameterType": None if canonical else value,
            "role": "CONSTITUENT_OR_INPUT",
            "required": True,
            "unitScaleExpectations": "Aligned with derivation logic",
            "alignmentRequirements": (
                "Match analytic level, scope, and time window"
            ),
        })
    return result


def rds_metadata(identifier: str, record: dict[str, Any]) -> dict[str, Any]:
    subtype, derivation_type = RDS_CLASSIFICATION[identifier]
    if identifier in NETWORK_RDS_IDS:
        logic = (
            f"Derive {record['name']} from the specified network configuration "
            "using the governed formula or representation: "
            f"{record.get('representationScale')}."
        )
        constituents = [
            "NETWORK_CONFIGURATION",
            "NETWORK_BOUNDARY",
            "TIE_DEFINITION",
        ]
        scope = (
            "Specify network boundary, tie type, direction, weighting, time "
            "window, selected formula, normalization, missing ties, and "
            "uncertainty."
        )
    else:
        logic, constituents, scope = RDS_DERIVATIONS[identifier]
    metadata: dict[str, Any] = {
        "entitySubtype": subtype,
        "constituentSpecifications": constituent_specifications(constituents),
        "derivationType": derivation_type,
        "derivationLogic": logic,
        "scopeRequirements": scope,
        "directManipulability": "VIA_CONSTITUENTS",
        "recalculationBehavior": (
            "Recalculate when a required constituent, reference, boundary, "
            "formula, or analysis window changes."
        ),
        "uncertaintyPropagation": (
            "Preserve and report constituent uncertainty; use analytic "
            "propagation or simulation when the selected operationalization "
            "supports it, otherwise note uncertainty qualitatively."
        ),
    }
    if identifier in NETWORK_RDS_IDS:
        metadata["networkMetricSpecification"] = {
            "networkBoundary": "REQUIRED_AT_ANALYSIS_TIME",
            "tieType": "REQUIRED_AT_ANALYSIS_TIME",
            "directionWeighting": "REQUIRED_AT_ANALYSIS_TIME",
            "timeWindow": "REQUIRED_AT_ANALYSIS_TIME",
            "formula": (
                record.get("representationScale")
                or "NAMED_FORMULA_REQUIRED_AT_ANALYSIS_TIME"
            ),
        }
    if identifier in RATIO_RDS_IDS:
        ratio_map = {
            "INF-010": (
                "represented decision-relevant requirements",
                "specified decision-information requirement set",
            ),
            "INF-068": (
                "materially relevant available information omitted",
                "materially relevant information in the defined evidence or "
                "context universe",
            ),
            "INS-039": (
                "workload or caseload demand",
                "qualified staffing capacity and available labor time",
            ),
            "INS-103": (
                "qualified staffing and deployable labor-time capacity",
                "formally assigned workload",
            ),
        }
        numerator, denominator = ratio_map[identifier]
        metadata["ratioSpecification"] = {
            "numerator": numerator,
            "denominator": denominator,
        }
    if identifier in TEMPORAL_RDS_IDS:
        metadata["temporalSpecification"] = {
            "observationWindow": "REQUIRED_AT_ANALYSIS_TIME",
            "updateRule": logic,
        }
    if identifier in DIFFERENCE_RDS_IDS:
        metadata["differenceSpecification"] = {
            "referenceConvention": scope,
            "signConvention": (
                record.get("polarityDirection")
                or "REQUIRED_AT_ANALYSIS_TIME"
            ),
        }
    if identifier in {"INS-024", "INS-039"}:
        metadata["compositeSpecification"] = {
            "components": constituents,
            "weights": "REQUIRED_AT_ANALYSIS_TIME",
        }
    return metadata


def apply_legacy_alias_rules(
    entities: list[dict[str, Any]],
    original_aliases: dict[str, list[str]],
    original_names: dict[str, str],
) -> dict[str, Any]:
    pending: list[tuple[str, str, str, str]] = []
    for entity in entities:
        identifier = entity["id"]
        for alias in original_aliases.get(identifier, []):
            pending.append((
                identifier,
                alias,
                "RELATED_SEARCH",
                "Migrated from the legacy untyped alias array; exact "
                "equivalence was not inferred.",
            ))
        old_name = original_names.get(identifier)
        if (
            old_name
            and normalized_text(old_name) != normalized_text(entity["name"])
        ):
            pending.append((
                identifier,
                old_name,
                "DEPRECATED_TERM",
                f"Canonical name changed in migration preview v{VERSION}.",
            ))
        entity["aliases"] = []
    pending.extend(EXPLICIT_ALIAS_ACTIONS)

    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for entity_id, alias, alias_type, note in pending:
        key = (normalized_text(alias), alias_type)
        if not key[0]:
            continue
        target = grouped.setdefault(key, {
            "text": alias,
            "normalizedText": key[0],
            "language": "en",
            "aliasType": alias_type,
            "entityIds": [],
            "notes": [],
            "sourceIds": [],
            "publicDisplayRule": (
                "DISPLAY_ON_ENTITY"
                if alias_type in {"EXACT_SYNONYM", "ABBREVIATION"}
                else "SEARCH_ONLY"
            ),
        })
        if entity_id not in target["entityIds"]:
            target["entityIds"].append(entity_id)
        if note not in target["notes"]:
            target["notes"].append(note)

    records = []
    for number, (_, record) in enumerate(sorted(grouped.items()), 1):
        record["entityIds"].sort()
        record["notes"] = " ".join(record["notes"])
        record["sourceIds"] = [ALIAS_STANDARD_DECISION]
        record["aliasId"] = f"ALS-{number:05d}"
        records.append(record)

    exact_by_entity: dict[str, list[str]] = defaultdict(list)
    for record in records:
        if record["aliasType"] in {"EXACT_SYNONYM", "ABBREVIATION"}:
            for entity_id in record["entityIds"]:
                exact_by_entity[entity_id].append(record["text"])
    for entity in entities:
        entity["aliases"] = sorted(
            exact_by_entity[entity["id"]],
            key=normalized_text,
        )
    return {"schemaVersion": "1.0", "aliases": records}


def v3_relationship(
    record: dict[str, Any],
    entities: dict[str, dict[str, Any]],
    status: str = "ACTIVE",
) -> dict[str, Any]:
    subject_id = record["sourceDriverId"]
    object_id = record["targetDriverId"]
    subject = entities[subject_id]
    object_entity = entities[object_id]
    return {
        "id": record["id"],
        "subjectEntityId": subject_id,
        "subjectEntityName": subject["name"],
        "subjectEntityType": subject["entityType"],
        "predicate": record["causalRole"],
        "objectEntityId": object_id,
        "objectRelationshipId": None,
        "objectEntityName": object_entity["name"],
        "objectEntityType": object_entity["entityType"],
        "relationFamily": "CAUSAL",
        "polarity": record["polarity"],
        "directness": record["directness"],
        "mechanism": record["mechanism"],
        "conditionsModerators": record["conditionsModerators"],
        "moderatorEntityIds": list(record["moderatorDriverIds"]),
        "functionalForm": "UNSPECIFIED",
        "functionalFormNotes": None,
        "subjectLevel": record["sourceLevel"],
        "objectLevel": record["targetLevel"],
        "levelTransitionMechanism": record["levelTransitionMechanism"],
        "lagProfile": record["lagProfile"],
        "lagLowerBound": record["lagLowerBound"],
        "lagUpperBound": record["lagUpperBound"],
        "lagUnit": record["lagUnit"],
        "lagNarrative": record["lagNarrative"],
        "exposurePattern": record["exposurePattern"],
        "effectPersistence": record["effectPersistence"],
        "evidenceStrength": record["evidenceStrength"],
        "confidence": record["confidence"],
        "generalizabilityContext": record["generalizabilityContext"],
        "reciprocalProcessId": record["reciprocalProcessId"],
        "governanceClass": record["governanceClass"],
        "governanceStatus": status,
        "supportingEvidenceIds": list(record["supportingEvidenceIds"]),
        "notesCaveats": record["notesCaveats"],
        "source": deepcopy(record["source"]),
        "legacyRelationship": {
            "schemaVersion": "2.0",
            "sourceDriverId": subject_id,
            "sourceDriverName": record["sourceDriverName"],
            "targetDriverId": object_id,
            "targetDriverName": record["targetDriverName"],
            "causalRole": record["causalRole"],
        },
    }


def new_relationship(
    identifier: str,
    subject_id: str,
    predicate: str,
    object_id: str,
    family: str,
    explanation: str,
    conditions: str,
    entities: dict[str, dict[str, Any]],
    *,
    polarity: str | None = None,
    status: str = "ACTIVE",
    source: str = RELATIONSHIP_SCHEMA_DECISION,
) -> dict[str, Any]:
    subject = entities[subject_id]
    object_entity = entities[object_id]
    causal = family == "CAUSAL"
    return {
        "id": identifier,
        "subjectEntityId": subject_id,
        "subjectEntityName": subject["name"],
        "subjectEntityType": subject["entityType"],
        "predicate": predicate,
        "objectEntityId": object_id,
        "objectRelationshipId": None,
        "objectEntityName": object_entity["name"],
        "objectEntityType": object_entity["entityType"],
        "relationFamily": family,
        "polarity": polarity if causal else None,
        "directness": "DIRECT_AT_STATED_RESOLUTION" if causal else None,
        "mechanism": explanation,
        "conditionsModerators": conditions,
        "moderatorEntityIds": [],
        "functionalForm": (
            "UNSPECIFIED"
            if causal
            else "FORMULA_DEFINED"
            if family == "DERIVATIONAL"
            else None
        ),
        "functionalFormNotes": (
            explanation if family == "DERIVATIONAL" else None
        ),
        "subjectLevel": None,
        "objectLevel": None,
        "levelTransitionMechanism": None,
        "lagProfile": ["MIXED_CONTEXT_DEPENDENT"] if causal else [],
        "lagLowerBound": None,
        "lagUpperBound": None,
        "lagUnit": None,
        "lagNarrative": "Context-dependent" if causal else None,
        "exposurePattern": "NOT_SPECIFIED" if causal else None,
        "effectPersistence": None,
        "evidenceStrength": None,
        "confidence": "HIGH",
        "generalizabilityContext": conditions,
        "reciprocalProcessId": None,
        "governanceClass": "CONTEXT_DEPENDENT",
        "governanceStatus": status,
        "supportingEvidenceIds": [],
        "notesCaveats": None,
        "source": {
            "decisionRecord": source,
            "specification": "_migration_handoff_v0.3",
        },
        "legacyRelationship": None,
    }


def build_relationships(
    baseline: dict[str, Any],
    entities: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    baseline_rows = baseline.get("relationships", [])
    if baseline.get("schemaVersion") != "2.0" or len(baseline_rows) != 439:
        raise ValueError(
            "Expected the 439-record Relationship Schema v2 baseline"
        )
    active = []
    deprecated = []
    candidates = []
    original_by_id = {row["id"]: row for row in baseline_rows}
    for row in baseline_rows:
        if row["id"] in DEPRECATED_RELATIONSHIP_IDS:
            migrated = v3_relationship(row, entities, "DEPRECATED")
            migrated["notesCaveats"] = (
                "Deprecated by governed migration v0.3 because the proposition "
                "became derivational, semantic, or materially changed target/"
                "polarity."
            )
            deprecated.append(migrated)
        elif row["id"] in BLOCKED_RELATIONSHIP_IDS:
            migrated = v3_relationship(row, entities, "PROPOSED")
            migrated["reviewStatus"] = "BLOCKED_NEEDS_GOVERNANCE_INPUT"
            migrated["notesCaveats"] = (
                "Excluded from the active graph pending the explicitly required "
                "governed re-research or reassessment."
            )
            candidates.append(migrated)
        else:
            active.append(v3_relationship(row, entities))

    additions = (
        (
            "REL-RDS-0001", "INF-053", "CONSTITUENT_OF", "INF-014",
            "COMPOSITIONAL",
            "Language accessibility is the language-fit component of broader "
            "Message–Audience Readability.",
            "Apply only to the language-fit role within the same message, "
            "audience, and exposure context.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0002", "INF-053", "NARROWER_THAN", "INF-014",
            "SEMANTIC_MAPPING",
            "Message–Audience Language Accessibility has narrower scope than "
            "Message–Audience Readability.",
            "The message and intended audience must be aligned.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0003", "INF-068", "INVERSE_UNDER_ALIGNED_SCOPE",
            "INF-010", "SEMANTIC_MAPPING",
            "Selective omission and completeness may vary inversely only under "
            "aligned evidence-universe and requirement-set definitions.",
            "Require identical evidence universe, requirement set, weighting, "
            "scope, and update window.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0004", "SOC-024", "EQUIVALENT_UNDER_CONDITIONS",
            "SOC-049", "SEMANTIC_MAPPING",
            "Raw degree and active personal-network size may be numerically "
            "equal under a matched egocentric/whole-network operationalization.",
            "Require identical undirected, unweighted active-contact tie "
            "definition, boundary, focal actor, and time window.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0005", "SOC-090", "RELATED_METRIC", "SOC-095",
            "SEMANTIC_MAPPING",
            "Member-level cross-group friendship prevalence and cross-group tie "
            "density share cross-boundary friendship constituents but use "
            "different units and denominators.",
            "State the group boundary, friendship definition, member "
            "denominator, tie-opportunity denominator, and observation window.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0006", "SOC-056", "RELATED_METRIC", "SOC-090",
            "SEMANTIC_MAPPING",
            "Boundary-spanning tie prevalence and member-level cross-group "
            "friendship prevalence share network constituents but use tie-level "
            "versus member-level denominators.",
            "State tie type, boundary, denominator, direction, weighting, and "
            "observation window.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0007", "TEC-019", "REALIZES", "INF-004", "REALIZATION",
            "Interface visual prominence can instantiate Information-Item "
            "Prominence when the focal information is carried by the emphasized "
            "interface element.",
            "Conditional on a matched focal item, interface element, channel, "
            "competing information set, and exposure window.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0008", "TEC-013", "REALIZES", "INS-028", "REALIZATION",
            "An interface default-state configuration can instantiate the "
            "governing institutional default rule.",
            "Only when the interface configuration implements the formal "
            "institutional rule for the same decision and population.",
            None, CROSS_FAMILY_DECISION,
        ),
        (
            "REL-RDS-0010", "SOC-036", "OVERLAPS_WITH", "SOC-022",
            "SEMANTIC_MAPPING",
            "Repeated Interaction Probability overlaps Tie Survival Probability "
            "only when the operational tie definition is recurring interaction.",
            "Require an interaction-defined tie, identical actors, interval, "
            "risk set, and future horizon.",
            None, SECONDARY_DECISION,
        ),
        (
            "REL-RDS-0011", "SOC-022", "DERIVED_FROM", "SOC-103",
            "DERIVATIONAL",
            "Tie Survival Probability is derived from the dissolution hazard or "
            "transition process plus horizon and state-model assumptions.",
            "Specify tie definition, active baseline state, horizon, discrete or "
            "continuous model, censoring, competing risks, and reactivation.",
            None, TIE_DECISION,
        ),
        (
            "REL-RDS-0012", "SOC-022", "INVERSE_UNDER_ALIGNED_SCOPE",
            "SOC-103", "SEMANTIC_MAPPING",
            "Interval-specific survival and dissolution probabilities are "
            "inverses only under aligned discrete binary-state assumptions.",
            "Require identical tie definition, interval, active risk set, "
            "denominator, censoring, competing-state, and reactivation "
            "assumptions; do not apply directly to continuous-time hazards.",
            None, TIE_DECISION,
        ),
        (
            "REL-RDS-0013", "SOC-102", "NARROWER_THAN", "SOC-101",
            "SEMANTIC_MAPPING",
            "Triadic Closure Rate is the subset of tie formation conditional on "
            "eligible open triads.",
            "Require the same tie type, interval, eligible-dyad universe, and "
            "open-triad risk-set definition.",
            None, GAP_DECISION,
        ),
        (
            "REL-RDS-0014", "INF-014", "DERIVED_FROM", "INF-077",
            "DERIVATIONAL",
            "Surface-linguistic complexity is a message-side input to "
            "audience-relative readability.",
            "Align the message, channel, representation, audience, and exposure "
            "window; do not encode a universal inverse.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
        (
            "REL-RDS-0015", "INF-014", "DERIVED_FROM", "INF-053",
            "DERIVATIONAL",
            "Language accessibility is one audience-fit input to broader "
            "readability.",
            "Align the message, intended audience, language profile, "
            "proficiency, channel, and exposure window.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
        (
            "REL-RDS-0016", "BIO-006", "DERIVED_FROM", "BIO-073",
            "DERIVATIONAL",
            "Chronotype is one constituent of Chronotype–Schedule Fit.",
            "Specify chronotype instrument, required schedule, reference period, "
            "time zone, and fit convention.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
        (
            "REL-RDS-0017", "RDS-0003", "DERIVED_FROM", "BIO-001",
            "DERIVATIONAL",
            "Obtained Sleep Duration is the numerator/input for Sleep "
            "Sufficiency.",
            "Align interval, outcome criterion, sleep characteristics, and units "
            "with the sleep-need estimate.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
        (
            "REL-RDS-0018", "RDS-0003", "DERIVED_FROM", "BIO-074",
            "DERIVATIONAL",
            "Physiological Sleep Need is the reference denominator/input for "
            "Sleep Sufficiency.",
            "Align interval, outcome criterion, estimation method, uncertainty, "
            "sleep characteristics, and units.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
        (
            "REL-RDS-0019", "RDS-0004", "DERIVED_FROM", "BIO-001",
            "DERIVATIONAL",
            "Serial Sleep Duration observations supply obtained-sleep values for "
            "Cumulative Sleep Deficit.",
            "Align every interval to the declared need estimate and "
            "accumulation/recovery rule.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
        (
            "REL-RDS-0020", "RDS-0004", "DERIVED_FROM", "BIO-074",
            "DERIVATIONAL",
            "Physiological Sleep Need supplies the reference requirement for "
            "serial sleep shortfalls.",
            "Align the need estimate, intervals, outcome criterion, uncertainty, "
            "recovery, decay, and oversleep-credit rules.",
            None, RELATIONSHIP_SCHEMA_DECISION,
        ),
    )
    for (
        identifier,
        subject,
        predicate,
        object_id,
        family,
        explanation,
        conditions,
        polarity,
        source,
    ) in additions:
        active.append(new_relationship(
            identifier,
            subject,
            predicate,
            object_id,
            family,
            explanation,
            conditions,
            entities,
            polarity=polarity,
            source=source,
        ))

    replacement_specs = (
        (
            "REL-MIG-CAND-0001",
            "REL-SOC-013",
            "SOC-021",
            "SOC-103",
            "NEGATIVE",
            "Tie Multiplexity may reduce Tie Dissolution Rate under "
            "context-dependent longitudinal conditions.",
        ),
        (
            "REL-MIG-CAND-0002",
            "REL-SOC-014",
            "SOC-020",
            "SOC-103",
            "NEGATIVE",
            "Tie Reciprocity may reduce Tie Dissolution Rate under "
            "context-dependent longitudinal conditions.",
        ),
        (
            "REL-MIG-CAND-0003",
            "REL-SOC-015",
            "SOC-023",
            "SOC-103",
            "POSITIVE",
            "Negative Interaction Frequency may increase Tie Dissolution Rate "
            "under context-dependent longitudinal conditions.",
        ),
    )
    replacement_map: dict[str, list[str]] = {
        "REL-INF-023": ["REL-RDS-0001", "REL-RDS-0002"],
        "REL-INF-029": ["REL-RDS-0003"],
        "REL-SOC-056": ["REL-RDS-0005"],
    }
    for (
        identifier,
        old_id,
        subject,
        object_id,
        polarity,
        explanation,
    ) in replacement_specs:
        candidate = new_relationship(
            identifier,
            subject,
            "CAUSES",
            object_id,
            "CAUSAL",
            explanation,
            "Candidate requires longitudinal evidence review, "
            "duration-dependence specification, and confirmation that the "
            "original evidence supports the dissolution-process proposition.",
            entities,
            polarity=polarity,
            status="PROPOSED",
            source=TIE_DECISION,
        )
        candidate["reviewStatus"] = "BLOCKED_NEEDS_GOVERNANCE_INPUT"
        candidate["supportingEvidenceIds"] = list(
            original_by_id[old_id]["supportingEvidenceIds"]
        )
        candidate["legacyRelationship"] = {"replacesRelationshipId": old_id}
        candidates.append(candidate)
        replacement_map[old_id] = [identifier]

    active.sort(key=lambda row: row["id"])
    deprecated.sort(key=lambda row: row["id"])
    candidates.sort(key=lambda row: row["id"])
    return {
        "schemaVersion": "3.0",
        "relationships": active,
        "deprecatedRelationships": deprecated,
        "relationshipCandidates": candidates,
    }, replacement_map


def build_crosswalks(
    original_names: dict[str, str],
    entities: dict[str, dict[str, Any]],
    relationship_replacements: dict[str, list[str]],
) -> dict[str, Any]:
    rows = []
    secondary_ids = {
        "SOC-018", "SOC-035", "SOC-041", "SOC-046", "SOC-047", "SOC-074",
        "SOC-076", "SOC-096", "CUL-088", "PSY-078", "INS-039", "INS-103",
    }
    for identifier in sorted(APPROVED_RETYPES):
        entity = entities[identifier]
        rows.append({
            "resourceType": "ENTITY",
            "legacyId": identifier,
            "successorIds": [identifier],
            "migrationType": "RETYPE",
            "effectiveVersion": VERSION,
            "oldName": original_names[identifier],
            "newName": entity["name"],
            "oldEntityType": "DRIVER",
            "newEntityType": "RELATIONAL_DERIVED_STATE",
            "rationale": (
                "Explicit governed Driver→RDS retype in migration handoff v0.3."
            ),
            "compatibilityBehavior": (
                "Preserve the permanent ID and resolve legacy deep links to the "
                "RDS entity record."
            ),
            "sourceDecisionRecord": (
                SECONDARY_DECISION
                if identifier in secondary_ids
                else ARCHITECTURE_DECISION
            ),
        })
    for identifier in sorted(set(RENAME_MAP) - APPROVED_RETYPES):
        rows.append({
            "resourceType": "ENTITY",
            "legacyId": identifier,
            "successorIds": [identifier],
            "migrationType": "RENAME",
            "effectiveVersion": VERSION,
            "oldName": original_names[identifier],
            "newName": entities[identifier]["name"],
            "oldEntityType": "DRIVER",
            "newEntityType": "DRIVER",
            "rationale": (
                "Explicit governed canonical rename in migration handoff v0.3."
            ),
            "compatibilityBehavior": (
                "Preserve the permanent ID and resolve legacy names through "
                "typed aliases."
            ),
            "sourceDecisionRecord": CROSS_FAMILY_DECISION,
        })
    for legacy_id, successors in sorted(relationship_replacements.items()):
        rows.append({
            "resourceType": "RELATIONSHIP",
            "legacyId": legacy_id,
            "successorIds": successors,
            "migrationType": "REPLACED_BY",
            "effectiveVersion": VERSION,
            "oldName": None,
            "newName": None,
            "oldEntityType": "RELATIONSHIP",
            "newEntityType": "RELATIONSHIP",
            "rationale": (
                "The governed proposition became semantic/derivational or "
                "materially changed target and polarity."
            ),
            "compatibilityBehavior": (
                "Retain the deprecated relationship in provenance and exclude "
                "it from the active graph."
            ),
            "sourceDecisionRecord": (
                TIE_DECISION
                if legacy_id in {
                    "REL-SOC-013",
                    "REL-SOC-014",
                    "REL-SOC-015",
                }
                else CROSS_FAMILY_DECISION
            ),
        })
    for number, row in enumerate(rows, 1):
        row["crosswalkId"] = f"CW-{number:04d}"
    return {"schemaVersion": "1.0", "crosswalks": rows}


def index_entities(
    entities: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in entities}


def migrate_families(
    baseline: dict[str, Any],
    entities: list[dict[str, Any]],
) -> dict[str, Any]:
    result = deepcopy(baseline)
    by_id = index_entities(entities)
    members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        members[entity["primaryFamilyId"]].append(entity)
    for family in result["families"]:
        family_members = members[family["id"]]
        counts = Counter(row["entityType"] for row in family_members)
        family["primaryLayer"] = family["layer"]
        family["memberCountsByType"] = {
            "driverCount": counts["DRIVER"],
            "relationalDerivedStateCount": counts[
                "RELATIONAL_DERIVED_STATE"
            ],
            "totalEntityCount": len(family_members),
        }
        family["driverCount"] = counts["DRIVER"]
        family["relationalDerivedStateCount"] = counts[
            "RELATIONAL_DERIVED_STATE"
        ]
        family["totalEntityCount"] = len(family_members)
        original_representatives = family.get("representativeDriverIds", [])
        family["representativeDriverIds"] = [
            identifier
            for identifier in original_representatives
            if by_id[identifier]["entityType"] == "DRIVER"
        ]
        family["representativeDrivers"] = [
            by_id[identifier]["name"]
            for identifier in family["representativeDriverIds"]
        ]
        entity_representatives = list(original_representatives)
        if not entity_representatives and family_members:
            entity_representatives = [
                sorted(
                    family_members,
                    key=lambda row: (
                        row["entityType"],
                        normalized_text(row["name"]),
                        row["id"],
                    ),
                )[0]["id"]
            ]
        family["representativeEntityIds"] = entity_representatives
    return result


def validate_outputs(
    outputs: dict[str, Any],
    baseline_ids: set[str],
    baseline_relationships: dict[str, Any],
) -> None:
    drivers = outputs["drivers.json"]
    rds = outputs["relational-derived-states.json"]
    union = outputs["entities.json"]
    if (len(drivers), len(rds), len(union)) != (770, 41, 811):
        raise ValueError(
            "Count mismatch: "
            f"Drivers={len(drivers)}, RDS={len(rds)}, entities={len(union)}"
        )
    driver_ids = {row["id"] for row in drivers}
    rds_ids = {row["id"] for row in rds}
    union_ids = {row["id"] for row in union}
    if (
        len(driver_ids) != len(drivers)
        or len(rds_ids) != len(rds)
        or len(union_ids) != len(union)
    ):
        raise ValueError("Entity IDs are not globally unique")
    if driver_ids & rds_ids or driver_ids | rds_ids != union_ids:
        raise ValueError(
            "Driver/RDS canonical partition does not reconcile with entities.json"
        )
    if baseline_ids - APPROVED_RETYPES - driver_ids:
        raise ValueError("An unapproved baseline Driver was removed")
    if (baseline_ids & rds_ids) != APPROVED_RETYPES:
        unexpected = sorted(
            (baseline_ids & rds_ids) ^ APPROVED_RETYPES
        )
        raise ValueError(
            "Driver→RDS set differs from the 34 governed IDs: "
            f"{unexpected}"
        )
    if not REQUIRED_DRIVER_IDS <= driver_ids or REQUIRED_DRIVER_IDS & rds_ids:
        raise ValueError(
            "SOC-036, INS-102, or a positive control does not remain a Driver"
        )

    by_id = index_entities(union)
    for identifier, expected_name in RENAME_MAP.items():
        if by_id[identifier]["name"] != expected_name:
            raise ValueError(f"Governed name mismatch for {identifier}")

    families = outputs["families.json"]["families"]
    counts = Counter(row["primaryFamilyId"] for row in union)
    driver_counts = Counter(row["primaryFamilyId"] for row in drivers)
    rds_counts = Counter(row["primaryFamilyId"] for row in rds)
    if len(families) != 105:
        raise ValueError("Family count changed")
    for family in families:
        identifier = family["id"]
        actual = (
            family["driverCount"],
            family["relationalDerivedStateCount"],
            family["totalEntityCount"],
        )
        expected = (
            driver_counts[identifier],
            rds_counts[identifier],
            counts[identifier],
        )
        if actual != expected:
            raise ValueError(
                f"Family counts do not reconcile for {identifier}"
            )

    for row in rds:
        required = (
            "entitySubtype",
            "constituentSpecifications",
            "derivationType",
            "derivationLogic",
            "scopeRequirements",
            "directManipulability",
            "recalculationBehavior",
            "uncertaintyPropagation",
        )
        for field in required:
            if row.get(field) in (None, "", []):
                raise ValueError(f"RDS {row['id']} is missing {field}")
        if row["derivationType"] == "NETWORK_METRIC":
            network = row.get("networkMetricSpecification", {})
            if any(not network.get(field) for field in (
                "networkBoundary",
                "tieType",
                "directionWeighting",
                "timeWindow",
                "formula",
            )):
                raise ValueError(
                    f"Network RDS {row['id']} lacks boundary/tie/formula metadata"
                )
        if row["derivationType"] == "RATIO":
            ratio = row.get("ratioSpecification", {})
            if not ratio.get("numerator") or not ratio.get("denominator"):
                raise ValueError(
                    f"Ratio RDS {row['id']} lacks numerator/denominator metadata"
                )
        if row["entitySubtype"] == "TEMPORAL_PATTERN_STATE":
            temporal = row.get("temporalSpecification", {})
            if (
                not temporal.get("observationWindow")
                or not temporal.get("updateRule")
            ):
                raise ValueError(
                    f"Temporal RDS {row['id']} lacks window/update metadata"
                )

    aliases = outputs["aliases.json"]["aliases"]
    alias_ids = [row["aliasId"] for row in aliases]
    if len(alias_ids) != len(set(alias_ids)):
        raise ValueError("Alias IDs are not unique")
    for row in aliases:
        if not set(row["entityIds"]) <= union_ids:
            raise ValueError(
                f"Alias {row['aliasId']} has a dangling entity target"
            )
        if (
            row["aliasType"] == "EXACT_SYNONYM"
            and len(row["entityIds"]) != 1
        ):
            raise ValueError(
                f"Exact alias {row['aliasId']} maps ambiguously"
            )

    relationships = outputs["relationships.json"]
    all_relationship_ids = set()
    active_ids = set()
    for bucket in (
        "relationships",
        "deprecatedRelationships",
        "relationshipCandidates",
    ):
        for row in relationships[bucket]:
            if row["id"] in all_relationship_ids:
                raise ValueError(f"Duplicate Relationship ID {row['id']}")
            all_relationship_ids.add(row["id"])
            if bucket == "relationships":
                active_ids.add(row["id"])
            if (
                row["subjectEntityId"] not in union_ids
                or row["objectEntityId"] not in union_ids
            ):
                raise ValueError(
                    f"Relationship {row['id']} has a dangling entity endpoint"
                )
            if row["relationFamily"] != "CAUSAL":
                causal_fields = (
                    "polarity",
                    "lagLowerBound",
                    "lagUpperBound",
                    "lagUnit",
                    "lagNarrative",
                    "exposurePattern",
                    "effectPersistence",
                )
                if any(
                    row.get(field) not in (None, [], "")
                    for field in causal_fields
                ):
                    raise ValueError(
                        f"Noncausal relationship {row['id']} carries causal "
                        "lag/polarity"
                    )

    baseline_relationship_by_id = {
        row["id"]: row for row in baseline_relationships["relationships"]
    }
    expected_active_causal_ids = (
        set(baseline_relationship_by_id)
        - DEPRECATED_RELATIONSHIP_IDS
        - BLOCKED_RELATIONSHIP_IDS
    )
    active_causal = {
        row["id"]: row
        for row in relationships["relationships"]
        if row["relationFamily"] == "CAUSAL"
    }
    if set(active_causal) != expected_active_causal_ids or len(active_causal) != 431:
        raise ValueError(
            "Active causal relationships differ from the 431 governed baseline "
            "propositions"
        )
    for identifier, row in active_causal.items():
        baseline = baseline_relationship_by_id[identifier]
        preserved = (
            row["subjectEntityId"],
            row["objectEntityId"],
            row["predicate"],
            row["polarity"],
            row["directness"],
            row["mechanism"],
            row["conditionsModerators"],
        )
        expected = (
            baseline["sourceDriverId"],
            baseline["targetDriverId"],
            baseline["causalRole"],
            baseline["polarity"],
            baseline["directness"],
            baseline["mechanism"],
            baseline["conditionsModerators"],
        )
        if preserved != expected:
            raise ValueError(
                f"Active causal relationship {identifier} changed proposition identity"
            )

    crosswalk_rows = outputs["crosswalks.json"]["crosswalks"]
    migrated = {
        row["legacyId"]
        for row in crosswalk_rows
        if (
            row["resourceType"] == "ENTITY"
            and row["migrationType"] == "RETYPE"
        )
    }
    if migrated != APPROVED_RETYPES:
        raise ValueError(
            "Every governed retype must have exactly one entity crosswalk"
        )
    for row in crosswalk_rows:
        if (
            row["resourceType"] == "ENTITY"
            and not set(row["successorIds"]) <= union_ids
        ):
            raise ValueError(
                f"Crosswalk {row['crosswalkId']} has a dangling entity successor"
            )
        if (
            row["resourceType"] == "RELATIONSHIP"
            and not set(row["successorIds"]) <= all_relationship_ids
        ):
            raise ValueError(
                f"Crosswalk {row['crosswalkId']} has a dangling relationship "
                "successor"
            )
    if (
        DEPRECATED_RELATIONSHIP_IDS & active_ids
        or BLOCKED_RELATIONSHIP_IDS & active_ids
    ):
        raise ValueError(
            "A governed deprecated or blocked relationship remains active"
        )


def main() -> int:
    try:
        seed = load_json(SEED)
        validate_governance_seed(seed)

        baseline_drivers = load_baseline_json("drivers.json")
        baseline_families = load_baseline_json("families.json")
        baseline_relationships = load_baseline_json("relationships.json")
        if (
            not isinstance(baseline_drivers, list)
            or len(baseline_drivers) != BASELINE_COUNTS["drivers"]
        ):
            raise ValueError(
                f"Governed baseline commit {BASELINE_COMMIT} must contain "
                "exactly 793 Drivers"
            )
        original_by_id = {row["id"]: row for row in baseline_drivers}
        if (
            len(original_by_id) != len(baseline_drivers)
            or not APPROVED_RETYPES <= original_by_id.keys()
        ):
            raise ValueError(
                "Baseline Driver identities do not match the governed migration"
            )

        family_by_id, family_by_identity = family_indexes(
            baseline_families
        )
        baseline_hashes = {
            name: sha256_bytes(baseline_bytes(name))
            for name in (
                "drivers.json",
                "families.json",
                "relationships.json",
                "plain_language.json",
                "codebook.json",
                "sources.json",
            )
        }
        original_aliases = {
            identifier: list(row.get("aliases", []))
            for identifier, row in original_by_id.items()
        }
        original_names = {
            identifier: row["name"]
            for identifier, row in original_by_id.items()
        }

        drivers = []
        rds = []
        for identifier, source_record in original_by_id.items():
            record = deepcopy(source_record)
            record["name"] = RENAME_MAP.get(identifier, record["name"])
            family_id = family_by_identity[(
                record["layer"],
                record["family"],
            )]
            if identifier in APPROVED_RETYPES:
                subtype, _ = RDS_CLASSIFICATION[identifier]
                migrated = common_entity(
                    record,
                    family_id,
                    "RELATIONAL_DERIVED_STATE",
                    subtype,
                )
                migrated.update(rds_metadata(identifier, migrated))
                rds.append(migrated)
            else:
                drivers.append(common_entity(
                    record,
                    family_id,
                    "DRIVER",
                    None,
                ))

        for spec in NEW_DRIVER_SPECS:
            drivers.append(governed_new_entity(
                spec,
                family_by_id[spec["familyId"]],
                "DRIVER",
                TIE_DECISION if spec["id"] == "SOC-103" else GAP_DECISION,
            ))
        for spec in NEW_RDS_SPECS:
            entity = governed_new_entity(
                spec,
                family_by_id[spec["familyId"]],
                "RELATIONAL_DERIVED_STATE",
                GAP_DECISION,
            )
            entity.update({
                "constituentSpecifications": constituent_specifications(
                    spec["constituents"]
                ),
                "derivationType": spec["derivationType"],
                "derivationLogic": spec["logic"],
                "scopeRequirements": spec["scope"],
                "directManipulability": "VIA_CONSTITUENTS",
                "recalculationBehavior": (
                    "Recalculate when a required constituent, reference, "
                    "boundary, formula, or analysis window changes."
                ),
                "uncertaintyPropagation": (
                    "Preserve and report constituent uncertainty; propagate "
                    "analytically or by simulation when supported, otherwise "
                    "note it qualitatively."
                ),
            })
            if spec["derivationType"] == "NETWORK_METRIC":
                entity["networkMetricSpecification"] = {
                    "networkBoundary": "REQUIRED_AT_ANALYSIS_TIME",
                    "tieType": "REQUIRED_AT_ANALYSIS_TIME",
                    "directionWeighting": "REQUIRED_AT_ANALYSIS_TIME",
                    "timeWindow": "REQUIRED_AT_ANALYSIS_TIME",
                    "formula": spec["logic"],
                }
            if "ratio" in spec:
                entity["ratioSpecification"] = spec["ratio"]
            if spec["entitySubtype"] == "TEMPORAL_PATTERN_STATE":
                entity["temporalSpecification"] = {
                    "observationWindow": "REQUIRED_AT_ANALYSIS_TIME",
                    "updateRule": spec["logic"],
                }
            rds.append(entity)

        layer_order = [
            "Biological",
            "Psychological",
            "Social",
            "Cultural",
            "Physical / Environmental",
            "Institutional / Structural",
            "Informational",
            "Technological",
        ]

        def sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
            return (
                layer_order.index(row["layer"]),
                normalized_text(row["name"]),
                row["id"],
            )

        drivers.sort(key=sort_key)
        rds.sort(key=sort_key)
        entities = sorted(drivers + rds, key=sort_key)
        alias_output = apply_legacy_alias_rules(
            entities,
            original_aliases,
            original_names,
        )
        by_id = index_entities(entities)
        relationship_output, replacement_map = build_relationships(
            baseline_relationships,
            by_id,
        )
        family_output = migrate_families(
            baseline_families,
            entities,
        )
        crosswalk_output = build_crosswalks(
            original_names,
            by_id,
            replacement_map,
        )

        blocked_items = [
            {
                "itemType": "ENTITY",
                "itemId": "INS-102",
                "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT",
                "issue": (
                    "Fiscal Capacity remains in the governed lower-priority "
                    "boundary queue and is unchanged as a Driver."
                ),
                "sourceDecisionRecord": SECONDARY_DECISION,
            },
            {
                "itemType": "RELATIONSHIP",
                "itemId": "REL-SOC-028",
                "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT",
                "issue": (
                    "Resource Control Asymmetry → Dependence Asymmetry requires "
                    "re-research to distinguish causal constituent changes from "
                    "shortcut double counting."
                ),
                "sourceDecisionRecord": SECONDARY_DECISION,
            },
            {
                "itemType": "RELATIONSHIP",
                "itemId": "REL-TEC-049",
                "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT",
                "issue": (
                    "Algorithmic Ranking Weight → Information-Item Prominence "
                    "requires reassessment as realization/placement logic after "
                    "retype."
                ),
                "sourceDecisionRecord": CROSS_FAMILY_DECISION,
            },
            *[
                {
                    "itemType": "RELATIONSHIP_CANDIDATE",
                    "itemId": identifier,
                    "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT",
                    "issue": (
                        "Replacement dissolution-process proposition requires "
                        "governed longitudinal evidence review before activation."
                    ),
                    "sourceDecisionRecord": TIE_DECISION,
                }
                for identifier in (
                    "REL-MIG-CAND-0001",
                    "REL-MIG-CAND-0002",
                    "REL-MIG-CAND-0003",
                )
            ],
            {
                "itemType": "SCIENTIFIC_METADATA",
                "itemId": "NEW-ENTITIES-V0.3",
                "status": "BLOCKED_NEEDS_GOVERNANCE_INPUT",
                "issue": (
                    "The 18 admitted new entities have governed identities, "
                    "definitions, representations, boundaries, and RDS "
                    "derivations, but the handoff does not supply complete "
                    "mechanism, temporal, observability, evidence-strength, or "
                    "source-register fields. Those fields remain null/empty and "
                    "are listed per record instead of being invented."
                ),
                "sourceDecisionRecord": GAP_DECISION,
            },
        ]
        blocked_item_ids = tuple(item["itemId"] for item in blocked_items)
        if blocked_item_ids != OPEN_GOVERNANCE_ITEMS:
            raise ValueError(
                "Generated blocked items differ from the adopted open governance items"
            )

        outputs: dict[str, Any] = {
            "drivers.json": drivers,
            "relational-derived-states.json": rds,
            "entities.json": entities,
            "families.json": family_output,
            "relationships.json": relationship_output,
            "aliases.json": alias_output,
            "crosswalks.json": crosswalk_output,
        }
        manifest = {
            "schemaVersion": "1.0",
            "migrationVersion": VERSION,
            "status": BASELINE_STATUS,
            "specification": "_migration_handoff_v0.3",
            "specificationStatus": SPECIFICATION_STATUS,
            "authorityDecisionRecord": AUTHORITY_DECISION_RECORD,
            "effectiveCommit": EFFECTIVE_COMMIT,
            "effectiveDate": EFFECTIVE_DATE,
            "openGovernanceItems": list(OPEN_GOVERNANCE_ITEMS),
            "baselineGitCommit": BASELINE_COMMIT,
            "baselineCounts": BASELINE_COUNTS,
            "baselineArtifactSha256": baseline_hashes,
            "governedInputSha256": {
                f"_migration_handoff_v0.3/{name}": sha256_file(HANDOFF / name)
                for name in GOVERNED_HANDOFF_FILES
            },
            "migrationImplementation": {
                "path": "scripts/build_migration_preview_v0_3.py",
                "sha256": sha256_file(Path(__file__)),
            },
            "previewCounts": TARGET_COUNTS,
            "idAssignments": {
                "newDrivers": [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "familyId": row["familyId"],
                    }
                    for row in NEW_DRIVER_SPECS
                ],
                "newRelationalDerivedStates": [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "familyId": row["familyId"],
                    }
                    for row in NEW_RDS_SPECS
                ],
            },
            "retypedEntityIds": sorted(APPROVED_RETYPES),
            "keptDriverIds": sorted(REQUIRED_DRIVER_IDS),
            "renames": [
                {
                    "id": identifier,
                    "oldName": original_names[identifier],
                    "newName": new_name,
                }
                for identifier, new_name in sorted(RENAME_MAP.items())
                if original_names[identifier] != new_name
            ],
            "relationshipActions": {
                "active": len(relationship_output["relationships"]),
                "deprecated": len(
                    relationship_output["deprecatedRelationships"]
                ),
                "proposedOrBlocked": len(
                    relationship_output["relationshipCandidates"]
                ),
            },
            "blockedItems": blocked_items,
            "governanceDecisionRecords": [
                AUTHORITY_DECISION_RECORD,
                ARCHITECTURE_DECISION,
                RDS_SCHEMA_DECISION,
                RELATIONSHIP_SCHEMA_DECISION,
                ALIAS_STANDARD_DECISION,
                CROSS_FAMILY_DECISION,
                GAP_DECISION,
                TIE_DECISION,
                SECONDARY_DECISION,
                POSITIVE_CONTROL_DECISION,
            ],
        }
        outputs["migration-manifest.json"] = manifest
        validate_outputs(
            outputs,
            set(original_by_id),
            baseline_relationships,
        )

        payloads = {
            name: json_bytes(value)
            for name, value in outputs.items()
        }
        manifest["generatedArtifactSha256"] = {
            name: sha256_bytes(content)
            for name, content in sorted(payloads.items())
            if name != "migration-manifest.json"
        }
        payloads["migration-manifest.json"] = json_bytes(manifest)

        with tempfile.TemporaryDirectory(
            prefix="psywerx-migration-v0.3-",
            dir=DATA,
        ) as temp_name:
            temp = Path(temp_name)
            for name, content in payloads.items():
                (temp / name).write_bytes(content)
            for name in payloads:
                (temp / name).replace(DATA / name)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print("Governed migration baseline v0.3 built and validated")
    print("  Drivers: 770")
    print("  Relational & Derived States: 41")
    print("  Canonical entities: 811")
    print(
        "  Active relationships: "
        f"{len(relationship_output['relationships'])}"
    )
    print(
        "  Deprecated relationships: "
        f"{len(relationship_output['deprecatedRelationships'])}"
    )
    print(
        "  Proposed/blocked relationships: "
        f"{len(relationship_output['relationshipCandidates'])}"
    )
    print(f"  Blocked governance items: {len(blocked_items)}")
    print("  Errors: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
