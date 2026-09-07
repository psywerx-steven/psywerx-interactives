/* PSYWERX homepage interactions. No external dependencies, trackers, or API calls. */
(function () {
  'use strict';
  const data = window.PSYWERX_HOME;
  if (!data || !Array.isArray(data.platform)) return;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const areaById = new Map(data.platform.map(area => [area.id, area]));
  const selected = new Set();
  const validFilters = new Set(data.feedCategories.map(category => category.id));
  const filterButtons = $$('[data-filter]');
  const dialog = $('#detail-dialog');
  const loadOlderButton = $('#load-older');
  const loadedIds = new Set($$('.feed-item').map(card => card.dataset.feedId));
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  let nextPage = data.feedPagination && data.feedPagination.nextPage;
  let lastFocus = null;

  function node(tag, text, cls) {
    const element = document.createElement(tag);
    if (text != null) element.textContent = text;
    if (cls) element.className = cls;
    return element;
  }

  function safeExternalUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
    } catch (_) {
      return null;
    }
  }

  function safeFeedPageUrl(value) {
    if (!value) return null;
    try {
      const url = new URL(value, location.href);
      const validPath = /\/data\/research-stream\/public_feed_pages\/page-\d{4}\.json$/.test(url.pathname);
      return url.origin === location.origin && validPath && !url.search && !url.hash ? url.href : null;
    } catch (_) {
      return null;
    }
  }

  function validIsoDate(value, nullable = false) {
    if (value === null) return nullable;
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const parsed = new Date(value + 'T00:00:00Z');
    return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
  }

  function formatDate(value) {
    if (value === null) return 'date unavailable';
    const [year, month, day] = value.split('-').map(Number);
    return `${monthNames[month - 1]} ${day}, ${year}`;
  }

  function openDialog(eyebrow, title, children) {
    lastFocus = document.activeElement;
    $('#dialog-eyebrow').textContent = eyebrow;
    $('#dialog-title').textContent = title;
    $('#dialog-body').replaceChildren(...children);
    dialog.showModal();
  }

  function closeDialog() {
    dialog.close();
  }

  $('.dialog-close').addEventListener('click', closeDialog);
  dialog.addEventListener('close', () => {
    if (lastFocus && lastFocus.isConnected) lastFocus.focus({preventScroll: true});
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (
      event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom
    ) closeDialog();
  });

  // The six-area diagram is navigation, not a causal relationship graph.
  function selectArea(id) {
    const area = areaById.get(id);
    if (!area) return;
    $$('[data-area]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.area === id)));
    const content = node('div');
    content.append(node('span', area.label.toUpperCase(), 'eyebrow'), node('h3', area.question), node('p', area.description));
    const link = node('a', 'View this area →', 'map-detail-link');
    link.href = '#area-' + id;
    $('#map-detail').replaceChildren(content, link);
  }

  $$('[data-area]').forEach(button => button.addEventListener('click', () => selectArea(button.dataset.area)));

  function revealHashArea() {
    if (!location.hash.startsWith('#area-')) return;
    const element = document.getElementById(location.hash.slice(1));
    if (element && element.matches('details.area-card')) element.open = true;
  }

  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (!anchor) return;
    const hash = anchor.getAttribute('href');
    if (hash.startsWith('#area-')) {
      const area = document.getElementById(hash.slice(1));
      if (area) area.open = true;
    }
    ['explore-menu', 'mobile-menu'].forEach(id => {
      const menu = document.getElementById(id);
      if (menu) menu.open = false;
    });
  });
  window.addEventListener('hashchange', revealHashArea);
  revealHashArea();

  // Multi-select feed filters are OR within the selection. Empty selection = all.
  function syncFilterUrl() {
    try {
      const url = new URL(location.href);
      if (selected.size) url.searchParams.set('feed', Array.from(selected).sort().join(','));
      else url.searchParams.delete('feed');
      history.replaceState(null, '', url.href);
    } catch (_) {
      // Restricted file previews may prohibit history writes.
    }
  }

  function applyFilters(updateUrl = true) {
    const cards = $$('.feed-item');
    let visible = 0;
    cards.forEach(card => {
      const categories = (card.dataset.categories || '').split(' ');
      card.hidden = selected.size > 0 && !categories.some(id => selected.has(id));
      if (!card.hidden) visible += 1;
    });
    filterButtons.forEach(button => {
      const active = button.dataset.filter === 'all' ? selected.size === 0 : selected.has(button.dataset.filter);
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    $('#feed-result-count').textContent = visible + ' ' + (visible === 1 ? 'selection' : 'selections');
    $('#feed-empty').hidden = visible > 0 || cards.length === 0;
    $('.feed-scroll').scrollTop = 0;
    if (updateUrl) syncFilterUrl();
  }

  filterButtons.forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.filter;
    if (id === 'all') selected.clear();
    else if (selected.has(id)) selected.delete(id);
    else if (validFilters.has(id)) selected.add(id);
    applyFilters();
  }));
  $('#clear-feed').addEventListener('click', () => {
    selected.clear();
    applyFilters();
  });

  function loadFilterUrl() {
    selected.clear();
    const saved = (new URL(location.href).searchParams.get('feed') || '').split(',');
    saved.forEach(id => {
      if (validFilters.has(id)) selected.add(id);
    });
    applyFilters(false);
  }
  window.addEventListener('popstate', loadFilterUrl);
  loadFilterUrl();

  function validPublicItem(item) {
    return item &&
      typeof item.itemId === 'string' && /^research-[0-9a-f]{20}$/.test(item.itemId) &&
      typeof item.streamTitle === 'string' && item.streamTitle.trim() &&
      typeof item.streamSummary === 'string' && item.streamSummary.trim() &&
      typeof item.attribution === 'string' && item.attribution.trim() &&
      safeExternalUrl(item.sourceUrl) &&
      Array.isArray(item.categories) && item.categories.length > 0 &&
      item.categories.every(category => validFilters.has(category)) &&
      validIsoDate(item.sourcePublishedAt, true) &&
      validIsoDate(item.dateAdded);
  }

  function renderFeedCard(item) {
    const article = node('article', null, 'feed-item');
    article.dataset.categories = item.categories.join(' ');
    article.dataset.feedId = item.itemId;
    const meta = node('div', null, 'feed-meta');
    meta.append(
      node('span', 'Published ' + formatDate(item.sourcePublishedAt)),
      node('span', 'Added ' + formatDate(item.dateAdded))
    );
    const title = node('h3', item.streamTitle);
    const summary = node('p', item.streamSummary);
    const source = node('div', null, 'feed-source');
    const link = node('a', item.attribution);
    link.href = safeExternalUrl(item.sourceUrl);
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    const arrow = node('span', '↗', 'arrow');
    arrow.setAttribute('aria-hidden', 'true');
    source.append(link, arrow);
    article.append(meta, title, summary, source);
    return article;
  }

  function syncLoadOlder() {
    loadOlderButton.hidden = !safeFeedPageUrl(nextPage);
  }

  loadOlderButton.addEventListener('click', async () => {
    const url = safeFeedPageUrl(nextPage);
    if (!url) return;
    loadOlderButton.disabled = true;
    loadOlderButton.textContent = 'Loading…';
    try {
      const response = await fetch(url, {credentials: 'same-origin'});
      if (!response.ok) throw new Error('Research page request failed');
      const page = await response.json();
      if (
        page.schemaVersion !== 'psywerx-public-research-stream-v1' ||
        !Array.isArray(page.items) ||
        !page.items.every(validPublicItem)
      ) throw new Error('Research page is invalid');
      const container = $('#feed-items');
      const initialEmpty = container.querySelector('.feed-empty');
      if (initialEmpty) initialEmpty.remove();
      page.items.forEach(item => {
        if (loadedIds.has(item.itemId)) return;
        loadedIds.add(item.itemId);
        container.append(renderFeedCard(item));
      });
      nextPage = page.nextPage ? new URL(page.nextPage, new URL('../', url)).href : null;
      applyFilters(false);
    } catch (_) {
      $('#feed-result-count').textContent = 'Older selections could not be loaded';
    } finally {
      loadOlderButton.disabled = false;
      loadOlderButton.textContent = 'Load older selections →';
      syncLoadOlder();
    }
  });
  syncLoadOlder();

  $$('[data-open-dialog]').forEach(button => button.addEventListener('click', () => {
    if (button.dataset.openDialog !== 'feed-info') return;
    openDialog('RESEARCH & DISCUSSION', 'From the Morning Brief to the public stream.', [
      node('p', 'Each Morning Brief contributes every research item to the PSYWERX research database. Inclusion there supports retrieval, source tracking, deduplication, and later analysis.'),
      node('p', 'Only items the owner explicitly chooses to publish appear here. Hold and reject decisions keep an item in the research database without placing it in the public stream.'),
      node('p', 'Published identifies the source publication date when known; Added identifies the Morning Brief date when PSYWERX first added the item. Use more than one filter to show selections matching any of your chosen interests.')
    ]);
  }));

  // Native disclosure navigation, with Escape and click-outside behavior.
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    ['explore-menu', 'mobile-menu'].forEach(id => {
      const menu = document.getElementById(id);
      if (menu && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
  });
  document.addEventListener('click', event => {
    ['explore-menu', 'mobile-menu'].forEach(id => {
      const menu = document.getElementById(id);
      if (menu && menu.open && !menu.contains(event.target)) menu.open = false;
    });
  });
})();
