# Task examples

Format and quality examples. Format fields are mandatory; content within
fields is free. For the decision rules behind splitting, see
[splitting-rules.md](splitting-rules.md).

## Good task

```markdown
### T3 — Validation rules for exam fields added
- **Source:** FTD-exam-checker v3.1 §4.2
- **In:** fields `duration`, `exam_date`, `weight`; server-side validation
- **Out:** client-side validation (separate task); other fields; changes to the CSV parser
- **Acceptance criteria:**
  - [ ] `duration` outside 1–240 minutes yields an error message per field name
  - [ ] invalid `exam_date` is rejected before storage
  - [ ] error messages appear in the validation report, not only in the log
- **Verification:** `pytest tests/test_exam_fields.py -q`
- **Evidence:** red test run, green test output, diff of `validators/exam_fields.py`
- **Executor:** `agent`
- **Limits:** only `validators/` and `tests/test_exam_fields.py`
- **Rollback:** work on branch `feat/t3-exam-field-validation`
- **Depends on:** T1
- **NFR:** none
- **Steps:**
  - [ ] write red tests for `duration`, `exam_date`, `weight`
  - [ ] implement validation until the tests are green
  - [ ] run the tests and keep the output
```

Why this works: one deliverable, observable acceptance criteria, machine
check, evidence defined (including the red run), agent boundaries as an
allowlist, rollback present, source with version, short fields. `NFR` is
`none` because the language rule for error messages is a group rule: those
apply to every task automatically and are never named per task.

## Weak task

```markdown
### T3 — Make validation better
- **Source:** FTD
- **Acceptance criteria:**
  - [ ] validation works better
  - [ ] no bugs
- **Executor:** `agent`
- **Steps:**
  - [ ] check validation
  - [ ] add tests
  - [ ] maybe documentation too
  - [ ] and the parser?
```

What is wrong:

| Problem | Rule broken |
| --- | --- |
| Title is an activity, not an outcome | Title |
| Source without version or section | Source |
| No in/out boundary | In/Out |
| Acceptance criteria not observable or testable | SMART M/T, INVEST T |
| No verification or evidence | Agent contract |
| No limits or rollback for agent work | Agent contract |
| Steps contain a different deliverable ("and the parser?") | Task is not terminal |
| "Maybe" indicates undecided scope | Negotiable ≠ undecided |

## Task with human executor

```markdown
### T7 — Acceptance interview with client documented
- **Source:** PVA-exam-generator 2026-08-17 §3
- **In:** one-topic interview on storing seeded school years
- **Out:** other topics; decision-making in this interview
- **Acceptance criteria:**
  - [ ] client answers recorded in the decision document
  - [ ] open points marked as open, not smoothed over
- **Verification:** review by the client
- **Evidence:** decision document with date
- **Executor:** `human`
- **Depends on:** T5
- **NFR:** none
- **Steps:**
  - [ ] prepare the questions
  - [ ] conduct the interview
  - [ ] record the answers
```

Verification is optional for human tasks; here it is present because the
output is a document that someone must accept.

## Task with human-agent pairing

```markdown
### T10 — CI-pipeline for exam-checker set up
- **Source:** ci-pipeline-rationale 2026-09-12
- **In:** test and lint steps on GitHub Actions
- **Out:** deploy pipelines; release workflows
- **Acceptance criteria:**
  - [ ] the workflow runs lint + tests on every PR
  - [ ] merging is blocked when checks are red (repository setting, human step below)
  - [ ] the test step runs without outbound network access
- **Verification:** open a test PR, check the block on red tests, and confirm the test step runs without outbound network access
- **Evidence:** workflow file + screenshot of the block
- **Executor:** `agent-human`
- **Limits:** only `.github/workflows/`; no secrets changes; no repository settings
- **Rollback:** workflow file via git; disable the protection rule via repository settings
- **Depends on:** T2
- **NFR:** own criterion
- **Steps:**
  - [ ] agent: generate the workflow file
  - [ ] human: review and commit
  - [ ] human: set the required status check in branch protection
  - [ ] agent: open a test PR
  - [ ] human: assess the block
```

Note the split of concerns: the acceptance criterion "merging is blocked" is a
repository setting, not a workflow change. The task therefore has an explicit
human step for branch protection and its Limits bar the agent from touching
repository settings. Limits and steps must together be able to reach every
acceptance criterion.

## Edge case: task that must not be split further but looks large

```markdown
### T4 — Legal base elements linked to exam fields
- **Source:** legal-base-elements.md v2026-09-01
- **In:** mapping of 12 elements to exam fields, including the mapping table
- **Out:** checking existing exams; migration of old data
- **Acceptance criteria:**
  - [ ] the mapping table covers all 12 elements, each exactly once
  - [ ] a missing element blocks the check with an explicit error
- **Verification:** `pytest tests/test_legal_mapping.py -q`
- **Evidence:** red test run, green test output, mapping table in `mapping/legal_elements.json`
- **Executor:** `agent`
- **Limits:** only `mapping/` and `tests/test_legal_mapping.py`
- **Rollback:** branch `feat/t4-legal-mapping`
- **Depends on:** none
- **NFR:** none
- **Steps:**
  - [ ] build the mapping table from the source
  - [ ] write red tests for missing and duplicate elements
  - [ ] implement the mapping
  - [ ] keep the test run and coverage table
```

One deliverable (the mapping) even though it covers twelve elements. Splitting
per element would produce twelve tasks with identical acceptance criteria and
no standalone value — that would violate Independent and Valuable in the other
direction. This is a terminal task through rule 3 (not rule 1) of
[splitting-rules.md](splitting-rules.md): splitting per element keeps the
meaning of "a mapping", but the contracts would be identical.
