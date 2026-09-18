(function(){
'use strict';
const LIVE_URL='https://raw.githubusercontent.com/psywerx-steven/psywerx-interactives/research-data/data/research-stream/explorer.json';
const labels={'behavioral-science':'Behavioral Science','technology-modeling':'Technology & Modeling','operations-strategy':'Operations & Strategy','application-analysis':'Application & Analysis'};
const validCategories=new Set(Object.keys(labels));
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const text=(tag,value,cls)=>{const e=document.createElement(tag);if(value!=null)e.textContent=value;if(cls)e.className=cls;return e};
const state={category:'all',query:'',view:'items',from:'',to:'',item:null,focusBrief:null};
let suppressDialogClose=false;

function validData(data){
  return data&&data.schemaVersion==='psywerx-research-explorer-v1'&&Array.isArray(data.items)&&Array.isArray(data.briefs);
}
function validDate(value){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return false;
  const parsed=new Date(value+'T00:00:00Z');
  return !Number.isNaN(parsed.getTime())&&parsed.toISOString().slice(0,10)===value;
}
function displayDate(value){
  if(!validDate(value))return 'date unavailable';
  return new Intl.DateTimeFormat('en-US',{month:'short',day:'numeric',year:'numeric',timeZone:'UTC'}).format(new Date(value+'T00:00:00Z'));
}
function shortDate(value){
  if(!validDate(value))return '—';
  return new Intl.DateTimeFormat('en-US',{month:'short',day:'numeric',timeZone:'UTC'}).format(new Date(value+'T00:00:00Z'));
}
function safeExternalUrl(value){
  try{const url=new URL(value);return url.protocol==='https:'&&!url.username&&!url.password?url.href:null}catch(_){return null}
}
async function loadData(){
  try{
    const response=await fetch(LIVE_URL,{cache:'no-store',credentials:'omit'});
    if(response.ok){const live=await response.json();if(validData(live))return live;}
  }catch(_){/* use bundled projection if available */}
  return validData(window.PSYWERX_RESEARCH)?window.PSYWERX_RESEARCH:null;
}
function readUrlState(){
  try{
    const params=new URL(location.href).searchParams;
    const category=params.get('category');
    state.category=validCategories.has(category)?category:'all';
    state.query=(params.get('q')||'').slice(0,200);
    state.view=params.get('view')==='briefs'?'briefs':'items';
    state.from=validDate(params.get('from'))?params.get('from'):'';
    state.to=validDate(params.get('to'))?params.get('to'):'';
    state.item=/^research-[0-9a-f]{20}$/.test(params.get('item')||'')?params.get('item'):null;
  }catch(_){/* restricted previews can lack URL access */}
}
function syncUrl(){
  try{
    const url=new URL(location.href);
    const set=(key,value,keep)=>{if(keep)url.searchParams.set(key,value);else url.searchParams.delete(key)};
    set('view',state.view,state.view!=='items');
    set('category',state.category,state.category!=='all');
    set('q',state.query,state.query.trim().length>0);
    set('from',state.from,Boolean(state.from));
    set('to',state.to,Boolean(state.to));
    set('item',state.item,state.item!=null);
    history.replaceState(null,'',url.href);
  }catch(_){/* file previews may prohibit history changes */}
}

function init(data){
  const byId=new Map(data.items.map(item=>[item.itemId,item]));
  const briefDates=data.briefs.map(brief=>brief.briefDate).filter(validDate).sort();
  const minDate=briefDates[0]||'';
  const maxDate=briefDates[briefDates.length-1]||'';
  const detail=$('#detail');
  let activeBriefDate=null;

  function contentMatch(item){
    if(state.category!=='all'&&!item.categories.includes(state.category))return false;
    const q=state.query.trim().toLowerCase();
    if(!q)return true;
    return [item.streamTitle,item.streamSummary,item.attribution,item.questionAndWhy,item.whatTheyDid,item.whatTheyFound,item.whatItMeans]
      .join(' ').toLowerCase().includes(q);
  }
  function inRange(dateValue){
    if(!validDate(dateValue))return !state.from&&!state.to;
    if(state.from&&dateValue<state.from)return false;
    if(state.to&&dateValue>state.to)return false;
    return true;
  }
  function itemMatch(item){return contentMatch(item)&&inRange(item.dateAdded)}
  function briefItems(brief){return brief.itemIds.map(id=>byId.get(id)).filter(Boolean).filter(contentMatch)}
  function matchingBriefs(){return data.briefs.filter(brief=>inRange(brief.briefDate)&&briefItems(brief).length>0)}
  function matchingItems(){return data.items.filter(itemMatch)}

  function itemCard(item,briefDate=null){
    const card=text('article',null,'card');
    card.tabIndex=0;card.setAttribute('role','button');card.setAttribute('aria-label','Open '+item.streamTitle);
    const meta=text('div',null,'meta');
    meta.append(text('span',labels[item.primaryCategory]||item.primaryCategory),text('span','Surfaced '+displayDate(briefDate||item.dateAdded)));
    card.append(meta,text('h3',item.streamTitle),text('p',item.streamSummary),text('div',item.attribution,'source'));
    const open=()=>openDetail(item,briefDate||item.dateAdded,true);
    card.addEventListener('click',open);
    card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open()}});
    return card;
  }

  function openDetail(item,briefDate=item.dateAdded,updateUrl=false){
    activeBriefDate=validDate(briefDate)?briefDate:item.dateAdded;
    $('#detail-meta').textContent=(labels[item.primaryCategory]||item.primaryCategory)+' · Surfaced '+displayDate(activeBriefDate)+(validDate(item.sourcePublishedAt)?' · Source published '+displayDate(item.sourcePublishedAt):'');
    $('#detail-title').textContent=item.streamTitle;
    $('#detail-summary').textContent=item.streamSummary;
    $('#detail-question').textContent=item.questionAndWhy;
    $('#detail-did').textContent=item.whatTheyDid;
    $('#detail-found').textContent=item.whatTheyFound;
    $('#detail-means').textContent=item.whatItMeans;
    const source=safeExternalUrl(item.sourceUrl);
    $('#detail-source').href=source||'#';
    $('#detail-source').textContent=item.attribution+' ↗';
    $('#detail-source').hidden=!source;
    state.item=item.itemId;
    if(updateUrl)syncUrl();
    if(!detail.open)detail.showModal();
  }
  function closeDetail(updateUrl=true){
    if(detail.open){suppressDialogClose=true;detail.close();suppressDialogClose=false;}
    state.item=null;activeBriefDate=null;
    if(updateUrl)syncUrl();
  }

  function updateControls(){
    $('#search').value=state.query;
    $('#date-from').value=state.from;
    $('#date-to').value=state.to;
    $$('[data-category]').forEach(button=>{
      const active=button.dataset.category===state.category;
      button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));
    });
    $$('[data-view]').forEach(button=>{
      const active=button.dataset.view===state.view;
      button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));
    });
    $('#items-view').hidden=state.view!=='items';
    $('#briefs-view').hidden=state.view!=='briefs';
  }

  function updateSummary(items,briefs){
    $('#filtered-items').textContent=items.length;
    $('#filtered-briefs').textContent=briefs.length;
    const summary=$('#category-summary');summary.replaceChildren();
    Object.entries(labels).forEach(([id,label])=>{
      const count=items.filter(item=>item.categories.includes(id)).length;
      const pill=text('span',count+' '+label);pill.className='summary-pill';summary.append(pill);
    });
    const rangeStart=state.from||minDate,rangeEnd=state.to||maxDate;
    $('#sort-note').textContent=(rangeStart&&rangeEnd)?'Newest first · '+shortDate(rangeStart)+'–'+shortDate(rangeEnd):'Newest first';
  }

  function renderItems(items){
    $('#items-view').replaceChildren(...items.map(item=>itemCard(item)));
    $('#result-count').textContent=items.length+' '+(items.length===1?'research item':'research items');
    $('#empty').hidden=items.length>0;
  }

  function briefCard(brief){
    const matches=briefItems(brief);
    const card=text('article',null,'brief-card');card.id='brief-'+brief.briefDate;
    const meta=text('div',null,'meta');meta.append(text('span','PSYWERX Daily Brief'),text('span',displayDate(brief.briefDate)));
    card.append(meta,text('h3',displayDate(brief.briefDate)+' — PSYWERX Daily Brief'));
    const total=brief.totalItems||brief.itemIds.length;
    const countText=matches.length===total?total+' research items':matches.length+' of '+total+' items match current filters';
    const counts=Object.entries(brief.categoryCounts||{}).filter(([,n])=>n).map(([id,n])=>n+' '+(labels[id]||id)).join(' · ');
    card.append(text('p',countText+(counts?' · '+counts:'')));
    const button=text('button','Open brief →');button.type='button';button.setAttribute('aria-expanded','false');
    const itemsWrap=text('div',null,'brief-items');itemsWrap.hidden=true;
    const openBrief=()=>{
      const opening=itemsWrap.hidden;
      itemsWrap.hidden=!opening;button.textContent=opening?'Close brief ↑':'Open brief →';button.setAttribute('aria-expanded',String(opening));
      if(opening&&!itemsWrap.childNodes.length)matches.forEach(item=>itemsWrap.append(itemCard(item,brief.briefDate)));
    };
    button.addEventListener('click',openBrief);card.append(button,itemsWrap);
    if(state.focusBrief===brief.briefDate){openBrief();state.focusBrief=null;queueMicrotask(()=>card.scrollIntoView({block:'start',behavior:'smooth'}));}
    return card;
  }

  function render(){
    updateControls();
    const items=matchingItems(),briefs=matchingBriefs();
    updateSummary(items,briefs);
    if(state.view==='items')renderItems(items);
    else{
      $('#briefs-view').replaceChildren(...briefs.map(briefCard));
      $('#result-count').textContent=briefs.length+' '+(briefs.length===1?'Daily Brief':'Daily Briefs');
      $('#empty').hidden=briefs.length>0;
    }
    syncUrl();
  }

  function normalizeRange(changed){
    if(state.from&&state.to&&state.from>state.to){
      if(changed==='from')state.to=state.from;else state.from=state.to;
    }
  }

  readUrlState();
  $('#item-total').textContent=data.totalItems;
  $('#brief-total').textContent=data.briefs.length;
  $('#archive-span').textContent=minDate&&maxDate?shortDate(minDate)+'–'+shortDate(maxDate):'—';
  if(minDate){$('#date-from').min=minDate;$('#date-to').min=minDate}
  if(maxDate){$('#date-from').max=maxDate;$('#date-to').max=maxDate}

  $('#search').addEventListener('input',event=>{state.query=event.target.value.slice(0,200);render()});
  $$('[data-category]').forEach(button=>button.addEventListener('click',()=>{state.category=button.dataset.category;render()}));
  $('#date-from').addEventListener('change',event=>{state.from=validDate(event.target.value)?event.target.value:'';normalizeRange('from');render()});
  $('#date-to').addEventListener('change',event=>{state.to=validDate(event.target.value)?event.target.value:'';normalizeRange('to');render()});
  $('#clear-filters').addEventListener('click',()=>{state.category='all';state.query='';state.from='';state.to='';render()});
  $$('[data-view]').forEach(button=>button.addEventListener('click',()=>{state.view=button.dataset.view;render()}));
  $('#close-detail').addEventListener('click',()=>closeDetail());
  detail.addEventListener('click',event=>{if(event.target===detail)closeDetail()});
  detail.addEventListener('close',()=>{if(!suppressDialogClose&&state.item){state.item=null;activeBriefDate=null;syncUrl()}});
  $('#detail-brief').addEventListener('click',()=>{
    const date=activeBriefDate;
    closeDetail(false);
    state.view='briefs';state.focusBrief=date;render();
  });
  window.addEventListener('popstate',()=>{
    readUrlState();render();
    if(state.item&&byId.has(state.item))openDetail(byId.get(state.item),byId.get(state.item).dateAdded,false);
    else if(detail.open)closeDetail(false);
  });

  render();
  if(state.item&&byId.has(state.item))openDetail(byId.get(state.item),byId.get(state.item).dateAdded,false);
}

loadData().then(data=>{if(data)init(data);else{$('#result-count').textContent='Research archive unavailable';$('#empty').hidden=false;}});
})();
