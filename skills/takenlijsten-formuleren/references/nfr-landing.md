# Where NFRs land

Non-functional requirements belong to a grouping of tasks. One list is one
group, so that grouping is the list itself. Naming an NFR at group level is not
enough: an NFR counts as covered only when it lands in exactly one of three
places.

## The three landing spots

| # | Landing spot | When to use | What closes it |
| --- | --- | --- | --- |
| 1 | Task of its own | The NFR needs its own deliverable and owner | Task acceptance criteria |
| 2 | Acceptance criterion of a task | The NFR is satisfied by that task's output | The task's verification |
| 3 | Group-level closing rule | The NFR applies to the whole group and is checked once for all of it | Checked before the group closes |

Closing rules carry an id `GR1`, `GR2`, … so `Group rules` and the coverage
table can refer to them. Tasks do **not** reference group rules in the `NFR`
field: group rules already apply to every task in the group.

## Choosing between the three

```
Does the NFR need separate work with its own deliverable?
├─ Yes → 1. task of its own
└─ No
   ├─ Is it a single check over the whole group?
   │  ├─ Yes → 3. group closing rule
   │  └─ No → 2. acceptance criterion of the relevant task
```

## Examples

### Performance budget for report generation

- Needs profiling and a benchmark: **task of its own** (landing 1), with its
  own acceptance criterion like "p95 render < 2 s for 1 000 rows".

### Error messages in the user language

- One check over the whole group — every task either adds user-facing strings
  or adds none, and the rule is verified once for the batch: **group closing
  rule** (landing 3), for example GR2 "every new user-facing string exists in
  `messages.nl.yaml`". Tasks do not repeat this in their `NFR` field.

### Audit trail for one export action

- Tied to exactly one deliverable: **acceptance criterion** (landing 2) of the
  export task: "every export writes a row to `audit_log` with actor and
  timestamp".

## Anti-pattern

```markdown
## Group rules
- Performance: must be good
- Security: keep it in mind
- Accessibility: probably fine
```

None of these lands anywhere. Not covered. Rewrite to:

```markdown
## Group rules
- [ ] GR1: every new endpoint has a documented rate limit
- [ ] GR2: contrast ratio ≥ 4.5:1 on new screens (spot-check: home + form)
```

And put "export writes audit row" as an acceptance criterion on the export
task. The group rules above are verified once when the group closes; tasks
refer to neither of them.

## Cross-cutting NFRs

Security, accessibility, performance, and auditability often touch several
tasks. Prefer landing 3 when the check is uniform; prefer landing 1 when a
hardening pass is real work. Never spread one NFR over several landing spots —
that is how it falls between the cracks.
