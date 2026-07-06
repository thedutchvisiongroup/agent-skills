# HTML Scaffold

## Contents
- Purpose and constraints
- How to use this scaffold
- The full HTML template (copy-paste)
- Mermaid embedding pattern (CDN + fallback)
- CSS-box wireframe components
- Light/dark mode (OS preference + toggle)
- Notes on carrousel, tabs, collapsibles, sticky TOC, print

## Purpose and constraints

When the user requests HTML output (or both Markdown + HTML), generate ONE self-contained `.html` file from the Markdown draft. Constraints:

- **One file.** All CSS inline in `<style>`. All JS inline in `<script>`. No external assets except the Mermaid CDN (with fallback).
- **Mermaid via CDN** (`https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs`) with a fallback: if Mermaid fails to load, the raw diagram code is shown in a `<pre>` so the content is still readable offline.
- **Sticky TOC** on the left (desktop) / top (mobile).
- **Tabs** for top-level sections.
- **Collapsible** subsections within tabs.
- **Carrousel** for sequences of wireframes or diagrams.
- **Light/dark** respects OS `prefers-color-scheme` by default, with a manual toggle that persists to `localStorage`.
- **Print stylesheet** that expands all collapsed sections, hides TOC/tabs chrome, and produces a clean linear document.
- **Wireframes as CSS-box mockups** (gray boxes with labels). No SVG, no images.

The HTML does not need to be pretty source code — it needs to render well. Prioritise the rendered output.

## How to use this scaffold

1. Draft the Markdown FTD first (Phase 2).
2. Convert each Markdown section into the HTML structure below:
   - Each top-level heading (`#`) becomes a tab.
   - Each second-level heading (`##`) becomes a collapsible within a tab.
   - Mermaid code blocks become `<pre class="mermaid">…</pre>` blocks (Mermaid renders them; fallback shows the raw code).
   - Tables become HTML tables with the same classes.
   - Wireframe placeholders become `<div class="wireframe">…</div>` blocks.
3. Generate the file with the chosen filename (from Phase 1 Q4).
4. Open in a browser to verify rendering. If Mermaid does not render, the fallback shows the code — still acceptable.

## The full HTML template (copy-paste)

Below is the scaffold. Replace `[CONTENT]` placeholders with the FTD content. The CSS and JS are minimal but functional.

```html
<!DOCTYPE html>
<html lang="[nl|en]">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[FTD title] v[X.Y]</title>
<style>
  /* ---------- CSS variables: light/dark ---------- */
  :root {
    --bg: #ffffff;
    --fg: #1a1a1a;
    --muted: #6b7280;
    --accent: #2563eb;
    --border: #e5e7eb;
    --surface: #f9fafb;
    --code-bg: #f3f4f6;
    --wireframe-bg: #e5e7eb;
    --wireframe-border: #9ca3af;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0f172a;
      --fg: #e2e8f0;
      --muted: #94a3b8;
      --accent: #3b82f6;
      --border: #334155;
      --surface: #1e293b;
      --code-bg: #1e293b;
      --wireframe-bg: #334155;
      --wireframe-border: #64748b;
    }
  }
  :root[data-theme="dark"] {
    --bg: #0f172a;
    --fg: #e2e8f0;
    --muted: #94a3b8;
    --accent: #3b82f6;
    --border: #334155;
    --surface: #1e293b;
    --code-bg: #1e293b;
    --wireframe-bg: #334155;
    --wireframe-border: #64748b;
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--fg);
    line-height: 1.6;
  }

  /* ---------- Layout ---------- */
  .layout { display: flex; min-height: 100vh; }
  .toc {
    width: 280px;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 1.5rem 1rem;
  }
  .toc h2 { font-size: 0.875rem; text-transform: uppercase; color: var(--muted); margin: 0 0 1rem 0; }
  .toc ul { list-style: none; padding: 0; margin: 0; }
  .toc li { margin: 0.25rem 0; }
  .toc a { color: var(--fg); text-decoration: none; font-size: 0.875rem; display: block; padding: 0.25rem 0.5rem; border-radius: 4px; }
  .toc a:hover { background: var(--border); }
  .toc a.active { background: var(--accent); color: #fff; }
  .main { flex: 1; padding: 2rem 3rem; max-width: 960px; }

  @media (max-width: 768px) {
    .layout { flex-direction: column; }
    .toc { width: 100%; height: auto; position: relative; border-right: none; border-bottom: 1px solid var(--border); }
    .main { padding: 1rem; }
  }

  /* ---------- Header ---------- */
  .doc-header { margin-bottom: 2rem; border-bottom: 2px solid var(--accent); padding-bottom: 1rem; }
  .doc-header h1 { margin: 0 0 0.5rem 0; font-size: 1.875rem; }
  .doc-meta { display: flex; flex-wrap: wrap; gap: 1rem; color: var(--muted); font-size: 0.875rem; }

  /* ---------- Theme toggle ---------- */
  .theme-toggle {
    position: fixed; top: 1rem; right: 1rem; z-index: 100;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 50%; width: 40px; height: 40px; cursor: pointer;
    font-size: 1.2rem; display: flex; align-items: center; justify-content: center;
  }

  /* ---------- Tabs ---------- */
  .tabs { display: flex; flex-wrap: wrap; gap: 0.25rem; border-bottom: 2px solid var(--border); margin-bottom: 1.5rem; }
  .tab-button {
    background: none; border: none; padding: 0.75rem 1.25rem; cursor: pointer;
    font-size: 0.95rem; color: var(--muted); border-bottom: 2px solid transparent;
    margin-bottom: -2px;
  }
  .tab-button.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }

  /* ---------- Collapsible ---------- */
  .collapsible { border: 1px solid var(--border); border-radius: 6px; margin: 1rem 0; overflow: hidden; }
  .collapsible-header {
    background: var(--surface); padding: 0.75rem 1rem; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center; font-weight: 600;
  }
  .collapsible-header::after { content: "▶"; transition: transform 0.2s; color: var(--muted); }
  .collapsible.open .collapsible-header::after { transform: rotate(90deg); }
  .collapsible-body { padding: 1rem; display: none; }
  .collapsible.open .collapsible-body { display: block; }

  /* ---------- Tables ---------- */
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }
  th, td { border: 1px solid var(--border); padding: 0.5rem 0.75rem; text-align: left; }
  th { background: var(--surface); font-weight: 600; }
  tr:nth-child(even) { background: var(--surface); }

  /* ---------- Code & Mermaid ---------- */
  pre { background: var(--code-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; }
  code { font-family: "SF Mono", Monaco, Consolas, monospace; font-size: 0.875em; }
  pre.mermaid { text-align: center; background: var(--surface); }
  .mermaid-fallback { display: none; }

  /* ---------- Wireframe (CSS-box) ---------- */
  .wireframe {
    border: 2px dashed var(--wireframe-border);
    background: var(--wireframe-bg);
    border-radius: 6px; padding: 1.5rem; margin: 1rem 0;
    display: flex; flex-direction: column; gap: 0.75rem;
  }
  .wf-box {
    background: var(--bg); border: 1px solid var(--wireframe-border);
    border-radius: 4px; padding: 0.75rem; min-height: 40px;
    display: flex; align-items: center; justify-content: center;
    color: var(--muted); font-size: 0.85rem;
  }
  .wf-row { display: flex; gap: 0.75rem; }
  .wf-col { flex: 1; }

  /* ---------- Carrousel ---------- */
  .carrousel { position: relative; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; margin: 1rem 0; }
  .carrousel-track { display: flex; transition: transform 0.3s; }
  .carrousel-slide { min-width: 100%; padding: 1rem; }
  .carrousel-buttons { display: flex; justify-content: space-between; padding: 0.5rem 1rem; background: var(--surface); }
  .carrousel-buttons button { background: none; border: 1px solid var(--border); border-radius: 4px; padding: 0.25rem 0.75rem; cursor: pointer; color: var(--fg); }

  /* ---------- Print ---------- */
  @media print {
    .toc, .theme-toggle, .tabs, .carrousel-buttons { display: none !important; }
    .layout { display: block; }
    .tab-panel { display: block !important; }
    .collapsible-body { display: block !important; }
    .collapsible-header::after { content: ""; }
    .main { max-width: 100%; padding: 0; }
    body { background: #fff; color: #000; }
  }
</style>
</head>
<body>
<button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">🌓</button>

<div class="layout">
  <nav class="toc">
    <h2>Contents</h2>
    <ul id="toc-list">
      <!-- TOC entries auto-generated by JS -->
    </ul>
  </nav>

  <main class="main">
    <div class="doc-header">
      <h1>[FTD title]</h1>
      <div class="doc-meta">
        <span>v[X.Y]</span>
        <span>[Datum]</span>
        <span>[Auteur]</span>
        <span>[Status]</span>
      </div>
    </div>

    <div class="tabs" id="tabs">
      <!-- Tab buttons: one per top-level section -->
      <button class="tab-button active" onclick="showTab(0)">1. Documentbeheer</button>
      <button class="tab-button" onclick="showTab(1)">2. Scope</button>
      <button class="tab-button" onclick="showTab(2)">3. User stories</button>
      <!-- ... add one per section ... -->
    </div>

    <!-- Tab panels -->
    <div class="tab-panel active" data-tab="0">
      [Section 1 content]
    </div>
    <div class="tab-panel" data-tab="1">
      [Section 2 content]
    </div>
    <div class="tab-panel" data-tab="2">
      [Section 3 content]
    </div>
    <!-- ... one per section ... -->
  </main>
</div>

<script>
  // ---------- Theme ----------
  function applyTheme(t) { document.documentElement.setAttribute('data-theme', t); localStorage.setItem('ftd-theme', t); }
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const osDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const effective = current || (osDark ? 'dark' : 'light');
    applyTheme(effective === 'dark' ? 'light' : 'dark');
  }
  const savedTheme = localStorage.getItem('ftd-theme');
  if (savedTheme) { applyTheme(savedTheme); }

  // ---------- Tabs ----------
  function showTab(index) {
    document.querySelectorAll('.tab-button').forEach((b, i) => b.classList.toggle('active', i === index));
    document.querySelectorAll('.tab-panel').forEach((p, i) => p.classList.toggle('active', i === index));
    buildTOC(index);
  }

  // ---------- Collapsible ----------
  document.querySelectorAll('.collapsible-header').forEach(h => {
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  });

  // ---------- TOC builder ----------
  function buildTOC(tabIndex) {
    const panel = document.querySelector(`.tab-panel[data-tab="${tabIndex}"]`);
    const list = document.getElementById('toc-list');
    list.innerHTML = '';
    if (!panel) return;
    panel.querySelectorAll('h2, h3').forEach(h => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.textContent = h.textContent;
      a.href = '#';
      a.style.paddingLeft = h.tagName === 'H3' ? '1.5rem' : '0.5rem';
      a.addEventListener('click', e => { e.preventDefault(); h.scrollIntoView({behavior:'smooth', block:'start'}); });
      li.appendChild(a);
      list.appendChild(li);
    });
  }
  buildTOC(0);

  // ---------- Carrousel ----------
  document.querySelectorAll('.carrousel').forEach(c => {
    const track = c.querySelector('.carrousel-track');
    const slides = c.querySelectorAll('.carrousel-slide');
    let idx = 0;
    c.querySelector('.carrousel-next').addEventListener('click', () => {
      idx = (idx + 1) % slides.length; track.style.transform = `translateX(-${idx * 100}%)`;
    });
    c.querySelector('.carrousel-prev').addEventListener('click', () => {
      idx = (idx - 1 + slides.length) % slides.length; track.style.transform = `translateX(-${idx * 100}%)`;
    });
  });
</script>

<!-- Mermaid via CDN with fallback -->
<script type="module">
  const mermaidBlocks = document.querySelectorAll('pre.mermaid');
  try {
    const mermaid = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
    mermaid.default.initialize({
      startOnLoad: true,
      theme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'default'
    });
  } catch (e) {
    // Fallback: show the raw diagram code so content is still readable
    console.warn('Mermaid CDN failed to load:', e);
    mermaidBlocks.forEach(b => {
      const fb = document.createElement('pre');
      fb.className = 'mermaid-fallback';
      fb.textContent = b.textContent;
      b.parentNode.replaceChild(fb, b);
    });
  }
</script>
</body>
</html>
```

## Mermaid embedding pattern (CDN + fallback)

Each Mermaid diagram in the HTML is a `<pre class="mermaid">` block:

```html
<pre class="mermaid">
sequenceDiagram
    actor User
    participant API
    User->>API: POST /orders
    API-->>User: 201 Created
</pre>
```

The Mermaid v11 ESM module is imported via CDN. The module's `default` export provides `initialize()` and renders all `<pre class="mermaid">` blocks on load. If the CDN fails (offline, blocked, network error), the fallback script replaces each `<pre class="mermaid">` with a plain `<pre>` showing the raw diagram code. The content remains readable, just not rendered.

**Important:** the raw Mermaid code MUST be present inside the `<pre>` tag. Do not escape it further. Mermaid parses the text content of the element.

**Mermaid v11 note:** v11 uses ESM (`mermaid.esm.min.mjs`) as the primary distribution. The `default` export is the mermaid API — call `mermaid.default.initialize(...)` and it auto-renders `<pre class="mermaid">` blocks when `startOnLoad: true`.

## CSS-box wireframe components

Use the `.wireframe` container with `.wf-box`, `.wf-row`, and `.wf-col` to compose gray-box mockups.

```html
<div class="wireframe">
  <div class="wf-box">Header — logo, nav, login</div>
  <div class="wf-row">
    <div class="wf-col"><div class="wf-box">Sidebar — filters</div></div>
    <div class="wf-col"><div class="wf-box">Main — data table</div></div>
  </div>
  <div class="wf-box">Footer — actions</div>
</div>
```

For multi-step flows, use the carrousel:

```html
<div class="carrousel">
  <div class="carrousel-buttons">
    <button class="carrousel-prev">◀ Prev</button>
    <span>Step 1 of 3</span>
    <button class="carrousel-next">Next ▶</button>
  </div>
  <div class="carrousel-track">
    <div class="carrousel-slide">
      <div class="wireframe"><div class="wf-box">Step 1 — form</div></div>
    </div>
    <div class="carrousel-slide">
      <div class="wireframe"><div class="wf-box">Step 2 — review</div></div>
    </div>
    <div class="carrousel-slide">
      <div class="wireframe"><div class="wf-box">Step 3 — confirmation</div></div>
    </div>
  </div>
</div>
```

## Light/dark mode (OS preference + toggle)

- Default: respects `prefers-color-scheme` via the `@media` query in CSS.
- Manual toggle: the 🌓 button calls `toggleTheme()`, which sets `data-theme` on `<html>` and persists to `localStorage`.
- If a saved theme exists in `localStorage`, it overrides the OS preference on load.
- Mermaid is initialised with the matching theme (`dark` or `default`).

## Notes on carrousel, tabs, collapsibles, sticky TOC, print

- **Carrousel:** use for sequences of wireframes or multi-step flows. Each `.carrousel-slide` is a full-width panel; the track translates horizontally.
- **Tabs:** one per top-level section (`#` heading in Markdown). `showTab(index)` shows the matching panel and rebuilds the TOC for that section.
- **Collapsibles:** use for second-level sections (`##` headings) that are long. The user can expand/collapse. All collapsibles expand automatically in print.
- **Sticky TOC:** on desktop, the TOC stays visible on the left and shows the headings of the current tab. On mobile, it appears at the top.
- **Print:** all chrome (TOC, tabs, theme toggle, carrousel buttons) is hidden; all tab panels and collapsibles are expanded; the document becomes a linear flow suitable for PDF export.
