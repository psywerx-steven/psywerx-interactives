"""Optional deterministic scenario substrate. No ingestion, activation or causal execution.

Pure copy-on-write operations; scientific records stay in a separate governed
catalog. Numeric demonstrations execute only in explicit synthetic validation.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
import relational_state_contracts as contracts
import actions_events_v1 as ae
import relationship_intervention_v1 as ri

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = contracts.SYNTHETIC
BASELINE = '59cf40931b9d63811422dd2c9e648888178f9e09'
CATALOG = ROOT/'data/relational-state-v1/catalog.json'


class ValidationError(ValueError): pass


def require(condition, reason):
    if not condition: raise ValidationError(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@lru_cache(maxsize=1)
def schemas():
    values = [ae.read(p) for p in sorted(contracts.DIRECTORY.glob('*.schema.json'))]
    values += [ae.read(p) for p in sorted(ri.SCHEMA_DIR.glob('*.schema.json'))]
    registry = Registry().with_resources((v['$id'], Resource.from_contents(v)) for v in values)
    result = {}
    for name in contracts.SCHEMAS:
        value = ae.read(contracts.DIRECTORY/(name+'-v1.schema.json'))
        Draft202012Validator.check_schema(value)
        result[name] = Draft202012Validator(value, registry=registry, format_checker=FormatChecker())
    return result


def validate_schema(name, record):
    errors = sorted(schemas()[name].iter_errors(record), key=lambda e: str(list(e.path)))
    require(not errors, f'{name}: '+str(errors[0].message) if errors else '')


def canonical(record):
    r = copy.deepcopy(record)
    for key in ('nodes', 'ties', 'opportunities', 'provenance'):
        if key in r: r[key].sort(key=lambda v: v['id'])
    for node in r.get('nodes', []):
        node['memberships'].sort()
        if 'attributes' in node: node['attributes'].sort(key=lambda v: v['name'])
    for key in ('groups', 'tieTypeIds', 'layerIds', 'riskSetOpportunityIds', 'retiredTieIds'):
        if key in r: r[key].sort()
    if 'boundary' in r: r['boundary']['includedNodeIds'].sort()
    if 'construction' in r:
        for c in r['construction']:
            c['selectedNodeIds'].sort(); c['selectedTieIds'].sort()
        r['construction'].sort(key=lambda v: (v['observationRef']['id'], v['observationRef']['revision']))
    return r


def content_hash(record):
    r = canonical(record); r.pop('contentHash', None)
    return digest(r)


def seal(record):
    r = canonical(record); r['contentHash'] = content_hash(r); return r


def ref(record):
    return {'id': record['id'], 'revision': record['revision'], 'contentHash': record.get('contentHash', digest(record))}


def window_valid(w):
    require(w['start'] <= w['end'], 'Reversed time window')
    require((w['mode']=='SNAPSHOT' and w['start']==w['end'] and w['aggregation']=='SNAPSHOT_AT_START') or
            (w['mode']=='INTERVAL' and w['start']<w['end'] and w['aggregation']=='PERSISTENT_THROUGH_WINDOW'),
            'Static snapshot and temporal interval/aggregation must be distinguished')


def unique(rows, label):
    require(len({r['id'] for r in rows}) == len(rows), 'Duplicate '+label+' ID')


def data_integrity(r, observation=False):
    window_valid(r['window'])
    require(content_hash(r)==r['contentHash'], 'Content hash mismatch')
    for key in ('nodes', 'ties', 'provenance') + (() if observation else ('opportunities',)):
        unique(r[key], key)
    nodes = {n['id']: n for n in r['nodes']}; active = {n for n,v in nodes.items() if v['active']}
    require(set(r['boundary']['includedNodeIds']) <= active, 'Boundary references missing/inactive node')
    provenance = {p['id'] for p in r['provenance']}
    local_ids = [r['id'], r['scenarioId'], r['boundary']['id'], *nodes, *provenance]
    for n in nodes.values():
        require(n['id'].startswith(('NODE-', 'SYN-NODE-')), 'Scenario-local node namespace required')
        require(n['provenanceId'] in provenance, 'Node provenance unresolved')
        attrs = n.get('attributes', [])
        require(len({a['name'] for a in attrs})==len(attrs), 'Duplicate attribute')
        require(all(a['provenanceId'] in provenance for a in attrs), 'Attribute provenance unresolved')
    signatures = set()
    for t in r['ties']:
        require(t['id'].startswith(('TIE-', 'SYN-TIE-')), 'Social tie is not a PSYWERX Relationship')
        require(t['source'] in active and t['target'] in active, 'Missing/inactive tie endpoint')
        require(t['source'] != t['target'], 'Loop representation unsupported in V1')
        require(t['validUntil'] is None or t['validUntil']>t['validFrom'], 'Invalid half-open tie interval')
        require(t['provenanceId'] in provenance, 'Tie provenance unresolved')
        require((t['weight'] is None and t['weightMeaning'] is None and t['weightUnit'] is None) or
                (t['weight'] is not None and t['weightMeaning'] and t['weightUnit']), 'Weight meaning/unit must be explicit; unknown is not zero')
        pair = (t['source'], t['target']) if t['directed'] else tuple(sorted((t['source'], t['target'])))
        signature = (pair, t['tieTypeId'], t['layerId'], t['directed'])
        require(signature not in signatures, 'Duplicate dyad/type/layer; temporal multiedges unsupported')
        signatures.add(signature); local_ids.append(t['id'])
        if observation: require(t['basis'] in {'OBSERVED', 'INFERRED'}, 'Stipulated tie is not observation')
    if r['recordClass']==SYNTHETIC:
        require(all(i.startswith('SYN-') for i in local_ids), 'Synthetic-only local identities required')
        require(r['privacy']['classification']=='SYNTHETIC' and r['privacy']['externalIdentityReference'] is None,
                'Synthetic fixtures cannot contain real identity references')
    return nodes, active, provenance


def validate_state(s, observations=None):
    validate_schema('relational-state', s)
    nodes, active, provenance = data_integrity(s)
    require((s['revision']==1 and s['parent'] is None) or
            (s['revision']>1 and s['parent'] is not None and s['parent']['id']==s['id'] and s['parent']['revision']==s['revision']-1),
            'Immutable state parent/revision mismatch')
    require(all(set(n['memberships'])<=set(s['groups']) for n in nodes.values()), 'Unknown group membership')
    local = [s['id'], s['boundary']['id'], *s['groups']] + [v['id'] for k in ('nodes','ties','opportunities') for v in s[k]]
    require(len(local)==len(set(local)), 'Node/tie/group/state namespace collision')
    require(not set(s['retiredTieIds']) & {t['id'] for t in s['ties']}, 'Retired tie identity reused')
    for t in s['ties']:
        require(t['tieTypeId'] in s['tieTypeIds'] and t['layerId'] in s['layerIds'], 'Undeclared tie type/layer')
        if t['basis'] in {'OBSERVED','INFERRED'}:
            require(t['observationRef'] is not None and any(c['observationRef']==t['observationRef'] for c in s['construction']),
                    'Observed/inferred tie needs explicit construction/observation reference')
    for o in s['opportunities']:
        require(o['id'].startswith(('OPP-', 'SYN-OPP-')), 'Opportunity namespace required')
        require(o['source'] in active and o['target'] in active and o['source']!=o['target'], 'Invalid opportunity endpoint')
        require(o['provenanceId'] in provenance, 'Opportunity provenance unresolved')
        require(o['validUntil'] is None or o['validUntil']>o['validFrom'], 'Invalid opportunity interval')
    require(set(s['riskSetOpportunityIds'])<={o['id'] for o in s['opportunities']}, 'Risk set unresolved')
    if s['recordClass']==SYNTHETIC:
        require(all(i.startswith('SYN-') for i in local+s['tieTypeIds']+s['layerIds']), 'Synthetic namespace escape')
    require(len({(c['observationRef']['id'],c['observationRef']['revision']) for c in s['construction']})==len(s['construction']),
            'Duplicate observation construction mapping')
    if observations is not None:
        for construction in s['construction']:
            observation=observations.get(construction['observationRef']['id'])
            require(observation is not None, 'Missing referenced observation')
            validate_observation(observation)
            require(ref(observation)==construction['observationRef'] and observation['scenarioId']==s['scenarioId'], 'Observation mapping hash/scenario mismatch')
            require(set(construction['selectedNodeIds'])<={n['id'] for n in observation['nodes']}, 'Unobserved node mapping')
            require(set(construction['selectedTieIds'])<={t['id'] for t in observation['ties']}, 'Unobserved tie mapping')
    return True


def validate_observation(o):
    validate_schema('network-observation', o); data_integrity(o, True)
    if any(t['basis']=='INFERRED' for t in o['ties']): require(o['inferredTieMethod'], 'Inferred ties require method')
    return True


def construct_from_observation(template, observation, assumption, selected_node_ids, selected_tie_ids):
    """Explicitly construct an EMPTY new state; never overwrite or infer ties."""
    validate_state(template); validate_observation(observation)
    require(not template['nodes'] and not template['ties'] and template['revision']==1 and not template['construction'],
            'Observation construction requires an empty new state, not overwrite')
    require(template['scenarioId']==observation['scenarioId'] and bool(assumption.strip()), 'Explicit aligned construction assumption required')
    require((template['recordClass']==SYNTHETIC)==(observation['recordClass']==SYNTHETIC), 'Synthetic/real observation crossing')
    nodes={n['id']:n for n in observation['nodes']}; ties={t['id']:t for t in observation['ties']}
    require(len(set(selected_node_ids))==len(selected_node_ids) and set(selected_node_ids)<=set(nodes), 'Invalid observed node selection')
    require(len(set(selected_tie_ids))==len(selected_tie_ids) and set(selected_tie_ids)<=set(ties), 'Invalid observed tie selection')
    out=copy.deepcopy(template); out['nodes']=[copy.deepcopy(nodes[i]) for i in selected_node_ids]
    out['ties']=[copy.deepcopy(ties[i]) for i in selected_tie_ids]
    for t in out['ties']: t['observationRef']=ref(observation)
    provenance={p['id']:p for p in out['provenance']}
    for p in observation['provenance']:
        require(p['id'] not in provenance or provenance[p['id']]==p, 'Observation provenance collision')
        provenance[p['id']]=copy.deepcopy(p)
    out['provenance']=list(provenance.values()); out['window']=copy.deepcopy(observation['window'])
    out['boundary']=copy.deepcopy(observation['boundary'])
    out['boundary']['includedNodeIds']=[i for i in observation['boundary']['includedNodeIds'] if i in selected_node_ids]
    out['assumptions']=copy.deepcopy(observation['missingness']); out['assumptions']['limitations'].append(assumption)
    out['construction']=[{'observationRef':ref(observation),'assumption':assumption,
                         'selectedNodeIds':list(selected_node_ids),'selectedTieIds':list(selected_tie_ids)}]
    out=seal(out); validate_state(out,{observation['id']:observation}); return out


def apply_delta(state, delta):
    """Never mutates input or writes files. Caller controls persistence/permissions."""
    validate_state(state); validate_schema('scenario-state-delta', delta)
    if state['recordClass']==SYNTHETIC:
        require(delta['id'].startswith('SYN-') and delta['provenance']['id'].startswith('SYN-'), 'Synthetic delta namespace escape')
    require(delta['expectedState']==ref(state), 'Stale state revision/hash precondition')
    require(delta['scenarioId']==state['scenarioId'], 'Cross-scenario operation prohibited')
    require((delta['recordClass']==SYNTHETIC)==(state['recordClass']==SYNTHETIC), 'Synthetic/real state crossing')
    require(delta['id'] not in state['appliedDeltaIds'], 'Delta already applied')
    require(delta['effectiveAt']==state['window']['start'], 'V1 operations revise the declared as-of window; no implicit clock advancement/dynamic prediction')
    boundary_ops=[o for o in delta['operations'] if o['operation']=='CHANGE_BOUNDARY']
    require(not boundary_ops or len(delta['operations'])==1, 'Boundary selection cannot hide tie mutation')
    require((delta['basis']=='ANALYTIC_BOUNDARY_SELECTION')==bool(boundary_ops), 'Boundary change is not real tie formation')
    out=copy.deepcopy(state); removed=[]; removed_opportunities=[]
    p=delta['provenance']; previous=[x for x in out['provenance'] if x['id']==p['id']]
    require(not previous or previous==[p], 'Provenance ID collision')
    if not previous: out['provenance'].append(copy.deepcopy(p))
    for operation in delta['operations']:
        kind=operation['operation']; nodes={n['id']:n for n in out['nodes']}
        ties={t['id']:t for t in out['ties']}; opportunities={o['id']:o for o in out['opportunities']}
        if kind=='ADD_NODE':
            n=copy.deepcopy(operation['node']); require(n['id'] not in nodes, 'Node ID cannot be recycled')
            out['nodes'].append(n)
            if operation['includeInBoundary']: out['boundary']['includedNodeIds'].append(n['id']); out['boundary']['revision']+=1
        elif kind=='DEACTIVATE_NODE':
            identifier=operation['nodeId']; require(identifier in nodes and nodes[identifier]['active'], 'No active node to deactivate')
            nodes[identifier]['active']=False
            if identifier in out['boundary']['includedNodeIds']:
                out['boundary']['includedNodeIds'].remove(identifier); out['boundary']['revision']+=1
            removed += [t['id'] for t in out['ties'] if identifier in (t['source'],t['target'])]
            removed_opportunities += [o['id'] for o in out['opportunities'] if identifier in (o['source'],o['target'])]
            out['ties']=[t for t in out['ties'] if t['id'] not in removed]
            out['opportunities']=[o for o in out['opportunities'] if o['id'] not in removed_opportunities]
            out['riskSetOpportunityIds']=[i for i in out['riskSetOpportunityIds'] if i not in removed_opportunities]
        elif kind=='ADD_TIE':
            t=copy.deepcopy(operation['tie'])
            require(t['id'] not in ties and t['id'] not in out['retiredTieIds']+removed, 'Tie identity collision/recycling')
            out['ties'].append(t)
        elif kind=='REMOVE_TIE':
            require(operation['tieId'] in ties, 'No such tie')
            removed.append(operation['tieId']); out['ties']=[t for t in out['ties'] if t['id']!=operation['tieId']]
        elif kind=='UPDATE_TIE_WEIGHT':
            require(operation['tieId'] in ties, 'No such tie')
            for key in ('weight','weightMeaning','weightUnit'): ties[operation['tieId']][key]=operation[key]
        elif kind=='CHANGE_MEMBERSHIP':
            require(operation['nodeId'] in nodes and nodes[operation['nodeId']]['active'], 'No active member')
            nodes[operation['nodeId']]['memberships']=copy.deepcopy(operation['groupIds'])
        elif kind=='CHANGE_BOUNDARY':
            b=operation['boundary']; require(b['id']==state['boundary']['id'] and b['revision']==state['boundary']['revision']+1, 'Boundary revision mismatch')
            out['boundary']=copy.deepcopy(b)
        elif kind=='CHANGE_CONTACT_OPPORTUNITY':
            o=copy.deepcopy(operation['opportunity']); out['opportunities']=[x for x in out['opportunities'] if x['id']!=o['id']]+[o]
        elif kind=='CHANGE_ACCESS':
            require(operation['opportunityId'] in opportunities, 'No such contact opportunity')
            opportunities[operation['opportunityId']]['enabled']=operation['enabled']
        else: raise ValidationError('Unknown typed operation')
    out['retiredTieIds']+=removed; out['appliedDeltaIds'].append(delta['id'])
    out['parent']=ref(state); out['revision']+=1; out=seal(out); validate_state(out)
    receipt={'schemaVersion':'1.0.0','objectKind':'SCENARIO_OPERATION_RECEIPT','deltaId':delta['id'],
        'deltaHash':digest(delta),'before':ref(state),'after':ref(out),'scenarioId':state['scenarioId'],
        'effectiveAt':delta['effectiveAt'],'operationOrder':[o['operation'] for o in delta['operations']],
        'removedTieIds':sorted(removed),'removedOpportunityIds':sorted(removed_opportunities),
        'changeClass':'ANALYTIC_BOUNDARY_ONLY' if boundary_ops else 'STIPULATED_CONFIGURATION',
        'causalContribution':False,'empiricalEvidenceProduced':False,'ontologyRelationshipsEdited':0}
    receipt['receiptHash']=digest(receipt); validate_schema('state-receipt', receipt)
    return out, receipt


def replay(state, delta, expected_receipt):
    result, receipt=apply_delta(state,delta)
    require(receipt==expected_receipt, 'Receipt/replay mismatch')
    return result


def validate_operation_reference(link, delta, occurrences=None, types=None):
    validate_schema('scenario-operation-reference',link); validate_schema('scenario-state-delta',delta)
    require(link['deltaRef']=={'id':delta['id'],'revision':1,'contentHash':digest(delta)}, 'Delta reference mismatch')
    require(link['occurrenceRef']==delta['occurrenceRef'] and link['happeningTypeRef']==delta['happeningTypeRef'], 'Operation identity reference mismatch')
    for field, lookup in [('occurrenceRef',occurrences),('happeningTypeRef',types)]:
        if link[field] is not None:
            require(lookup is not None and link[field]['id'] in lookup, 'Scientific reference must resolve explicitly')
            require(link[field]==ref(lookup[link[field]['id']]), 'Scientific reference revision/hash mismatch')
    return True


def entity_reference(identifier):
    row=ri.Catalog.from_repository().entities[identifier]
    return {'id':identifier,'definitionVersion':'ENTITY_V0_3_GOVERNED_RECORD_HASH','definitionHash':ae.digest(row)}


def validate_binding(binding, authorizations=(), context=None):
    validate_schema('collection-derivation-binding',binding)
    context=context or ae.Context.repository()
    target=binding['targetRds']['id']; source=binding['inputContract']['inputEntity']['id']
    require(target=='RDS-0006' and source=='SOC-049', 'Unsupported governed collection variant/endpoints')
    require(context.entities[target]['entityType']=='RELATIONAL_DERIVED_STATE', 'Binding target must resolve to RDS, not causal target')
    require(binding['targetRds']==entity_reference(target) and binding['inputContract']['inputEntity']==entity_reference(source), 'Governed definition version/hash mismatch')
    require(len({f['id'] for f in binding['sourceFindings']})==len(binding['sourceFindings']), 'Duplicate source finding')
    require(all(f['sourceId'] in context.source_ids for f in binding['sourceFindings']), 'Derivation source unresolved')
    ri.SchemaSet().validate('governance',binding['governance'])
    ae.validate_lifecycle(binding,authorizations,context)
    if not context.synthetic:
        require(binding['recordClass']=='SCIENTIFIC_RECORD' and not binding['id'].startswith('SYN-'), 'Synthetic binding cannot enter scientific catalog')
        require(binding['governance']['activationStatus']=='INACTIVE', 'No Network State binding activation authorized')
    return True


def selected_graph(state, metric):
    require(metric['tieTypeId'] in state['tieTypeIds'] and metric['layerId'] in state['layerIds'], 'Metric selector unresolved')
    nodes=set(state['boundary']['includedNodeIds']); adjacency={n:set() for n in nodes}
    w=state['window']
    for tie in state['ties']:
        if tie['tieTypeId']!=metric['tieTypeId'] or tie['layerId']!=metric['layerId']: continue
        if not {tie['source'],tie['target']}<=nodes: continue
        persistent=tie['validFrom']<=w['start'] and (tie['validUntil'] is None or
             (tie['validUntil']>w['start'] if w['mode']=='SNAPSHOT' else tie['validUntil']>=w['end']))
        if not persistent: continue
        require(not tie['directed'], 'Directed metric variant unsupported; no silent collapse')
        require(tie['weight']==1 and tie['weightMeaning']=='BINARY_TIE_PRESENCE' and tie['weightUnit']=='1',
                'Metric requires explicitly binary unweighted ties; unknown/intensity not silently binarized')
        adjacency[tie['source']].add(tie['target']); adjacency[tie['target']].add(tie['source'])
    return adjacency


def require_collection(request,state,binding,degree):
    c=request['collection']; benchmark=request['externalBenchmark']
    require(c is not None and benchmark is not None and binding is not None, 'Complete collection/binding/external benchmark required')
    require(request['bindingRef']==ref(binding), 'Binding revision/hash mismatch')
    require(c['stateRef']==ref(state) and c['boundary']==state['boundary'] and c['window']==state['window'], 'Collection state/boundary/window mismatch')
    require(c['inputEntity']==binding['inputContract']['inputEntity'], 'Input definition mismatch')
    require(c['metric']['variant']=='DEGREE_RAW_UNDIRECTED' and c['metric']['normalization']=='NONE', 'Degree scores only, not other centralities')
    for key in ('tieTypeId','layerId','direction','loops','weightPolicy','parallelTies'):
        require(c['metric'][key]==request['metric'][key], 'Collection metric alignment mismatch')
    expected=set(state['boundary']['includedNodeIds'])
    require(set(c['subjectNodeIds'])==expected and len(c['values'])==len(expected), 'Incomplete/extra node-degree collection')
    values={r['nodeId']:r['value'] for r in c['values']}
    require(len(values)==len(c['values']) and set(values)==expected, 'Duplicate/missing actor scores')
    require(values==degree, 'Degree values do not match the bound network configuration')
    n=len(expected); require(n>=binding['minimumNodes'], 'Centralization normalization undefined for fewer than three nodes')
    require(benchmark['nodeCount']==n and benchmark['maximum']==(n-1)*(n-2), 'Missing/wrong same-size star maximum')
    require(request['contributionIdentity']==binding['sharedContributionIdentity'], 'Shared-contribution binding mismatch')


def calculate(request,state,binding=None,authorizations=()):
    """Explicit unsupported results, no scientific execution of inactive knowledge."""
    validate_schema('calculation-request',request); validate_state(state)
    receipt={'schemaVersion':'1.0.0','objectKind':'CALCULATION_RECEIPT','requestId':request['id'],
        'requestHash':digest(request),'stateRef':ref(state),'bindingRef':request['bindingRef'],'targetRds':request['targetRds'],
        'status':'UNSUPPORTED_OR_INCOMPLETE','value':None,'reason':'Unresolved variant/inputs',
        'limitations':['Deterministic modeled calculation only; not empirical causal evidence or a real-network truth estimate.',
                       *state['assumptions']['limitations']], 'contributionIdentity':request['contributionIdentity'],
        'causalContribution':False,'scientificUseEligible':False,'modelEligibility':False,'practitionerActionEligibility':False}
    try:
        require(request['stateRef']==ref(state) and request['boundary']==state['boundary'] and request['window']==state['window'], 'Requested state/boundary/window version mismatch')
        variant=request['metric']['variant']
        targets={'DEGREE_RAW_UNDIRECTED':'SOC-049','DENSITY_SIMPLE_UNDIRECTED':'SOC-052','CLUSTERING_LOCAL_UNDIRECTED':'SOC-053',
                 'FRAGMENTATION_UNREACHABLE_PAIRS':'RDS-0007','FREEMAN_DEGREE_CENTRALIZATION':'RDS-0006'}
        require(request['targetRds']==entity_reference(targets[variant]), 'Exact RDS definition/variant mismatch')
        if request['useMode']!='SYNTHETIC_VALIDATION':
            receipt.update(status='NOT_AUTHORIZED',reason='No active Network State calculation binding / production execution registration; scientific activation not authorized')
        else:
            require(request['recordClass']==SYNTHETIC and state['recordClass']==SYNTHETIC and request['id'].startswith('SYN-'), 'Synthetic evaluation cannot operate on real-person/state data')
            adjacency=selected_graph(state,request['metric']); n=len(adjacency); degree={k:len(v) for k,v in adjacency.items()}
            norm={'DEGREE_RAW_UNDIRECTED':'NONE','DENSITY_SIMPLE_UNDIRECTED':'POSSIBLE_PAIRS',
                  'CLUSTERING_LOCAL_UNDIRECTED':'NEIGHBOR_PAIRS','FRAGMENTATION_UNREACHABLE_PAIRS':'POSSIBLE_PAIRS',
                  'FREEMAN_DEGREE_CENTRALIZATION':'SAME_SIZE_STAR'}[variant]
            require(request['metric']['normalization']==norm, 'Metric normalization mismatch')
            if variant!='FREEMAN_DEGREE_CENTRALIZATION':
                require(request['bindingRef'] is None and request['collection'] is None and request['externalBenchmark'] is None,
                        'Unrelated binding/collection cannot confer execution authority')
            if variant=='DEGREE_RAW_UNDIRECTED': value=degree
            elif variant=='DENSITY_SIMPLE_UNDIRECTED':
                require(n>=2,'Density denominator undefined'); value=sum(degree.values())/(n*(n-1))
            elif variant=='CLUSTERING_LOCAL_UNDIRECTED':
                require(request['metric']['lowDegreeClustering']=='ZERO_BY_SPECIFICATION', 'Low-degree convention required')
                value={k:(sum(b in adjacency[a] for a,b in combinations(v,2))/(len(v)*(len(v)-1)/2) if len(v)>1 else 0) for k,v in adjacency.items()}
            elif variant=='FRAGMENTATION_UNREACHABLE_PAIRS':
                require(n>=2,'Unreachable-pair denominator undefined'); unseen=set(adjacency); sizes=[]
                while unseen:
                    todo=[min(unseen)]; seen=set()
                    while todo:
                        node=todo.pop()
                        if node in seen: continue
                        seen.add(node); todo.extend(adjacency[node]-seen)
                    unseen-=seen; sizes.append(len(seen))
                value=1-sum(k*(k-1) for k in sizes)/(n*(n-1))
            else:
                require(binding is not None,'Collection derivation binding required')
                validate_binding(binding,authorizations)
                require_collection(request,state,binding,degree)
                value=sum(max(degree.values())-v for v in degree.values())/request['externalBenchmark']['maximum']
            receipt.update(status='CALCULATED_SYNTHETIC',value=value,reason='Exact declared synthetic variant calculated; no scientific/model/practitioner eligibility conferred')
    except (ValidationError, KeyError) as error:
        receipt['reason']=str(error)
    receipt['receiptHash']=digest(receipt); validate_schema('calculation-receipt',receipt)
    return receipt


def validate_repository():
    for name,value in contracts.SCHEMAS.items():
        require(ae.read(contracts.DIRECTORY/(name+'-v1.schema.json'))==value,'Generated schema drift '+name)
        Draft202012Validator.check_schema(value)
    if not CATALOG.exists(): return {'bindings':0,'activeBindings':0}
    catalog=ae.read(CATALOG)
    require(set(catalog)=={'schemaVersion','bindings','authorizations'} and catalog['schemaVersion']=='1.0.0','Invalid derivation catalog')
    unique(catalog['bindings'],'binding'); unique([{'id':a['decisionId']} for a in catalog['authorizations']],'authorization')
    for auth in catalog['authorizations']: ae.schema_set().validate('authorization',auth)
    for binding in catalog['bindings']: validate_binding(binding,catalog['authorizations'])
    return {'bindings':len(catalog['bindings']),'activeBindings':sum(ri.governed_active(b) for b in catalog['bindings']),
            'statesInScientificCatalog':0,'causalRelationshipsAdded':0,'scientificEffectTargetsUnchanged':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--validate-repository',action='store_true',required=True)
    parser.parse_args(); print(json.dumps(validate_repository(),indent=2))
