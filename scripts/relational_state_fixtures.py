"""Fictional SYN-* state fixtures; no real-person data or scientific findings."""
import argparse
import copy
import json
from pathlib import Path
import relational_state_v1 as ns
P='SYN-PROV-FIXTURE'
TIME='2026-01-01T00:00:00Z'


def node(letter): return {'id':'SYN-NODE-'+letter,'active':True,'memberships':['SYN-GROUP-A'],'provenanceId':P}


def tie(pair):
    return {'id':'SYN-TIE-'+pair,'objectKind':'SOCIAL_TIE','source':'SYN-NODE-'+pair[0],'target':'SYN-NODE-'+pair[1],
        'tieTypeId':'SYN-TYPE-FRIENDSHIP','layerId':'SYN-LAYER-CONTACT','directed':False,'weight':1,
        'weightMeaning':'BINARY_TIE_PRESENCE','weightUnit':'1','validFrom':TIME,'validUntil':None,
        'provenanceId':P,'basis':'ASSUMED','observationRef':None}


def opportunity(identifier='SYN-OPP-SEAT',kind='ASSIGNED_SEATING'):
    return {'id':identifier,'objectKind':'CONTACT_OPPORTUNITY','source':'SYN-NODE-A','target':'SYN-NODE-D',
        'kind':kind,'enabled':True,'validFrom':TIME,'validUntil':None,'provenanceId':P}


def state():
    return ns.seal({'schemaVersion':'1.0.0','objectKind':'RELATIONAL_STATE','recordClass':ns.SYNTHETIC,
        'id':'SYN-STATE-BASE','scenarioId':'SYN-SCENARIO-001','revision':1,'parent':None,
        'window':{'mode':'SNAPSHOT','start':TIME,'end':TIME,'aggregation':'SNAPSHOT_AT_START'},
        'boundary':{'id':'SYN-BOUNDARY-001','revision':1,'includedNodeIds':['SYN-NODE-'+c for c in 'ABCD'],
            'includedPopulationRule':'Fictional analytic node frame A-D','excludedPopulationRule':'E known outside boundary, not nonexistent',
            'unknownPopulationRule':'No real population or ground-truth completeness claim'},
        'nodes':[node(c) for c in 'ABCDE'],'groups':['SYN-GROUP-A','SYN-GROUP-B'],
        'ties':[tie(pair) for pair in ('AB','AC','BC','CD','DE')],
        'opportunities':[opportunity('SYN-OPP-ACCESS','PLATFORM_ACCESS')],
        'tieTypeIds':['SYN-TYPE-FRIENDSHIP'],'layerIds':['SYN-LAYER-CONTACT'],'riskSetOpportunityIds':['SYN-OPP-ACCESS'],
        'provenance':[{'id':P,'method':'SYNTHETIC_FIXTURE','sourceLocators':[],
            'description':'Fictional author-stipulated graph; no citation, person or empirical causal effect'}],
        'construction':[],'assumptions':{'missingNodes':'None within fictional stipulated frame; real-world coverage not asserted',
            'missingTies':'Unknown real ties; only fictional configuration','absentTieMeaning':'UNKNOWN_UNLESS_EXPLICITLY_STIPULATED',
            'coverage':'COMPLETE_STIPULATED_FRAME','limitations':['SYNTHETIC / NON_PRODUCTION / NOT A SCIENTIFIC MODEL'],
            'realNetworkTruthClaim':False},
        'privacy':{'classification':'SYNTHETIC','identityMapping':'SEPARATE_NOT_RESOLVED','externalIdentityReference':None,
            'accessPolicy':'CALLER_AUTHORIZATION_REQUIRED','retentionPolicy':'Fictional artifacts only',
            'exportPolicy':'DENY_BY_DEFAULT','topologyMayIdentify':True},
        'appliedDeltaIds':[],'retiredTieIds':[],'scientificConsequences':[],'causalExecutionAuthorized':False})


def delta(state,ops,identifier='SYN-DELTA-001'):
    return {'schemaVersion':'1.0.0','objectKind':'SCENARIO_STATE_DELTA','recordClass':ns.SYNTHETIC,
        'id':identifier,'scenarioId':state['scenarioId'],'expectedState':ns.ref(state),'effectiveAt':TIME,
        'basis':'ANALYTIC_BOUNDARY_SELECTION' if any(o['operation']=='CHANGE_BOUNDARY' for o in ops) else 'STIPULATED_MODELED_OPERATION',
        'provenance':copy.deepcopy(state['provenance'][0]),'occurrenceRef':None,'happeningTypeRef':None,
        'realWorldSuccessClaim':False,'empiricalEvidenceProduced':False,'operations':ops}


def metric(variant):
    norm={'DEGREE_RAW_UNDIRECTED':'NONE','DENSITY_SIMPLE_UNDIRECTED':'POSSIBLE_PAIRS','CLUSTERING_LOCAL_UNDIRECTED':'NEIGHBOR_PAIRS',
          'FRAGMENTATION_UNREACHABLE_PAIRS':'POSSIBLE_PAIRS','FREEMAN_DEGREE_CENTRALIZATION':'SAME_SIZE_STAR'}[variant]
    return {'variant':variant,'tieTypeId':'SYN-TYPE-FRIENDSHIP','layerId':'SYN-LAYER-CONTACT','direction':'UNDIRECTED',
        'loops':False,'weightPolicy':'EXPLICIT_BINARY_UNWEIGHTED','parallelTies':False,'normalization':norm,
        'lowDegreeClustering':'ZERO_BY_SPECIFICATION' if variant=='CLUSTERING_LOCAL_UNDIRECTED' else 'NOT_APPLICABLE'}


def request(state,variant,binding=None):
    target={'DEGREE_RAW_UNDIRECTED':'SOC-049','DENSITY_SIMPLE_UNDIRECTED':'SOC-052','CLUSTERING_LOCAL_UNDIRECTED':'SOC-053',
            'FRAGMENTATION_UNREACHABLE_PAIRS':'RDS-0007','FREEMAN_DEGREE_CENTRALIZATION':'RDS-0006'}[variant]
    r={'schemaVersion':'1.0.0','objectKind':'RDS_CALCULATION_REQUEST','id':'SYN-CALC-'+variant.replace('_','-'),
       'recordClass':ns.SYNTHETIC,'stateRef':ns.ref(state),'boundary':copy.deepcopy(state['boundary']),'window':copy.deepcopy(state['window']),
       'targetRds':ns.entity_reference(target),'metric':metric(variant),'bindingRef':None,'collection':None,'externalBenchmark':None,
       'useMode':'SYNTHETIC_VALIDATION','contributionIdentity':'SYN-CONTRIB-RECALCULATION','propagationRoutes':['STATE_RECALCULATION']}
    if binding:
        scores=ns.selected_graph(state,metric('DEGREE_RAW_UNDIRECTED'))
        r['bindingRef']=ns.ref(binding); r['contributionIdentity']=binding['sharedContributionIdentity']
        r['collection']={'subjectNodeIds':sorted(scores),'completeness':'COMPLETE_ALIGNED','stateRef':ns.ref(state),
            'boundary':copy.deepcopy(state['boundary']),'window':copy.deepcopy(state['window']),
            'inputEntity':ns.entity_reference('SOC-049'),'metric':metric('DEGREE_RAW_UNDIRECTED'),
            'values':[{'nodeId':key,'value':len(value)} for key,value in sorted(scores.items())]}
        n=len(scores); r['externalBenchmark']={'kind':'SAME_SIZE_SIMPLE_UNDIRECTED_STAR','nodeCount':n,'maximum':(n-1)*(n-2)}
    return r


def observation(identifier,removed_tie):
    s=state(); o={'schemaVersion':'1.0.0','objectKind':'NETWORK_OBSERVATION','recordClass':ns.SYNTHETIC,
       'id':identifier,'scenarioId':s['scenarioId'],'revision':1,
       **{k:copy.deepcopy(s[k]) for k in ('window','boundary','nodes','ties','provenance','privacy')},
       'observationMethod':'Fictional report, not empirical data','samplingFrame':'Explicit fictional A-E roster',
       'inferredTieMethod':None,'missingness':copy.deepcopy(s['assumptions']),'automaticStateOverwrite':False}
    o['ties']=[t for t in o['ties'] if t['id']!=removed_tie]
    for t in o['ties']: t['basis']='OBSERVED'
    o['missingness'].update(coverage='INCOMPLETE',missingNodes='Unknown unobserved actors',missingTies='Reports may omit different ties')
    return ns.seal(o)


def empty_state(identifier):
    s=state(); s['id']=identifier; s['nodes']=[]; s['ties']=[]; s['opportunities']=[]
    s['riskSetOpportunityIds']=[]; s['boundary']['includedNodeIds']=[]; return ns.seal(s)


def demonstration():
    import materialize_soc_f07_completion as completion
    s=state(); b=completion.binding(); auth=[completion.authorization([b])]
    boundary=copy.deepcopy(s['boundary']); boundary['revision']+=1; boundary['includedNodeIds'].append('SYN-NODE-E')
    cases=[('add-tie',{'operation':'ADD_TIE','tie':tie('AD')}),('remove-tie',{'operation':'REMOVE_TIE','tieId':'SYN-TIE-AB'}),
        ('add-node',{'operation':'ADD_NODE','node':node('F'),'includeInBoundary':True}),
        ('deactivate-node',{'operation':'DEACTIVATE_NODE','nodeId':'SYN-NODE-C','incidentPolicy':'REMOVE_AND_RECORD'}),
        ('membership',{'operation':'CHANGE_MEMBERSHIP','nodeId':'SYN-NODE-A','groupIds':['SYN-GROUP-B']}),
        ('boundary-only',{'operation':'CHANGE_BOUNDARY','boundary':boundary}),
        ('tie-weight',{'operation':'UPDATE_TIE_WEIGHT','tieId':'SYN-TIE-AB','weight':2,'weightMeaning':'FICTIONAL_CONTACT_INTENSITY','weightUnit':'fictional-unit'}),
        ('disable-access',{'operation':'CHANGE_ACCESS','opportunityId':'SYN-OPP-ACCESS','enabled':False}),
        ('seating-not-friendship',{'operation':'CHANGE_CONTACT_OPPORTUNITY','opportunity':opportunity()})]
    examples=[]
    for number,(name,operation) in enumerate(cases,1):
        d=delta(s,[operation],f'SYN-DELTA-{number:03d}'); after,receipt=ns.apply_delta(s,d)
        calc=ns.calculate(request(after,'DEGREE_RAW_UNDIRECTED'),after)
        examples.append({'name':name,'delta':d,'receipt':receipt,'after':after,'degreeCalculation':calc})
    for number,removed in [(1,'SYN-TIE-AB'),(2,'SYN-TIE-AC')]:
        o=observation(f'SYN-OBS-{number}',removed); template=empty_state(f'SYN-STATE-OBS-{number}')
        after=ns.construct_from_observation(template,o,'One incomplete modeled assumption; not ground truth',
                    [n['id'] for n in o['nodes']],[t['id'] for t in o['ties']])
        examples.append({'name':f'observation-assumption-{number}','observation':o,'after':after})
    first=examples[0]; replayed=ns.replay(s,first['delta'],first['receipt'])
    examples.append({'name':'deterministic-replay','sameResult':replayed==first['after'],'originalUnchanged':s==state()})
    metrics={v:ns.calculate(request(s,v,b if v=='FREEMAN_DEGREE_CENTRALIZATION' else None),s,b,auth)
             for v in ('DEGREE_RAW_UNDIRECTED','DENSITY_SIMPLE_UNDIRECTED','CLUSTERING_LOCAL_UNDIRECTED','FRAGMENTATION_UNREACHABLE_PAIRS','FREEMAN_DEGREE_CENTRALIZATION')}
    return {'recordClass':ns.SYNTHETIC,'label':'NOT A SCIENTIFIC MODEL','baseState':s,'examples':examples,'metrics':metrics,
            'realPersonData':False,'newActive':0}


def safe_output(path):
    path=Path(path).resolve(); allowed=(ns.ROOT/'reports/relational-state-v1').resolve()
    if not path.is_relative_to(allowed): raise ns.ValidationError('Output must be explicitly under reports/relational-state-v1')
    target=(path/'synthetic-validation.json').resolve()
    if not target.is_relative_to(allowed): raise ns.ValidationError('Symlink output escape')
    return target


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',required=True); args=p.parse_args()
    out=safe_output(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(demonstration(),sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('12 fictional demonstrations; no scientific activation or model execution')
