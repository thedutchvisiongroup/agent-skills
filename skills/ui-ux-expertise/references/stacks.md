# Stack notes

How to apply the design rules in the stacks this skill usually meets. Follow the project's own conventions first; these notes only say where design decisions belong in each stack. For framework-specific APIs, consult current documentation (or a dedicated skill such as `filamentphp-development`) instead of memory.

## Tailwind CSS

- **Tokens live in the theme, not in class lists.** Tailwind v4 declares them in CSS `@theme { --color-*: …; --font-*: …; }`; v3 in `tailwind.config.*` under `theme.extend`. Add a token when a value repeats; an arbitrary value (`text-[13px]`, `z-[9999]`) is a one-off that the system should own.
- **Read the class list as design.** `uppercase tracking-widest text-xs` above a heading is the banned eyebrow; `bg-clip-text` with a gradient is gradient text; `border-l-4` with an accent color is the side stripe; `transition-all`, `animate-bounce`, and `backdrop-blur` are the reflex versions of motion and depth. The detector flags these.
- **States are classes too.** Every interactive element needs `hover:`, `focus-visible:`, `active:`, and `disabled:` variants; `focus:outline-none` without a `focus-visible:` replacement removes keyboard focus.
- **Dark mode** follows the project's strategy (`dark:` variant with `class` or media). Redefine semantic tokens for dark instead of sprinkling `dark:` overrides per element.
- **Repeated class bundles** become a component or partial in the template layer. Use `@apply` sparingly for genuinely shared primitives.

## Filament (Laravel)

- Filament panels are Operate surfaces. Familiarity with Filament's own components is a feature; the design work is theming, density, copy, and states, not reinventing controls.
- **Theme through the panel, not by overriding internals.** Brand colors go through `$panel->colors([...])`. Deeper styling goes in a custom theme (`php artisan make:filament-theme`, registered with `$panel->viteTheme(...)`). Never edit vendor views or fight component markup with high-specificity CSS.
- Use Filament's schema components (sections, tabs, grids, infolists) for layout and its notification, modal, and action APIs for feedback before building custom ones. Empty states, table states, and validation copy still deserve full attention.
- Load the `filamentphp-development` skill for version-specific APIs.

## Blade, Twig, Jinja, and other template engines

- Repeated UI becomes a reusable unit: a Blade component (`<x-button>`), a Twig/Jinja macro or include, a Nunjucks macro. One authoritative implementation per pattern keeps states and spacing consistent across pages.
- Keep design values in CSS tokens, not in template logic. Templates choose variants (`variant="primary"`), they do not compute colors or spacing.
- Escape output by default (`{{ }}` in Blade, Twig, and Jinja with autoescape on). Raw output (`{!! !!}`, `|raw`, `|safe`) is a security decision, never a styling shortcut.
- Long and missing content is real in server-rendered pages: test partials with empty collections, very long names, and translated strings.

## Component frameworks (React, Vue, Svelte, Astro)

- Variants are props on one component, not copies. States (`loading`, `disabled`, `error`) are part of the component's API.
- Inputs must keep focus and value across hydration; URL state (filters, tabs, pagination) belongs in the router, not only in local state.
- Prefer CSS for motion; reach for the Web Animations API or a library (Motion, GSAP) only for sequences CSS cannot express.
- Server components and islands ship less JavaScript; keep interactivity where interaction actually happens.

## Plain HTML and CSS

- Custom properties on `:root` are the token system. Keep one stylesheet entry point, `<meta name="viewport" content="width=device-width, initial-scale=1">` without zoom restrictions, and semantic elements (`<header>`, `<nav>`, `<main>`, `<button>`, `<a href>`).
- Self-host chosen fonts with `@font-face` and `font-display`, and preload only the critical weight.
