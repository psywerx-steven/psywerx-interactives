"""Offline and repository-integration acceptance tests for the homepage preview."""
import unittest, json, importlib.util, tempfile, shutil, re, copy, subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
R=REPO/'homepage'
SITE=REPO/'homepage-preview'
spec=importlib.util.spec_from_file_location('builder',R/'tools/build_homepage.py')
builder=importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)

def dataset():
 return tuple(json.loads((R/'content'/f).read_text(encoding='utf-8')) for f in ('site.json','platform.json','feed.json'))

class HomepageTests(unittest.TestCase):
 def test_approved_taxonomies(self):
  self.assertTrue(builder.validate(*dataset()))
 def test_exact_single_brand_line(self):
  self.assertEqual(dataset()[0]['brandLine'],'exploring the human condition from theory to practice')
 def test_only_two_live_explorers(self):
  live=[x for a in dataset()[1] for x in a['tools'] if x['status']=='live']
  self.assertEqual({x['path'] for x in live},{'/drivers/','/cognitive-security/'})
 def test_training_is_coming_soon(self):
  self.assertTrue(all(t['status']=='soon' for t in dataset()[1][-1]['tools']))
 def test_no_false_public_approval(self):
  self.assertTrue(all(x['status']=='draft' for x in dataset()[2]))
 def test_feed_has_all_four_categories(self):
  self.assertEqual(set().union(*(set(i['categories']) for i in dataset()[2])),set(builder.EXPECTED_FEED))
 def test_feed_preserves_source_and_brief_dates(self):
  self.assertTrue(any(i['sourcePublishedAt']!=i['briefDate'] for i in dataset()[2]))
 def test_invalid_url_rejected(self):
  s,p,f=dataset(); f[0]['sourceUrl']='javascript:alert(1)'
  with self.assertRaises(ValueError): builder.validate(s,p,f)
 def test_duplicate_id_rejected(self):
  s,p,f=dataset(); f.append(copy.deepcopy(f[0]))
  with self.assertRaises(ValueError): builder.validate(s,p,f)
 def test_approval_requires_source_verification(self):
  s,p,f=dataset(); f[0]['status']='approved';f[0]['primarySourceChecked']=False
  with self.assertRaises(ValueError): builder.validate(s,p,f)
 def test_approval_requires_review_date(self):
  s,p,f=dataset(); f[0]['status']='approved'
  with self.assertRaises(KeyError): builder.validate(s,p,f)
 def test_no_cname_or_dns_artifact(self):
  self.assertFalse((SITE/'CNAME').exists())
 def test_no_secret_or_private_source_urls(self):
  text='\n'.join(p.read_text(encoding='utf-8') for p in SITE.rglob('*') if p.suffix in ('.html','.js','.css','.json'))
  self.assertNotRegex(text,r'https://(?:docs\.google\.com|drive\.google\.com)')
  self.assertNotRegex(text,r'sk-[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9]{20,}|C:\\\\Users')
  self.assertNotRegex(text,r'[âÂ�]')
 def test_no_fake_signup_form(self):
  text=(SITE/'index.html').read_text(encoding='utf-8')
  self.assertNotIn('type="email"',text)
 def test_no_search_or_ai_control(self):
  text=(SITE/'index.html').read_text(encoding='utf-8')
  self.assertNotIn('type="search"',text); self.assertNotIn('Ask PSYWERX',text)
 def test_all_local_assets_exist(self):
  text=(SITE/'index.html').read_text(encoding='utf-8')
  for asset in re.findall(r'(?:src|href)="(assets/[^\"]+)"',text):
   self.assertTrue((SITE/asset).is_file(),asset)
 def test_build_is_deterministic(self):
  builder.build(); first={p.name:p.read_bytes() for p in [SITE/'index.html',SITE/'assets/home-data.js']}
  builder.build(); second={p.name:p.read_bytes() for p in [SITE/'index.html',SITE/'assets/home-data.js']}
  self.assertEqual(first,second)
 def test_release_excludes_unapproved_feed(self):
  with tempfile.TemporaryDirectory() as temp:
   r=Path(temp); shutil.copytree(R/'content',r/'content');shutil.copytree(R/'src',r/'src')
   report=builder.build('release','local',r)
   self.assertEqual(report['feedCount'],0)
   page=(r/'site/index.html').read_text(encoding='utf-8')
   self.assertIn('./drivers/',page);self.assertNotIn('noindex,nofollow',page)
   self.assertNotIn('data-feed-detail=',page)
 def test_public_feed_allowlist(self):
  builder.build(); text=(SITE/'assets/home-data.js').read_text(encoding='utf-8'); data=json.loads(text[len('window.PSYWERX_HOME = '):].strip().removesuffix(';'))
  self.assertEqual(set(data['feed'][0]),set(builder.PUBLIC_FEED_FIELDS))
 def test_verified_integrations_only(self):
  site=dataset()[0]
  self.assertIsNone(site['newsletterUrl'])
  self.assertEqual(site['linkedinUrl'],'https://www.linkedin.com/company/psywerx')
 def test_staging_output_excludes_editorial_control_fields(self):
  text=(SITE/'assets/home-data.js').read_text(encoding='utf-8')
  data=json.loads(text[len('window.PSYWERX_HOME = '):].strip().removesuffix(';'))
  for private_field in ('primarySourceChecked','reviewedAt','status','order'):
   self.assertTrue(all(private_field not in item for item in data['feed']))
 def test_staging_path_and_size(self):
  self.assertTrue((SITE/'index.html').is_file())
  total=sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file())
  self.assertLess(total,300_000)
 def test_root_and_cname_match_origin_main(self):
  for name in ('index.html','CNAME'):
   result=subprocess.run(['git','diff','--exit-code','origin/main','--',name],cwd=REPO,capture_output=True)
   self.assertEqual(result.returncode,0,result.stdout.decode(errors='replace')+result.stderr.decode(errors='replace'))
 def test_date_is_valid(self):
  s,p,f=dataset();f[0]['briefDate']='2026-22-90'
  with self.assertRaises(ValueError):builder.validate(s,p,f)

if __name__=='__main__': unittest.main(verbosity=2)
