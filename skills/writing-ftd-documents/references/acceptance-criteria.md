# Acceptance Criteria

## Contents
- Format choice (bullets vs EARS)
- Format 1: Bullet lists (default)
- Format 2: EARS notation
- INVEST for user stories
- Examples (EN + NL) — bullets
- Examples (EN + NL) — EARS
- Edge case handling
- Anti-patterns

The format is chosen by the user in Phase 1 (mandatory output question 4). The agent MUST ask; never assume. Both formats produce testable, verifiable criteria — the difference is in precision and formality.

## Format choice (bullets vs EARS)

| Aspect | Bullets | EARS |
|--------|---------|------|
| **When to use** | Default; feature and most project scenarios; when the team prefers readability | Enterprise, regulated, or safety-critical contexts; when requirements must be unambiguous and individually traceable |
| **Precision** | High (one testable statement per bullet) | Very high (structured syntax removes ambiguity) |
| **Learning curve** | None | Low — 5 patterns to learn |
| **Tooling** | None required | Optional: EARS-compatible requirement tools; works in plain markdown |
| **Gherkin** | Not used (see anti-patterns) | Not used — EARS is a separate, lighter notation |

**Rule:** whichever format is chosen, ALL acceptance criteria in a single FTD MUST use the same format. Do not mix bullets and EARS within one document.

## Format 1: Bullet lists (default)

Acceptance criteria as **bullet lists**. Each bullet is a single, testable statement.

**Rules:**
- One criterion per bullet. No compound statements with "and".
- Each criterion must be verifiable by a test, a demo, or an inspection.
- State the expected behaviour, not the implementation.
- Include boundary values and error paths, not just the happy path.
- Write in active voice: "The system rejects...", not "It should be rejected".

## Format 2: EARS notation

EARS (Easy Approach to Requirements Syntax) is a lightweight notation for writing unambiguous requirement sentences. It was developed by Alistair Mavin and is widely adopted in requirements engineering, especially in regulated and safety-critical contexts.

### The 5 EARS patterns

Each acceptance criterion is a single sentence matching one of five patterns. The verb is always "**shall**" (normative, testable).

#### 1. Ubiquitous

Always true; no trigger condition.

```
The <system> shall <response>.
```

**EN example:** The system shall log every authentication attempt to the audit log.
**NL example:** Het systeem shall elke authenticatiepoging vastleggen in de audit log.

> Dutch note: EARS uses English "shall" as the normative verb. In Dutch-language FTDs, you may use "zal" or keep "shall" (common in Dutch technical writing). Be consistent within the document.

#### 2. State-driven

True while a specific state holds.

```
While <state>, the <system> shall <response>.
```

**EN example:** While the system is in maintenance mode, the system shall return HTTP 503 with a Retry-After header of 300 seconds.
**NL example:** While het systeem zich in onderhoudsmodus bevindt, the system shall HTTP 503 teruggeven met een Retry-After header van 300 seconden.

#### 3. Event-driven

Triggered by an event.

```
When <event>, the <system> shall <response>.
```

**EN example:** When a CSV file larger than 10 MB is uploaded, the system shall reject it with HTTP 413 and a message stating the size limit.
**NL example:** When een CSV-bestand groter dan 10 MB wordt geüpload, the system shall dit weigeren met HTTP 413 en een melding met de maximale bestandsgrootte.

#### 4. Optional feature

Triggered by a configurable feature or condition.

```
Where <feature is included>, the <system> shall <response>.
```

**EN example:** Where multi-factor authentication is enabled, the system shall require a one-time code on every admin login.
**NL example:** Where multi-factor authenticatie is ingeschakeld, the system shall bij elke admin-login een eenmalige code vereisen.

#### 5. Unwanted behaviour

Triggered by an unwanted condition; specifies the safe response.

```
If <unwanted condition>, then the <system> shall <response>.
```

**EN example:** If the database connection is lost, then the system shall return HTTP 503, log the incident, and queue pending writes for retry.
**NL example:** If de databaseverbinding verloren gaat, then the system shall HTTP 503 teruggeven, het incident loggen, en openstaande schrijfacties in de wachtrij plaatsen voor retry.

### EARS rules

- **One pattern per criterion.** Do not combine patterns ("When X and while Y, the system shall Z" is not valid EARS).
- **Always "shall".** Never "should", "must", "will", or "may" in EARS. "Shall" is the normative verb.
- **Response must be observable and testable.** "Shall handle errors gracefully" is not EARS — specify the response.
- **Include all relevant conditions.** If the behaviour depends on state AND event, use the event-driven pattern and include the state in the event description, or split into two criteria.

### When to prefer EARS over bullets

- **Enterprise scenario** — EARS makes requirements individually traceable to compliance controls.
- **Regulated context** (medical, government, finance) — auditors expect "shall" statements.
- **Safety-critical** — ambiguity in safety requirements is unacceptable.
- **When the user chose EARS in Phase 1** — always respect the user's choice.

## INVEST for user stories

Every user story is checked against INVEST before it enters the FTD:

| Letter | Criterion | Fail signal |
|--------|-----------|-------------|
| **I**ndependent | Can be delivered without depending on another story in the same sprint | "Story A must be done before Story B can start" within the same sprint |
| **N**egotiable | Leaves room for the team to find the best implementation | Prescribes a specific technical solution |
| **V**aluable | Delivers visible value to a stakeholder | "Refactor the database" with no user-facing outcome |
| **E**stimable | The team can size it with reasonable confidence | Unknown scope, missing acceptance criteria |
| **S**mall | Fits in a single sprint (≤ ½ of sprint capacity) | Multi-sprint effort not split |
| **T**estable | Has clear acceptance criteria that can be verified | "It should work well" |

If a story fails INVEST, rewrite or split it before including in the FTD.

## Examples (EN + NL) — bullets

### English

**US-01: CSV invoice import**
- The system accepts CSV files up to 10 MB in size.
- The system rejects CSV files larger than 10 MB with HTTP 413 and a message stating the size limit.
- The system validates each row against the published schema before any row is persisted.
- The system persists all valid rows in status "New" within 5 seconds of upload for files up to 10 MB.
- The system returns a summary report listing imported row count, rejected row count, and rejection reasons.
- The system logs the importing user, timestamp, file hash, and row count to the audit log.

### Dutch

**US-02: Factuurgoedkeuring door manager**
- Het systeem toont alle facturen met status "Wacht op goedkeuring" in een lijst, gesorteerd op vervaldatum oplopend.
- Het systeem toont per factuur: leverancier, bedrag inclusief BTW, vervaldatum, en de scan van de originele factuur.
- De manager kan een factuur goedkeuren of afwijzen met een verplichte reden bij afwijzing.
- Bij goedkeuring verandert de status naar "Goedgekeurd" en ontvangt de financiële afdeling een notificatie binnen 1 minuut.
- Bij afwijzing verandert de status naar "Afgewezen" en ontvangt de indiener een notificatie met de opgegeven reden.
- Het systeem logt elke goedkeurings- of afwijzingsactie met gebruiker, tijdstip, factuur-ID, en actie in de audit log.

## Examples (EN + NL) — EARS

### English

**US-01: CSV invoice import (EARS)**
- The system shall accept CSV files up to 10 MB in size.
- When a CSV file larger than 10 MB is uploaded, the system shall reject it with HTTP 413 and a message stating the size limit.
- When a CSV file is uploaded, the system shall validate each row against the published schema before any row is persisted.
- When all rows in an uploaded CSV file pass validation, the system shall persist them in status "New" within 5 seconds of upload for files up to 10 MB.
- When the import process completes, the system shall return a summary report listing imported row count, rejected row count, and rejection reasons.
- The system shall log the importing user, timestamp, file hash, and row count to the audit log for every import.

### Dutch

**US-02: Factuurgoedkeuring door manager (EARS)**
- The system shall alle facturen met status "Wacht op goedkeuring" tonen in een lijst, gesorteerd op vervaldatum oplopend.
- The system shall per factuur tonen: leverancier, bedrag inclusief BTW, vervaldatum, en de scan van de originele factuur.
- When een manager een factuur afwijst, the system shall een verplichte reden vereisen.
- When een manager een factuur goedkeurt, the system shall de status wijzigen naar "Goedgekeurd" en de financiële afdeling binnen 1 minuut notificeren.
- When een manager een factuur afwijst, the system shall de status wijzigen naar "Afgewezen" en de indiener notificeren met de opgegeven reden.
- The system shall elke goedkeurings- of afwijzingsactie loggen met gebruiker, tijdstip, factuur-ID, en actie in de audit log.

## Edge case handling

Every story should include criteria for the edge cases, not just the happy path:

- What happens when input is empty?
- What happens when input exceeds the limit?
- What happens when a dependency is unavailable?
- What happens when the user lacks permission?
- What happens on concurrent access?

In EARS, edge cases map naturally to the **Unwanted behaviour** pattern ("If <unwanted condition>, then the system shall <response>").

## Anti-patterns

| Anti-pattern | Example | Fix |
|--------------|---------|-----|
| Compound criterion | "The system validates the file and stores it and sends a notification" | Split into three bullets or three EARS statements |
| Vague criterion | "The system should be user-friendly" | Replace with measurable: "New users complete the core flow in < 2 minutes without help" |
| Implementation-prescriptive | "The system uses Redis to cache the response" | Reframe as behaviour: "Repeated identical requests within 60s return a cached response" |
| Untestable | "The system handles errors gracefully" | Specify: "On timeout, the system returns HTTP 503 with a retry-after header of 30 seconds" |
| Happy-path only | Only criteria for valid input | Add criteria for empty, oversized, malformed, and unauthorised input |
| Hidden Gherkin | "Given a user, when they click, then..." | Rewrite as a bullet: "Clicking [button] results in [behaviour]" — or as an EARS event-driven statement |
| Mixed formats | Some criteria as bullets, some as EARS, in the same FTD | Pick one format (Phase 1, question 4) and use it consistently throughout |
| EARS with "should" | "The system should reject files over 10 MB" | Use "shall": "When a file over 10 MB is uploaded, the system shall reject it with HTTP 413" |
| EARS compound pattern | "When X and while Y, the system shall Z" | Split into two criteria, or fold the state into the event: "When X occurs while Y, the system shall Z" |
