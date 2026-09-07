"""EXPERIMENTAL / NON_PRODUCTION: synthetic state bookkeeping, NOT a scientific model.

No production imports, reads or writes; no inferred ties, causal effects, diffusion,
recommendations or empirical observations. CLI writes only beneath this experiment.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from itertools import combinations
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE=Path(__file__).resolve().parent
LABEL='SYNTHETIC / NON_PRODUCTION / NOT A SCIENTIFIC MODEL'
SID={'type':'string','pattern':'^SYN-[A-Z0-9-]+$'}
TEXT={'type':'string','minLength':1}
IDS={'type':'array','items':SID,'uniqueItems':True}
HASH={'type':'string','pattern':'^[0-9a-f]{64}$'}
TIME={'type':'string','format':'date-time','pattern':r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'}


def obj(properties):
    return {'type':'object','additionalProperties':False,'required':list(properties),'properties':properties}


NODE=obj({'id':SID,'active':{'type':'boolean'},'memberships':IDS})
TIE=obj({'id':SID,'objectKind':{'const':'SOCIAL_TIE'},'source':SID,'target':SID,'tieType':SID,
         'layerId':SID,'directed':{'type':'boolean'},'weight':{'type':'number','exclusiveMinimum':0},
         'validFrom':TIME,'validUntil':{'anyOf':[TIME,{'type':'null'}]},'provenanceId':SID})
OPPORTUNITY=obj({'id':SID,'source':SID,'target':SID,'enabled':{'type':'boolean'},'kind':{'enum':['PLATFORM_ACCESS','ASSIGNED_SEATING','CONTACT_OPPORTUNITY']},
                 'validFrom':TIME,'validUntil':{'anyOf':[TIME,{'type':'null'}]},'provenanceId':SID})
WINDOW=obj({'mode':{'enum':['SNAPSHOT','INTERVAL']},'start':TIME,'end':TIME,'aggregation':{'enum':['SNAPSHOT_AT_START','PERSISTENT_THROUGH_WINDOW']}})
OBSERVATION=obj({'recordKind':{'const':'SYNTHETIC_OBSERVATION_METADATA'},'provenanceId':SID,
    'accessDepth':{'const':'SYNTHETIC'},'realStateKnown':{'const':False},'isGroundTruth':{'const':False},
    'coverage':{'enum':['COMPLETE_SYNTHETIC_FRAME','INCOMPLETE','UNKNOWN']},
    'missingNodes':TEXT,'missingTies':TEXT,'sampling':TEXT,'tieInferenceMethod':TEXT,
    'latentStateRelation':{'const':'NOT_IDENTICAL_BY_ASSUMPTION'}})
STATE_SCHEMA={
    '$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'urn:psywerx:experimental:network-state-vnext:state',
    **obj({'label':{'const':LABEL},'architectureStatus':{'const':'PENDING'},'objectKind':{'const':'RELATIONAL_STATE'},
      'id':SID,'version':{'type':'integer','minimum':1},'parentHash':{'anyOf':[HASH,{'type':'null'}]},'contentHash':HASH,
      'stateNature':{'enum':['SYNTHETIC_MODELED_CONFIGURATION','SYNTHETIC_OBSERVATION']},
      'nodeCatalog':{'type':'array','items':NODE},'groupIds':IDS,'ties':{'type':'array','items':TIE},
      'opportunities':{'type':'array','items':OPPORTUNITY},
      'boundary':obj({'id':SID,'includedNodeIds':IDS,'selectionRule':TEXT,'outsideFramePolicy':TEXT}),
      'networkSpecification':obj({'tieTypeId':SID,'layerIds':IDS,'multiplexPolicy':{'const':'SELECT_ONE_LAYER_NO_COLLAPSE'},
                                  'metricLayerId':SID,'weightInterpretation':TEXT,'riskSetOpportunityIds':IDS}),
      'window':WINDOW,'observation':OBSERVATION,'appliedDeltaIds':IDS,
      'scientificClaims':{'type':'array','maxItems':0},'executionEligibility':{'const':False}})}


def operation(name, fields):
    return obj({'operation':{'const':name},**fields})


OPERATIONS=[
    operation('ADD_TIE',{'tie':TIE}),operation('REMOVE_TIE',{'tieId':SID}),
    operation('REWIRE_TIE',{'removedTieId':SID,'addedTie':TIE}),
    operation('ADD_NODE',{'node':NODE,'includeInBoundary':{'type':'boolean'}}),
    operation('REMOVE_NODE',{'nodeId':SID,'incidentTiePolicy':{'const':'REMOVE_AND_RECORD'}}),
    operation('ASSIGN_MEMBERSHIP',{'nodeId':SID,'groupIds':IDS}),
    operation('SET_BOUNDARY',{'includedNodeIds':IDS,'selectionReason':TEXT}),
    operation('SET_WEIGHT',{'tieId':SID,'weight':{'type':'number','exclusiveMinimum':0}}),
    operation('SET_ACCESS',{'opportunityId':SID,'enabled':{'type':'boolean'}}),
    operation('ASSIGN_SEATING',{'opportunity':OPPORTUNITY}),
]
DELTA_SCHEMA={
    '$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'urn:psywerx:experimental:network-state-vnext:delta',
    **obj({'label':{'const':LABEL},'architectureStatus':{'const':'PENDING'},'id':SID,
      'objectKind':{'const':'SCENARIO_STATE_DELTA'},'stateId':SID,'expectedVersion':{'type':'integer','minimum':1},
      'expectedHash':HASH,'targetNamespace':{'const':'SCENARIO_STATE'},
      'basis':{'enum':['SYNTHETIC_SCENARIO_OPERATION','SYNTHETIC_SCOPE_SELECTION']},
      'occurrenceStatus':{'const':'HYPOTHETICAL'},'provenanceId':SID,'effectiveAt':TIME,
      'assertedConsequences':{'type':'array','maxItems':0},
      'operations':{'type':'array','minItems':1,'items':{'oneOf':OPERATIONS}}})}


class Rejected(ValueError): pass


def require(value, reason):
    if not value: raise Rejected(reason)


def validate_schema(schema, value):
    errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(value))
    if errors: raise Rejected(str(errors[0].message))


def canonical(state):
    s=copy.deepcopy(state)
    for key in ('nodeCatalog','ties','opportunities'): s[key].sort(key=lambda r:r['id'])
    for row in s['nodeCatalog']: row['memberships'].sort()
    for key in ('groupIds',): s[key].sort()
    s['boundary']['includedNodeIds'].sort()
    for key in ('layerIds','riskSetOpportunityIds'): s['networkSpecification'][key].sort()
    return s


def content_hash(state):
    value=canonical(state); value.pop('contentHash',None)
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def sealed(state):
    state=canonical(state); state['contentHash']=content_hash(state); return state


def unique(rows, label):
    require(len({r['id'] for r in rows})==len(rows),'Duplicate '+label+' identity')


def validate_state(s):
    validate_schema(STATE_SCHEMA,s)
    require(content_hash(s)==s['contentHash'],'State content/version hash mismatch')
    for key in ('nodeCatalog','ties','opportunities'): unique(s[key],key)
    all_ids=[s['id'],s['boundary']['id'],*s['groupIds']]+[r['id'] for key in ('nodeCatalog','ties','opportunities') for r in s[key]]
    require(len(set(all_ids))==len(all_ids),'State/node/tie/group identity collision')
    nodes={r['id']:r for r in s['nodeCatalog']}; active={k for k,r in nodes.items() if r['active']}
    require(set(s['boundary']['includedNodeIds'])<=active,'Boundary refers to missing/inactive nodes')
    require(all(set(r['memberships'])<=set(s['groupIds']) for r in nodes.values()),'Unknown group')
    spec=s['networkSpecification']
    require(spec['metricLayerId'] in spec['layerIds'],'Metric layer not declared')
    require(set(spec['riskSetOpportunityIds'])<={r['id'] for r in s['opportunities']},'Unresolved opportunity risk set')
    signatures=set()
    for row in s['ties']+s['opportunities']:
        require(row['source'] in active and row['target'] in active,'Unresolved/inactive tie or opportunity endpoint')
        require(row['source']!=row['target'],'Self ties/opportunities not supported by this prototype')
        require(row['validUntil'] is None or row['validUntil']>=row['validFrom'],'Reversed validity interval')
    for tie in s['ties']:
        require(tie['layerId'] in spec['layerIds'] and tie['tieType']==spec['tieTypeId'],'Undeclared tie layer/type')
        pair=(tie['source'],tie['target']) if tie['directed'] else tuple(sorted((tie['source'],tie['target'])))
        sig=(pair,tie['layerId'],tie['tieType'],tie['directed'])
        require(sig not in signatures,'Duplicate same-relation dyad; temporal multiedge merging is not implemented')
        signatures.add(sig)
    window=s['window']; require(window['end']>=window['start'],'Reversed observation window')
    if window['mode']=='SNAPSHOT':
        require(window['end']==window['start'] and window['aggregation']=='SNAPSHOT_AT_START','Snapshot cannot imply dynamic interval')
    else: require(window['end']>window['start'] and window['aggregation']=='PERSISTENT_THROUGH_WINDOW','Explicit interval aggregation required')
    require(s['observation']['missingNodes'].strip() and s['observation']['missingTies'].strip(),'Missingness cannot be silently ignored')
    return True


def tie(identifier, source, target, weight=1, directed=False):
    return {'id':identifier,'objectKind':'SOCIAL_TIE','source':source,'target':target,'tieType':'SYN-TYPE-FRIENDSHIP',
            'layerId':'SYN-LAYER-FRIENDSHIP','directed':directed,'weight':weight,
            'validFrom':'2026-01-01T00:00:00Z','validUntil':None,'provenanceId':'SYN-PROVENANCE-FIXTURE'}


def opportunity(identifier, source, target, kind='PLATFORM_ACCESS'):
    return {'id':identifier,'source':source,'target':target,'enabled':True,'kind':kind,
            'validFrom':'2026-01-01T00:00:00Z','validUntil':None,'provenanceId':'SYN-PROVENANCE-FIXTURE'}


def fixture():
    nodes=['SYN-NODE-'+c for c in 'ABCDE']
    s={'label':LABEL,'architectureStatus':'PENDING','objectKind':'RELATIONAL_STATE','id':'SYN-STATE-001','version':1,'parentHash':None,
       'stateNature':'SYNTHETIC_MODELED_CONFIGURATION',
       'nodeCatalog':[{'id':n,'active':True,'memberships':['SYN-GROUP-1']} for n in nodes],
       'groupIds':['SYN-GROUP-1','SYN-GROUP-2'],
       'ties':[tie('SYN-TIE-'+pair,'SYN-NODE-'+pair[0],'SYN-NODE-'+pair[1]) for pair in ('AB','AC','BC','CD','DE')],
       'opportunities':[opportunity('SYN-OPPORTUNITY-AD',nodes[0],nodes[3])],
       'boundary':{'id':'SYN-BOUNDARY-001','includedNodeIds':nodes[:4],
                   'selectionRule':'Fictional analytic frame A-D; E known outside selected frame','outsideFramePolicy':'Known outside-frame ties retained, not treated as absence'},
       'networkSpecification':{'tieTypeId':'SYN-TYPE-FRIENDSHIP','layerIds':['SYN-LAYER-FRIENDSHIP'],
                               'metricLayerId':'SYN-LAYER-FRIENDSHIP','multiplexPolicy':'SELECT_ONE_LAYER_NO_COLLAPSE',
                               'weightInterpretation':'Positive fictional contact intensity; metric projection explicitly binary, not causal strength',
                               'riskSetOpportunityIds':['SYN-OPPORTUNITY-AD']},
       'window':{'mode':'SNAPSHOT','start':'2026-01-01T00:00:00Z','end':'2026-01-01T00:00:00Z','aggregation':'SNAPSHOT_AT_START'},
       'observation':{'recordKind':'SYNTHETIC_OBSERVATION_METADATA','provenanceId':'SYN-PROVENANCE-FIXTURE','accessDepth':'SYNTHETIC',
                       'realStateKnown':False,'isGroundTruth':False,'coverage':'COMPLETE_SYNTHETIC_FRAME',
                       'missingNodes':'None by fictional fixture construction; not a claim about real-world coverage',
                       'missingTies':'None by fictional fixture construction; no latent real network is observed',
                       'sampling':'Explicit fictional node frame; no real respondents','tieInferenceMethod':'Authored fixture, not inferred empirical ties',
                       'latentStateRelation':'NOT_IDENTICAL_BY_ASSUMPTION'},
       'appliedDeltaIds':[],'scientificClaims':[],'executionEligibility':False}
    return sealed(s)


def delta(state, identifier, operations):
    scope=all(o['operation']=='SET_BOUNDARY' for o in operations)
    return {'label':LABEL,'architectureStatus':'PENDING','id':identifier,'objectKind':'SCENARIO_STATE_DELTA',
            'stateId':state['id'],'expectedVersion':state['version'],'expectedHash':state['contentHash'],
            'targetNamespace':'SCENARIO_STATE','basis':'SYNTHETIC_SCOPE_SELECTION' if scope else 'SYNTHETIC_SCENARIO_OPERATION',
            'occurrenceStatus':'HYPOTHETICAL','provenanceId':'SYN-PROVENANCE-OPERATION','effectiveAt':state['window']['start'],
            'assertedConsequences':[],'operations':operations}


def apply_delta(original, change):
    validate_state(original); validate_schema(DELTA_SCHEMA,change)
    require(change['stateId']==original['id'],'Wrong state identity')
    require((change['expectedVersion'],change['expectedHash'])==(original['version'],original['contentHash']),'Stale precondition')
    require(change['id'] not in original['appliedDeltaIds'],'Delta already applied')
    require(change['effectiveAt']==original['window']['start'],'Prototype only edits a declared snapshot/counterfactual interval start; no dynamic execution')
    scope=any(o['operation']=='SET_BOUNDARY' for o in change['operations'])
    require(not scope or all(o['operation']=='SET_BOUNDARY' for o in change['operations']),'Boundary selection cannot be bundled as an actual tie mutation')
    require((change['basis']=='SYNTHETIC_SCOPE_SELECTION')==scope,'Scope change is not structural intervention evidence')
    state=copy.deepcopy(original); removed=[]
    def node(identifier):
        rows=[r for r in state['nodeCatalog'] if r['id']==identifier and r['active']]
        require(len(rows)==1,'Active node not found'); return rows[0]
    def remove_tie(identifier):
        rows=[r for r in state['ties'] if r['id']==identifier]
        require(len(rows)==1,'Tie not found'); removed.append(identifier); state['ties'].remove(rows[0])
    for op in change['operations']:
        kind=op['operation']
        if kind=='ADD_TIE': state['ties'].append(copy.deepcopy(op['tie']))
        elif kind=='REMOVE_TIE': remove_tie(op['tieId'])
        elif kind=='REWIRE_TIE':
            remove_tie(op['removedTieId']); state['ties'].append(copy.deepcopy(op['addedTie']))
        elif kind=='ADD_NODE':
            require(op['node']['active'],'Entering node must be active')
            require(op['node']['id'] not in {r['id'] for r in state['nodeCatalog']},'No node identity recycling')
            state['nodeCatalog'].append(copy.deepcopy(op['node']))
            if op['includeInBoundary']: state['boundary']['includedNodeIds'].append(op['node']['id'])
        elif kind=='REMOVE_NODE':
            identifier=op['nodeId']; row=node(identifier); row['active']=False; row['memberships']=[]
            for t in list(state['ties']):
                if identifier in (t['source'],t['target']): remove_tie(t['id'])
            state['opportunities']=[o for o in state['opportunities'] if identifier not in (o['source'],o['target'])]
            state['networkSpecification']['riskSetOpportunityIds']=[i for i in state['networkSpecification']['riskSetOpportunityIds'] if i in {o['id'] for o in state['opportunities']}]
            state['boundary']['includedNodeIds']=[n for n in state['boundary']['includedNodeIds'] if n!=identifier]
        elif kind=='ASSIGN_MEMBERSHIP': node(op['nodeId'])['memberships']=list(op['groupIds'])
        elif kind=='SET_BOUNDARY':
            state['boundary']['includedNodeIds']=list(op['includedNodeIds']); state['boundary']['selectionRule']=op['selectionReason']
        elif kind=='SET_WEIGHT':
            matches=[r for r in state['ties'] if r['id']==op['tieId']]; require(len(matches)==1,'Tie not found'); matches[0]['weight']=op['weight']
        elif kind=='SET_ACCESS':
            matches=[r for r in state['opportunities'] if r['id']==op['opportunityId']]; require(len(matches)==1,'Opportunity not found'); matches[0]['enabled']=op['enabled']
        elif kind=='ASSIGN_SEATING':
            require(op['opportunity']['kind']=='ASSIGNED_SEATING','Seating is an opportunity, not friendship')
            state['opportunities'].append(copy.deepcopy(op['opportunity']))
            state['networkSpecification']['riskSetOpportunityIds'].append(op['opportunity']['id'])
    state['version']+=1; state['parentHash']=original['contentHash']; state['appliedDeltaIds'].append(change['id'])
    state=sealed(state); validate_state(state)
    receipt={'label':LABEL,'deltaId':change['id'],'beforeHash':original['contentHash'],'afterHash':state['contentHash'],
             'changeClass':'ANALYTIC_BOUNDARY_ONLY' if scope else 'DETERMINISTIC_SYNTHETIC_STATE_OPERATION',
             'removedTieIds':sorted(removed),'scientificConsequencesEstablished':False,'empiricalEvidenceProduced':False,
             'ontologyRelationshipsEdited':0,'executionEligibility':False}
    return state,receipt


def centralization(degrees, node_ids, benchmark):
    require(set(degrees)==set(node_ids) and len(node_ids)==len(set(node_ids)),'Complete aligned all-node degree distribution required; one ego is insufficient')
    n=len(node_ids)
    require(benchmark=={'definition':'UNDIRECTED_SIMPLE_LOOPLESS_DEGREE_STAR_MAX','nodeCount':n,'maximum':(n-1)*(n-2)},'Explicit matching degree benchmark required')
    require(all(type(v) is int and 0<=v<n for v in degrees.values()),'Invalid unweighted degree')
    # Havel-Hakimi consistency check: a complete vector must also be realizable
    # as a simple graph. This checks arithmetic, not provenance/empirical truth.
    remaining=sorted(degrees.values(),reverse=True)
    while remaining and remaining[0]:
        d=remaining.pop(0)
        require(d<=len(remaining),'Non-graphical degree collection')
        for index in range(d): remaining[index]-=1
        require(all(v>=0 for v in remaining),'Non-graphical degree collection')
        remaining.sort(reverse=True)
    if n<3: return {'value':None,'status':'NOT_APPLICABLE','reason':'Star normalization denominator is undefined/zero for n<3'}
    return {'value':sum(max(degrees.values())-v for v in degrees.values())/benchmark['maximum'],
            'status':'CALCULATED_SYNTHETIC_REPRESENTATION_ONLY'}


def metrics(state):
    validate_state(state)
    ns=state['networkSpecification']; nodes=sorted(state['boundary']['includedNodeIds']); adjacency={n:set() for n in nodes}
    time=state['window']['start']; stop=state['window']['end']
    selected=[t for t in state['ties'] if t['layerId']==ns['metricLayerId'] and t['source'] in adjacency and t['target'] in adjacency
              and t['validFrom']<=time and (t['validUntil'] is None or
                  (t['validUntil']>=stop if state['window']['mode']=='INTERVAL' else t['validUntil']>time))]
    require(not any(t['directed'] for t in selected),'Directed metrics require a separate metric specification; do not collapse direction')
    for t in selected: adjacency[t['source']].add(t['target']); adjacency[t['target']].add(t['source'])
    degree={n:len(adjacency[n]) for n in nodes}; n=len(nodes); m=len(selected)
    clustering={u:(sum(v in adjacency[w] for v,w in combinations(sorted(adjacency[u]),2))/(degree[u]*(degree[u]-1)/2) if degree[u]>=2 else 0) for u in nodes}
    unseen=set(nodes); components=[]
    while unseen:
        todo=[min(unseen)]; component=set()
        while todo:
            u=todo.pop()
            if u in component: continue
            component.add(u); todo.extend(adjacency[u]-component)
        unseen-=component; components.append(sorted(component))
    benchmark={'definition':'UNDIRECTED_SIMPLE_LOOPLESS_DEGREE_STAR_MAX','nodeCount':n,'maximum':(n-1)*(n-2)}
    return {'label':LABEL,'stateId':state['id'],'stateVersion':state['version'],'stateHash':state['contentHash'],
            'scope':{'boundaryId':state['boundary']['id'],'nodeIds':nodes,'metricLayerId':ns['metricLayerId'],'window':state['window'],
                     'projection':'BINARY_POSITIVE_WEIGHT_SIMPLE_UNDIRECTED_LOOPLESS; weights deliberately not causal or numeric effect weights',
                     'localClusteringLowDegreeConvention':'ZERO_WHEN_FEWER_THAN_TWO_NEIGHBORS'},
            'nodeCount':n,'edgeCount':m,'degree':degree,'density':2*m/(n*(n-1)) if n>1 else None,
            'localClustering':clustering,'componentNodeSets':components,
            'componentFragmentation':{'variant':'UNREACHABLE_UNORDERED_PAIR_FRACTION','value':1-sum(len(c)*(len(c)-1) for c in components)/(n*(n-1)) if n>1 else None},
            'degreeCentralization':centralization(degree,nodes,benchmark),'externalBenchmark':benchmark,
            'realWorldMetricKnown':False,'observationCoverage':state['observation']['coverage'],
            'warnings':['Conditional on declared synthetic representation; neither latent truth nor causal effect.',
                        'Changes in analytic boundary can change metrics without any tie change.',
                        'No temporal reachability, uncertainty propagation or population estimation implemented.'],
            'propagationPolicy':'RECOMPUTE_ONLY_NO_ADDITIVE_CAUSAL_PROPAGATION'}


def assert_use(request):
    """Fail-closed experiment boundary; not a replacement production validator."""
    forbidden={'EMPIRICAL_CAUSAL_EVIDENCE','MEDIATION_FROM_REACHABILITY','DYNAMIC_PREDICTION','METRIC_CAUSAL_PROPAGATION',
               'DIRECT_RDS_EFFECT','ONTOLOGY_RELATIONSHIP_EDIT','PRACTITIONER_RECOMMENDATION','REAL_STATE_TRUTH'}
    require(request not in forbidden,'Unauthorized interpretation: '+request)
    require(request=='SYNTHETIC_METRIC_RECOMPUTATION','Only deterministic synthetic metric recomputation allowed')


def demonstration():
    base=fixture()
    examples=[
        ('ADD-TIE',[{'operation':'ADD_TIE','tie':tie('SYN-TIE-AD','SYN-NODE-A','SYN-NODE-D')}]),
        ('REMOVE-TIE',[{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}]),
        ('NODE-ENTRY',[{'operation':'ADD_NODE','node':{'id':'SYN-NODE-F','active':True,'memberships':[]},'includeInBoundary':True}]),
        ('NODE-EXIT',[{'operation':'REMOVE_NODE','nodeId':'SYN-NODE-C','incidentTiePolicy':'REMOVE_AND_RECORD'}]),
        ('MEMBERSHIP',[{'operation':'ASSIGN_MEMBERSHIP','nodeId':'SYN-NODE-A','groupIds':['SYN-GROUP-2']}]),
        ('BOUNDARY',[{'operation':'SET_BOUNDARY','includedNodeIds':['SYN-NODE-'+c for c in 'ABCDE'],'selectionReason':'Expand analytic frame to include already-known fictional E; no tie created'}]),
        ('WEIGHT',[{'operation':'SET_WEIGHT','tieId':'SYN-TIE-AB','weight':2}]),
        ('ACCESS',[{'operation':'SET_ACCESS','opportunityId':'SYN-OPPORTUNITY-AD','enabled':False}]),
        ('SEATING',[{'operation':'ASSIGN_SEATING','opportunity':opportunity('SYN-OPPORTUNITY-SEATS','SYN-NODE-A','SYN-NODE-D','ASSIGNED_SEATING')}]),
    ]
    results=[]
    for identifier,ops in examples:
        change=delta(base,'SYN-DELTA-'+identifier,ops); after,receipt=apply_delta(base,change)
        results.append({'id':'SYN-EXAMPLE-'+identifier,'delta':change,'afterState':after,'receipt':receipt,'metrics':metrics(after)})
    return {'label':LABEL,'architectureStatus':'PENDING','baseState':base,'baseMetrics':metrics(base),'examples':results}


def safe_output(path):
    target=Path(path).resolve()
    require(target.is_relative_to(HERE) and target!=HERE,'Output must be an explicit child directory inside this experiment')
    # Resolve parents AND each file to reject symlink/junction redirection.
    for name in ('synthetic-examples.json','state.schema.json','delta.schema.json'):
        require((target/name).resolve().is_relative_to(HERE),'Output file escapes isolated experiment')
    return target


def generate(output):
    target=safe_output(output); payload=demonstration()
    target.mkdir(parents=True,exist_ok=True)
    for name,value in [('synthetic-examples.json',payload),('state.schema.json',STATE_SCHEMA),('delta.schema.json',DELTA_SCHEMA)]:
        (target/name).write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    return {'syntheticExamples':len(payload['examples']),'scientificFindings':0,'productionWrites':0}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',required=True)
    print(json.dumps(generate(parser.parse_args().output),sort_keys=True))
