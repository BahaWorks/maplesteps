(function () {
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function del(k) { try { localStorage.removeItem(k); } catch (e) {} }

  // Remember the reader's language choice.
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () { set('ms-lang', a.getAttribute('data-lang')); });
  });
  var current = document.documentElement.getAttribute('lang');
  var codeMap = { 'en-CA': 'en', 'fr-CA': 'fr', 'ar': 'ar', 'zh-Hans': 'zh', 'hi': 'hi', 'fa': 'fa' };
  if (codeMap[current] && !document.body.classList.contains('root-page')) set('ms-lang', codeMap[current]);

  // On the language picker, highlight the language used last time.
  if (document.body.classList.contains('root-page')) {
    var saved = get('ms-lang');
    if (saved) {
      var tile = document.querySelector('.lang-tile[data-lang="' + saved + '"]');
      if (tile) tile.classList.add('remembered');
    }
  }

  // Close the language menu when clicking elsewhere.
  var det = document.querySelector('details.lang');
  if (det) document.addEventListener('click', function (ev) { if (!det.contains(ev.target)) det.open = false; });

  // Share buttons: copy link + the phone's own share sheet (WeChat, Messages, etc.).
  document.querySelectorAll('.share .copy').forEach(function (b) {
    var label = b.textContent;
    b.addEventListener('click', function () {
      var url = b.getAttribute('data-url');
      function done() { b.textContent = b.getAttribute('data-done'); b.classList.add('ok'); setTimeout(function () { b.textContent = label; b.classList.remove('ok'); }, 2200); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { window.prompt('', url); });
      else window.prompt('', url);
    });
  });
  if (navigator.share) document.querySelectorAll('.share .native').forEach(function (b) {
    b.hidden = false;
    b.addEventListener('click', function () {
      navigator.share({ title: b.getAttribute('data-title'), url: b.getAttribute('data-url') }).catch(function () {});
    });
  });

  // Checklist progress, saved per device.
  var list = document.querySelector('.checklist');
  if (!list) return;
  var boxes = list.querySelectorAll('input[data-check]');
  var text = list.querySelector('.progress-text');
  var bar = list.querySelector('.bar');
  var tpl = list.getAttribute('data-progress-text');
  function update() {
    var done = 0;
    boxes.forEach(function (b) { if (b.checked) done++; });
    text.textContent = tpl.replace('{done}', done).replace('{total}', boxes.length);
    bar.style.setProperty('--pct', (done / boxes.length * 100) + '%');
  }
  boxes.forEach(function (b) {
    b.checked = get('ms-step-' + b.dataset.check) === '1';
    b.addEventListener('change', function () {
      if (b.checked) set('ms-step-' + b.dataset.check, '1'); else del('ms-step-' + b.dataset.check);
      update();
    });
  });
  list.querySelector('.reset').addEventListener('click', function () {
    boxes.forEach(function (b) { b.checked = false; del('ms-step-' + b.dataset.check); });
    update();
  });
  update();
})();
