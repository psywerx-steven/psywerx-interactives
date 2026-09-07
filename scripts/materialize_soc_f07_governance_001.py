"""Exact, additive SOC-F07 human decision materialization; never activation.

No production contract changes. Collection derivation and non-PubMed registration
are explicit failed gates, not free-text workarounds. Candidate science is retained.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

import actions_events_v1 as ae
import relationship_intervention_v1 as ri

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/governance/pilots/SOC-F07'
STORE = ROOT / 'data/candidates/actions-events-v1/SOC-F07'
AE_PATH = ROOT / 'data/actions-events-v1/catalog.json'
SOURCE_PATH = ROOT / 'data/relationship-intervention-v1/source-register.json'
HEAD = '339c2e80206b0b304cdb262e7c5fec6dc0bc27ab'
BASELINE = 'f0be9c24288bd128231e0d1243b34c03ad055906'
AUDIT = 'AUD-SOC-F07-AE-V1-20260906-001'
DECISION = 'GOV-SOC-F07-001-2026-09-06'
DECISION_PATH = 'docs/governance/pilots/SOC-F07/SOC_F07_GOVERNANCE_DECISION_001.md'
DATE = '2026-09-06'
STAMP = '2026-09-07T04:00:00Z'
MANIFEST = DOCS / 'SOC_F07_SOURCE_REGISTRATION_MANIFEST.json'
MARKER = DOCS / 'SOC_F07_HUMAN_DECISIONS.json'
HT_IDS = [f'HT-V1-SOC-F07-{n:03d}' for n in range(1, 8)]
RETAIN = ['REL-RDS-0004', 'REL-RDS-0006', 'REL-RDS-0013']
RETYPE = [f'REL-SOC-{n:03d}' for n in range(31, 35)]
REVISION = ['REL-INS-047', 'REL-SOC-035']
REJECTED = ['H01','H02','H03','H04','H07','H09','H13','H14','H21','H22','H23','H24','H25','H28','H29']
RESEARCH = ['H05','H06','H10','H11','H15','H16','H17','H18','H19','H26','H27']
CONCEPT = ('Degree-based Freeman-style network centralization is derived from the COMPLETE aligned distribution '
           'of all node degree values (SOC-049) for a specifically defined network, plus explicit node set, '
           'boundary, denominator, normalization and maximum/benchmark inputs. One ego value is insufficient. '
           'This does not cover betweenness, eigenvector or closeness centralization and is not causality.')
IDENTITY_LIMIT = (' Identity definition only: no efficacy, causality, practitioner permission or recommendation, '
                  'network-metric change, SOC-102 change, or EffectAssertion activation is implied.')

# Metadata independently reconciled using NCBI efetch, 2026-09-07 UTC / 09-06 local.
# No abstracts or empirical findings are promoted to governed efficacy evidence.
BIBLIOGRAPHY = [
    ('005','553','40587796','Tendencies toward triadic closure: Field experimental evidence',
     ['Mohsen Mosleh','Dean Eckles','David G Rand'],2025,'Proceedings of the National Academy of Sciences of the United States of America','10.1073/pnas.2404590122','RANDOMIZED_FIELD_EXPERIMENT'),
    ('006','554','32076003','Short-term and long-term effects of a social network intervention on friendships among university students',
     ['Zsófia Boda','Timon Elmer','András Vörös','Christoph Stadtfeld'],2020,'Scientific reports','10.1038/s41598-020-59594-z','RANDOMIZED_NETWORK_INTERVENTION'),
    ('007','555','22084103','Dynamic social networks promote cooperation in experiments with humans',
     ['David G Rand','Samuel Arbesman','Nicholas A Christakis'],2011,'Proceedings of the National Academy of Sciences of the United States of America','10.1073/pnas.1108243108','CONTROLLED_NETWORK_EXPERIMENT'),
    ('008','556','25952354','Social network targeting to maximise population behaviour change: a cluster randomised controlled trial',
     ['David A Kim','Alison R Hwong','Derek Stafford','D Alex Hughes',"A James O'Malley",'James H Fowler','Nicholas A Christakis'],2015,'Lancet (London, England)','10.1016/S0140-6736(15)60095-2','CLUSTER_RANDOMIZED_CONTROLLED_TRIAL'),
    ('011','557','25964337','A natural experiment of social network formation and dynamics',
     ['Tuan Q Phan','Edoardo M Airoldi'],2015,'Proceedings of the National Academy of Sciences of the United States of America','10.1073/pnas.1404770112','NATURAL_EXPERIMENT_LONGITUDINAL_NETWORK'),
    ('012','558','34379633','Proximity can induce diverse friendships: A large randomized classroom experiment',
     ['Julia M Rohrer','Tamás Keller','Felix Elwert'],2021,'PloS one','10.1371/journal.pone.0255097','RANDOMIZED_CLASSROOM_EXPERIMENT'),
]
SOURCE_MAP = {'SRC-CAND-SOC-F07-'+r[0]:'SRC-'+r[1] for r in BIBLIOGRAPHY}
SOURCE_MAP.update({'SRC-235':'SRC235', 'SRC-250':'SRC250'})


@lru_cache(maxsize=None)
def frozen(path):
    return json.loads(subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT))


def write(path, value):
    allowed = [DOCS, STORE]
    exact_production={AE_PATH.resolve(),SOURCE_PATH.resolve(),(AE_PATH.parent/'SOC-F07-materialization-manifest.json').resolve()}
    if path.resolve() not in exact_production and not any(path.resolve().is_relative_to(p.resolve()) for p in allowed):
        raise ValueError('Output outside exact governance materialization scope')
    path.parent.mkdir(parents=True,exist_ok=True)
    canonical=path in (AE_PATH,SOURCE_PATH)
    if canonical:
        def ordered(obj, template):
            if isinstance(obj,dict) and isinstance(template,dict):
                return {k:ordered(obj[k],template.get(k)) for k in list(template)+[k for k in obj if k not in template] if k in obj}
            if isinstance(obj,list) and isinstance(template,list):
                reference={r.get('id',r.get('decisionId')):r for r in template if isinstance(r,dict)}
                return [ordered(r,reference.get(r.get('id',r.get('decisionId')))) if isinstance(r,dict) else r for r in obj]
            return obj
        value=ordered(value,frozen(path.relative_to(ROOT).as_posix()))
    text = value.rstrip()+'\n' if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2,sort_keys=not canonical)+'\n'
    path.write_text(text,encoding='utf-8',newline='\n')


def sources():
    return [{
        'schemaVersion':'1.0.0','id':'SRC-'+n,'citationText':'; '.join(authors)+f'. {title}. {venue}. {year}. doi:{doi}. PMID:{pmid}.',
        'title':title,'authors':authors,'year':year,'publication':venue,'doi':doi,'pmid':pmid,
        'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/','sourceType':kind,
        'verification':{'status':'VERIFIED','system':'PUBMED_NCBI_EUTILITIES','verifiedDate':DATE,'identifierChecked':f'PMID:{pmid}; DOI:{doi}'},
        'governanceDecisionRecord':DECISION_PATH,'auditId':AUDIT,
    } for _,n,pmid,title,authors,year,venue,doi,kind in BIBLIOGRAPHY]


def identities():
    candidates = frozen('data/candidates/actions-events-v1/SOC-F07/workspace.json')['passB']['happeningTypes']
    records = []
    for candidate in candidates[:7]:
        r=copy.deepcopy(candidate); cid=r['id']; r['id']=cid.replace('HT-CAND-','HT-V1-')
        # The same reusable operation; the lineage manifest prevents double counting.
        r['identityKey']=candidate['identityKey']
        r['identitySourceIds']=[SOURCE_MAP[s] for s in r['identitySourceIds'] if s in SOURCE_MAP]
        if not r['identitySourceIds']: raise ValueError('Cannot remove structured identity source provenance')
        r['description']=candidate['description']+IDENTITY_LIMIT
        if r['id'].endswith('006'):
            r['kindTags']=['EVENT','EXPOSURE']
            r['description']+=' This storm-related exposure is not a deliberate practitioner action.'
        g=r['governance']
        for t in g['transitionProvenance']:
            t['objectId']=r['id']
            t['provenance']+=f'; candidate transition retained from {cid}'
        g.update(lifecycleStatus='GOVERNED',activationStatus='INACTIVE',decisionOutcome='APPROVED',
                 decisionRecord=DECISION_PATH,authorizedBy='authorized human governor',decisionDate=DATE,
                 effectiveVersion='SOC-F07-GOVERNANCE-001',decisionRationale='Exact human-approved reusable identity; no effect or activation approved.')
        g['transitionProvenance'].append({
            'fromState':{'lifecycleStatus':'REVIEW_READY','activationStatus':'NOT_ELIGIBLE'},
            'toState':{'lifecycleStatus':'GOVERNED','activationStatus':'INACTIVE'},
            'actorClass':'AUTOMATED_PROCESS_OR_AI','rationale':'Exact materialization of authorized human identity decision; activation withheld.',
            'timestamp':STAMP,'objectId':r['id'],'revision':1,'provenance':f'{AUDIT}:{HEAD}:{cid}',
            'governanceDecisionRecord':DECISION_PATH,'exactDecisionMaterialization':True})
        r['provenance']={'actorClass':'AUTOMATED_PROCESS_OR_AI','method':'Exact authorized candidate-to-canonical identity materialization',
            'recordedAt':STAMP,'originReferences':[AUDIT,HEAD,cid,DECISION,DECISION_PATH],
            'limitations':['Identity definition is not efficacy evidence; all use eligibility remains false while inactive.',
                'Candidate research/source findings are retained without receiving scientific authority from identity governance.']}
        records.append(r)
    return records


def authorization(records):
    return {'decisionId':DECISION,'decisionRecord':DECISION_PATH,'actorClass':'AUTHORIZED_HUMAN_GOVERNOR',
            'effectiveDate':DATE,'recordClass':'SCIENTIFIC_RECORD','authorizedObjects':[
                {'id':r['id'],'revision':r['revision'],'recordHash':ae.digest(r)} for r in records]}


def exact_additions(path, original, current):
    """Compare ALL old records and envelope metadata, not a file-level whitelist."""
    if path not in {'data/actions-events-v1/catalog.json','data/relationship-intervention-v1/source-register.json'}:
        return False
    old=json.loads(original); new=copy.deepcopy(json.loads(current))
    # The later NS-enabled checkpoint is separately hash-bound. Never absorb
    # it into, or regenerate, this historical seven-identity decision.
    import materialize_soc_f07_completion as completion
    if completion.MANIFEST.exists():
        try: new=completion.strip_additions(path,new)
        except ValueError: return False
    if path.endswith('catalog.json'):
        expected={r['id']:r for r in identities()}
        additions={r['id']:r for r in new['happeningTypes'] if r['id'] in expected}
        if additions!=expected: return False
        new['happeningTypes']=[r for r in new['happeningTypes'] if r['id'] not in expected]
        added=[r for r in new['authorizations'] if r['decisionId']==DECISION]
        if added!=[authorization(identities())]: return False
        new['authorizations']=[r for r in new['authorizations'] if r['decisionId']!=DECISION]
    else:
        expected={r['id']:r for r in sources()}
        if {r['id']:r for r in new['sources'] if r['id'] in expected}!=expected: return False
        new['sources']=[r for r in new['sources'] if r['id'] not in expected]
    # Ordering is not scientific content; every existing record and metadata is.
    for key in ('happeningTypes','authorizations','sources'):
        if key in old:
            by=lambda rows:sorted(rows,key=lambda r:r.get('id',r.get('decisionId','')))
            old[key]=by(old[key]); new[key]=by(new[key])
    return old==new


def decision_rows():
    w=frozen('data/candidates/actions-events-v1/SOC-F07/workspace.json')
    audits=frozen('data/candidates/actions-events-v1/SOC-F07/existing-relationship-audit.json')
    rows=[]
    for a in audits:
        identifier=a['id']
        outcome=('APPROVE_RETAIN_AS_IS' if identifier in RETAIN else 'APPROVE_RETYPE_REVIEW_ONLY' if identifier in RETYPE
                 else 'APPROVE_REVISION_REVIEW_ONLY' if identifier in REVISION else 'APPROVE_RESEARCH_NEEDED_DISPOSITION')
        rows.append({'id':identifier,'outcome':outcome,'propositionOrDisposition':a['proposedReview'],
                     'sourceIds':a['sources'],'implementation':'EXISTING_GOVERNED_RECORD_UNCHANGED'})
    rows.append({'id':'REL-CAND-SOC-F07-001','outcome':'MODIFY_APPROVE_AS_MODIFIED','propositionOrDisposition':CONCEPT,
                 'sourceIds':w['passA']['relationshipCandidates'][0]['sourceIds'],
                 'implementation':'BLOCKED_PENDING_REPRESENTATION'})
    for h in w['passB']['happeningTypes']:
        rows.append({'id':h['id'],'outcome':'APPROVE_IDENTITY','propositionOrDisposition':h['name']+'.'+IDENTITY_LIMIT,
                     'sourceIds':h['identitySourceIds'],'implementation':'BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT' if h['id'].endswith('008') else 'GOVERNED_INACTIVE'})
    for e in w['passB']['effectAssertions']:
        rows.append({'id':e['id'],'outcome':'APPROVE_RESEARCH_NEEDED_DISPOSITION','propositionOrDisposition':e['typeId']+' -> SOC-102; exact direction UNKNOWN; no effect governed.',
                     'sourceIds':[],'implementation':'RESEARCH_NEEDED_NOT_ELIGIBLE'})
    for h in frozen('data/candidates/actions-events-v1/SOC-F07/hypotheses.json'):
        short=h['shortId']
        outcome=('APPROVE_REJECTION' if short in REJECTED else 'KEEP_RESEARCH_NEEDED' if short in RESEARCH else
                 'KEEP_BLOCKED' if short in {'H12','H20'} else 'MODIFY_APPROVE_AS_MODIFIED')
        rows.append({'id':h['id'],'shortId':short,'outcome':outcome,'propositionOrDisposition':h['proposition'],
                     'rationale':h['reason'],'sourceIds':h['sourceIds'],
                     'implementation':'BLOCKED_PENDING_REPRESENTATION' if short=='H08' else h['disposition']})
    for gap in frozen('data/candidates/actions-events-v1/SOC-F07/ontology-target-gaps.json'):
        rows.append({'id':gap['id'],'outcome':'KEEP_BLOCKED','propositionOrDisposition':'Preserve unresolved underlying relational-configuration target gap; not a request for a new Driver per RDS.',
                     'sourceIds':[],'implementation':'NEEDS_GOVERNANCE_INPUT'})
    rows.append({'id':'SOC-F07-NON-CREATION','outcome':'APPROVE_NON_CREATION',
        'propositionOrDisposition':'No formal new causal, association, temporal, semantic, moderation or pathway record; no STRUCTURE or relationship-targeted effect.',
        'sourceIds':[],'implementation':'NO_RECORDS_CREATED'})
    return rows


def decisions():
    return {'decisionId':DECISION,'auditId':AUDIT,'baselineCommit':BASELINE,'pilotHeadBeforeGovernance':HEAD,'pr':19,
            'actorClass':'authorized human governor','effectiveDate':DATE,'materializedAt':STAMP,'activationAuthorized':False,
            'rows':decision_rows(),'newArchitectureDecisionStatus':'PENDING'}


def human_outcome(identifier):
    for r in decision_rows():
        if identifier in {r['id'],r.get('shortId')}:
            return r['outcome']+' — '+r['implementation']
    raise ValueError('No authorized human decision for '+identifier)


def decorate_products(products):
    for a in products['existing-relationship-audit.json']: a['governanceDecision']=human_outcome(a['id'])
    for r in products['revision-proposals.json']: r['governanceDecision']=human_outcome(r['currentRecord']['id'])
    for h in products['hypotheses.json']: h['humanDecision']=human_outcome(h['id'])
    for gap in products['ontology-target-gaps.json']: gap['humanDecision']=human_outcome(gap['id'])
    for s in products['source-registration-queue.json']:
        if s['sourceId'] in SOURCE_MAP:
            s.update(canonicalRegistration='REGISTERED_IDENTITY_PROVENANCE_ONLY',canonicalSourceId=SOURCE_MAP[s['sourceId']],
                     condition='Authorized by '+DECISION+'; no effect evidence or activation authority conferred.')
        elif s['sourceId']=='SRC-CAND-SOC-F07-010':
            s.update(canonicalRegistration='BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT',
                     condition='Verified non-PubMed identity; do not falsely label PubMed verification or remove structured source binding.')
        else:
            s.update(canonicalRegistration='NOT_REQUIRED_AT_THIS_CHECKPOINT',condition='No actually governed record requires this source.')


def decorate_document(path, value):
    if isinstance(value,dict):
        value=copy.deepcopy(value)
        value.update(newGoverned=7,newActive=0,approval=DECISION,recordClass='GOVERNANCE_MATERIALIZATION_AUDIT',
                     scientificReadiness='GOVERNED_INACTIVE_IDENTITIES_ONLY; derivation representation and HT-008 source contract blocked',
                     governanceCheckpoint={'decisionRecord':DECISION_PATH,'materializationManifest':'data/actions-events-v1/SOC-F07-materialization-manifest.json',
                                           'happeningTypes':7,'relationships':0,'evidenceAssessments':0,'sourceFindings':0,'sources':6})
        return value
    if path.name=='SOC_F07_GOVERNANCE_DECISION_PACKAGE.md': return decision_document(package=True)
    value=value.replace('Candidate-only; no governance, activation or source registration.',
        'Candidate audit preserved; human governance checkpoint recorded. Seven identities are governed INACTIVE; six identity-provenance sources registered. No activation. See [decision](SOC_F07_GOVERNANCE_DECISION_001.md).')
    # Existing-edge sections retain exact scientific concerns; replace only their human field.
    for identifier in RETAIN+RETYPE+REVISION+['REL-TEC-050']:
        start=value.find('## '+identifier+' ')
        if start>=0:
            end=value.find('\n## ',start+4)
            if end<0: end=len(value)
            value=value[:start]+value[start:end].replace('PENDING — APPROVE / MODIFY / REJECT',human_outcome(identifier))+value[end:]
    return value


def decision_document(package=False):
    title='SOC-F07 human governance decision package — materialized outcomes' if package else 'SOC-F07 human governance decision 001'
    text=f'# {title}\n\nDecision `{DECISION}`; audit `{AUDIT}`; effective local date {DATE}. Actor class: `authorized human governor`.\n\n'
    text+=f'Frozen main `{BASELINE}`; pre-checkpoint head `{HEAD}`; [PR #19](https://github.com/psywerx-steven/psywerx-interactives/pull/19). Authorization basis: the explicit human SOC-F07 governance and bounded architecture-review instruction. Activation explicitly withheld. No merge authorized.\n\n'
    text+='Scientific approval does not cure representation or source-contract defects. Existing governed records, blocked fields, classifications and prior pilots remain unchanged. Candidate copies remain non-governed lineage; the authoritative new identities are in the production AE catalog.\n\n'
    text+='## Exact decisions\n\n| ID | Human outcome | Exact proposition / disposition | Materialization |\n| --- | --- | --- | --- |\n'
    for r in decision_rows():
        proposition=r['propositionOrDisposition']+(' Rationale: '+r['rationale'] if 'rationale' in r else '')
        text+='| '+r['id']+' | '+r['outcome']+' | '+proposition.replace('|','/')+' | '+r['implementation']+' |\n'
    text+='\n## Retained semantic bounds\n\nREL-RDS-0004 is equivalent only under matched boundary, tie definition, window and binary/unweighted/undirected assumptions. REL-RDS-0006 is RELATED_METRIC, not equality or causality. REL-RDS-0013 is NARROWER_THAN with aligned risk set/interval. No duplicate V1 propositions were minted.\n'
    text+='\n## Materialization gates and sources\n\n'+CONCEPT+'\n\n'
    text+='The current binary Relationship V1 schema has no collection quantifier, alignment key, external-input binding or benchmark completeness validator. Free text and unconstrained functionalForm objects cannot enforce all-node versus one-ego dependency. REL-CAND-SOC-F07-001 is therefore BLOCKED_PENDING_REPRESENTATION; H08 concept approval is preserved, but neither Relationship nor definitional assessment is governed. No causal assessment is invented.\n\n'
    text+='HT-CAND-SOC-F07-008 identity is human-approved and its bibliographic identity is verified, but its structured source is not registrable under the native schema’s PUBMED_NCBI_EUTILITIES constant. Publisher/preprint verification is not PubMed verification. No replacement source, empty-source workaround or production contract edit is used. The candidate stays REVIEW_READY / NOT_ELIGIBLE; materialization is BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT. This is not scientific rejection.\n\n'
    text+='Seven canonical identities HT-V1-SOC-F07-001 through 007, revision 1, are GOVERNED / INACTIVE. SRC-553 through SRC-558 support only their definitions; existing source tokens SRC-235 and SRC-250 normalize to actual canonical IDs SRC235 and SRC250. SRC-509’s Centola component duplicates SRC235 and is not independent evidence. The Hunter review is unnecessary for the approved seeding identity and is not registered; its candidate evidence remains intact.\n\n'
    text+='[Source registration manifest](SOC_F07_SOURCE_REGISTRATION_MANIFEST.json) records exact mappings, access and unregistered sources. [Machine-readable decisions](SOC_F07_HUMAN_DECISIONS.json) preserve every outcome. [Materialization lineage/hashes](../../../../data/actions-events-v1/SOC-F07-materialization-manifest.json) bind candidate revision/hash to canonical revision/hash and this decision.\n\n'
    text+='## No activation or architecture approval\n\nNew GOVERNED = 7; new INACTIVE = 7; new ACTIVE = 0. New Relationships, EffectAssertions, Occurrences, EvidenceAssessments and governed sourceFindings = 0. Production remains 770 Drivers, 41 RDS, 811 entities, 457 active Relationships / 436 active causal. All three SOC-F07 effects stay RESEARCH_NEEDED with UNKNOWN direction. Identity approval never governs their source findings.\n\n'
    text+='H12/H20 and twelve target gaps remain unresolved; four retype and two revision proposals remain non-governed/unimplemented. No AE04/D10 change, network-state entity, model, recommendation, deployment or other Family work. The isolated Network State review and NS01–NS12 remain EXPERIMENTAL / NON_PRODUCTION / PENDING. See [handoff](SOC_F07_NETWORK_STATE_HANDOFF.md).\n'
    return text


def source_manifest():
    candidates=frozen('data/candidates/actions-events-v1/SOC-F07/source-registry.json')
    records=identities()
    return {'auditId':AUDIT,'governanceDecisionId':DECISION,'verificationDate':DATE,'verificationUtcDate':'2026-09-07',
        'supplementalEvaluated':18,'supplementalSelectedForIdentityVerification':7,'registeredCount':6,
        'newDuplicateRecords':0,'newGovernedEvidenceAssessments':0,'newGovernedSourceFindings':0,
        'registrations':[{'candidateSourceId':s['id'],'canonicalSourceId':SOURCE_MAP[s['id']],
            'governedRecords':[r['id'] for r in records if SOURCE_MAP[s['id']] in r['identitySourceIds']],
            'purpose':'IDENTITY_DEFINITION_ONLY_NOT_EFFICACY','deduplication':'Complete legacy/native DOI, PMID and normalized title/year: no new duplicate',
            'checkpointAccessDepth':'METADATA','priorPilotAccessDepth':s['accessDepth'],
            'verificationUrl':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+next(r['pmid'] for r in sources() if r['id']==SOURCE_MAP[s['id']])+'&retmode=xml'}
            for s in candidates if s['id'] in SOURCE_MAP and s['id'].startswith('SRC-CAND')],
        'canonicalReused':[{'candidateToken':'SRC-235','canonicalId':'SRC235','governedRecords':['HT-V1-SOC-F07-004']},
                           {'candidateToken':'SRC-250','canonicalId':'SRC250','governedRecords':['HT-V1-SOC-F07-005']}],
        'preservedOverlap':'SRC-509 linked Centola component is the same work as SRC235 (pilot alias SRC-235); unresolved second component is not independent evidence. Reviews and included primary studies are not independent replications.',
        'unregistered':[{'candidateSourceId':s['id'],'reason':'BLOCKED_NON_PUBMED_VERIFICATION_CONTRACT' if s['researchKey']=='010' else 'NOT_REQUIRED_BY_ACTUALLY_MATERIALIZED_RECORD',
                         'title':s['title']} for s in candidates if s['id'].startswith('SRC-CAND') and s['id'] not in SOURCE_MAP],
        'bibliographyReconciledButContractBlocked':{'candidateSourceId':'SRC-CAND-SOC-F07-010','governedRecord':None,
            'approvedCandidateId':'HT-CAND-SOC-F07-008','authors':['Tianshu Sun','Sean J. Taylor'],
            'preprint':{'year':2019,'url':'https://arxiv.org/abs/1905.02762','doi':'10.48550/arXiv.1905.02762','accessDepth':'ABSTRACT_METADATA'},
            'journalVersion':{'year':2020,'title':'Displaying things in common to encourage friendship formation: A large randomized field experiment',
                'venue':'Quantitative Marketing and Economics','volume':18,'pages':'237–271','publicationDate':'2020-05-23',
                'doi':'10.1007/s11129-020-09224-9','url':'https://link.springer.com/article/10.1007/s11129-020-09224-9','accessDepth':'PUBLISHER_ABSTRACT_METADATA'},
            'overlap':'Preprint and journal are versions of the same work, not independent studies.',
            'pubmedQuery':'"10.1007/s11129-020-09224-9"','pubmedResultCount':0,
            'result':'Bibliographic identity verified; no truthful native registration path used. Human review of source contract required.'},
        'recordsBlockedByBibliographicIdentityFailure':[],
        'recordsBlockedBySourceContract':['HT-CAND-SOC-F07-008'],
        'derivationSourceRegistration':'NOT_PERFORMED: collection representation gate failed; SRC255 (pilot SRC-255) and UCINET candidate documentation remain candidate provenance.'}


def materialize():
    record_set=identities(); new_sources=sources()
    # Reject ID collision or a differing rerun rather than overwrite existing science.
    catalog=ae.read(AE_PATH); register=ae.read(SOURCE_PATH)
    for collection, records in ((catalog['happeningTypes'],record_set),(register['sources'],new_sources)):
        existing={r['id']:r for r in collection}
        for record in records:
            if record['id'] in existing and existing[record['id']]!=record: raise ValueError('Existing record collision '+record['id'])
            if record['id'] not in existing: collection.append(record)
        collection.sort(key=lambda r:r['id'])
    auth=authorization(record_set)
    existing=[r for r in catalog['authorizations'] if r['decisionId']==DECISION]
    if existing and existing!=[auth]: raise ValueError('Existing authorization cannot be silently rewritten')
    if not existing: catalog['authorizations'].append(auth)
    catalog['authorizations'].sort(key=lambda r:r['decisionId'])
    # Validate in memory before writes, including complete source deduplication.
    old_sources=frozen('data/sources.json')['sources']+frozen('data/relationship-intervention-v1/source-register.json')['sources']
    def norm(value): return re.sub(r'[^a-z0-9]','',value.casefold())
    for s in new_sources:
        ri.SchemaSet().validate('source',s)
        for old in old_sources:
            text=json.dumps(old).casefold()
            if s['doi'].casefold() in text or ('pubmed.ncbi.nlm.nih.gov/'+s['pmid']) in text:
                raise ValueError('Duplicate canonical source '+s['id'])
            if norm(s['title']) in norm(old.get('title',old.get('citationText',''))) and str(s['year']) in text:
                raise ValueError('Duplicate title/year '+s['id'])
    write(Path(ROOT/DECISION_PATH),decision_document())
    c=ae.Context.repository(); c.source_ids|={s['id'] for s in new_sources}
    ae.validate_catalog(catalog,c)
    write(AE_PATH,catalog); write(SOURCE_PATH,register)
    write(MARKER,decisions()); write(MANIFEST,source_manifest())
    lineage=[{'candidateId':r['id'].replace('HT-V1-','HT-CAND-'),'candidateRevision':1,
              'candidateHash':ae.digest(next(h for h in frozen('data/candidates/actions-events-v1/SOC-F07/workspace.json')['passB']['happeningTypes'] if h['id']==r['id'].replace('HT-V1-','HT-CAND-'))),
              'canonicalId':r['id'],'canonicalRevision':1,'canonicalHash':ae.digest(r),'governanceDecision':DECISION,
              'identitySourceIds':r['identitySourceIds'],'sameScientificIdentity':True,'effectEvidenceInherited':False} for r in record_set]
    write(AE_PATH.parent/'SOC-F07-materialization-manifest.json',{
        'schemaVersion':'1.0.0','auditId':AUDIT,'baselineCommit':BASELINE,'pilotHeadBeforeGovernance':HEAD,
        'governanceDecisionId':DECISION,'governanceDecisionRecord':DECISION_PATH,'activationAuthorized':False,
        'candidateLineage':lineage,'newGoverned':7,'newInactive':7,'newActive':0,
        'counts':{'happeningTypes':7,'relationships':0,'effectAssertions':0,'evidenceAssessments':0,'sourceFindings':0,'sources':6},
        'blocked':{'REL-CAND-SOC-F07-001':'BLOCKED_PENDING_REPRESENTATION','HT-CAND-SOC-F07-008':'BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT'},
        'existingScientificRecordsChanged':0,'architectureDecisions':'PENDING','productionActiveRelationships':457,'productionActiveCausal':436})
    import build_soc_f07_pilot as pilot
    pilot.build()
    print('SOC-F07: seven GOVERNED/INACTIVE identities; six sources; zero ACTIVE; derivation and HT-008 not materialized.')


if __name__=='__main__': materialize()
