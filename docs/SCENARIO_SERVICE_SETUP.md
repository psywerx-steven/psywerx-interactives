# PSYWERX Scenario Service Setup

The Scenario Service is a small Node.js server that provides the protected API
boundary between the static GitHub Pages Driver Explorer and the OpenAI
Responses API. GitHub Pages remains static; it never receives or stores an API
key.

The implementation follows the official OpenAI
[Responses API](https://developers.openai.com/api/reference/typescript/resources/responses/methods/create)
and [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
conventions: `responses.create`, `text.format` with a strict JSON Schema,
`output_text`, and `store: false`.

## Requirements

- Node.js 20.11 or later
- An OpenAI API key held only by the server environment
- A configured OpenAI model that supports Structured Outputs
- The repository's generated `data/entities.json`, `data/families.json`, and
  `data/plain_language.json` available at their normal paths

The service has one runtime dependency: the official `openai` JavaScript SDK.
It uses Node's built-in HTTP server and test runner; it does not require Express,
a database, browser SDK, or build system.

## Install

From the repository root:

```powershell
Set-Location scenario-service
npm install
Copy-Item .env.example .env
```

`.env.example` intentionally contains variable names only. Put real values in
the ignored `.env` file or, preferably in production, in the deployment
platform's encrypted secret/configuration store.

## Configuration

| Variable | Required | Default when blank | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes | None | Server-only API credential. Never expose it through frontend configuration. |
| `OPENAI_MODEL` | Yes | None | Model used by `responses.create`; deployment-controlled rather than browser-controlled. |
| `HOST` | No | `127.0.0.1` | Listen address. Use the platform-required bind address in production. |
| `PORT` | No | `8787` | Listen port. |
| `ALLOWED_ORIGINS` | Yes | None | Comma-separated exact HTTP(S) origins. Wildcards and origins with paths are rejected. |
| `MAX_REQUEST_BYTES` | No | `32768` | Maximum raw JSON request size. |
| `RATE_LIMIT_WINDOW_MS` | No | `60000` | In-memory rate-limit window. |
| `RATE_LIMIT_MAX_REQUESTS` | No | `10` | Requests allowed per client key in one window. |
| `RATE_LIMIT_MAX_KEYS` | No | `10000` | Maximum in-memory client-key entries. |
| `OPENAI_TIMEOUT_MS` | No | `14000` | Per-attempt OpenAI timeout. |
| `OPENAI_MAX_OUTPUT_TOKENS` | No | `1800` | Maximum generated output tokens. |
| `SERVER_REQUEST_TIMEOUT_MS` | No | `32000` | Maximum time Node allows for receiving a complete HTTP request. Model generation is bounded separately by `OPENAI_TIMEOUT_MS` on each of at most two attempts. |
| `TRUST_PROXY` | No | `false` | Trust the first `X-Forwarded-For` value for rate limiting only behind a correctly configured trusted proxy. |

Local CORS configuration for the repository's usual preview server can be:

```text
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

For GitHub Pages, allow the exact site origin, such as
`https://ACCOUNT.github.io`. An Origin contains the scheme, host, and optional
port—not the repository path.

## Run locally

After filling `.env`:

```powershell
npm run start:env
```

The service listens on `http://127.0.0.1:8787` with the defaults. Verify the
liveness endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8787/health
```

Expected response:

```json
{"status":"ok"}
```

The health endpoint confirms that configuration and public catalogs loaded and
the HTTP process started. It does not make a billable model request.

The current local Driver Explorer configuration targets
`http://localhost:8787/v1/operationalize`. Start the repository's static HTTP
preview separately, then exercise a Driver in scenario mode.

When no secure endpoint is configured, the production Explorer presents the
Scenario action as an intentional disabled coming-soon feature and cannot issue
a request. Scenario form text is stored only in the current tab session; an
explicit operationalization request sends it transiently to this service and
the configured model provider. The form warns users not to enter classified,
controlled, personally identifying, or otherwise sensitive information.

## Tests

Run the unit/integration suite with Node's built-in test runner after installing
packages:

```powershell
npm test
```

The tests cover exact request and response shapes, nullable protected-Driver
editorial fields, catalog snapshot verification, exactly three examples,
clarification rules, private-path rejection, strict Responses API parameters,
one malformed-output retry, no retry on API failure, CORS, request-size limits,
rate limits, and the health endpoint. Tests use a fake Responses client and do
not make billable API calls.

## Deployment boundary

Deploy `scenario-service` on a server or serverless platform that supports a
long-lived Node request up to the configured timeout. The deployment must also
package or mount the three generated public data files at their repository
relative locations. Restart the service after those catalogs change so its
in-memory indexes reflect the new release.

Set the browser's `window.PSYWERX_CONFIG.scenarioApiUrl` to the deployed HTTPS
endpoint and enable the feature only after CORS and service secrets are
configured. CORS is a browser control, not authentication or a complete abuse
control. A public production deployment should also use platform-level request
limits, cost alerts, and an API gateway or equivalent edge protection.

If `TRUST_PROXY=true`, configure it only when the service is reachable solely
through a trusted proxy that replaces, rather than appends untrusted values to,
`X-Forwarded-For`. Otherwise clients can evade the basic in-memory limit.

The included limiter is intentionally basic and process-local. It resets on
restart and does not coordinate across multiple instances. Replace or augment
it with a managed distributed limiter before horizontally scaling the service.

## Privacy and logging

- Scenario inputs and clarification answers are processed transiently.
- The service has no persistence or response cache.
- OpenAI requests set `store: false`.
- Logs contain only request ID, method, route, status, duration, and an error
  code when applicable.
- Logs never contain request bodies, Driver prose, scenario text, model output,
  API keys, stack traces, source provenance, or local paths.
- The model receives one selected Driver and Family, never Relationships or the
  whole ontology.

The public UI should continue warning users not to enter classified,
controlled, personally identifying, or otherwise sensitive information.

## Retry and failure behavior

The official SDK is configured with `maxRetries: 0`. The application performs
at most one retry, and only when a completed model response contains malformed
or contract-invalid structured output. It does not retry API errors, refusals,
incomplete responses, or timeouts. Public errors are concise and omit service
internals.

## Ignored local files

`scenario-service/.gitignore` already protects the service-local secret and
development artifacts. The effective entries are:

```gitignore
node_modules/
.env
.env.*
!.env.example
coverage/
*.log
```

The root `.gitignore` does not need to change. If policy later requires these
patterns to be centralized at the repository root, use their prefixed forms:

```gitignore
scenario-service/node_modules/
scenario-service/.env
scenario-service/.env.*
!scenario-service/.env.example
scenario-service/coverage/
scenario-service/*.log
```

Never commit a populated `.env`, an API key, or raw scenario logs.
