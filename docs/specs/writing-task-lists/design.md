---
type: Design Note
title: "Writing Task Lists — Design Note"
description: "Design choices, rationale and decision history behind the writing-task-lists skill: phases with a to-do and a Definition of Done, one action or check per item, per-item source links, and three list variants."
tags: [design-note, skill, task-lists, writing-task-lists]
generated:
  by: claude-code/claude-opus-5-5
  at: 2026-10-16T08:30:54+02:00
status: draft
---

# Design Note — writing-task-lists

## Purpose

This note records how the `writing-task-lists` skill was designed and why it
looks the way it does. It is a design document for the skill: it describes the
choices, the reasoning behind them and the path that led there. It is not a
user guide. That lives in the skill's `SKILL.md` and `references/`.

The skill was developed under the working name `takenlijsten-formuleren`; the
rounds below refer to that period.

## Background and scope

The question was: what makes a good task list for software development, and
how do you formulate one so that the right end result comes out? That split
into two parts: research into what a good task list is, and a skill that
formulates task lists for execution by people and by orchestrated AI agents.

Since round 6 the bar is more concrete. A list must be workable for a
beginning programmer writing their first program. They must be able to trace
every action back to the right place in the source. And the list must exist
in three forms: for one person, for a team, or for one person with an agent.

The scope remains **formulating** task lists. Change policy, failure modes,
collaboration agreements, estimation philosophy and shared project status are
out of scope. Those are process agreements, not list content.

## Structure

```
skills/writing-task-lists/
├── SKILL.md                      # core, < 500 lines
└── references/
    ├── list-variants.md          # solo, team, human-agent
    ├── splitting-rules.md        # phases, items, decision tree
    ├── nfr-landing.md            # four landing places for NFRs
    └── task-examples.md          # good and weak phase, timing,
                                  #   human-agent and team fragment
```

`SKILL.md` carries the workflow and the rules. The references are progressive
disclosure: they are loaded only when needed and sit one level below
`SKILL.md`. The folder must be called `references/`, because `SKILL.md` links
to it. In the first upload the files sat loose next to `SKILL.md`, and all
four links pointed to nothing.

This design note is not referenced by the skill. It is documentation for the
reader, not execution material, so it lives in `docs/specs/` and not in the
skill folder.

The skill is in English. The lists it produces are in the language of the
request.

## Core choices

### Phases with a to-do and a DoD

A list consists of phases. A phase is a use case from the source, or a
cross-cutting phase: preparation, integration and review, release,
observation. Every phase has a to-do with the actions and a DoD with the
checks. Phase 0 always exists. It holds the checks from the verification step.

This replaces "one list is one group" from round 5. That choice was needed
because group rules automatically applied to every task, and there was no
field to record which group a task belonged to. Phases solve that. An item
belongs to the phase it is in. No further bookkeeping is needed.

### Items: one action or one check

A to-do item is one action, with the full path and, when known, the exact
command. A DoD item is one check you answer with yes or no, with the evidence
attached. There are no subtasks. An item that needs sub-items is a phase or
several items.

The old task contract with thirteen fields per task is gone. In the round 6
test, the content disappeared between the field names. Moreover, the steps
repeated the acceptance criteria, because the skill prescribed that the *how*
should stay open. Now it is the other way round. The how is in there, down to
the command. Only design choices the source leaves open stay open.

SMART and INVEST no longer have a section of their own, but live in the item
rules. Specific and Measurable are in "one action" and "yes or no with
evidence". Achievable is in the verification step and the toolchain rule.
Relevant is in the mandatory source link. Valuable and Small work at phase
level: a phase is a vertical slice of a use case that can close on its own.

### Beginner level

The reader knows the basics of the programming language, but not the
project, the tools or the source. So no step is implicit. Whatever must be
true beforehand, such as installed dependencies or running services, is listed
under "Before you begin", with the command that checks it. Every command gets
one line of explanation. A step that can go wrong in a known way gets "If it
goes wrong". A removal also says what must stay.

This comes straight from practice. When executing the first phase, nearly
every item raised a follow-up question: where is the script, what exactly do I
remove, why does `vitest` not work? The latter was due to a missing `npm ci`,
something CI does and the list did not mention. Once it came close to removing
the whole test step instead of only the coverage.

### Three variants

There are three variants: `solo`, `team` and `human-agent`. The variant
determines the files and the labels, not the rules.

`solo` is one list without executor labels. A step by someone else, such as
an approval, names the role from the source.

`team` is one shared list plus one list per person. The shared list is the
only place where a phase closes. It holds the DoDs, the shared actions and the
handovers. The personal lists contain only that person's own actions. They
link back to the shared list and keep their source link per item.

`human-agent` is one list in which every item starts with `(human)` or
`(agent)`. Per phase it states the agent's limits, the evidence it records and
the rollback. A human step is for judgement, decisions, approvals and external
settings. Checking something a run already shows is not a human step.

This also changes the "owner = executor" choice. In `team`, who does what is
recorded, otherwise there are no personal lists. That is deliberate. Who does
what is different from ownership or responsibility. Those stay outside the
list. The split comes from the user. The skill may propose one, but does not
decide.

### Traceability per item

Every to-do and DoD item ends with exactly one marker. That is either a
wikilink to the heading in the source that the item executes, or the
"addition" marker with a link to the reason. Additions have their own
section, stating what the source does not say, why the list needs it and who
confirms it.

Previously the source was given per task. As a result, my own additions in
round 6 looked as if they came from the FTD. Installing actionlint, for
example, was listed as a task, while the FTD only mentions it as an option.
Marking per item makes that difference visible. After writing, the skill
checks itself that every item has a marker and that every wikilink points to
an existing heading.

### Verify, don't assume

Everything the list relies on is checked before a phase starts. A reference
in the source is opened and read. A tool must be available through the
project's toolchain, not merely installable.

In round 6 this went wrong twice on a single point. The FTD's DoD required
YAML validation "per ADR-0008 convention". At first ADR-0008 seemed not to
exist. Then it turned out to mention PyYAML only as a one-off check, not as a
convention. And PyYAML was not in Devbox. A convention you have not read is a
rumour with an ADR number.

This is different from flagging whether a source has already been
implemented. That remains rejected (see Deliberately not done). Here it is
only about what the list itself needs to be executable.

### Checkable at the moment of closing

Every DoD item must be checkable at the moment the phase closes, with the
triggers, branches and environment that exist then. If that is not possible, a
to-do is added that makes it possible, or the item moves to the phase where it
can be checked.

This was the biggest mistake in the first list. The test workflows became
push-only on `main` and `dev`. As a result nothing could be proven before the
merge, while the DoD required it. The solution in the reference list is a
temporary validation branch, plus an item that cleans it up again.

### Red before green, also outside tests

A check that has never failed proves nothing. That already applied to tests
and now also applies to behavioural checks in CI. For a change in
configuration or toolchain there are three questions. Is gone what had to go?
Has nothing else changed? Do you notice it in the behaviour? For Xdebug, at
first only the first question was in the DoD. The diff of `devbox.lock` and
`php -v` turned out to be needed to really know.

### Toolchain and execution strategy follow the source

An addition adds no tools or dependencies outside the toolchain the source
defines. If something is needed anyway, it becomes an open question for
whoever decides. Branches, the number of pull requests and rollback follow the
source's rollout. The first list gave every task its own branch, while the FTD
prescribed one PR. "Git revert of the task commit" therefore had no meaning.

### Coverage from the source

The 100% rule stays: every source element lands somewhere, and nothing is
done twice. What is new is where the coverage table comes from. It is built by
enumerating all sections of the source, not just the user stories: DoD,
success criteria, NFRs, constraints, risks, quality scenarios, rollout and
open questions. The first list built the table from its own tasks and thereby
claimed completeness. A table the list lays next to itself only proves that
the list covers itself.

A second rule belongs with it: every DoD item and every review from the source
has a to-do that executes it. The first list required a review by
`code-reviewer`, but no task carried it out.

### NFRs in four places

An NFR only counts as covered when it lands in exactly one place and has a
check there:

1. its own to-dos with a DoD item, within the phase it belongs to;
2. a DoD item of the phase whose outcome fulfils it;
3. the DoD of the whole list, when it is one check over everything;
4. a DoD item of the observation phase, when it is measured over time.

Place 4 is new. The first list put NFRs that are measured over a week under
Out. As a result the FTD's DoD could never reach done. An NFR you cannot
measure when a phase closes does not disappear. It moves.

### Limits as an allowlist

This stays, but now at phase level in the `human-agent` variant. The
allowlist names what the agent may touch. Everything not on it is forbidden.
What is new is that lock files and generated files a tool changes as a side
effect must also be on it. `devbox.lock` was missing in the first list.

### Ask, but not too much

The skill asks only what the request and the source do not answer. The old
"Do not proceed without answers" let an agent fill in the ceiling itself, and
it excluded the observation. Now the ceiling may never exclude the source's
DoD, success criteria or rollout. If the user wants that anyway, it goes under
open questions.

Also new is the question about working material. If the repository is
available, the skill reads the real files, so items name real paths and
commands. If it is not, an item that needs a location starts with a search
action, not with a guess.

### Language

The whole list is in the language of the request, including headings and
labels. A fixed table maps the Dutch and English labels. Programming terms,
commands, identifiers and source terms stay as they are.

This replaces the old rule that field names and contract values always stayed
in English. That rule was needed for the thirteen-field contract. Now that the
contract is gone, it only produced a half-English list.

### Closing per level

There are three levels. An item is done when it is ticked off with evidence.
A phase is done when all its items are ticked off. The list is done when all
phases are closed, the list's DoD is met, coverage is complete and the open
questions are resolved or deliberately accepted. Without a closing rule,
"done" remains a feeling.

## Decision history

The skill was sharpened over six rounds. Per round: what came up and what was
decided.

### Round 0 — the start (2026-09-23)

Together we established what a good task list must have: SMART with
time-boxed as lowest priority, INVEST in full, tasks that cannot be split
further, traceability with closing rules (DoR, acceptance criteria, DoD), an
audience of humans and orchestrated agents, a closing rule per level, a clear
scope with in and out, NFRs at group level, documentation and tests at the
right moment (red tests → code → tests again), and short descriptions that
refer to the original documentation.

Additions we had overlooked earlier and that did make it into the design:
preflight on dependencies and tools, reversibility for agentic work (git), and
the classification of executability with criteria and evidence per class.

Deliberately dropped on my judgement: change policy, failure modes, spikes,
ownership, lifetime of the list, right to change, estimation philosophy. Those
belong to collaboration and consultation, not to the list. Status contract and
independent review apply only when agents execute.

### Round 1 — structure following writing-skills

Chosen: a skill directory with progressive disclosure, English content, a
medium degree of freedom (format mandatory, content free), and for now kept
only in `concepten/`, not yet installed. Result: `SKILL.md` plus three
references.

### Round 2 — errors in the examples and open items

What came up: the CI example did not meet its own acceptance criterion
(branch protection is a repo setting, not something in `.github/workflows/`);
a validation example mentioned client-side validation while the allowlist only
permitted server-side; NFR references differed in name and language; an
example had a review done by a person named by name; the decision tree gave
contradictory outcomes; "exactly once" was too strict for source elements; the
coverage check left no evidence; the output language was not defined.

Also the owner question: "one owner" was in the terminal test, there was no
field for it, and ownership was at the same time excluded from scope.

**Decided:** the owner becomes the party in `Executor`. No new field, but
checkable. Further: a sequential decision tree, the coverage table as
mandatory evidence, one language per list, Limits as an allowlist, a red run
as evidence, `agent-human` explained, one executor session as the size
measure, and a fixed section for open questions.

### Round 3 — following through on consequences

What came up: an example task still used a denylist for Limits; that same
task failed its own terminal test, which with the "all four" wording created a
loop with the decision tree; there was a broken link in the workflow; "list
owner" crept in as a new concept while owner had just been excluded; the
first branch of the decision tree did not route to splitting with two
deliverables; merging along a hard chain had no limit; the coverage table did
not yet know `Out` as a value and mixed "section" with "element"; the language
rule contradicted itself; the check on agent tasks lacked rollback and the
reachability of criteria.

**Decided:** terminal test as (1 or 3) and 2 and 4; `Out` as a coverage
value; element as the unit; a language rule with explicit contract
exceptions; and the NFR reference format fixed, because it would otherwise
differ per list.

### Round 4 — the NFR field and the network criterion

What came up: the NFR field could carry only one group rule, while group rules
by definition apply to all tasks. A reference per task is then either
incomplete or noise. The landing example named a subset and thereby violated
its own definition of landing 3. Audience and ceiling had no place in the
output. A remnant of the old notation remained. The language rule missed the
contract values themselves. And the network criterion in the CI example was
unattainable: `pip install` and `actions/checkout` go over the network.

**Decided:** group rules apply automatically and are not named per task; the
`NFR` field still knows `own criterion` and `none`; landing 3 becomes one
check over the whole group; a `Header` section is added; the language rule
names all backticked contract values; and the network criterion is limited to
the test step. Own addition: the coverage table accepts `GR<n>` as a value,
otherwise an element that lands as a group rule looks like a gap.

### Round 5 — group model and remnants

What came up: the output could contain only one group, while the list closing
spoke of "all groups". And now that group rules applied automatically, group
membership did determine which rules applied to a task. There was no field to
record that. Further: the list no longer opened with preflight while the text
still required it; workflow step 2 still mentioned "source version" while the
source had moved to the header; group rules were written in two notations; and
the network criterion still partly depended on test code outside the task's
allowlist.

**Decided:** one list is one group. The ceiling is one theme, the group level
coincides with the list level, and there are two closing levels instead of
three. Preflight follows the header. Group rules are consistently written as
checkboxes, because they are ticked off. And the network criterion becomes a
property of the workflow itself ("the test step runs without outbound network
access"), so that allowlist and steps together can meet the criterion.

### Round 6 — the field test (2026-09-28 and 2026-09-29)

After round 5 the skill had not been tried on a fresh list. That happened
now, on the PTA Vision FTD "CI/CD Simplification & Optimization". The list
that came out was formally correct and unworkable in practice. The yardstick
was my own prompt: phases per use case, with a to-do and a DoD as a checklist
per phase.

What came up, in order of severity. The skill forbade phases ("one list is
one group"), while the prompt asked for them. The steps repeated the
acceptance criteria, because the how had to stay open. Two tasks could only be
ticked off after the merge, because the triggers became push-only. The ceiling
excluded the observation, making the FTD's DoD unreachable. A review from the
DoD had no task that carried it out. The source was given per task instead of
per item, so additions could not be told apart from the FTD. And a convention
from the source turned out not to exist when read.

I then executed the first phase of the reference list myself. That produced
the second half of the lessons. An item such as "let the client job run
`vitest run`" was not something I could execute without explanation. Locally
`node_modules` and `vendor/` were missing. The database was not reachable
locally under the name CI uses. And a locally installed validator would have
become a dependency outside Devbox.

After the test, three requirements were added. There are three variants:
solo, team and human with agent. Every action refers with a wikilink to the
right place in the FTD. And a beginning programmer must be able to work with
the list.

**Decided:** phases with a to-do and a DoD replace the group model from round
5. The thirteen-field task contract is dropped. Items are one action or one
check, with path, command and expected outcome. Every item gets a wikilink or
the "addition" marker, with its own Additions section. The verification step
becomes phase 0. The timing check and coverage from the source become
mandatory. NFRs get a fourth landing place in the observation phase. Three
variants in a new reference. Beginner rules in the item rules. The language
rule is simplified to one language with a fixed label table. The reference
list `ftd-tasks.md` is the yardstick for the next test.

Two earlier choices were thereby deliberately reversed. "One list is one
group" from round 5 is dropped, because phases solve the membership problem.
And "owner = executor" from round 2 is broadened: in the team variant, who
does what is recorded. Ownership in the sense of responsibility stays outside
the list.

## Deliberately not done

- **Updating the test artefact.** `takenlijst-ftd-exam-checker-v1-3.md` does
  not conform to the current rules. That is deliberate: it is a test, not a
  goal in itself.
- **Flagging that a source already seems (partly) implemented.** Rejected:
  not wanted in the skill. The verification step from round 6 is something
  else. It only checks what the list itself needs.
- **Shipping a script for the link check.** The skill describes the check
  (every item marked, every wikilink to an existing heading), but ships no
  script for it. That can come later as `scripts/`, if the check turns out to
  be done by hand often.

## Open items

- After round 6 the skill has not yet been tried on a fresh list. The next
  test is the same FTD with the same prompt, compared with `ftd-tasks.md`.
- The team variant has only been designed on paper. No list with personal
  lists and handovers has been made yet.
- The rule that Obsidian drops a colon in links to headings I have seen in
  practice, but not checked in the official documentation.
- Whether the OKF validator accepts frontmatter of the type "tasks" is
  unknown. The skill therefore copies the frontmatter of an existing document
  in the target folder.

## Sources

Basis for the design (researched earlier, 2026-09-23):

- Anthropic, *Equipping agents for the real world with Agent Skills* (2025)
  and *Skill authoring best practices*: progressive disclosure, degrees of
  freedom, evals-first, feedback loops.
- Agent Skills specification (agentskills.io, 2025): format of `SKILL.md`,
  `scripts/`, `references/`, `assets/`.
- Bill Wake, *INVEST in Good Stories, and SMART Tasks* (2003): INVEST and
  SMART. The weighting of Time-boxed comes from the observation that size is
  already in the story.
- PMBOK / WBS practice: 100% rule, mutually exclusive, work packages, terminal
  elements.
- Cucumber / Gherkin: observable outcomes in `Then` steps.
- Cialdini (2021) and Meincke et al. (2025): commitment through checklists
  and bright-line rules.

Added in round 6:

- The field test itself: `ftd.md` (FTD-ci-cd-simplification v1.1) and the
  reference list `ftd-tasks.md`, 2026-09-28.
- dorny/paths-filter, README (consulted 2026-09-28): on push the action works
  with git and by default compares against the default branch. That prompted
  the rule that claims from the source are read and checked.
