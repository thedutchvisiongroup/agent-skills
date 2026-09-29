---
name: takenlijsten-formuleren
description: Formulates executable software development task lists from a source document (FTD, spec, plan), organised in phases with a to-do and a Definition of Done per phase, every item wikilinked to its place in the source. Supports three variants - one person, a team (shared list plus one list per person), or one person working with an agent - at a level a beginning programmer can follow. Use when creating or revising task lists, backlogs, work plans or sprint tasks for software development.
---

# Formulating task lists

A task list turns a source document into work someone can actually do, down
to a beginning programmer writing their first program. Every item is one
concrete action or one check, linked to the exact place in the source. Every
phase closes on checks that can be ticked off at the moment the phase ends.

## When NOT to use

- Capturing change policy, failure handling, collaboration agreements or
  estimation philosophy. Those do not belong in a task list.
- Designing a solution. Fix the source first. The list reflects the source;
  where it must add something, it says so under Additions.

## Before you start

Establish four things. Take them from the request and the source first. Ask
only for what is still missing.

1. **Source**: the authoritative document, its version or date, and its file
   name and location. The file name is the wikilink target.
2. **Variant**: `solo`, `team` or `human-agent`. See
   [references/list-variants.md](references/list-variants.md). For `team`,
   also the people and who does what. The user decides the split; you may
   propose one.
3. **Ceiling**: which part of the source the list covers. The ceiling never
   drops the source's own Definition of Done, success criteria or rollout
   steps. If the user wants that anyway, record it under Open questions.
4. **Working material**: is the repository available? If yes, read the files
   the source names (workflows, scripts, config, package manifests) so items
   name real paths, steps and commands. If no, an item that needs a location
   starts with a lookup action (a search command), never with a guess.

If no source can be named, the list cannot be traced. Say so and stop.

## Workflow

Copy this checklist and track progress:

```
Task-list progress:
- [ ] 1. Establish source, variant, ceiling, working material
- [ ] 2. Read the whole source and enumerate its elements
- [ ] 3. Verify what the list will rely on (becomes phase 0)
- [ ] 4. Divide into phases
- [ ] 5. Write each phase: header, to-do, DoD
- [ ] 6. Give every item one marker: source link or addition
- [ ] 7. Timing check: every DoD item can be ticked when its phase closes
- [ ] 8. Coverage check: every element lands; every DoD item has a to-do that produces it; nothing twice
- [ ] 9. Link check: every item marked, every wikilink resolves to a heading
- [ ] 10. Deliver in the output structure, per variant
```

### Step 2: Enumerate source elements

Elements come from every section, not only the user stories: acceptance
criteria, success criteria, Definition of Done, NFRs, constraints, risks and
their mitigations, quality and failure scenarios, security and privacy
controls, rollout and rollback steps, open questions. Build the coverage
table from this enumeration, not from the finished list. A table built from
the list only proves the list covers itself.

### Step 3: Verify, do not assume

Everything the list relies on is checked before any phase starts. The checks
become the to-dos of phase 0.

- **References in the source.** Open every document, ADR or convention the
  source refers to. Check that it exists and says what the source claims.
  "Per convention X" is a claim until you have read X.
- **Tools and commands.** Check that each one is available through the
  project's declared toolchain (for example `devbox run`, the package
  manager, the CI image). Installable is not the same as available.
- **Local prerequisites.** Dependencies installed, services running,
  environment variables present. A beginner hits these first.
- **External facts** the list builds on, where the source states them
  (action versions, tool behaviour).

When a check fails, fix it through an item, or record it under Open
questions. Never cover it with a guessed task.

### Step 4: Phases

- One phase per feature or use case of the source, in source order unless a
  dependency says otherwise.
- Add cross-cutting phases for work that belongs to no single use case:
  preparation (always phase 0), integration and review, release or merge,
  and observation after release when the source's DoD or success criteria
  need measurement over time.
- A phase closes on its own DoD. The list closes when every phase has closed
  and the list DoD holds.
- Splitting rules: [references/splitting-rules.md](references/splitting-rules.md).

Every phase starts with a header:

```markdown
## Phase <n> — <use case id>: <outcome>

Basis: <wikilinks to the source sections>
Touches: <allowlist: files and areas, including lock and generated files a tool changes>
Starts after: <phase or "phase 0">

### Before you begin
- [ ] <prerequisite, with the command that checks it>
```

`Before you begin` is omitted when the phase has no local prerequisites.
Variant-specific header lines are in the variants reference.

### Step 5: Item rules

**To-do items** are the work.

- One action per item, in the imperative. Two actions joined by "and" are
  two items, unless one command does both.
- Full path of every file.
- The exact command in a code block when the command is known from the
  source or the repository. Each command gets a one-line comment saying what
  it does.
- The expected result: `Expect: ...`.
- When an action removes or replaces something, say what stays: "Replace the
  script name in the step; the step itself stays."
- A "leave unchanged" requirement is written as a check: "Check that X is
  still present."
- Side effects are stated: an action that deploys, costs money, notifies
  people or cannot be undone says so.
- Order within a phase is execution order. Install and prepare before run.
- No tools or dependencies outside the project's declared toolchain. If one
  seems needed, it becomes an Open question for the decision maker.

**DoD items** are the closing checks.

- An observable result, answerable with yes or no, with the evidence named:
  run link, command output, diff.
- **Checkable when the phase closes**, with the triggers, branches and
  environment that exist at that moment. If not, add the to-do that makes it
  checkable (and, if temporary, the to-do that removes it again), or move the
  item to the phase where it becomes checkable.
- Behaviour checks show red before green where possible. A check that has
  never failed proves nothing.
- A configuration or toolchain change is covered by three checks: what had
  to go is gone (or what had to come is there); nothing else changed (the
  diff); the behaviour changed (run it).
- Every DoD item is produced by at least one to-do in the same or an earlier
  phase. Every review or approval named in the source has a to-do that
  performs it.

**Beginner level.** Write for a reader who knows the programming language
basics but not this project, its tools or the source.

- No implicit steps. If a step only works after another, that other step is
  an item before it.
- The first use of a project term or tool links to the source glossary, or
  gets one line in the list's Terms section.
- A step that can fail in a known way gets `If it fails:` with what the
  failure means and the next action. Often: stop and ask.

**Human steps** (variants `team` and `human-agent`) are for judgment,
decisions, approvals, external settings and anything needing credentials.
Checking an outcome that a run already shows is not a human step.

### Step 6: Markers and wikilinks

Every to-do and DoD item ends with exactly one marker:

- a wikilink to the source section it implements:
  `([[<source-file>#<heading>|§<n>]])`
- or an addition: `(addition, [[#A<n> <title>|A<n>]])`, pointing to the
  Additions section of the list.

Wikilink rules (Obsidian):

- Target: the source file name without extension.
- Heading: exactly as in the source, with `:` removed. Headings containing
  `#`, `|`, `^`, `[` or `]` cannot be linked; link the nearest parent heading.
- Link the most specific heading that states the requirement. Bold
  paragraphs are not headings: link their heading and name the item in the
  alias (`§10.3 DD-5`).
- Alias: the section number or the source id (`§7.1`, `US-01`, `R-02`).
- Links between lists of one variant: `[[<list-file>#<heading>]]`.

**Additions** are what the list needs but the source does not say. Each gets
a heading `### A<n> <short title>` with three lines: what the source does not
say, why the list needs it, and who confirms it. An addition never
contradicts the source silently. A deviation from the source is named as a
deviation and repeated under Open questions.

After writing, check mechanically that every item carries a marker and that
every wikilink target heading exists. Report the result in one line.

### NFRs

An NFR lands in exactly one place: its own to-dos with a DoD item, a DoD item
of the phase whose output satisfies it, or the list DoD when it is one check
over the whole list. NFRs measured over time land in the observation phase.
Details: [references/nfr-landing.md](references/nfr-landing.md).

## Execution strategy follows the source

Branches, number of pull requests and rollback follow the source's rollout.
Do not invent a branch or rollback per item. Rollback is described per phase
(or per list), in terms the rollout supports.

## Closing rules

| Level | Closed when |
| --- | --- |
| Item | Ticked, with its evidence recorded |
| Phase | All `Before you begin`, to-do and DoD items ticked |
| List | All phases closed, list DoD met, coverage complete, open questions resolved or explicitly accepted |

## Output

Sections in this order. Omit a section that would be empty.

1. Title, and frontmatter only if documents in the target folder use it
   (copy the fields of an existing document there).
2. Reading guide: three lines on markers, executor labels and Additions.
3. Additions (`A1`..`An`)
4. Terms
5. Phases 0..n
6. List DoD
7. Coverage: source element (as wikilink) → phase(s), person in `team`, or
   "not in this list" with the reason. Every element from step 2 appears.
8. Open questions

Variant structure and file names:
[references/list-variants.md](references/list-variants.md). Examples:
[references/task-examples.md](references/task-examples.md).

**Language.** The whole list is in the language of the user's request,
including headings and labels. Only these labels are fixed per language:

| English | Dutch |
| --- | --- |
| Phase | Phase |
| Before you begin | Voordat je begint |
| To-do | To-do |
| DoD | DoD |
| Basis / Touches / Starts after | Basis / Raakt / Start na |
| Expect: / If it fails: | Verwacht: / Als het misgaat: |
| (human) / (agent) | (mens) / (agent) |
| (addition, …) | (aanvulling, …) |
| Additions / Terms / Coverage / Open questions | Aanvullingen / Begrippen / Dekking / Open vragen |

Source terms, identifiers, commands and quotes stay as they are. Programming
terms stay English.

**Files.** Hyphens instead of spaces. Default name `<source-stem>-tasks.md`,
next to the source when its location is known.

Never hide an open question as a vague item. It belongs under Open questions.
