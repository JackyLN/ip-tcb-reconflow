/* Public reader: all assets local, Markdown HTML disabled server-side, Mermaid strict. */

const menu = document.querySelector('.docs-menu');
const mobile = matchMedia('(max-width: 850px)');
function menuSize() { if (menu) menu.open = !mobile.matches; }
menuSize();
mobile.addEventListener('change', menuSize);

const search = document.querySelector('#docs-search');
const results = document.querySelector('#docs-search-results');
if (search && results) {
  const entries = [...document.querySelectorAll('.docs-catalog-entry')].map(link => ({
    title: link.textContent.trim(), href: link.getAttribute('href'),
  }));
  search.addEventListener('input', () => {
    results.replaceChildren();
    const query = search.value.trim().toLowerCase();
    results.hidden = !query;
    if (!query) return;
    const matches = entries.filter(entry => entry.title.toLowerCase().includes(query));
    for (const entry of matches.slice(0, 12)) {
      const link = document.createElement('a');
      link.href = entry.href;
      link.textContent = entry.title;
      results.append(link);
    }
    if (!matches.length) results.textContent = 'No matching document titles.';
  });
}

const diagrams = [...document.querySelectorAll('pre > code.language-mermaid')];
if (diagrams.length) {
const {default: mermaid} = await import('mermaid');
mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  secure: ['secure', 'securityLevel', 'startOnLoad', 'maxTextSize', 'maxEdges'],
  maxTextSize: 40000,
  maxEdges: 300,
  theme: 'base',
  fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',
  themeVariables: {
    primaryColor: '#fff1f1', primaryTextColor: '#202020', primaryBorderColor: '#cc1720',
    lineColor: '#626262', secondaryColor: '#f5f5f5', tertiaryColor: '#fbf4e7',
  },
});

for (const [index, code] of diagrams.entries()) {
  const pre = code.parentElement;
  const figure = document.createElement('figure');
  figure.className = 'docs-diagram';
  const status = document.createElement('p');
  status.setAttribute('role', 'status');
  status.textContent = 'Rendering diagram…';
  const source = document.createElement('details');
  const summary = document.createElement('summary');
  summary.textContent = 'Diagram source';
  pre.replaceWith(figure);
  source.append(summary, pre);
  figure.append(status, source);
  try {
    const rendered = await mermaid.render(`public-diagram-${index}`, code.textContent);
    const diagram = document.createElement('div');
    diagram.className = 'docs-diagram-canvas';
    diagram.tabIndex = 0;
    diagram.setAttribute('role', 'region');
    diagram.setAttribute('aria-label', 'Diagram, horizontally scrollable');
    // Mermaid strict mode sanitizes generated SVG; no HTML from Markdown is inserted here.
    diagram.innerHTML = rendered.svg;
    figure.prepend(diagram);
    status.remove();
    figure.dataset.rendered = 'true';
  } catch {
    status.textContent = 'Diagram could not render. Its source is available below.';
    status.setAttribute('role', 'alert');
    source.open = true;
  }
}

}
