# Animate

> **Additional context needed**: performance constraints.

Use motion to explain state, relationship, and hierarchy, or to create one authored moment the surface has earned. Decoration without purpose is animation debt.

---

## Contents

- Mode
- Find the job
- Set the motion thesis
- Choose material by meaning
- Shape the motion
- Timing and easing
- Components
- Implement to the runtime
- Accessibility and control
- Never
- Verify
- Reference

## Mode

- **Persuade + Experience:** motion may carry the voice. Prefer one rehearsed focal sequence to repeated section reveals.
- **Operate + Read:** motion serves feedback, state, and continuity. Keep routine transitions fast and do not make users wait through page-load choreography.

## Find the job

Inspect the existing motion language, interaction states, target devices, and performance budget. Find only the places where motion would:

- acknowledge an action;
- make a state change or spatial relationship legible;
- preserve continuity through navigation or layout change;
- direct attention at a meaningful moment;
- embody the selected visual world.

Frequency decides before taste. An action used 100+ times a day or triggered from the keyboard (command palette, shortcuts) gets no animation. One used tens of times a day gets fast, near-imperceptible feedback or none. Occasional overlays get standard motion. Rare moments (first use, completion) hold the delight budget.

Ask only when a material constraint cannot be inferred. Do not animate a static area merely because it exists.

## Set the motion thesis

Write a short plan before implementation:

- **Focal moment:** the one sequence or interaction that deserves authorship, if any.
- **Continuity:** the state, layout, or navigation changes that need explanation.
- **Feedback:** the controls and outcomes that need acknowledgment.
- **Budget:** which effects may be expensive and how often they run.

The focal moment must come from this product and surface concept. A generic fade-and-rise, hover lift, parallax layer, or scroll reveal is not a thesis.

## Choose material by meaning

Transform and opacity are reliable foundations, not the entire palette. Choose properties for what the transition communicates:

- **Continuity and relationship:** shared-element motion, FLIP-style transforms, view transitions, or deliberate spatial movement.
- **Focus and depth:** bounded blur, filter, backdrop, light, or shadow changes.
- **Reveal and composition:** masks, clip paths, cropping, or controlled occlusion.
- **Material and energy:** color, gradient position, texture, distortion, or shader effects when the world and runtime support them.
- **State and feedback:** the smallest change that makes cause and result unmistakable.

Do not stack techniques for spectacle. One strong material idea, carried through the focal sequence and quiet supporting states, is usually enough.

Sibling stagger is appropriate when a list appears as a list. Cap the total delay, and never reinterpret every scrolled section as a staggered list.

## Shape the motion

- **Nothing appears from nothing.** Enter from `scale(0.95–0.97)` plus opacity, never `scale(0)`.
- **Origin at the trigger.** Popovers, menus, and tooltips grow from the element that opened them (`transform-origin` on the trigger side). Modals are not anchored and stay centered. For SVG, set `transform-box: fill-box` so the origin is the shape, not the canvas.
- **Exit the way it entered.** A drawer leaves through its edge; a swiped toast leaves in the swipe direction.
- **Retarget, don't restart.** Anything a user can trigger twice in a second (toggles, toasts, hover) uses transitions, which continue from the current value; keyframes restart from zero.
- **Gate hover motion** with `@media (hover: hover) and (pointer: fine)`; touch fires sticky hovers on tap.
- **Distance and size set duration.** A larger element or a longer path takes longer; a small one moving far feels slow.

## Timing and easing

Timing should express distance and consequence:

| Duration | Typical use |
|---|---|
| 100–150 ms | immediate feedback |
| 150–300 ms | routine state change |
| 300–500 ms | layout, overlay, or view transition |
| 500–800 ms | a deliberately authored focal entrance |

Exit faster than entrance. Long feedback feels like latency.

Choose the curve by what moves:

| Motion | Easing |
|---|---|
| Entering, or leaving an overlay | ease-out (decelerating; `--ease-out-*` tokens) |
| Moving or morphing on screen | ease-in-out |
| Hover and color change | `ease` or ease-out, short |
| Progress, constant motion | `linear` |
| Leaving the screen for good (dismissed drawer, cleared toast) | ease-in, short; the user is no longer watching it |

Never ease-in an entrance or feedback: it delays the moment the user watches. Do not use bounce or elastic curves by reflex.

**Springs** fit drag, gestures, and motion the user can interrupt or reverse, because they carry velocity through the change. Keep bounce at 0.1–0.3 and reserve it for drag and playful moments. CSS `linear()` can draw a spring-shaped curve for a fixed duration, but it does not carry velocity.

## Components

Starting points, not a house style; the design context and its tokens win.

| Component | Duration | Shape | Reduced motion |
|---|---|---|---|
| Button press | 100–160 ms | `:active` `scale(0.97)`, ease-out | keep, or color only |
| Tooltip | 125–200 ms | from trigger, `scale(0.97)`; once one is open, neighbours open instantly | opacity |
| Dropdown, popover, menu | 150–250 ms | from trigger, `scale(0.95)` + opacity | opacity |
| Modal, dialog | 200–300 ms | centered, `scale(0.96)` + opacity, backdrop fades with it | opacity |
| Drawer, sheet | 250–400 ms | `translate` 100% from its edge, back to the same edge | opacity or instant |
| Toast | 200–400 ms | from its stack edge, transitions not keyframes | opacity |
| Accordion | 150–250 ms | grid rows `0fr` → `1fr` (snippet below) | instant |
| Tabs | 150–250 ms | indicator slides with ease-in-out; panels crossfade | indicator jumps |
| Skeleton | 1.5–2 s loop | gentle opacity pulse; crossfade to content in ≤200 ms | static |
| Route change | 200–400 ms | View Transition; shared element when continuity matters | crossfade or none |

Dialog or popover from `display: none`, with entry and exit in CSS only:

```css
dialog {
  opacity: 0;
  transform: scale(0.96);
  transition:
    opacity var(--duration-base) var(--ease-out-quart),
    transform var(--duration-base) var(--ease-out-quart),
    overlay var(--duration-base) allow-discrete,
    display var(--duration-base) allow-discrete;
}
dialog[open] { opacity: 1; transform: none; }
@starting-style {
  dialog[open] { opacity: 0; transform: scale(0.96); }
}
```

`overlay` is Chromium-only; elsewhere the exit is cut short, which is acceptable.

Accordion to an unknown height without animating `height`:

```css
.panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows var(--duration-base) var(--ease-out-quart); }
.panel[data-open] { grid-template-rows: 1fr; }
.panel > * { overflow: hidden; }
```

## Implement to the runtime

- Use CSS transitions and keyframes for declarative state and bounded sequences.
- Use Web Animations API or the project's existing motion library for interruption, sequencing, and dynamic values.
- Use View Transitions or shared-element techniques when continuity across states is the point.
- Use scroll-driven motion only when the scroll relationship itself carries meaning, with a robust fallback.
- Start scroll-triggered reveals with Intersection Observer and unobserve after the first run.
- Do not add a dependency for an effect the existing stack can express cleanly.

Modern CSS removes most reasons for a library (support as of October 2026; check MDN for newer features):

- `@starting-style` + `transition-behavior: allow-discrete` (all browsers): entry and exit from `display: none` for dialogs, popovers, and inserted elements.
- `linear()` easing (all browsers): spring- or overshoot-shaped curves for fixed durations.
- View Transitions: same-document `document.startViewTransition()` in all browsers; cross-document `@view-transition { navigation: auto; }` in Chromium and Safari 18.2+, not Firefox. Give every shared element a unique `view-transition-name` and feature-detect.
- Scroll-driven `animation-timeline: scroll()` / `view()`: Chromium and Safari 26+, Firefox not by default. Wrap in `@supports (animation-timeline: view())` and keep the static state complete.
- `interpolate-size: allow-keywords` (Chromium only): animating to `height: auto` as an enhancement over the grid-rows technique.

Keep content visible in the default state so failed scripts do not hide the page. Avoid casually animating layout-driving properties such as `width`, `height`, `top`, `left`, and margins; use FLIP, transforms, or grid techniques when appropriate. Bound blur, filter, shadow, canvas, and shader work to isolated regions, and keep animated blur at or below about 20px. Apply `will-change` only during known animation. Measure on target viewports and devices rather than assuming transform means fast.

## Accessibility and control

Respect autoplay and sound preferences. Any nonessential loop must stop when offscreen or hidden.

Every web animation needs a `prefers-reduced-motion` path with an intentional alternative. Remove or reduce spatial movement while preserving opacity, color, and state transitions that carry meaning. Reduced motion means fewer and gentler animations, not disabling all motion; feedback that confirms an action should remain legible.

- **Vestibular triggers** go first under reduced motion: parallax, zooming or scaling large areas, spinning, full-viewport slides, and scroll-linked movement.
- **No flashing** more than three times per second (WCAG 2.3.1).
- **Autoplaying motion longer than 5 seconds** next to other content needs a pause, stop, or hide control (WCAG 2.2.2).
- **Script-driven motion** reads the preference too: `matchMedia('(prefers-reduced-motion: reduce)')` with a change listener, or the library's own hook (see Reference).

## Never

- Hide content until an animation or script runs.
- Animate keyboard-triggered or 100+/day actions.
- `transition: all`, or casual animation of `width`, `height`, `top`, `left`, or margins.
- Enter from `scale(0)`, ease-in an entrance, or reach for bounce or elastic by reflex.
- Keyframes on rapidly re-triggered UI; they restart instead of retargeting.
- Scroll listeners for reveals, or reveals that replay on every scroll-by.
- Stagger without a cap, or stagger that blocks interaction.
- Ship an animation without a reduced-motion path, or an autoplay loop without a pause control.

## Verify

- The focal motion is specific to the selected world and surface.
- Every supporting animation explains feedback, state, or relationship.
- Interruption and repeated use behave correctly.
- Desktop, mobile, and keyboard paths remain usable.
- The `prefers-reduced-motion` path reduces movement without erasing meaningful feedback or state changes.
- Expensive effects stay smooth on the target device.
- Removing an animation would lose meaning or authored character, not merely decoration.

How to check:

- Emulate reduced motion (Playwright `page.emulateMedia({ reducedMotion: 'reduce' })` or DevTools Rendering) and inspect the alternative.
- Trigger each animation twice quickly and reverse it mid-flight: it retargets without a jump or restart.
- Judge curves at 2–5× slower in the DevTools Animations panel, or frame by frame; take screenshots only after motion settles.
- Record a Performance trace at the target viewport with CPU throttling; look for dropped frames and layout or paint work during the animation.

When motion earns its place, hand off to `/ui-ux-expertise polish` for the final pass.

## Reference

### Motion tokens

Extend the project's existing motion tokens before adding these.

```css
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);   /* smooth */
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);  /* slightly snappier */
--ease-out-expo:  cubic-bezier(0.16, 1, 0.3, 1);   /* confident, decisive */
--ease-in-out:    cubic-bezier(0.65, 0, 0.35, 1);  /* movement within the screen */
--ease-in:        cubic-bezier(0.5, 0, 0.75, 0);   /* leaving the screen for good */

--duration-fast:  120ms;  /* feedback */
--duration-base:  200ms;  /* routine state change */
--duration-slow:  350ms;  /* layout, overlay, view */
--duration-focal: 600ms;  /* one authored entrance */
```

Exit at roughly 75% of the entrance duration. Bounce and elastic curves (`cubic-bezier` values outside 0-1) read as dated and draw attention to the animation itself.

### Stagger

Drive list stagger from an index variable and cap the total: `transition-delay: calc(min(var(--i), 8) * 40ms)`. Past about eight items the tail feels like waiting.

### Stacks

- **Tailwind:** put movement behind `motion-safe:` and the quiet alternative behind `motion-reduce:`. Name the properties (`transition-transform`, `transition-opacity`, `transition-[transform,opacity]`). In v4, `--ease-*` and `--animate-*` in `@theme` generate `ease-*` and `animate-*` utilities; there is no duration namespace, so use `duration-200` or `duration-(--duration-base)`.
- **React with Motion:** set `<MotionConfig reducedMotion="user">` at the root, or branch on `useReducedMotion()` for custom values. Use springs for gestures and layout animation, CSS for the rest.
- **Vue:** `<Transition>` and `<TransitionGroup>` classes use the same tokens and the CSS `prefers-reduced-motion` query.
- **Svelte:** zero the distance of `fly`, `slide`, and `scale` when `prefersReducedMotion.current` from `svelte/motion` is true (Svelte 5.7+).

### Perceived performance

- Respond within about 80 ms so an action feels instant: the feedback must start that fast, even when it takes 100–150 ms to finish.
- Start the transition while work is in flight (skeletons, progressive images) instead of waiting for completion.
- Optimistic UI suits low-stakes actions (like, follow, toggle); avoid it for payments and destructive operations, and roll back visibly on failure.
- For spinners and skeletons, delay showing them by about 150-300 ms and keep them visible at least 300-500 ms once shown, so fast responses do not flicker.

### Reduced motion example

Replace spatial movement with a quiet alternative instead of killing every transition:

```css
.panel { transition: transform 300ms var(--ease-out-quart), opacity 300ms var(--ease-out-quart); }

@media (prefers-reduced-motion: reduce) {
  .panel { transition: opacity 150ms linear; transform: none; }
}
```

```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
reduce.addEventListener('change', () => applyMotion(!reduce.matches));
```
