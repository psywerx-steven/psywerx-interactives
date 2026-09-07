"""Candidate-only Layer reconciliation/reporting. No scientific judgment generation."""
from __future__ import annotations
import argparse
import hashlib
import random
import re
import sys
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote
import psychological_layer_v1 as p
import build_psychological_family_v1 as b

DECISION = 'PENDING — APPROVE / MODIFY / REJECT'
DISPOSITIONS = ['RETAIN_AS_IS','RETAIN_V1_INCOMPLETE','REVISION_CANDIDATE','RETYPE_CANDIDATE',
                'SPLIT_CANDIDATE','MERGE_DUPLICATE_CANDIDATE','DEPRECATION_CANDIDATE',
                'RESEARCH_NEEDED','BLOCKED_NEEDS_GOVERNANCE_INPUT']
SAMPLE_COMMIT = 'd43a2c0c422ed19d310c01380813982a9959f890'


def load():
    return {f:{'research':p.read(p.STORE/f/'research.json'),
               'inputs':p.read(p.STORE/f/'evidence-inputs.json'),
               'workspace':p.read(p.STORE/f/'workspace.json'),
               'ledger':p.read(p.STORE/f/'actions-events-search-ledger.json'),
               'manifest':p.read(p.STORE/f/'AUDIT_MANIFEST.json')} for f in p.FAMILIES}


def sample_records():
    """Reproducible random sample, selected before the closeout judgment file."""
    result=[]
    for family,data in load().items():
        rng=random.Random(int(hashlib.sha256((p.PROGRAM+'/'+family+'/skeptical-sample-v1').encode()).hexdigest(),16))
        # Freeze the selection universe before any skeptical-review correction.
        path=(p.STORE/family/'evidence-inputs.json').relative_to(p.ROOT).as_posix()
        original=json.loads(subprocess.check_output(['git','show',f'{SAMPLE_COMMIT}:{path}'],cwd=p.ROOT).decode('utf-8'))
        spec=rng.choice(sorted(original['assertions'],key=lambda x:x['id']))
        findings={x['key']:x for x in original['findings']}
        selected=rng.choice(sorted(spec['findingKeys']))
        result.append({'familyId':family,'assertion':spec,'finding':findings[selected]})
    return result


def rows():
    data=load(); reg=p.read(p.STORE/'relationship-review-registry.json')
    issues=p.read(p.STORE/'cross-family-issues.json'); result=[]
    def issue_ids(ids):
        return sorted(x['id'] for x in issues if set(x.get('recordIds',[])) & set(ids))
    for identifier,x in reg.items():
        rv=x['review']; frozen=x['frozenRecord']; a,z=p.endpoints(frozen)
        d=x['primaryDisposition']; group='A' if d=='RETAIN_AS_IS' else 'B' if d=='RETAIN_V1_INCOMPLETE' else 'L' if d=='RESEARCH_NEEDED' else 'M' if d=='BLOCKED_NEEDS_GOVERNANCE_INPUT' else 'C'
        result.append({'id':identifier,'group':group,'type':'EXISTING_RELATIONSHIP_REVIEW',
            'family':x['ownerFamilyId'],'processingFamily':x['processingFamilyId'],
            'proposition':f'{a} {frozen.get("predicate","CAUSES")} {z}', 'endpoints':[a,z],
            'lifecycle':'EXISTING_PRODUCTION_UNCHANGED','recommendation':d,
            'evidence':rv['evidence'],'strength':rv['strength'],'confidence':rv['confidence'],
            'support':rv['rationale'],'nullContrary':rv['nullContrary'],
            'boundaries':rv.get('proposal') or frozen.get('conditionsModerators','See frozen scope'),
            'risk':rv['rationale'],'sources':rv['sources'],'issueIds':issue_ids([identifier,a,z]),
            'priority':'HIGH' if group in {'C','M'} else 'NORMAL','humanDecision':DECISION})
    for family,d in data.items():
        inp=d['inputs']; fs={x['key']:x for x in inp['findings']}
        for a in inp['assertions']:
            fnd=[fs[k] for k in a['findingKeys']]
            result.append({'id':a['id'],'group':'D' if a['type']=='RELATIONSHIP' else 'J',
                'type':a['type'],'family':a.get('ownerFamilyId',family),'processingFamily':family,
                'proposition':a['scope'],'endpoints':[a.get('source',a.get('typeId')),a['target']],
                'lifecycle':a['status'],'recommendation':a['status'],'evidence':a['disposition'],
                'strength':a['strength'],'confidence':a['confidence'],
                'support':' '.join(x['result'] for x in fnd if x['disposition']=='SUPPORTS') or 'See scoped mixed/insufficient findings; no isolated supportive contrast asserted.',
                'nullContrary':' '.join(x['result'] for x in fnd if x['disposition']!='SUPPORTS') or 'No contradictory/null contrast extracted; absence is not proof of unanimity.',
                'boundaries':a['scope'],'risk':a.get('risk',a['rationale']),
                'sources':sorted({x['sourceId'] for x in fnd}),
                'issueIds':issue_ids([a['target'],a.get('source')]),'priority':'HIGH' if a['status']=='REVIEW_READY' else 'NORMAL',
                'sharedContributionId':a['sharedContributionId'],'humanDecision':DECISION})
        for ht in inp['happeningTypes']:
            result.append({'id':ht['id'],'group':'I','type':'HAPPENING_TYPE_IDENTITY','family':family,'processingFamily':family,
                'proposition':ht['name'],'endpoints':[],'lifecycle':'REVIEW_READY','recommendation':'REVIEW_IDENTITY_ONLY',
                'evidence':'OPERATION_PROVENANCE_NOT_EFFICACY','strength':'NOT_ASSESSED','confidence':'NOT_ASSESSED',
                'support':ht['description'],'nullContrary':'No efficacy inference from identity. See separate effects.',
                'boundaries':ht['description'],'risk':ht['constraints'],'sources':ht['sources'],
                'issueIds':[],'priority':'NORMAL','humanDecision':DECISION})
        for h in d['research']['hypotheses']:
            if h['status']=='REVIEW_READY':
                continue  # Discovery paths link formal records, never a second vote.
            group='K' if h['status']=='REJECTED_HYPOTHESIS' else 'M' if h['status']=='BLOCKED_NEEDS_GOVERNANCE_INPUT' else 'L'
            result.append({'id':h['id'],'group':group,'type':'HYPOTHESIS_LEDGER','family':family,'processingFamily':family,
                'proposition':h['question'],'endpoints':[h.get('source'),h.get('target')],
                'lifecycle':'NON_GOVERNED_LEDGER','recommendation':h['status'],
                'evidence':'NOT_A_FORMAL_ASSERTION','strength':'NOT_ASSESSED','confidence':'NOT_ASSESSED',
                'support':h['reason'],'nullContrary':h['reason'],'boundaries':h['reason'],'risk':h['reason'],
                'sources':h['sources'],'issueIds':issue_ids([h.get('source'),h.get('target')]),
                'priority':'HIGH' if group=='M' else 'NORMAL','humanDecision':DECISION})
    for x in issues + p.read(p.STORE/'architecture-escalations.json'):
        result.append({'id':x['id'],'group':'M' if x['status']=='BLOCKED_NEEDS_GOVERNANCE_INPUT' else 'L',
            'type':'SHARED_ISSUE_NOT_SCIENTIFIC_RECORD','family':x.get('ownerFamilyId',x.get('familyId')),
            'processingFamily':x.get('familyId',x.get('familyIds',[None])[0]),'proposition':x['question'],
            'endpoints':x.get('entityIds',x.get('recordIds',[])), 'lifecycle':'NON_GOVERNED_LEDGER',
            'recommendation':x['status'],'evidence':'SEE_LINKED_FAMILY_REVIEW','strength':'NOT_ASSESSED','confidence':'NOT_ASSESSED',
            'support':x.get('finding',x['question']),'nullContrary':'See linked source/construct reviews.',
            'boundaries':x['question'],'risk':'Do not resolve by silent canonical edits or schema expansion.',
            'sources':[],'issueIds':[x['id']],'priority':'HIGH' if x['status']=='BLOCKED_NEEDS_GOVERNANCE_INPUT' else 'NORMAL','humanDecision':DECISION})
    return sorted(result,key=lambda x:(x['group'],x['family'] or '',{'STRONG':0,'MODERATE':1,'LIMITED':2}.get(x['strength'],3),{'HIGH':0,'MODERATE':1,'LOW':2}.get(x['confidence'],3),x['priority']!='HIGH',x['id']))


def graph_flags():
    edges=p.read(p.STORE/'baseline.json')['activeEdges']
    nodes={v for e in edges for v in (e['source'],e['target'])}
    reach={n:set() for n in nodes};degree=Counter()
    for e in edges:
        reach[e['source']].add(e['target'])
        degree.update([e['source'],e['target']])
    for k in sorted(nodes):
        for n in sorted(nodes):
            if k in reach[n]:reach[n]|=reach[k]
    components=set()
    for n in nodes:
        component=tuple(sorted(v for v in nodes if v in reach[n] and n in reach[v]))
        if component:components.add(component)
    return {'scope':'Frozen incident subgraph only; not a whole-ontology cycle census',
            'cyclicComponents':sorted(components),
            'topPsychologicalDegrees':sorted(((n,d) for n,d in degree.items() if n.startswith('PSY-')),key=lambda x:(-x[1],x[0]))[:10],
            'interpretation':'Flags only; reachability is not mediation or executable causal evidence.'}


def collect():
    data=load(); baseline=p.read(p.STORE/'baseline.json'); reg=p.read(p.STORE/'relationship-review-registry.json')
    states=Counter(); finding_states=Counter(); bases=Counter(); unique_findings=set(); sources=set(); referenced=set(); hypotheses=Counter(); semantics=Counter(); families=[]; origins=Counter(); domains=Counter(); properties=defaultdict(Counter)
    assertion_count=ht_count=rel_count=effect_count=attached=0
    for family,d in data.items():
        inp=d['inputs']; r=d['research']; referenced.update(s for e in r['entityReviews'] for s in e['sources'])
        referenced.update(s for h in r['hypotheses'] for s in h['sources'])
        referenced.update(s for x in r['existingReviews'] for s in x['sources'])
        for h in r['hypotheses']: hypotheses[h['status']]+=1;semantics[h['semantics']]+=1
        for collection in p.ae.COLLECTIONS:
            for record in d['workspace']['passB'][collection]:states[record['governance']['lifecycleStatus']]+=1
        for record in d['workspace']['passA']['relationshipCandidates']+d['workspace']['passA']['evidence']:
            states[record['governance']['lifecycleStatus']]+=1
        for spec in inp['assertions']:
            assertion_count+=1
            if spec['type']=='RELATIONSHIP':rel_count+=1
            else:effect_count+=1
            fs={x['key']:x for x in inp['findings']}
            for key in spec['findingKeys']:
                f=fs[key];attached+=1;unique_findings.add((family,key));sources.add(f['sourceId']);finding_states[f['disposition']]+=1;bases[f['basis']]+=1
        ht_count+=len(inp['happeningTypes'])
        for x in inp['happeningTypes']:origins.update(x['origins']);domains[x['domain']]+=1;referenced.update(x['sources'])
        for x in d['ledger']['drivers']:
            for prop,val in x['effectProperties'].items():properties[prop][val]+=1
        families.append({**d['manifest'],'primaryReviews':len(r['existingReviews']),
            'consultedReusedReviews':len(r.get('reusedExistingReviewIds',[])),
            'hypotheses':dict(Counter(x['status'] for x in r['hypotheses'])),
            'reviewedSourceIds':sorted({s for e in r['entityReviews'] for s in e['sources']}|{s for h in r['hypotheses'] for s in h['sources']}|{s for x in r['existingReviews'] for s in x['sources']}|{x['sourceId'] for x in inp['findings']})})
    referenced|=sources
    allrows=rows(); registry=p.read(p.STORE/'candidate-source-registry.json')
    return {'programId':p.PROGRAM,'baselineCommit':p.BASELINE,'baseline':baseline['summary'],'productionCounts':baseline['productionCounts'],
        'familiesCompleted':len(families),'driversReviewed':sum(x['driversSearched'] for x in families),
        'entitiesReviewed':sum(x['entitiesReviewed'] for x in families),'rdsReviewed':1,
        'existingReviewedOnce':len(reg),'existingDispositions':{k:sum(x['primaryDisposition']==k for x in reg.values()) for k in DISPOSITIONS},
        'newRelationships':rel_count,'newRelationshipSemantics':{'CAUSAL':rel_count,'ASSOCIATION':0,'DERIVATIONAL':0,'SEMANTIC':0,'TEMPORAL':0,'MODERATION':0,'CAUSAL_PATHWAY':0},
        'happeningTypes':ht_count,'effectAssertions':effect_count,'evidenceAssessments':assertion_count,
        'sourceFindingsAttached':attached,'uniqueSourceResultExtractions':len(unique_findings),
        'sourceFindingDispositionAttached':dict(finding_states),'sourceFindingBasisAttached':dict(bases),
        'assessmentDispositions':dict(Counter(a['disposition'] for d in data.values() for a in d['inputs']['assertions'])),
        'sourceRegistryEntries':len(registry),'supplementalSources':sum(x['id'].startswith('SRC-CAND-') for x in registry),
        'canonicalSourcesReferenced':sorted(s for s in referenced if not s.startswith('SRC-CAND-')),
        'sourcesDirectlyUsedInAssertions':sorted(sources),'uniqueReferencedSources':len(referenced),
        'sourceOverlapIssues':len(p.read(p.STORE/'source-overlap-registry.json')),
        'hypothesisDispositions':dict(hypotheses),'hypothesisSemanticFunnel':dict(semantics),
        'formalScientificLifecycle':dict(states),'newGoverned':0,'newActive':0,
        'architectureEscalations':len(p.read(p.STORE/'architecture-escalations.json')),
        'sharedIssues':len(p.read(p.STORE/'cross-family-issues.json')),
        'candidateIdentityOrigins':dict(origins),'candidateIdentityDomains':dict(domains),
        'effectPropertyLedgerCoverage':{k:dict(v) for k,v in properties.items()},
        'driverLedgersWithoutFormalEffect':sum(not x['candidateEffectIds'] for d in data.values() for x in d['ledger']['drivers']),
        'governanceDecisionRows':len(allrows),'decisionGroups':dict(Counter(x['group'] for x in allrows)),
        'decisionPriority':dict(Counter(x['priority'] for x in allrows)),
        'families':families,'graphFlags':graph_flags(),'protectedComparison':p.check_protected(),
        'limitations':['Bounded structured audits, not135 formal systematic reviews.','Coverage is not scientific completeness.','Hypotheses, shared issues and supporting evidence are not independent scientific propositions.','All human decisions PENDING; no governance/activation/source registration/merge.']}


def validate(require_review=True):
    s=collect();data=load();reg=p.read(p.STORE/'relationship-review-registry.json')
    assert (s['familiesCompleted'],s['driversReviewed'],s['rdsReviewed'],s['entitiesReviewed'],s['existingReviewedOnce'])==(14,134,1,135,111)
    all_review_ids=[x['id'] for d in data.values() for x in d['research']['existingReviews']]
    assert len(all_review_ids)==len(set(all_review_ids))==len(reg) and set(all_review_ids)==set(reg)
    prog=p.read(p.STORE/'progress.json')
    for f,d in data.items():
        assert all(v=='DONE' for v in prog['families'][f].values())
        assert d['manifest']['localComplete'] and d['research']['status']=='LOCAL_COMPLETE'
        ids={k for k,v in reg.items() if f in v['psychologicalFamilyIds']}
        assert ids=={x['id'] for x in d['research']['existingReviews']}|set(d['research'].get('reusedExistingReviewIds',[]))
        assert not p.ae.validate_workspace(d['workspace'],b.context())['productionEligible']
        for collection in p.ae.COLLECTIONS:
            for x in d['workspace']['passB'][collection]:
                assert x['governance']['activationStatus']=='NOT_ELIGIBLE'
        for x in d['ledger']['drivers']:
            assert (len(x['originLayerSearch']),len(x['domainSearch']),len(x['effectProperties']))==(8,9,11)
            assert x['activationStatus']=='NOT_ELIGIBLE'
            assert not any(x[k] for k in ('scientificUseEligibility','modelEligibility','practitionerActionEligibility'))
    assert not ({'GOVERNED','ACTIVE'} & set(s['formalScientificLifecycle']))
    assert b.validate_sources()==s['sourceRegistryEntries']
    for issue in p.read(p.STORE/'cross-family-issues.json'):
        for f in issue['familyIds']:
            if f in p.FAMILIES: assert issue['consultation'][f]=='CANDIDATE_REVIEW_COMPLETE',(issue['id'],f)
    cr=p.read(p.STORE/'candidate-proposition-registry.json')
    assert len(cr)==len({tuple(x['semanticKey']) for x in cr})
    ht=p.read(p.STORE/'actions-events-identity-registry.json')
    assert len(ht)==len({x['identityKey'] for x in ht})
    decisions=rows();assert len(decisions)==len({x['id'] for x in decisions})
    if require_review:
        review=p.read(p.STORE/'layer-reconciliation.json')
        expected={x['familyId']:x for x in sample_records()}
        assert review['status']=='COMPLETE' and len(review['randomSampleReviews'])==14
        assert {x['familyId'] for x in review['randomSampleReviews']}==set(p.FAMILIES)
        for x in review['randomSampleReviews']:
            e=expected[x['familyId']]
            assert (x['assertionId'],x['findingKey'])==(e['assertion']['id'],e['finding']['key'])
            assert x['outcome'] in {'RETAIN_CANDIDATE_SCOPE','DOWNGRADED','CORRECTED_MECHANICAL','SCOPED_EVIDENCE_CORRECTION'}
        assert not review['productionChangesAuthorized']
    return s


def link_check():
    errors=[];checked=0
    for f in p.DOCS.rglob('*.md'):
        text=re.sub(r'```.*?```','',f.read_text(encoding='utf-8'),flags=re.S)
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',text):
            target=match.group(1).strip().strip('<>')
            if target.startswith(('https:','http:','mailto:','#')):continue
            target=unquote(target.split('#')[0])
            if target and not (f.parent/target).resolve().exists():errors.append((str(f),target))
            checked+=1
    if errors:raise ValueError(errors)
    return {'checkedLocalLinks':checked,'errors':[]}


def render():
    s=validate();review=p.read(p.STORE/'layer-reconciliation.json');rr=rows()
    p.write(p.STORE/'layer-summary.json',s);p.write(p.STORE/'governance-index.json',rr)
    p.write(p.DOCS/'PSYCHOLOGICAL_LAYER_AUDIT_MANIFEST.json',s)
    header=['# Psychological Layer — candidate-only closeout','',f'Program `{p.PROGRAM}`; frozen main `{p.BASELINE}`.','',
        'All14 bounded Family audits complete. Human scientific governance remains PENDING. No new GOVERNED/ACTIVE, source registration, canonical modification, external Family audit or PR merge.','']
    def out(name,lines):p.write(p.DOCS/name,'\n'.join(header+lines).rstrip()+'\n')
    def code(v):return ['```json',p.encode(v).strip(),'```','']
    out('PSYCHOLOGICAL_LAYER_RELATIONSHIP_SUMMARY.md',code({k:s[k] for k in ['existingReviewedOnce','existingDispositions','newRelationshipSemantics','graphFlags']})+
        ['111 unique production propositions, all causal:19 within-Family,41 Psychological cross-Family,44 incoming/7outgoing cross-Layer. V3 projections add zero. No inactive/deprecated incident proposition was found at baseline.',
         '', 'Review once in shared registry; both endpoint Families consult. Existing owner remains unchanged. Candidate REL0001 owner INF-F07; Psychological endpoint consultation completed without auditing the external Family.','']+review['graphReview'])
    out('PSYCHOLOGICAL_LAYER_CROSS_FAMILY_ISSUES.md',review['ownershipReview']+['','| Issue | Families | Classification | Question |','|---|---|---|---|']+
        [f"| {x['id']} | {', '.join(x['familyIds'])} | {x.get('classification',x['status'])} | {x['question']} |" for x in p.read(p.STORE/'cross-family-issues.json')])
    out('PSYCHOLOGICAL_LAYER_CONSTRUCT_BOUNDARIES.md',review['constructReview']+['','See [shared issue map](PSYCHOLOGICAL_LAYER_CROSS_FAMILY_ISSUES.md). No canonical synonym, class or definition was changed.'])
    out('PSYCHOLOGICAL_LAYER_ACTIONS_EVENTS_SUMMARY.md',code({k:s[k] for k in ['happeningTypes','effectAssertions','candidateIdentityOrigins','candidateIdentityDomains','driverLedgersWithoutFormalEffect','effectPropertyLedgerCoverage']})+review['identityAndContributionReview']+
        ['', 'Every134Driver ledger considers8origins/9domains/11properties. NOT_INVESTIGATED means no exact evidence extracted for that cell; the dimensions are not query quotas. All formal effects target Drivers;0exact-Relationship effects,0moderations,0pathways. No direct RDS or scenario-state target.'])
    out('PSYCHOLOGICAL_LAYER_EVIDENCE_SUMMARY.md',code({k:s[k] for k in ['sourceRegistryEntries','supplementalSources','uniqueReferencedSources','sourcesDirectlyUsedInAssertions','sourceFindingsAttached','uniqueSourceResultExtractions','sourceFindingDispositionAttached','sourceFindingBasisAttached','assessmentDispositions','sourceOverlapIssues']})+review['sourceReview']+
        ['', 'Canonical source references used/reviewed (some are alignment problems, not endorsements): '+', '.join(s['canonicalSourcesReferenced']), '', 'Attached finding counts include same result attached to both Relationship/EffectAssertion. Unique extraction and overlap registries prevent interpreting this as replication. Basis counts are findings, not independent studies. Bibliographic-only access is not a full-text review.'])
    out('PSYCHOLOGICAL_LAYER_REJECTIONS.md',code(s['hypothesisDispositions'])+['Rejections are pilot recommendations, not human-governed REJECTED transitions. Research-needed hypotheses are not formal assertions. See [governance index](PSYCHOLOGICAL_LAYER_GOVERNANCE_INDEX.md).'])
    out('PSYCHOLOGICAL_LAYER_ARCHITECTURE_ESCALATIONS.md',review['architectureReview']+code(p.read(p.STORE/'architecture-escalations.json')))
    out('PSYCHOLOGICAL_LAYER_COMPLETENESS_REPORT.md',code({k:s[k] for k in ['familiesCompleted','driversReviewed','rdsReviewed','entitiesReviewed','existingReviewedOnce','formalScientificLifecycle','hypothesisDispositions','newGoverned','newActive','protectedComparison']})+
        ['| Family | Entities | Incident / primary reviews | New REL / HT / EA | Supplemental sources |','|---|---:|---:|---:|---:|']+
        [f"| [{x['familyId']}]({x['familyId']}/GOVERNANCE_DECISION_PACKAGE.md) | {x['entitiesReviewed']} | {x['existingIncidentReviewed']} / {x['primaryReviews']} | {x['newRelationships']} / {x['happeningTypes']} / {x['effectAssertions']} | {x['supplementalSourcesInFamily']} |" for x in s['families']]+
        ['', 'Incident and source counts are not additive across Families. Per-Family manifests retain local provenance; final Layer receipt is authoritative for reconciliation. Coverage is not scientific completeness.', '', '## RDS', '', *review['rdsReview'], '', '## Independent sampled self-audit', '', 'Seed: SHA256(program/Family/skeptical-sample-v1), one assertion and finding per Family, chosen before review. This is a separate skeptical pass by the same assistant, not an external human peer review.', '', *[f"- {x['familyId']} / {x['assertionId']} / {x['findingKey']}: {x['outcome']}. {x['reason']}" for x in review['randomSampleReviews']]])
    groups={'A':'Existing retain','B':'Existing V1 incomplete','C':'Existing revision/retype/deprecation proposals','D':'New causal candidates','E':'New noncausal candidates','F':'Derivational candidates','G':'Moderation candidates','H':'CausalPathway candidates','I':'HappeningType identities','J':'EffectAssertions','K':'Rejected hypotheses','L':'Research-needed/shared issues','M':'Governance/architecture blocked'}
    lines=code({k:s[k] for k in ['governanceDecisionRows','decisionGroups','decisionPriority']})+review['governanceWorkload']+['','Rows include ledger/shared-question decisions, not that many independent scientific claims. Existing revision proposals are included in their existing-edge row, not counted twice. Evidence is attached to each assertion, not an independent activation request.','']
    for group,title in groups.items():
        lines += [f'## {group}. {title}','']
        selected=[x for x in rr if x['group']==group]
        if not selected:lines+=['None retained as formal records.',''];continue
        for x in selected:
            lines += [f"### {x['id']} — {x['family']}",'',x['proposition'],'',
                f"Type: {x['type']}; endpoints/target: {', '.join(str(i) for i in x['endpoints'] if i)}. Lifecycle: {x['lifecycle']}. Recommendation: {x['recommendation']}. Priority: {x['priority']}.",'',
                f"Evidence: {x['evidence']} / {x['strength']} / {x['confidence']}. Supporting: {x['support']}",'',
                f"Null/contrary/insufficient: {x['nullContrary']}",'',f"Boundaries: {x['boundaries']}",'',f"Risk if approved incorrectly: {x['risk']}",'',
                'Sources: '+(', '.join(x['sources']) or 'See linked source/construct issue; no invented supporting study.')+'.',
                'Shared issues: '+(', '.join(x['issueIds']) or 'None assigned.')+'.','',
                f"[Family package]({x['processingFamily']}/GOVERNANCE_DECISION_PACKAGE.md)" if x['processingFamily'] in p.FAMILIES else 'External owner retained; endpoint-only review.', '',DECISION,'']
    out('PSYCHOLOGICAL_LAYER_GOVERNANCE_INDEX.md',lines)
    out('PSYCHOLOGICAL_LAYER_VALIDATION.md',['Required validation results are recorded in validation-results.json and exact-head GitHub Linux/Windows checks. No test success confers scientific authority.','']+code(p.read(p.STORE/'validation-results.json')) if (p.STORE/'validation-results.json').exists() else ['Final required validation is in progress; see progress record.'])
    out('PSYCHOLOGICAL_LAYER_CROSS_LAYER_FINDINGS.md',review['crossLayerReview'])
    out('README.md',['Start with the [governance index](PSYCHOLOGICAL_LAYER_GOVERNANCE_INDEX.md), [completeness report](PSYCHOLOGICAL_LAYER_COMPLETENESS_REPORT.md), [evidence summary](PSYCHOLOGICAL_LAYER_EVIDENCE_SUMMARY.md), [cross-Layer findings](PSYCHOLOGICAL_LAYER_CROSS_LAYER_FINDINGS.md), and [progress](PSYCHOLOGICAL_LAYER_PROGRESS.md).','',
        'The program is a coherent candidate package, not scientific activation or automatic population. Source/construct/measurement backlogs remain visible. All human decision fields remain PENDING.'])
    return s


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser();ap.add_argument('--sample',action='store_true');ap.add_argument('--render',action='store_true');ap.add_argument('--validate',action='store_true');ap.add_argument('--links',action='store_true');args=ap.parse_args()
    if args.sample:print(p.encode(sample_records()))
    if args.render:print(p.encode({k:v for k,v in render().items() if k!='families'}))
    if args.validate:print(p.encode({k:v for k,v in validate().items() if k!='families'}))
    if args.links:print(p.encode(link_check()))
