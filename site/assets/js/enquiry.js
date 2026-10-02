/* Enquiry workflow (runs on enquiry.html): items -> details -> review & send.
 * HONESTY RULE: this site has no backend or email service. It prepares an email draft (mailto:) and downloadable /
 * copyable text. It never reports an enquiry as "sent" and never invents a reference number.
 */
(function () {
  'use strict';
  var E = window.SanyoEnquiry;
  var S = window.SANYO;
  var app = document.getElementById('enquiry-app');
  if (!E || !S || !app) return;

  var STEPS = ['items', 'details', 'review'];
  var MAILTO_LIMIT = 1800; // conservative length for a mailto: URL across browsers / mail clients
  var $ = function (id) { return document.getElementById(id); };
  var sections = {};
  STEPS.forEach(function (s) { sections[s] = $('step-' + s); });
  var summary = $('error-summary');
  var list = $('items-list');
  var emptyEl = $('items-empty');
  var removed = null;

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function isPlantItem(it) { return it.section === 'plants' || it.section === 'plants-driftwood'; }

  /* ------------------------------------------------------------ error summary */
  function showErrors(errors, heading) {
    if (!errors.length) { summary.hidden = true; summary.innerHTML = ''; return; }
    summary.innerHTML = '<h2>' + esc(heading || 'Please fix the following') + '</h2><ul>' +
      errors.map(function (e) { return '<li><a href="#' + esc(e.field) + '" data-focus="' + esc(e.field) + '">' + esc(e.message) + '</a></li>'; }).join('') + '</ul>';
    summary.hidden = false;
    summary.focus();
  }
  summary.addEventListener('click', function (e) {
    var a = e.target.closest('[data-focus]');
    if (a) {
      e.preventDefault();
      var el = $(a.getAttribute('data-focus'));
      if (el) el.focus();
    }
  });
  function clearErrors() { showErrors([]); }

  /* ------------------------------------------------------------ items step */
  function renderItems() {
    var items = E.getItems();
    emptyEl.hidden = items.length > 0;
    $('custom-form').hidden = false;
    list.innerHTML = items.map(function (it, n) {
      var thumb = it.img
        ? '<div class="ei-thumb"><img src="' + esc(it.img) + '" alt="' + esc(it.imgAlt || '') + '" width="84" height="56"></div>'
        : '<div class="ei-thumb is-cat" aria-hidden="true">' + (it.type === 'custom' ? 'Custom' : 'Category') + '</div>';
      var aiLabel = it.photoVariant === 'ai-illustration'
        ? '<p class="ai-label ai-label-enquiry">AI illustration · not evidence of stock</p>' : '';
      var plant = isPlantItem(it);
      var supply = '';
      if (plant) {
        supply = '<div class="field"><label for="sup-' + n + '">Supply form</label><select id="sup-' + n + '" data-supply="' + esc(it.id) + '">' +
          '<option value="">Not specified</option>' + S.supplyForms.map(function (f) {
            return '<option value="' + esc(f) + '"' + (it.supply === f ? ' selected' : '') + '>' + esc(f) + '</option>';
          }).join('') + '</select></div>';
      }
      var srcLink = it.src ? ' · <a href="' + esc(it.src) + '" target="_blank" rel="noopener">original page<span class="visually-hidden"> (opens in a new tab)</span> ↗</a>' : '';
      return '<li class="enquiry-item" data-id="' + esc(it.id) + '">' + thumb +
        '<div class="ei-main"><p class="ei-title">' + esc(it.label) + '</p><p class="ei-sub">' + esc(it.sub) + srcLink + '</p>' + aiLabel + '</div>' +
        '<div class="ei-controls' + (plant ? ' has-supply' : '') + '">' +
        '<div class="field"><label for="qty-' + n + '">Quantity</label><input id="qty-' + n + '" type="number" inputmode="numeric" min="1" max="' + E.MAX_QTY + '" step="1" value="' + it.qty + '" data-qty="' + esc(it.id) + '" aria-describedby="qe-' + n + '"><p class="field-error" id="qe-' + n + '" hidden></p></div>' +
        supply +
        '<div class="field"><label for="note-' + n + '">Variety / size notes</label><input id="note-' + n + '" type="text" maxlength="300" value="' + esc(it.note) + '" data-note="' + esc(it.id) + '" autocomplete="off"></div>' +
        '<button type="button" class="btn btn-ghost-dark ei-remove" data-remove="' + esc(it.id) + '" aria-label="Remove ' + esc(it.label) + ' from the list">Remove</button>' +
        '</div></li>';
    }).join('');
  }

  function qtyProblem(raw) {
    var v = String(raw).trim();
    if (!v) return 'Enter a quantity.';
    if (!/^\d+$/.test(v)) return 'Quantity must be a whole number (digits only).';
    var n = parseInt(v, 10);
    if (n < 1) return 'Quantity must be at least 1.';
    if (n > E.MAX_QTY) return 'Quantity can be at most ' + E.MAX_QTY + '.';
    return '';
  }
  function markQty(input, msg) {
    var err = input.parentNode.querySelector('.field-error');
    if (msg) { input.setAttribute('aria-invalid', 'true'); err.textContent = msg; err.hidden = false; }
    else { input.removeAttribute('aria-invalid'); err.textContent = ''; err.hidden = true; }
  }

  list.addEventListener('input', function (e) {
    var t = e.target;
    if (t.matches('[data-qty]')) {
      var msg = qtyProblem(t.value);
      markQty(t, msg);
      if (!msg) E.update(t.getAttribute('data-qty'), { qty: t.value });
    } else if (t.matches('[data-note]')) {
      E.update(t.getAttribute('data-note'), { note: t.value });
    }
  });
  list.addEventListener('change', function (e) {
    var t = e.target;
    if (t.matches('[data-supply]')) E.update(t.getAttribute('data-supply'), { supply: t.value });
  });
  list.addEventListener('click', function (e) {
    var b = e.target.closest('[data-remove]');
    if (!b) return;
    var gone = E.remove(b.getAttribute('data-remove'));
    if (gone) {
      removed = gone;
      renderItems();
      window.SanyoUI.toast('Removed “' + gone.label + '”.', {
        action: { label: 'Undo', run: function () { if (removed) { E.add(removed); removed = null; renderItems(); } } }
      });
      ($('items-list').querySelector('input') || $('custom-name')).focus();
    }
  });

  function validateItems() {
    var errors = [];
    var items = E.getItems();
    if (!items.length) {
      errors.push({ field: 'custom-name', message: 'Add at least one item to your enquiry list.' });
      return errors;
    }
    list.querySelectorAll('[data-qty]').forEach(function (input) {
      var msg = qtyProblem(input.value);
      markQty(input, msg);
      if (msg) {
        var title = input.closest('.enquiry-item').querySelector('.ei-title').textContent;
        errors.push({ field: input.id, message: title + ': ' + msg });
      }
    });
    return errors;
  }

  $('custom-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var name = $('custom-name');
    var qty = $('custom-qty');
    var note = $('custom-note');
    var err = $('custom-error');
    var problems = [];
    if (!name.value.trim()) problems.push('Enter the species or product name.');
    var qp = qtyProblem(qty.value);
    if (qp) problems.push(qp);
    if (problems.length) {
      err.textContent = problems.join(' ');
      err.hidden = false;
      name.setAttribute('aria-invalid', name.value.trim() ? 'false' : 'true');
      (name.value.trim() ? qty : name).focus();
      return;
    }
    err.hidden = true;
    name.removeAttribute('aria-invalid');
    var r = E.add({
      id: 'custom-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), type: 'custom',
      label: name.value.trim(), sub: 'Custom item entered by you', section: '', qty: parseInt(qty.value, 10), note: note.value.trim()
    });
    if (r.status === 'duplicate') {
      err.textContent = '“' + r.item.label + '” is already in your list. Change its quantity above instead.';
      err.hidden = false;
      name.focus();
      return;
    }
    $('custom-form').reset();
    qty.value = '1';
    renderItems();
    window.SanyoUI.toast('Added “' + r.item.label + '”.');
    name.focus();
  });

  $('to-details').addEventListener('click', function () {
    var errors = validateItems();
    if (errors.length) { showErrors(errors); return; }
    clearErrors();
    goto('details');
  });
  $('clear-list').addEventListener('click', function () {
    if (!E.count()) return;
    if (window.confirm('Remove all items from your enquiry list?')) { E.clear(); renderItems(); window.SanyoUI.toast('Enquiry list cleared.'); }
  });

  /* ------------------------------------------------------------ details step */
  var FIELDS = ['name', 'designation', 'company', 'email', 'phone', 'destination', 'address', 'requirements', 'message'];
  var form = $('details-form');
  function fieldEl(n) { return $('f-' + n); }
  function readDetails() {
    var d = {};
    FIELDS.forEach(function (n) { d[n] = fieldEl(n).value.trim(); });
    return d;
  }
  function loadDetails() {
    var d = E.getDetails();
    FIELDS.forEach(function (n) { if (typeof d[n] === 'string') fieldEl(n).value = d[n]; });
  }
  form.addEventListener('input', function () { E.setDetails(readDetails()); });

  function validateDetails() {
    var d = readDetails();
    var errors = [];
    function bad(n, msg) { errors.push({ field: 'f-' + n, message: msg }); }
    if (!d.name) bad('name', 'Enter your name.');
    if (!d.company) bad('company', 'Enter your company name.');
    if (!d.email) bad('email', 'Enter an email address.');
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) bad('email', 'Enter a valid email address, for example name@company.com.');
    if (d.phone && !(/^[+()\d][\d\s().+-]{5,24}$/.test(d.phone) && d.phone.replace(/\D/g, '').length >= 6 && d.phone.replace(/\D/g, '').length <= 15)) {
      bad('phone', 'Phone can only contain digits, spaces and + ( ) . - (6 to 15 digits).');
    }
    if (!d.destination) bad('destination', 'Enter the destination country or city.');
    FIELDS.forEach(function (n) {
      var el = fieldEl(n);
      var err = $('e-' + n);
      var hit = errors.filter(function (x) { return x.field === 'f-' + n; })[0];
      if (hit) { el.setAttribute('aria-invalid', 'true'); if (err) { err.textContent = hit.message; err.hidden = false; } }
      else { el.removeAttribute('aria-invalid'); if (err) { err.textContent = ''; err.hidden = true; } }
    });
    return errors;
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var errors = validateDetails();
    if (errors.length) { showErrors(errors); $(errors[0].field).focus(); summary.focus(); return; }
    clearErrors();
    E.setDetails(readDetails());
    goto('review');
  });
  $('back-items').addEventListener('click', function () { goto('items'); });
  $('clear-details').addEventListener('click', function () {
    form.reset();
    E.clearDetails();
    FIELDS.forEach(function (n) { fieldEl(n).removeAttribute('aria-invalid'); var er = $('e-' + n); if (er) { er.hidden = true; er.textContent = ''; } });
    window.SanyoUI.toast('Your details were cleared from this browser tab.');
    fieldEl('name').focus();
  });

  /* ------------------------------------------------------------ review step: text builders */
  function lineFor(it, n) {
    var parts = [n + '. ' + it.label + ' — Qty: ' + it.qty];
    if (it.photoVariant === 'ai-illustration') parts.push('AI illustration, not evidence of stock');
    if (it.supply) parts.push('Supply form: ' + it.supply);
    if (it.note) parts.push('Notes: ' + it.note);
    return parts.join(' — ');
  }
  function sourceLine(it) { return '   Source: ' + it.sub + (it.src ? ' — ' + it.src : ''); }
  function buildText(opts) {
    opts = opts || {};
    var items = E.getItems();
    var d = E.getDetails();
    var when = new Date().toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' });
    var head = [
      'ENQUIRY FOR ' + S.site.name.toUpperCase(),
      'Prepared ' + when + ' on the sender’s device. This is a draft: it is not sent until the sender emails it.',
      '',
      'CONTACT DETAILS',
      'Name: ' + (d.name || ''),
      'Designation: ' + (d.designation || ''),
      'Company: ' + (d.company || ''),
      'Email: ' + (d.email || ''),
      'Phone: ' + (d.phone || ''),
      'Company address: ' + (d.address || ''),
      '',
      'DESTINATION',
      'Country / city: ' + (d.destination || ''),
      'Requirements: ' + (d.requirements || ''),
      '',
      'MESSAGE',
      d.message || '(none)',
      '',
      'ITEMS REQUESTED (' + items.length + ')'
    ];
    var body = [];
    var max = opts.maxItems == null ? items.length : opts.maxItems;
    items.slice(0, max).forEach(function (it, i) {
      body.push(lineFor(it, i + 1));
      if (!opts.compact) body.push(sourceLine(it));
    });
    if (max < items.length) body.push('[' + (items.length - max) + ' more item(s) not shown: this email link was too long. Please paste the copied text or attach the downloaded file.]');
    return head.concat(body).join('\r\n');
  }
  function csvCell(v) { return '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"'; }
  function buildCsv() {
    var d = E.getDetails();
    var rows = [['line', 'item', 'type', 'source_gallery_or_category', 'quantity', 'supply_form', 'notes', 'source_page_url',
      'contact_name', 'company', 'email', 'phone', 'destination']];
    E.getItems().forEach(function (it, i) {
      rows.push([i + 1, it.label, it.type, it.sub, it.qty, it.supply, it.note, it.src,
        i === 0 ? d.name : '', i === 0 ? d.company : '', i === 0 ? d.email : '', i === 0 ? d.phone : '', i === 0 ? d.destination : '']);
    });
    return '﻿' + rows.map(function (r) { return r.map(csvCell).join(','); }).join('\r\n');
  }
  function buildMailto() {
    var d = E.getDetails();
    var items = E.getItems();
    var subject = 'Enquiry' + (d.company ? ' from ' + d.company : '') + ' — ' + items.length + (items.length === 1 ? ' item' : ' items');
    var base = 'mailto:' + S.site.emailSales + '?subject=' + encodeURIComponent(subject) + '&body=';
    var truncated = false;
    var n = items.length;
    var href = base + encodeURIComponent(buildText({ compact: false, maxItems: n }));
    if (href.length > MAILTO_LIMIT) {
      // try compact lines first, then fewer items
      while (n > 0) {
        href = base + encodeURIComponent(buildText({ compact: true, maxItems: n }));
        if (href.length <= MAILTO_LIMIT) break;
        n--;
      }
      truncated = n < items.length;
      if (n === 0) href = base + encodeURIComponent(buildText({ compact: true, maxItems: 0 }));
    }
    return { href: href, truncated: truncated, shown: n, total: items.length };
  }

  function download(name, mime, text) {
    var blob = new Blob([text], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function stamp() {
    var d = new Date();
    function p(n) { return String(n).padStart(2, '0'); }
    return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + '-' + p(d.getHours()) + p(d.getMinutes());
  }

  function completion(kind) {
    var c = $('completion');
    var email = S.site.emailSales;
    var msgs = {
      mailto: ['Email draft prepared — not sent', 'Your email program should now show a draft addressed to ' + email + '. <strong>Nothing has been sent</strong> until you press Send there, and this website cannot tell whether you did. If no draft opened, use “Copy text” or a download and email it to ' + email + '.'],
      copy: ['Text copied — not sent', 'Paste it into an email to ' + email + ' and send it yourself. <strong>Nothing has been sent.</strong>'],
      txt: ['File downloaded — not sent', 'Attach the .txt file to an email to ' + email + ' and send it yourself. <strong>Nothing has been sent.</strong>'],
      csv: ['File downloaded — not sent', 'Attach the .csv file to an email to ' + email + ' and send it yourself. <strong>Nothing has been sent.</strong>'],
      print: ['Print dialog opened — not sent', 'Printing or saving as PDF does not send anything. Email the file to ' + email + ' yourself.'],
      fail: ['Could not copy automatically', 'Your browser blocked clipboard access. Use a download instead, or select the text from the downloaded file.']
    };
    var m = msgs[kind];
    c.className = 'completion' + (kind === 'fail' ? ' is-warn' : '');
    c.innerHTML = '<h4>' + m[0] + '</h4><p>' + m[1] + '</p><p class="small">Your item list stays saved on this device until you clear it.</p>';
    c.hidden = false;
  }

  function renderReview() {
    var items = E.getItems();
    var d = E.getDetails();
    $('review-items').innerHTML = items.map(function (it) {
      return '<li><strong>' + esc(it.label) + '</strong> — qty ' + it.qty +
        (it.supply ? ' · ' + esc(it.supply) : '') + (it.note ? '<br><span class="muted">Notes: ' + esc(it.note) + '</span>' : '') +
        '<br><span class="muted small">' + esc(it.sub) + '</span></li>';
    }).join('');
    var rows = [['Name', d.name], ['Designation', d.designation], ['Company', d.company], ['Email', d.email], ['Phone', d.phone],
      ['Company address', d.address], ['Destination', d.destination], ['Requirements', d.requirements], ['Message', d.message]];
    $('review-details').innerHTML = rows.map(function (r) {
      return '<div><dt>' + r[0] + '</dt><dd>' + (r[1] ? esc(r[1]) : '<span class="muted">—</span>') + '</dd></div>';
    }).join('');
    var m = buildMailto();
    var a = $('send-mailto');
    a.href = m.href;
    a.dataset.truncated = m.truncated ? 'true' : 'false';
    $('mailto-hint').textContent = m.truncated
      ? 'Your list is long, so the email draft shows ' + m.shown + ' of ' + m.total + ' items. Clicking “Open email draft” also copies the full text to your clipboard so you can paste it in.'
      : 'The draft opens in your own email program, addressed to ' + S.site.emailSales + '.';
    $('completion').hidden = true;
  }

  $('send-mailto').addEventListener('click', function () {
    var m = buildMailto();
    if (m.truncated && navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(buildText()).catch(function () { /* user can still use Copy text */ });
    }
    completion('mailto');
  });
  $('copy-text').addEventListener('click', function () {
    var text = buildText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { completion('copy'); }, function () { completion('fail'); });
    } else { completion('fail'); }
  });
  $('dl-txt').addEventListener('click', function () { download('sanyo-enquiry-' + stamp() + '.txt', 'text/plain;charset=utf-8', buildText()); completion('txt'); });
  $('dl-csv').addEventListener('click', function () { download('sanyo-enquiry-' + stamp() + '.csv', 'text/csv;charset=utf-8', buildCsv()); completion('csv'); });
  $('print-enq').addEventListener('click', function () { completion('print'); window.print(); });
  $('edit-items').addEventListener('click', function () { goto('items'); });
  $('edit-details').addEventListener('click', function () { goto('details'); });
  $('back-details').addEventListener('click', function () { goto('details'); });
  $('start-new').addEventListener('click', function () {
    if (window.confirm('Clear your item list and your details and start a new enquiry?')) {
      E.clear(); E.clearDetails(); form.reset(); renderItems(); goto('items'); window.SanyoUI.toast('Started a new enquiry.');
    }
  });

  /* ------------------------------------------------------------ step navigation */
  var current = null;
  function goto(step) { if (location.hash !== '#' + step) location.hash = step; else show(step, true); }
  function show(step, force) {
    // guards: later steps need valid earlier steps
    if (step !== 'items') {
      var ie = validateItems();
      if (ie.length) { step = 'items'; if (location.hash !== '#items') history.replaceState(null, '', '#items'); renderItems(); showErrors(ie, 'Check your items first'); }
    }
    if (step === 'review') {
      var de = validateDetails();
      if (de.length) { step = 'details'; history.replaceState(null, '', '#details'); showErrors(de, 'Check your details first'); }
    }
    if (current === step && !force) return;
    var moved = current !== null && current !== step;
    current = step;
    STEPS.forEach(function (s) { sections[s].hidden = s !== step; });
    document.querySelectorAll('[data-step-ind]').forEach(function (li) {
      if (li.getAttribute('data-step-ind') === step) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
    });
    if (step === 'items') renderItems();
    if (step === 'review') renderReview();
    if (step !== 'items' && step !== 'details') { /* keep any error summary hidden on success */ }
    if (moved || force) {
      var h = sections[step].querySelector('h2');
      if (h) { h.focus(); }
      app.scrollIntoView({ block: 'start' });
    }
  }
  function fromHash() {
    var h = (location.hash || '').replace('#', '');
    var step = STEPS.indexOf(h) !== -1 ? h : 'items';
    var before = summary.hidden;
    if (step === 'items' || !summary.hidden === false) { /* no-op */ }
    show(step, false);
    return before;
  }
  window.addEventListener('hashchange', function () {
    clearErrorsOnNavigation();
    fromHash();
  });
  function clearErrorsOnNavigation() { /* guards inside show() re-add errors when needed */ summary.hidden = true; summary.innerHTML = ''; }

  E.on(function (evt) {
    if (evt && (evt.type === 'external')) { if (current === 'items') renderItems(); if (current === 'review') renderReview(); }
  });

  loadDetails();
  var startHash = (location.hash || '').replace('#', '');
  renderItems();
  show(STEPS.indexOf(startHash) !== -1 ? startHash : 'items', false);
  if (!E.storageHealthy()) {
    window.SanyoUI.toast('Your browser is blocking storage, so your list is kept only while this page stays open.', { warn: true, ttl: 9000 });
  }
})();
