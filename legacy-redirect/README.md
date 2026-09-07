# Legacy `drivers.psywerx.io` redirect

The legacy hostname is being retired as part of the PSYWERX apex-domain cutover. The canonical Driver Explorer URL is:

`https://psywerx.io/drivers/`

The redirect project is deployed on Vercel as `psywerx-drivers-redirect`. Its production deployment has been verified to return HTTP 308 redirects with these contracts:

- `https://drivers.psywerx.io/` → `https://psywerx.io/drivers/`
- any non-root path on `drivers.psywerx.io` → the same path on `https://psywerx.io`
- query strings are preserved

The `drivers.psywerx.io` custom domain is ownership-verified in Vercel but intentionally remains pointed at GitHub Pages until the coordinated production DNS cutover. Vercel may therefore report `Invalid Configuration` before cutover; that is expected while the current `drivers` CNAME still points to GitHub Pages.

Do not change the legacy hostname DNS independently of the coordinated cutover. Preserve the `_vercel` ownership-verification TXT record.
