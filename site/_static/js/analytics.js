// Privacy-respecting analytics via Plausible (https://plausible.io).
// 1. Sign up at plausible.io and add the site "blog.vikrampawar.com"
// 2. Set ENABLED to true below. That's it — no cookie banner needed.
(function() {
  var ENABLED = false;
  if (!ENABLED) return;
  var s = document.createElement('script');
  s.defer = true;
  s.setAttribute('data-domain', 'blog.vikrampawar.com');
  s.src = 'https://plausible.io/js/script.js';
  document.head.appendChild(s);
})();
