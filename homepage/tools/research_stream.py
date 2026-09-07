#!/usr/bin/env python3
"""Canonical PSYWERX research database and public-stream projection."""
from __future__ import annotations
import hashlib, ipaddress, json, os, re, tempfile
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

HANDOFF_SCHEMA="psywerx-research-items-v1"; PUBLIC_SCHEMA="psywerx-public-research-stream-v1"
CATEGORIES=("behavioral-science","technology-modeling","operations-strategy","application-analysis")
DECISIONS=("pending","publish","hold","reject")
HANDOFF_TOP_FIELDS={"schemaVersion","briefDate","briefType","items"}
HANDOFF_ITEM_FIELDS={"sourceItemNumber","primaryCategory","categories","questionAndWhy","whatTheyDid","whatTheyFound","whatItMeans","streamTitle","streamSummary","attribution","sourceUrl","sourcePublishedAt","sourceKey","sourceVerified","briefDate","briefType","streamDecision"}
CANONICAL_FIELDS=("itemId","sourceKey","firstSeenBriefDate","latestSeenBriefDate","sourcePublishedAt","primaryCategory","categories","questionAndWhy","whatTheyDid","whatTheyFound","whatItMeans","streamTitle","streamSummary","attribution","sourceUrl","sourceVerified","streamDecision","decisionDate","publishedAt","reviewRequired")
CONTENT_FIELDS=("sourcePublishedAt","primaryCategory","categories","questionAndWhy","whatTheyDid","whatTheyFound","whatItMeans","streamTitle","streamSummary","attribution","sourceUrl","sourceVerified")
PUBLIC_FIELDS=("itemId","streamTitle","streamSummary","attribution","sourceUrl","categories","sourcePublishedAt","dateAdded")
DOI_RE=re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+",re.I); ITEM_ID_RE=re.compile(r"research-[0-9a-f]{20}")
TRACKING={"fbclid","gclid","mc_cid","mc_eid"}; SENSITIVE={"api_key","apikey","key","password","secret","signature","token"}; NON_SOURCE={"docs.google.com","drive.google.com","localhost"}

class ResearchStreamError(ValueError): pass

def _exact(d, expected, label):
    if not isinstance(d,dict): raise ResearchStreamError(f"{label} must be an object")
    if set(d)!=set(expected): raise ResearchStreamError(f"{label} fields differ; missing={sorted(set(expected)-set(d))}, extra={sorted(set(d)-set(expected))}")
def _date(v,label,nullable=False):
    if v is None and nullable:return None
    if not isinstance(v,str): raise ResearchStreamError(f"{label} must be an ISO date string")
    try:p=date.fromisoformat(v)
    except ValueError as e: raise ResearchStreamError(f"{label} must be YYYY-MM-DD") from e
    if p.isoformat()!=v: raise ResearchStreamError(f"{label} must be canonical YYYY-MM-DD")
    return v
def _text(v,label):
    if not isinstance(v,str) or not v.strip():raise ResearchStreamError(f"{label} must be non-empty text")
    v=" ".join(v.split())
    if len(v)>4000:raise ResearchStreamError(f"{label} is unexpectedly long")
    return v

def normalize_doi(v):
    if not isinstance(v,str):return None
    c=v.strip(); low=c.lower()
    if low.startswith("doi:"):c=c[4:].strip()
    else:
        try:u=urlsplit(c)
        except ValueError:u=None
        if u and u.scheme.lower() in ("http","https") and (u.hostname or "").lower() in ("doi.org","dx.doi.org"):c=u.path.lstrip("/")
        elif not low.startswith("10."):return None
    c=c.strip().lower(); return c if DOI_RE.fullmatch(c) else None

def normalize_url(v):
    if not isinstance(v,str):raise ResearchStreamError("source URL must be text")
    try:u=urlsplit(v.strip()); port=u.port
    except ValueError as e:raise ResearchStreamError("source URL is invalid") from e
    if u.scheme.lower()!="https" or not u.hostname or u.username or u.password:raise ResearchStreamError("source URL must be public HTTPS without credentials")
    host=u.hostname.lower()
    if host in NON_SOURCE or host.endswith(".local"):raise ResearchStreamError("source URL cannot be a private document or local host")
    try:addr=ipaddress.ip_address(host)
    except ValueError:addr=None
    if addr is not None and not addr.is_global:raise ResearchStreamError("source URL cannot use a non-public IP address")
    netloc=host if port in (None,443) else f"{host}:{port}"; path=re.sub(r"/{2,}","/",u.path or "/")
    if path!="/":path=path.rstrip("/")
    q=[(k,val) for k,val in parse_qsl(u.query,keep_blank_values=True) if not k.lower().startswith("utm_") and k.lower() not in TRACKING]
    if any(k.lower() in SENSITIVE or k.lower().startswith("x-amz-") for k,_ in q):raise ResearchStreamError("source URL query appears to contain credentials")
    q.sort(); return urlunsplit(("https",netloc,path,urlencode(q,doseq=True),""))

def normalize_source_identity(key,url):
    kd,ud=normalize_doi(key),normalize_doi(url)
    if kd or ud:
        if kd and ud and kd!=ud:raise ResearchStreamError("sourceKey DOI does not match sourceUrl DOI")
        d=kd or ud; return f"doi:{d}",f"https://doi.org/{d}" if ud else normalize_url(url)
    return normalize_url(key),normalize_url(url)
def item_id_for(key):return "research-"+hashlib.sha256(key.encode()).hexdigest()[:20]

def validate_handoff(p):
    _exact(p,HANDOFF_TOP_FIELDS,"handoff")
    if p["schemaVersion"]!=HANDOFF_SCHEMA:raise ResearchStreamError(f"schemaVersion must be {HANDOFF_SCHEMA}")
    bd=_date(p["briefDate"],"briefDate")
    if p["briefType"]!="daily":raise ResearchStreamError("briefType must be daily")
    if not isinstance(p["items"],list) or not p["items"]:raise ResearchStreamError("items must be a non-empty array")
    nums=set(); keys=set(); out=[]
    for n,raw in enumerate(p["items"]):
        label=f"items[{n}]"; _exact(raw,HANDOFF_ITEM_FIELDS,label); sn=raw["sourceItemNumber"]
        if isinstance(sn,bool) or not isinstance(sn,int) or sn<1 or sn in nums:raise ResearchStreamError(f"{label}.sourceItemNumber must be a unique positive integer")
        nums.add(sn); primary=raw["primaryCategory"]; cats=raw["categories"]
        if primary not in CATEGORIES or not isinstance(cats,list) or not cats or primary not in cats or len(cats)!=len(set(cats)) or any(c not in CATEGORIES for c in cats):raise ResearchStreamError(f"{label}.categories are invalid")
        if raw["briefDate"]!=bd or raw["briefType"]!="daily":raise ResearchStreamError(f"{label} brief provenance must match the handoff")
        if raw["streamDecision"]!="pending":raise ResearchStreamError(f"{label}.streamDecision must be pending")
        if not isinstance(raw["sourceVerified"],bool):raise ResearchStreamError(f"{label}.sourceVerified must be boolean")
        key,url=normalize_source_identity(raw["sourceKey"],raw["sourceUrl"])
        if key in keys:raise ResearchStreamError(f"handoff repeats normalized sourceKey {key}")
        keys.add(key); item={k:raw[k] for k in HANDOFF_ITEM_FIELDS}; item.update(sourceKey=key,sourceUrl=url)
        for f in ("questionAndWhy","whatTheyDid","whatTheyFound","whatItMeans","streamTitle","streamSummary","attribution"):item[f]=_text(item[f],f"{label}.{f}")
        item["sourcePublishedAt"]=_date(item["sourcePublishedAt"],f"{label}.sourcePublishedAt",True); item["categories"]=list(cats); out.append(item)
    return {"schemaVersion":HANDOFF_SCHEMA,"briefDate":bd,"briefType":"daily","items":out}

def extract_handoff(text):
    if not isinstance(text,str) or not text.strip():raise ResearchStreamError("input is empty")
    try:raw=json.loads(text.strip())
    except json.JSONDecodeError:raw=None
    if raw is not None:return validate_handoff(raw)
    matches=[]; malformed=False
    for block in re.findall(r"```(?:json)?\s*\r?\n(.*?)```",text,flags=re.I|re.S):
        if HANDOFF_SCHEMA not in block:continue
        try:c=json.loads(block.strip())
        except json.JSONDecodeError:malformed=True; continue
        if isinstance(c,dict) and c.get("schemaVersion")==HANDOFF_SCHEMA:matches.append(c)
    if len(matches)>1:raise ResearchStreamError(f"multiple fenced {HANDOFF_SCHEMA} objects found")
    if not matches:raise ResearchStreamError("research-items fenced JSON is malformed" if malformed else f"no fenced {HANDOFF_SCHEMA} JSON object found")
    return validate_handoff(matches[0])

def validate_record(r):
    _exact(r,CANONICAL_FIELDS,"research item"); key,url=normalize_source_identity(r["sourceKey"],r["sourceUrl"])
    if key!=r["sourceKey"] or url!=r["sourceUrl"]:raise ResearchStreamError("source identity is not canonical")
    # sourceKey is the canonical deduplication identity. itemId is an opaque, stable public identifier;
    # newly ingested items remain deterministic hashes, while backfilled archive records may retain
    # stable IDs assigned during migration rather than being rewritten solely to match a hash.
    if not isinstance(r["itemId"],str) or not ITEM_ID_RE.fullmatch(r["itemId"]):raise ResearchStreamError("itemId is invalid")
    first=_date(r["firstSeenBriefDate"],"firstSeenBriefDate"); latest=_date(r["latestSeenBriefDate"],"latestSeenBriefDate")
    if first>latest:raise ResearchStreamError("firstSeenBriefDate cannot follow latestSeenBriefDate")
    _date(r["sourcePublishedAt"],"sourcePublishedAt",True); primary=r["primaryCategory"]; cats=r["categories"]
    if primary not in CATEGORIES or not isinstance(cats,list) or not cats or primary not in cats or len(cats)!=len(set(cats)) or any(c not in CATEGORIES for c in cats):raise ResearchStreamError("categories are invalid")
    for f in ("questionAndWhy","whatTheyDid","whatTheyFound","whatItMeans","streamTitle","streamSummary","attribution"):
        if _text(r[f],f)!=r[f]:raise ResearchStreamError(f"{f} is not normalized")
    if not isinstance(r["sourceVerified"],bool):raise ResearchStreamError("sourceVerified must be boolean")
    d=r["streamDecision"]
    if d not in DECISIONS:raise ResearchStreamError("streamDecision is invalid")
    if d=="publish" and r["sourceVerified"] is not True:raise ResearchStreamError("publish records require sourceVerified: true")
    dd=_date(r["decisionDate"],"decisionDate",True); pub=_date(r["publishedAt"],"publishedAt",True)
    if d=="pending" and (dd is not None or pub is not None):raise ResearchStreamError("pending records cannot have decisionDate or publishedAt")
    if d=="publish" and (dd is None or pub is None):raise ResearchStreamError("publish records require decisionDate and publishedAt")
    if d in ("hold","reject") and (dd is None or pub is not None):raise ResearchStreamError(f"{d} records require decisionDate and no publishedAt")
    if not isinstance(r["reviewRequired"],bool):raise ResearchStreamError("reviewRequired must be boolean")
    return r

def _read(path):
    if not path.exists():return []
    out=[]
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():raise ResearchStreamError(f"blank JSONL line in {path.name} at {n}")
        try:r=json.loads(line)
        except json.JSONDecodeError as e:raise ResearchStreamError(f"invalid JSON in {path.name} line {n}: {e.msg}") from e
        out.append(validate_record(r))
    return out
def database_files(path):
    archive=path.parent/"archive"; return [path]+(sorted(archive.glob("*.jsonl")) if archive.exists() else [])
def load_database(path):
    out=[]; keys=set(); ids=set()
    for p in database_files(path):
        for r in _read(p):
            if r["sourceKey"] in keys or r["itemId"] in ids:raise ResearchStreamError(f"duplicate source identity across research database shards: {r['sourceKey']}")
            keys.add(r["sourceKey"]); ids.add(r["itemId"]); out.append(r)
    return out
def _atomic(path,text):
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:f.write(text)
        os.replace(tmp,path)
    except Exception:
        try:os.unlink(tmp)
        except FileNotFoundError:pass
        raise
def write_database(path,records):
    archive=path.parent/"archive"; origins={}; shards=sorted(archive.glob("*.jsonl")) if archive.exists() else []
    for shard in shards:
        for r in _read(shard):origins[r["sourceKey"]]=shard
    groups={path:[]}; groups.update({s:[] for s in shards})
    for r in records:validate_record(r); groups.setdefault(origins.get(r["sourceKey"],path),[]).append(r)
    for target,group in groups.items():
        lines=[json.dumps({f:r[f] for f in CANONICAL_FIELDS},ensure_ascii=False,separators=(",",":")) for r in sorted(group,key=lambda x:x["itemId"])]
        _atomic(target,"\n".join(lines)+("\n" if lines else ""))
def _incoming_record(i):
    return {"itemId":item_id_for(i["sourceKey"]),"sourceKey":i["sourceKey"],"firstSeenBriefDate":i["briefDate"],"latestSeenBriefDate":i["briefDate"],"sourcePublishedAt":i["sourcePublishedAt"],"primaryCategory":i["primaryCategory"],"categories":i["categories"],"questionAndWhy":i["questionAndWhy"],"whatTheyDid":i["whatTheyDid"],"whatTheyFound":i["whatTheyFound"],"whatItMeans":i["whatItMeans"],"streamTitle":i["streamTitle"],"streamSummary":i["streamSummary"],"attribution":i["attribution"],"sourceUrl":i["sourceUrl"],"sourceVerified":i["sourceVerified"],"streamDecision":"pending","decisionDate":None,"publishedAt":None,"reviewRequired":False}
def ingest_handoff(payload,database_path,*,dry_run=False):
    p=validate_handoff(payload); records=load_database(database_path); by={r["sourceKey"]:r for r in records}; rep={"added":[],"updated":[],"unchanged":[],"conflicts":[],"rejected":[]}
    for i in p["items"]:
        incoming=_incoming_record(i); existing=by.get(incoming["sourceKey"])
        if existing is None:records.append(incoming);by[incoming["sourceKey"]]=incoming;rep["added"].append(incoming["itemId"]);continue
        changed=[f for f in CONTENT_FIELDS if existing[f]!=incoming[f]]; old_latest=existing["latestSeenBriefDate"]
        first=min(existing["firstSeenBriefDate"],i["briefDate"]); latest=max(old_latest,i["briefDate"]); provenance=(first!=existing["firstSeenBriefDate"] or latest!=old_latest); existing["firstSeenBriefDate"]=first;existing["latestSeenBriefDate"]=latest
        if not changed:rep["updated" if provenance else "unchanged"].append(existing["itemId"]);continue
        if existing["streamDecision"]!="pending":existing["reviewRequired"]=True;rep["conflicts"].append({"itemId":existing["itemId"],"sourceKey":existing["sourceKey"],"preservedDecision":existing["streamDecision"],"changedFields":changed});continue
        if i["briefDate"]<old_latest:rep["updated" if provenance else "unchanged"].append(existing["itemId"]);continue
        for f in CONTENT_FIELDS:
            if f=="sourceVerified":existing[f]=existing[f] or incoming[f]
            elif f=="sourcePublishedAt" and incoming[f] is None and existing[f] is not None:continue
            else:existing[f]=incoming[f]
        rep["updated"].append(existing["itemId"])
    for r in records:validate_record(r)
    if not dry_run:write_database(database_path,records)
    return {"schemaVersion":HANDOFF_SCHEMA,"briefDate":p["briefDate"],"dryRun":dry_run,**{k:len(v) for k,v in rep.items()},"details":rep}
def public_item(r):
    validate_record(r); return {"itemId":r["itemId"],"streamTitle":r["streamTitle"],"streamSummary":r["streamSummary"],"attribution":r["attribution"],"sourceUrl":r["sourceUrl"],"categories":r["categories"],"sourcePublishedAt":r["sourcePublishedAt"],"dateAdded":r["firstSeenBriefDate"]}
def generate_public_feed(database_path,output_path,*,page_size=24):
    if isinstance(page_size,bool) or not isinstance(page_size,int) or not 1<=page_size<=100:raise ResearchStreamError("page_size must be between 1 and 100")
    records=[r for r in load_database(database_path) if r["streamDecision"]=="publish"]; records.sort(key=lambda r:(r["firstSeenBriefDate"],r["sourcePublishedAt"] or "",r["itemId"]),reverse=True); items=[public_item(r) for r in records]; pages=[items[i:i+page_size] for i in range(0,len(items),page_size)] or [[]]
    page_dir=output_path.parent/"public_feed_pages"; expected=set()
    def env(n,x):return {"schemaVersion":PUBLIC_SCHEMA,"page":n,"pageSize":page_size,"totalItems":len(items),"items":x,"nextPage":f"public_feed_pages/page-{n+1:04d}.json" if n<len(pages) else None}
    _atomic(output_path,json.dumps(env(1,pages[0]),ensure_ascii=False,indent=2)+"\n")
    for n,x in enumerate(pages[1:],2):p=page_dir/f"page-{n:04d}.json";expected.add(p);_atomic(p,json.dumps(env(n,x),ensure_ascii=False,indent=2)+"\n")
    if page_dir.exists():
        for p in page_dir.glob("page-*.json"):
            if p not in expected:p.unlink()
        try:page_dir.rmdir()
        except OSError:pass
    return env(1,pages[0])
def review_item(database_path,item_id,decision,decision_date):
    if decision not in ("publish","hold","reject"):raise ResearchStreamError("decision must be publish, hold, or reject")
    _date(decision_date,"decision date"); records=load_database(database_path); match=[r for r in records if r["itemId"]==item_id]
    if not match:raise ResearchStreamError(f"unknown itemId: {item_id}")
    r=match[0]
    if decision=="publish" and r["sourceVerified"] is not True:raise ResearchStreamError("sourceVerified must be true before publish")
    previous=r["streamDecision"];r["streamDecision"]=decision;r["decisionDate"]=decision_date;r["publishedAt"]=decision_date if decision=="publish" else None;r["reviewRequired"]=False;write_database(database_path,records)
    return {"itemId":item_id,"previousDecision":previous,"streamDecision":decision,"decisionDate":decision_date}
