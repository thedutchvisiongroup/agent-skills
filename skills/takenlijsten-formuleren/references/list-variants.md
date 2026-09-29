# List variants

Three variants. Take the variant from the request. Ask only when it is not
clear. All rules from SKILL.md apply to every variant; this file adds what
differs.

| Variant | Who works | Files |
| --- | --- | --- |
| `solo` | one person | one list |
| `team` | several people | one general list plus one list per person |
| `human-agent` | one person and one or more agents | one list |

## `solo`

One person does all the work. No executor labels.

Steps that need someone else, such as an approval, name that role in bold at
the start of the item: `**(PO)** Approve the pull request.` Take the role
from the source; do not invent names.

Skeleton:

```markdown
## Phase 1 — US-01: <outcome>

Basis: [[ftd#7.1 US-01 <title>|§7.1]]
Touches: `<paths>`
Starts after: phase 0

### Before you begin
- [ ] <prerequisite + check command>

### To-do
- [ ] <one action> ([[ftd#…|§…]])

### DoD
- [ ] <observable check + evidence> ([[ftd#…|§…]])
```

## `team`

Several people work on the same source. The work is split over files so each
person sees only their own actions, while phase status stays in one place.

### Files

- **General list** `<source-stem>-tasks.md`: all phases, every DoD, the
  shared to-dos (integration, review, merge, handovers), Additions, Terms,
  Coverage, Open questions. This is the single place where a phase is closed.
- **Personal list** `<source-stem>-tasks-<person>.md` per person: only that
  person's to-dos, in execution order, grouped under the phases of the
  general list.

### Assignment

- The user decides who does what. You may propose a split per phase or per
  deliverable. Split vertically (a whole use case), not per layer.
- One item has one person. For pair work, assign it to one person and name
  the other in the item text.
- An item nobody is assigned to goes under Open questions, not into a
  personal list.

### Links between the files

- In the general list, each phase header gets an `Assigned:` line linking to
  the personal lists: `Assigned: [[ftd-tasks-eva#Phase 1 — US-01 …|Eva]]`.
- In a personal list, each phase heading links back to the general list:
  `Status and DoD: [[ftd-tasks#Phase 1 — US-01 …|general list]]`.
- Every personal item keeps its source marker. The source link stays the
  basis, not the general list.
- A handover between people is an explicit item in the receiving person's
  list: `Start after: [[ftd-tasks-lonneke#…|Lonneke — schema ready]]`.

### Skeleton, general list

```markdown
## Phase 2 — US-02: <outcome>

Basis: [[ftd#7.2 …|§7.2]]
Touches: `<paths>`
Starts after: phase 1
Assigned: [[ftd-tasks-eva#Phase 2 — US-02 …|Eva]], [[ftd-tasks-lonneke#Phase 2 — US-02 …|Lonneke]]

### Shared to-do
- [ ] <handover or joint action> ([[ftd#…|§…]])

### DoD
- [ ] <check + evidence> ([[ftd#…|§…]])
```

### Skeleton, personal list

```markdown
## Phase 2 — US-02: <outcome>

Status and DoD: [[ftd-tasks#Phase 2 — US-02 …|general list]]

### Before you begin
- [ ] <prerequisite + check command>

### To-do
- [ ] <one action> ([[ftd#…|§…]])
```

## `human-agent`

One person works with one or more agents. One list. Every to-do item starts
with its executor label: `(agent)` or `(human)`.

### Division of work

- `(agent)`: mechanical work with a checkable result: editing files, running
  commands, collecting evidence.
- `(human)`: judgment, decisions, approvals, external settings, anything
  needing credentials the agent must not hold, and review of agent output
  before a step that depends on it.
- A human item is never "check what the run already shows".

### Agent contract per phase

Every phase with agent items adds three header lines:

```markdown
Agent limits: <allowlist of files, commands and areas; anything not listed is off limits>
Agent evidence: <what the agent records per DoD item: output, diff, run link>
Rollback: <how the phase is undone, following the source's rollout>
```

- Limits together with the to-dos must be able to reach every DoD item. If a
  DoD item needs something the limits forbid, fix the phase. Do not widen the
  limits silently.
- Limits include lock files and generated files that a tool changes as a
  side effect.
- An agent item whose result no DoD item checks is not allowed.
- Unless an item says otherwise, the agent does not install tools, change
  repository settings or push to protected branches.

### Handover

When agent output needs human review before the next step, make it an item:
`(human) Review the diff of <path> before continuing.`

### Skeleton

```markdown
## Phase 4 — US-04: <outcome>

Basis: [[ftd#7.4 …|§7.4]]
Touches: `<paths>`
Starts after: phase 3
Agent limits: `<paths>`; commands `<…>`
Agent evidence: command output and run links in the run log
Rollback: revert the phase commits on the working branch

### To-do
- [ ] (agent) <one action> ([[ftd#…|§…]])
- [ ] (human) <decision or review> ([[ftd#…|§…]])

### DoD
- [ ] <check + evidence> ([[ftd#…|§…]])
```
