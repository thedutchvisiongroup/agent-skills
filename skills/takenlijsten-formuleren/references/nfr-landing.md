# Where NFRs land

An NFR counts as covered only when it lands in exactly one place and has a
check there. Naming it without a check does not count.

## The landing spots

| # | Landing spot | When to use | What closes it |
| --- | --- | --- | --- |
| 1 | Own to-dos plus a DoD item, inside the phase it belongs to | The NFR needs real work of its own (profiling, a hardening pass) | That DoD item |
| 2 | DoD item of the phase whose output satisfies it | The NFR is a property of one phase's result | The phase DoD |
| 3 | List DoD | One check over the whole list | Checked before the list closes |
| 4 | DoD item of the observation phase | The NFR is measured over time (a week of runs, five pushes) | The observation phase DoD |

Landing 4 exists because an NFR measured over time cannot be checked when the
phase that built it closes. Dropping it is not an option: the source still
requires it.

## Choosing

```
Is the NFR measured over time or over several runs?
├─ Yes → 4. observation phase
└─ No
   ├─ Does it need separate work of its own?
   │  ├─ Yes → 1. own to-dos plus DoD item
   │  └─ No
   │     ├─ Is it one check over the whole list?
   │     │  ├─ Yes → 3. list DoD
   │     │  └─ No → 2. DoD item of the producing phase
```

Every NFR item carries the source marker of the NFR itself:
`([[ftd#13. Non-functional requirements|NFR-04]])`.

## Examples

### Job duration budget

- "The job completes in ≤ 5 minutes": a property of one phase's output.
  **Landing 2**: DoD item of that phase, with the measured duration as
  evidence.

### Cache-hit share over one week

- "≥ 80% of runs over one week": measured over time. **Landing 4**: DoD item
  of the observation phase, with a count table in the run log as evidence.

### Least privilege on every workflow

- "Every workflow in scope holds only `contents: read`": one check over all
  files. **Landing 3**: list DoD.

## Anti-pattern

```markdown
### DoD
- [ ] Performance is good
- [ ] Security is taken into account
```

Neither item can be answered with yes or no, and neither names evidence.
Rewrite as a measurable check with evidence and a marker:

```markdown
### DoD
- [ ] The GraphQL gate completes in ≤ 5 minutes; duration recorded in the run log ([[ftd#13. Non-functional requirements|NFR-04]])
```

## Cross-cutting NFRs

Security, accessibility, performance and auditability often touch several
phases. Prefer landing 3 when the check is uniform. Prefer landing 1 when a
hardening pass is real work. Never spread one NFR over several spots: that is
how it falls between the cracks.
