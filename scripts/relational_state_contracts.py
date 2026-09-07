"""Governed NS01–NS12 additive schemas; deterministic schema generation only."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'schemas/relational-state/v1'
BASE = 'https://psywerx.org/schemas/relational-state/v1/'
SYNTHETIC = 'SYNTHETIC / NON_PRODUCTION'
TEXT = {'type': 'string', 'minLength': 1}
ID = {'type': 'string', 'pattern': '^[A-Za-z][A-Za-z0-9_.:-]{2,127}$'}
HASH = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
REV = {'type': 'integer', 'minimum': 1}
TIME = {'type': 'string', 'format': 'date-time', 'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'}


def arr(item, minimum=0, unique=False):
    return {'type': 'array', 'items': item, 'minItems': minimum, 'uniqueItems': unique}


def nullable(item): return {'anyOf': [item, {'type': 'null'}]}
def enum(*items): return {'enum': list(items)}
def const(value): return {'const': value}


def obj(properties, optional=()):
    return {'type': 'object', 'additionalProperties': False,
            'required': [k for k in properties if k not in optional], 'properties': properties}


IDS = arr(ID, unique=True)
REF = obj({'id': ID, 'revision': REV, 'contentHash': HASH})
WINDOW = obj({'mode': enum('SNAPSHOT', 'INTERVAL'), 'start': TIME, 'end': TIME,
              'aggregation': enum('SNAPSHOT_AT_START', 'PERSISTENT_THROUGH_WINDOW')})
BOUNDARY = obj({'id': ID, 'revision': REV, 'includedNodeIds': IDS,
                'includedPopulationRule': TEXT, 'excludedPopulationRule': TEXT,
                'unknownPopulationRule': TEXT})
PROVENANCE = obj({'id': ID, 'method': enum('SYNTHETIC_FIXTURE', 'SCENARIO_STIPULATION', 'OBSERVATION_REFERENCE'),
                 'sourceLocators': arr(TEXT), 'description': TEXT})
ATTRIBUTE = obj({'name': TEXT, 'value': nullable({'type': ['number', 'string', 'boolean']}),
                'schemaUri': {'type': 'string', 'format': 'uri'}, 'provenanceId': ID, 'sensitive': {'type': 'boolean'}})
NODE = obj({'id': ID, 'active': {'type': 'boolean'}, 'memberships': IDS, 'provenanceId': ID,
            'attributes': arr(ATTRIBUTE)}, optional=('attributes',))
TIE = obj({'id': ID, 'objectKind': const('SOCIAL_TIE'), 'source': ID, 'target': ID,
           'tieTypeId': ID, 'layerId': ID, 'directed': {'type': 'boolean'},
           'weight': nullable({'type': 'number', 'minimum': 0}),
           'weightMeaning': nullable(TEXT), 'weightUnit': nullable(TEXT),
           'validFrom': TIME, 'validUntil': nullable(TIME), 'provenanceId': ID,
           'basis': enum('ASSUMED', 'OBSERVED', 'INFERRED'), 'observationRef': nullable(REF)})
OPPORTUNITY = obj({'id': ID, 'objectKind': const('CONTACT_OPPORTUNITY'), 'source': ID, 'target': ID,
                   'kind': enum('CONTACT', 'ASSIGNED_SEATING', 'PLATFORM_ACCESS'),
                   'enabled': nullable({'type': 'boolean'}), 'validFrom': TIME,
                   'validUntil': nullable(TIME), 'provenanceId': ID})
PRIVACY = obj({'classification': enum('SYNTHETIC', 'RESTRICTED'),
               'identityMapping': const('SEPARATE_NOT_RESOLVED'), 'externalIdentityReference': nullable(ID),
               'accessPolicy': const('CALLER_AUTHORIZATION_REQUIRED'), 'retentionPolicy': TEXT,
               'exportPolicy': enum('DENY_BY_DEFAULT', 'AGGREGATED_ONLY'), 'topologyMayIdentify': const(True)})
ASSUMPTIONS = obj({'missingNodes': TEXT, 'missingTies': TEXT, 'absentTieMeaning': const('UNKNOWN_UNLESS_EXPLICITLY_STIPULATED'),
                   'coverage': enum('COMPLETE_STIPULATED_FRAME', 'INCOMPLETE', 'UNKNOWN'),
                   'limitations': arr(TEXT, 1), 'realNetworkTruthClaim': const(False)})
CONSTRUCTION = obj({'observationRef': REF, 'assumption': TEXT, 'selectedNodeIds': IDS, 'selectedTieIds': IDS})


def schema(name, fields, optional=()):
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': BASE+name+'-v1.schema.json',
            'title': 'PSYWERX '+name+' V1', **obj({'schemaVersion': const('1.0.0'), **fields}, optional)}


STATE = schema('relational-state', {'objectKind': const('RELATIONAL_STATE'),
    'recordClass': enum('SCENARIO_STATE', SYNTHETIC), 'id': ID, 'scenarioId': ID, 'revision': REV,
    'parent': nullable(REF), 'contentHash': HASH, 'window': WINDOW, 'boundary': BOUNDARY,
    'nodes': arr(NODE), 'groups': IDS, 'ties': arr(TIE), 'opportunities': arr(OPPORTUNITY),
    'tieTypeIds': IDS, 'layerIds': IDS, 'riskSetOpportunityIds': IDS,
    'provenance': arr(PROVENANCE, 1), 'construction': arr(CONSTRUCTION), 'assumptions': ASSUMPTIONS,
    'privacy': PRIVACY, 'appliedDeltaIds': IDS, 'retiredTieIds': IDS,
    'scientificConsequences': arr(TEXT), 'causalExecutionAuthorized': const(False)})
STATE['properties']['scientificConsequences']['maxItems'] = 0
OBSERVATION = schema('network-observation', {'objectKind': const('NETWORK_OBSERVATION'),
    'recordClass': enum('OBSERVATION_DATA', SYNTHETIC), 'id': ID, 'scenarioId': ID, 'revision': REV, 'contentHash': HASH,
    'window': WINDOW, 'boundary': BOUNDARY, 'nodes': arr(NODE), 'ties': arr(TIE),
    'observationMethod': TEXT, 'samplingFrame': TEXT, 'inferredTieMethod': nullable(TEXT),
    'missingness': ASSUMPTIONS, 'provenance': arr(PROVENANCE, 1), 'privacy': PRIVACY,
    'automaticStateOverwrite': const(False)})


def op(name, fields): return obj({'operation': const(name), **fields})


OPERATIONS = [op('ADD_NODE', {'node': NODE, 'includeInBoundary': {'type': 'boolean'}}),
    op('DEACTIVATE_NODE', {'nodeId': ID, 'incidentPolicy': const('REMOVE_AND_RECORD')}),
    op('ADD_TIE', {'tie': TIE}), op('REMOVE_TIE', {'tieId': ID}),
    op('UPDATE_TIE_WEIGHT', {'tieId': ID, 'weight': nullable({'type': 'number', 'minimum': 0}),
                            'weightMeaning': nullable(TEXT), 'weightUnit': nullable(TEXT)}),
    op('CHANGE_MEMBERSHIP', {'nodeId': ID, 'groupIds': IDS}),
    op('CHANGE_BOUNDARY', {'boundary': BOUNDARY}),
    op('CHANGE_CONTACT_OPPORTUNITY', {'opportunity': OPPORTUNITY}),
    op('CHANGE_ACCESS', {'opportunityId': ID, 'enabled': nullable({'type': 'boolean'})})]
DELTA = schema('scenario-state-delta', {'objectKind': const('SCENARIO_STATE_DELTA'),
    'recordClass': enum('SCENARIO_OPERATION', SYNTHETIC), 'id': ID, 'scenarioId': ID,
    'expectedState': REF, 'effectiveAt': TIME,
    'basis': enum('STIPULATED_MODELED_OPERATION', 'ANALYTIC_BOUNDARY_SELECTION'),
    'provenance': PROVENANCE, 'occurrenceRef': nullable(REF), 'happeningTypeRef': nullable(REF),
    'realWorldSuccessClaim': const(False), 'empiricalEvidenceProduced': const(False),
    'operations': arr({'oneOf': OPERATIONS}, 1)})
RECEIPT = schema('state-receipt', {'objectKind': const('SCENARIO_OPERATION_RECEIPT'), 'deltaId': ID,
    'deltaHash': HASH, 'before': REF, 'after': REF, 'scenarioId': ID, 'effectiveAt': TIME,
    'operationOrder': arr(TEXT, 1), 'removedTieIds': IDS, 'removedOpportunityIds': IDS,
    'changeClass': enum('ANALYTIC_BOUNDARY_ONLY', 'STIPULATED_CONFIGURATION'),
    'causalContribution': const(False), 'empiricalEvidenceProduced': const(False),
    'ontologyRelationshipsEdited': const(0), 'receiptHash': HASH})
ENTITY_REF = obj({'id': ID, 'definitionVersion': TEXT, 'definitionHash': HASH})
METRIC = obj({'variant': enum('DEGREE_RAW_UNDIRECTED', 'DENSITY_SIMPLE_UNDIRECTED', 'CLUSTERING_LOCAL_UNDIRECTED',
                'FRAGMENTATION_UNREACHABLE_PAIRS', 'FREEMAN_DEGREE_CENTRALIZATION'),
              'tieTypeId': ID, 'layerId': ID, 'direction': const('UNDIRECTED'), 'loops': const(False),
              'weightPolicy': const('EXPLICIT_BINARY_UNWEIGHTED'), 'parallelTies': const(False),
              'normalization': enum('NONE', 'POSSIBLE_PAIRS', 'NEIGHBOR_PAIRS', 'SAME_SIZE_STAR'),
              'lowDegreeClustering': enum('NOT_APPLICABLE', 'ZERO_BY_SPECIFICATION')})
INPUT_SCHEMA = obj({'collectionSubject': const('ALL_NODES_OF_BOUND_STATE_BOUNDARY'),
    'completenessRule': const('EXACT_SET_EQUALITY_NO_MISSING_NO_EXTRA'), 'inputEntity': ENTITY_REF,
    'inputMetricVariant': const('DEGREE_RAW_UNDIRECTED'),
    'alignment': const('SAME_STATE_HASH_BOUNDARY_WINDOW_TYPE_LAYER'),
    'requiredExternalInputs': {'const': ['NODE_SET', 'NETWORK_STATE', 'BOUNDARY', 'WINDOW', 'METRIC_SPECIFICATION', 'MAXIMUM_BENCHMARK']}})
FINDING = obj({'id': ID, 'sourceId': ID, 'locator': TEXT, 'accessDepth': TEXT,
               'basis': const('DEFINITIONAL_CALCULATIONAL'), 'result': TEXT, 'limitations': arr(TEXT, 1),
               'empiricalCausalEvidence': const(False), 'overlap': TEXT})
BINDING = schema('collection-derivation-binding', {'objectKind': const('COLLECTION_DERIVATION_BINDING'),
    'recordClass': enum('SCIENTIFIC_RECORD', SYNTHETIC), 'id': ID, 'revision': REV,
    'targetRds': ENTITY_REF, 'inputContract': INPUT_SCHEMA,
    'metricVariant': const('FREEMAN_DEGREE_CENTRALIZATION'),
    'normalization': const('SAME_SIZE_SIMPLE_UNDIRECTED_STAR_MAXIMUM'),
    'calculationReference': const('SUM_MAX_DEGREE_MINUS_DEGREES_DIVIDED_BY_N_MINUS_1_TIMES_N_MINUS_2'),
    'minimumNodes': const(3), 'causalRelationship': const(False),
    'evidenceBasis': const('DEFINITIONAL_CALCULATIONAL'), 'sourceFindings': arr(FINDING, 1),
    'scopeLimitations': arr(TEXT, 1), 'sharedContributionIdentity': ID,
    'contributionPolicy': const('RECALCULATION_ONLY_NO_CAUSAL_SUM'),
    'lineage': obj({'candidateId': ID, 'candidateRevision': REV, 'candidateHash': HASH,
                    'scientificDecisionId': ID, 'architectureDecisionId': ID}),
    'governance': {'$ref': 'https://psywerx.org/schemas/relationship-intervention/v1/governance-v1.schema.json'}})
COLLECTION = obj({'subjectNodeIds': IDS, 'completeness': const('COMPLETE_ALIGNED'),
    'stateRef': REF, 'boundary': BOUNDARY, 'window': WINDOW, 'inputEntity': ENTITY_REF,
    'metric': METRIC, 'values': arr(obj({'nodeId': ID, 'value': {'type': 'integer', 'minimum': 0}}))})
BENCHMARK = obj({'kind': const('SAME_SIZE_SIMPLE_UNDIRECTED_STAR'), 'nodeCount': {'type': 'integer', 'minimum': 3},
                 'maximum': {'type': 'integer', 'minimum': 1}})
REQUEST = schema('calculation-request', {'objectKind': const('RDS_CALCULATION_REQUEST'), 'id': ID,
    'recordClass': enum('CALCULATION_REQUEST', SYNTHETIC), 'stateRef': REF, 'boundary': BOUNDARY, 'window': WINDOW,
    'targetRds': ENTITY_REF, 'metric': METRIC, 'bindingRef': nullable(REF), 'collection': nullable(COLLECTION),
    'externalBenchmark': nullable(BENCHMARK), 'useMode': enum('SYNTHETIC_VALIDATION', 'SCIENTIFIC_USE'),
    'contributionIdentity': ID, 'propagationRoutes': {'const': ['STATE_RECALCULATION']}})
CALC_RECEIPT = schema('calculation-receipt', {'objectKind': const('CALCULATION_RECEIPT'), 'requestId': ID,
    'requestHash': HASH, 'stateRef': REF, 'bindingRef': nullable(REF), 'targetRds': ENTITY_REF,
    'status': enum('CALCULATED_SYNTHETIC', 'UNSUPPORTED_OR_INCOMPLETE', 'NOT_AUTHORIZED'),
    'value': nullable({'type': ['number', 'object']}), 'reason': TEXT, 'limitations': arr(TEXT, 1),
    'contributionIdentity': ID, 'causalContribution': const(False), 'scientificUseEligible': const(False),
    'modelEligibility': const(False), 'practitionerActionEligibility': const(False), 'receiptHash': HASH})
LINK = schema('scenario-operation-reference', {'objectKind': const('SCENARIO_OPERATION_REFERENCE'),
    'occurrenceRef': nullable(REF), 'happeningTypeRef': nullable(REF), 'deltaRef': REF,
    'relation': const('REFERENCES_STIPULATED_OPERATION_NOT_EFFECT'), 'automaticExecution': const(False),
    'empiricalConsequenceClaim': const(False)})
SCHEMAS = {'relational-state': STATE, 'network-observation': OBSERVATION, 'scenario-state-delta': DELTA,
           'state-receipt': RECEIPT, 'collection-derivation-binding': BINDING, 'calculation-request': REQUEST,
           'calculation-receipt': CALC_RECEIPT, 'scenario-operation-reference': LINK}


def generate():
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    for name, value in SCHEMAS.items():
        (DIRECTORY/(name+'-v1.schema.json')).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__': generate()
