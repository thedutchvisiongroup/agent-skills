# Splitting rules

Decide what becomes a phase, what becomes an item, and what stays inside one
item. Wrong splitting produces either fragments nobody can finish or hidden
work nobody sees.

## Levels

| Level | What it is | Closed when |
| --- | --- | --- |
| Phase | One use case or one cross-cutting stage, with its own DoD | All its items ticked |
| To-do item | One action | Done, evidence recorded |
| DoD item | One check | Answered yes, evidence recorded |

There are no subtasks. An item that needs sub-items is either a phase (promote
it) or several items (split it).

## Phases

Default: one use case of the source is one phase.

Split a use case into two phases only when all three hold:

1. Each part has its own DoD items.
2. Each part can close without the other.
3. The source treats the parts separately (separate criteria, separate
   rollout steps).

Merge two use cases into one phase only when they cannot close separately:
their DoD items can only be checked together.

Cross-cutting phases (preparation, integration and review, release,
observation) exist when the source needs that work and it belongs to no
single use case. Phase 0 (preparation) always exists: it holds the checks
from the Verify step.

## Items

Walk these questions in order and stop at the first decisive answer.

```
1. Does the item contain more than one action?
   ├─ Yes → split per action, unless one command performs all of them.
   └─ No → continue to 2

2. Does the item need something that is not yet true
   (installed, running, known, decided)?
   ├─ Yes → add an item before it that makes it true.
   └─ No → continue to 3

3. Can a beginner do it with only the item text, the linked source
   section and the commands given?
   ├─ No → add what is missing (path, command, expected result),
   │        or split off the lookup as its own item before it.
   └─ Yes → the item is final.
```

## Signals that you must split

| Signal | Example | Why |
| --- | --- | --- |
| "and" joins two actions | "Remove the step and update the lock file" | two actions, two results to check |
| Two different files | edit the workflow, edit the manifest | one path per item |
| Different executor | agent edits, human decides | different label |
| Separate check | one part is tested, the other reviewed | two DoD items |
| Lookup hidden in an action | "Replace the test command" when the command is unknown | the lookup is its own item |

## Signals that you must NOT split

| Signal | Example | Why |
| --- | --- | --- |
| One command does it all | `devbox install` updates the lock file | one action |
| Same check for many parts | 12 fields, one test suite | one DoD item, not twelve |
| Parts only work together | mapping table and its validator | no standalone result |
| Atomic by nature | schema migration in one transaction | atomicity is the content |

## Vertical slicing

When a use case spans layers (database, API, UI), the phase delivers a thin
path through all layers. Phases per layer ("first all database work") have no
standalone value and cannot close on their own DoD.

## Final item test

An item is final when all of these hold:

1. It is one action or one check.
2. It has one executor (or one person, in the `team` variant).
3. It names every file by full path and every known command exactly.
4. It carries exactly one marker: a source link or an addition.
