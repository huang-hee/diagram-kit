(function () {
  // copy buttons
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.copy');
    if (!btn) return;
    var code = btn.parentElement.querySelector('code');
    var text = code ? code.textContent : '';
    function selectIt() {
      var r = document.createRange(); r.selectNodeContents(code);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      btn.textContent = '已选中，按 ⌘C 复制';
    }
    try {
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = '已复制';
        setTimeout(function () { btn.textContent = '复制'; }, 1600);
      }, selectIt);
    } catch (err) { selectIt(); }
  });

  // search
  var q = document.getElementById('q'), hits = document.getElementById('hits'), empty = document.getElementById('empty');
  var types = Array.prototype.slice.call(document.querySelectorAll('.type'));
  var cats = Array.prototype.slice.call(document.querySelectorAll('.cat'));
  function apply() {
    var terms = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    document.body.classList.toggle('searching', terms.length > 0);
    var n = 0;
    types.forEach(function (el) {
      var ok = terms.every(function (t) { return el.dataset.search.indexOf(t) !== -1; });
      el.hidden = !ok; if (ok) n++;
    });
    cats.forEach(function (c) { c.hidden = terms.length > 0 && !c.querySelector('.type:not([hidden])'); });
    hits.textContent = terms.length ? n + ' 种' : '';
    empty.classList.toggle('show', terms.length > 0 && n === 0);
  }
  q.addEventListener('input', apply);

  // collapse the index on narrow screens
  var idx = document.querySelector('.index');
  if (window.matchMedia('(max-width: 960px)').matches) idx.removeAttribute('open');

  // highlight the entry being read
  var links = {};
  document.querySelectorAll('.index a[href^="#"]').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window) {
    var cur = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && links[en.target.id]) {
          if (cur) cur.classList.remove('active');
          cur = links[en.target.id]; cur.classList.add('active');
        }
      });
    }, { rootMargin: '0px 0px -70% 0px' });
    document.querySelectorAll('.type, .topic, #quick').forEach(function (el) { io.observe(el); });
  }
})();
