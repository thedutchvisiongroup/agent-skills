# Design Principles Review

Read this during Phase 5 (Design and Maintainability). Principles are heuristics, not laws — apply them with judgment, and only where relevant to the code under review.

## Contents

- DRY — With the Essential Nuance
- SOLID — Where Relevant
- YAGNI / Over-Engineering
- KISS / Simplicity
- When NOT to Push Principles
- Review Checklist

## DRY — With the Essential Nuance

DRY is about duplicating **knowledge**, not lines of code. Every business rule should have a single, authoritative representation — but two similar-looking code blocks are not necessarily the same knowledge.

**Harmful duplication (flag it):**

- The same business rule implemented in two or more places — change one, forget the other
- Shotgun surgery: one logical change requires edits scattered across files
- Copy-pasted logic that has already started to drift apart

**Acceptable look-alike code (do NOT flag it):**

- Two pieces of code that look similar today but evolve for different reasons
- Setup duplication in tests (clarity beats DRY — see `test-quality.md`)
- Code you can't name well: if no abstraction name honestly covers both uses, they are probably two things

**The counter-principle:** *duplication is far cheaper than the wrong abstraction* (Sandi Metz). The wrong abstraction calcifies: each new requirement adds a parameter and a conditional until the shared code serves nobody well.

**Rule of three:** first time, write it. Second time, notice the duplication and tolerate it. Third time, abstract it.

**Signals of premature abstraction (flag these too):**

- An abstraction with exactly one caller
- Shared code whose behavior is switched by parameters (`if mode == "a" ... else ...`) for each caller
- Generic helpers built "for future reuse" (see YAGNI below)

**Minimal implementations:** the change should implement exactly what the requirement asks — no more. Duplication review and YAGNI review are two sides of the same question: *is every line here earning its place?*

## SOLID — Where Relevant

Applies to OO-style code. For functional or procedural code, SRP and DIP-style thinking still translate; OCP/LSP/ISP usually do not. **Never force OO principles onto code that isn't object-oriented.**

### S — Single Responsibility

- **The "and" test:** describe what the unit does in one sentence. Every "and" is a candidate extra responsibility.
- **Reasons to change:** how many distinct stakeholders or requirement types could force this unit to change? More than one → suspect.
- Signals: persistence + formatting + notification in one class; god classes; `utils`/`helpers` grab-bags.

### O — Open/Closed

- New behavior should arrive as **new** code, not edits to stable, working code.
- Signals: switch/if-else chains on type that grow with every new variant; a core class edited for each new case.
- Recommend extension points (strategy, registry, polymorphism) **only** where the codebase already uses that idiom or variants clearly keep coming. Don't build a plugin architecture for two cases — that's YAGNI.

### L — Liskov Substitution

- Subtypes must be usable anywhere their base type is, without special handling.
- Signals: overridden methods that throw "not supported"; callers doing type-checks for special subclasses; weakened guarantees in overrides (stricter preconditions, looser postconditions); defensive code wrapping specific subtypes.

### I — Interface Segregation

- Clients shouldn't depend on methods they never use.
- Signals: fat interfaces whose implementers stub out most methods; one interface serving unrelated callers; implementers raising `NotImplementedError` for interface members.

### D — Dependency Inversion

- High-level policy should not depend on low-level details.
- Signals: business logic directly constructing concrete infrastructure (database connections, HTTP clients); units that can't be tested without real infrastructure; missing seams.
- Follow the codebase's existing convention (DI framework, constructor injection, factories) — flag the dependency, not the mechanism.

## YAGNI / Over-Engineering

**You Aren't Gonna Need It.** Reviewers should be *especially vigilant* about over-engineering: code made more generic than needed, or functionality added for speculated future requirements. The future problem should be solved when it arrives and its real shape is visible.

**Signals:**

- Configuration options, parameters, or feature flags nobody currently uses ("for flexibility")
- A framework/abstraction layer serving exactly one use case
- Extension points and hooks with no consumers
- Module B built "because module A might need it later"
- Error handling for scenarios that cannot occur

**The test question:** "Which *current* requirement does this serve?" No answer → flag as `issue` or `suggestion`.

**Counterbalance:** YAGNI is not a license for sloppy code. Structure for change (clear names, small units, good seams) — just don't *implement* the change before it's needed.

## KISS / Simplicity

- The simplest design that satisfies the requirement wins.
- "Too complex" = "can't be understood quickly by code readers" or "likely to attract bugs when modified".
- For concrete signals and thresholds, see `complexity-metrics.md`.

## When NOT to Push Principles

Bias resistance: do not flag these as principle violations.

- **Spikes, prototypes, exploration code** — disposability is the point (but flag if it's being merged to main as-is)
- **Tests** — clarity first (see `test-quality.md`)
- **Performance-critical paths** where an abstraction has a *measured* cost
- **Small glue scripts, one-off migrations** — they run once and die
- **Established codebase conventions** that deliberately deviate — consistency with the surrounding code beats abstract principle-purity. Note it as `thought` at most.

## Review Checklist

- [ ] Knowledge duplication identified and flagged (with the nuance: harmful vs. look-alike)
- [ ] No premature abstractions (one-caller abstractions, parameter-switched shared code)
- [ ] Every implementation is minimal for its stated requirement
- [ ] SRP: units have one reason to change (OO code)
- [ ] OCP/LSP/ISP/DIP checked where the paradigm fits — not forced where it doesn't
- [ ] No speculative generality: every abstraction, option, and hook has a current consumer
- [ ] Principles applied as heuristics — no dogmatic flagging of justified deviations
