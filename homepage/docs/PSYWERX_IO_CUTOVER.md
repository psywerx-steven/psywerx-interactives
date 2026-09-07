# `psywerx.io` cutover and rollback runbook

This launch candidate changes only version-controlled files. It does not change DNS, Super, the GitHub Pages custom domain, or any redirect-service setting.

## Observed production state (2026-09-07)

| Name | Observed public configuration |
|---|---|
| `psywerx.io` | `A 76.76.21.21`; HTTP response served by Vercel/Super |
| `www.psywerx.io` | `CNAME cname.super.so`, then `cname.vercel-dns.com`; permanent redirect to the apex |
| `drivers.psywerx.io` | `CNAME psywerx-steven.github.io`; HTTP response served by GitHub Pages |
| authoritative name servers | `ns-cloud-a1` through `ns-cloud-a4.googledomains.com` |
| mail | Google MX records at priorities 1, 5, and 10 |
| public TXT | SPF including `_spf.mlsend.com`, Google site verification, and MailerLite domain verification |
| repository Pages model | Existing repository documentation records legacy GitHub Pages publication from `main` `/`; the public host and checked-in `CNAME` are consistent with that model. The unauthenticated Pages API does not expose the private repository's settings. |

The authoritative name servers identify Google Domains infrastructure, but they do not prove which current registrar/account UI controls the zone. The domain owner must identify the credentialed DNS console before cutover.

## Why `CNAME` remains unchanged in this PR

The checked-in `CNAME` remains `drivers.psywerx.io`. Changing it to `psywerx.io` on an ordinary merge could detach the currently live explorer hostname before the replacement redirect service and apex DNS are ready. Immediately before an intentionally coordinated cutover merge, add a final reviewed commit that changes the file to exactly:

```text
psywerx.io
```

Do not merge the launch PR while it still contains `drivers.psywerx.io`; doing so would publish the new root homepage at the old explorer host before the domain migration is staged.

## Redirect service contract

Deploy `legacy-redirect/worker.mjs` to an HTTPS redirect service and attach `drivers.psywerx.io`. The service must return:

| Request | Required `Location` |
|---|---|
| `https://drivers.psywerx.io/` | `https://psywerx.io/drivers/` |
| `https://drivers.psywerx.io/drivers/...?...` | `https://psywerx.io/drivers/...?...` |
| `https://drivers.psywerx.io/cognitive-security/...?...` | `https://psywerx.io/cognitive-security/...?...` |
| any other non-root path | same path and query on `https://psywerx.io` |

Use HTTP 308, keep the initial cache lifetime at five minutes, and raise it only after validation. DNS alone is not an HTTP redirect. Fragments are not transmitted to servers; browsers normally retain the original fragment when `Location` omits one, so validate representative hash links in browsers.

## Pre-cutover human checklist

1. Export or snapshot the Super/Notion site, its 99-URL sitemap, Super configuration, and current DNS zone. Keep the Super subscription/site active through validation.
2. Decide the disposition of every secondary Super URL listed in `CURRENT_SITE_INVENTORY.md`. Implement approved content moves or redirects before retiring Super; do not guess from URL slugs.
3. Identify the credentialed DNS provider/account and a person authorized to edit the GitHub Pages settings.
4. In GitHub, complete domain verification for `psywerx.io` using GitHub's unique `_github-pages-challenge-...` TXT value. This is additive and should not disturb the live site.
5. Lower only the apex, `www`, and `drivers` record TTLs to 300 at least one prior TTL window before cutover. Do not change MX, SPF, MailerLite verification, Google verification, or unrelated records.
6. Choose the HTTPS redirect service. Deploy the checked-in redirect handler, prove it through the service's temporary hostname, attach `drivers.psywerx.io` using non-disruptive domain validation where supported, and confirm its certificate can be issued at cutover.
7. Complete editorial decisions in `FEED_LAUNCH_REVIEW.md`. It is valid to launch with the honest empty feed; it is not valid to publish unreviewed drafts.
8. Re-run the repository, browser, explorer, governance, secret, link, and deterministic-build checks on the final PR head. Require all GitHub CI checks to pass.
9. Add the final cutover commit changing `CNAME` to `psywerx.io`, rebuild once, and confirm the diff changes no explorer data or semantics.

## Coordinated cutover

1. Announce the cutover window and freeze unrelated merges to `main`.
2. Confirm Super still serves the apex and the old GitHub Pages explorer still serves `drivers.psywerx.io` immediately before starting.
3. Merge the reviewed launch PR only after its final `CNAME` commit and green CI.
4. In the DNS console, replace the apex's Vercel address with the four GitHub Pages `A` records currently documented by GitHub: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, and `185.199.111.153`. If IPv6 is used, set the four documented `AAAA` records: `2606:50c0:8000::153` through `2606:50c0:8003::153`. Re-check GitHub's official documentation at execution time.
5. Replace `www`'s Super CNAME with `psywerx-steven.github.io`. Confirm GitHub redirects `www` to the chosen apex canonical host.
6. Replace `drivers`' GitHub Pages CNAME with the redirect service's exact verified DNS target. Do not point it at the apex.
7. Confirm the GitHub Pages custom-domain setting is `psywerx.io`. Wait for the certificate to become valid, then enable **Enforce HTTPS**. Do not accept certificate warnings as a successful cutover.
8. Validate from at least two networks/resolvers: apex, `www`, both explorers, codebook, deep/query links, old-host redirects, assets, newsletter form structure, LinkedIn, metadata, robots, sitemap, and TLS.
9. Monitor 404s and redirect failures. Keep Super and the redirect rollback configuration intact until the owner accepts production.

## Validation commands and cases

- Resolve `A`, `AAAA`, `CNAME`, `MX`, and `TXT` records from more than one resolver.
- Request headers for `https://psywerx.io/`, `/drivers/`, `/cognitive-security/`, and `/drivers/codebook/`.
- Verify `https://drivers.psywerx.io/` returns 308 to `/drivers/`.
- Verify old Driver and Cognitive Security URLs retain paths and query strings.
- In a browser, verify representative Explorer query/hash state, including a URL with both query and fragment.
- Confirm the certificate covers `psywerx.io`, `www.psywerx.io`, and `drivers.psywerx.io` through their respective hosts.
- Submit one owner-controlled newsletter test address only after the owner authorizes a live subscription test.

## Rollback

1. Keep the Super site active and its configuration/export untouched.
2. If the apex fails validation, restore the apex `A` record to `76.76.21.21` and restore `www CNAME cname.super.so`. Leave MX/TXT records unchanged.
3. If only legacy redirects fail, restore `drivers CNAME psywerx-steven.github.io` **only if** GitHub Pages has first been restored to the `drivers.psywerx.io` custom domain; otherwise that DNS record will not restore service.
4. Revert the launch commit on `main` with a new non-destructive revert commit and restore the repository `CNAME` to `drivers.psywerx.io` if returning Pages to the former explorer host. Do not reset or rewrite history.
5. Wait for DNS/TLS propagation, verify the old root and explorer hosts, and document the incident before attempting another cutover.

Because the Super origin and old repository state are retained, rollback remains possible until the owner explicitly retires them after the acceptance window.
