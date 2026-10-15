> **Additional context needed**: quality bar and shipping constraints.

Polish is refinement, never concealed redesign. Preserve the incumbent visual world, content, behavior, and everything outside scope. If the concept itself is wrong, say so and recommend redesign or `bolder` instead of smuggling in a replacement.

A detector finding is defect evidence, not proof of quality. Inspect the rendered experience and real interaction path.

## 1. Establish the system

Read the design context and representative tokens, shared components, patterns, and neighboring flows. If no formal system exists, use coherent project conventions.

Classify each drift before fixing it:

- **missing token:** the system needs a reusable value;
- **one-off implementation:** an existing shared component or pattern should replace it;
- **conceptual mismatch:** the flow, information architecture, or hierarchy differs from comparable product areas;
- **local defect:** the implementation is simply incomplete or inconsistent.

Fix the cause at the narrowest correct level. Ask when a binding system principle cannot be inferred.

## 2. Gather the evidence

Use the feature yourself at its representative sizes (desktop and mobile at minimum). Determine:

- whether the path is functionally complete;
- the intended quality bar and time available;
- known constraints or deliberately unfinished work;
- the states, content lengths, roles, and input methods users will actually encounter.

If a critique from this conversation exists, use its P0 and P1 issues as one input and name it. Perform an independent pass either way.

## 3. Triage

Separate functional defects from cosmetic ones and fix in this order:

1. broken or blocked tasks, data loss, misleading state, and inaccessible paths;
2. missing loading, empty, error, success, disabled, and permission states;
3. flow, hierarchy, responsive, and design-system drift;
4. visual and motion inconsistencies;
5. code and asset cleanup.

Do not perfect one corner while leaving the rest below the same quality bar.

## 4. Polish the whole path

### Flow and hierarchy

- Match neighboring mental models, terminology, disclosure, routing, save behavior, and optimistic or pessimistic patterns.
- Make the primary task and current state obvious without flattening every element to equal weight.
- Ensure arrival, transition, empty, and recovery paths connect instead of behaving as isolated screens.

### Layout and type

- Align to the project's grid and spacing scale; fix optical as well as mathematical alignment.
- Group related content tightly and separate distinct groups generously.
- Keep same-role typography consistent; test measure, wrapping, localization expansion, zoom, and font loading.
- Verify every supported viewport rather than correcting only the current screenshot.

### Color, imagery, and icons

- Use semantic tokens and stable color meanings across themes.
- Verify text, control, and focus contrast in every state.
- Keep icon families, stroke/weight, sizing, and optical alignment coherent.
- Prevent image layout shift; use correct aspect ratios, responsive sources, and useful alt text.

### Interaction and state

- Every control needs appropriate default, hover, focus, active, disabled, loading, error, and success behavior.
- Preserve visible keyboard focus, logical tab order, labels, and platform-appropriate touch targets.
- Keep motion coherent, interruptible, and performant. Do not add animation merely to make polish visible.
- Validate long, missing, localized, offline, slow, and permission-limited content where the product can encounter it.

### Content and code

- Keep terminology, capitalization, punctuation, and factual copy consistent. Ask before changing claims.
- Remove debug output, dead code, unused imports, obsolete styles, and polish-created duplication.
- Replace custom implementations with shared components where the system owns the pattern.
- Promote genuinely reusable values to tokens; do not create a system abstraction for one local exception.

## 5. Verify and finish

Walk the complete path again with mouse, keyboard, and touch where applicable. Check:

- mobile, intermediate, and wide layouts;
- loading, empty, error, success, disabled, long-content, and missing-content states;
- zoom, contrast, focus, semantics, and screen-reader names;
- console errors, layout shift, interaction latency, image loading, and supported browsers;
- agreement with the design context, neighboring features, and the user's scope.

Run the detector once over the changed files (`python3 <skill-dir>/scripts/detect.py <changed files>`), verify each finding in context, and check the result against [craft-floor.md](craft-floor.md). Fix real defects and document only narrow intentional exceptions. A clean scan does not replace visual judgment.

Finish with a source diff: remove accidental churn, orphaned code, redundant values, and temporary artifacts. Ship only when the feature is functionally complete and consistently finished across the path.

## Checklist

- [ ] Drift against the design system named and resolved at its cause
- [ ] Flow and information architecture match neighboring features
- [ ] Alignment and spacing hold at every breakpoint and use the spacing scale
- [ ] Same-role typography is identical across the path
- [ ] Every interactive state exists (see [interaction-design.md](interaction-design.md))
- [ ] Loading, empty, error, and success states are designed, not defaulted
- [ ] Forms are labeled, validated, and recoverable
- [ ] Icons share one family, stroke, and optical size
- [ ] Contrast meets WCAG 2.2 AA in every state; focus is visible and never obscured
- [ ] Touch targets are at least 44x44px on touch surfaces (24x24px absolute floor)
- [ ] Keyboard path works end to end
- [ ] Reduced motion has an intentional alternative
- [ ] No console errors, layout shift, or stray debug code

**NEVER**:
- Polish before the path is functionally complete.
- Polish on top of system drift; that is decoration on drift.
- Guess at a design-system principle instead of asking.
- Fix one screen when the spacing or type problem is systemic; fix the system.
- Create one-off components or hard-coded values where the system has an equivalent.
- Introduce new patterns or flows that diverge from established ones.
