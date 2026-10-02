/* Catalogue search + filters (runs on catalogue.html). Data comes from window.SANYO (generated). */
(function () {
  'use strict';
  var S = window.SANYO;
  var form = document.getElementById('cat-form');
  if (!S || !form) return;

  var qInput = document.getElementById('q');
  var albumSel = document.getElementById('album');
  var chipBtns = Array.prototype.slice.call(form.querySelectorAll('[data-section-chip]'));
  var results = document.getElementById('results');
  var countEl = document.getElementById('result-count');
  var state = { q: '', section: '', album: '' };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function norm(s) { return String(s).toLowerCase().replace(/[_·]/g, ' ').replace(/\s+/g, ' ').trim(); }

  function albumOptions() {
    var html = '<option value="">All galleries</option>';
    Object.keys(S.albums).forEach(function (id) {
      var a = S.albums[id];
      if (state.section && a.sec !== state.section) return;
      html += '<option value="' + esc(id) + '"' + (state.album === id ? ' selected' : '') + '>' + esc(a.title) + '</option>';
    });
    albumSel.innerHTML = html;
  }

  function matches(rec, tokens) {
    for (var i = 0; i < tokens.length; i++) { if (rec.s.indexOf(tokens[i]) === -1) return false; }
    return true;
  }

  function card(it) {
    var a = S.albums[it.album];
    var sci = it.named ? it.named.name : a.sci;
    var pageNote = a.pages > 1 ? ' · original page ' + it.pg : '';
    var showAI = !!it.ai && S.site.imageMode === 'ai-illustration';
    var variant = showAI ? 'ai-illustration' : 'original';
    var image = showAI ? it.ai : it.img;
    var alt = showAI ? it.aiAlt : it.alt;
    var aiNote = it.ai ? '<p class="ai-label" data-ai-label' + (showAI ? '' : ' hidden') + '>AI illustration</p>' : '';
    var variantButton = it.ai && S.site.imageMode === 'both'
      ? '<button type="button" class="btn btn-small btn-ghost-dark ai-variant-toggle" data-card-variant aria-pressed="' + (showAI ? 'true' : 'false') + '">' + (showAI ? 'Show original photo' : 'Show AI illustration') + '</button>' : '';
    return '<li class="card" data-item="' + esc(it.id) + '" data-album="' + esc(it.album) + '" data-section="' + esc(it.sec) + '">' +
      '<button type="button" class="card-media" data-open="' + esc(it.id) + '" data-variant="' + variant + '" aria-label="Enlarge: ' + esc(it.title) + '">' +
      '<img src="' + esc(image) + '" data-original-src="' + esc(it.img) + '" data-original-alt="' + esc(it.alt) + '" data-ai-src="' + esc(it.ai || '') + '" data-ai-alt="' + esc(it.aiAlt || '') + '" width="' + it.w + '" height="' + it.h + '" loading="lazy" decoding="async" alt="' + esc(alt) + '"></button>' +
      '<div class="card-body"><h3 class="card-title">' + esc(it.title) + '</h3>' +
      (sci ? '<p class="card-sci"><i>' + esc(sci) + '</i></p>' : '') +
      '<p class="card-src">Source file ' + esc(it.file) + pageNote + '</p>' +
      aiNote + variantButton +
      '<button type="button" class="btn btn-small btn-add" data-add="' + esc(it.id) + '">Add to enquiry</button></div></li>';
  }

  function wholeCategory(albumId) {
    for (var i = 0; i < S.categories.length; i++) {
      var c = S.categories[i];
      if (c.album === albumId && c.photos) return c;
    }
    return null;
  }

  function render() {
    var tokens = norm(state.q).split(' ').filter(Boolean);
    var photos = S.items.filter(function (it) {
      return (!state.section || it.sec === state.section) && (!state.album || it.album === state.album) && matches(it, tokens);
    });
    var cats = S.categories.filter(function (c) {
      return !c.photos && !state.album && (!state.section || c.sec === state.section) && matches(c, tokens);
    });
    var byAlbum = {};
    photos.forEach(function (it) { (byAlbum[it.album] = byAlbum[it.album] || []).push(it); });
    var html = '';
    var groups = 0;
    Object.keys(S.albums).forEach(function (aid) {
      var list = byAlbum[aid];
      if (!list) return;
      groups++;
      var a = S.albums[aid];
      var whole = wholeCategory(aid);
      html += '<section class="result-group" aria-labelledby="g-' + esc(aid) + '"><div class="group-head"><div><h2 id="g-' + esc(aid) + '">' + esc(a.title) +
        ' <span class="muted small">(' + list.length + (list.length === 1 ? ' photo' : ' photos') + (list.length !== a.n ? ' of ' + a.n : '') + ')</span></h2>' +
        (a.sci ? '<span class="group-sci">' + esc(a.sci) + '</span>' : '') + '</div><div class="group-links"><a href="' + esc(a.page) + '">Open gallery page</a>' +
        (whole ? ' <button type="button" class="btn btn-small btn-primary btn-add" data-add="' + esc(whole.id) + '">Add &ldquo;' + esc(a.label) + '&rdquo; (any)</button>' : '') +
        '</div></div><ul class="gallery" data-gallery aria-label="' + esc(a.title) + ' photos">' + list.map(card).join('') + '</ul></section>';
    });
    if (cats.length) {
      html += '<section class="result-group" aria-labelledby="g-cats"><div class="group-head"><h2 id="g-cats">Categories listed without photographs <span class="muted small">(' + cats.length + ')</span></h2></div>' +
        '<p class="muted">Named on the original site but with no photo gallery there. Add one to ask about it.</p><ul class="chip-list">' +
        cats.map(function (c) {
          return '<li class="chip-item"><span class="chip-label">' + esc(c.label) + ' <span class="muted small">(' + esc(secLabel(c.sec)) + ')</span></span>' +
            '<button type="button" class="btn btn-small btn-add" data-add="' + esc(c.id) + '" aria-label="Add ' + esc(c.label) + ' category to enquiry">Add</button></li>';
        }).join('') + '</ul></section>';
    }
    var total = photos.length + cats.length;
    if (!total) {
      var shown = state.q ? '“' + esc(state.q) + '”' : 'these filters';
      html = '<div class="empty-state"><h2>No results for ' + shown + '</h2><p>Try a shorter word, a scientific name or a file number, or clear the filters.</p>' +
        '<p><button type="button" class="btn btn-primary" data-clear>Clear filters</button> ' +
        '<a class="btn btn-ghost-dark" href="enquiry.html#items">Add an item that is not listed</a></p></div>';
      countEl.textContent = 'No results.';
    } else {
      if (!photos.length) {
        countEl.textContent = cats.length + (cats.length === 1 ? ' listed category' : ' listed categories') + ' (no photographs on the original site).';
      } else {
        countEl.textContent = photos.length + (photos.length === 1 ? ' photo' : ' photos') + ' in ' + groups + (groups === 1 ? ' gallery' : ' galleries') +
          (cats.length ? ' and ' + cats.length + (cats.length === 1 ? ' listed category' : ' listed categories') : '') + '.';
      }
    }
    results.innerHTML = html;
    if (window.SanyoUI) window.SanyoUI.syncAddButtons();
  }

  function secLabel(id) {
    for (var i = 0; i < S.sections.length; i++) { if (S.sections[i].id === id) return S.sections[i].label.replace(' (source page)', ''); }
    return id;
  }

  function syncChips() {
    chipBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-section-chip') === state.section ? 'true' : 'false'); });
  }
  function writeUrl() {
    var p = new URLSearchParams();
    if (state.q.trim()) p.set('q', state.q.trim());
    if (state.section) p.set('section', state.section);
    if (state.album) p.set('album', state.album);
    var s = p.toString();
    try { history.replaceState(null, '', location.pathname + (s ? '?' + s : '')); } catch (e) { /* ignore */ }
  }
  function apply() { syncChips(); albumOptions(); writeUrl(); render(); }

  qInput.addEventListener('input', function () { state.q = qInput.value; writeUrl(); render(); });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  albumSel.addEventListener('change', function () { state.album = albumSel.value; writeUrl(); render(); });
  chipBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      state.section = b.getAttribute('data-section-chip');
      if (state.album && S.albums[state.album] && state.section && S.albums[state.album].sec !== state.section) state.album = '';
      apply();
    });
  });
  function clearAll() { state = { q: '', section: '', album: '' }; qInput.value = ''; apply(); qInput.focus(); }
  form.addEventListener('reset', function (e) { e.preventDefault(); clearAll(); });
  document.addEventListener('click', function (e) { if (e.target.closest('[data-clear]')) clearAll(); });

  // initial state from the URL (deep links and refresh)
  var params = new URLSearchParams(location.search);
  state.q = (params.get('q') || '').slice(0, 80);
  var sec = params.get('section') || '';
  if (S.sections.some(function (s) { return s.id === sec; })) state.section = sec;
  var alb = params.get('album') || '';
  if (S.albums[alb] && (!state.section || S.albums[alb].sec === state.section)) state.album = alb;
  qInput.value = state.q;
  apply();
})();
