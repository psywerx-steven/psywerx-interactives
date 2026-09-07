# Homepage launch migration boundary

This launch candidate is limited to version-controlled preparation. It does not authorize external DNS changes, Super changes, GitHub Pages configuration, redirect-service deployment, or a production merge.

## Repository boundary

- The approved homepage is generated at the repository root with same-site `/drivers/` and `/cognitive-security/` links.
- `homepage-preview/` remains a generated noindex design/QA surface.
- Driver and Cognitive Security application code, data, IDs, methodology, and governed semantics remain outside the homepage migration.
- The checked-in `CNAME` remains `drivers.psywerx.io` until a coordinated cutover commit.
- The existing Super homepage and current Explorer host remain live until production acceptance succeeds.

## Super retirement decision

The owner has explicitly authorized retirement of the 98 secondary Super/Notion pages. They will not be migrated, recreated, individually redirected, given a special 404, or treated as a launch dependency. `CURRENT_SITE_INVENTORY.md` remains only as a historical and rollback snapshot.

Do not delete or disable the Super site before the new apex homepage passes the production acceptance window. After acceptance, the obsolete secondary content and Super site may be retired by the owner.

## Research stream boundary

Every Morning Brief item enters the canonical JSONL database whether or not it is selected for the homepage. The database is not a causal model and does not require Driver, mechanism, pathway, intervention-chain, or ontology representation.

All new records begin pending. Only an explicit evening owner decision makes a record eligible for the public stream. Hold and reject retain the record in the database. The public homepage receives an allowlisted, paginated projection and never exposes the four substantive research notes or private source-system metadata.

No Google Drive connector, credential, private document identifier, backend, or automated publication transition is part of this launch candidate.

## Legacy Explorer-host boundary

`drivers.psywerx.io` requires a deliberately configured HTTPS redirect service after Pages moves to the apex. DNS alone cannot preserve paths. The checked-in handler retains Driver and Cognitive Security paths and queries, with old-host `/` routed to `/drivers/`. Deployment and DNS attachment remain cutover actions.
