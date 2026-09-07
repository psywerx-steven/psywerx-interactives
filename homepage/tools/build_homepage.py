#!/usr/bin/env python3
"""Build PSYWERX's static homepage from small, validated editorial JSON files.

Standard library only. No network, API keys, source transcripts, or account data.
Preview includes explicitly draft feed selections; release includes approved only.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT.parent / 'homepage-preview'
EXPECTED_AREAS = ['foundations','methods','application','assessment','inquiry','learning']
EXPECTED_FEED = ['behavioral-science','technology-modeling','operations-strategy','application-analysis']
STATUS_LABELS = {'live':'Live','progress':'Work in progress','soon':'Coming soon'}
PUBLIC_FEED_FIELDS = ['id','title','summary','categories','publisher','sourceUrl','sourceType','briefDate','briefType','sourcePublishedAt','detail']
ICONS = {
 'nodes':'<circle cx="12" cy="12" r="3"/><circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="m7 7 3 3m4 4 3 3M17 7l-3 3m-4 4-3 3"/>',
 'change':'<path d="M4 8h13l-3-3m3 3-3 3M20 16H7l3-3m-3 3 3 3"/><circle cx="4" cy="8" r="1"/><circle cx="20" cy="16" r="1"/>',
 'framework':'<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><rect x="14" y="14" width="7" height="7" rx="1.4"/><path d="M10 6.5h4M6.5 10v4m11-4v4M10 17.5h4"/>',
 'measure':'<path d="M4 3v17h17M8 16v-5m5 5V8m5 8V5"/><path d="m7 7 5-3 6-1"/>',
 'inquiry':'<circle cx="10" cy="10" r="6"/><path d="m14.5 14.5 6 6M7 10h6m-3-3v6"/>',
 'book':'<path d="M12 5c-3-2-6-2-9-1v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1Zm0 0v15M6 8h3m-3 4h3m6-4h3m-3 4h3"/>'
}
def icon(name: str) -> str:
 return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
def esc(s): return html.escape(str(s),quote=True)
def read_json(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(data,encoding='utf-8',newline='\n')
def https_url(value):
 try:
  u=urlparse(value)
  return u.scheme=='https' and bool(u.hostname) and not u.username and not u.password
 except (TypeError,ValueError): return False

def validate(site,platform,feed):
 if [a['id'] for a in platform]!=EXPECTED_AREAS: raise ValueError('Six approved platform areas required, in order.')
 if [x['id'] for x in site['feedCategories']]!=EXPECTED_FEED: raise ValueError('Feed taxonomy differs from approved taxonomy.')
 if site['brandLine']!='exploring the human condition from theory to practice': raise ValueError('Brand line changed.')
 for key in ('currentToolsOrigin','targetOrigin'):
  if not https_url(site[key]): raise ValueError(f'Invalid URL: {key}')
 for key in ('newsletterUrl','linkedinUrl'):
  if site.get(key) is not None and not https_url(site[key]): raise ValueError(f'Invalid URL: {key}')
 for area in platform:
  for tool in area['tools']:
   if tool['status'] not in STATUS_LABELS: raise ValueError('Unknown tool status')
   if tool['status']=='live' and tool.get('path') not in ('/drivers/','/cognitive-security/'): raise ValueError('Live destination requires verification')
 seen=set()
 for item in feed:
  if not re.fullmatch(r'[a-z0-9-]+',item['id']) or item['id'] in seen: raise ValueError('Invalid or duplicated feed ID')
  seen.add(item['id'])
  if not item['title'].strip() or not item['summary'].strip(): raise ValueError('Missing feed prose')
  if not https_url(item['sourceUrl']): raise ValueError('Feed source requires safe HTTPS URL')
  if not item['categories'] or set(item['categories'])-set(EXPECTED_FEED): raise ValueError('Invalid feed category')
  if len(item['categories'])!=len(set(item['categories'])): raise ValueError('Duplicate category')
  date.fromisoformat(item['briefDate'])
  if item.get('sourcePublishedAt'): date.fromisoformat(item['sourcePublishedAt'])
  if item['briefType'] not in ('daily','weekly'): raise ValueError('Unknown brief type')
  if item.get('status') not in ('draft','approved','archived'): raise ValueError('Unknown editorial status')
  if item.get('status')=='approved':
   if item.get('primarySourceChecked') is not True: raise ValueError('Verify primary source before approval')
   date.fromisoformat(item['reviewedAt'])
 return True

def build(mode='preview',tool_links='preview',root=ROOT,output=None):
 site_dir=Path(output) if output else (DEFAULT_SITE if root==ROOT else root/'site')
 site=read_json(root/'content/site.json'); platform=read_json(root/'content/platform.json'); feed=read_json(root/'content/feed.json')
 validate(site,platform,feed)
 selected=[i for i in feed if i['status']=='approved' or (mode=='preview' and i['status']=='draft')]
 selected.sort(key=lambda i:(-date.fromisoformat(i['briefDate']).toordinal(),i.get('order',0),i['id']))
 public_feed=[{k:i.get(k) for k in PUBLIC_FEED_FIELDS} for i in selected]
 def tool_url(path): return site['currentToolsOrigin'].rstrip('/')+path if tool_links=='preview' else '.'+path
 def area_tools(area):
  out=[]
  for t in area['tools']:
   name=f'<a href="{esc(tool_url(t["path"]))}">{esc(t["name"])} ↗</a>' if t['status']=='live' else esc(t['name'])
   link=f'<a class="tool-link" href="#{esc(t["localAnchor"])}">View feed preview →</a>' if t.get('localAnchor') else ''
   out.append(f'<li><h4>{name}</h4><span class="status {t["status"]}">{STATUS_LABELS[t["status"]]}</span><p>{esc(t["description"])}</p>{link}</li>')
  return ''.join(out)
 cards=[]; mega=[]; nodes=[]
 for a in platform:
  has_live=any(t['status']=='live' for t in a['tools'])
  foot='Live & in development' if has_live else ('Coming soon' if a['id']=='learning' else 'Work in progress')
  cards.append(f'<details class="area-card" id="area-{a["id"]}"><summary aria-label="{esc(a["label"]+": "+a["domain"]+" — view tools")}"><div class="area-top"><span class="area-icon">{icon(a["icon"])}</span><span class="area-number">{a["number"]}</span></div><span class="area-label">{esc(a["label"])}</span><h3>{esc(a["domain"])}</h3><p class="area-description">{esc(a["description"])}</p><span class="area-open"><span>{foot}</span><span class="area-plus" aria-hidden="true">+</span></span></summary><ul class="area-tools">{area_tools(a)}</ul></details>')
  mega.append(f'<a class="mega-link" href="#area-{a["id"]}">{icon(a["icon"])}<div><strong>{esc(a["label"])}</strong><span>{esc(a["domain"])}</span></div></a>')
  nodes.append(f'<button type="button" class="map-node map-node-{a["id"]}" data-area="{a["id"]}" aria-pressed="{"true" if a["id"]=="foundations" else "false"}" aria-controls="map-detail"><div><strong>{esc(a["label"])}</strong><small>{esc(a["domain"])}</small></div><span aria-hidden="true">↗</span></button>')
 cats={c['id']:c for c in site['feedCategories']}
 filters=''.join(f'<button type="button" class="filter-chip" data-filter="{c["id"]}" aria-pressed="false" title="{esc(c["description"])}">{esc(c["label"])}</button>' for c in site['feedCategories'])
 feed_html=[]
 for i in selected:
  d=date.fromisoformat(i['briefDate']); ds=d.strftime('%d %b').lstrip('0')
  tags=''.join(f'<span>{esc(cats[k]["short"])}</span>' for k in i['categories'])
  feed_html.append(f'<article class="feed-item" data-categories="{esc(" ".join(i["categories"]))}" data-feed-id="{esc(i["id"])}"><div class="feed-meta"><span class="feed-kind">{esc(i["sourceType"])}</span><time datetime="{d.isoformat()}" title="Selected in the {i["briefType"]} brief, {d.isoformat()}">{ds} · {esc(i["briefType"])}</time></div><h3><button type="button" class="feed-title-button" data-feed-detail="{esc(i["id"])}">{esc(i["title"])}</button></h3><p>{esc(i["summary"])}</p><div class="feed-tags">{tags}</div><div class="feed-source"><a href="{esc(i["sourceUrl"])}" target="_blank" rel="noopener noreferrer">{esc(i["publisher"])}</a><span class="arrow" aria-hidden="true">↗</span></div></article>')
 if not feed_html: feed_html=['<div class="feed-empty"><h3>Research selections are on the way.</h3><p>Approved items from our daily and weekly briefs will appear here.</p></div>']
 replacements={
 'ROBOTS':'<meta name="robots" content="noindex,nofollow">' if mode=='preview' else '',
 'MISSION':esc(site['mission']),'DRIVERS_URL':esc(tool_url('/drivers/')),'COGNITIVE_URL':esc(tool_url('/cognitive-security/')),
 'MEGA_LINKS':''.join(mega),'AREA_CARDS':''.join(cards),'MAP_NODES':''.join(nodes),'FILTERS':filters,'FEED_COUNT':str(len(selected)),
 'FEED_ITEMS':''.join(feed_html),'FEED_SNAPSHOT':'Preview · 4–6 Sep 2026' if mode=='preview' else 'From PSYWERX briefings',
 'PREVIEW_BADGE':'<span class="preview-badge">Preview</span>' if mode=='preview' else '',
 'YEAR':'2026','FOOTER_STATUS':'Homepage design preview · not yet deployed' if mode=='preview' else 'Behavioral & social science · Tools · Research · Learning',
 'BOOK_ICON':icon('book'),'FRAMEWORK_ICON':icon('framework'),'CHANGE_ICON':icon('change')}
 template=(root/'src/homepage.template.html').read_text(encoding='utf-8')
 for k,v in replacements.items(): template=template.replace('{{'+k+'}}',v)
 if re.search(r'{{[A-Z_]+}}',template): raise ValueError('Unresolved template marker')
 write(site_dir/'index.html',template)
 data={'mode':mode,'platform':platform,'feed':public_feed,'feedCategories':site['feedCategories'],'links':{k:site.get(k) for k in ('newsletterUrl','linkedinUrl')}}
 js='window.PSYWERX_HOME = '+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
 write(site_dir/'assets/home-data.js',js)
 manifest={p.relative_to(site_dir).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(site_dir.rglob('*')) if p.is_file()}
 write(root/'docs/BUILD_MANIFEST.json',json.dumps({'mode':mode,'toolLinks':tool_links,'feedCount':len(selected),'files':manifest},indent=2)+'\n')
 return {'mode':mode,'feedCount':len(selected),'totalBytes':sum(x['bytes'] for x in manifest.values())}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--mode',choices=['preview','release'],default='preview')
 parser.add_argument('--tool-links',choices=['preview','local'],default='preview')
 args=parser.parse_args()
 try: print(json.dumps(build(args.mode,args.tool_links),indent=2))
 except (ValueError,KeyError,TypeError,OSError) as exc: print(f'Build failed: {exc}',file=sys.stderr); sys.exit(1)
