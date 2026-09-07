"""Candidate-only network pilot: falsification, isolation and deterministic audit checks."""
import copy
import hashlib
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import actions_events_v1 as ae
import audit_family as af
import build_soc_f07_pilot as p
import relationship_intervention_v1 as ri
import materialize_soc_f07_governance_001 as checkpoint


class SocF07PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w=ae.read(p.STORE/'workspace.json')
        cls.m=ae.read(p.DOCS/'SOC_F07_AUDIT_MANIFEST.json')
        cls.sources=ae.read(p.STORE/'source-registry.json')
        cls.sides=ae.read(p.STORE/'source-findings.json')
        cls.audits=ae.read(p.STORE/'existing-relationship-audit.json')
        cls.revs=ae.read(p.STORE/'revision-proposals.json')
        cls.gaps=ae.read(p.STORE/'ontology-target-gaps.json')
        c=ae.Context.repository()
        cls.c=ae.Context(c.entities,c.relationships,c.source_ids|{s['id'] for s in cls.sources})
        cls.records=cls.w['passA']['relationshipCandidates']+cls.w['passA']['evidence']+ae.all_records(cls.w['passB'])

    def test_exact_production_counts(self):
        i=af.enriched_inventory()['summary']
        self.assertEqual([i[k] for k in ('drivers','rds','entities','combinedActiveRelationships','combinedActiveCausal')],[770,41,811,457,436])

    def test_exact_membership_driver_rds(self):
        members={e['id'] for e in self.c.entities.values() if e['primaryFamilyId']=='SOC-F07'}
        self.assertEqual(members,{'SOC-'+str(i).zfill(3) for i in range(49,58)}|{'SOC-102','RDS-0005','RDS-0006','RDS-0007'})
        self.assertEqual({e for e in members if self.c.driver(e)},{'SOC-102'})
        self.assertEqual(len(members),13)

    def test_all_incident_buckets_reviewed(self):
        self.assertEqual(len(self.audits),10)
        self.assertEqual(Counter(a['bucket'] for a in self.audits),{'relationships':10})
        self.assertEqual(Counter(a['primaryDisposition'] for a in self.audits),{'RETAIN_AS_IS':3,'RETYPE_CANDIDATE':4,'REVISION_CANDIDATE':2,'RESEARCH_NEEDED':1})
        self.assertTrue(all(a['fieldReview'] and a['governanceDecision']==checkpoint.human_outcome(a['id']) for a in self.audits))

    def test_every_five_rds_source_explicit(self):
        rows=[a for a in self.audits if a['currentRecord']['relationFamily']=='CAUSAL' and a['currentRecord']['subjectEntityType']=='RELATIONAL_DERIVED_STATE']
        self.assertEqual({a['currentRecord']['subjectEntityId'] for a in rows},{'SOC-052','SOC-053','SOC-054','SOC-055','SOC-056'})
        self.assertEqual(Counter(a['rdsGate'] for a in rows),{'EXCEPTIONAL_CAUSAL':4,'HEIGHTENED_CAUSAL':1})
        self.assertTrue(all(a['temporalIndependence']=='NOT_ESTABLISHED' and a['evidenceRationale'] and a['identification'] for a in rows))

    def test_graph_projection_dedup_and_degree(self):
        g=self.m['graph']
        self.assertEqual(g['degreeBefore'],g['degreeAfter'])
        self.assertEqual((g['incidentBefore'],g['incidentAfter']),(10,10))
        self.assertEqual(len(g['causalIsolates']),7)
        self.assertEqual(g['scopeBySemantics'],{'CAUSAL/internal':4,'CAUSAL/sameLayerCrossFamily':1,'CAUSAL/crossLayer':2,'SEMANTIC/sameLayerCrossFamily':3})
        self.assertEqual(af.enriched_inventory()['summary']['projections']['additionalPropositions'],0)
        self.assertEqual(g['newCausalCycles'],0)

    def test_all_schema_and_semantic_validation(self):
        ae.validate_workspace(self.w,self.c)
        for side in self.sides:
            for f in side['sourceFindings']: ae.schema_set().validate('source-finding',f)

    def test_all_records_non_governed(self):
        for r in self.records+self.revs+self.gaps:
            self.assertIn(r['governance']['lifecycleStatus'],{'CANDIDATE','RESEARCH_NEEDED','REVIEW_READY'})
            self.assertEqual(r['governance']['activationStatus'],'NOT_ELIGIBLE')
            ri.validate_governance_record(r)
        # Candidate copies never receive canonical authority; seven separately
        # authorized inactive identities are reconciled by checkpoint tests.
        self.assertEqual((self.m['newGoverned'],self.m['newActive']),(7,0))
        self.assertFalse(self.w['passB']['authorizations'])

    def test_governance_escalation_rejected(self):
        w=copy.deepcopy(self.w)
        w['passB']['happeningTypes'][0]['governance']['lifecycleStatus']='GOVERNED'
        with self.assertRaises((ae.ValidationError,ri.ArchitectureValidationError)): ae.validate_workspace(w,self.c)

    def test_rds_target_rejected_for_every_family_rds(self):
        for entity in self.m['frozenFamily']['memberIds']:
            if entity=='SOC-102': continue
            w=copy.deepcopy(self.w); w['passB']['effectAssertions'][0]['targetId']=entity
            with self.subTest(entity=entity),self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_structure_is_not_rds_loophole(self):
        w=copy.deepcopy(self.w); e=w['passB']['effectAssertions'][0]
        e.update(targetId='SOC-049',property='STRUCTURE')
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_social_tie_cannot_be_ontology_edge_target(self):
        w=copy.deepcopy(self.w); e=w['passB']['effectAssertions'][0]
        e.update(targetKind='RELATIONSHIP',targetId='SOCIAL-TIE-PERSON-A-PERSON-B',property='STRUCTURE')
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_noncausal_edge_cannot_be_effect_target(self):
        w=copy.deepcopy(self.w); e=w['passB']['effectAssertions'][0]
        e.update(targetKind='RELATIONSHIP',targetId='REL-RDS-0013',property='STRUCTURE')
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_derivation_not_causality(self):
        r=self.w['passA']['relationshipCandidates'][0]
        self.assertEqual((r['relationFamily'],r['predicate'],r['sourceEntityId'],r['targetEntityId']),('DERIVATIONAL','DERIVED_FROM','RDS-0006','SOC-049'))
        self.assertFalse(r['causalClaim']); self.assertIsNone(r['causalReviewGate'])
        self.assertIn('complete aligned distribution',r['boundaryConditions'])
        self.assertIn('benchmark',r['boundaryConditions'])
        self.assertEqual(ri.causal_traversal([r]),[])

    def test_formula_derived_causal_effect_rejected(self):
        w=copy.deepcopy(self.w); w['passB']['effectAssertions'][0]['grounding']['derivationEntailed']='YES'
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_shared_driver_contribution_requires_control(self):
        w=copy.deepcopy(self.w); w['passB']['effectAssertions'][0]['grounding']['representedDriverId']='SOC-102'
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_two_routes_cannot_be_summed(self):
        w=copy.deepcopy(self.w)
        w['passB']['effectAssertions'][1]['contribution']['groupId']=w['passB']['effectAssertions'][0]['contribution']['groupId']
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_unknown_not_increase_or_zero(self):
        for change in ('INCREASE','NO_DETECTED_CHANGE'):
            w=copy.deepcopy(self.w); w['passB']['effectAssertions'][0]['change']=change
            with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)
        self.assertTrue(all(e['change']=='UNKNOWN' and e['observedChange'] is None for e in self.w['passB']['effectAssertions']))

    def test_missing_null_findings_cannot_be_erased(self):
        w=copy.deepcopy(self.w); w['passB']['evidenceAssessments'][0]['synthesis']['conflicts']=[]
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_supported_causality_not_from_wrong_evidence(self):
        w=copy.deepcopy(self.w); e=w['passB']['effectAssertions'][0]
        e.update(productionMethod='SYNTHESIS',knowledgeStatus='SUPPORTED_EFFECT',change='INCREASE')
        for f in w['passB']['evidenceAssessments'][0]['sourceFindings']: f['supportedSemantics']=['ASSOCIATION']
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)

    def test_model_inference_not_empirical(self):
        w=copy.deepcopy(self.w); w['passB']['effectAssertions'][0]['productionMethod']='MODEL_INFERENCE'
        with self.assertRaises(ae.ValidationError): ae.validate_workspace(w,self.c)
        self.assertEqual(next(s for s in self.sources if s['researchKey']=='003')['basis'],'MODEL_SIMULATION')

    def test_network_inputs_and_all_blocked_fields_preserved(self):
        rows=ae.read(p.STORE/'entity-rds-review.json')
        blocked={r['id']:r['blockedOrMissingFields'] for r in rows if r['blockedOrMissingFields']}
        self.assertEqual(set(blocked),{'SOC-102','RDS-0005','RDS-0006','RDS-0007'})
        self.assertTrue(all(len(v)==11 for v in blocked.values()))
        for r in rows:
            self.assertEqual(r['currentRecord'],self.c.entities[r['id']])
            self.assertEqual(len(r['boundarySensitivity']),11)
        antecedents=ae.read(p.STORE/'rds-antecedent-ledger.json')
        self.assertEqual(len(antecedents),12)
        self.assertTrue(all(a['validCompleteConfigurationDriverId'] is None and a['exactCausalRelationshipTargetId'] is None for a in antecedents))

    def test_source_resolution_and_no_registration(self):
        canonical=ae.Context.repository().source_ids
        extra={s['id'] for s in self.sources if s['id'].startswith('SRC-CAND')}
        self.assertFalse(extra & canonical); self.assertEqual(len(extra),18)
        self.assertEqual(len(self.sources),33)
        self.assertTrue(all(s['url'] and s['title'] and s['authors'] and s['accessDepth'] for s in self.sources))
        queue=ae.read(p.STORE/'source-registration-queue.json')
        registered=[s for s in queue if s['canonicalRegistration']=='REGISTERED_IDENTITY_PROVENANCE_ONLY']
        self.assertEqual({s['canonicalSourceId'] for s in registered},{f'SRC-{n}' for n in range(553,559)})

    def test_aliases_do_not_collapse_closure_into_clustering(self):
        rows={r['id']:r for r in ae.read(p.STORE/'entity-rds-review.json')}
        alias=next(a for a in rows['SOC-053']['aliasRecords'] if a['text']=='triadic closure')
        self.assertEqual(alias['publicDisplayRule'],'SEARCH_ONLY')
        self.assertEqual(alias['aliasType'],'RELATED_SEARCH')
        self.assertIn('distinct conditional-rate Driver SOC-102',rows['SOC-053']['aliasRisk'])
        self.assertFalse(self.c.driver('SOC-053'))
        self.assertTrue(self.c.driver('SOC-102'))

    def test_source_findings_complete_and_no_numbers(self):
        seen=set()
        for assessment in self.sides+self.w['passB']['evidenceAssessments']:
            fs=assessment['sourceFindings']; syn=assessment['synthesis']
            self.assertEqual({f['id'] for f in fs},set(syn['sourceFindingIds']))
            self.assertFalse(seen & {f['id'] for f in fs}); seen|={f['id'] for f in fs}
            self.assertEqual({f['id'] for f in fs if f['disposition'] in {'MIXED','NULL_FINDING','CONTRADICTED'}},{c['findingId'] for c in syn['conflicts']})
            self.assertTrue(all(f['sourceId'] in self.c.source_ids and f['quantitativeEstimate'] is None for f in fs))
            self.assertTrue(syn['datasetOverlap'])
        self.assertEqual(len(seen),34)

    def test_canonical_composite_not_independent_replication(self):
        src={s['id']:s for s in self.sources}
        self.assertIn('duplicates SRC-235',src['SRC-509']['overlap'])
        fs=[f for side in self.sides for f in side['sourceFindings'] if f['sourceId'] in {'SRC-235','SRC-509'}]
        self.assertEqual({tuple(f['datasetIds']) for f in fs},{('STUDY-CENTOLA-2010',)})

    def test_all_axes_search_ledgers(self):
        s=ae.read(p.STORE/'search-ledger.json')
        self.assertEqual(len(s['driverOriginDomainCoverage']),72)
        self.assertEqual({r['originLayer'] for r in s['driverOriginDomainCoverage']},{'BIO','PSY','SOC','CUL','ENV','INS','INF','TEC'})
        self.assertEqual(len({r['domain'] for r in s['driverOriginDomainCoverage']}),9)
        self.assertEqual(len(s['effectPropertyCoverage']),88)
        self.assertEqual(len({r['property'] for r in s['effectPropertyCoverage']}),11)
        self.assertTrue(all(r['outcome']!='SUPPORTED_NULL' for r in s['effectPropertyCoverage']))

    def test_ownership_no_duplicate_proposition(self):
        for r in self.w['passA']['relationshipCandidates']:
            self.assertEqual(af.ownership(r['sourceEntityId'],r['targetEntityId'],r['relationFamily'],self.c.entities),'SOC-F07')
            sig=(r['sourceEntityId'],r['targetEntityId'],r['predicate'])
            self.assertNotIn(sig,{(e['source'],e['target'],e['predicate']) for e in af.enriched_inventory()['edges']})
        self.assertTrue(all(a['ownerFamilyId'] and a['consultationStatus'].startswith('REVIEW_CANDIDATE_ONLY') for a in self.audits))

    def test_no_occurrence_pathway_moderation_inference(self):
        self.assertFalse(self.w['passB']['occurrences'])
        self.assertEqual({r['relationFamily'] for r in self.w['passA']['relationshipCandidates']},{'DERIVATIONAL'})
        self.assertTrue(all(not e['moderatorLinks'] and e['interaction']['mode']=='NONE' for e in self.w['passB']['effectAssertions']))

    def test_no_actionability_or_package_inference(self):
        for e in self.w['passB']['effectAssertions']:
            eligibility=ae.use_eligibility(e['id'],self.w['passB'],self.c)
            self.assertTrue(all(not eligibility[k]['eligible'] for k in ('scientificUseEligibility','modelEligibility','practitionerActionEligibility')))
        types=self.w['passB']['happeningTypes']
        self.assertFalse(next(h for h in types if h['id'].endswith('006'))['interventionSubset'])
        self.assertEqual(len({h['identityKey'] for h in types}),8)
        self.assertTrue(all(h['packageKind']=='ATOMIC' and not h['components'] for h in types))

    def test_rejection_and_blocked_ledger_protection(self):
        h=ae.read(p.STORE/'hypotheses.json')
        self.assertEqual(Counter(x['disposition'] for x in h),{'REJECTED':15,'RESEARCH_NEEDED':11,'BLOCKED_NEEDS_GOVERNANCE_INPUT':2,'REVIEW_READY':1})
        self.assertTrue(all(x['regenerationRule'] and x['humanDecision']==checkpoint.human_outcome(x['id']) for x in h))
        self.assertTrue(all(x['governance']['blockStatus']=='NEEDS_GOVERNANCE_INPUT' for x in self.gaps))

    def test_exact_old_propositions_and_revision_nonimplementation(self):
        current=ae.read(p.ROOT/'data/relationships.json')
        current={r['id']:r for k in ('relationships','deprecatedRelationships','relationshipCandidates') for r in current[k]}
        for a in self.audits: self.assertEqual(a['currentRecord'],current[a['id']])
        self.assertEqual(len(self.revs),6)
        for r in self.revs:
            self.assertEqual(r['currentRecordHash'],ae.digest(current[r['currentRecord']['id']]))
            self.assertEqual(r['governanceDecision'],checkpoint.human_outcome(r['currentRecord']['id']))

    def test_protected_science_bio_inf_schema_source_service(self):
        report=p.protected()
        self.assertTrue(report['passed'])
        self.assertEqual(report,ae.read(p.STORE/'protected-science.json'))
        self.assertGreaterEqual(report['filesCompared'],133)

    def test_renderer_canonical_write_fails(self):
        for target in (p.ROOT/'data/entities.json',p.ROOT/'schemas/test.json',p.ROOT/'docs/governance/pilots/INF-F03/test.md'):
            with self.assertRaises(ValueError): p.emit(target,{})

    def test_deterministic_all_rendered_products(self):
        captured={}
        with patch.object(p,'emit',side_effect=lambda path,value:captured.update({path:copy.deepcopy(value)})): p.build()
        for path,value in captured.items():
            expected=value.rstrip()+'\n' if isinstance(value,str) else p.encode(value)
            self.assertEqual(path.read_text(encoding='utf-8'),expected,str(path))

    def test_artifact_hashes(self):
        for name,digest in self.m['artifactHashes'].items():
            data=(p.STORE/name).read_bytes().replace(b'\r\n',b'\n')
            self.assertEqual(hashlib.sha256(data).hexdigest(),digest,name)

    def test_markdown_links(self):
        for doc in p.DOCS.glob('*.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
                link=unquote(link.strip('<>').split('#',1)[0])
                if link and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',link):
                    self.assertTrue((doc.parent/link).exists(),(doc.name,link))


if __name__=='__main__': unittest.main()
