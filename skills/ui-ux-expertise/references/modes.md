# Modes

The mode names what the visitor's success looks like on the surface in front of you. Choose it from the requested surface, not the product: a tool's landing page is still Persuade; a fashion house's documentation is still Read; a docs index is Read, not Persuade. Propose the mode in the clarification gate and let the user confirm it.

## Contents

- Persuade and Experience
- Operate
- Read
- First-viewport sketches per mode

## Persuade and Experience

**Persuade:** the visitor decides and acts; design is the product. Landing pages, marketing, campaigns, pricing. Earn attention and action. Ship real imagery when the brief needs it; follow the committed world, not category habit.

**Experience:** the visitor is inside the work itself. Portfolios, galleries, showcases. Let the artifact lead from the first viewport; the interface recedes.

For **Persuade**, the opening must make the offer intelligible and desirable, expose a clear action, and demonstrate something only this product can prove. The action is the one the category's visitors came to take, in its working form: an airline's route-and-dates search, a clinic's open appointment slots, a store's add to cart. A decorative link pointing at it elsewhere does not count. Conversion lives inside the form's own vocabulary: a hook that lands in one line, a visible primary action, a legible reading order. A committed form that hides the offer or the action has not finished translating. For **Experience**, the work itself leads from the first viewport.

### The slop test

If someone could look at the page and say "AI made that" without hesitation, it failed. The bar is distinctiveness: a visitor should ask "how was this made?", not "which AI made this?" Restraint without intent reads as mediocre, not refined. In one sentence, describe what you are about to build the way a competitor would describe theirs; if that sentence fits the modal landing page in the category, restart.

### Typography and color

- Faces with a point of view. The reflex-face list and calibration in [new-work.md](new-work.md) apply here in full.
- A single well-chosen family with committed weight and size contrast beats a timid display-plus-body pair. Modular scale with a ratio of at least 1.25; fluid `clamp()` for headings only.
- Light text on dark grounds: add 0.05–0.1 to line height.
- Persuade and Experience surfaces have permission for the Committed, Full palette, and Drenched color strategies. When the strategy is Committed or Drenched, color carries the brand; do not hedge with neutrals around the edges.
- When a cultural-symbol palette is the obvious pull, reach past it; let the cultural reading come from type, imagery, and copy.

### Imagery

Image-led subjects (restaurants, hotels, travel, fashion, food, photography, hobbies) without imagery read as incomplete, not restrained. When the brief implies imagery, ship imagery: real project assets first; otherwise verified stock photos or a credible canvas, SVG, or WebGL scene. Never colored `<div>` placeholders where a photo belongs.

- Verify every stock URL resolves before you reference it (a web-fetch or browser tool). Without a verification path, use fewer photos you are sure of; guessed IDs ship as broken images.
- Search for the subject's physical object, not the category: "handmade pasta on a scratched wooden table" beats "Italian food".
- One decisive photo beats five mediocre ones.
- Alt text is part of the voice: "Coastal fettuccine, hand-cut, served on the terrace" beats "pasta dish".

### Bans on top of the craft floor

- Large rounded-corner icons above every heading.
- All-caps body copy. Caps are for short labels and headings only.
- A family picked by reflex rather than voice.
- Editorial-magazine aesthetics (display serif, italic, drop caps, broadsheet grid) on a brief that is not magazine-shaped.

### Permissions

- Ambitious first-load motion that earns its place: one orchestrated sequence, not fade-on-scroll for every section.
- Single-purpose viewports: one dominant idea per fold, long scroll, deliberate pacing.
- Art direction per section when the narrative demands it; consistency of voice beats consistency of treatment.

## Operate

**Operate:** the visitor completes a task. App UI, dashboards, editors, admin, settings, tools. Scanability, consistency, native expectations, and the real usage scene outrank expression. Brand lives in precise details.

Someone who uses tools like this one should know where everything is before they notice the world. The world lends four things and only these: type, palette, density, and one signature move. It never supplies the layout, the navigation model, or the controls. Colour is part of the world's contribution, and it does real jobs: a committed palette for the shell (a coloured rail or header, a tinted ground), state colours, data series, selection, and the signature move. A grey screen with one accent colour is the category default without the category's polish, not restraint.

Read every candidate direction through that limit before you propose it. A world taken from a tool or instrument the audience operates (a terminal, a scope, a control panel, a cockpit) or from a fictional interface comes back as a costume of that tool on a working screen: take from it only what transfers as type, palette, density, and a signature move, or replace the candidate.

Write each direction's first viewport as the product's shell first: the navigation, the work areas and what each is for, the data the visitor reads first and its states, and then where the signature move lives. Expression may never obscure the task, state, or familiar affordance. Name the signature move concretely, so the comp and the build can find it: service health drawn as a transit map, a schedule set in a timetable's column rhythm. A direction whose world shows up only as a colour scheme has not found its move yet. Product clarity includes reading as a working product of this category.

### The product slop test

Familiarity is often a feature here. The test is whether a category-fluent user can trust the interface immediately or must pause at every subtly-off component.

Product UI's failure mode isn't flatness, it's strangeness without purpose: over-decorated buttons, mismatched form controls, gratuitous motion, display fonts where labels should be, invented affordances for standard tasks. The bar is earned familiarity. The tool should disappear into the task.

### Typography

- **One family is often right.** Product UIs don't need display/body pairing. A well-tuned sans carries headings, buttons, labels, body, data.
- **Fixed rem scale, not fluid.** Clamp-sized headings don't serve product UI. Users view at consistent DPI, and a fluid h1 that shrinks in a sidebar looks worse, not better.
- **Tighter scale ratio.** 1.125–1.2 between steps is typical. More type elements here than on brand surfaces; exaggerated contrast creates noise.
- **Line length still applies for prose** (65–75ch). Data and compact UI can run denser; tables at 120ch+ are fine.

### Color

Product defaults to Restrained. A single surface can earn Committed (a dashboard where one category color carries a report, an onboarding flow with a drenched welcome screen), but Restrained is the floor.

- State-rich semantic vocabulary: hover, focus, active, disabled, selected, loading, error, warning, success, info. Standardize these.
- Accent color used for primary actions, current selection, and state indicators only, not decoration.
- A second neutral layer for sidebars, toolbars, and panels (slightly cooler or warmer than the content surface).

### Layout

- Responsive behavior is structural (collapse sidebar, responsive table, breakpoint-driven columns), not fluid typography.

### Components

Every interactive component has: default, hover, focus, active, disabled, loading, error. Don't ship with half of these.

- Skeleton states for loading, not spinners in the middle of content.
- Empty states that teach the interface, not "nothing here."
- Consistent affordances across the surface. Same button shape. Same form-control vocabulary. Same icon style.
- Overlays escape their container. An absolutely positioned dropdown inside an `overflow: hidden` or `overflow: auto` ancestor gets clipped; reach for `<dialog>`, the popover API, `position: fixed`, or a portal.

### Motion

- 150–250 ms on most transitions. Users are in flow; don't make them wait for choreography.
- Motion conveys state, not decoration. State change, feedback, loading, reveal: nothing else.
- No orchestrated page-load sequences. Product loads into a task; users don't want to watch it load.

### Product constraints

- Decorative motion that doesn't convey state.
- Inconsistent component vocabulary across screens. If the "save" button looks different in two places, one is wrong.
- Display fonts in UI labels, buttons, data.
- Reinventing standard affordances for flavor (custom scrollbars, weird form controls, non-standard modals).
- Heavy color or full-saturation accents on inactive states.
- Modal as first thought. Modals are usually laziness. Exhaust inline / progressive alternatives first.

### Product permissions

Product can afford things brand surfaces can't.

- System fonts and familiar sans defaults.
- Standard navigation patterns: top bar + side nav, breadcrumbs, tabs, command palettes.
- Density. Tables with many rows, panels with many labels, dense information when users need it.
- Consistency over surprise. The same visual vocabulary screen to screen is a virtue; delight is saved for moments, not pages.

## Read

**Read:** the visitor understands something. Docs, articles, guides, help, changelogs. Structure for comprehension, then make the reading experience worth staying in.

The reader's question leads, and comprehension and wayfinding stay intact at every step. Documentation reads as documentation, a guide as a guide, an article as an article, a changelog as a changelog. The world owns the frame and serves the column. The frame is the masthead, the navigation rail, the ground, the title and section openers, and the way code, tables, and callouts are set: there the world's palette, type, and signature move commit fully, so the page could belong to no other product. The reading column inside it stays calm: a reading face, real contrast, a real measure, nothing performing behind the text. The world never supplies the reading order or replaces the navigation with something a reader has to learn. Documentation still reads as documentation, a guide as a guide, an article as an article.

Candidates from the world's own publishing traditions transfer best: reference books, type specimens, timetables, field guides, technical manuals, scholarly apparatus, a newspaper's wayfinding. A tool, instrument, or fictional interface from the audience's world comes back as a costume on a page meant for reading: take from it only what transfers as type, palette, density, and a signature move, or replace the candidate.

Write each direction's first viewport as the document's shell first: the navigation and where the reader stands in it, the title and the opening that answers or frames the reader's question, the reading column, and the way forward (contents, section headings, next and previous). Then name where the world owns the frame and where the signature move lives: a masthead, a coloured rail, a running head, a margin system, a numbering scheme, a way of setting code or tables. Product clarity includes how fast a reader finds and understands the answer.

Read surfaces use the Operate typography and consistency rules above; prose measure and navigation matter more than component density. Body text sits near 16px at a 60–75 character measure in a reading face with real contrast; monospace is for code, parameters, and small labels, never the running text.

## First-viewport sketches per mode

When [new-work.md](new-work.md) calls for an HTML or ASCII sketch of the first viewport, sketch what the mode needs:

- **Persuade:** the offer made intelligible, the primary action in its working form, and the one proof only this product can show. The world carries the page; it is never a poster with no working parts.
- **Operate:** the product shell first: navigation, work areas and what each is for, the data read first and its states, then where the signature move lives. Standard controls only; realistic data with units and one state worth seeing (an alert, an empty filter result).
- **Read:** the document as the reader meets it: where they stand in the navigation, the title and the opening that answers their question, the reading column, and the way forward.
- **Experience:** the work itself in the first viewport, with the interface receding.
