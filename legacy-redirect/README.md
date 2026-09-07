# Legacy `drivers.psywerx.io` redirect handler

This version-controlled handler is intentionally **not deployed** by the repository. It is ready for an HTTPS edge service with a standards-compatible Fetch API (for example, a Cloudflare Worker) after the domain owner chooses and configures that service.

Behavior:

- `drivers.psywerx.io/` → `https://psywerx.io/drivers/`
- every non-root path is copied to `https://psywerx.io` unchanged, including `/drivers/...`, `/cognitive-security/...`, and static assets
- query strings are copied exactly
- status is `308 Permanent Redirect`
- unknown host headers fail closed with `421`

Fragments are never sent in HTTP requests, so no server can copy them explicitly. Standards-compliant browsers normally retain an original fragment when the redirect `Location` does not supply one; validate this in the cutover browser matrix.

Run the local contract tests with `node --test legacy-redirect/test_redirect.mjs`. Do not point public DNS at this handler until its service has the hostname attached, a valid certificate issued, and direct service-origin tests pass.
