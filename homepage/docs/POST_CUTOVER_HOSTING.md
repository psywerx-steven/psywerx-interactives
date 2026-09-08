# PSYWERX production hosting after the 2026-09-07 cutover

PSYWERX is hosted directly on GitHub Pages at the apex custom domain `psywerx.io`.

Canonical public routes:

- `https://psywerx.io/`
- `https://psywerx.io/drivers/`
- `https://psywerx.io/drivers/codebook/`
- `https://psywerx.io/cognitive-security/`

`www.psywerx.io` is a DNS CNAME to `psywerx-steven.github.io` and GitHub Pages redirects it to the apex canonical host.

The retired `drivers.psywerx.io` hostname is intentionally not part of the production architecture. The temporary Vercel redirect project and its DNS records were removed after launch. Future PSYWERX tools should be published as paths under `https://psywerx.io/` rather than as separate hosting stacks or subdomains unless a specific technical requirement justifies an exception.

The repository root `CNAME` must remain exactly:

```text
psywerx.io
```

Current production hosting therefore has one primary static host: GitHub Pages.
