# Intake Question Bank

## Contents
- How to use this reference
- Scope dimension
- Functional dimension
- Technical dimension
- Output dimension (the five mandatory questions)
- Probing techniques

## How to use this reference

This is a question **bank**, not a script. The intake is a free conversation — pick questions relevant to what is already known. Other skills may have gathered context (research, codebase analysis, prior FTDs); use that as input and do not re-ask answered questions. Keep probing until each dimension is fully clear. Vague answers are not answers.

## Scope dimension

Goal: establish a crisp boundary of what is in and out.

- What is the problem or opportunity this FTD addresses?
- What is explicitly **in scope**? (List components, teams, data, processes)
- What is explicitly **out of scope**? (Adjacent work that someone might assume is included)
- What is the boundary? Where does this system start and stop interacting with the outside world?
- What is the success criterion? How will we know the design is complete and correct?
- What happens if we do nothing? (Status quo cost)
- Are there dependencies on other projects or FTDs?
- Is there a hard deadline or budget cap that constrains the design?

## Functional dimension

Goal: understand who the users are and what the system must do for them.

- Who are the personas / user roles? (Named, not "the user")
- For each persona: what is their goal, what is their pain today, what changes for them?
- What are the user stories? (Capture in "As a…/I want…/So that…" or Dutch equivalent)
- What are the business rules that govern behaviour?
- What are the edge cases? (What happens when input is wrong, missing, or adversarial?)
- What workflows or processes must the system support?
- What data does the user create, read, update, or delete?
- What notifications, reports, or exports are expected?
- Are there accessibility requirements? (WCAG 2.1 AA is the enterprise default)
- What is the multilingual requirement? (UI labels vs document content)

## Technical dimension

Goal: understand the existing world and what changes.

- What is the existing architecture? (Provide or link a C4 Context diagram if one exists)
- What components change, what is new, what is deprecated?
- What is the data model today, and what must it become? (ERD)
- What integrations exist or are needed? (APIs, message queues, file transfers, ETL)
- What are the technical constraints? (Tech stack, hosting, network, budget, time)
- What are the non-functional expectations? Probe each:
  - **Performance**: p95 latency targets, throughput, concurrent users
  - **Availability**: uptime target (e.g. 99.9%), maintenance windows
  - **Security**: which threats, which framework (OWASP ASVS level, ISO 27001, BIO, NEN 7510)
  - **Privacy**: is personal data involved? Special categories (health, biometric)? DPIA triggers?
  - **Scalability**: expected growth over 1-3 years
  - **Maintainability**: who will operate this, what is their skill level
  - **Compliance**: AVG, NEN 7510, BIO, ISO 27001, EU AI Act — which apply
- What is the deployment target? (Cloud, on-prem, hybrid, edge)
- What is the rollback plan if the release fails?
- What observability is required? (Logs, metrics, traces, dashboards, alerts)
- Are there migrations from existing systems? (Data, users, cutover)
- What is backwards-compatibility expectation? (API consumers, stored data)

## Output dimension (the five mandatory questions)

These MUST be asked in every intake, regardless of scenario. If the user already answered one unprompted, confirm it explicitly rather than skipping it.

### 1. FSD/TSD split vs combined FTD

> "Should we produce two separate documents (functional design + technical design) or one combined FTD?"

Propose a default based on the scenario and the [split-decision.md](split-decision.md) decision tree:
- **feature**: combined FTD (almost always)
- **project**: combined FTD unless multiple suppliers with separate approval flows
- **enterprise**: propose split (separate FSD and TSD) when supplier boundaries or compliance traceability demand it

**The user always decides.** Record their choice and rationale.

### 2. Output language

> "In which language should the FTD be written — English (default, 'As a…/I want…/So that…') or Dutch ('Als…/wil ik…/zodat…')?"

### 3. Output mode

> "Which output mode: Markdown only, HTML only, or both? Markdown is the baseline with OKF frontmatter and Mermaid diagrams (for humans AND agents); HTML is a self-contained portable file for human presentation. If both, I draft Markdown first then generate HTML from it."

### 4. Acceptance criteria format

> "Which acceptance criteria format: simple bullet lists (default) or EARS notation? EARS is recommended for enterprise and regulated contexts where unambiguous requirement sentences are needed."

See [acceptance-criteria.md](acceptance-criteria.md) for both formats. **The user always decides.** Record the choice — it is written into the document as an `<!-- ac-format: bullets|ears -->` marker.

### 5. Filename and storage location

> "What filename convention should I use? Suggested: `FTD-[project]-[feature]-vX.Y.{md,html}` — or, for enterprise, the bundle directory `FTD-[project]/`. Where should I save the file(s)?"

## Probing techniques

Vague answers are not answers. Use these techniques to convert vagueness into measurable scope:

| Vague answer | Probe |
|--------------|-------|
| "It should be fast" | "What does fast mean — p95 latency target under which concurrent load?" |
| "It should be secure" | "Against which threats? Complying with which framework (OWASP ASVS, ISO 27001, BIO, NEN 7510)?" |
| "It should scale" | "From what to what, over which timeframe? Concurrent users, data volume, request rate?" |
| "We need to be GDPR-compliant" | "Which personal data specifically? Is a DPIA triggered? Who is the DPO?" |
| "The users are everyone" | "Name the distinct personas and their goals. 'Everyone' is not a persona." |
| "It's a small change" | "Which components, which teams, which data? Does it touch regulated data or external suppliers?" |
| "We'll figure out NFRs later" | "An FTD without measurable NFRs cannot be validated. Let's set minimum thresholds now and refine during draft." |

## When to stop probing

Stop when, for every dimension, you can write a one-paragraph summary that the user would confirm as accurate and complete. If you cannot write that summary, you do not have enough — keep probing.
