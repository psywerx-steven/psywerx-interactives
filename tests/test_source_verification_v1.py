import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import source_verification_v1 as sv
import materialize_soc_f07_completion as completion
import relationship_intervention_v1 as ri
import actions_events_v1 as ae


class SourceVerificationTests(unittest.TestCase):
    def setUp(self): self.source=completion.source()

    def test_legacy_pubmed_schema_branch_exact(self):
        old=completion.frozen('schemas/relationship-intervention/v1/source-record-v1.schema.json')
        current=ae.read(ROOT/'schemas/relationship-intervention/v1/source-record-v1.schema.json')
        self.assertTrue(completion.source_schema_extension_only(old,current))

    def test_every_old_source_byte_content_unchanged(self):
        old=completion.frozen('data/relationship-intervention-v1/source-register.json')['sources']
        current={r['id']:r for r in ae.read(ROOT/'data/relationship-intervention-v1/source-register.json')['sources']}
        for record in old:
            self.assertEqual(current[record['id']],record); ri.SchemaSet().validate('source',record); self.assertTrue(sv.validate_source(record))

    def test_new_authoritative_route(self):
        ri.SchemaSet().validate('source',self.source); self.assertTrue(sv.validate_source(self.source))
        self.assertIsNone(self.source['pmid']); self.assertEqual(self.source['verification']['accessDepth'],'ABSTRACT_METADATA')

    def test_arbitrary_web_authority_fails(self):
        self.source['verification']['registryLocator']='https://example.org/works/'+self.source['doi']
        with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_host_spoof_and_plain_http_fail(self):
        for url in ('https://api.crossref.org.evil.invalid/works/'+self.source['doi'],
                    'http://api.crossref.org/works/'+self.source['doi'],
                    'https://api.crossref.org@evil.invalid/works/'+self.source['doi']):
            self.source['verification']['registryLocator']=url
            with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_nonpubmed_cannot_claim_pubmed(self):
        self.source['verification']={'system':'PUBMED_NCBI_EUTILITIES','status':'VERIFIED',
            'verifiedDate':'2026-09-07','identifierChecked':'DOI:'+self.source['doi']}
        with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_nonpubmed_unverified_pmid_rejected(self):
        self.source['pmid']='12345678'
        with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_unverified_and_conflicting_fail(self):
        for key,value in [('status','UNVERIFIED'),('conflicts',['unresolved authorship'])]:
            record=copy.deepcopy(self.source); record['verification'][key]=value
            with self.assertRaises(sv.VerificationError): sv.validate_source(record)

    def test_snapshot_hash_mismatch(self):
        self.source['verification']['provenance']['contentHash']='0'*64
        with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_verified_fields_align(self):
        for field,value in [('title','Different title'),('authors',['Different Author']),('year',2021),('publication','Different venue')]:
            record=copy.deepcopy(self.source); record[field]=value
            with self.subTest(field=field),self.assertRaises(sv.VerificationError): sv.validate_source(record)

    def test_identifier_and_publisher_match(self):
        for key,value in [('identifierChecked','DOI:10.0000/wrong'),('publisherLocator','https://example.org/'+self.source['doi'])]:
            record=copy.deepcopy(self.source); record['verification'][key]=value
            with self.assertRaises(sv.VerificationError): sv.validate_source(record)

    def test_no_access_depth_inflation(self):
        self.source['verification']['accessDepth']='FULL_TEXT'
        with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_attestation_path_escape(self):
        self.source['verification']['provenance']['path']='data/sources.json'
        with self.assertRaises(sv.VerificationError): sv.validate_source(self.source)

    def test_duplicate_doi_still_rejected(self):
        a=copy.deepcopy(self.source); b=copy.deepcopy(self.source); b['id']='SRC-999'
        with patch.object(ri,'_native_records',return_value=[a,b]),self.assertRaises(ri.ArchitectureValidationError):
            ri.validate_native_source_register(ri.SchemaSet())

    def test_duplicate_pmid_still_rejected(self):
        a=completion.frozen('data/relationship-intervention-v1/source-register.json')['sources'][0]
        b=copy.deepcopy(a); b['id']='SRC-999'
        with patch.object(ri,'_native_records',return_value=[a,b]),self.assertRaises(ri.ArchitectureValidationError):
            ri.validate_native_source_register(ri.SchemaSet())

    def test_registry_publisher_corroboration_required(self):
        snapshot=ae.read(ROOT/self.source['verification']['provenance']['path'])
        snapshot['registryPublisherLinks']=['https://example.org/'+self.source['doi']]
        self.source['verification']['provenance']['contentHash']=sv.digest(snapshot)
        with patch.object(Path,'read_text',return_value=json.dumps(snapshot)),self.assertRaises(sv.VerificationError):
            sv.validate_source(self.source)

    def test_existing_source_component_issue_preserved(self):
        old=completion.frozen('docs/governance/pilots/SOC-F07/SOC_F07_SOURCE_REGISTRATION_MANIFEST.json')
        self.assertEqual(ae.read(ROOT/'docs/governance/pilots/SOC-F07/SOC_F07_SOURCE_REGISTRATION_MANIFEST.json'),old)
        self.assertIn('SRC-509',old['preservedOverlap']); self.assertIn('SRC235',old['preservedOverlap'])

    def test_published_schema_matches_embedded_contract(self):
        self.assertEqual(ae.read(ROOT/'schemas/source-verification/v1/verification-v1.schema.json'),sv.SCHEMA)


if __name__=='__main__': unittest.main()
