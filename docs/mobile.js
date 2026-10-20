/* Phone layout helper for theshansstudio.com
 *
 * The pages are exported from Claude Design as fixed 1440px desktop canvases.
 * mobile.css reflows them on phones; this script adds what CSS alone can't:
 *   - marks the page type on <html> so mobile.css can target each page
 *   - orders the About-page cards by their headings (contact first, etc.)
 *   - turns hover-only interactions into taps (night view on project heroes)
 *
 * The Claude Design runtime re-renders its own elements and drops attributes
 * it doesn't know, so this script never writes onto those elements. It only
 * touches <html> and its own <style> block. Inert above 760px.
 */
(function () {
  var PHONE = window.matchMedia('(max-width: 760px)');
  var root = document.documentElement;

  function pageType() {
    var f = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    if (f === '' || f === 'index.html' || f.indexOf('home') === 0) return 'home';
    if (f.indexOf('about') === 0) return 'about';
    if (f.indexOf('main') === 0) return 'projects';
    if (f.indexOf('chapter') === 0) return 'project';
    return 'other';
  }
  var TYPE = pageType();
  root.classList.add('m-' + TYPE);

  /* ---- About: phone order of the cards, matched by what they say ---- */
  var ORDER = [            // [text to look for, order, hide on phone]
    ['contact me', 3], ['technical', 5], ['in practice', 6], ['experience', 7],
    ['education', 8], ['human bit', 9], ['download', 2], ['skills', 4, true],
    ['shanmathi', 1]
  ];
  var styleEl = null;
  function orderCards() {
    var notes = document.querySelectorAll('.pf-page .pf-note');
    if (!notes.length) return false;
    var rules = [];
    for (var i = 0; i < notes.length; i++) {
      var n = notes[i], parent = n.parentElement;
      var idx = Array.prototype.indexOf.call(parent.children, n) + 1;
      var scope = parent.classList.contains('pf-notes') ? '.pf-notes' : '.pf-page';
      var t = (n.textContent || '').toLowerCase();
      for (var j = 0; j < ORDER.length; j++) {
        if (t.indexOf(ORDER[j][0]) === -1) continue;
        var sel = 'html.m-about ' + scope + ' > :nth-child(' + idx + ')';
        rules.push(sel + '{order:' + ORDER[j][1] + (ORDER[j][2] ? ';display:none!important' : '') + '}');
        break;
      }
    }
    if (!styleEl) {
      styleEl = document.createElement('style');
      styleEl.id = 'm-about-order';
      document.head.appendChild(styleEl);
    }
    var css = '@media (max-width:760px){' + rules.join('') + '}';
    if (styleEl.textContent !== css) styleEl.textContent = css;
    return true;
  }

  /* ---- Project heroes: tap to switch day / night render ---- */
  document.addEventListener('click', function (e) {
    if (!PHONE.matches || TYPE !== 'project') return;
    if (e.target.closest && e.target.closest('.pf-hero')) root.classList.toggle('m-night');
  });

  /* Claude Design renders after load, so wait for the content to appear. */
  if (TYPE === 'about') {
    var found = 0, tries = 0;
    (function poll() {
      if (orderCards()) found++;
      if (found > 3 || ++tries > 40) return;  // a few passes catch re-renders
      setTimeout(poll, 400);
    })();
  }
})();
