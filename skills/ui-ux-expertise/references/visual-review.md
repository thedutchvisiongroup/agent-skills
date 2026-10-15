# Visual review

A fresh-eyes review of the rendered result. The `ui-reviewer` agent uses it; the main thread can use it for its own inspection round (see new-work.md, section 8). It judges what renders, never the code: source quality belongs to code review, and mechanical source checks belong to the detector.

## Contents

- Inputs
- Evidence gate
- Checks, in order
- Severity and verdict
- Report

## Inputs

Expect from the delegation contract:
- the original request and confirmed answers;
- the target (URL and/or the routes or components in scope);
- the direction contract or design brief (`design-brief.md` in the run directory) when one exists;
- screenshots at desktop and mobile width (plus any user viewport the contract names), or a URL to open;
- the confirmed design context (design-system or product docs) when one exists;
- the states that must be reviewed (empty, error, loading, long content, …).

When an input other than visual evidence is missing, note it in one line and review what is reviewable.

## Evidence gate

Visual evidence is mandatory. Without it there is no review.

1. Use the screenshots the contract provides.
2. If they are missing or incomplete and a browser or screenshot tool is available (browser extension, Playwright, built-in browser), open the contract's URL yourself and capture desktop (about 1440px) and mobile (about 390px), full page from the top, plus the required states the URL can reach.
3. Neither possible: stop with verdict `BLOCKED` (or `NEEDS_CONTEXT` in a reviewer template that has no BLOCKED) and name exactly what you need. Never judge from source code alone.

A capture is valid only when it shows what it claims. Entrance motion has settled; there are no blank or black regions and no half-loaded state; the page is the right route at the right width. Recapture invalid evidence when you can; otherwise report it as the blocker.

## Checks, in order

1. **Brief coverage.** Every requirement in the request and brief is present and findable within seconds. The primary action or task is unmistakable.
2. **Direction.** When a direction contract exists, check it promise by promise: THESIS visible in the first viewport, OWN-WORLD recognizable, FIRST VIEWPORT composition as written, SIGNATURE interaction present. A promise that renders as a mood is unmet.
3. **Mode fit.** Judge against [modes.md](modes.md). A Persuade page makes the offer intelligible with a working action. An Operate screen reads as a working product of its category with standard controls. A Read page keeps a calm reading column with clear wayfinding.
4. **Craft floor, as seen.** Hold the screenshots against [craft-floor.md](craft-floor.md):
   - contrast as perceived, gray text on color;
   - hierarchy and spacing rhythm, heading spacing;
   - type measure and overflow;
   - visible focus;
   - every item on the Refuse list (eyebrows, gradient text, side stripes, hard offset shadows, glyph icons, identical card grids, hero-metric template, ghost cards, decorative glass).
5. **Responsive.** Mobile is composed, not merely stacked: no horizontal scroll, no overflowing headings, touch targets that look tappable, navigation that works at that width.
6. **States.** The required states render deliberately (empty, loading, error, success, long and missing content). A browser default or a blank region is a finding.
7. **Truth.** Illustrative content is labeled where a visitor could mistake it for real; no invented commercial claims; imagery present where the brief implies it, with no broken images or colored placeholder blocks.
8. **Ceiling.** Where does the render stop short of the committed direction (unused signature, timid color commitment, generic sections)? Report it as one finding, not a list of tastes.

## Severity and verdict

Map findings to the reviewer severities:

| Visual severity | Reviewer severity | Examples |
|---|---|---|
| P0 Blocking | Critical | Task or primary action not possible, content unreadable, page broken at a required width |
| P1 Major | Important | WCAG AA contrast or focus failure, a banned anti-pattern, missing required state, direction promise unmet |
| P2 Minor / P3 Polish | Minor | Spacing or alignment inconsistencies, small rhythm issues |

Verdict: `APPROVED` when no Critical or Important finding remains; `CHANGES_REQUESTED` otherwise; `NEEDS_CONTEXT` or `BLOCKED` when the evidence gate failed or a required input is missing. Do not soften: a page that looks finished but breaks a brief promise is not approved.

## Report

Every finding cites its evidence: screenshot file (and region) or URL plus viewport, what is wrong, why it matters to the user, severity, and a concrete fix direction (a command such as `/ui-ux-expertise layout` is welcome). Group findings by severity. Add a short "evidence used" line listing the captures and their widths, and a "not reviewed" line for anything out of reach.
