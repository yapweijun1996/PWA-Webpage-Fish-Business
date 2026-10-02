/* Enquiry list store.
 * - Item list: localStorage (survives page changes and browser restarts on this device only).
 * - Contact details: sessionStorage (this tab only; cleared when the tab closes). Never uploaded anywhere.
 * If browser storage is blocked, data falls back to memory for the current page and a flag is exposed.
 */
(function () {
  'use strict';
  var ITEMS_KEY = 'sanyo.enquiry.items.v1';
  var DETAILS_KEY = 'sanyo.enquiry.details.v1';
  var MAX_QTY = 99999;
  var memory = { items: [], details: {} };
  var health = { local: true, session: true };
  var listeners = [];

  function readJSON(kind, key) {
    try {
      var raw = window[kind].getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      health[kind === 'localStorage' ? 'local' : 'session'] = false;
      return null;
    }
  }
  function writeJSON(kind, key, value) {
    try {
      window[kind].setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      health[kind === 'localStorage' ? 'local' : 'session'] = false;
      return false;
    }
  }

  function validQty(v) {
    if (typeof v === 'string') {
      if (!/^\d+$/.test(v.trim())) return false;
      v = parseInt(v, 10);
    }
    return Number.isInteger(v) && v >= 1 && v <= MAX_QTY;
  }

  function clean(x) {
    if (!x || typeof x !== 'object' || typeof x.id !== 'string' || typeof x.label !== 'string' || !x.label.trim()) return null;
    var type = x.type === 'category' || x.type === 'custom' ? x.type : 'photo';
    return {
      id: x.id.slice(0, 80),
      type: type,
      label: x.label.slice(0, 160),
      sub: typeof x.sub === 'string' ? x.sub.slice(0, 240) : '',
      section: typeof x.section === 'string' ? x.section.slice(0, 40) : '',
      src: typeof x.src === 'string' && /^https?:\/\//.test(x.src) ? x.src.slice(0, 300) : '',
      img: typeof x.img === 'string' && /^assets\/img\//.test(x.img) ? x.img.slice(0, 200) : '',
      imgAlt: typeof x.imgAlt === 'string' ? x.imgAlt.slice(0, 300) : '',
      photoVariant: x.photoVariant === 'ai-illustration' ? 'ai-illustration' : 'original',
      file: typeof x.file === 'string' ? x.file.slice(0, 80) : '',
      qty: validQty(x.qty) ? parseInt(x.qty, 10) : 1,
      note: typeof x.note === 'string' ? x.note.slice(0, 300) : '',
      supply: typeof x.supply === 'string' ? x.supply.slice(0, 60) : '',
      added: typeof x.added === 'number' ? x.added : Date.now()
    };
  }

  function emit(evt) {
    listeners.slice().forEach(function (fn) { try { fn(evt); } catch (e) { /* ignore listener errors */ } });
  }

  function getItems() {
    var arr = readJSON('localStorage', ITEMS_KEY);
    if (!Array.isArray(arr)) arr = health.local ? [] : memory.items;
    var seen = {};
    return arr.map(clean).filter(function (x) {
      if (!x || seen[x.id]) return false;
      seen[x.id] = true;
      return true;
    });
  }
  function saveItems(arr, evt) {
    memory.items = arr;
    writeJSON('localStorage', ITEMS_KEY, arr);
    emit(evt || { type: 'change' });
  }

  function has(id) { return getItems().some(function (x) { return x.id === id; }); }

  /* Add one item. Returns {status:'added'|'duplicate'|'invalid', item}. Never creates a second row for the same id. */
  function add(item) {
    var c = clean(item);
    if (!c) return { status: 'invalid' };
    var items = getItems();
    var dup = items.filter(function (x) {
      return x.id === c.id || (c.type === 'custom' && x.type === 'custom' && x.label.trim().toLowerCase() === c.label.trim().toLowerCase());
    })[0];
    if (dup) return { status: 'duplicate', item: dup };
    items.push(c);
    saveItems(items, { type: 'add', id: c.id });
    return { status: 'added', item: c };
  }
  function remove(id) {
    var items = getItems();
    var gone = items.filter(function (x) { return x.id === id; })[0];
    if (!gone) return null;
    saveItems(items.filter(function (x) { return x.id !== id; }), { type: 'remove', id: id });
    return gone;
  }
  function update(id, patch) {
    var items = getItems();
    var changed = false;
    items.forEach(function (x) {
      if (x.id !== id) return;
      if ('qty' in patch && validQty(patch.qty)) { x.qty = parseInt(patch.qty, 10); changed = true; }
      if ('note' in patch) { x.note = String(patch.note).slice(0, 300); changed = true; }
      if ('supply' in patch) { x.supply = String(patch.supply).slice(0, 60); changed = true; }
    });
    if (changed) saveItems(items, { type: 'update', id: id });
    return changed;
  }
  function clear() { saveItems([], { type: 'clear' }); }
  function count() { return getItems().length; }

  function getDetails() {
    var d = readJSON('sessionStorage', DETAILS_KEY);
    return d && typeof d === 'object' ? d : (health.session ? {} : memory.details);
  }
  function setDetails(d) {
    memory.details = d;
    writeJSON('sessionStorage', DETAILS_KEY, d);
  }
  function clearDetails() {
    memory.details = {};
    try { window.sessionStorage.removeItem(DETAILS_KEY); } catch (e) { health.session = false; }
  }

  /* Build a stored item from the generated catalogue data (window.SANYO). */
  function fromCatalogue(id, variant) {
    var S = window.SANYO;
    if (!S) return null;
    var i, it;
    for (i = 0; i < S.items.length; i++) {
      if (S.items[i].id === id) {
        it = S.items[i];
        var a = S.albums[it.album];
        var useAI = !!it.ai && (variant === 'ai-illustration' || (!variant && S.site.imageMode === 'ai-illustration'));
        var imageLabel = 'AI illustration';
        var sourceText = (it.named ? 'New Fishes page entry' : a.title + ' gallery') + ' · source file ' + it.file;
        if (useAI) sourceText = imageLabel + ' · ' + sourceText;
        return {
          id: it.id, type: 'photo', label: it.named ? it.named.name : it.title,
          sub: sourceText, section: it.sec, src: it.src, img: useAI ? it.ai : it.img,
          imgAlt: useAI ? it.aiAlt : it.alt, photoVariant: useAI ? 'ai-illustration' : 'original',
          file: it.file, qty: 1, note: '', supply: ''
        };
      }
    }
    for (i = 0; i < S.categories.length; i++) {
      if (S.categories[i].id === id) {
        var c = S.categories[i];
        return {
          id: c.id, type: 'category', label: c.title,
          sub: c.photos ? 'Whole category (any variety)' : 'Category listed on the original site (no photographs there)',
          section: c.sec, src: c.src, img: '', file: '', qty: 1, note: '', supply: ''
        };
      }
    }
    return null;
  }
  function addFromCatalogue(id, variant) {
    var item = fromCatalogue(id, variant);
    return item ? add(item) : { status: 'invalid' };
  }

  window.addEventListener('storage', function (e) {
    if (e.key === ITEMS_KEY) emit({ type: 'external' });
  });

  window.SanyoEnquiry = {
    MAX_QTY: MAX_QTY, validQty: validQty, getItems: getItems, has: has, add: add, remove: remove, update: update,
    clear: clear, count: count, getDetails: getDetails, setDetails: setDetails, clearDetails: clearDetails,
    addFromCatalogue: addFromCatalogue, fromCatalogue: fromCatalogue,
    on: function (fn) { listeners.push(fn); },
    storageHealthy: function () { return health.local && health.session; },
    health: health
  };
})();
