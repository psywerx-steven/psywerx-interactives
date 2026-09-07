/* PSYWERX homepage interactions. No external dependencies, trackers, or API calls. */
(function () {
  'use strict';
  const data = window.PSYWERX_HOME;
  if (!data || !Array.isArray(data.platform)) return;
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const areaById = new Map(data.platform.map(a => [a.id, a]));
  const itemById = new Map(data.feed.map(i => [i.id, i]));
  const selected = new Set();
  const validFilters = new Set(data.feedCategories.map(c => c.id));
  const filterButtons = $$('[data-filter]');
  const feedCards = $$('.feed-item');
  const dialog = $('#detail-dialog');
  let lastFocus = null;

  function node(tag, text, cls) {
    const el = document.createElement(tag);
    if (text != null) el.textContent = text;
    if (cls) el.className = cls;
    return el;
  }
  function safeUrl(value) {
    try {
      const u = new URL(value);
      return u.protocol === 'https:' && !u.username && !u.password ? u.href : null;
    } catch (_) { return null; }
  }
  function externalLink(text, url) {
    const a = node('a', text);
    a.href = safeUrl(url) || '#';
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    return a;
  }
  function dateLabel(iso) {
    if (!iso) return '';
    return new Intl.DateTimeFormat('en-US', {month:'long',day:'numeric',year:'numeric',timeZone:'UTC'}).format(new Date(iso + 'T00:00:00Z'));
  }
  function openDialog(eyebrow, title, children) {
    lastFocus = document.activeElement;
    $('#dialog-eyebrow').textContent = eyebrow;
    $('#dialog-title').textContent = title;
    $('#dialog-body').replaceChildren(...children);
    dialog.showModal();
  }
  function closeDialog() { dialog.close(); }
  $('.dialog-close').addEventListener('click', closeDialog);
  dialog.addEventListener('close', () => { if (lastFocus && lastFocus.isConnected) lastFocus.focus({preventScroll:true}); });
  dialog.addEventListener('click', e => {
    if (e.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeDialog();
  });

  // The six-area diagram is a navigation component, not a causal relationship graph.
  function selectArea(id) {
    const a = areaById.get(id);
    if (!a) return;
    $$('[data-area]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.area === id)));
    const content = node('div');
    content.append(node('span', a.label.toUpperCase(), 'eyebrow'), node('h3', a.question), node('p', a.description));
    const link = node('a', 'View this area →', 'map-detail-link');
    link.href = '#area-' + id;
    $('#map-detail').replaceChildren(content, link);
  }
  $$('[data-area]').forEach(button => button.addEventListener('click', () => selectArea(button.dataset.area)));
  function revealHashArea() {
    if (!location.hash.startsWith('#area-')) return;
    const el = document.getElementById(location.hash.slice(1));
    if (el && el.matches('details.area-card')) el.open = true;
  }
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (!anchor) return;
    const hash = anchor.getAttribute('href');
    if (hash.startsWith('#area-')) {
      const area = document.getElementById(hash.slice(1));
      if (area) area.open = true;
    }
    ['explore-menu','mobile-menu'].forEach(id => { const menu=document.getElementById(id); if(menu) menu.open=false; });
  });
  window.addEventListener('hashchange', revealHashArea);
  revealHashArea();

  // Multi-select feed filters are OR within the selection. Empty selection = all.
  function syncFilterUrl() {
    try {
      const u = new URL(location.href);
      if (selected.size) u.searchParams.set('feed', Array.from(selected).sort().join(','));
      else u.searchParams.delete('feed');
      history.replaceState(null, '', u.href);
    } catch (_) { /* File previews in restricted hosts may prohibit history writes. */ }
  }
  function applyFilters(updateUrl = true) {
    let visible=0;
    feedCards.forEach(card => {
      const cats=(card.dataset.categories || '').split(' ');
      card.hidden=selected.size > 0 && !cats.some(id => selected.has(id));
      if(!card.hidden) visible++;
    });
    filterButtons.forEach(button => {
      const active=button.dataset.filter === 'all' ? selected.size === 0 : selected.has(button.dataset.filter);
      button.classList.toggle('active',active);
      button.setAttribute('aria-pressed',String(active));
    });
    $('#feed-result-count').textContent=visible+' '+(visible===1?'selection':'selections');
    $('#feed-empty').hidden=visible > 0 || data.feed.length === 0;
    $('.feed-scroll').scrollTop=0;
    if(updateUrl) syncFilterUrl();
  }
  filterButtons.forEach(button => button.addEventListener('click', () => {
    const id=button.dataset.filter;
    if(id==='all') selected.clear();
    else if(selected.has(id)) selected.delete(id);
    else if(validFilters.has(id)) selected.add(id);
    applyFilters();
  }));
  $('#clear-feed').addEventListener('click', () => { selected.clear(); applyFilters(); });
  function loadFilterUrl() {
    selected.clear();
    const saved=(new URL(location.href).searchParams.get('feed')||'').split(',');
    saved.forEach(id=>{if(validFilters.has(id)) selected.add(id);});
    applyFilters(false);
  }
  window.addEventListener('popstate',loadFilterUrl);
  loadFilterUrl();

  $$('[data-feed-detail]').forEach(button => button.addEventListener('click', () => {
    const item=itemById.get(button.dataset.feedDetail);
    if(!item) return;
    const selection=node('p', 'Selected in the '+item.briefType+' brief · '+dateLabel(item.briefDate), 'dialog-meta');
    const summary=node('p',item.summary);
    const detail=node('p',item.detail);
    const source=node('p','Source: '+item.publisher, 'source-label');
    const children=[selection,summary,detail,source];
    if(item.sourcePublishedAt) children.push(node('p','Source publication: '+dateLabel(item.sourcePublishedAt),'dialog-meta'));
    children.push(externalLink('Read the original source ↗',item.sourceUrl));
    openDialog(item.sourceType.toUpperCase(),item.title,children);
  }));

  $$('[data-open-dialog]').forEach(button => button.addEventListener('click', () => {
    switch(button.dataset.openDialog) {
      case 'feed-info':
        openDialog('RESEARCH & DISCUSSION','From the briefs to the bigger picture.',[
          node('p','This feed brings together selected research, technical developments, operational discussions, and analytical approaches from PSYWERX’s daily and weekly reports.'),
          node('p','Use more than one filter to show selections from any of your chosen interests. Dates beside the cards identify the brief; source publication dates appear in the details.'),
          node('p',data.mode==='preview' ? 'This design preview uses six draft selections from the September 4 and September 6, 2026 brief archive. It is not connected to an automatic publishing service. Entries must be reviewed before public release.' : 'Selections are published after editorial review. The feed does not update automatically from private reports.')
        ]);
        break;
    }
  }));
  // Native disclosure navigation, with Escape and click-outside behavior.
  document.addEventListener('keydown', e=>{
    if(e.key!=='Escape') return;
    ['explore-menu','mobile-menu'].forEach(id=>{
      const menu=document.getElementById(id);
      if(menu && menu.open){menu.open=false; menu.querySelector('summary').focus();}
    });
  });
  document.addEventListener('click', e=>{
    ['explore-menu','mobile-menu'].forEach(id=>{
      const menu=document.getElementById(id);
      if(menu && menu.open && !menu.contains(e.target)) menu.open=false;
    });
  });
})();
