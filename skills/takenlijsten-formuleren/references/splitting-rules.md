# Splitting rules

Decide whether something is one task, several sibling tasks, or steps within
one task. Wrong splitting produces either fragmented work or hidden
complexity.

## The core question

Walk the decision tree below in order. Do not skip ahead: the questions build
on each other.

"Enkelvoudig" (single) means: one deliverable, one verification — not one
hand movement.

## Decision tree

Ask these three questions **in this order** and stop at the first decisive
answer:

```
1. Is the item one deliverable with one executor class?
   ├─ No → split per deliverable or per executor, then evaluate each part
   │        from 1. Only "describe the deliverable first" when the item is
   │        too vague to name its deliverable.
   └─ Yes → continue to 2

2. Would splitting change what the parts mean?
   ├─ Yes → terminal. Do not split.
   └─ No → continue to 3

3. Does a part have standalone value AND its own acceptance criteria,
   without producing parallel tasks with identical contracts?
   ├─ Yes → split into sibling tasks
   └─ No → keep as one task with steps
```

## Signals that you must split

| Signal | Example | Why |
| --- | --- | --- |
| Two independently acceptable outputs | "implement + interview client" | one deliverable, one owner (= executor) |
| Independent value | "CSV-parser + validatie-regels" with separate users | each part is Valuable alone |
| Separate acceptance | one part is tested, the other reviewed | each needs its own contract |
| Different executor | agent can code, human must negotiate | agent contract differs |
| Independent rollback | one part can be reverted alone | safety differs |

## Signals that you must NOT split

| Signal | Example | Why |
| --- | --- | --- |
| Same verification for every part | 12 fields, one test suite | splitting duplicates the contract |
| Parts only work together | mapping table + its validator | no standalone value |
| Split would change content | schema migration in one transaction | atomicity is the content |
| Steps are pure sequence | write tests → implement → retest | these are steps |

## Layers

Do not confuse these levels:

| Level | Purpose | Tracked |
| --- | --- | --- |
| Theme/story | Outcome with value for user or client | closed per group DoD |
| Task | Work package (this skill) | closed per acceptance criteria |
| Steps | Execution order within one deliverable | does not count toward closing rules |

A story MAY contain several tasks. A task MUST NOT contain subtasks. If you
want subtasks, you are either looking at a story (promote the parent) or at
steps (demote the children).

## Vertical slicing

When a theme spans layers (database, API, UI), slice vertically: every task
delivers a thin path through all layers. Horizontal slices ("first all
database work") have no standalone value and violate INVEST Valuable.

## Terminal test

A task is terminal when rules 2 and 4 hold, **and** at least one of rules 1
and 3 holds:

1. Splitting it would change what the parts mean.
2. It has exactly one owner (= the party named in `Executor`) and one
   executor class.
3. Its acceptance criteria cannot be split into independent sets — or
   splitting would produce parallel tasks with identical contracts and no
   independent value.
4. Its verification runs as one unit.

Rule 1 or rule 3: each is a valid reason to stop splitting. Requiring both
would contradict the decision tree, where question 2 ("Yes") and question 3
("No") each already yield a terminal task.

If rules 2 or 4 fail, go back to the decision tree.
