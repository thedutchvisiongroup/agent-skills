# Examples

Quality examples for phases and items. The format is fixed; the content is
free. The source in these examples is `ftd.md`, so wikilinks target `ftd`.

## Good phase (`solo`)

```markdown
## Phase 1 — US-01: Quality ratchet removed from the fast gate

Basis: [[ftd#7.1 US-01 Remove the quality ratchet|§7.1]], [[ftd#3.2 In scope|§3.2]]
Touches: `.github/workflows/run-tests-app.yml`, `devbox.json`, `devbox.lock`
Starts after: phase 0

### Before you begin
- [ ] Install the Node dependencies exactly as the lock file pins them ([[ftd#5.4 Constraints|§5.4]])
      ```bash
      # Same install as CI; removes node_modules first
      devbox run -- npm ci
      ```
      Expect: no errors; `node_modules/` exists.

### To-do
- [ ] In `.github/workflows/run-tests-app.yml`, job `client`, step "Run client tests with coverage": replace `test:client:coverage` with `test:client` and rename the step to "Run client tests". The step itself stays ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
- [ ] In the same job, delete the whole step "Upload client coverage", from `- name:` up to and including `if-no-files-found: warn` ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
- [ ] Check that `test:client:coverage` is still present in `packages/app/package.json` ([[ftd#3.3 Out of scope|§3.3]])
      ```bash
      # Expect one line: "test:client:coverage": "vitest run --coverage"
      grep -n '"test:client:coverage"' packages/app/package.json
      ```
- [ ] Remove `php84Extensions.xdebug` from `devbox.json` ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
- [ ] Sync the lock file with `devbox.json`. Do not run `devbox update`: that upgrades every package ([[ftd#5.4 Constraints|§5.4]])
      ```bash
      # Removes lock entries that devbox.json no longer declares
      devbox install
      ```

### DoD
- [ ] No coverage left in the workflow: `grep -n "coverage" .github/workflows/run-tests-app.yml` gives no output ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
- [ ] The client tests pass without coverage: `devbox run -- npm --workspace @pta-vision/app run test:client` is green and creates no `packages/app/coverage/` ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
- [ ] Xdebug is gone: `grep -n xdebug devbox.json devbox.lock` gives no output ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
- [ ] Nothing else changed: `git diff devbox.lock` shows only the removed `php84Extensions.xdebug@latest` block ([[ftd#5.4 Constraints|§5.4]])
- [ ] PHP runs without Xdebug: `devbox run -- php -v` prints a version line and no Xdebug line ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
      If it fails: no PHP version line means PHP itself did not start. Stop and ask.
```

Why this works:

- Every item is one action or one check, with full paths.
- Replacements say what stays; "leave unchanged" is written as a check.
- `Before you begin` covers the install a beginner would otherwise miss.
- The configuration change is covered three ways: gone, nothing else
  changed, behaviour changed.
- Every item links to the section it implements. The two items that protect
  the toolchain link to the constraint, not to the user story.

## Weak phase

```markdown
### T4 — Push-only triggers
- **Source:** FTD
- **Acceptance criteria:**
  - [ ] a front-end-only push skips the php job
- **Steps:**
  - [ ] set triggers to push-only
  - [ ] add gating
  - [ ] validate the YAML (actionlint or PyYAML)
```

What is wrong:

| Problem | Rule broken |
| --- | --- |
| No phase structure; task instead of phase with to-do and DoD | Phases |
| Source without section, no wikilink per item | Markers |
| Steps repeat the criterion instead of naming actions, paths, commands | To-do items |
| The criterion needs a push that, after this change, only runs on `main`/`dev`: not checkable when the phase closes | Timing check |
| "actionlint or PyYAML" without checking that either is in the toolchain | Verify step |
| No red-before-green: nothing shows the gating can fail | DoD items |

## Timing: making a DoD item checkable

A DoD item that can only be checked after merge needs a to-do that makes it
checkable earlier, plus one that removes the temporary route:

```markdown
### To-do
- [ ] Create validation branch `ci/validate-simplification` from the working branch (addition, [[#A1 Validation before merge|A1]])
- [ ] On that branch only, add it to `branches` of both test workflows, in one commit starting with `TEMP:` (addition, [[#A1 Validation before merge|A1]])

### DoD
- [ ] Run evidence: a push touching only `packages/app/resources/ts/**` shows `php` as skipped, not failed ([[ftd#7.2 US-02 Push-only triggers with per-job change gating|§7.2]])
```

And in the integration phase:

```markdown
- [ ] Check that the working branch contains no temporary triggers: `grep -rn "validate-simplification" .github/` gives no output (addition, [[#A1 Validation before merge|A1]])
```

## `human-agent` fragment

```markdown
Agent limits: `.github/workflows/_verify-graphql-contract.yml`; commands `devbox run …`, `git`
Agent evidence: run links and command output in the run log
Rollback: revert the phase commits on the working branch

### To-do
- [ ] (agent) Create `.github/workflows/_verify-graphql-contract.yml` as a `workflow_call` workflow, modelled on `_verify-pdf-contract.yml` ([[ftd#10.3 Design decisions (ADR-style; recorded formally as ADR-0010 where marked)|§10.3 DD-5]])
- [ ] (agent) Push a deliberately stale `schema.graphql` to the validation branch ([[ftd#3.4 Success criteria|SC-4]])
- [ ] (human) Decide whether the minimal inline env fallback is acceptable, if the gate failed on booting artisan ([[ftd#16. Risk register|R-01]])

### DoD
- [ ] Run evidence: the stale-schema run is red and prints the regeneration command ([[ftd#3.4 Success criteria|SC-4]])
```

The human item is a decision. "Check that the run is red" would not be a
human item: the run already shows it.

## `team` fragment

General list `ftd-tasks.md`:

```markdown
## Phase 1 — US-01: Quality ratchet removed from the fast gate

Basis: [[ftd#7.1 US-01 Remove the quality ratchet|§7.1]]
Starts after: phase 0
Assigned: [[ftd-tasks-eva#Phase 1 — US-01 Quality ratchet removed from the fast gate|Eva]], [[ftd-tasks-lonneke#Phase 1 — US-01 Quality ratchet removed from the fast gate|Lonneke]]

### Shared to-do
- [ ] Lonneke hands the ADR-0010 number to Eva before the OI-03 closure ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])

### DoD
- [ ] ADR-0010 exists and supersedes ADR-0008 ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
```

Personal list `ftd-tasks-eva.md`:

```markdown
## Phase 1 — US-01: Quality ratchet removed from the fast gate

Status and DoD: [[ftd-tasks#Phase 1 — US-01 Quality ratchet removed from the fast gate|general list]]

### To-do
- [ ] Start after: [[ftd-tasks-lonneke#Phase 1 — US-01 Quality ratchet removed from the fast gate|Lonneke — ADR-0010 number]]
- [ ] Close OI-03 in `packages/app/docs/specs/testing-framework/open-issues.md` as "won't do (ratchet scrapped)", with a link to ADR-0010 ([[ftd#7.1 US-01 Remove the quality ratchet|§7.1]])
```

The DoD lives only in the general list. The personal list links to it and
keeps the source link on every item.
