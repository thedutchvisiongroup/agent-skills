# Acceptance Criteria

## Contents
- Format rules
- INVEST for user stories
- Examples (EN + NL)
- Anti-patterns

## Format rules

Acceptance criteria in this skill are **bullet lists**. Each bullet is a single, testable statement. Gherkin (Given-When-Then) is NOT used.

**Rules:**
- One criterion per bullet. No compound statements with "and".
- Each criterion must be verifiable by a test, a demo, or an inspection.
- State the expected behaviour, not the implementation.
- Include boundary values and error paths, not just the happy path.
- Write in active voice: "The system rejects...", not "It should be rejected".

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

## Examples

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

### Edge case handling

Every story should include criteria for the edge cases, not just the happy path:

- What happens when input is empty?
- What happens when input exceeds the limit?
- What happens when a dependency is unavailable?
- What happens when the user lacks permission?
- What happens on concurrent access?

## Anti-patterns

| Anti-pattern | Example | Fix |
|--------------|---------|-----|
| Compound criterion | "The system validates the file and stores it and sends a notification" | Split into three bullets |
| Vague criterion | "The system should be user-friendly" | Replace with measurable: "New users complete the core flow in < 2 minutes without help" |
| Implementation-prescriptive | "The system uses Redis to cache the response" | Reframe as behaviour: "Repeated identical requests within 60s return a cached response" |
| Untestable | "The system handles errors gracefully" | Specify: "On timeout, the system returns HTTP 503 with a retry-after header of 30 seconds" |
| Happy-path only | Only criteria for valid input | Add criteria for empty, oversized, malformed, and unauthorised input |
| Hidden Gherkin | "Given a user, when they click, then..." | Rewrite as a bullet: "Clicking [button] results in [behaviour]" |
