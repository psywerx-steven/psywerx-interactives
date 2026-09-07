"""Deterministic SOC-F07 candidate audit renderer. Never writes production science.

Scientific judgments are explicit inputs, not graph-derived discoveries. This does
not execute network simulations, make human decisions, register sources or activate.
"""
import copy
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import actions_events_v1 as ae
import audit_family as af
import relationship_intervention_v1 as ri
import soc_f07_research_inputs as inp

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/candidates/actions-events-v1/SOC-F07'
DOCS = ROOT / 'docs/governance/pilots/SOC-F07'
BASE = ROOT / 'reports/actions-events-v1/SOC-F07-pilot-baseline'
DECISION = 'PENDING — APPROVE / MODIFY / REJECT'
NETWORK_LIMIT = ('Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, '
                 'window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. '
                 'Changing any of these can change a statistic without the claimed real-world mechanism.')
IDENTIFICATION = ('Check reflection, homophily, selection into ties, latent traits, common environment, '
                  'institutional assignment, simultaneity, reciprocity, correlated exposure, interference, '
                  'endogenous formation, attrition and tie measurement error; longitudinal observation alone is not identification.')


def encode(v):
    return json.dumps(v, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def emit(path, value):
    p = path.resolve()
    if not any(p.is_relative_to(d.resolve()) for d in (DOCS, STORE)):
        raise ValueError('SOC-F07 renderer output outside its candidate/docs directories')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value.rstrip() + '\n' if isinstance(value, str) else encode(value), encoding='utf-8', newline='\n')


def provenance():
    return {'actorClass': 'AUTOMATED_PROCESS_OR_AI', 'method': 'Structured evidence search and skeptical candidate audit',
            'recordedAt': inp.STAMP, 'originReferences': [inp.AUDIT, inp.BASELINE, 'scripts/soc_f07_research_inputs.py'],
            'limitations': ['Selected accessed sections, not an exhaustive systematic review; no human scientific decision']}


def governance(identifier, status='RESEARCH_NEEDED', blocked=False):
    before = {'lifecycleStatus': None, 'activationStatus': 'NOT_ELIGIBLE'}
    transitions = []
    states = ['CANDIDATE'] + (['RESEARCH_NEEDED'] if status != 'CANDIDATE' else []) + (['REVIEW_READY'] if status == 'REVIEW_READY' else [])
    for state in states:
        after = {'lifecycleStatus': state, 'activationStatus': 'NOT_ELIGIBLE'}
        transitions.append({'fromState': before, 'toState': after, 'actorClass': 'AUTOMATED_PROCESS_OR_AI',
            'rationale': 'Candidate preparation only; uncertainty and target gaps preserved', 'timestamp': inp.STAMP,
            'objectId': identifier, 'revision': 1, 'provenance': inp.AUDIT, 'governanceDecisionRecord': None,
            'exactDecisionMaterialization': False})
        before = after
    return {'lifecycleStatus': status, 'activationStatus': 'NOT_ELIGIBLE',
            'blockStatus': 'NEEDS_GOVERNANCE_INPUT' if blocked else 'NONE', 'decisionOutcome': 'NOT_DECIDED',
            'authorityBasis': 'V1_NATIVE', 'decisionRecord': None, 'authorizedBy': None, 'decisionDate': None,
            'effectiveVersion': None, 'decisionRationale': None, 'supersedesIds': [], 'transitionProvenance': transitions}


def base(identifier, status='RESEARCH_NEEDED'):
    return {'schemaVersion': '1.0.0', 'id': identifier, 'revision': 1, 'recordClass': 'SCIENTIFIC_RECORD',
            'provenance': provenance(), 'governance': governance(identifier, status)}


def source_registry():
    existing = ae.read(ROOT / 'data/sources.json')['sources'] + ae.read(ROOT / 'data/relationship-intervention-v1/source-register.json')['sources']
    result, keys = [], {}
    for row in inp.SOURCES:
        key, title, authors, year, venue, doi, url, access, basis, locator, population, finding, limit = row
        matches = []
        for old in existing:
            text = json.dumps(old, ensure_ascii=False).casefold()
            if (doi and doi.casefold() in text) or (len(title) > 20 and title.casefold() in text):
                matches.append(old['id'])
        identifier = key if key.startswith('SRC-') else sorted(matches)[0] if matches else 'SRC-CAND-SOC-F07-' + key
        keys[key] = identifier
        result.append({'id': identifier, 'researchKey': key, 'title': title, 'authors': authors, 'year': year,
            'venue': venue, 'doi': doi, 'url': url, 'accessDepth': access, 'locator': locator, 'basis': basis,
            'populationNetwork': population, 'findingSummary': finding, 'limitations': limit,
            'accessedLocalDate': '2026-09-06', 'accessedUtcDates': ['2026-09-07'],
            'networkDesign': inp.SOURCE_DESIGNS.get(key, {k:'NOT_EXTRACTED; see stated source access and scope' for k in ('nodes','ties','boundary','exposure','comparator','outcome','timing','identification','confounds','limitations')}),
            'sourceType': 'MAINTAINER_DOCUMENTATION' if key == '018' else 'PREPRINT' if key == '010' else 'REPORT' if key in {'SRC-497','SRC-505'} else 'COMPOSITE_REFERENCE' if key == 'SRC-509' else 'JOURNAL_ARTICLE',
            'verification': 'LINKED_COMPONENT_ONLY' if key == 'SRC-509' else 'IDENTITY_AND_STATED_ACCESS_VERIFIED',
            'deduplication': {'canonicalMatches': sorted(set(matches + ([key] if key.startswith('SRC-') else []))),
                'outcome': 'REUSE_CANONICAL' if identifier.startswith('SRC-') and not identifier.startswith('SRC-CAND') else 'CANDIDATE_ONLY',
                'method': 'Complete canonical registries: DOI, exact title and manual linked-identifier reconciliation'},
            'overlap': 'SRC-509 linked PMID duplicates SRC-235; unresolved composite component is not an independent study.' if key in {'SRC-235','SRC-509'} else 'Review/primary overlap recorded per finding; preprint/journal versions are one work.',
            'supportedCandidateIds': []})
    return result, keys


def finding(source, assertion, disposition='INSUFFICIENT', interpretation=None):
    fid = 'FND-SOC-F07-' + assertion + '-' + source['researchKey']
    out = {'id': fid, 'sourceId': source['id'], 'locator': source['locator'] + '; ' + source['url'],
           'accessDepth': source['accessDepth'], 'population': source['populationNetwork'], 'context': NETWORK_LIMIT,
           'basis': [source['basis']], 'supportedSemantics': ['DERIVATIONAL'] if source['basis'] == 'DEFINITIONAL_CALCULATIONAL' else [],
           'inputRole': 'DIRECT_FINDING', 'design': source['basis'] + '; ' + source['populationNetwork'],
           'exposure': source['populationNetwork'], 'comparator': 'Source-specific comparison; see result/locator. No synthetic common comparator imposed.',
           'measurement': source['findingSummary'], 'timing': 'Reported source window only; no causal lag/persistence inferred. ' + source['populationNetwork'],
           'result': interpretation or source['findingSummary'], 'disposition': disposition, 'quantitativeEstimate': None,
           'uncertainty': ['No comparable exact-ontology coefficient or numeric confidence extracted'],
           'limitations': [source['limitations'], NETWORK_LIMIT, IDENTIFICATION],
           'datasetIds': ['STUDY-CENTOLA-2010' if source['researchKey'] in {'SRC-235','SRC-509'} else 'STUDY-' + source['id']],
           'overlapNotes': 'Reviews SRC-254/256/269 and candidate 009 may include cited primary studies: no independent-replication count. ' + source['overlap'],
           'nullInterpretation': None, 'provenance': provenance()}
    if source['researchKey'] in inp.SOURCE_DESIGNS:
        design=source['networkDesign']
        out.update(exposure=design['exposure'],comparator=design['comparator'],measurement=design['outcome'],timing=design['timing'],
                   context=design['boundary']+'; '+design['ties'],design=source['basis']+'; '+design['identification'])
        out['limitations'] += [design['confounds'],design['limitations']]
    if source['accessDepth']=='METADATA':
        out['basis']=['UNTESTED_HYPOTHESIS']
        out['supportedSemantics']=[]
        out['design']='Metadata alignment assessment only; no empirical design or direct scientific result inferred'
    if disposition == 'NULL_FINDING':
        out['nullInterpretation'] = {'contrast': interpretation or source['findingSummary'],
            'precisionAssessment': 'No equivalence bounds or precision-based zero-effect inference extracted',
            'interpretation': 'NO_DETECTED_DIFFERENCE', 'rationale': 'Nonsignificance is not evidence of zero or equivalence'}
    return out


def synthesis(fs, reason, ready=False):
    return {'sourceFindingIds': [f['id'] for f in fs], 'disposition': 'SUPPORTS' if ready else 'INSUFFICIENT',
            'evidenceStrength': 'MODERATE' if ready else 'LIMITED', 'confidence': 'MODERATE' if ready else 'LOW',
            'rationale': reason, 'confidenceRationale': 'Judgment concerns the exact scoped proposition, not the prestige of a source.',
            'conflicts': [{'findingId': f['id'], 'dispositionRationale': 'Preserved source-level mixed/null/contrary result; not a zero-effect claim'}
                          for f in fs if f['disposition'] in {'MIXED','NULL_FINDING','CONTRADICTED'}],
            'contraryEvidenceSearch': 'ASSESSED', 'generalizationLimits': [NETWORK_LIMIT, IDENTIFICATION],
            'datasetOverlap': 'Same publication reused across assertions is one dataset; review/primary overlap not counted as independent replication.'}


def ri_evidence(identifier, assertion, fs, reason, scope, ready=False):
    syn = synthesis(fs, reason, ready)
    g = governance(identifier, 'REVIEW_READY' if ready else 'RESEARCH_NEEDED')
    ev = {'schemaVersion': '1.0.0', 'id': identifier, 'revision': 1,
          'assertion': {'objectType': 'RELATIONSHIP', 'objectId': assertion}, 'sourceIds': sorted({f['sourceId'] for f in fs}),
          'evidenceRationale': reason, 'evidenceStrength': syn['evidenceStrength'], 'confidence': syn['confidence'],
          'evidenceDisposition': syn['disposition'], 'population': scope, 'context': NETWORK_LIMIT,
          'studyDesignCharacterizations': [{'designType': 'OTHER_SPECIFIED', 'specification': f['design']} for f in fs],
          'quantitativeEstimate': None, 'uncertainty': ['No graph weight; no numeric causal estimate invented'],
          'conflictingEvidence': {'sourceIds': sorted({f['sourceId'] for f in fs if f['disposition'] in {'MIXED','NULL_FINDING','CONTRADICTED'}}), 'summary': reason},
          'limitations': sorted({x for f in fs for x in f['limitations']}),
          'reviewProvenance': {'createdAt': inp.STAMP, 'createdByActorClass': 'AUTOMATED_PROCESS_OR_AI',
                              'reviewedAt': None, 'reviewedBy': None, 'sourceSchema': 'RI_V1_WITH_AE_SOURCE_FINDING_CANDIDATE_SIDECAR'},
          'governance': g}
    return ev, {'evidenceAssessmentId': identifier, 'assertionId': assertion, 'productionMethod': 'SYNTHESIS',
                'sourceFindings': fs, 'synthesis': syn, 'governance': g,
                'note': 'Candidate normalization sidecar; production AE assertion target enum is unchanged.'}


def derivation_candidate(c, sources):
    identifier = 'REL-CAND-SOC-F07-001'
    r = dict.fromkeys(ae.read(ROOT/'schemas/relationship-intervention/v1/relationship-v1.schema.json')['required'])
    scope = ('Only Freeman degree-based network centralization for a specified binary network: the complete aligned '
             'distribution of SOC-049 node degrees, plus node set, normalization and maximum-possible benchmark. '
             'Not a single ego value; not betweenness-, eigenvector- or closeness-based centralization; external inputs remain required.')
    r.update(schemaVersion='1.0.0', id=identifier, revision=1, relationFamily='DERIVATIONAL', predicate='DERIVED_FROM',
             symmetry='DIRECTED', causalClaim=False, sourceEntityId='RDS-0006', targetEntityId='SOC-049',
             sourceEntityType=c.entities['RDS-0006']['entityType'], targetEntityType=c.entities['SOC-049']['entityType'],
             mechanism='Calculation dependency, not causal force: compare the complete degree distribution with its specified maximum benchmark.',
             boundaryConditions=scope, applicability={'analyticUnit':'Whole bounded network and all node degree values', 'populationOrSystem':scope, 'context':scope},
             moderatorSpecifications=[], sourceIds=[sources[k]['id'] for k in ['SRC-255','018']],
             evidenceAssessmentIds=['EVA-' + identifier], governance=governance(identifier,'REVIEW_READY'),
             compatibility={'sourceSchema':'RELATIONSHIP_V1','authorityStatus':'V1_LIFECYCLE','migrationCompleteness':'INCOMPLETE',
                 'v1Executability':'NOT_EXECUTABLE','blockedFields':['humanScientificGovernance','activation','selectedOperationalization'],
                 'legacyRelationFamily':None,'legacyScientificFields':None,'legacyRecordHash':None,'legacyRecord':None})
    fs = [finding(sources[k],identifier,'SUPPORTS') for k in ['SRC-255','018']]
    ev, side = ri_evidence('EVA-'+identifier,identifier,fs,scope,scope,True)
    return r, ev, side


def happening(spec, sources):
    n, name, origins, deliberate, domains, skeys, desc, risk = spec
    identifier = 'HT-CAND-SOC-F07-' + n
    role = 'ROLE-AUTHORIZED-NETWORK-PROTOCOL-OPERATOR' if deliberate else 'SYSTEM-STORM-AND-INSTITUTIONAL-RESPONSE'
    return {**base(identifier,'REVIEW_READY'), 'name':name,'aliases':[], 'identityKey':'SOC-F07-'+n,
            'description':desc + ' Identity only: no efficacy, permission or activation implied.',
            'kindTags':['ACTION'] if deliberate else ['EVENT','EXPOSURE'], 'domainTags':domains, 'originLayers':origins,
            'interventionSubset':deliberate, 'packageKind':'ATOMIC','components':[],'componentEnumeration':'NOT_APPLICABLE',
            'actorOrSourceSystem':role,'intentionality':'DELIBERATE' if deliberate else 'UNINTENDED',
            'controlProfiles':[{'actorId':role,'extent':'PARTIAL' if deliberate else 'NONE','capabilities':['INITIATE','TUNE'] if deliberate else [],
                'population':risk,'context':desc,'conditions':'Proposed role only. Prerequisites, feasibility, consent, privacy, legal/ethical/risk and applicability checks NOT_ASSESSED.',
                'provenance':provenance()}], 'pattern':['DISCRETE'],
            'identityDefiningProfile':{k:None for k in ('timing','doseIntensity','duration','frequency','reach')},
            'identitySourceIds':[sources[k]['id'] for k in skeys]}


def effect(n, htn, sources, skeys, reason, source_dispositions):
    identifier = 'EA-CAND-SOC-F07-' + n
    eid = 'EVA-AE-CAND-SOC-F07-' + n
    fs = [finding(sources[k],identifier,source_dispositions.get(k,'INSUFFICIENT')) for k in skeys]
    if n == '001':
        fs.append(finding(sources['005'],identifier+'-CONTROL','NULL_FINDING',
                          'The source reports no detected difference between control configurations; this does not establish equivalence or a general zero closure effect.'))
    syn = synthesis(fs,reason)
    scope = {'population':sources[skeys[0]]['populationNetwork'], 'context':reason, 'boundaryConditions':NETWORK_LIMIT,
             'timing':'Source-specific tie formation window; baseline open-triad risk set and censoring require exact alignment',
             'measurement':'SOC-102 conditional open-triad closure hazard/rate, not snapshot transitivity, all friendship incidence or raw triangle count; mapping unresolved'}
    e = {**base(identifier), 'typeId':'HT-CAND-SOC-F07-'+htn,'occurrenceId':None,'targetKind':'DRIVER','targetId':'SOC-102',
         'targetLayers':['SOC'],'claimSemantics':'CAUSAL','productionMethod':'HYPOTHESIS','property':'LEVEL','change':'UNKNOWN',
         'otherSpecified':None,'intendedChange':None,'observedChange':None,'knowledgeStatus':'INSUFFICIENT_EVIDENCE',
         'scope':scope,'exposureProfile':{k:None for k in ('timing','doseIntensity','duration','frequency','reach')},
         'mechanism':reason,'mechanismStatus':'PARTIAL','mechanisticDriverIds':[],
         'grounding':{'causalIdentificationRationale':'Exact SOC-102 effect remains unresolved despite source-specific design leverage',
                      'derivationEntailed':'NO','representedDriverId':None,'duplicatePropagationControl':None},
         'contribution':{'groupId':'CONTRIB-SOC-F07-'+htn,'role':'PRIMARY','relatedAssertionIds':[],'reconciliation':None},
         'moderatorLinks':[],'interaction':{'mode':'NONE','otherEffectIds':[],'evidenceAssessmentIds':[]},
         'qualifiers':{'reach':None,'distribution':None,'subgroups':[],
             'unintendedConsequences':['Selection/exclusion, privacy intrusion, stigma, coercion and unequal contact opportunities require review'],
             'risks':[reason],'prerequisites':['Exact risk set and protocol; voluntary participation; independently assessed control, feasibility, legal, ethical and applicability conditions'],
             'evaluation':{'valence':'NOT_EVALUATED','stakeholder':None,'criterion':None}},
         'outcomes':[],'evidenceAssessmentIds':[eid],'uncertainty':[reason,IDENTIFICATION], 'inferenceProvenance':None}
    ev = {**base(eid), 'assertion':{'objectType':'EFFECT_ASSERTION','objectId':identifier},'sourceFindings':fs,'synthesis':syn,
          'completeness':{k:('MISSING' if k in {'direction','measurement'} else 'SPECIFIED') for k in ('target','direction','mechanism','population','context','timing','measurement','boundaries')}}
    return e, ev


def protected():
    roots = ['data','schemas','_migration_handoff_v0.3','scenario-service','docs/governance/pilots/BIO-F01','docs/governance/pilots/INF-F03']
    paths = subprocess.check_output(['git','ls-tree','-r','--name-only',inp.BASELINE,'--',*roots],cwd=ROOT).decode().splitlines()
    report = {}
    for p in paths:
        original = subprocess.check_output(['git','show',inp.BASELINE+':'+p],cwd=ROOT).replace(b'\r\n',b'\n')
        current = (ROOT/p).read_bytes().replace(b'\r\n',b'\n')
        report[p] = {'baselineSha256':hashlib.sha256(original).hexdigest(),'currentSha256':hashlib.sha256(current).hexdigest(),'unchanged':original==current}
    return {'baseline':inp.BASELINE,'comparison':'LF_NORMALIZED_BYTES; Git checkout CRLF is not scientific modification',
            'passed':all(x['unchanged'] for x in report.values()),'filesCompared':len(report),'files':report}


def table(headers, rows):
    clean = lambda x: str(x).replace('|','/').replace('\n',' ')
    return '\n|'+' | '.join(headers)+' |\n|'+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(clean(x) for x in r)+' |\n' for r in rows)


def build():
    registry, keys = source_registry()
    sources = {s['researchKey']:s for s in registry}
    orig = ae.Context.repository()
    c = ae.Context(orig.entities,orig.relationships,orig.source_ids | {s['id'] for s in registry})
    frozen = ae.read(BASE/'SOC-F07_baseline.json')
    membership = set(frozen['family']['memberIds'])
    if membership != {e['id'] for e in c.entities.values() if e['primaryFamilyId']=='SOC-F07'}:
        raise ValueError('Production Family membership drift')
    legacy = ae.read(ROOT/'data/relationships.json')
    incident = [(bucket,r) for bucket in ('relationships','deprecatedRelationships','relationshipCandidates') for r in legacy[bucket]
                if r.get('subjectEntityId') in membership or r.get('objectEntityId') in membership]
    if {r['id'] for _,r in incident} != set(inp.EXISTING):
        raise ValueError('Every incident record requires an explicit disposition')
    w = ae.empty_workspace('SOC-F07',inp.BASELINE)
    w['readiness'] = {k:True for k in w['readiness']}
    audits, revisions, sidecars = [], [], []
    for bucket, row in incident:
        disp, proposal, skeys, risk = inp.EXISTING[row['id']]
        causal = row['relationFamily']=='CAUSAL'
        fs = [finding(sources[k],row['id']) for k in skeys]
        if row['id']=='REL-SOC-035':
            fs[0]['disposition']='MIXED'
            fs[0]['result']='Assigned clustered topology supports redundant adoption exposure in a bounded experiment; exact independence/metric correspondence to SOC-061 remains limited.'
            fs.append(finding(sources['SRC-235'],row['id']+'-MARGINAL','NULL_FINDING','Fourth and further notifications had no detected additional adoption effect in the reported small contrast; not proof of a zero effect on SOC-061.'))
        if row['id']=='REL-TEC-050':
            fs[-1]['disposition']='MIXED'
            fs.append(finding(sources['015'],row['id']+'-OTHER-OUTCOMES','NULL_FINDING','No detected effects on some partisanship/affective-polarization outcomes in the feed experiment; these are not the network-segregation endpoint.'))
        owner=af.ownership(row['subjectEntityId'],row['objectEntityId'], 'CAUSAL' if causal else 'SEMANTIC',c.entities)
        endpoints=[row['subjectEntityId'],row['objectEntityId']]
        audit={'id':row['id'],'bucket':bucket,'primaryDisposition':disp,'currentRecord':row,
               'currentV1Projection':ri.project_v3_relationship(row) if bucket=='relationships' else None,
               'proposedReview':proposal,'evidenceRationale':risk,'sources':[keys[k] for k in skeys],
               'ownerFamilyId':owner,'consultedFamilyIds':sorted({c.entities[x]['primaryFamilyId'] for x in endpoints}-{owner}),
               'consultationStatus':'REVIEW_CANDIDATE_ONLY; no consultation represented as completed',
               'governanceDecision':DECISION,'evidenceStrength':'LIMITED' if causal else 'MODERATE','confidence':'LOW' if causal else 'MODERATE',
               'rdsGate':ri.expected_causal_review_gate(row['subjectEntityType'],row['objectEntityType']) if causal else None,
               'fieldReview':{k:{'recordedValue':v,'assessment':'Absent/unspecified: do not infer' if v in (None,[],'UNSPECIFIED','NOT_SPECIFIED') else 'Preserved; exact interpretation qualified by proposedReview/evidenceRationale'} for k,v in row.items()},
               'networkBoundary':NETWORK_LIMIT,'identification':IDENTIFICATION,'temporalIndependence':'NOT_ESTABLISHED' if causal else 'NOT_APPLICABLE',
               'mechanisticIndependence':'PLAUSIBLE_BUT_EXACT_MAPPING_UNRESOLVED' if row['id']=='REL-SOC-035' else 'NOT_ESTABLISHED' if causal else 'NOT_APPLICABLE',
               'sharedInputRisk':'PRESENT: same adjacency/mixing inputs' if row['id'] in {'REL-SOC-031','REL-SOC-032','REL-SOC-033','REL-SOC-034'} else 'ASSESS_SPECIFIED_NETWORK_AND_OUTCOME',
               'v1Executable':False,'currentAuthorityPreserved':True}
        audits.append(audit)
        if causal:
            ev, side=ri_evidence('EVA-AUD-SOC-F07-'+row['id'],row['id'],fs,proposal+' '+risk,row.get('generalizabilityContext'))
            w['passA']['evidence'].append(ev); sidecars.append(side)
        if disp in {'REVISION_CANDIDATE','RETYPE_CANDIDATE'}:
            rid='REV-CAND-SOC-F07-'+row['id']
            revisions.append({'id':rid,'recordClass':'NON_GOVERNED_REVISION_PROPOSAL','currentRecord':row,'currentRecordHash':ae.digest(row),
                'primaryDisposition':disp,'exactProposal':proposal,'fieldChanges':{
                    'endpoints':'Retain IDs for review; any replacement endpoint requires separate human decision',
                    'relationFamily':'Retype alternative only; replacement predicate unresolved' if disp=='RETYPE_CANDIDATE' else 'CAUSAL remains a research hypothesis, not a revised authoritative edge',
                    'polarity':'No new universal polarity approved','mechanism':proposal,'populationContext':NETWORK_LIMIT,
                    'lagPersistenceFunctionalForm':'No numeric or mechanistic values manufactured','sources':'Candidate assessment '+ 'EVA-AUD-SOC-F07-'+row['id']},
                'rdsSafeguards':risk,'unresolved':risk,'identityPolicy':'A family/predicate/endpoint change ultimately needs a new proposition ID; scope-only revision identity needs later human adjudication.',
                'governance':governance(rid),'governanceDecision':DECISION})
        w['passA']['existingDispositions'].append({'id':'AUD-'+row['id'],'questionOrDisposition':disp,'ownerFamilyId':owner,
            'consultedFamilyIds':audit['consultedFamilyIds'],'recordIds':[row['id']],'rationale':proposal+' '+risk,
            'status':'REVIEW_READY' if disp=='RETAIN_AS_IS' else 'RESEARCH_NEEDED'})
    rel, ev, side=derivation_candidate(c,sources)
    w['passA']['relationshipCandidates'].append(rel); w['passA']['evidence'].append(ev); sidecars.append(side)
    w['passA']['ownership'].append({'id':'OWN-'+rel['id'],'questionOrDisposition':rel['boundaryConditions'],
        'ownerFamilyId':'SOC-F07','consultedFamilyIds':[],'recordIds':[rel['id']],'rationale':'Derived-state Family owns dependency; one conditional scientific proposition, no V3 duplicate','status':'REVIEW_READY'})
    hypotheses=[]
    for hid,claim,semantic,status,reason,skeys,endpoints in inp.HYPOTHESES:
        families=sorted({c.entities[x]['primaryFamilyId'] for x in endpoints})
        h={'id':'HYP-SOC-F07-'+hid,'shortId':hid,'proposition':claim,'semanticTriage':semantic,'disposition':status,
           'reason':reason,'sourceIds':[keys[k] for k in skeys],'endpointIds':endpoints,'ownerFamilyId':c.entities[endpoints[0]]['primaryFamilyId'] if endpoints else 'SOC-F07',
           'consultedFamilyIds':families,'sharedIssueId':'ISSUE-SOC-F07-'+hid,'humanDecision':DECISION,
           'regenerationRule':'Require new evidence/operationalization and explicit superseding review; never silently regenerate rejected category error',
           'duplicateCheck':'Compared complete legacy/native/candidate IDs and endpoint semantics; existing-edge questions stay on their review paths'}
        hypotheses.append(h)
        item={'id':h['id'],'questionOrDisposition':claim,'ownerFamilyId':h['ownerFamilyId'],'consultedFamilyIds':families,
              'recordIds':[rel['id']] if hid=='H08' else [],'rationale':reason,'status':'REJECTED_HYPOTHESIS' if status=='REJECTED' else status}
        w['passA']['gapQuestions'].append(item)
        if status in {'RESEARCH_NEEDED','BLOCKED_NEEDS_GOVERNANCE_INPUT'}: w['passA']['unresolved'].append(item)
    for spec in inp.ACTIONS: w['passB']['happeningTypes'].append(happening(spec,sources))
    effect_specs=[('001','001',['005'],inp.ACTIONS[0][-1],{'005':'MIXED'}),
                  ('002','002',['006','017'],inp.ACTIONS[1][-1],{'006':'MIXED','017':'INSUFFICIENT'}),
                  ('003','006',['011'],inp.ACTIONS[5][-1],{'011':'MIXED'})]
    for args in effect_specs:
        e,ev=effect(args[0],args[1],sources,*args[2:]); w['passB']['effectAssertions'].append(e); w['passB']['evidenceAssessments'].append(ev)
    findings=[f for s in sidecars for f in s['sourceFindings']]+[f for e in w['passB']['evidenceAssessments'] for f in e['sourceFindings']]
    for f in findings: ae.schema_set().validate('source-finding',f)
    ae.validate_workspace(w,c)
    for s in registry:
        s['supportedCandidateIds']=sorted({side['assertionId'] for side in sidecars if any(f['sourceId']==s['id'] for f in side['sourceFindings'])} |
            {r['id'] for r in w['passB']['happeningTypes'] if s['id'] in r['identitySourceIds']} |
            {e['assertion']['objectId'] for e in w['passB']['evidenceAssessments'] if any(f['sourceId']==s['id'] for f in e['sourceFindings'])})
    report=protected()
    if not report['passed']: raise ValueError('Protected pre-existing scientific content changed')
    entity_reviews, gaps, antecedents=entities_review(frozen,audits,w)
    search=search_ledgers(w,audits,keys)
    counts=counts_report(w,audits,registry,findings,hypotheses,revisions,gaps)
    manifest={'auditId':inp.AUDIT,'baselineCommit':inp.BASELINE,'branch':inp.BRANCH,'recordClass':'NON_GOVERNED_PILOT_AUDIT',
              'frozenFamily':frozen['family'],'counts':counts,'protectedScience':{'passed':report['passed'],'filesCompared':report['filesCompared']},
              'sourceRegisterVersion':ae.digest(ae.read(ROOT/'data/sources.json')),'riSourceRegisterVersion':ae.digest(ae.read(ROOT/'data/relationship-intervention-v1/source-register.json')),
              'schemaHashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in sorted((ROOT/'schemas').rglob('*.json'))},
              'derivationVersions':{e['id']:{'recordHash':ae.digest(e),'namedVersion':e.get('derivationVersion'),'missingVersionNotInvented':True} for e in frozen['entities'] if e['entityType']!='DRIVER'},
              'newGoverned':0,'newActive':0,'approval':DECISION,'scientificReadiness':'CANDIDATE_REVIEW_ONLY; no activatable yield promised',
              'sourceAccessLimitations':['Direct PMC opens sometimes challenged; indexed selected sections used and locators recorded','Abstract/metadata sources cannot support narrower uninspected empirical claims'],
              'selfReview':['Removed speculative causal edge production: H05 remains a question, not a causal record','All three Driver effects downgraded to RESEARCH_NEEDED for exact risk-set/metric alignment','No STRUCTURE EffectAssertion targets a calculated network metric','No formal moderation/pathway without exact edge and transmitted-effect evidence']}
    products={'workspace.json':w,'source-registry.json':registry,'source-findings.json':sidecars,'existing-relationship-audit.json':audits,
              'revision-proposals.json':revisions,'hypotheses.json':hypotheses,'entity-rds-review.json':entity_reviews,
              'ontology-target-gaps.json':gaps,'rds-antecedent-ledger.json':antecedents,'search-ledger.json':search,
              'protected-science.json':report,'source-registration-queue.json':[
                  {'sourceId':s['id'],'canonicalRegistration':'NOT_AUTHORIZED','supportedCandidateIds':s['supportedCandidateIds'],
                   'condition':'Only after later human approval and fresh exact bibliographic/source alignment verification','possibleCanonicalMatches':s['deduplication']['canonicalMatches']}
                  for s in registry if s['id'].startswith('SRC-CAND') and s['supportedCandidateIds']]}
    for name,obj in products.items(): emit(STORE/name,obj)
    manifest['artifactHashes']={name:hashlib.sha256(encode(value).encode()).hexdigest() for name,value in products.items()}
    emit(DOCS/'SOC_F07_AUDIT_MANIFEST.json',manifest)
    render_docs(manifest,registry,audits,revisions,hypotheses,entity_reviews,gaps,antecedents,search,w,findings)
    return manifest


def entities_review(frozen,audits,w):
    reviews=[]; antecedents=[]; gaps=[]
    sensitivity=['networkBoundary','nodeSet','tieDefinition','tieThreshold','observationWindow','missingTies','directedness','weighting','multiplexCollapse','isolateExclusion','sampleVsWholeNetwork']
    for e in sorted(frozen['entities'],key=lambda x:x['id']):
        eid=e['id']; isrds=e['entityType']!='DRIVER'; note=inp.RDS_NOTES.get(eid)
        fields=e.get('blockedFields',e.get('metadataGovernance',{}).get('blockedFields',[]))
        # Metadata schema may store exact paths in fieldGovernance; retain full record regardless.
        nulls=[k for k in ('mechanism','modifiability','volatility','timeScaleOfChange','onsetCausalLag','persistenceRecovery','measurementAssessmentMethods','observability','evidenceStrength','evidenceNotes','keySources') if e.get(k) in (None,[])]
        related=[a['id'] for a in audits if eid in (a['currentRecord']['subjectEntityId'],a['currentRecord']['objectEntityId'])]
        outgoing=[a['id'] for a in audits if a['currentRecord']['subjectEntityId']==eid and a['currentRecord']['relationFamily']=='CAUSAL']
        review={'id':eid,'currentRecord':e,'currentRecordHash':ae.digest(e),'fieldReview':{k:{'value':v,'assessment':'Missing/blocked; preserved' if v in (None,[]) else 'Canonical statement preserved; not independently endorsed'} for k,v in e.items()},
                'blockedOrMissingFields':nulls,'explicitBlockedFields':fields,'relatedRelationships':related,'outgoingCausalRelationships':outgoing,
                'scientificAuditCanProceed':True,'targetability':'FORBIDDEN_DIRECT_RDS_EFFECT' if isrds else 'DRIVER_TARGET_VALID; blocked metadata and exact risk set constrain evidence',
                'boundarySensitivity':{k:'MUST_SPECIFY_AND_SENSITIVITY_CHECK; not instantiated in this pilot' for k in sensitivity},
                'metricConstructDistinction':note[0] if note else 'Conditional open-triad tie formation, not static triangle/clustering score or all-tie rate',
                'derivationReview':note[1] if note else 'Canonical Driver classification preserved. Operational rate denominator is eligible open triads; do not reclassify because measured by a ratio.',
                'realWorldAntecedents':note[2] if note else 'Mutual-neighbor cues and contact opportunities may change restricted formation; actual rate effect unresolved',
                'sharedInputs':'Same network representation may feed multiple RDS; no independent simultaneous propagation' if isrds else 'Open-triad risk set shares graph inputs; closure events must not also propagate as a second snapshot triangle effect',
                'uncertainty':'Use governed external-input uncertainty requirements; do not instantiate missing algorithm/window/normalization',
                'exogenousRootRisk':'Existing outgoing legacy causal claim needs D10 review' if outgoing else 'No outgoing causal claim; do not create exogenous role',
                'governanceQuestion':'Resolve named blocked operational metadata only in a separate authorized decision; no substitute entity' if nulls else 'Choose operational network boundary and estimator per application; no context-free scalar assumption'}
        reviews.append(review)
        if isrds:
            action_ids=['HT-CAND-SOC-F07-'+n for n in note[3].split(',')]
            ant={'rdsId':eid,'realWorldAntecedent':note[2],'networkInputs':note[1],'happeningTypeIds':action_ids,
                 'driverTargetAssessment':'SOC-101/SOC-103 describe formation/dissolution rates, SOC-102 restricted closure; none specifies full adjacency, node membership or boundary.',
                 'validCompleteConfigurationDriverId':None,'exactCausalRelationshipTargetId':None,
                 'representationStatus':'BLOCKED_NEEDS_GOVERNANCE_INPUT','rdsRole':['RECALCULATED_STATE','MEASUREMENT','OUTCOME'],
                 'downstreamEvidence':'No inherited consequence; consult existing causal-source audit and H05-H27 questions',
                 'prohibitedShortcut':'No direct effect on '+eid+'; social ties are not ontology Relationships'}
            antecedents.append(ant)
            gid='GAP-SOC-F07-'+eid
            gaps.append({'id':gid,'rdsId':eid,'question':note[2],'missingTarget':'Complete real-network configuration / contact-opportunity / boundary representation',
                         'existingDriverAlternatives':['SOC-101','SOC-102','SOC-103'],'whyNotSubstitute':'Rates do not uniquely specify ties or adjacency; do not mint a Driver.',
                         'governance':governance(gid,blocked=True),'humanDecision':DECISION})
    return reviews,gaps,antecedents


def search_ledgers(w,audits,keys):
    vocab=ae.read(ROOT/'schemas/actions-events/v1/vocabulary.json')
    layers=['BIO','PSY','SOC','CUL','ENV','INS','INF','TEC']
    queries=[{'id':q,'question':question,'concepts':concepts,'system':'Public web search index; primary publisher/PMC/author repository/maintainer pages',
              'localDate':'2026-09-06','sourceIds':[keys[k] for k in skeys.split()],'selection':reason,'access':'Depth and locators in source-registry.json'} for q,question,concepts,skeys,reason in inp.SEARCHES]
    coverage=[]
    for layer in layers:
        for domain in vocab['domainTags']:
            ids=[h['id'] for h in w['passB']['happeningTypes'] if layer in h['originLayers'] and domain in h['domainTags']]
            coverage.append({'driverId':'SOC-102','originLayer':layer,'domain':domain,'searchIds':['Q03','Q04','Q05','Q06','Q07'],
                             'happeningTypeIds':ids,'outcome':'INSUFFICIENT_EVIDENCE',
                             'reason':'Source-backed identity found, but exact conditional closure effect not yet sufficiently aligned' if ids else 'Combined concept searches screened this origin/domain; no adequately supported exact SOC-102 effect retained. This is not proof of no effect.'})
    properties=[]
    targets=['SOC-102']+[a['id'] for a in audits if a['currentRecord']['relationFamily']=='CAUSAL']
    for target in targets:
        for prop in vocab['propertyChanges']:
            properties.append({'target':target,'property':prop,'searchIds':['Q02','Q03','Q04','Q05','Q06','Q07'],
                'outcome':'INSUFFICIENT_EVIDENCE','candidateIds':[e['id'] for e in w['passB']['effectAssertions']] if target=='SOC-102' and prop=='LEVEL' else [],
                'reason':'Real-world configuration change must resolve a Driver; no RDS or ontology-edge-edit loophole' if prop=='STRUCTURE' else 'No supported exact property/target effect retained; temporal or nonlinear observations do not supply a universal effect descriptor'})
    return {'method':'Structured evidence search/audit; not a formal systematic review. Matrices document screening, not 72 or 88 independent database searches.',
            'queries':queries,'driverOriginDomainCoverage':coverage,'effectPropertyCoverage':properties,
            'qualifierReview':{'reachDistribution':'Platform/classroom/cohort/village boundaries limit transfer','subgroups':'Homophily, assignment and subgroup opportunities confound pooled interpretation',
                'interactionSynergyAntagonism':'No exact joint-effect or moderation estimate retained','intendedObserved':'Identity intention does not establish observed effect',
                'unintended':'Exclusion, manipulation, privacy and stigma require actor-specific ethical review','benefitHarmNull':'No universal beneficial label; null findings are outcome-specific and not zero'},
            'unresolved':['Biological, Psychological and Cultural exact Driver effects not retained','No supported relationship-targeted effect with exact eligible edge','STRUCTURE target gaps unresolved',
                          'No trial-registry subscription search or inaccessible full-text review claimed']}


def counts_report(w,audits,sources,findings,hypotheses,revisions,gaps):
    # Generic read-only inventory already deduplicates V3 projections and native propositions.
    inventory=af.enriched_inventory()
    prod={k:inventory['summary'][k] for k in ('drivers','rds','entities','combinedActiveRelationships','combinedActiveCausal','combinedBySemantic')}
    recs=w['passA']['relationshipCandidates']+w['passA']['evidence']+list(ae.all_records(w['passB']))
    return {'production':prod,'existingDisposition':dict(Counter(a['primaryDisposition'] for a in audits)),
            'hypothesisDisposition':dict(Counter(h['disposition'] for h in hypotheses)),
            'newRelationships':len(w['passA']['relationshipCandidates']),'newRelationshipSemantics':dict(Counter(r['relationFamily'] for r in w['passA']['relationshipCandidates'])),
            'happeningTypes':len(w['passB']['happeningTypes']),'effectAssertions':len(w['passB']['effectAssertions']),
            'evidenceAssessments':len(w['passA']['evidence'])+len(w['passB']['evidenceAssessments']),
            'sourceFindings':len(findings),'findingDisposition':dict(Counter(f['disposition'] for f in findings)),
            'sources':len(sources),'canonicalReused':len([s for s in sources if not s['id'].startswith('SRC-CAND')]),
            'supplemental':len([s for s in sources if s['id'].startswith('SRC-CAND')]),'sourceDesignDistribution':dict(Counter(s['basis'] for s in sources)),
            'scientificRecordLifecycle':dict(Counter(r['governance']['lifecycleStatus'] for r in recs)),
            'revisionProposals':len(revisions),'ontologyTargetGaps':len(gaps),'separateGovernanceBlockedItems':len(gaps)+sum(h['disposition']=='BLOCKED_NEEDS_GOVERNANCE_INPUT' for h in hypotheses),
            'newGoverned':0,'newActive':0,'note':'Evidence findings nested within candidate assessments are not extra scientific identities. Revision/target-gap/hypothesis ledgers counted separately.'}


def render_docs(m,sources,audits,revisions,hypotheses,entities,gaps,antecedents,search,w,findings):
    header=f"Audit: `{inp.AUDIT}`. Frozen baseline: `{inp.BASELINE}`. Candidate-only; no governance, activation or source registration.\n"
    emit(DOCS/'README.md','# SOC-F07 — Network Structure & Position\n\n'+header+
         '\nThe pilot retained one conditional derivational candidate, eight reusable happening identities, and three research-needed Driver-effect hypotheses. It did not create new causal, association, moderation or pathway records. The principal finding is a missing complete network-configuration target beneath the calculated statistics.\n\n'+
         '\n'.join('- ['+name+']('+name+')' for name in ['SOC_F07_ENTITY_RDS_REVIEW.md','SOC_F07_EXISTING_RELATIONSHIP_AUDIT.md','SOC_F07_EVIDENCE_SUMMARY.md','SOC_F07_RESEARCH_LOG.md','SOC_F07_COMPLETENESS_REPORT.md','SOC_F07_GOVERNANCE_DECISION_PACKAGE.md','SOC_F07_SPECIAL_NETWORK_FINDINGS.md','SOC_F07_AUDIT_MANIFEST.json','EXECUTION.md'])+
         '\n\nMachine-readable records: [candidate workspace](../../../../data/candidates/actions-events-v1/SOC-F07/workspace.json). Original sources are linked in the evidence summary. No recommendation or scale-up authorization is implied.\n')
    text='# Entity and RDS review\n\n'+header+'\nAll canonical fields, including aliases, crosswalks, evidence notes and missing values, are frozen in the baseline and fully captured in [structured review](../../../../data/candidates/actions-events-v1/SOC-F07/entity-rds-review.json). Canonical narrative is not newly endorsed science.\n'
    for e in entities:
        r=e['currentRecord']
        text+=f"\n## {e['id']} — {r['name']}\n\n{r['definition']}\n\n"+table(['Item','Audit finding'],[
            ('Class / scale',r['entityType']+' / '+str(r.get('representationScale'))),('Construct / statistic',e['metricConstructDistinction']),
            ('Derivation / risk set',e['derivationReview']),('Real antecedents',e['realWorldAntecedents']),('Outgoing causal IDs',e['outgoingCausalRelationships']),
            ('Blocked/missing fields',e['blockedOrMissingFields']),('Shared inputs',e['sharedInputs']),('Targetability',e['targetability']),('Governance question',e['governanceQuestion'])])
        text+='\nBoundary sensitivity: '+NETWORK_LIMIT+' Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.\n'
    emit(DOCS/'SOC_F07_ENTITY_RDS_REVIEW.md',text)
    text='# Existing relationship audit\n\n'+header+'\nV3 projections are views of the same ten propositions, not ten additional relationships. All seven causal claims remain V1-incomplete and scientifically unchanged. No archived incident record was found.\n'
    for a in audits:
        r=a['currentRecord']; text+=f"\n## {a['id']} — {a['primaryDisposition']}\n\n`{r['subjectEntityId']} → {r['objectEntityId']}`; {r['relationFamily']}; gate `{a['rdsGate']}`.\n\n{a['proposedReview']}\n\n{a['evidenceRationale']}\n\nSources: {', '.join(a['sources'])}. Evidence {a['evidenceStrength']} / confidence {a['confidence']}. Owner {a['ownerFamilyId']}; endpoint Families marked for consultation {a['consultedFamilyIds']} (not claimed consulted).\n\nShared-input assessment: {a['sharedInputRisk']}. Temporal independence: {a['temporalIndependence']}. No new lag, persistence, functional form or quantitative magnitude. {DECISION}.\n"
    text+='\n## Exact review proposals, not replacement records\n\n'+table(['Proposal','Current edge','Proposed representation','Identity implications'],[(r['id'],r['currentRecord']['id'],r['exactProposal'],r['identityPolicy']) for r in revisions])
    text+='\nComplete field-level snapshots, proposed field changes, source changes, hashes and unresolved choices are in [revision proposals](../../../../data/candidates/actions-events-v1/SOC-F07/revision-proposals.json).\n'
    emit(DOCS/'SOC_F07_EXISTING_RELATIONSHIP_AUDIT.md',text)
    text='# Evidence and source summary\n\n'+header+'\nSource findings precede synthesis. Source-level support for a different outcome is not exact-ontology support. All numerical estimates remain null rather than invented. Findings marked NULL_FINDING mean no detected difference in the stated contrast, not a supported zero.\n\n'+table(['Source','Bibliographic identity','Access / basis','Exact applicability / limitation'],[(s['id'],f"[{s['title']}]({s['url']}) — {s['authors']}; {s['year']}; {s['venue']}; DOI {s['doi']}",s['accessDepth']+' / '+s['basis'],s['findingSummary']+' '+s['limitations']) for s in sources])
    text+='\n## Synthesis and contrary findings\n\n'+table(['Count','Value'],list(m['counts'].items()))
    text+='\nSRC-509 links to the same Centola experiment as SRC-235; its unresolved composite second citation is not independent evidence. Hunter and other reviews overlap included primary trials; no replication count is derived from paper count. Full PMC page access was sometimes challenged; indexed selected methods/results were reviewed, not an inaccessible entire paper. SRC-497 is metadata-level only.\n\nThe controlled closure study offers the strongest Driver-specific lead, but its invitation/reciprocal-follow risk set requires alignment with SOC-102. Group introduction and storm findings use different metrics. Those effects remain research-needed. Degree centralization evidence is definitional, not causal.\n'
    emit(DOCS/'SOC_F07_EVIDENCE_SUMMARY.md',text)
    text='# Structured research log\n\n'+header+'\n'+search['method']+' Selection prioritized primary experiments, methods and measurement papers; existing relationships were read before gap/action searches. Searches stopped after the main semantic/identification alternatives were supported; not scientific completeness.\n'+table(['Search','Question','Concepts','Sources','Selection'],[(q['id'],q['question'],q['concepts'],', '.join(q['sourceIds']),q['selection']) for q in search['queries']])
    text+='\n## Driver coverage\n\nEight origins × nine domains were screened against SOC-102 using the linked combined queries. All 72 cells retain INSUFFICIENT_EVIDENCE for an exact supported effect; identity leads are not efficacy findings. Eleven properties were considered for SOC-102 and each of seven reviewed causal edges (88 cells). No supported-null cell inferred from a nonsignificant study.\n\n'+table(['Origin','Identity leads','Exact effect outcome'],[(l,', '.join(sorted({h['id'] for h in w['passB']['happeningTypes'] if l in h['originLayers']})) or 'None retained','INSUFFICIENT_EVIDENCE') for l in ['BIO','PSY','SOC','CUL','ENV','INS','INF','TEC']])
    text+='\nComplete cells, qualifiers, no-findings, source-access limitations and unresolved gaps: [search ledger](../../../../data/candidates/actions-events-v1/SOC-F07/search-ledger.json). Psychological/cultural selection and biological development/illness were searched; their exact Driver effects were not established.\n'
    emit(DOCS/'SOC_F07_RESEARCH_LOG.md',text)
    render_decisions(header,m,audits,revisions,hypotheses,gaps,w)
    render_special(header,m,entities,antecedents)


def render_decisions(header,m,audits,revisions,hypotheses,gaps,w):
    text='# Human governance decision package\n\n'+header+'\nEvery human field remains **'+DECISION+'**. Recommendations below are audit proposals, not approvals. No candidate is activation-eligible.\n'
    groups=[('A. Existing — retain',[a for a in audits if a['primaryDisposition']=='RETAIN_AS_IS']),
            ('B. Existing — V1 incomplete',[]),('C. Existing — revision/retype/deprecation',[a for a in audits if a['primaryDisposition'] in {'REVISION_CANDIDATE','RETYPE_CANDIDATE'}])]
    for name, rows in groups:
        text+='\n## '+name+'\n\n'
        text+=table(['ID','Recommendation / exact proposal','Evidence / confidence','Boundaries / risk','Human decision'],[(a['id'],a['proposedReview'],str(a['sources'])+'; '+a['evidenceStrength']+'/'+a['confidence'],a['evidenceRationale']+' Owner '+a['ownerFamilyId'],DECISION) for a in rows]) if rows else 'No primary RETAIN_V1_INCOMPLETE disposition: all seven legacy causal records are incomplete, but stronger revision/retype/research questions govern their primary disposition.\n'
    for name in ['D. New causal','E. New association/semantic/temporal','G. Moderation','H. CausalPathway']:
        text+='\n## '+name+'\n\nNo formal record retained. Relevant questions remain in L; no quota and no graph-derived mediation.\n'
    r=w['passA']['relationshipCandidates'][0]
    text+='\n## F. Derivational candidate\n\n'+table(['ID','Proposition','Lifecycle','Evidence / confidence','Risk','Human decision'],[(r['id'],'RDS-0006 DERIVED_FROM SOC-049 only for degree-based centralization using all node degrees and external benchmark','REVIEW_READY',str(r['sourceIds'])+'; MODERATE/MODERATE',r['boundaryConditions'],DECISION)])
    text+='\n## I. HappeningType identities\n\n'+table(['ID','Reusable operation','Lifecycle','Evidence / confidence','Boundary / ownership','Human decision'],[(h['id'],h['name'],'REVIEW_READY',str(h['identitySourceIds'])+'; identity definition only, efficacy confidence NOT_ASSESSED',h['description']+' Owner SOC-F07; no effects inherited.',DECISION) for h in w['passB']['happeningTypes']])
    text+='\n## J. EffectAssertions\n\n'+table(['ID','Proposition','Lifecycle / recommendation','Evidence / confidence','Boundaries / risk','Human decision'],[(e['id'],e['typeId']+' → SOC-102; LEVEL, exact direction UNKNOWN','RESEARCH_NEEDED; do not govern',e['evidenceAssessmentIds'][0]+'; INSUFFICIENT/LIMITED/LOW',e['mechanism']+' Owner SOC-F07. No demonstrated general closure effect.',DECISION) for e in w['passB']['effectAssertions']])
    for name,status in [('K. Rejected hypotheses','REJECTED'),('L. Research-needed','RESEARCH_NEEDED'),('M. Governance/ontology blocked','BLOCKED_NEEDS_GOVERNANCE_INPUT')]:
        text+='\n## '+name+'\n\n'+table(['ID','Question','Triage','Reason / sources','Human decision'],[(h['id'],h['proposition'],h['semanticTriage'],h['reason']+' '+str(h['sourceIds']),DECISION) for h in hypotheses if h['disposition']==status])
    text+='\nREL-TEC-050 independently remains RESEARCH_NEEDED; no replacement. Twelve RDS target-gap records remain RESEARCH_NEEDED with NEEDS_GOVERNANCE_INPUT blocks. H12/H20 are two shared hypothesis-level manifestations, not fourteen distinct missing Drivers.\n\n## Evidence-level decisions\n\nOnly the conditional derivation assessment is REVIEW_READY/SUPPORTS/MODERATE/MODERATE. Seven existing-causal audit assessments and three EffectAssertion assessments are RESEARCH_NEEDED/INSUFFICIENT/LIMITED/LOW, with mixed/null findings retained. Evidence governance must remain assertion-specific.\n\n## Priority human questions\n\n1. Should a future governance process define a complete underlying network-state/contact-opportunity representation? Do not repurpose SOC-102 or rates as adjacency.\n2. Adjudicate the four contemporaneous RDS-to-RDS retype proposals before allowing executable propagation.\n3. Is the bounded SOC-053 → SOC-061 topology/reinforcement construct alignment adequate, or does it need another exact representation?\n4. Approve/reject the degree-only derivation dependency without resolving other RDS-0006 metadata.\n5. Decide whether platform-specific open-triad outcomes align sufficiently with SOC-102; keep its 11 blocked fields untouched.\n'
    emit(DOCS/'SOC_F07_GOVERNANCE_DECISION_PACKAGE.md',text)
    summary=ae.read(BASE/'inventory.json')
    fam=next(f for f in summary['families'] if f['id']=='SOC-F07')
    text='# Completeness and integrity report\n\n'+header+'\nRecorded coverage flags are not instructions to invent edges.\n'+table(['Metric','Value'],list(fam.items()))
    text+='\n## Corpus and candidate counts\n\n'+table(['Metric','Value'],list(m['counts'].items()))
    text+='\n## Structural flags\n\nNo production edge changed, so before/after production degree, isolates, cycles and connectivity are identical. All five current RDS causal sources were audited: SOC-052, SOC-054, SOC-055, SOC-056, SOC-053. Four internal RDS-to-RDS claims have shared-input/temporal risks. The one same-Layer outgoing claim needs scoped reinforcement evidence. Suspicious-hub/contradiction signals are review flags, not diagnoses. No new causal candidate, reciprocal edge or pathway was created.\n\nThe retained derivation is noncausal and adds no causal degree. RDS metrics can share adjacency, degree distributions, shortest paths and partitions; missing data and graph-size effects are not independent causes. No duplicate projection was counted.\n\n## RDS and action coverage\n\nAll twelve RDS have explicit antecedent/target-gap ledgers; none is an EffectAssertion direct target. SOC-102 has complete search screening across eight origins/nine domains/eleven properties, but no adequately aligned supported effect. Eight identities do not imply eight efficacious interventions. Five origins have retained identities (SOC/INS/ENV/INF/TEC); BIO/PSY/CUL are searched no-findings for exact effects. No identity or effect is practitioner-eligible.\n\n## Protected science\n\n'+str(m['protectedScience'])+'; comparison covers pre-existing data, schemas, migration handoff, scenario service, BIO-F01 and INF-F03 documents. New GOVERNED=0; new ACTIVE=0. Production counts remain 770 Drivers / 41 RDS / 811 entities / 457 active Relationships / 436 active causal.\n\n## Self-review\n\nAll three potential Driver effects were retained only as research-needed hypotheses. No direct metric manipulation, intervention ranking, numeric execution, homophily-as-influence or reachability-as-mediation was admitted. Per-record findings distinguish source designs; model/theory evidence is not labeled empirical. Access limitations prevent stronger exact-edge claims.\n'
    emit(DOCS/'SOC_F07_COMPLETENESS_REPORT.md',text)


def render_special(header,m,entities,antecedents):
    text='# Network representation stress test and cross-pilot lessons\n\n'+header+'\n## Answers to the pilot questions\n\n1. **Can AE V1 represent network interventions?** Reusable action identities and effects on valid process Drivers can be represented. A full topology/configuration effect cannot be honestly compressed into a derived-statistic target. This pilot retained no supported STRUCTURE effect.\n2. **Adequate Driver layer?** SOC-102 represents conditional closure rate. Neighboring SOC-101/103 represent formation/dissolution rates. These do not uniquely specify node membership, tie identities, adjacency, access, boundary or weights beneath twelve RDS. The coverage gap is real at the representation level, not proof that a particular new Driver is scientifically correct.\n3. **Potentially defensible RDS source?** SOC-053 → SOC-061 has experimental topology/reinforcement motivation but needs exact metric, independence, time and outcome alignment. Existing authority remains unchanged. Position-causes-outcome hypotheses are not rejected just because the source is derived.\n4. **Category/shared-input risks?** Density/clustering, assortativity/segregation, constraint/cross-cluster share and cross-cluster share/segregation may compare contemporaneous summaries of shared graph construction. Four retype-review proposals require adjudication, not automatic deletion.\n5. **Unrepresentable manipulations?** Allocation/rewiring/node removal and boundary changes can alter RDS calculations, but no complete configuration Driver is available. The twelve target-gap records share this issue; they are not twelve requests to create new entities.\n6. **Future ontology governance?** Review whether underlying tie configuration, opportunity or other representation is needed. This pilot creates none and repairs no blocked fields.\n7. **Does STRUCTURE work?** The property correctly distinguishes real-world reconfiguration from ontology graph editing. Target restrictions fail closed. Renaming a metric effect STRUCTURE does not legalize an RDS target.\n8. **Before scale-up?** Resolve or explicitly defer the target-coverage issue and the four RDS retype questions. Do not weaken AE04/D10, infer simulation weights or launch population to fill gaps. No new architecture is authorized here.\n\n## Identification and boundary discipline\n\n'+IDENTIFICATION+' '+NETWORK_LIMIT+' Random topology tests do not independently manipulate every correlated statistic. Static snapshots do not demonstrate persistence or dynamic transmitted effects. Degree, betweenness, centrality, brokerage and exposure are not interchangeable. SOC-F08 exposure and diffusion remain separate from SOC-F07 topology.\n\n## Per-RDS antecedent ledger\n\n'+table(['RDS','Inputs / real antecedent','Representation result'],[(a['rdsId'],a['networkInputs']+' '+a['realWorldAntecedent'],a['representationStatus']+'; '+a['driverTargetAssessment']) for a in antecedents])
    text+='\n## Cross-pilot process lessons\n\n'+table(['Concern','BIO-F01','INF-F03','SOC-F07'],[
        ('RDS safety','Sleep state derivation versus Driver interventions','Message × audience fit and numerator contributions','Shared adjacency, boundary and normalization; only one Driver'),
        ('Evidence','Phase-dependent and mixed/null clinical findings','Construct/proxy and feature-specific scope','Identification, interference, metric versus process and design overlap'),
        ('Actions/Events','Driver-linked deliberate interventions','Identity/effect separation and exposure identities','Identities represent real operations; full topology target missing'),
        ('Governance burden','Selective activation after evidence corrections','Partial activation; feature-scope issue left inactive','No activation proposed; many retype/target-gap questions'),
        ('Ownership','Cross-Family endpoint scope','Source-Family ownership with psychological target','SOC-F08 exposure, SOC-F03 formation and cross-Layer inputs must not duplicate'),
        ('Source handling','Registered sources after human approval','Selective canonicalization and source findings','Candidate register only; composite SRC-509 and review overlap flagged'),
        ('Isolation','Active model execution remained separate','Scientific/model/practitioner distinction','All candidate NOT_ELIGIBLE; no network simulation/recommendations')])
    text+='\nThe generic inventory and linked Pass A/B workflow generalize. Activatable scientific yield does not. Three pilots do not themselves authorize 105-Family scale-up. A later human decision must review target sufficiency, source-alignment backlog, cross-Family ownership and persistent blocked metadata. Prior pilots remain byte-for-byte unchanged.\n'
    emit(DOCS/'SOC_F07_SPECIAL_NETWORK_FINDINGS.md',text)


if __name__ == '__main__':
    print(encode(build()['counts']))
