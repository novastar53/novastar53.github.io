(function() {
  function initYearGroups() {
    const yearGroups = {'2024': ['how-positional-embeddings-work', 'how-dropout-works', 'nadaraya-watson-kernel-regression'], '2025': ['how-mixture-of-experts-works-part-1', 'how-batchnorm-works-part-2', 'how-residual-connections-work', 'how-batchnorm-works'], '2026': ['how-mixture-of-experts-works-part-2', 'pallas-matmul', 'pallas-softmax']};

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
          const fileName = href.split('/').pop().replace('.html', '');

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
