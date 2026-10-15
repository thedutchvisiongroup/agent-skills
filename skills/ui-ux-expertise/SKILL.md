---
name: ui-ux-expertise
description: Designs, builds, critiques, and refines frontend interfaces to an opinionated UI/UX craft standard. Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, typeset, lay out, or otherwise improve web UI, including landing pages, marketing sites, dashboards, app screens, Filament admin panels, forms, settings, onboarding, empty states, and components. Covers visual hierarchy, information architecture, layout and spacing, typography, color, motion, UX copy, accessibility (WCAG 2.2), responsive behavior, interaction states, design systems and tokens, and the anti-patterns of generic AI-generated design. Also use for bland designs that need to become bolder, loud designs that should become quieter, or ambitious effects that should feel technically extraordinary. Not for backend-only work or native mobile apps.
license: Apache-2.0
user-invocable: true
argument-hint: "[shape · critique|audit · polish|bolder|quieter|distill|harden|onboard · animate|colorize|typeset|layout|delight|overdrive · clarify|adapt|optimize · init|document|extract] [target]"
---

# UI/UX Expertise

Design and build interfaces the way an award-winning design director would: production-grade code, a clear point of view, deep care for the people using it, and exceptional craft. Safe, timid, category-default output is the failure this skill exists to prevent.

`<skill-dir>` below means the directory that contains this SKILL.md. Reference files live in `<skill-dir>/references/`, the detector in `<skill-dir>/scripts/detect.py`.

## When NOT to use

- Backend-only work, APIs, data pipelines, CLI tools without a UI.
- Native mobile apps (SwiftUI, Jetpack Compose, Flutter, React Native screens); this skill covers web interfaces only.
- Pure copy or content strategy with no interface attached.

## Setup (REQUIRED, in order)

### 1. Clarification gate

Before you change anything, confirm with the user, two or three questions per round at most (use `AskUserQuestion` in Claude Code, `question` in OpenCode, otherwise ask and wait):

- **Target and boundaries:** which page, route, or component, and what must stay untouched.
- **Mode:** propose Persuade, Operate, Read, or Experience from the surface (see Modes below) and let the user confirm.

When the request already names the target or mode, restate it in one line for confirmation instead of asking again. A trivial, unambiguous fix (one button label, one spacing error) needs only a one-line confirmation of what you will change. A command's own questions (shape, new-work, critique) come on top of this gate, never instead of it.

```
STOP. Before the first edit:
- [ ] Target and what stays untouched are confirmed
- [ ] Mode is confirmed (or the fix is trivial and confirmed in one line)
- [ ] Design context is confirmed for this session (step 2)
```

### 2. Design context discovery (once per session)

Design and product documentation has no fixed name or place. Search for it once per session, before the first design decision:

1. Look for design- and product-related directories and files: `docs/`, `design/`, `.design/`, `brand/`, files such as `DESIGN.md`, `PRODUCT.md`, `design-system*`, `style-guide*`, `brand*`, `tokens*`. Then filter all Markdown files by design and product terms (design system, brand, typography, palette, color, tokens, components, persona, audience, product principles).
2. Note the token sources in code too: Tailwind `@theme` or `tailwind.config.*`, CSS custom properties on `:root`, theme files, a Filament panel theme.
3. **Files found:** list them and ask the user to confirm they may be used as the design context.
4. **Nothing found:** ask whether a general design exists and where.
5. **No design at all:** derive the visual system from the existing code (tokens, components, recurring values). If the code yields nothing either: for new work, propose one direction and offer a neutral grayscale baseline as the alternative ([references/new-work.md](references/new-work.md)); for a small fix, use the grayscale baseline or what the code implies.

The confirmed result is the **design context** for this session; every reference uses that term. It is optional input, never a prerequisite: missing files never block work, and no file is written unless the user asks (`init`, `document`).

### 3. Load the playbook

- A command (explicit or clearly implied): read `references/<command>.md` before acting. It defines the flow; without it you will skip steps the user expects.
- A request to build something new, with or without a command: read [references/new-work.md](references/new-work.md).
- Then read the matching part of [references/modes.md](references/modes.md) for the confirmed mode.
- Inspect the target and the incumbent visual truth in code (at least one stylesheet or token file and one representative component or page) before editing.

### 4. Read the craft floor before editing

Immediately before any UI edit, including small refinements, read [references/craft-floor.md](references/craft-floor.md). Do not load it for planning-only work.

## How to design

- **The brief wins.** Honor pinned aesthetics, eras, materials, fonts, and palettes even when they conflict with a calibration warning. Redirecting a clear brief toward your own taste is failure.
- **Refinement preserves; redesign replaces.** Refinement keeps the incumbent identity, behavior, copy, and everything outside scope; ask before replacing factual copy or adding claims. Redesign keeps product truth, content, function, and constraints, but treats the old look as evidence, not authority. Never split the difference into polish on a discarded look.
- **Visual authority is evidence, not a filename.** A coherent identity in code counts even when no design-system file exists.
- **Loaded symbols stay out of the decoration.** A subject's world does not license emblems tied to militarism, supremacy, or hate movements as motifs, badges, or ornament; reach for that world's neutral forms instead.
- **Go all out, then stop.** Deliver the complete thing (except assets only the user can provide), then verify in bounded passes: build fully, inspect once in a batched round (desktop and mobile together), fix everything that round shows in one batch, confirm with at most one more round, and stop. Open-ended self-QA costs the user money and does worse than a fresh reviewer.
- **Truth binds claims.** Author illustrative content at full fidelity and label it synthetic; never invent prices, customers, benchmarks, or capabilities.

## Modes

The mode names what the visitor's success looks like on this surface. Choose it from the requested surface, not the product.

| Mode | The visitor… | Surfaces | Leads with |
|---|---|---|---|
| **Persuade** | decides and acts | landing pages, marketing, campaigns, pricing | earned attention, a working action, real imagery |
| **Operate** | completes a task | app UI, dashboards, admin, settings, tools | scanability, consistency, standard controls |
| **Read** | understands something | docs, articles, guides, help, changelogs | comprehension and wayfinding |
| **Experience** | is inside the work | portfolios, galleries, showcases | the artifact itself; the interface recedes |

Details per mode: [references/modes.md](references/modes.md).

## Commands

Invoke as `/ui-ux-expertise <command> [target]`, or describe the intent in words.

| Command | Category | Description | Reference |
|---|---|---|---|
| `shape [feature]` | Build | Plan UX/UI and return a confirmed brief, no code | [shape.md](references/shape.md) |
| `init` | Build | Capture product context in a file, on request only | [init.md](references/init.md) |
| `document` | Build | Record the existing visual system in a design-system file | [document.md](references/document.md) |
| `extract [target]` | Build | Pull reusable tokens and components into the system | [extract.md](references/extract.md) |
| `critique [target]` | Evaluate | UX design review with heuristic scoring | [critique.md](references/critique.md) |
| `audit [target]` | Evaluate | Technical quality checks (a11y, performance, theming, responsive) | [audit.md](references/audit.md) |
| `polish [target]` | Refine | Final quality pass before shipping | [polish.md](references/polish.md) |
| `bolder [target]` | Refine | Amplify safe or bland designs | [bolder.md](references/bolder.md) |
| `quieter [target]` | Refine | Tone down aggressive or overstimulating designs | [quieter.md](references/quieter.md) |
| `distill [target]` | Refine | Strip to essence, remove complexity | [distill.md](references/distill.md) |
| `harden [target]` | Refine | Production-ready: errors, i18n, edge cases | [harden.md](references/harden.md) |
| `onboard [target]` | Refine | First-run flows, empty states, activation | [onboard.md](references/onboard.md) |
| `animate [target]` | Enhance | Purposeful animation and motion | [animate.md](references/animate.md) |
| `colorize [target]` | Enhance | Strategic color for monochrome or flat UIs | [colorize.md](references/colorize.md) |
| `typeset [target]` | Enhance | Typography hierarchy and faces | [typeset.md](references/typeset.md) |
| `layout [target]` | Enhance | Spacing, rhythm, and visual hierarchy | [layout.md](references/layout.md) |
| `delight [target]` | Enhance | Personality and memorable touches | [delight.md](references/delight.md) |
| `overdrive [target]` | Enhance | Technically extraordinary effects | [overdrive.md](references/overdrive.md) |
| `clarify [target]` | Fix | UX copy, labels, and error messages | [clarify.md](references/clarify.md) |
| `adapt [target]` | Fix | Different screen sizes, devices, and input methods | [adapt.md](references/adapt.md) |
| `optimize [target]` | Fix | Diagnose and fix UI performance | [optimize.md](references/optimize.md) |

Building something new has no command: "build a landing page", "make this settings screen", or "redesign the dashboard" follow [references/new-work.md](references/new-work.md).

### Routing

1. **No argument** ("what should I do?"): gather cheap signals yourself: changed files in `git status`, whether a design context exists, and optionally one detector run over the changed markup and style files. Lead with the 2-3 highest-value commands, each with a one-line reason from those signals and the exact command to type, then show the table above grouped by category. Never auto-run a command.
   - Coherent UI but no design-system file → `document`.
   - Never critiqued → `critique <surface>`.
   - Changes concentrated in one surface → `audit` or `polish` scoped to those files.
   - Detector hits of one family → the matching command (eyebrows or gradient text → `quieter` / `typeset`; flat gray palette → `colorize`; many a11y hits → `audit`).
2. **First word is a command:** load its reference and follow it. Everything after the command name is the target.
3. **Intent clearly maps to one command** ("fix the spacing" → `layout`, "rewrite this error message" → `clarify`, "the colors feel flat" → `colorize`): load that reference and proceed as if invoked. If two commands fit, ask once which.
4. **A request to build or redesign:** [references/new-work.md](references/new-work.md).
5. **Anything else:** general design work under Setup, the craft floor, and the mode reference.

"Bolder" or "safer" said while a direction proposal is still open steers that proposal, not the `bolder` command.

## Verification

- **Screenshots when available.** Use a browser or screenshot tool (browser extension, Playwright, built-in browser) for the batched inspection round. Without one, say plainly that the render was not inspected and ask the user to check it.
- **Detector.** `python3 <skill-dir>/scripts/detect.py [--json] <paths>` scans HTML, CSS, template, and component files (including Tailwind classes) for the mechanical anti-patterns. Exit 0 clean, 1 findings, 2 usage error. Every hit needs verification in context; rule ids are explained in [references/anti-patterns.md](references/anti-patterns.md). It never replaces looking at the render.

## Delegated work

A delegated subagent cannot ask the user. For it, the confirmed answers in its delegation contract (target, boundaries, mode, design context) satisfy Setup steps 1 and 2; anything missing or contradictory goes back to the coordinator as `NEEDS_CONTEXT`, never as a guess.

When the work runs under the `using-subagents` skill:

- Write the confirmed brief or direction contract to `design-brief.md` in the approved run directory, so implementers and reviewers receive it by path. Without a run, it stays in the conversation.
- Delegated implementers load this skill for UI tasks.
- Recommend the optional `ui-reviewer` agent for an independent, visual-only review of rendered results; it needs screenshots or a browser. Whether to schedule it is the coordinator's decision under `using-subagents`. Its method is [references/visual-review.md](references/visual-review.md).

## Reference index

| Reference | Read when |
|---|---|
| [new-work.md](references/new-work.md) | Building a new surface or replacing a visual identity |
| [modes.md](references/modes.md) | After the mode is confirmed (Setup step 3) |
| [craft-floor.md](references/craft-floor.md) | Immediately before any UI edit |
| [interaction-design.md](references/interaction-design.md) | States, focus, forms, overlays, keyboard, gestures |
| [stacks.md](references/stacks.md) | Applying decisions in Tailwind, Filament, Blade/Twig/Jinja, component frameworks |
| [anti-patterns.md](references/anti-patterns.md) | Interpreting detector output; manual anti-pattern checks |
| [visual-review.md](references/visual-review.md) | A visual review of rendered results (also the `ui-reviewer` method) |
| `references/<command>.md` | Running that command |

## Before reporting done

```
STOP. Verify:
- [ ] The clarification gate and design-context confirmation happened
- [ ] The craft floor was read before the first edit, and its Refuse list holds in the result
- [ ] One batched inspection round ran (or the missing render is stated plainly)
- [ ] Detector findings on changed files are fixed or explained
- [ ] The report names what was verified, what was not, and any illustrative content to replace
```

Derived from [Impeccable](https://github.com/pbakaus/impeccable) v4.5.2 by Paul Bakaus (Apache-2.0), adapted without its CLI engine, live mode, hooks, and image generation.
