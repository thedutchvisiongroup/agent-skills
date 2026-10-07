# Examples and Acceptance Criteria

## Contents

- Small feature, no speculative architecture
- Reuse with behavioral fit
- Bug with multiple callers
- Test work in the existing suite
- Early coordinator clarification
- When extra code is simpler
- When an abstraction or dependency is justified
- Boundary checks and distinct caller contracts
- Specialist constraints and non-technical tasks

These are contrasting design examples, not templates to copy. The acceptable
implementation depends on the actual task and project. Acceptance criteria
describe observable behavior; reading these examples is not a live-agent test.

## Small feature, no speculative architecture

**Request:** add an optional nickname to the existing account form and save it
using the current account-update flow.

**Overbuilt:** add a profile-module framework, field registry, generic settings
service and several extension interfaces for future profile fields.

**Appropriate:** clarify nickname constraints if missing, then extend the current
form, validation and update flow. Keep the error/accessibility behavior the form
already requires. Add relevant checks using the existing test method.

**Acceptance:** the nickname saves and reloads; established validation and access
rules hold; no unused profile framework or unrequested settings are introduced.

**Counterexample:** multiple profile modules with independent lifecycle rules are
part of the approved current task. A module boundary may now be necessary.

## Reuse with behavioral fit

**Request:** generate product slugs. The project already has a slug helper that
handles accents, collisions and reserved identifiers.

**Overbuilt:** write a regex helper, a second collision algorithm and a wrapper
service without looking for existing code.

**Appropriate:** find the existing helper and inspect its behavior. Use it if its
contract matches. For pagination, apply the same reasoning to the framework's
built-in paginator instead of constructing another pagination system.

**Acceptance:** existing domain behavior is preserved and its knowledge remains
authoritative. The call site adds only the integration required by the task.

**Counterexample:** a native date input cannot meet approved date-range, calendar
or accessibility requirements. A suitable existing component or maintained
package may be simpler overall; native controls are a candidate, not a mandate.

## Bug with multiple callers

**Request:** transfers can overdraw an account. Transfers and withdrawals both
use a shared debit operation; that operation owns the non-negative-balance rule.

**Misleading small patch:** guard transfers only, leaving withdrawals broken.

**Appropriate:** trace both callers and the shared operation. Fix the invariant
where it belongs and verify that legitimate transactions still work. Respect the
existing transaction/locking model; a balance check alone may not handle races.

**Acceptance:** relevant callers satisfy the same invariant, valid behavior still
works, and the fix covers the actual cause rather than just the named symptom.

**Counterexample:** some approved account types allow overdrafts. A universal
guard would change their contract; clarify or implement the policy at its real owner.

## Test work in the existing suite

**Request:** cover the debit regression. A test runner, account fixtures and
database-test setup already exist.

**Overbuilt:** build another test harness, add mocks for every method and assert
internal call order rather than the balance/error behavior.

**Appropriate:** use the existing setup and relevant transaction fixtures. Add
behavior checks that fail for the bug and retain meaningful boundary cases.
Follow the test specialist's Red/production-handoff/Green workflow.

**Acceptance:** tests detect the regression without coupling to incidental
implementation details. Required verification and production-code handoff remain
intact; useful fixtures are not removed just to reduce lines.

## Early coordinator clarification

**Request:** “Put all settings behind a plugin system so we can extend it later.”

**Appropriate question:** “Which extensions are needed now? If these are a fixed
set of settings, would the current settings flow cover the requirement?”

Before planning, establish the actual outcome and constraints. A plugin system
is justified if real current extension requirements need it; do not replace it
with a smaller feature without agreement.

**Acceptance:** any material change of scope is agreed before dispatch. The
technical delegation contract requires loading `writing-simple-code`, states
confirmed requirements and success criteria, and routes uncertainty back through
the coordinator. A sufficient approved contract is not followed by duplicate
questions to the user from each worker.

## When extra code is simpler

**Situation:** a one-line condition intertwines account state, privileges and
several domain checks.

**Appropriate:** named intermediate values or a cohesive predicate can expose the
intent and make debugging easier, even with more lines. Use the project's idiom.

**Acceptance:** behavior is unchanged and readers can understand the policy
without mentally unpacking a clever expression. Fewer lines are not the verdict.

## When an abstraction or dependency is justified

**Situation:** one endpoint needs to parse a complex external document format.

**Appropriate:** a cohesive module can hide parsing details despite having one
caller. A maintained parser may meet the contract more reliably than a short
regex implementation. Explain the present benefit and follow dependency rules.

**Acceptance:** the abstraction has a clear responsibility and a simpler caller
interface; the dependency solves supported behavior. There are no speculative
format registries, future adapters or unused configuration options.

## Boundary checks and distinct caller contracts

**Situation:** an authenticated request reaches a helper through multiple paths.

**Appropriate:** preserve validation and authorization at their real boundaries.
Remove a repeated internal check only if the helper's enforced contract actually
guarantees it. Account for background jobs, public entry points and dynamic calls.

**DRY counterexample:** two forms look alike but use different eligibility rules.
Keep those policies separate rather than adding modes to a generic validator.
Conversely, a single tax rule used in several places should have one owner.

**Acceptance:** established guarantees justify any removed check, and distinct
domain knowledge is not accidentally unified.

## Specialist constraints and non-technical tasks

**Situation:** a binding domain skill mandates a container or dependency that
appears unnecessary for a tiny feature.

**Appropriate:** follow that prescription or ask about the specific conflict
before departing from it. The simplicity skill is not permission to override it.
Reviewers advise, security reviewers stay within security, and test specialists
hand off production changes regardless of how small the change is.

**When not to apply:** translating a non-technical email does not require this
skill or a code-complexity checklist. For technical reports, apply simplicity to
the recommendations while retaining the role skill's report format.
