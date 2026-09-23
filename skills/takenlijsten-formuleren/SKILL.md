---
name: takenlijsten-formuleren
description: Formulates software development task lists with traceability, INVEST and SMART criteria for execution by team members and orchestrated AI agents. Use when creating, splitting, or revising task lists, backlogs, work plans, or sprint tasks for software development.
---

# Formulating task lists

Produce task lists where every task is unambiguous, no longer splittable,
traceable to its source, and — where needed — executable by an agent with
verifiable evidence.

## When NOT to use

- Capturing change policy, failure handling, ownership, collaboration
  agreements, or estimation philosophy. Those do not belong in a task list.
- Managing shared project status across people. Out of scope here.
- Designing or architecting solutions. Fix the source document first; the
  list only reflects it.

## Before You Start

You MUST confirm these three points with the user before writing the list:

1. **Source**: which document is authoritative, with version or date.
2. **Audience**: humans, agents, or both.
3. **Ceiling**: the single theme this list covers, and where scope stops.

Do not proceed without answers. If the user cannot name a source, the list
cannot have traceability — say so.

## Workflow

Copy this checklist and track your progress:

```
Task-list progress:
- [ ] 1. Confirm source, audience, ceiling
- [ ] 2. Write preflight (dependencies, tools)
- [ ] 3. Write scope (in / out) and group rules (incl. NFRs)
- [ ] 4. Decompose into terminal tasks (see references/splitting-rules.md)
- [ ] 5. Fill every task against the task contract
- [ ] 6. Check: every source element maps to at least one task or is explicitly
      under Out; no two tasks deliver the same output (100% rule)
- [ ] 7. Check: agent tasks have verification, evidence, limits, rollback; and
      limits + steps together can reach every acceptance criterion
- [ ] 8. Fill the coverage table (one row per source element → T-ids, `GR<n>`, or `Out`)
- [ ] 9. Deliver the list in the output structure below
```

### Step 1: Confirm the three points

Ask, then record the answers in the list header:

```markdown
## Header
- Source: <document> version/date <...>
- Audience: `humans` | `agents` | `both`
- Ceiling: <top level and where scope stops>
```

### Step 2: Preflight

The preflight block comes right after the `Header`. No task starts while
preflight is unchecked.

```markdown
## Preflight
- [ ] Dependencies available and correctly configured
- [ ] Tools present and set up (list per task what is needed)
- [ ] Group definition-of-done read (see Group rules)
```

### Step 3: Scope and group rules

One list is one group. The group level and the list level coincide: the
ceiling is a single theme, so there is no subgroup membership to record.

```markdown
## Scope
In: ...
Out: ... (list-level anti-goals)

## Group rules
- [ ] GR1: <closing rule, including how it is checked>
- [ ] GR2: <closing rule, including how it is checked>
- <group definition-of-done items>
```

Give every closing rule an id `GR1`, `GR2`, … in order. Tasks do not refer to
these ids: group rules already apply to every task in the group. The ids
serve `Group rules` itself and the coverage table. Definition-of-done items do
not need an id.

NFRs MUST land in exactly one of these places — see
[references/nfr-landing.md](references/nfr-landing.md):

1. a task of their own;
2. an acceptance criterion of a task in the group;
3. a group-level closing rule that is checked before the group is closed.

Naming an NFR without a verification point does not count.

### Step 4: Decompose

Split until every item is a **work package**: one deliverable, one owner, not
further splittable without changing its content. The decision rules are in
[references/splitting-rules.md](references/splitting-rules.md).

**Owner** means the party named in `Executor` — nothing more. Do not record
ownership, responsibility, or accountability separately: those are
collaboration agreements and are out of scope for this list.

Two levels inside a task:

| Level | What it is | Rule |
| --- | --- | --- |
| Task | Work package with its own acceptance criteria | Tracked and closed |
| Steps | Execution order inside one deliverable | Do not count toward closing rules |

### Step 5: Fill the task contract

Every task MUST use this format:

```markdown
### T<n> — <what, one line>
- **Source:** <document> v<version/section>
- **In:** <boundary>
- **Out:** <anti-goals for this task>
- **Acceptance criteria:**
  - [ ] <observable, testable result>
- **Verification:** <command, check, or review>
- **Evidence:** <what is delivered: test output, diff, screenshot, commit>
- **Executor:** `human` | `agent` | `agent-human`
- **Limits:** <agent only: allowlist of what may be touched>
- **Rollback:** <agent only: branch/commit/backup>
- **Depends on:** <T-ids or "none">
- **NFR:** <`own criterion` | `none`>
- **Steps:**
  - [ ] ...
```

Worked examples: [references/task-examples.md](references/task-examples.md).

## Field rules

### Title

One line, outcome-oriented, not an activity. "Validation rules for exam
fields added", not "working on validation".

### Source

Every task points to the original document with version or section. Depth
about what/why/how lives there. Keep the task short; no walls of text.

### SMART — weighting

- **S**pecific — MUST. Unambiguous, one interpretation.
- **M**easurable — MUST. Core question: can we tick this off?
- **A**chievable — MUST. Doable with available means.
- **R**elevant — MUST. Contributes to the theme; otherwise it does not belong.
- **T**ime-boxed — least important. Size already sits in story and scope; do
  not record clock time. For agent tasks one size rule does apply: it MUST fit
  one executor session — one executor completes it without renegotiating scope
  or switching to another deliverable.

### INVEST — full

- **I**ndependent — minimise dependencies; whatever remains MUST be explicit.
  Hard chain? Merge into one task only if the result still passes the terminal
  test and fits one executor session.
- **N**egotiable — fix *what* and acceptance criteria; leave *how* open.
- **V**aluable — delivers value to user or client. Slice vertically (through
  all layers), not horizontally per layer.
- **E**stimable — you need not estimate, but size MUST be such that you could.
- **S**mall — terminal. If a part has standalone value *and* its own acceptance
  criteria, it becomes a sibling task; the rest becomes steps.
- **T**estable — every acceptance criterion MUST be checkable.

### Acceptance criteria

Observable results. Describe what comes out of the system, not internal state.
For code tasks the order is: red tests first, then code, then tests again.
Schedule other tests immediately where possible.

### Verification and evidence

Verification says *how* "done" is checked. Evidence says *what* is handed over
so someone else can confirm without redoing the work. Both MAY sit at group
level when identical for all tasks in the group.

For tasks with tests, evidence MUST include the red run as well as the green
run: the red run is the proof that the test actually checks the behaviour.

### NFR reference

Use exactly one of these forms in the `NFR` field, and no other:

- `own criterion` — the NFR sits in this task's acceptance criteria;
- `none` — no NFR of its own in this task.

Group rules are never named here: they apply to every task in the group
automatically and are checked once when the group closes.

These two forms are contract language: keep them English in every list. An
optional clarification in parentheses MAY follow, e.g. `own criterion (audit
trail)`. Nothing else may be added: no dash, no free text, no second form.

### Executor

| Field | `human` | `agent` | `agent-human` |
| --- | --- | --- | --- |
| Acceptance criteria | yes | yes, machine-checkable | yes |
| Verification | optional | MUST | MUST |
| Evidence | optional | MUST | MUST |
| Limits | optional | MUST | MUST |
| Rollback | not needed | MUST (e.g. git) | MUST |

**`agent-human`** is one task in two phases: the agent executes what it can, a
human performs the steps that need a person (review, external settings,
judgment). Still one deliverable, one owner (= the executor class), one closing
moment.

An agent task without verification and evidence MUST NOT be included.

### Dependencies

Explicit T-ids. If T2 blocks T3, say so. Preflight catches technical
prerequisites; this field catches order.

### Limits

An **allowlist**, not a denylist: name what may be touched (files, commands,
areas). Anything not listed is off limits. Together with the steps, the
allowlist must be able to reach every acceptance criterion — if a criterion
needs something the allowlist forbids, fix the task instead of loosening the
limit silently.

## Closing rules per level

One list is one group, so there are two levels to close:

| Level | Closed when |
| --- | --- |
| Task | Acceptance criteria ticked, verification green, evidence present |
| List (= the group) | Group definition-of-done met, including NFR checks; preflight still valid; list anti-goals respected; coverage table complete |

Without a closing rule, "done" is a feeling.

## Output

Deliver the list as markdown with these sections, in this order:

1. `Header` (source, audience, ceiling)
2. `Preflight`
3. `Scope` (In / Out)
4. `Group rules`
5. `Tasks` (T1..Tn)
6. `Coverage` — one row per source element, mapped to T-ids, `GR<n>`, or `Out`
7. `Open questions` — scope or source questions; omit the section if there are
   none

**Language.** Write the whole list in one language: that of the **user's
request** — that is who reads it. Everything that is contract stays English
whatever the list language: field names, section names (`Header`, `Preflight`,
`Scope`, `Group rules`, `Tasks`, `Coverage`, `Open questions`), and all
backticked contract values (`human`, `agent`, `agent-human`, `own criterion`,
`none`, `Out`, `GR<n>`, `humans`, `agents`, `both`). Source terms, identifiers
and quotes stay in their original language. Everything else follows the list
language. No other mixing.

Do not summarize these rules in the output — only the list itself. Never hide
open questions as vague tasks: they belong in `Open questions`.
