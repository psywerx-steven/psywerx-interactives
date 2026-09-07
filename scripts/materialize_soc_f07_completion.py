"""Exact NS-enabled completion of two previously human-approved SOC objects.

No activation; no rewriting old science or historical governance snapshots.
"""
import copy
import json
import subprocess
from pathlib import Path
import actions_events_v1 as ae
import relationship_intervention_v1 as ri
import relational_state_v1 as ns
import source_verification_v1 as sv
import materialize_soc_f07_governance_001 as prior

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ns.BASELINE
DECISION='GOV-SOC-F07-COMPLETION-2026-09-07'
DECISION_PATH='docs/governance/pilots/SOC-F07/SOC_F07_GOVERNANCE_COMPLETION_002.md'
ARCHITECTURE='GOV-NETWORK-STATE-V1-2026-09-07'
MANIFEST=ROOT/'data/relational-state-v1/SOC-F07-completion-manifest.json'
STAMP='2026-09-07T15:28:00Z'


def frozen(path): return json.loads(subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT))


def source():
    path='docs/governance/source-verification/SRC-559.json'; snapshot=ae.read(ROOT/path)
    m=snapshot['registryMetadata']
    return {'schemaVersion':'1.0.0','id':'SRC-559',
        'citationText':'; '.join(m['authors'])+'. '+m['title']+'. '+m['publication']+'. 2020. doi:'+m['doi']+'.',
        **m,'pmid':None,'url':snapshot['publisherLocator'],
        'verification':{'status':'VERIFIED','system':'AUTHORITATIVE_BIBLIOGRAPHIC','verificationVersion':'1.0.0',
            'verifiedDate':'2026-09-07','identifierChecked':'DOI:'+m['doi'],'method':'DOI_REGISTRY_AND_PUBLISHER_ALIGNMENT',
            'authority':'CROSSREF','registryLocator':snapshot['registryLocator'],'publisherLocator':snapshot['publisherLocator'],
            'verifiedFields':sv.FIELDS,'accessDepth':snapshot['accessDepth'],'conflicts':[],'verificationConfidence':'HIGH',
            'provenance':{'path':path,'contentHash':sv.digest(snapshot),'reviewMethod':snapshot['reviewMethod'],'limitations':snapshot['limitations']}},
        'governanceDecisionRecord':DECISION_PATH,'auditId':prior.AUDIT}


def governance(candidate,identifier):
    g=copy.deepcopy(candidate['governance'])
    for t in g['transitionProvenance']:
        t['objectId']=identifier; t['provenance']+='; exact candidate lineage '+candidate['id']
    g.update(lifecycleStatus='GOVERNED',activationStatus='INACTIVE',decisionOutcome='APPROVED',
        decisionRecord=DECISION_PATH,authorizedBy='authorized human governor',decisionDate='2026-09-07',
        effectiveVersion='SOC-F07-COMPLETION-002',decisionRationale='Prior exact human scientific approval; representation/source gate satisfied. No activation.')
    g['transitionProvenance'].append({'fromState':{'lifecycleStatus':'REVIEW_READY','activationStatus':'NOT_ELIGIBLE'},
        'toState':{'lifecycleStatus':'GOVERNED','activationStatus':'INACTIVE'},'actorClass':'AUTOMATED_PROCESS_OR_AI',
        'rationale':'Exact conditional human approval materialization, no scientific scope expansion','timestamp':STAMP,
        'objectId':identifier,'revision':1,'provenance':candidate['id']+'; '+prior.DECISION+'; '+ARCHITECTURE,
        'governanceDecisionRecord':DECISION_PATH,'exactDecisionMaterialization':True})
    return g


def identity():
    candidate=frozen('data/candidates/actions-events-v1/SOC-F07/workspace.json')['passB']['happeningTypes'][-1]
    assert candidate['id']=='HT-CAND-SOC-F07-008'
    r=copy.deepcopy(candidate); r['id']='HT-V1-SOC-F07-008'
    r['identitySourceIds']=['SRC-559']; r['description']+=prior.IDENTITY_LIMIT
    r['governance']=governance(candidate,r['id']); return r


def binding():
    candidate=frozen('data/candidates/actions-events-v1/SOC-F07/workspace.json')['passA']['relationshipCandidates'][0]
    identifier='DER-V1-SOC-F07-001'
    return {'schemaVersion':'1.0.0','objectKind':'COLLECTION_DERIVATION_BINDING','recordClass':'SCIENTIFIC_RECORD',
        'id':identifier,'revision':1,'targetRds':ns.entity_reference('RDS-0006'),
        'inputContract':{'collectionSubject':'ALL_NODES_OF_BOUND_STATE_BOUNDARY','completenessRule':'EXACT_SET_EQUALITY_NO_MISSING_NO_EXTRA',
            'inputEntity':ns.entity_reference('SOC-049'),'inputMetricVariant':'DEGREE_RAW_UNDIRECTED',
            'alignment':'SAME_STATE_HASH_BOUNDARY_WINDOW_TYPE_LAYER',
            'requiredExternalInputs':['NODE_SET','NETWORK_STATE','BOUNDARY','WINDOW','METRIC_SPECIFICATION','MAXIMUM_BENCHMARK']},
        'metricVariant':'FREEMAN_DEGREE_CENTRALIZATION','normalization':'SAME_SIZE_SIMPLE_UNDIRECTED_STAR_MAXIMUM',
        'calculationReference':'SUM_MAX_DEGREE_MINUS_DEGREES_DIVIDED_BY_N_MINUS_1_TIMES_N_MINUS_2','minimumNodes':3,
        'causalRelationship':False,'evidenceBasis':'DEFINITIONAL_CALCULATIONAL',
        'sourceFindings':[{'id':'SF-DER-V1-SOC-F07-001','sourceId':'SRC255',
            'locator':'Freeman, Centrality in social networks: Conceptual clarification; abstract reviewed in prior SOC pilot, not full-paper formula extraction.',
            'accessDepth':'ABSTRACT','basis':'DEFINITIONAL_CALCULATIONAL',
            'result':'Methodological distinction between node centrality forms and corresponding graph centralization. Complete degree collection/benchmark concept has separate exact human approval.',
            'limitations':['Prior abstract-level access only; no full-paper or empirical effect review claimed.',
                'Only the declared binary, simple, undirected, loopless degree variant. Other centrality/weight/direction variants unsupported.',
                'Mathematical benchmark checked by declared star maximum argument and synthetic calculation, not empirical causal evidence.'],
            'empiricalCausalEvidence':False,'overlap':'SRC-255 is a pilot alias of canonical SRC255. Candidate UCINET documentation not treated as independent replication.'}],
        'scopeLimitations':['Complete aligned values for the exact declared network; never one ego.',
            'No betweenness/eigenvector/closeness centralization from degree.',
            'RDS blocked metadata unchanged; inactive knowledge confers no production execution or direct effect target.'],
        'sharedContributionIdentity':'CONTRIB-SOC-F07-DEGREE-CENTRALIZATION','contributionPolicy':'RECALCULATION_ONLY_NO_CAUSAL_SUM',
        'lineage':{'candidateId':candidate['id'],'candidateRevision':candidate['revision'],'candidateHash':ae.digest(candidate),
                   'scientificDecisionId':prior.DECISION,'architectureDecisionId':ARCHITECTURE},
        'governance':governance(candidate,identifier)}


def authorization(records):
    return {'decisionId':DECISION,'decisionRecord':DECISION_PATH,'actorClass':'AUTHORIZED_HUMAN_GOVERNOR',
        'effectiveDate':'2026-09-07','authorizedObjects':[{'id':r['id'],'revision':r['revision'],'recordHash':ae.digest(r)} for r in records],
        'recordClass':'SCIENTIFIC_RECORD'}


def strip_additions(path, current):
    """Remove only exactly expected completion records; reject any changed addition."""
    result=copy.deepcopy(current)
    if path=='data/actions-events-v1/catalog.json':
        ht=identity(); auth=authorization([ht])
        found=[r for r in result['happeningTypes'] if r['id']==ht['id']]
        if found:
            if found!=[ht]: raise ValueError('Unauthorized HT-008 variation')
            result['happeningTypes']=[r for r in result['happeningTypes'] if r['id']!=ht['id']]
            if [a for a in result['authorizations'] if a['decisionId']==DECISION]!=[auth]: raise ValueError('Completion authorization mismatch')
            result['authorizations']=[a for a in result['authorizations'] if a['decisionId']!=DECISION]
    elif path=='data/relationship-intervention-v1/source-register.json':
        expected=source(); found=[r for r in result['sources'] if r['id']==expected['id']]
        if found:
            if found!=[expected]: raise ValueError('Unauthorized SRC-559 variation')
            result['sources']=[r for r in result['sources'] if r['id']!=expected['id']]
    return result


def source_schema_extension_only(old,new):
    candidate=copy.deepcopy(new); v=candidate['properties']['verification']
    extension=copy.deepcopy(sv.SCHEMA); extension.pop('$schema'); extension.pop('$id')
    if v!={'oneOf':[old['properties']['verification'],extension]}: return False
    candidate['properties']['verification']=old['properties']['verification']
    return candidate==old


def write(path,value):
    allowed={prior.AE_PATH,prior.SOURCE_PATH,ns.CATALOG,MANIFEST}
    if path not in allowed: raise ValueError('Outside exact conditional materialization scope')
    path.parent.mkdir(parents=True,exist_ok=True)
    # Preserve existing key order and all old records; additions are deterministic.
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def materialize():
    ht=identity(); derived=binding(); src=source()
    ri.SchemaSet().validate('source',src); sv.validate_source(src)
    old=frozen('data/sources.json')['sources']+frozen('data/relationship-intervention-v1/source-register.json')['sources']
    text=json.dumps(old).casefold()
    if src['doi'] in text or '10.48550/arxiv.1905.02762' in text: raise ValueError('Canonical work already exists; reconcile rather than remint')
    norm=lambda x: ''.join(c for c in x.casefold() if c.isalnum())
    if any(norm(src['title']) in norm(r.get('title',r.get('citationText',''))) for r in old): raise ValueError('Duplicate title')
    catalog=ae.read(prior.AE_PATH); register=ae.read(prior.SOURCE_PATH)
    derivations=ae.read(ns.CATALOG) if ns.CATALOG.exists() else {'schemaVersion':'1.0.0','bindings':[],'authorizations':[]}
    for values, additions, key in [(catalog['happeningTypes'],[ht],'id'),(register['sources'],[src],'id'),
            (catalog['authorizations'],[authorization([ht])],'decisionId'),(derivations['bindings'],[derived],'id'),
            (derivations['authorizations'],[authorization([derived])],'decisionId')]:
        for addition in additions:
            matches=[r for r in values if r[key]==addition[key]]
            if matches and matches!=[addition]: raise ValueError('Existing canonical collision '+addition[key])
            if not matches: values.append(addition)
    context=ae.Context.repository(); context.source_ids.add(src['id'])
    ae.validate_catalog(catalog,context); ns.validate_binding(derived,derivations['authorizations'],context)
    # Exact runtime collection gate demonstrated before scientific writes.
    import relational_state_fixtures as fixtures
    state=fixtures.state(); request=fixtures.request(state,'FREEMAN_DEGREE_CENTRALIZATION',derived)
    assert ns.calculate(request,state,derived,derivations['authorizations'])['status']=='CALCULATED_SYNTHETIC'
    bad=copy.deepcopy(request); bad['collection']['values']=bad['collection']['values'][:1]
    assert ns.calculate(bad,state,derived,derivations['authorizations'])['status']=='UNSUPPORTED_OR_INCOMPLETE'
    write(prior.AE_PATH,catalog); write(prior.SOURCE_PATH,register); write(ns.CATALOG,derivations)
    write(MANIFEST,{'schemaVersion':'1.0.0','baselineCommit':BASELINE,'decisionId':DECISION,'priorScientificDecision':prior.DECISION,
        'architectureDecision':ARCHITECTURE,'activationAuthorized':False,'newGoverned':2,'newInactive':2,'newActive':0,
        'records':[{'id':r['id'],'revision':r['revision'],'contentHash':ae.digest(r)} for r in [ht,derived]],
        'candidateLineage':{'HT-CAND-SOC-F07-008':ht['id'],'REL-CAND-SOC-F07-001':derived['id']},
        'sourceMapping':{'SRC-CAND-SOC-F07-010':'SRC-559','SRC-255':'SRC255'},
        'sourceHash':ae.digest(src),'sourceFindingCount':1,'separateEvidenceAssessmentCount':0,
        'sourceFindingPurpose':'Internal definitional finding, no empirical causal evidence or separate activation',
        'scientificTargetGapsResolved':0,'existingRelationshipsChanged':0,'activeRelationships':457,'activeCausal':436})
    print('Conditional SOC completion: HT-008 and collection binding GOVERNED/INACTIVE; SRC-559; ACTIVE additions 0')


if __name__=='__main__': materialize()
