# Anti-patterns

The catalog behind `scripts/detect.py` plus the checks no script can make. Rule ids match the detector output exactly. Every detector hit is a candidate, not a verdict: verify it in context, and treat a deliberate, brief-earned use as a documented exception rather than a defect.

## Contents

- Running the detector
- Detector rules
- Manual checks

## Running the detector

```bash
python3 <skill-dir>/scripts/detect.py [--json] [--ignore RULE[,RULE...]] PATH [PATH ...]
```

- Scans `.html .htm .css .scss .sass .less .vue .svelte .astro .jsx .tsx .twig .jinja .jinja2 .j2 .njk` and `.blade.php` files; dependency and build directories are skipped.
- Exit 0 = no findings, 1 = findings, 2 = usage error.
- Output: `path:line  [E|W] rule-id  message`, or JSON with `--json`.
- It reads source, not the rendered page: dynamic classes, computed styles, and contrast are invisible to it.

## Detector rules

| Rule id | Sev | What it catches | Why it matters | Fix direction |
|---|---|---|---|---|
| `gradient-text` | E | `background-clip: text` with a gradient; Tailwind `bg-clip-text` + gradient | Decorative, never meaningful; a top AI tell | One solid color; emphasis through weight or size |
| `side-stripe-border` | E | Colored `border-left/right` ≥2px; `border-l-4` etc. | The reflex accent on cards, callouts, alerts | Full border, background tint, leading icon or number, or nothing |
| `hard-offset-shadow` | W | Zero-blur offset shadow (`4px 4px 0`) | Neobrutalist costume outside a world that chose it | Offset plus soft blur, or no shadow |
| `glow-halo` | W | Zero-offset colored glow | Decoration posing as depth | Real elevation or a state color with meaning |
| `glass-default` | W | `backdrop-filter: blur`; `backdrop-blur` | Glassmorphism as default chrome | Keep only as a specific, purposeful effect |
| `eyebrow-kicker` | E | Small, uppercase, widely tracked label | The banned eyebrow above headings | Delete it; let the heading carry its weight |
| `numbered-section-label` | W | `01 /`, `02 ·` section labels | Scaffolding by reflex | Keep only when the sequence carries information |
| `bounce-easing` | W | Overshooting `cubic-bezier`, bounce/elastic animations | Dated; draws attention to the motion itself | Exponential ease-out (quart, quint, expo) |
| `transition-all` | W | `transition: all`; `transition-all` | Animates layout properties by accident; jank | List the properties (usually transform, opacity) |
| `layout-transition` | W | Transitions on width, height, top, left, margin, padding | Triggers layout every frame | Transform, FLIP, or grid-row techniques |
| `arbitrary-z-index` | W | `z-index` ≥ 999; `z-[9999]` | Stacking wars | Semantic z-index scale |
| `outline-removed` | E | `outline: none` / `outline-none` with no `:focus-visible` replacement in the file | Keyboard users lose their place | A visible `:focus-visible` ring with ≥3:1 contrast |
| `zoom-disabled` | E | `user-scalable=no`, `maximum-scale=1` | Blocks zoom; WCAG 1.4.4 failure | Remove the restriction; fix the layout instead |
| `extreme-tracking` | W | Letter-spacing below -0.04em; `tracking-tighter` | Letters touch; cramped, not designed | -0.02 to -0.03em for display type |
| `tiny-text` | W | Font size under 12px | Unreadable for many users | 12px minimum for metadata, 16px for body |
| `justified-text` | W | `text-align: justify` | Rivers and uneven spacing on the web | Left-aligned (start-aligned) text |
| `reflex-font` | W | Training-data default faces (Fraunces, Playfair, Space Grotesk, …) | Category-default typography | A face from the subject's world; see [new-work.md](new-work.md) |
| `cream-tokens` | W | `--cream`, `--paper`, `--parchment`, … tokens | The saturated warm-neutral AI default | A ground that belongs to this brand |
| `stripes-background` | W | `repeating-linear-gradient` backgrounds | Texture without a subject | Remove, or tie it to a real canvas, map, or tool |
| `img-missing-alt` | E | `<img>` without `alt` | Screen readers announce the file name | Informative alt, or `alt=""` for decoration |
| `img-missing-dimensions` | W | `<img>` without width and height | Layout shift (CLS) | Explicit dimensions or `aspect-ratio` |
| `clickable-div` | E | Click handler on `div`/`span` without role and tabindex | Not focusable or announced | A real `<button>` or `<a href>` |
| `positive-tabindex` | W | `tabindex` ≥ 1 | Breaks the natural focus order | `0` or `-1`, and fix DOM order |
| `emoji-icon` | W | Emoji inside buttons and links | Glyphs standing in for an icon system | One icon library or authored SVG |
| `marketing-buzzword` | W | "seamless experience", "supercharge your", "world-class", … | Generic claims any competitor could make | Specific, provable statements about this product |

## Manual checks

No regex can judge these; check them in the render or the source:

- **Contrast in context:** text and UI against their real backgrounds, in every state and theme (WCAG 2.2 AA).
- **Nested cards** and **identical card grids** (icon + heading + text, repeated) as page structure.
- **The hero-metric template:** big number, small label, supporting stats, accent.
- **Category-default aesthetics:** the four calibration looks in [new-work.md](new-work.md).
- **Ghost cards:** a 1px border under a wide soft shadow.
- **Gray text on colored backgrounds.**
- **Modal by reflex** where inline or progressive disclosure would do.
- **Monospace as a "technical" costume** rather than for code, data, or measurement.
- **Content hidden at rest** until a script-triggered reveal runs.
- **Text overflow** of long headings at tablet and mobile widths.
- **Missing states:** hover, focus, active, disabled, loading, empty, error, success.
