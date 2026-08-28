# PSYWERX Scenario Operationalization Schema v1.0

**Status:** Governed service contract

**Endpoint:** `POST /v1/operationalize`
**Purpose:** Return a bounded, illustrative operationalization of one canonical
PSYWERX Driver for one user-supplied scenario.

This contract is separate from the canonical Driver, Family, Relationship, and
plain-language schemas. A scenario result is transient analytical support. It
does not amend the ontology, establish that a Driver is present, or establish
that the Driver caused an observed outcome.

## Request envelope

The request is an exact object with no additional properties.

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| `actor` | string | Yes | Trimmed, 1–200 characters. Identifies the actor or population being examined. |
| `behaviorObjective` | string | Yes | Trimmed, 1–400 characters. States the behavior, decision, response, or objective being examined. |
| `context` | string | Yes | Trimmed, 1–800 characters. States the circumstances that bound the scenario. |
| `clarificationAnswer` | string or `null` | Yes | `null` on the initial request; otherwise trimmed, 1–400 characters. |
| `driver` | object | Yes | Exact browser snapshot described below. |

The service does not accept a prompt, system message, instruction, template,
model name, schema, tool choice, or arbitrary additional field from the
browser.

### Driver snapshot

The `driver` object must contain exactly these fields:

| Field | Type |
| --- | --- |
| `id` | canonical Driver ID string |
| `name` | string |
| `definition` | string |
| `plainLanguageExplanation` | string or `null` |
| `analyticQuestion` | string or `null` |
| `whatThisDoesNotMean` | string or `null` |
| `layer` | string |
| `family` | string |
| `familyDefinition` | string or `null` |
| `familyIncludes` | string or `null` |
| `familyExclusions` | string or `null` |
| `mechanism` | string |
| `moderatorsBoundaryConditions` | string |
| `indicators` | array of strings |
| `measurementAssessmentMethods` | string |
| `observability` | string |
| `measurementCaveats` | string |
| `dataType` | string |
| `timeScaleOfChange` | array of strings |
| `onsetCausalLag` | array of strings |
| `commonMisinterpretations` | string |
| `evidenceNotes` | string |

The snapshot is an integrity assertion, not an authority boundary. The service
resolves the ID against its own loaded `data/drivers.json`,
`data/families.json`, and `data/plain_language.json` and requires every supplied
value to match. It then constructs model context from the server-resolved
record. Unknown IDs and stale or modified snapshots are rejected.

A canonical Driver without a public plain-language record remains eligible.
For such a Driver, all three browser-supplied editorial fields and the optional
boundary field must be `null`, and the service uses canonical Driver and Family
context without inventing replacement permanent plain-language content.

## Successful response

The response is an exact object with no additional properties.

| Field | Type | Required | Validation and meaning |
| --- | --- | --- | --- |
| `driverId` | string | Yes | Must equal the requested canonical Driver ID. |
| `scenarioMeaning` | string | Yes | 40–900 characters. Explains the selected Driver's variable in the bounded scenario without asserting presence or causality. |
| `operationalizationExamples` | array | Yes | Exactly three objects using the example schema below. |
| `importantCaveat` | string | Yes | 20–500 characters. States the most important interpretive boundary. |
| `inputSufficiency` | enum | Yes | `SUFFICIENT`, `PARTIALLY_SUFFICIENT`, or `INSUFFICIENT`. |
| `clarificationQuestion` | string or `null` | Yes | Must be `null` for `SUFFICIENT`; otherwise one 8–300 character question ending in `?`. |

### Operationalization example

Every one of the three examples contains exactly:

| Field | Type | Validation and meaning |
| --- | --- | --- |
| `title` | string | 3–100 characters; concise name for the approach. |
| `operationalization` | string | 30–700 characters; a bounded way to define, observe, compare, classify, or investigate the Driver. |
| `whatToLookFor` | array of strings | Two to four observable items; each at most 200 characters. |
| `questionToAsk` | string | 8–300 characters, ending in `?`, with exactly one question mark. |

The service validates the model result after Structured Outputs validation.
This second validation enforces exact keys, length limits, Driver identity,
array sizes, question punctuation, clarification consistency, and exclusion of
private filesystem paths.

## Example successful response

The following hypothetical response demonstrates shape only:

```json
{
  "driverId": "BIO-001",
  "scenarioMeaning": "In this scenario, sleep quantity means the amount of sleep obtained by the stated actor during a defined period relative to physiological need.",
  "operationalizationExamples": [
    {
      "title": "Sleep obtained during the decision period",
      "operationalization": "Define a relevant observation window and compare sleep obtained during that window with the actor's stated physiological sleep need.",
      "whatToLookFor": [
        "Hours slept during the defined window",
        "Estimated sleep need for the same actor and period"
      ],
      "questionToAsk": "How much sleep was obtained during the defined window relative to estimated physiological need?"
    },
    {
      "title": "Repeated sleep-window comparison",
      "operationalization": "Compare sleep obtained with estimated need across several equivalent periods to distinguish a single short interval from a repeated shortfall.",
      "whatToLookFor": [
        "Sleep duration for each equivalent period",
        "Difference between obtained sleep and estimated need",
        "Consistency of the difference across periods"
      ],
      "questionToAsk": "How consistently does obtained sleep differ from estimated need across the selected periods?"
    },
    {
      "title": "Converging sleep measures",
      "operationalization": "Use two suitable measurement approaches for the same period and examine whether they support a similar estimate of sleep quantity relative to need.",
      "whatToLookFor": [
        "Agreement between the selected sleep measures",
        "Measurement gaps or periods not captured",
        "A clearly stated estimate of physiological need"
      ],
      "questionToAsk": "Do the selected measures support a consistent estimate of sleep obtained relative to need?"
    }
  ],
  "importantCaveat": "Sleep duration does not by itself establish sleep quality, impairment, or a causal effect on the behavior being examined.",
  "inputSufficiency": "SUFFICIENT",
  "clarificationQuestion": null
}
```

## Clarification governance

- The service returns no clarification question when inputs are sufficient.
- A partial or insufficient result returns exactly one highest-value
  clarification question.
- The question should request a missing boundary such as a time window,
  comparison baseline, geographic or organizational unit, focal system, or
  measurement unit.
- It must not request sensitive information or broaden the analysis to other
  Drivers.
- A clarification answer is transient input to a new request; it is not stored.
- Editing or clearing the active scenario invalidates any in-flight request, so
  a response produced for an earlier scenario cannot be presented under the
  new scenario state.

## Error responses

Errors use this exact public shape:

```json
{
  "error": "A concise public message.",
  "code": "MACHINE_READABLE_CODE"
}
```

Expected status classes include:

| HTTP status | Meaning |
| --- | --- |
| `400` | Invalid JSON, query string, request shape, or field constraint. |
| `403` | Browser Origin is not allowlisted. |
| `404` | Unknown endpoint. |
| `405` | Unsupported method. |
| `409` | Browser Driver snapshot is stale or does not match governed server data. |
| `413` | Request exceeds the configured byte limit. |
| `415` | Unsupported content type or content encoding. |
| `422` | Unknown Driver or a model refusal that cannot produce a governed result. |
| `429` | In-memory request limit exceeded. |
| `502` | Upstream failure, incomplete response, or invalid structured output. |
| `504` | Upstream generation timeout. |

Errors never include scenario text, model output, secrets, stack traces, source
provenance, or local paths.

## Model boundary

The server sends only the selected canonical Driver, its Family boundary, any
available reviewed plain-language content, and the scenario fields. It does not
send Relationship data, other Drivers, the whole ontology, source provenance,
or local paths. System instructions and the response schema are fixed in
server code. The OpenAI API request uses the Responses API, strict JSON Schema
Structured Outputs, no tools, and `store: false`.
