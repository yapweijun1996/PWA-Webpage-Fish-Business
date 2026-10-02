/* Shared UI: navigation toggle, enquiry counters, add-to-enquiry buttons, toasts, accessible lightbox. */
(function () {
  'use strict';
  var E = window.SanyoEnquiry;
  var S = window.SANYO || null;

  /* ---------------- navigation toggle ---------------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.querySelector('.nav-toggle-label').textContent = open ? 'Close' : 'Menu';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.querySelector('.nav-toggle-label').textContent = 'Menu';
        toggle.focus();
      }
    });
  }

  /* ---------------- counters ---------------- */
  function updateCounts() {
    var n = E.count();
    document.querySelectorAll('[data-enquiry-count]').forEach(function (el) {
      el.textContent = String(n);
      el.setAttribute('aria-label', n + (n === 1 ? ' item' : ' items') + ' in enquiry list');
    });
  }

  /* ---------------- toasts ---------------- */
  var region = document.getElementById('toast-region');
  var toastTimer = null;
  function toast(message, opts) {
    if (!region) return;
    opts = opts || {};
    region.textContent = '';
    var t = document.createElement('div');
    t.className = 'toast' + (opts.warn ? ' is-warn' : '');
    var span = document.createElement('span');
    span.textContent = message;
    t.appendChild(span);
    if (opts.href) {
      var a = document.createElement('a');
      a.href = opts.href;
      a.textContent = opts.linkText || 'View list';
      t.appendChild(a);
    }
    if (opts.action) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn btn-small btn-accent';
      b.textContent = opts.action.label;
      b.addEventListener('click', function () { opts.action.run(); region.textContent = ''; });
      t.appendChild(b);
    }
    region.appendChild(t);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { region.textContent = ''; }, opts.ttl || 6000);
  }

  /* ---------------- add buttons ---------------- */
  function syncAddButtons() {
    var ids = {};
    E.getItems().forEach(function (x) { ids[x.id] = true; });
    document.querySelectorAll('[data-add]').forEach(function (btn) {
      if (!btn.hasAttribute('data-label')) btn.setAttribute('data-label', btn.textContent.trim());
      var inList = !!ids[btn.getAttribute('data-add')];
      btn.classList.toggle('is-added', inList);
      if (inList) {
        btn.setAttribute('aria-disabled', 'true');
        btn.textContent = btn.classList.contains('btn-small') && btn.closest('.chip-item') ? 'Added' : 'In enquiry list';
      } else {
        btn.removeAttribute('aria-disabled');
        btn.textContent = btn.getAttribute('data-label');
      }
    });
    var lbAdd = document.querySelector('[data-lb-add]');
    var lb = document.getElementById('lightbox');
    if (lbAdd && lb && lb.open && lb.dataset.current) {
      var inL = !!ids[lb.dataset.current];
      lbAdd.textContent = inL ? 'In enquiry list' : 'Add to enquiry';
      if (inL) lbAdd.setAttribute('aria-disabled', 'true'); else lbAdd.removeAttribute('aria-disabled');
    }
  }

  function handleAdd(id, variant) {
    var r = E.addFromCatalogue(id, variant);
    var label = (E.getItems().filter(function (x) { return x.id === id; })[0] || {}).label || 'Item';
    if (r.status === 'added') {
      toast('Added “' + label + '” to your enquiry list.', { href: 'enquiry.html' });
    } else if (r.status === 'duplicate') {
      toast('“' + label + '” is already in your list — it was not added twice. Change its quantity on the enquiry page.', { href: 'enquiry.html', linkText: 'Open list', warn: true });
    } else {
      toast('That item could not be added.', { warn: true });
    }
    if (!E.storageHealthy()) {
      toast('Your browser is blocking storage, so the list is kept only while this page stays open.', { warn: true, ttl: 9000 });
    }
    syncAddButtons();
  }

  function setCardVariant(card, variant) {
    if (!card) return;
    var media = card.querySelector('[data-open]');
    var image = media && media.querySelector('img');
    if (!media || !image) return;
    var useAI = variant === 'ai-illustration' && !!image.getAttribute('data-ai-src');
    media.dataset.variant = useAI ? 'ai-illustration' : 'original';
    image.src = useAI ? image.getAttribute('data-ai-src') : image.getAttribute('data-original-src');
    image.alt = useAI ? image.getAttribute('data-ai-alt') : image.getAttribute('data-original-alt');
    var label = card.querySelector('[data-ai-label]');
    if (label) label.hidden = !useAI;
    var toggleBtn = card.querySelector('[data-card-variant]');
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-pressed', useAI ? 'true' : 'false');
      toggleBtn.textContent = useAI ? 'Show original photo' : 'Show AI illustration';
    }
  }

  function setThumbnailVariant(thumbnail, variant, button) {
    var image = thumbnail && thumbnail.querySelector('img[data-ai-src]');
    if (!image) return;
    var useAI = variant === 'ai-illustration' && !!image.getAttribute('data-ai-src');
    thumbnail.dataset.variant = useAI ? 'ai-illustration' : 'original';
    image.src = useAI ? image.getAttribute('data-ai-src') : image.getAttribute('data-original-src');
    image.alt = useAI ? image.getAttribute('data-ai-alt') : image.getAttribute('data-original-alt');
    var label = thumbnail.querySelector('[data-ai-label]');
    if (label) label.hidden = !useAI;
    if (button) {
      button.setAttribute('aria-pressed', useAI ? 'true' : 'false');
      button.textContent = useAI ? 'Show original photo' : 'Show AI illustration';
    }
  }

  function setCompanyVariant(figure, variant, button) {
    var image = figure && figure.querySelector('img[data-ai-src]');
    if (!image) return;
    var useAI = variant === 'ai-illustration' && !!image.getAttribute('data-ai-src');
    figure.dataset.variant = useAI ? 'ai-illustration' : 'original';
    image.src = useAI ? image.getAttribute('data-ai-src') : image.getAttribute('data-original-src');
    image.alt = useAI ? image.getAttribute('data-ai-alt') : image.getAttribute('data-original-alt');
    var label = figure.querySelector('[data-ai-label]');
    if (label) label.hidden = !useAI;
    var caption = figure.querySelector('[data-company-caption]');
    if (caption) caption.textContent = useAI ? caption.getAttribute('data-ai-caption') : caption.getAttribute('data-original-caption');
    if (button) {
      button.setAttribute('aria-pressed', useAI ? 'true' : 'false');
      button.textContent = useAI ? 'Show original photo' : 'Show AI illustration';
    }
  }

  document.addEventListener('click', function (e) {
    var companyVariantBtn = e.target.closest('[data-company-variant]');
    if (companyVariantBtn) {
      e.preventDefault();
      var companyFigure = companyVariantBtn.closest('[data-company-image]');
      setCompanyVariant(companyFigure, companyFigure && companyFigure.dataset.variant === 'ai-illustration' ? 'original' : 'ai-illustration', companyVariantBtn);
      return;
    }
    var thumbnailBtn = e.target.closest('[data-thumb-variant]');
    if (thumbnailBtn) {
      e.preventDefault();
      var thumbnail = thumbnailBtn.closest('[data-thumbnail]');
      if (!thumbnail) {
        var thumbOwner = thumbnailBtn.closest('[data-item]');
        thumbnail = thumbOwner && thumbOwner.querySelector('[data-thumbnail]');
      }
      setThumbnailVariant(thumbnail, thumbnail && thumbnail.dataset.variant === 'ai-illustration' ? 'original' : 'ai-illustration', thumbnailBtn);
      return;
    }
    var variantBtn = e.target.closest('[data-card-variant]');
    if (variantBtn) {
      e.preventDefault();
      var card = variantBtn.closest('[data-item]');
      var media = card && card.querySelector('[data-open]');
      setCardVariant(card, media && media.dataset.variant === 'ai-illustration' ? 'original' : 'ai-illustration');
      return;
    }
    var btn = e.target.closest('[data-add]');
    if (btn) {
      e.preventDefault();
      var itemCard = btn.closest('[data-item]');
      var itemMedia = itemCard && itemCard.querySelector('[data-open]');
      handleAdd(btn.getAttribute('data-add'), itemMedia ? itemMedia.dataset.variant : undefined);
    }
  });

  E.on(function () { updateCounts(); syncAddButtons(); });
  updateCounts();
  syncAddButtons();

  /* ---------------- lightbox ---------------- */
  var lb = document.getElementById('lightbox');
  if (lb && S) {
    var img = document.getElementById('lb-img');
    var stage = document.getElementById('lb-stage');
    var zoomBtn = lb.querySelector('[data-lb-zoom]');
    var variantBtn = lb.querySelector('[data-lb-variant]');
    var prevBtn = lb.querySelector('[data-lb-prev]');
    var nextBtn = lb.querySelector('[data-lb-next]');
    var byId = {};
    S.items.forEach(function (it) { byId[it.id] = it; });
    var seq = [];
    var idx = 0;
    var opener = null;
    var actual = false;

    function visibleOpeners() {
      return Array.prototype.filter.call(document.querySelectorAll('[data-open]'), function (el) {
        return el.offsetParent !== null || el.getClientRects().length > 0;
      });
    }
    function fit(it, useAI) {
      var availW = Math.max(120, stage.clientWidth - 2 * 56 - 20);
      var availH = Math.max(140, Math.min(window.innerHeight * 0.5, 520));
      var w = useAI ? it.aiW : it.w;
      var h = useAI ? it.aiH : it.h;
      var s;
      if (actual) { s = 1; } else { s = Math.min(3, availW / w, availH / h); }
      img.style.width = Math.round(w * s) + 'px';
      img.style.height = Math.round(h * s) + 'px';
      stage.classList.toggle('is-actual', actual);
      return s;
    }
    function render() {
      var id = seq[idx];
      var it = byId[id];
      if (!it) return;
      lb.dataset.current = id;
      var a = S.albums[it.album];
      var useAI = !!it.ai && lb.dataset.variant === 'ai-illustration';
      lb.dataset.variant = useAI ? 'ai-illustration' : 'original';
      document.getElementById('lb-title').textContent = it.title;
      img.alt = useAI ? it.aiAlt : it.alt;
      img.src = useAI ? it.ai : it.img;
      var s = fit(it, useAI);
      var aiLabel = document.getElementById('lb-ai-label');
      if (aiLabel) aiLabel.hidden = !useAI;
      variantBtn.hidden = !(it.ai && S.site.imageMode === 'both');
      variantBtn.setAttribute('aria-pressed', useAI ? 'true' : 'false');
      variantBtn.textContent = useAI ? 'Show original photo' : 'Show AI illustration';
      var sci = it.named ? it.named.name : (a.sci || '');
      document.getElementById('lb-sci').textContent = sci ? sci : '';
      var care = it.named ? { ph: it.named.ph, temp: it.named.temp } : a.care;
      document.getElementById('lb-care').textContent = care ? ('pH ' + care.ph + ' · ' + care.temp + ' (as published on the original website)') : '';
      var src = document.getElementById('lb-src');
      src.textContent = '';
      src.appendChild(document.createTextNode('Album: ' + a.title + ' · source file ' + it.file + (a.pages > 1 ? ' · original page ' + it.pg : '') + ' · '));
      var l1 = document.createElement('a'); l1.href = it.src; l1.target = '_blank'; l1.rel = 'noopener'; l1.textContent = 'original page ↗';
      var l2 = document.createElement('a'); l2.href = it.orig; l2.target = '_blank'; l2.rel = 'noopener'; l2.textContent = 'original image ↗';
      src.appendChild(l1); src.appendChild(document.createTextNode(' · ')); src.appendChild(l2);
      document.getElementById('lb-res').textContent = (useAI ? 'AI illustration: ' + it.aiW + ' × ' + it.aiH + ' px' : 'Original photo: ' + it.w + ' × ' + it.h + ' px') + (actual ? '.' : ' (shown at ' + (Math.round(s * 10) / 10) + '×).');
      document.getElementById('lb-count').textContent = 'Photo ' + (idx + 1) + ' of ' + seq.length;
      prevBtn.disabled = idx === 0;
      nextBtn.disabled = idx === seq.length - 1;
      syncAddButtons();
    }
    function openAt(el) {
      opener = el;
      var els = visibleOpeners();
      var group = el.closest('[data-gallery], #results');
      if (group) els = els.filter(function (x) { return group.contains(x); });
      seq = els.map(function (x) { return x.getAttribute('data-open'); });
      idx = Math.max(0, seq.indexOf(el.getAttribute('data-open')));
      lb.dataset.variant = el.dataset.variant || (S.site.imageMode === 'ai-illustration' ? 'ai-illustration' : 'original');
      actual = false;
      zoomBtn.setAttribute('aria-pressed', 'false');
      zoomBtn.textContent = 'Actual size (1×)';
      if (!lb.open) lb.showModal();
      document.documentElement.style.overflow = 'hidden';
      render();
      lb.querySelector('[data-lb-close]').focus();
    }
    function step(d) {
      var n = idx + d;
      if (n < 0 || n >= seq.length) return;
      idx = n;
      var nextOpener = visibleOpeners().filter(function (x) { return x.getAttribute('data-open') === seq[idx]; })[0];
      var nextItem = byId[seq[idx]];
      lb.dataset.variant = nextOpener ? nextOpener.dataset.variant : (S.site.imageMode === 'ai-illustration' && nextItem && nextItem.ai ? 'ai-illustration' : 'original');
      render();
    }
    document.addEventListener('click', function (e) {
      var o = e.target.closest('[data-open]');
      if (o) { e.preventDefault(); openAt(o); }
    });
    prevBtn.addEventListener('click', function () { step(-1); });
    nextBtn.addEventListener('click', function () { step(1); });
    lb.querySelector('[data-lb-close]').addEventListener('click', function () { lb.close(); });
    lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
    });
    lb.addEventListener('close', function () {
      document.documentElement.style.overflow = '';
      var cur = lb.dataset.current;
      delete lb.dataset.current;
      // return focus to the thumbnail of the photo that was last shown (falls back to the original trigger)
      var target = null;
      if (cur) target = Array.prototype.filter.call(document.querySelectorAll('[data-open]'), function (el) { return el.getAttribute('data-open') === cur; })[0] || null;
      target = target || opener;
      if (target && document.contains(target)) target.focus();
    });
    zoomBtn.addEventListener('click', function () {
      actual = !actual;
      zoomBtn.setAttribute('aria-pressed', actual ? 'true' : 'false');
      zoomBtn.textContent = actual ? 'Fit to window' : 'Actual size (1×)';
      render();
    });
    variantBtn.addEventListener('click', function () {
      var it = byId[seq[idx]];
      if (!it || !it.ai) return;
      lb.dataset.variant = lb.dataset.variant === 'ai-illustration' ? 'original' : 'ai-illustration';
      var card = Array.prototype.filter.call(document.querySelectorAll('.card[data-item]'), function (el) { return el.getAttribute('data-item') === it.id; })[0];
      setCardVariant(card, lb.dataset.variant);
      render();
    });
    lb.querySelector('[data-lb-add]').addEventListener('click', function () {
      if (lb.dataset.current) handleAdd(lb.dataset.current, lb.dataset.variant);
    });
    window.addEventListener('resize', function () { if (lb.open && byId[seq[idx]]) render(); });
  }

  window.SanyoUI = { toast: toast, syncAddButtons: syncAddButtons, updateCounts: updateCounts };
})();
