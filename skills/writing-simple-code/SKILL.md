---
name: writing-simple-code
description: Keeps code and technical designs understandable and complete while preventing over-engineering, speculative architecture, broad refactors, redundant defensive code, and duplication. Applies YAGNI, KISS, knowledge-focused DRY, and Avoid Hasty Abstractions through clarification, suitable reuse, and justified structure. Use when writing, changing, debugging, reviewing, or designing production code, tests, scripts, configuration, dependencies, or technical recommendations. Complements specialist workflows and applies within the agent's role. Also use when the user asks for simple or minimal implementations or flags unnecessary complexity. Do not use for purely non-technical work or prose-style editing.
---

# Writing Simple Code

**Choose the simplest complete solution that is easy to understand and change.**
Fewer lines are useful only when they reduce unnecessary complexity. Correct
behavior and clear intent come before line count, file count, or a tiny diff.

## Scope and precedence

- Apply to code and technical design, including tests, scripts, configuration,
  dependency choices, reviews, and implementation recommendations.
- Load the applicable role/domain skill first. This skill complements its method;
  it does NOT relax permissions, role boundaries, required gates or verification.
- Preserve agreed functionality, security, data integrity, accessibility,
  compatibility, relevant error handling, and supported performance/scale needs.
- Respect binding project conventions and specialist prescriptions. If an
  appropriate simplification conflicts with one, explain the conflict and ASK
  before departing from it. Simplicity does NOT authorize a silent override.
- Purely non-technical tasks and prose formatting are outside this skill. It does
  not define an orchestration process or a new report format.

## Before technical work: clarify and understand

1. **Check scope early.** Identify the requested outcome, relevant constraints,
   and what would demonstrate completion. Briefly align on the intended task.
2. **Ask before guessing.** If scope, behavior, constraints or success criteria
   are uncertain, ask concrete questions before acting on that uncertainty. Use
   the question tool when available. Suggest a simpler alternative when a
   request appears overbuilt; get agreement before changing its scope or guarantees.
3. **Reuse confirmed context.** Do not manufacture questions when the scope is
   already fully clear. A sufficient, approved delegation contract counts as
   alignment only for the role-gate items it explicitly answers. Perform required
   detection and check every gate item; matching user-confirmed answers satisfy
   confirmation, not the whole gate by assumption. Missing answers, mismatches
   and new material tradeoffs go through the coordinator; wait for resolution.
   For direct work, retain the role skill's ordinary clarification gate.
4. **Understand before minimizing.** Read the affected code and trace relevant
   inputs, behavior, callers and contracts. Resolve uncertainty about existing
   APIs using the project's/domain skill's research workflow. For bugs, find the
   cause and all affected paths before selecting the smallest appropriate fix.

When an answer changes a material decision, wait for it. A smaller feature
shipped first and questioned afterward is not a substitute for agreement.

## Choose the implementation

Use this decision path after understanding the task; it is not an exhaustive
research exercise or a rigid ranking of tools:

1. **Necessity:** distinguish current requirements from speculative additions.
   Implement the former; leave hypothetical capabilities for a real requirement.
2. **Suitable reuse:** look for existing project helpers, framework features,
   standard-library functions, native platform capabilities and installed
   dependencies. Verify behavioral fit, constraints and compatibility. Reuse
   should simplify the whole solution, not import unrelated complexity.
3. **Direct solution:** choose straightforward code with clear names and flow.
   A few readable statements can be simpler than one compressed expression.
4. **Justified structure:** add a helper, module, abstraction or dependency when
   it provides a concrete current benefit: shared knowledge, useful encapsulation,
   a required contract, testability, clarity or a supported operational need.
   Future flexibility alone is not a justification.

## Rules that prevent unnecessary complexity

- **YAGNI:** omit unrequested options, extension points, configuration, fallback
  paths and scaffolding for imagined future consumers. Fully implement agreed
  requirements; do not silently downgrade them to a prototype.
- **KISS:** prefer explicit, cohesive responsibilities and familiar project
  idioms. Do not add indirection merely to satisfy a design-pattern checklist.
  Avoid code golf and unrelated behavior hidden behind clever expressions.
- **DRY + AHA:** give the same domain knowledge one authoritative owner. Similar
  syntax with different reasons to change may stay separate. Extract only a
  concept you understand; do not force unrelated policies into flag-driven shared
  code. One caller or one implementation is a signal to inspect, not a ban.
- **Local, necessary change:** simplify inside the affected responsibility when
  it directly helps the task and preserves required behavior. Offer broader
  cleanup as follow-up work. Before deleting apparently unused code, investigate
  its consumers, public contracts and dynamic/framework usage; ask if uncertain.
- **Correct fix location:** fix a common invariant at its actual shared owner
  when all affected paths require it. Keep caller-specific rules local when their
  semantics differ. The shortest patch in the wrong place is not a simple fix.
- **Proportionate protection:** validate real trust boundaries and handle relevant
  failures. Remove repeated internal checks only when an established contract
  makes them redundant. Do not hide failures with empty catches, success-shaped
  defaults or fallback chains that obscure the cause.
- **Dependencies:** assess total complexity and maintenance, not just import size.
  Justify a new dependency by present needs. Use a suitable maintained library
  rather than reinventing security-sensitive or intricate behavior for fewer lines.
- **Performance:** avoid speculative caching, concurrency and optimization.
  Use demonstrated requirements, known input bounds or measurements; do not
  ignore clear algorithmic problems at the supported scale.
- **Tests:** use established tooling and specialist methods. Prefer relevant
  behavior checks over implementation-mirroring tests or needless mocks/helpers.
  Keep useful fixtures and meaningful regression checks. This skill imposes no
  test quota, tooling ban, or exemption from required verification.

## Apply within your role

| Role | Apply simplicity to |
| --- | --- |
| Implementer | The complete implementation and local changes permitted by the task. |
| Orchestrator/coordinator | Early scope discussion, design choices, and technical delegation contracts. Require delegated workers to load this skill and give them the confirmed constraints and success criteria. |
| Code reviewer | Evidence-backed complexity findings: location, current cost, and a concrete simpler alternative that preserves requirements. Advise; do not edit reviewed code. |
| Security reviewer | Security-relevant recommendations and their design tradeoffs, without weakening protection. Route unrelated code-quality issues through the existing handoff workflow. |
| Test specialist | Test code and test-design recommendations. Preserve testing discipline and hand off production-code changes. |

Keep required role-specific reporting and collaboration. Explain meaningful
tradeoffs rather than narrating this entire checklist for every task.

## Before completion

- [ ] All agreed behavior and relevant guarantees remain satisfied.
- [ ] The changed/recommended code follows the actual flow and contracts.
- [ ] Reuse fits; every added layer, option and dependency has a current reason.
- [ ] Shared knowledge is not duplicated or confused with look-alike code.
- [ ] Simplification is local and necessary; no unrelated cleanup was bundled in.
- [ ] Required checks are complete and their actual outcomes are reported.

For advisory work, verify these claims for the proposed change and report gaps;
do not claim to have implemented or verified an unexecuted recommendation.

## References

Load only the reference relevant to the current question:

- [Examples](references/examples.md): common tasks, counterexamples and observable
  acceptance criteria; consult when deciding whether a simplification fits.
- [Principles and sources](references/principles-and-sources.md): rationale,
  disagreements and evidence limits; consult when a principle or tradeoff is disputed.
