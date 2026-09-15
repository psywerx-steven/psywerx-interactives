(function(){
'use strict';
const LIVE_URL='https://raw.githubusercontent.com/psywerx-steven/psywerx-interactives/research-data/data/research-stream/explorer.json';
const labels={'behavioral-science':'Behavioral Science','technology-modeling':'Technology & Modeling','operations-strategy':'Operations & Strategy','application-analysis':'Application & Analysis'};
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const text=(tag,value,cls)=>{const e=document.createElement(tag);e.textContent=value;if(cls)e.className=cls;return e};

function validData(data){
  return data&&data.schemaVersion==='psywerx-research-explorer-v1'&&Array.isArray(data.items)&&Array.isArray(data.briefs);
}

async function loadData(){
  try{
    const response=await fetch(LIVE_URL,{cache:'no-store',credentials:'omit'});
    if(response.ok){const live=await response.json();if(validData(live))return live;}
  }catch(_){/* fall back to bundled data when available */}
  return validData(window.PSYWERX_RESEARCH)?window.PSYWERX_RESEARCH:null;
}

function init(data){
  const byId=new Map(data.items.map(i=>[i.itemId,i]));
  let category='all',query='',view='items';
  const escDate=v=>v||'date unavailable';
  function itemCard(item){
    const card=text('article','', 'card');card.tabIndex=0;card.setAttribute('role','button');card.setAttribute('aria-label','Open '+item.streamTitle);
    const meta=text('div','', 'meta');meta.append(text('span',labels[item.primaryCategory]||item.primaryCategory),text('span','Added '+escDate(item.dateAdded)));
    card.append(meta,text('h3',item.streamTitle),text('p',item.streamSummary),text('div',item.attribution,'source'));
    const open=()=>openDetail(item);card.addEventListener('click',open);card.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}});return card;
  }
  function openDetail(item){
    $('#detail-meta').textContent=(labels[item.primaryCategory]||item.primaryCategory)+' · Added '+item.dateAdded;
    $('#detail-title').textContent=item.streamTitle;$('#detail-summary').textContent=item.streamSummary;$('#detail-question').textContent=item.questionAndWhy;$('#detail-did').textContent=item.whatTheyDid;$('#detail-found').textContent=item.whatTheyFound;$('#detail-means').textContent=item.whatItMeans;$('#detail-source').href=item.sourceUrl;$('#detail-source').textContent=item.attribution+' ↗';$('#detail').showModal();
  }
  function filtered(){const q=query.trim().toLowerCase();return data.items.filter(item=>{if(category!=='all'&&!item.categories.includes(category))return false;if(!q)return true;return [item.streamTitle,item.streamSummary,item.attribution,item.questionAndWhy,item.whatTheyDid,item.whatTheyFound,item.whatItMeans].join(' ').toLowerCase().includes(q)})}
  function renderItems(){const items=filtered();$('#items-view').replaceChildren(...items.map(itemCard));$('#result-count').textContent=items.length+' '+(items.length===1?'item':'items');$('#empty').hidden=items.length>0}
  function briefCard(brief){
    const card=text('article','', 'brief-card');const meta=text('div','', 'meta');meta.append(text('span','PSYWERX Daily Brief'),text('span',brief.briefDate));card.append(meta,text('h3',brief.briefDate+' — PSYWERX Daily Brief'));
    const counts=Object.entries(brief.categoryCounts||{}).filter(([,n])=>n).map(([id,n])=>n+' '+labels[id]).join(' · ');card.append(text('p',brief.totalItems+' research items'+(counts?' · '+counts:'')));
    const button=text('button','Open brief →');const itemsWrap=text('div','', 'brief-items');itemsWrap.hidden=true;
    button.addEventListener('click',()=>{const opening=itemsWrap.hidden;itemsWrap.hidden=!opening;button.textContent=opening?'Close brief ↑':'Open brief →';if(opening&&!itemsWrap.childNodes.length){brief.itemIds.map(id=>byId.get(id)).filter(Boolean).forEach(item=>itemsWrap.append(itemCard(item)))}});card.append(button,itemsWrap);return card;
  }
  function renderBriefs(){$('#briefs-view').replaceChildren(...data.briefs.map(briefCard));$('#result-count').textContent=data.briefs.length+' '+(data.briefs.length===1?'brief':'briefs');$('#empty').hidden=data.briefs.length>0}
  function render(){if(view==='items')renderItems();else renderBriefs()}
  $('#item-total').textContent=data.totalItems;$('#brief-total').textContent=data.briefs.length;
  $('#search').addEventListener('input',e=>{query=e.target.value;renderItems()});
  $$('[data-category]').forEach(button=>button.addEventListener('click',()=>{category=button.dataset.category;$$('[data-category]').forEach(b=>b.classList.toggle('active',b===button));renderItems()}));
  $$('[data-view]').forEach(button=>button.addEventListener('click',()=>{view=button.dataset.view;$$('[data-view]').forEach(b=>b.classList.toggle('active',b===button));$('#items-view').hidden=view!=='items';$('#briefs-view').hidden=view!=='briefs';$('#item-controls').hidden=view!=='items';render()}));
  $('#close-detail').addEventListener('click',()=>$('#detail').close());$('#detail').addEventListener('click',e=>{if(e.target===$('#detail'))$('#detail').close()});render();
}

loadData().then(data=>{if(data)init(data);else{$('#result-count').textContent='Research archive unavailable';$('#empty').hidden=false;}});
})();
