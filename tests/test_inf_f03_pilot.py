"""INF-F03 science remains candidate-only; checks never approve a proposition."""
import copy
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import actions_events_v1 as ae
import audit_family as af
import build_inf_f03_pilot as pilot
import relationship_intervention_v1 as ri


class InfF03PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = ae.read(pilot.STORE/'workspace.json')
        cls.m = ae.read(pilot.DOCS/'INF_F03_AUDIT_MANIFEST.json')
        cls.sides = ae.read(pilot.STORE/'relationship-source-findings.json')
        cls.revs = ae.read(pilot.STORE/'revision-proposals.json')
        cls.c = pilot.context()
        cls.records = cls.w['passA']['relationshipCandidates'] + cls.w['passA']['evidence'] + ae.all_records(cls.w['passB']) + cls.revs

    def test_production_partition_counts(self):
        i = af.enriched_inventory()['summary']
        self.assertEqual([i[k] for k in ('drivers','rds','entities','combinedActiveRelationships','combinedActiveCausal')], [770,41,811,457,436])

    def test_family_all_buckets(self):
        f = self.m['family']
        self.assertEqual([f[k] for k in ('drivers','rds','entities','causalIncident','internal','sameLayerCrossFamily','crossLayer')],[4,4,8,9,4,2,3])
        audits = ae.read(pilot.STORE/'existing-relationship-audit.json')
        self.assertEqual(Counter(a['bucket'] for a in audits),{'relationships':14,'deprecatedRelationships':2})
        self.assertEqual(len({a['id'] for a in audits}),16)
        self.assertTrue(all(a['primaryDisposition'] for a in audits))
        self.assertTrue(all(a['currentV1Projection'] is None for a in audits if a['bucket']=='deprecatedRelationships'))

    def test_all_production_schemas_and_workspace(self):
        ae.validate_workspace(self.w,self.c)
        for side in self.sides:
            for f in side['sourceFindings']:
                ae.schema_set().validate('source-finding',f)

    def test_only_nongoverned_states(self):
        for r in self.records:
            self.assertIn(r['governance']['lifecycleStatus'],{'CANDIDATE','RESEARCH_NEEDED','REVIEW_READY'})
            self.assertEqual(r['governance']['activationStatus'],'NOT_ELIGIBLE')
            ri.validate_governance_record(r)
        self.assertFalse(self.w['passB']['authorizations'])

    def test_no_autonomous_governance(self):
        w = copy.deepcopy(self.w)
        w['passB']['effectAssertions'][0]['governance']['lifecycleStatus'] = 'GOVERNED'
        with self.assertRaises((ae.ValidationError,ri.ArchitectureValidationError)):
            ae.validate_workspace(w,self.c)

    def test_production_graph_exclusion(self):
        self.assertEqual(ri.causal_traversal(self.w['passA']['relationshipCandidates']),[])
        for r in self.w['passB']['effectAssertions']:
            result = ae.use_eligibility(r['id'],self.w['passB'],self.c)
            self.assertFalse(result['scientificUseEligibility']['eligible'])
            self.assertFalse(result['modelEligibility']['eligible'])
            self.assertFalse(result['practitionerActionEligibility']['eligible'])

    def test_rds_target_mutation_rejected(self):
        for identifier in ('INF-010','INF-011','INF-014','RDS-0001'):
            w = copy.deepcopy(self.w)
            w['passB']['effectAssertions'][0]['targetId'] = identifier
            with self.assertRaises(ae.ValidationError):
                ae.validate_workspace(w,self.c)

    def test_new_causal_no_rds_endpoint(self):
        for r in self.w['passA']['relationshipCandidates']:
            self.assertEqual(r['causalReviewGate'],'STANDARD_CAUSAL')
            self.assertEqual({r['sourceEntityType'],r['targetEntityType']},{'DRIVER'})
            self.assertEqual(r['compatibility']['v1Executability'],'NOT_EXECUTABLE')

    def test_existing_rds_review_flags(self):
        a = {r['id']:r for r in ae.read(pilot.STORE/'existing-relationship-audit.json')}
        for identifier in ('REL-INF-003','REL-INF-006','REL-INF-007','REL-INF-008','REL-INF-009'):
            self.assertEqual(a[identifier]['rdfCausalGate'],'HEIGHTENED_CAUSAL')
        self.assertEqual(self.m['family']['rdsCausalSourceCount'],2)

    def test_no_current_edge_mutation(self):
        original = ae.read(pilot.ROOT/'data/relationships.json')
        lookup = {r['id']:r for k in ('relationships','deprecatedRelationships') for r in original[k]}
        for a in ae.read(pilot.STORE/'existing-relationship-audit.json'):
            self.assertEqual(a['currentRecord'],lookup[a['id']])

    def test_no_candidate_duplicate_or_projection(self):
        i = af.enriched_inventory()
        sigs = {(r['source'],r['target'],r['predicate']) for r in i['edges']}
        candidates = [(r['sourceEntityId'],r['targetEntityId'],r['predicate']) for r in self.w['passA']['relationshipCandidates']]
        self.assertEqual(len(candidates),len(set(candidates)))
        self.assertEqual(sigs & set(candidates), {('INF-015', 'PSY-113', 'CAUSES')})
        self.assertEqual(i['summary']['projections']['additionalPropositions'],0)

    def test_owner_is_source_family(self):
        for row in self.w['passA']['ownership']:
            r = next(r for r in self.w['passA']['relationshipCandidates'] if r['id'] in row['recordIds'])
            self.assertEqual(row['ownerFamilyId'], self.c.entities[r['sourceEntityId']]['primaryFamilyId'])
            self.assertIn(self.c.entities[r['targetEntityId']]['primaryFamilyId'],row['consultedFamilyIds'])

    def test_source_registry_selective_governance_checkpoint(self):
        ids = {s['id'] for s in pilot.R['sources']}
        self.assertFalse(ids & ae.Context.repository().source_ids)
        self.assertEqual(len(ids),14)
        queue = ae.read(pilot.STORE/'source-registration-queue.json')
        registered = {s['id']: s['canonicalDuplicateId'] for s in queue if s['registrationPerformed']}
        self.assertEqual(registered, {
            'SRC-CAND-INF-F03-001': 'SRC-550',
            'SRC-CAND-INF-F03-002': 'SRC-551',
            'SRC-CAND-INF-F03-003': 'SRC-552',
        })
        for s in queue:
            if s['id'] not in registered:
                self.assertFalse(s['registrationPerformed'])
                self.assertFalse(s['canonicalDuplicateIds'])
            self.assertTrue(s['url'] and s['title'] and s['authors'])

    def test_source_findings_before_synthesis(self):
        evidence = self.sides + self.w['passB']['evidenceAssessments']
        seen = set()
        for e in evidence:
            if 'productionMethod' in e:
                self.assertIn(e['productionMethod'],{'SOURCE_EXTRACTION','SYNTHESIS','MODEL_INFERENCE','HYPOTHESIS'})
            fs = e['sourceFindings']
            self.assertEqual({f['id'] for f in fs},set(e['synthesis']['sourceFindingIds']))
            self.assertFalse(seen & {f['id'] for f in fs})
            seen.update(f['id'] for f in fs)
            contrary = {f['id'] for f in fs if f['disposition'] in {'NULL_FINDING','MIXED','CONTRADICTED'}}
            self.assertEqual(contrary,{x['findingId'] for x in e['synthesis']['conflicts']})
            self.assertTrue(all(f['sourceId'] in self.c.source_ids for f in fs))
            for f in fs:
                if f['accessDepth']=='METADATA':
                    self.assertEqual(f['basis'],['UNTESTED_HYPOTHESIS'])
                    self.assertFalse(f['supportedSemantics'])
        self.assertEqual(len(seen),self.m['newCounts']['sourceFindings'])

    def test_no_invented_quantitative_data(self):
        for e in self.sides+self.w['passB']['evidenceAssessments']:
            self.assertTrue(all(f['quantitativeEstimate'] is None for f in e['sourceFindings']))
        self.assertTrue(all(r['causalLag'] is None and r['persistence'] is None for r in self.w['passA']['relationshipCandidates']))

    def test_noise_null_not_scalar_complexity_decrease(self):
        e = next(e for e in self.w['passB']['effectAssertions'] if e['id'].endswith('004'))
        self.assertEqual((e['change'],e['knowledgeStatus']),('UNKNOWN','INSUFFICIENT_EVIDENCE'))
        f = next(e for e in self.w['passB']['evidenceAssessments'] if e['id'].endswith('004'))['sourceFindings'][0]
        self.assertEqual(f['disposition'],'NULL_FINDING')
        self.assertEqual(f['nullInterpretation']['interpretation'],'NO_DETECTED_DIFFERENCE')

    def test_mixed_and_ambiguity_contrary_retained(self):
        audit = next(e for e in self.sides if e['assertionId']=='REL-INF-041')
        self.assertTrue(any(f['disposition']=='CONTRADICTED' for f in audit['sourceFindings']))
        r = next(e for e in self.sides if e['assertionId']=='REL-CAND-INF-F03-001')
        self.assertEqual(r['synthesis']['disposition'],'MIXED')

    def test_unknown_is_not_zero(self):
        w = copy.deepcopy(self.w)
        e = next(e for e in w['passB']['effectAssertions'] if e['knowledgeStatus']=='INSUFFICIENT_EVIDENCE')
        e['change']='NO_DETECTED_CHANGE'
        with self.assertRaises(ae.ValidationError):
            ae.validate_workspace(w,self.c)

    def test_no_occurrence_moderation_pathway_inference(self):
        self.assertFalse(self.w['passB']['occurrences'])
        self.assertTrue(all(r['relationFamily']=='CAUSAL' for r in self.w['passA']['relationshipCandidates']))
        self.assertTrue(all(not e['moderatorLinks'] and e['interaction']['mode']=='NONE' for e in self.w['passB']['effectAssertions']))

    def test_rejection_registry_preserved(self):
        rejected = {h[0] for h in pilot.R['hypotheses'] if h[3]=='REJECTED_HYPOTHESIS'}
        self.assertEqual(rejected,{'H01','H02','H03','H05','H06','H10','H11','H14','H15','H18','H19'})
        self.assertTrue(all('HYP-' not in r['id'] for r in self.records))

    def test_all_four_driver_ledgers_all_axes(self):
        ledgers = ae.read(pilot.STORE/'driver-search-ledger.json')
        self.assertEqual({l['driverId'] for l in ledgers},{'INF-012','INF-013','INF-015','INF-077'})
        for l in ledgers:
            self.assertEqual(len(l['originReview']),8)
            self.assertEqual(len(l['domainReview']),9)
            self.assertEqual(len(l['propertyReview']),11)
            self.assertTrue(l['noFindings'])

    def test_origins_not_targets_and_nonactionable_exposures(self):
        t = {r['id']:r for r in self.w['passB']['happeningTypes']}
        for e in self.w['passB']['effectAssertions']:
            self.assertEqual(e['targetLayers'],['INF'])
        self.assertEqual(t['HT-CAND-INF-F03-004']['originLayers'],['ENV','SOC'])
        self.assertFalse(t['HT-CAND-INF-F03-004']['interventionSubset'])
        self.assertFalse(t['HT-CAND-INF-F03-007']['interventionSubset'])

    def test_no_package_effect_inference(self):
        self.assertTrue(all(t['packageKind']=='ATOMIC' and not t['components'] for t in self.w['passB']['happeningTypes']))
        self.assertEqual(len({t['identityKey'] for t in self.w['passB']['happeningTypes']}),7)

    def test_revision_proposals_not_replacements(self):
        self.assertEqual(len(self.revs),6)
        for r in self.revs:
            self.assertTrue(r['notAReplacementRelationshipRecord'])
            self.assertTrue(r['id'].startswith('REV-CAND-'))
            self.assertEqual(r['governanceDecision'],pilot.DECISION)

    def test_protected_science_schema_service_bio(self):
        checks = pilot.protected()
        self.assertTrue(pilot.protected_checkpoint_ok(checks))
        changed = {path for path, check in checks.items() if not check['unchanged']}
        # Later NS approval adds only a verification union; all historical
        # source/AE branches and scientific records have separate exact tests.
        self.assertTrue(changed <= pilot.AUTHORIZED_CHECKPOINT_PATHS | {'schemas/relationship-intervention/v1/source-record-v1.schema.json'})
        self.assertEqual(
            changed,
            {
                'data/actions-events-v1/README.md',
                'data/actions-events-v1/catalog.json',
                'data/relationship-intervention-v1/README.md',
                'data/relationship-intervention-v1/evidence-assessments.json',
                'data/relationship-intervention-v1/relationships.json',
                'data/relationship-intervention-v1/source-register.json',
                'schemas/relationship-intervention/v1/source-record-v1.schema.json',
            },
        )

    def test_renderer_canonical_write_rejected(self):
        for target in (pilot.ROOT/'data/entities.json',pilot.ROOT/'schemas/probe.json'):
            with self.assertRaises(ValueError):
                pilot.emit(target,{})

    def test_deterministic_candidate_generation(self):
        captured = {}
        with patch.object(pilot,'emit',side_effect=lambda p,v: captured.update({str(p):copy.deepcopy(v)})):
            pilot.build()
        self.assertEqual(captured[str(pilot.STORE/'workspace.json')],self.w)
        self.assertEqual(captured[str(pilot.STORE/'revision-proposals.json')],self.revs)

    def test_manifest_counts(self):
        self.assertEqual(Counter(r['governance']['lifecycleStatus'] for r in self.records), self.m['lifecycleCounts'])
        self.assertEqual((self.m['newGoverned'],self.m['newActive']),(12,5))
        self.assertFalse(self.m['governanceCheckpoint']['activationAuthorized'])
        self.assertEqual(len(self.m['activationCheckpoint']['activeIds']), 5)
        self.assertEqual(self.m['workspaceHash'],ae.digest(self.w))

    def test_markdown_local_links(self):
        for doc in pilot.DOCS.glob('*.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
                link = unquote(link.strip('<>').split('#',1)[0])
                if link and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',link):
                    self.assertTrue((doc.parent/link).exists(),(doc.name,link))


if __name__ == '__main__':
    unittest.main()
