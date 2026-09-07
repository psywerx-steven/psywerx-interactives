# Homepage integration checkpoint

The original preview checkpoint has been superseded by launch-candidate PR #23 on `feature/psywerx-homepage-launch`.

Current repository state:

- Approved homepage generated at the repository root; preview remains under `homepage-preview/`.
- Same-site release links target `/drivers/` and `/cognitive-security/`.
- Verified MailerLite form and LinkedIn destination are integrated without credentials or intrusive embeds.
- Every Morning Brief item is stored in `data/research-stream/research_items.jsonl`.
- The six former preview records are ordinary pending database records and are not public.
- Public stream generation includes only explicit `publish` decisions.
- Owner-authorized retirement of all 98 secondary Super pages is documented; the inventory remains historical only.
- `CNAME` remains `drivers.psywerx.io`; no external domain or hosting setting has changed.

Primary validation commands:

```powershell
py homepage/tools/build_research_stream.py
py homepage/tools/build_homepage.py --mode preview --tool-links preview
py homepage/tools/build_homepage.py --mode release --tool-links local --output .
py -m unittest tests.test_research_stream tests.test_homepage_preview -v
py homepage/tools/browser_qa.py
```
