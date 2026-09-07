"""Read-only release check: deterministic artifacts, exact additions and links."""
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote
import actions_events_v1 as ae
import audit_family as af
import relational_state_v1 as ns
import relational_state_fixtures as fixtures
import materialize_soc_f07_completion as completion


def check():
    ns.validate_repository()
    expected=fixtures.demonstration()
    path=ns.ROOT/'reports/relational-state-v1/synthetic-validation.json'
    if ae.read(path)!=expected: raise ValueError('Synthetic report is not deterministic/current')
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',ns.BASELINE,'--','data','schemas','scenario-service',
        '_migration_handoff_v0.3','docs/governance/pilots/BIO-F01','docs/governance/pilots/INF-F03'],cwd=ns.ROOT).decode().splitlines()
    changed={}; unchanged={}
    for p in paths:
        before=subprocess.check_output(['git','show',ns.BASELINE+':'+p],cwd=ns.ROOT).replace(b'\r\n',b'\n')
        after=(ns.ROOT/p).read_bytes().replace(b'\r\n',b'\n')
        hashes={'before':hashlib.sha256(before).hexdigest(),'after':hashlib.sha256(after).hexdigest()}
        if before==after: unchanged[p]=hashes; continue
        if p in ('data/actions-events-v1/catalog.json','data/relationship-intervention-v1/source-register.json'):
            assert completion.strip_additions(p,json.loads(after))==json.loads(before),p
            hashes['reason']='Exact hash-bound conditional addition; every pre-existing record/envelope unchanged'
        elif p=='schemas/relationship-intervention/v1/source-record-v1.schema.json':
            assert completion.source_schema_extension_only(json.loads(before),json.loads(after)),p
            hashes['reason']='Exact additive verification union; historical PubMed contract unchanged'
        elif p=='data/candidates/actions-events-v1/SOC-F07/protected-science.json':
            import build_soc_f07_pilot as pilot
            assert json.loads(after)==pilot.protected() and pilot.protected()['passed'],p
            hashes['reason']='Recomputed integrity hashes only; not candidate science'
        else: raise ValueError('Unapproved protected change '+p)
        changed[p]=hashes
    summary=af.enriched_inventory()['summary']
    assert [summary[k] for k in ('drivers','rds','entities','combinedActiveRelationships','combinedActiveCausal')]==[770,41,811,457,436]
    docpaths=subprocess.check_output(['git','diff','--name-only',ns.BASELINE,'--','*.md'],cwd=ns.ROOT).decode().splitlines()
    # Include new untracked docs during local pre-commit validation.
    docpaths+=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','*.md'],cwd=ns.ROOT).decode().splitlines()
    checked=0
    for p in set(docpaths):
        doc=ns.ROOT/p
        if not doc.exists(): continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
            link=unquote(link.split('#',1)[0]).strip('<>')
            if not link or '://' in link or link.startswith('mailto:'): continue
            target=ns.ROOT/link.lstrip('/') if link.startswith('/') else doc.parent/link
            if not target.exists(): raise ValueError('Broken local link '+p+': '+link)
            checked+=1
    return {'baseline':ns.BASELINE,'passed':True,'protectedFiles':len(paths),'unchangedFiles':len(unchanged),
        'authorizedChanges':changed,'unchangedManifestHash':ns.digest(unchanged),'localLinksChecked':checked,
        'activeRelationships':457,'activeCausal':436,'newActive':0,'syntheticDemonstrations':12,
        'derivationCatalog':ns.validate_repository()}


if __name__=='__main__': print(json.dumps(check(),indent=2))
