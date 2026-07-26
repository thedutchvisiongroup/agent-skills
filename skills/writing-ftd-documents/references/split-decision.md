# FSD/TSD vs Combined FTD — Decision Tree

## Contents
- When to split into separate documents
- When to keep combined
- Decision tree
- Traceability rule when splitting
- Note on terminology

## Note on terminology

This skill uses **TSD** (Technical Specification Document) for the technical part of a split. The acronym **TDD** is avoided because in a development context it is the standard abbreviation for Test-Driven Development, which causes ambiguity. "TSD" and "TDD" should never be used interchangeably in an FTD.

## Note: FSD/TSD split vs multi-file bundle

Two orthogonal "splits" exist — do not conflate them:

- **FSD/TSD split (this reference):** split by **audience and approval flow** (functional vs technical stakeholders, separate sign-off). Driven by supplier boundaries and compliance traceability.
- **Enterprise multi-file bundle (SKILL.md Phase 2):** split by **size and consumption** — one design, multiple files behind an OKF `index.md`, so humans review per part and agents load only the relevant slice. Driven by the size budget.

They combine freely: an enterprise design can be a split FSD+TSD where each document is itself a bundle.

## When to split into separate documents

- Produce a separate **Functional Design Document (FSD)** and **Technical Specification Document (TSD)** when ANY of:

- Multiple suppliers or teams with separate approval flows (e.g. business approves FSD, architecture approves TSD)
- Regulatory or procurement traceability requires separate functional and technical sign-off
- The functional design is stable but technical decisions are still evolving (or vice versa)
- The FSD will be shared with stakeholders who should not see technical detail (procurement, legal, end-user representatives)
- Enterprise scenario with compliance evidence that maps to functional requirements separately from technical controls

## When to keep combined as one FTD

Produce a single **combined FTD** when ALL of:

- One team or supplier owns both functional and technical design
- Single approval workflow (one sign-off covers both)
- No regulatory need for separation
- The audience benefits from seeing functional and technical in one place (smaller scope, faster review)
- Feature or most project scenarios

## Decision tree

```
Start
  │
  ▼
Is this an enterprise scenario with multiple suppliers
or separate approval workflows?
  │
  ├─ YES → SPLIT (FSD + TSD)
  │
  └─ NO
       │
       ▼
  Does a regulatory or procurement framework require
  separate functional vs technical traceability?
       │
       ├─ YES → SPLIT (FSD + TSD)
       │
       └─ NO
            │
            ▼
       Will the functional design be shared with
       stakeholders who should not see technical detail?
            │
            ├─ YES → SPLIT (FSD + TSD)
            │
            └─ NO → COMBINED FTD
```

## Default proposal by scenario

| Scenario | Default proposal | Rationale |
|----------|------------------|-----------|
| feature | Combined FTD | Single team, small scope, no separation benefit |
| project | Combined FTD (unless multiple suppliers) | One approval flow usually sufficient |
| enterprise | Propose SPLIT (FSD + TSD) | Multiple suppliers, compliance traceability, separate approval flows likely |

**The user always decides.** The agent proposes based on the tree; the user confirms or overrides. Record the decision and rationale in the FTD's document control section.

## Traceability rule when splitting

When producing separate FSD and TSD:

- The **FSD** owns: scope, user stories, acceptance criteria, business rules, wireframes, business context, traceability matrix (requirements side)
- The **TSD** owns: architecture, data model, API, NFRs, privacy-by-design, security-by-design, deployment, observability, risk register
- A **shared traceability matrix** links every FSD requirement to its TSD design component and test
- Both documents reference each other by ID and version
- The FSD is approved first; the TSD references the approved FSD version

```
FSD v1.0 (approved)
  │
  ├── US-01 ──┐
  ├── US-02 ──┤
  └── US-03 ──┤
              │
              ▼
        Traceability matrix
              │
              ▼
  TSD v1.0 (references FSD v1.0)
    ├── Component A implements US-01, US-02
    ├── Component B implements US-03
    └── Tests TC-01..TC-05 verify US-01..US-03
```

## Anti-patterns

- Splitting for no reason: adds overhead without value. If the team is one and the approval is one, keep combined.
- Combining when procurement requires separation: creates compliance gaps.
- Splitting but losing traceability: the matrix must connect both documents or requirements go orphaned.
- Letting the agent decide silently: the decision is always the user's, with the agent's proposal.
