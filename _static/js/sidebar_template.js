(function() {
  function initYearGroups() {
    const yearGroups = YEARGROUPS_PLACEHOLDER;

    const wrapper = document.querySelector('.sphinxsidebarwrapper');
    if (!wrapper) return;

    const list = wrapper.querySelector('ul');
    if (!list) return;

    const listItems = Array.from(list.children);
    const usedItems = new Set();

    const years = Object.keys(yearGroups).sort(function(a, b) { return parseInt(b) - parseInt(a); });

    const yearSections = {};

    years.forEach(function(year) {
      const header = document.createElement('p');
      header.className = 'caption';
      header.textContent = year;
      header.setAttribute('data-year', year);

      const section = document.createElement('section');
      section.setAttribute('data-year', year);

      const groupFiles = yearGroups[year];

      listItems.forEach(function(li) {
        if (usedItems.has(li)) return;

        const link = li.querySelector('a.reference');
        if (link) {
          const href = link.getAttribute('href') || '';
          // Sphinx renders the current page's toctree entry as href="#"
          const fileName = href === '#'
            ? location.pathname.split('/').pop().replace('.html', '')
            : href.split('/').pop().replace('.html', '');

          if (groupFiles.includes(fileName)) {
            section.appendChild(li.cloneNode(true));
            li.style.display = 'none';
            usedItems.add(li);
          }
        }
      });

      if (section.querySelectorAll('li').length > 0) {
        header.classList.add('expanded');

        header.addEventListener('click', function() {
          this.classList.toggle('expanded');
          localStorage.setItem('sidebar_year_' + year, this.classList.contains('expanded'));
        });

        const stored = localStorage.getItem('sidebar_year_' + year);
        if (stored === 'false') {
          header.classList.remove('expanded');
        }

        yearSections[year] = { header, section };
      }
    });

    const ungroupedItems = [];
    listItems.forEach(function(li) {
      if (!usedItems.has(li)) {
        ungroupedItems.push(li);
      }
    });

    const recentYear = years[years.length - 1];
    if (yearSections[recentYear]) {
      ungroupedItems.forEach(function(li) {
        yearSections[recentYear].section.appendChild(li.cloneNode(true));
        li.style.display = 'none';
      });
    }

    const yearsReverse = years.slice().reverse();
    yearsReverse.forEach(function(year) {
      const item = yearSections[year];
      if (item) {
        list.insertBefore(item.section, list.firstChild);
        list.insertBefore(item.header, list.firstChild);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initYearGroups);
  } else {
    initYearGroups();
  }
})();

(function() {
  var root = document.documentElement;
  var KEY = 'theme';

  function current() {
    return root.getAttribute('data-theme') || '';
  }

  function apply(theme, persist) {
    root.setAttribute('data-theme', theme);
    if (persist) {
      localStorage.setItem(KEY, theme);
    }
    var btn = document.querySelector('button.theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? '☀  Light mode' : '☾  Dark mode';
    }
  }

  function preferred() {
    var stored = localStorage.getItem(KEY);
    if (stored === 'dark' || stored === 'light') return stored;
    return 'light'; // light is the default; OS preference is not auto-followed
  }

  apply(preferred(), false);

  function addToggle() {
    var wrapper = document.querySelector('.sphinxsidebarwrapper');
    if (!wrapper || wrapper.querySelector('button.theme-toggle')) return;
    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.addEventListener('click', function() {
      apply(current() === 'dark' ? 'light' : 'dark', true);
    });
    wrapper.insertBefore(btn, wrapper.firstChild);
    apply(current(), false); // set the initial label
  }

  function markCurrentPage() {
    var here = location.pathname.split('/').pop();
    var links = document.querySelectorAll('.sphinxsidebarwrapper a.reference');
    Array.prototype.forEach.call(links, function(a) {
      var href = (a.getAttribute('href') || '').split('#')[0].split('/').pop();
      // href "#" (or empty after stripping the fragment) means this IS the current page
      if ((href && href === here) || a.getAttribute('href') === '#') {
        a.classList.add('current');
        // make sure the current post's year group is expanded
        var section = a.closest('section[data-year]');
        if (section) {
          var header = section.previousElementSibling;
          if (header && header.classList.contains('caption')) {
            header.classList.add('expanded');
          }
        }
      }
    });
  }

  function addSidebarToggle() {
    if (document.querySelector('button.sidebar-toggle')) return;
    var btn = document.createElement('button');
    btn.className = 'sidebar-toggle';
    btn.setAttribute('aria-label', 'Toggle navigation');
    btn.addEventListener('click', function() {
      document.body.classList.toggle('sidebar-open');
    });
    document.body.insertBefore(btn, document.body.firstChild);

    // Close the drawer after navigating to a page from it
    var sidebar = document.querySelector('div.sphinxsidebar');
    if (sidebar) {
      sidebar.addEventListener('click', function(e) {
        if (e.target.closest('a')) document.body.classList.remove('sidebar-open');
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addToggle);
    document.addEventListener('DOMContentLoaded', markCurrentPage);
    document.addEventListener('DOMContentLoaded', addSidebarToggle);
  } else {
    addToggle();
    markCurrentPage();
    addSidebarToggle();
  }
})();
