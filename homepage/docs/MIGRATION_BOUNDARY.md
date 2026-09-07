# Preserve the current site while preparing the homepage

This package does not authorize switching DNS or replacing the live root redirect.

## Preview phase

Integrate into an isolated feature branch and preview directory. Do not alter existing driver/cognitive-security data, application scripts, root CNAME, Pages settings, publishing workflow, DNS, MX/TXT records, or the old Super/Notion site. Main has newer work beyond the historical PR #8 checkpoint; fetch and preserve it.

A safe candidate staging location is `homepage-preview/`, with the supplied `site/` contents beneath it. The existing root redirect remains unchanged. The two live tool URLs remain absolute current URLs in preview mode.

## Separate launch phase — requires explicit approval

After visual, content, accessibility, and integration review:

- Inventory current Super pages and important public URLs; do not lose useful content by moving only the screenshot.
- Back up site and DNS configuration.
- Plan the site root homepage and clean `/drivers/` and `/cognitive-security/` paths.
- Rebuild with local tool paths at the eventual root.
- Verify the apex domain and configure Pages/custom-domain settings through the supported process.
- Make the corresponding DNS changes, preserve mail and verification records, check TLS, and test the whole site.
- Retain a rollback route to the former site until cutover is validated.

## Old subdomain links need an explicit plan

`drivers.psywerx.io` cannot be assumed to remain a supported alias automatically after the Pages custom domain is changed. DNS alone cannot perform a path-preserving HTTP redirect, and one Pages CNAME cannot list both hostnames.

Keep the old domain only through a deliberately configured redirect host/service with valid HTTPS. Preserve paths and query strings, and handle its root specially: old `drivers.psywerx.io/` should resolve to the Drivers Explorer, not unexpectedly to the new PSYWERX homepage. Existing cognitive-security links on that subdomain must retain their cognitive-security path.

Do not attempt this cutover in the initial design PR. A later migration plan should name the actual DNS provider, redirect mechanism, verification steps, and rollback procedure.
