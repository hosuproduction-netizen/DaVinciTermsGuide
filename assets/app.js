(() => {
  'use strict';
  if (window.__davinciGuideReady) return;
  window.__davinciGuideReady = true;
  const root = window.DG_ROOT || '';
  const data = window.DG_DATA || { features: [] };
  // HTML 파일을 직접 열어도 디렉터리 링크가 index.html로 연결되도록 보완합니다.
  const offline = window.location.protocol === 'file:';
  const usableHref = href => {
    if (!offline || !href || /^(?:https?:|mailto:|#|javascript:)/i.test(href)) return href;
    return href.replace(/\/(?=\?|#|$)/, '/index.html');
  };
  if (offline) document.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (href) a.setAttribute('href', usableHref(href));
  });
  const normalize = text => String(text || '').toLocaleLowerCase('ko-KR').replace(/\s+/g, ' ').trim();
  const matches = (haystack, words) => words.every(word => haystack.includes(word));

  // 홈 검색: 기능 이름뿐 아니라 모든 프로그램의 대응 용어·한글 별칭을 검색합니다.
  const globalForm = document.querySelector('[data-global-form]');
  const globalInput = document.querySelector('[data-global-search]');
  const globalResults = document.querySelector('[data-global-results]');
  if (globalInput && globalResults && globalForm) {
    const makeElement = (tag, className, text) => {
      const element = document.createElement(tag);
      if (className) element.className = className;
      if (text !== undefined) element.textContent = text;
      return element;
    };
    const all = data.features.map(feature => ({
      feature,
      haystack: normalize([feature.title, feature.resolve, feature.summary, feature.location, ...feature.keywords, ...Object.values(feature.maps).map(mapping => mapping.name)].join(' ')),
    }));
    const updateGlobalSearch = () => {
      const query = normalize(globalInput.value);
      globalResults.replaceChildren();
      if (!query) { globalResults.hidden = true; return; }
      const words = query.split(' ').filter(Boolean);
      const found = all.filter(item => matches(item.haystack, words));
      globalResults.hidden = false;
      if (!found.length) {
        globalResults.append(makeElement('p', 'global-none', '검색 결과가 없습니다. 다른 용어로 검색해 보세요.'));
      } else {
        found.slice(0, 5).forEach(({ feature }) => {
          const a = makeElement('a', 'global-result-item');
          a.href = usableHref(`${root}features/${encodeURIComponent(feature.slug)}/`);
          const info = makeElement('span');
          info.append(makeElement('strong', '', feature.title), makeElement('small', '', `${feature.resolve} · ${feature.category}`));
          a.append(info, makeElement('span', '', '↗'));
          globalResults.append(a);
        });
        if (found.length > 5) {
          const more = makeElement('a', 'global-more', `검색 결과 ${found.length}개 모두 보기 ↗`);
          more.href = usableHref(`${root}dictionary/?q=${encodeURIComponent(globalInput.value.trim())}`);
          globalResults.append(more);
        }
      }
    };
    globalInput.addEventListener('input', updateGlobalSearch);
    globalForm.addEventListener('submit', event => {
      event.preventDefault();
      const query = globalInput.value.trim();
      if (query) window.location.href = usableHref(`${root}dictionary/?q=${encodeURIComponent(query)}`);
      else globalInput.focus();
    });
  }

  // 비교표와 기능 사전: 실제 렌더링된 정적 HTML 행을 필터링합니다.
  const list = document.querySelector('[data-list-area]');
  const listInput = document.querySelector('[data-list-search]');
  const countEl = document.querySelector('[data-result-count]');
  const filterButtons = [...document.querySelectorAll('[data-filters] [data-cat]')];
  const rows = list ? [...list.querySelectorAll('[data-row]')] : [];
  const noResults = list?.querySelector('[data-empty]');
  if (list && listInput) {
    let activeCategory = '전체';
    const queryString = new URLSearchParams(window.location.search).get('q');
    if (queryString && queryString.length <= 200) listInput.value = queryString;
    const updateList = () => {
      const words = normalize(listInput.value).split(' ').filter(Boolean);
      let visible = 0;
      rows.forEach(row => {
        const categoryMatches = activeCategory === '전체' || row.dataset.category === activeCategory;
        const textMatches = matches(normalize(row.dataset.search), words);
        row.hidden = !(categoryMatches && textMatches);
        if (!row.hidden) visible++;
      });
      if (countEl) countEl.textContent = String(visible);
      if (noResults) noResults.hidden = visible !== 0;
    };
    listInput.addEventListener('input', updateList);
    filterButtons.forEach(button => button.addEventListener('click', () => {
      activeCategory = button.dataset.cat || '전체';
      filterButtons.forEach(item => {
        const active = item === button;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      updateList();
    }));
    const clear = list.querySelector('[data-clear-filters]');
    if (clear) clear.addEventListener('click', () => {
      listInput.value = '';
      filterButtons.find(b => b.dataset.cat === '전체')?.click();
      listInput.focus();
    });
    updateList();
  }
  const switcher = document.querySelector('[data-program-switch]');
  if (switcher) switcher.addEventListener('change', () => {
    if (switcher.value) window.location.href = usableHref(switcher.value);
  });
})();

// 기존에 생성된 개별 기능 페이지의 장식용 영문 라벨을 한국어로 표시합니다.
// 새로 빌드한 HTML은 templates/feature.html에서 이미 한국어로 생성됩니다.
const koreanPageLabels = {
  'WHERE TO FIND IT': '다빈치에서 찾는 위치',
  'REFERENCE': '공식 자료',
  'QUICK REFERENCE': '기능 한눈에 보기',
  'KEEP EXPLORING': '관련 기능',
  'DAVINCI RESOLVE 21.1': '다빈치 리졸브 21.1'
};
if (document.body.classList.contains('is-feature')) {
  document.querySelectorAll('.feature-path-caption,.official-source>span,.aside-panel>.eyebrow,.related-section .eyebrow,.feature-hero>.eyebrow,.feature-hero > div > .eyebrow').forEach(el => {
    const val = el.textContent.trim();
    if (koreanPageLabels[val]) el.textContent = koreanPageLabels[val];
    else if (val.includes('DAVINCI RESOLVE 21.1')) el.textContent = val.replace('DAVINCI RESOLVE 21.1', '다빈치 리졸브 21.1');
  });
  document.querySelectorAll('.quick-box b').forEach(el => {
    if (el.textContent.trim() === 'DaVinci Resolve 21.1') el.textContent = '다빈치 리졸브 21.1';
  });
}
