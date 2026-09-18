"""Regression tests for the curated overlay, not a new clustering procedure."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from cognitive_security.topic_guides import (AUTHORING, PUBLIC, SITE, Corpus, GuideError,
    compile_outputs, validate_guides, field_sha, load)

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=[]; self.meta={}; self.tags=[]; self.h1=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.tags.append((tag,a))
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content')

class TopicGuidesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=Corpus(ROOT);cls.g=load(ROOT/AUTHORING/'guides.json');cls.out,cls.report=compile_outputs(ROOT)

    def test_01_canonical_source_authority(self):
        self.assertEqual(self.c.manifest['methodVersion'],'deduplicated-canonical-resynthesis')
        self.c.validate_lock(load(ROOT/AUTHORING/'source_lock.json'))

    def test_02_all_127_name_pairs_are_locked(self):
        lock=load(ROOT/AUTHORING/'source_lock.json')
        self.assertEqual(len(lock['clusterNameById']),127)
        self.assertEqual(lock['clusterNameById'],{k:v['name'] for k,v in self.c.records['cluster'].items()})

    def test_03_known_id_name_corrections(self):
        expected={'KCFT-21':'Information Environment & Ecosystem Models','KCFT-22':'Targeting, Segmentation & Audience Analysis','KCFT-23':'Campaign Integration & Cross-Domain Synchronization','KCFT-24':'Innovation, Experimentation & Foresight','KCFT-25':'Organizational Learning & Talent Development','KCFT-26':'Platform, Algorithmic & Information Ecosystem Concepts','KCFT-27':'Campaigning & Persistent Competition Concepts','KCFT-28':'Human-Centered Security & Human Terrain Concepts','KCFT-29':'Cross-Domain & Integrated Competition Frameworks','KCFT-30':'Learning, Education & Cognitive Development Frameworks','OPP-05':'Campaigning, Targeting & Influence Operations','OPP-11':'Workforce, Talent & Human Capital'}
        for key,value in expected.items():self.assertEqual(self.c.get('cluster',key)['name'],value)

    def test_04_valid_but_wrong_id_name_rejected(self):
        x=copy.deepcopy(self.g); x['guides'][0]['sourceTopics'][0]['expectedName']='Workforce, Expertise & Training Gaps'
        with self.assertRaisesRegex(GuideError,'ID/name mismatch'):validate_guides(self.c,x)

    def test_05_selected_source_wrong_name_rejected(self):
        ref=copy.deepcopy(self.g['guides'][0]['sections']['concepts'][0]);ref['expectedName']='Experimentation, Evaluation & Feedback'
        with self.assertRaisesRegex(GuideError,'ID/name mismatch'):self.c.resolve(ref)

    def test_06_all_improved_family_assignments_locked(self):
        lock=load(ROOT/AUTHORING/'source_lock.json');self.assertEqual(len(lock['primaryFamilyByCluster']),127);self.assertEqual(lock['primaryFamilyByCluster'],self.c.family_for)

    def test_07_method_not_legacy(self):
        c=copy.deepcopy(self.c);c.manifest['methodVersion']='initial-pass'
        with self.assertRaisesRegex(GuideError,'noncanonical'):c.validate_lock(load(ROOT/AUTHORING/'source_lock.json'))

    def test_08_registry_has_first_fifteen_not_all_topics(self):
        self.assertEqual(len(self.g['guides']),15);self.assertTrue(self.g['unmappedAllowed']);self.assertGreater(self.report['unmappedClusterCount'],0)

    def test_09_unmapped_sources_do_not_block(self):
        x=copy.deepcopy(self.g);x['guides']=x['guides'][:1]
        validate_guides(self.c,x)

    def test_10_no_similarity_gate(self):
        source=(ROOT/'scripts/cognitive_security/topic_guides.py').read_text()
        for name in ('similarity_data.json','episode_discovery.json','weighted_jaccard','qualified_topics','primaryItemMinimum','prominenceShareMinimum'):
            self.assertNotIn(name,source)

    def test_11_assessment_controls_retained(self):
        g=next(g for g in self.g['guides'] if g['slug']=='assessment');numbers={e['expectedEpisodeNumber'] for e in g['featuredEpisodes']}
        self.assertTrue({174,82,81,182,115}<=numbers)
        burgos=next(e for e in g['featuredEpisodes'] if e['expectedEpisodeNumber']==115)
        self.assertIn('CRB-01',burgos['topicIds'])

    def test_12_cyber_controls_retained(self):
        g=next(g for g in self.g['guides'] if g['slug']=='cyber');self.assertTrue({133,57,179,40,30}<={e['expectedEpisodeNumber'] for e in g['featuredEpisodes']})

    def test_13_broad_source_not_automatic_membership(self):
        g=next(g for g in self.g['guides'] if g['slug']=='cyber');self.assertIn('FTP-11',{s['id'] for s in g['sourceTopics']})
        self.assertNotIn('FTP-11',{r['id'] for refs in g['sections'].values() for r in refs})
        index=json.loads(self.out[PUBLIC/'reverse_index.json']);self.assertNotIn(g['guideId'],index['entities'].get('cluster:FTP-11',[]))

    def test_14_duplicate_slug_rejected(self):
        x=copy.deepcopy(self.g);x['guides'][1]['slug']=x['guides'][0]['slug']
        with self.assertRaisesRegex(GuideError,'Duplicate guide'):validate_guides(self.c,x)

    def test_15_unknown_entity_rejected(self):
        r=copy.deepcopy(self.g['guides'][0]['sections']['concepts'][0]);r['id']='KCFT-999'
        with self.assertRaisesRegex(GuideError,'Unknown'):self.c.resolve(r)

    def test_16_stale_passage_rejected(self):
        r=copy.deepcopy(self.g['guides'][0]['sections']['concepts'][0]);r['sourceFieldSha256']='0'*64
        with self.assertRaisesRegex(GuideError,'Stale'):self.c.resolve(r)

    def test_17_field_allowlists_reject_private_item_ids(self):
        r=copy.deepcopy(self.g['guides'][0]['sections']['concepts'][0]);r['itemId']='private'
        with self.assertRaisesRegex(GuideError,'allowlisted'):self.c.resolve(r)

    def test_18_no_new_analytical_counts_or_core_files(self):
        for p in self.out:
            self.assertFalse(str(p).startswith('data/cognitive-security/'))
            self.assertFalse(str(p).startswith('data/cognitive-security-discovery/'))

    def test_19_all_refs_and_finding_routes(self):
        for p,b in self.out.items():
            if p.suffix!='html':continue
            h=Links();h.feed(b.decode())
            for url in h.links:
                part=urlparse(url)
                if part.path=='/cognitive-security/' and part.query:
                    args=parse_qs(part.query);kind=args.get('view',[''])[0]
                    if 'id' in args:self.c.get(kind,args['id'][0])
        app=(ROOT/'cognitive-security/app.js').read_text();self.assertIn('categoryFinding: "finding"',app);self.assertIn('finding: renderFinding',app)

    def test_20_all_fifteen_static_share_pages(self):
        self.assertEqual(sum(p.suffix=='.html' for p in self.out),16)
        for g in self.g['guides']:
            p=SITE/g['slug']/'index.html';h=Links();h.feed(self.out[p].decode());self.assertEqual(h.h1,1)
            self.assertEqual(h.meta['og:url'],'https://psywerx.io/cognitive-security/topic/'+g['slug']+'/')
            self.assertIn(g['title'],h.meta['og:title']);self.assertEqual(h.meta['og:description'],g['scope'])

    def test_21_no_duplicate_html_ids(self):
        for p,b in self.out.items():
            if p.suffix=='.html':
                h=Links();h.feed(b.decode());self.assertEqual(len(h.ids),len(set(h.ids)),str(p))

    def test_22_fragments_resolve(self):
        for p,b in self.out.items():
            if p.suffix=='.html':
                h=Links();h.feed(b.decode())
                for url in h.links:
                    if url.startswith('#'):self.assertIn(url[1:],h.ids)

    def test_23_no_continue_exploring_or_voices_section(self):
        for p,b in self.out.items():
            if p.suffix=='.html':
                self.assertNotIn('Continue Exploring',b.decode());self.assertNotIn('Voices from the Corpus',b.decode())

    def test_24_tension_poles_both_present(self):
        page=self.out[SITE/'assessment'/'index.html'].decode()
        for ref in self.g['guides'][0]['sections']['tensions']:
            rec=self.c.get('tension',ref['id'])
            import html
            for field in ('poleALabel','poleBLabel','poleAAssumption','poleBAssumption','falseDichotomyCaveat'):self.assertIn(html.escape(rec[field]),page)

    def test_25_reverse_index_is_exact(self):
        expected={}
        for g in self.g['guides']:
            pairs=[(r['type'],r['id']) for refs in g['sections'].values() for r in refs]+[('episode',e['episodeId']) for e in g['featuredEpisodes']]
            for k,i in pairs:expected.setdefault(k+':'+i,set()).add(g['guideId'])
        result=json.loads(self.out[PUBLIC/'reverse_index.json'])['entities'];self.assertEqual(result,{k:sorted(v) for k,v in expected.items()})

    def test_26_all_pages_are_quote_free(self):
        for path, data in self.out.items():
            if path.suffix == '.html':
                parser = Links(); parser.feed(data.decode())
                self.assertFalse(any(tag in ('blockquote', 'q') for tag, attrs in parser.tags), str(path))
                self.assertNotIn('episode-quote', data.decode())
                self.assertNotIn('Transcript excerpt;', data.decode())

    def test_27_quote_fields_cannot_be_reintroduced(self):
        for field in ('quoteId', 'quote', 'quoteText', 'transcriptPath'):
            payload = copy.deepcopy(self.g)
            payload['guides'][0]['featuredEpisodes'][0][field] = 'not allowed'
            with self.assertRaisesRegex(GuideError, 'allowlisted'):
                validate_guides(self.c, payload)

    def test_28_episode_citations_and_takeaways_remain(self):
        for guide in self.g['guides']:
            page = self.out[SITE/guide['slug']/'index.html'].decode()
            self.assertEqual(page.count('Listening notes:'), len(guide['featuredEpisodes']))
            for episode in guide['featuredEpisodes']:
                self.assertEqual(len(episode['takeaways']), 2)
                self.assertIn(episode['episodeId'], page)

    def test_29_deterministic(self):
        again,_=compile_outputs(ROOT);self.assertEqual(again,self.out)

    def test_30_quote_payload_and_assets_are_absent(self):
        manifest = json.loads(self.out[PUBLIC/'manifest.json'])
        self.assertEqual(manifest['schemaVersion'], '1.1')
        self.assertEqual(set(manifest['files']), {'guide_directory.json', 'reverse_index.json', 'topic_guides.json'})
        self.assertNotIn('quoteCount', manifest)
        self.assertNotIn('quoteOmissions', self.report)
        for path in (AUTHORING/'quote_excerpts.json', AUTHORING/'quote_approvals.json', PUBLIC/'quote_excerpts.json'):
            self.assertFalse((ROOT/path).exists())
        for path, data in self.out.items():
            if path.is_relative_to(PUBLIC):
                self.assertNotIn('quoteId', data.decode())
                self.assertNotIn('verificationBasis', data.decode())

    def test_31_public_payload_has_no_private_source_records(self):
        forbidden={'itemId','evidenceId','transcriptPath','sourceFile','source_file','worksheet','prompt','reviewNotes','adjudicationId','sourceFilename'}
        def walk(v):
            if isinstance(v,dict):
                self.assertFalse(set(v)&forbidden)
                for a in v.values():walk(a)
            elif isinstance(v,list):
                for a in v:walk(a)
        for p,b in self.out.items():
            if p.is_relative_to(PUBLIC):walk(json.loads(b))

    def test_32_episode_tags_have_actual_primary_support(self):
        for g in self.g['guides']:
            for e in g['featuredEpisodes']:
                for cid in e['topicIds']:self.assertGreater(self.c.direct[(e['episodeId'],cid)]['primaryItemCount'],0)

    def test_33_early_outline_labels_do_not_replace_current_names(self):
        refs=[r for g in self.g['guides'] for cards in g['sections'].values() for r in cards]
        for r in refs:
            if r['type']=='cluster':self.assertEqual(r['expectedName'],self.c.records['cluster'][r['id']]['name'])

    def test_34_generated_files_current(self):
        for p,b in self.out.items():self.assertEqual((ROOT/p).read_bytes(),b,str(p))

if __name__=='__main__':unittest.main()
