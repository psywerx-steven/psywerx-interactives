"""Independent exact-scope assertions for the conditional human checkpoint."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import actions_events_v1 as ae
import relationship_intervention_v1 as ri
import materialize_soc_f07_governance_001 as g
import build_soc_f07_pilot as p
import audit_family as af


class GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=ae.read(g.AE_PATH)
        # Freeze this checkpoint's seven records; the NS completion suite
        # separately proves the exact eighth addition and all current totals.
        cls.records=[r for r in ae.all_records(cls.catalog) if r['id'] in {f'HT-V1-SOC-F07-{n:03d}' for n in range(1,8)}]
        cls.decisions=ae.read(g.MARKER)
        cls.byid={r['id']:r for r in cls.decisions['rows']}
        cls.manifest=ae.read(g.AE_PATH.parent/'SOC-F07-materialization-manifest.json')
        cls.w=ae.read(g.STORE/'workspace.json')

    def test_exact_seven_materialized_eighth_explicitly_blocked(self):
        self.assertEqual({r['id'] for r in self.records},{f'HT-V1-SOC-F07-{n:03d}' for n in range(1,8)})
        self.assertEqual(self.byid['HT-CAND-SOC-F07-008']['outcome'],'APPROVE_IDENTITY')
        self.assertEqual(self.byid['HT-CAND-SOC-F07-008']['implementation'],'BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT')

    def test_inactive_human_hash_bound_authority(self):
        ae.validate_catalog(self.catalog)
        for r in self.records:
            self.assertEqual(r['governance']['lifecycleStatus'],'GOVERNED')
            self.assertEqual(r['governance']['activationStatus'],'INACTIVE')
            self.assertEqual(r['governance']['authorizedBy'],'authorized human governor')
        self.assertFalse(self.decisions['activationAuthorized'])
        tampered=copy.deepcopy(self.catalog)
        next(r for r in tampered['happeningTypes'] if r['id']=='HT-V1-SOC-F07-001')['description']+=' efficacy'
        with self.assertRaises(ae.ValidationError): ae.validate_catalog(tampered)

    def test_approved_decisions_not_new_architecture_approval(self):
        self.assertEqual(self.decisions['newArchitectureDecisionStatus'],'PENDING')
        self.assertEqual(self.decisions['decisionId'],'GOV-SOC-F07-001-2026-09-06')
        self.assertEqual(self.decisions['actorClass'],'authorized human governor')
        for n in range(1,9): self.assertEqual(self.byid[f'HT-CAND-SOC-F07-{n:03d}']['outcome'],'APPROVE_IDENTITY')

    def test_retained_semantics_and_existing_relationships_exact(self):
        current=ae.read(g.ROOT/'data/relationships.json')
        self.assertEqual(current,g.frozen('data/relationships.json'))
        for i in ('REL-RDS-0004','REL-RDS-0006','REL-RDS-0013'):
            self.assertEqual(self.byid[i]['outcome'],'APPROVE_RETAIN_AS_IS')
        self.assertEqual(self.byid['REL-TEC-050']['outcome'],'APPROVE_RESEARCH_NEEDED_DISPOSITION')

    def test_review_only_no_retyping_revision(self):
        for n in range(31,35): self.assertEqual(self.byid[f'REL-SOC-{n:03d}']['outcome'],'APPROVE_RETYPE_REVIEW_ONLY')
        for i in ('REL-INS-047','REL-SOC-035'): self.assertEqual(self.byid[i]['outcome'],'APPROVE_REVISION_REVIEW_ONLY')
        for r in ae.read(g.STORE/'revision-proposals.json'):
            self.assertEqual(r['governance']['lifecycleStatus'],'RESEARCH_NEEDED')
            self.assertEqual(r['governance']['activationStatus'],'NOT_ELIGIBLE')

    def test_derivation_concept_approved_but_no_record(self):
        row=self.byid['REL-CAND-SOC-F07-001']
        self.assertEqual(row['outcome'],'MODIFY_APPROVE_AS_MODIFIED')
        self.assertEqual(row['implementation'],'BLOCKED_PENDING_REPRESENTATION')
        for phrase in ('COMPLETE','all node','benchmark','One ego','betweenness','eigenvector','closeness'):
            self.assertIn(phrase,row['propositionOrDisposition'])
        native=ae.read(g.ROOT/'data/relationship-intervention-v1/relationships.json')['relationships']
        self.assertFalse(any('SOC-F07' in r['id'] for r in native))

    def test_current_schema_rejects_typed_collection_contract(self):
        r=copy.deepcopy(self.w['passA']['relationshipCandidates'][0])
        r['collectionInput']={'entityId':'SOC-049','quantifier':'ALL_NETWORK_NODES','benchmarkRequired':True}
        with self.assertRaises(ri.ArchitectureValidationError): ri.SchemaSet().validate('relationship',r)

    def test_free_text_does_not_enforce_all_node_alignment(self):
        r=copy.deepcopy(self.w['passA']['relationshipCandidates'][0])
        # Falsification: schema accepts this scalar wording. Merely writing ALL
        # in another valid string cannot be a machine-enforced quantifier.
        r['boundaryConditions']='A single ego degree value, no network benchmark'
        ri.SchemaSet().validate('relationship',r)
        self.assertEqual(r['targetEntityId'],'SOC-049')
        self.assertEqual(ri.causal_traversal([r]),[])

    def test_six_sources_registered_exactly(self):
        before={s['id']:s for s in g.frozen('data/relationship-intervention-v1/source-register.json')['sources']}
        import materialize_soc_f07_completion as completion
        current=ae.read(g.SOURCE_PATH)
        if completion.MANIFEST.exists(): current=completion.strip_additions('data/relationship-intervention-v1/source-register.json',current)
        after={s['id']:s for s in current['sources']}
        self.assertEqual(set(after)-set(before),{f'SRC-{n}' for n in range(553,559)})
        self.assertTrue(all(after[i]==r for i,r in before.items()))
        ri.validate_native_source_register(ri.SchemaSet())
        used={s for r in self.records for s in r['identitySourceIds']}
        self.assertEqual(used,{f'SRC-{n}' for n in range(553,559)}|{'SRC235','SRC250'})

    def test_non_pubmed_source_not_mislabeled(self):
        manifest=ae.read(g.MANIFEST)
        self.assertEqual(manifest['bibliographyReconciledButContractBlocked']['pubmedResultCount'],0)
        self.assertEqual(manifest['recordsBlockedBySourceContract'],['HT-CAND-SOC-F07-008'])
        s=copy.deepcopy(g.sources()[0]); s['verification']['system']='PUBLISHER_AND_ARXIV'
        with self.assertRaises(ri.ArchitectureValidationError): ri.SchemaSet().validate('source',s)

    def test_overlap_and_token_normalization_explicit(self):
        manifest=ae.read(g.MANIFEST)
        self.assertEqual({r['canonicalId'] for r in manifest['canonicalReused']},{'SRC235','SRC250'})
        self.assertIn('same work',manifest['preservedOverlap'])
        self.assertIn('SRC-509',manifest['preservedOverlap'])
        self.assertEqual(ae.read(g.ROOT/'data/sources.json'),g.frozen('data/sources.json'))

    def test_candidate_science_and_evidence_unchanged(self):
        self.assertEqual(self.w,g.frozen('data/candidates/actions-events-v1/SOC-F07/workspace.json'))
        self.assertEqual(ae.read(g.STORE/'source-findings.json'),g.frozen('data/candidates/actions-events-v1/SOC-F07/source-findings.json'))
        for r in self.w['passB']['effectAssertions']:
            self.assertEqual(r['change'],'UNKNOWN'); self.assertEqual(r['governance']['lifecycleStatus'],'RESEARCH_NEEDED')
            self.assertEqual(r['governance']['activationStatus'],'NOT_ELIGIBLE')
        for key in ('effectAssertions','evidenceAssessments','occurrences'):
            self.assertEqual(self.catalog[key],g.frozen('data/actions-events-v1/catalog.json')[key])

    def test_lineage_exact_candidate_revision_hash(self):
        candidates={r['id']:r for r in self.w['passB']['happeningTypes']}
        canonical={r['id']:r for r in self.records}
        self.assertEqual(len(self.manifest['candidateLineage']),7)
        for row in self.manifest['candidateLineage']:
            self.assertEqual(row['candidateHash'],ae.digest(candidates[row['candidateId']]))
            self.assertEqual(row['canonicalHash'],ae.digest(canonical[row['canonicalId']]))
            self.assertEqual(row['governanceDecision'],g.DECISION)
            self.assertTrue(row['sameScientificIdentity']); self.assertFalse(row['effectEvidenceInherited'])

    def test_rejected_research_blocked_exact(self):
        rejected={'H01','H02','H03','H04','H07','H09','H13','H14','H21','H22','H23','H24','H25','H28','H29'}
        research={'H05','H06','H10','H11','H15','H16','H17','H18','H19','H26','H27'}
        for row in ae.read(g.STORE/'hypotheses.json'):
            short=row['shortId']
            if short in rejected: self.assertEqual(row['disposition'],'REJECTED')
            elif short in research: self.assertEqual(row['disposition'],'RESEARCH_NEEDED')
            elif short in {'H12','H20'}: self.assertEqual(row['disposition'],'BLOCKED_NEEDS_GOVERNANCE_INPUT')
            self.assertNotIn('PENDING — APPROVE / MODIFY / REJECT',row['humanDecision'])
        gaps=ae.read(g.STORE/'ontology-target-gaps.json')
        self.assertEqual(len(gaps),12)
        self.assertTrue(all(r['governance']['blockStatus']=='NEEDS_GOVERNANCE_INPUT' for r in gaps))

    def test_no_rds_effect_target_or_structure_workaround(self):
        self.assertFalse(any('SOC-F07' in r['id'] for r in self.catalog['effectAssertions']))
        c=ae.Context.repository()
        self.assertTrue(all(c.driver(e['targetId']) for e in self.w['passB']['effectAssertions']))
        self.assertFalse(any(e['property']=='STRUCTURE' for e in self.w['passB']['effectAssertions']))

    def test_identity_not_practitioner_permission(self):
        storm=next(r for r in self.records if r['id'].endswith('006'))
        self.assertFalse(storm['interventionSubset'])
        self.assertEqual(storm['kindTags'],['EVENT','EXPOSURE'])
        for r in self.records:
            self.assertIn('no efficacy',r['description'])
            self.assertIn('SOC-102 change',r['description'])
            self.assertFalse(ae.state_active(r))

    def test_counts_and_zero_new_activation(self):
        i=af.enriched_inventory()['summary']
        self.assertEqual([i[k] for k in ('drivers','rds','entities','combinedActiveRelationships','combinedActiveCausal')],[770,41,811,457,436])
        self.assertEqual((self.manifest['newGoverned'],self.manifest['newInactive'],self.manifest['newActive']),(7,7,0))
        audit=ae.read(g.DOCS/'SOC_F07_AUDIT_MANIFEST.json')
        self.assertEqual(audit['newGoverned'],audit['counts']['newGoverned'])
        self.assertEqual(audit['counts']['candidateWorkspaceGoverned'],0)

    def test_protected_record_comparison_detects_unapproved_edits(self):
        report=p.protected(); self.assertTrue(report['passed'])
        changed={path for path,row in report['files'].items() if not row['unchanged']}
        self.assertEqual(changed,{'data/actions-events-v1/catalog.json','data/relationship-intervention-v1/source-register.json','schemas/relationship-intervention/v1/source-record-v1.schema.json'})
        old=json.dumps(g.frozen('data/actions-events-v1/catalog.json')).encode()
        bad=copy.deepcopy(self.catalog); bad['happeningTypes'][0]['name']='unauthorized change'
        self.assertFalse(g.exact_additions('data/actions-events-v1/catalog.json',old,json.dumps(bad).encode()))

    def test_materialization_reproducible_without_writes(self):
        self.assertEqual(self.records,g.identities())
        self.assertEqual(ae.read(g.MARKER),g.decisions())
        self.assertEqual(ae.read(g.MANIFEST),g.source_manifest())


if __name__=='__main__': unittest.main()
