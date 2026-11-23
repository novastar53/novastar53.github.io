(function() {
  var MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function initYearGroups() {
    const yearGroups = YEARGROUPS_PLACEHOLDER; // {year: {month: [file, ...]}}

    const wrapper = document.querySelector('.sphinxsidebarwrapper');
    if (!wrapper) return;

    const list = wrapper.querySelector('ul');
    if (!list) return;

    const listItems = Array.from(list.children);
    const usedItems = new Set();

    const years = Object.keys(yearGroups).sort(function(a, b) { return parseInt(b) - parseInt(a); });

    const yearSections = {};

    function matchFile(li, groupFiles) {
      const link = li.querySelector('a.reference');
      if (!link) return false;
      const href = link.getAttribute('href') || '';
      // Sphinx renders the current page's toctree entry as href="#"
      const fileName = href === '#'
        ? location.pathname.split('/').pop().replace('.html', '')
        : href.split('/').pop().replace('.html', '');
      return groupFiles.includes(fileName);
    }

    years.forEach(function(year) {
      const header = document.createElement('p');
      header.className = 'caption year-caption';
      header.textContent = year;
      header.setAttribute('data-year', year);

      const section = document.createElement('section');
      section.setAttribute('data-year', year);

      // newest month first within the year
      const months = Object.keys(yearGroups[year]).sort(function(a, b) { return parseInt(b) - parseInt(a); });

      months.forEach(function(month) {
        const monthKey = year + '-' + ('0' + month).slice(-2);
        const monthHeader = document.createElement('p');
        monthHeader.className = 'caption month-caption';
        monthHeader.textContent = MONTH_NAMES[parseInt(month) - 1];
        monthHeader.setAttribute('data-month', monthKey);

        const monthSection = document.createElement('section');
        monthSection.setAttribute('data-month', monthKey);

        const groupFiles = yearGroups[year][month];

        listItems.forEach(function(li) {
          if (usedItems.has(li)) return;
          if (matchFile(li, groupFiles)) {
            monthSection.appendChild(li.cloneNode(true));
            li.style.display = 'none';
            usedItems.add(li);
          }
        });

        if (monthSection.querySelectorAll('li').length > 0) {
          monthHeader.addEventListener('click', function() {
            this.classList.toggle('expanded');
            localStorage.setItem('sidebar_month_' + monthKey, this.classList.contains('expanded'));
          });

          const stored = localStorage.getItem('sidebar_month_' + monthKey);
          if (stored === 'true') {
            monthHeader.classList.add('expanded');
          }

          section.appendChild(monthHeader);
          section.appendChild(monthSection);
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
        // expand the current post's month group and year group
        var monthSection = a.closest('section[data-month]');
        if (monthSection) {
          var monthHeader = monthSection.previousElementSibling;
          if (monthHeader && monthHeader.classList.contains('caption')) {
            monthHeader.classList.add('expanded');
          }
        }
        var yearSection = a.closest('section[data-year]');
        if (yearSection) {
          var yearHeader = yearSection.previousElementSibling;
          if (yearHeader && yearHeader.classList.contains('caption')) {
            yearHeader.classList.add('expanded');
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
