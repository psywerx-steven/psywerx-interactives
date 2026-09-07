"""Truthful additive bibliographic verification; no live fetching or registration.

Validate externally obtained registry/publisher attestations against frozen
metadata. A passed check proves internal/source alignment, not scientific efficacy
or freshness. Canonical registration still requires exact human governance.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
from jsonschema import Draft202012Validator, FormatChecker
import hashlib

ROOT=Path(__file__).resolve().parents[1]
TEXT={'type':'string','minLength':1}
FIELDS=['title','authors','year','publication','doi','sourceType']
SCHEMA={
    '$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'https://psywerx.org/schemas/source-verification/v1/verification-v1.schema.json',
    'title':'Authoritative non-PubMed bibliographic verification V1',
    'type':'object','additionalProperties':False,
    'required':['status','system','verificationVersion','verifiedDate','identifierChecked','method','authority',
                'registryLocator','publisherLocator','verifiedFields','accessDepth','conflicts','verificationConfidence','provenance'],
    'properties':{
        'status':{'const':'VERIFIED'},'system':{'const':'AUTHORITATIVE_BIBLIOGRAPHIC'},
        'verificationVersion':{'const':'1.0.0'},'verifiedDate':{'type':'string','format':'date'},
        'identifierChecked':TEXT,'method':{'const':'DOI_REGISTRY_AND_PUBLISHER_ALIGNMENT'},
        'authority':{'enum':['CROSSREF','DATACITE']},
        'registryLocator':{'type':'string','format':'uri'},'publisherLocator':{'type':'string','format':'uri'},
        'verifiedFields':{'const':FIELDS},'accessDepth':{'enum':['METADATA','ABSTRACT_METADATA','SELECTED_FULL_TEXT','FULL_TEXT']},
        'conflicts':{'type':'array','maxItems':0},
        'verificationConfidence':{'enum':['MODERATE','HIGH']},
        'provenance':{'type':'object','additionalProperties':False,'required':['path','contentHash','reviewMethod','limitations'],
            'properties':{'path':TEXT,'contentHash':{'type':'string','pattern':'^[a-f0-9]{64}$'},
                          'reviewMethod':TEXT,'limitations':{'type':'array','minItems':1,'items':TEXT}}}
    }}


class VerificationError(ValueError): pass


def require(condition,message):
    if not condition: raise VerificationError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def doi(value):
    value=unquote(str(value or '')).strip().lower()
    for prefix in ('https://doi.org/','http://doi.org/','doi:'):
        if value.startswith(prefix): value=value[len(prefix):]
    return value.strip()


def https_url(value):
    u=urlparse(value)
    require(u.scheme=='https' and u.hostname and u.username is None and u.password is None and u.port in (None,443),
            'Verification requires authoritative HTTPS locators without userinfo')
    return u


def validate_source(source, root=ROOT):
    v=source['verification']
    if v['system']=='PUBMED_NCBI_EUTILITIES':
        # Preserve the old contract exactly; no fabricated PMID or rebadged route.
        require(set(v)=={'status','system','verifiedDate','identifierChecked'},'Legacy PubMed provenance changed')
        require(source.get('pmid') and source['pmid'].isdigit(), 'PubMed route requires an actual PMID')
        require(source['pmid'] in v['identifierChecked'], 'PubMed checked identifier mismatch')
        if source.get('doi'): require(doi(source['doi']) in v['identifierChecked'].lower(), 'PubMed DOI alignment mismatch')
        return True
    errors=list(Draft202012Validator(SCHEMA,format_checker=FormatChecker()).iter_errors(v))
    require(not errors, str(errors[0].message) if errors else '')
    require(source.get('pmid') is None, 'Non-PubMed route cannot assert unverified PubMed identifier')
    identifier=doi(source.get('doi')); require(identifier.startswith('10.') and '/' in identifier, 'DOI required')
    require(v['identifierChecked']=='DOI:'+identifier, 'Verified DOI mismatch')
    registry=https_url(v['registryLocator']); publisher=https_url(v['publisherLocator'])
    routes={'CROSSREF':('api.crossref.org','/works/'),'DATACITE':('api.datacite.org','/dois/')}
    host,prefix=routes[v['authority']]
    require(registry.hostname==host and unquote(registry.path).lower()==prefix+identifier and not registry.query and not registry.fragment,
            'Untrusted/wrong registry locator')
    path=(Path(root)/v['provenance']['path']).resolve()
    require(path.is_relative_to((Path(root)/'docs/governance/source-verification').resolve()) and path.suffix=='.json' and path.is_file(),
            'Verification attestation must resolve in governed provenance directory')
    snapshot=json.loads(path.read_text(encoding='utf-8'))
    require(digest(snapshot)==v['provenance']['contentHash'], 'Verification snapshot hash mismatch')
    require(snapshot.get('recordKind')=='BIBLIOGRAPHIC_VERIFICATION_ATTESTATION' and snapshot.get('conflicts')==[], 'Unresolved bibliographic conflict')
    require(snapshot['verifiedDate']==v['verifiedDate'] and snapshot['authority']==v['authority'], 'Verification date/authority mismatch')
    require(snapshot['registryLocator']==v['registryLocator'] and snapshot['publisherLocator']==v['publisherLocator'], 'Evidence locators mismatch')
    require(snapshot['accessDepth']==v['accessDepth'], 'Access-depth inflation')
    for field in FIELDS:
        for metadata in (snapshot['registryMetadata'],snapshot['publisherMetadata']):
            require(metadata[field]==source[field], 'Bibliographic field mismatch: '+field)
    require(any(https_url(link).hostname==publisher.hostname and identifier in unquote(link).lower()
                for link in snapshot['registryPublisherLinks']), 'Publisher not corroborated by registry links')
    require(source['url']==v['publisherLocator'], 'Canonical URL not verified publisher locator')
    require(snapshot['locators'] and all(snapshot['locators'].get(field) for field in FIELDS), 'Verified fields lack result locators')
    require(snapshot['verificationPurpose']=='BIBLIOGRAPHIC_IDENTITY_ONLY_NOT_EFFECT_EVIDENCE', 'Verification cannot confer effect support')
    require(Path(root,source['governanceDecisionRecord']).resolve().is_relative_to(Path(root,'docs/governance').resolve()) and
            Path(root,source['governanceDecisionRecord']).is_file(), 'Scientific source registration decision unresolved')
    return True


def generate_schema():
    path=ROOT/'schemas/source-verification/v1/verification-v1.schema.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(SCHEMA,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__': generate_schema()
