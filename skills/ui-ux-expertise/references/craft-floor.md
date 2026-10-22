# Craft floor

Load this after the direction is settled, immediately before any UI edit, including small refinements. Do not load it for planning-only work. Build without announcing the checklist. A pinned brief or the committed visual world overrides anything here; your own habit does not.

## Contents

- Verify: checks on the built result
- Structure: layout and implementation rules
- Refuse: page scaffolds and surface habits
- Floor, not ceiling

## Verify

Each of these is a check on the built result, not an intention. Run them together in the batched inspection round, not as separate screenshot trips; the checks share one render.

- **Contrast:** body and placeholder text ≥4.5:1, large text (≥24px, or ≥18.66px bold) ≥3:1, UI components and focus indicators ≥3:1 (WCAG 2.2 AA). On colored surfaces tint secondary text from that hue or the foreground; never gray. Light gray body text "for elegance" is the most common readability failure.
- **Depth:** shadows carry an offset and a soft blur. A zero-offset colored halo is decoration.
- **Spacing:** tight groups, generous separation, more space above a heading than below it. Vary spacing for rhythm. Read the computed values.
- **Type:** body measure 65–75ch, display max 6rem (`clamp()` max ≤ 6rem), tracking floor -0.04em, `text-wrap: balance` on h1–h3 and `text-wrap: pretty` on long prose, obvious scale and weight steps. Do not pair two faces that are similar but not identical (two geometric sans, two humanist sans); pair on a contrast axis or use one family in several weights. Run the real copy at every breakpoint and fix what overflows.
- **Motion:** one authored moment, not scattered effects and not one identical entrance on every section. Exponential ease-out from an already-visible default: never gate content visibility on a class-triggered transition, because transitions pause in hidden tabs and headless renderers and the section ships blank. Reach past transform and opacity: blur, backdrop-filter, clip-path, mask, and shadow belong to the palette when they stay smooth. Every animation has an intentional `prefers-reduced-motion` alternative.
- **States:** hover, focus, active, disabled, loading, error, empty, success. Plus real content, working controls, responsive composition, visible keyboard focus that sticky headers never cover.
- **Browser surfaces:** the parts you did not draw still carry the design. Text selection, the caret, scrollbars, focus rings, underline offset, `color-scheme` and `<meta name="theme-color">` matching the page ground, and the numerals in tabular data (`font-variant-numeric: tabular-nums`) all ship with browser defaults that belong to no design system. Theme them from the palette. This is the cheapest signal that a page was built rather than assembled, and the one models skip most reliably.
- **Copy:** the product's own language. Controls name their action; errors name the problem and the recovery.
- **Coverage:** every brief requirement present and findable within seconds.

## Structure

- Flexbox for one-dimensional layout, Grid for two-dimensional. Do not default to Grid when `flex-wrap` is simpler. For responsive grids without breakpoints: `repeat(auto-fit, minmax(min(280px, 100%), 1fr))`.
- Use a semantic z-index scale (dropdown → sticky → modal-backdrop → modal → toast → tooltip). Never arbitrary values like 999 or 9999.
- Overlays escape their container: an absolutely positioned dropdown inside `overflow: hidden` or `overflow: auto` is clipped. Use `<dialog>`, the popover API, `position: fixed`, or a portal.
- Declare elevation once, border or shadow. A 1px border under a wide soft shadow is the ghost card. Card radii stay around 12–16px; pills are for small controls.
- Never disable zoom (`user-scalable=no`, `maximum-scale=1`).

## Refuse

These are the category's defaults, not bans: the brief's own words can earn any of them. Reaching for one when the axis is free means you were not deciding; recognizing that means rewriting the element, not softening it.

Page scaffolds:

- Same-size cards of icon plus heading plus text as the page structure. Cards are the lazy container; nested cards are always wrong.
- The hero-metric template: big number, small label, supporting stats, accent.
- A kicker or eyebrow above a heading (small uppercase tracked label). This one is a ban, not a default: no brief earns it back. The heading carries its own weight; delete the label and let the heading speak.
- Section numbers (01 / 02 / 03) unless the sequence itself carries information the reader needs.
- A modal for a task that needs neither interruption nor protected focus.

Surface habits:

- Gradient text. Emphasis comes from weight or size.
- Glass and blur as decoration rather than as a specific effect.
- A colored `border-left` or `border-right` above 1px on cards, list items, callouts, or alerts.
- Hard offset shadows (`box-shadow: 4px 4px 0`) outside a world that is actually neobrutalist. The zero-blur block shadow is a costume, not a depth system.
- Sparklines, progress rings, and soft-shadowed rounded rectangles standing in for content.
- Monospace as a costume for "technical" rather than for code, data, or measurement.
- A system display face (Impact, Arial Black, the platform sans) as the display voice of an expressive page. Source and self-host a face whose character matches the direction; the closest installed font is a failure, not a fallback.
- Unicode glyphs or emoji standing in for an icon system. Icons are drawn, from a real library or authored SVG, in one consistent stroke and weight.
- Geometric masks standing in for organic contours. A circle, polygon, or radial-gradient cutout approximating a photographic subject's edge reads worse than omitting it.
- Sketch-style SVG scenes, doodle class names, and `feTurbulence` grain as illustration. Real illustration or none. This bans SVG imitating pictures, never SVG doing geometry: crisp shapes, diagrams, animated linework, and shader effects remain first-class.
- Decorative backgrounds: `repeating-linear-gradient` stripes and two-axis grid overlays need an actual canvas, map, blueprint, or measuring tool under them.
- Light or dark picked by category. Pick it from the use scene: who, where, under what ambient light.
- Claims and configuration invented for effect. They come from supplied truth; label illustrative values honestly.

Run `python3 <skill-dir>/scripts/detect.py <changed files>` to catch the mechanical subset of this list; [anti-patterns.md](anti-patterns.md) explains each rule id and lists the checks no script can make.

## Floor, not ceiling

The floor holds the mechanics; it never picks the direction. With every check green, spend the page on the committed world, and when torn between refined and committed, commit.
