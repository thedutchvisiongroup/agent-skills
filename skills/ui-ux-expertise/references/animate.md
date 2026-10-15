> **Additional context needed**: performance constraints.

Use motion to explain state, relationship, and hierarchy, or to create one authored moment the surface has earned. Decoration without purpose is animation debt.

---

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

## Timing and easing

Timing should express distance and consequence:

| Duration | Typical use |
|---|---|
| 100–150 ms | immediate feedback |
| 150–300 ms | routine state change |
| 300–500 ms | layout, overlay, or view transition |
| 500–800 ms | a deliberately authored focal entrance |

Exit faster than entrance. Use natural deceleration such as `cubic-bezier(0.16, 1, 0.3, 1)` for confident arrivals; do not use bounce or elastic curves by reflex. Long feedback feels like latency.

## Implement to the runtime

- Use CSS transitions and keyframes for declarative state and bounded sequences.
- Use Web Animations API or the project's existing motion library for interruption, sequencing, and dynamic values.
- Use View Transitions or shared-element techniques when continuity across states is the point.
- Use scroll-driven motion only when the scroll relationship itself carries meaning, with a robust fallback.
- Do not add a dependency for an effect the existing stack can express cleanly.

Keep content visible in the default state so failed scripts do not hide the page. Avoid casually animating layout-driving properties such as `width`, `height`, `top`, `left`, and margins; use FLIP, transforms, or grid techniques when appropriate. Bound blur, filter, shadow, canvas, and shader work to isolated regions. Apply `will-change` only during known animation. Measure on target viewports and devices rather than assuming transform means fast.

## Accessibility and control

Respect autoplay and sound preferences. Any nonessential loop must stop when offscreen or hidden.

Every web animation needs a `prefers-reduced-motion` path with an intentional alternative. Remove or reduce spatial movement while preserving opacity, color, and state transitions that carry meaning. Reduced motion means fewer and gentler animations, not disabling all motion; feedback that confirms an action should remain legible.

## Verify

- The focal motion is specific to the selected world and surface.
- Every supporting animation explains feedback, state, or relationship.
- Interruption and repeated use behave correctly.
- Desktop, mobile, and keyboard paths remain usable.
- The `prefers-reduced-motion` path reduces movement without erasing meaningful feedback or state changes.
- Expensive effects stay smooth on the target device.
- Removing an animation would lose meaning or authored character, not merely decoration.

When motion earns its place, hand off to `/ui-ux-expertise polish` for the final pass.

## Reference

### Easing tokens

```css
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);   /* smooth */
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);  /* slightly snappier */
--ease-out-expo:  cubic-bezier(0.16, 1, 0.3, 1);   /* confident, decisive */
```

Exit at roughly 75% of the entrance duration. Bounce and elastic curves (`cubic-bezier` values outside 0-1) read as dated and draw attention to the animation itself.

### Stagger

Drive list stagger from an index variable and cap the total: `transition-delay: calc(min(var(--i), 8) * 40ms)`. Past about eight items the tail feels like waiting.

### Implementation preference

- CSS transitions and keyframes first, then the Web Animations API, then a library (Motion, GSAP) for sequences CSS cannot express.
- List the properties you animate. `transition: all` also animates layout-driving properties and causes jank.
- Motion stays interruptible by user input.
- Start scroll-triggered reveals with Intersection Observer and unobserve after the first run; never a scroll listener.

### Perceived performance

- Anything under about 80 ms feels instant; target it for press feedback.
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
