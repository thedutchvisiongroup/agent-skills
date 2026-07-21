# Dataflow and Taint Analysis

Read this at the start of Phase 4. This is the review method: every other reference assumes you apply it.

## Contents

- The Model
- Sources (where untrusted data enters)
- Sinks (where it becomes dangerous)
- Guards (sanitizers, validators, authorization)
- Trust Boundaries
- The Tracing Procedure
- Confidence Assignment
- Worked Example (language-agnostic)
- Common Tracing Failures

## The Model

Nearly every code-level vulnerability has one shape:

```
SOURCE  ──(data crosses trust boundary)──▶  SINK
                 without adequate GUARD
```

- **Source** — a location where data you do not control enters the program.
- **Sink** — an operation that is dangerous when reached by attacker-influenced data.
- **Guard** — anything that makes the data safe for that specific sink: sanitization, escaping, parameterization, validation, authorization, allow-listing.

A source-to-sink path without an adequate guard is a **candidate finding**. A candidate becomes a **finding** when you have verified the path in context.

> Language-agnostic rule: do not ask "does this code look dangerous?" Ask "where does this value come from, and where can it end up?"

## Sources (where untrusted data enters)

Treat ALL of these as untrusted, regardless of language or framework:

| Category | Examples |
|----------|----------|
| HTTP/RPC input | request bodies, query params, path params, headers (incl. `Host`, `X-Forwarded-*`, `User-Agent`, `Referer`), cookies |
| Client-side storage | localStorage/sessionStorage values sent back, hidden form fields, JWT payloads (until signature-verified) |
| Files | uploaded files, parsed documents (XML/JSON/CSV/YAML/images/archives), file paths from users |
| Environment & config | env vars, config files writable by others, CLI arguments |
| Network responses | third-party API responses, database rows that contain prior user input (second-order), message-queue payloads, webhook bodies |
| Deserialized data | anything unmarshalled/unserialized/decoded from external bytes |

**Second-order sources matter:** data read from YOUR OWN database is untrusted if it was ever user-supplied. Stored XSS and second-order SQLi live here.

## Sinks (where it becomes dangerous)

| Sink family | Operation shape | Vulnerability class |
|-------------|-----------------|---------------------|
| Query interpreter | SQL/NoSQL/LDAP/XPath/graph query construction | Injection |
| Command execution | shell/subprocess/process spawn | Command injection |
| Code evaluation | eval, template rendering, dynamic import/load, expression languages | Code/template injection |
| HTML/JS output | markup generation, DOM writes, redirects | XSS / open redirect |
| Filesystem | path open/read/write/delete, archive extraction | Path traversal, unsafe upload |
| Network egress | HTTP client calls, URL fetches, redirects | SSRF, open redirect |
| Deserialization | bytes → object reconstruction | Deserialization attacks |
| Authorization decisions | resource lookup by user-controlled key, role checks | IDOR/BOLA, privilege escalation |
| Cryptographic operations | encrypt/sign/hash with weak or misused primitives | Cryptographic failures |
| Logs & errors | log statements, exception messages returned to users | Information disclosure |

Each class reference has its own detailed sink table — this one is the map.

## Guards (what makes a path safe)

A guard is only valid if it **matches the sink**. The right guard for SQL is not the right guard for HTML.

| Guard | Effective for | NOT effective for |
|-------|---------------|-------------------|
| Parameterized queries / bound parameters | SQL injection | NoSQL operator injection, ORM raw fragments |
| Context-aware output encoding | XSS | Injection into SQL/shell |
| Allow-list validation (strict set) | most sinks | nothing, if the list is wrong |
| Type/length/range validation | resource consumption, logic abuse | injection |
| Authorization check on THIS object + THIS action | IDOR/BOLA | injection |
| Escaping for the target interpreter | shell/LDAP/XPath | XSS (wrong context) |
| Canonicalization + containment check | path traversal | anything else |

**Verify, don't assume:** when code claims a guard exists ("input is validated upstream"), trace to the actual guard and confirm it covers THIS sink for THIS data. Assumed sanitization is exploitation fuel.

### Guard red flags

- Blocklist-based filtering (attackers enumerate around blocklists)
- Home-grown escaping/encoding where the platform provides a vetted one
- Validation that checks format but not authorization
- Sanitization applied at input time for a sink that needs output-time encoding (stored XSS)
- Guards that can be bypassed by encoding tricks (double-encoding, Unicode, null bytes)

## Trust Boundaries

A trust boundary is any line across which control of data changes hands:

- network → application (requests, webhooks)
- application → interpreter (SQL, shell, template, XML)
- application → filesystem
- application → third-party service and back
- privileged code ↔ unprivileged data (authorization decisions)
- process → process (IPC, deserialization)

**Rule:** every crossing needs either a guard on the data or an explicit, verified reason none is needed.

## The Tracing Procedure

Work sink-first (backward tracing) — it scales better than reading every line hoping to spot danger:

1. **Enumerate sinks** in scope for the current vulnerability class (grep/structure — e.g. every query call, every shell spawn, every DOM write).
2. **For each sink, trace its inputs backward** to their origin. Ask at each hop: "who controls this value?"
3. **Classify each hop**: source (untrusted), transformed (how?), or constant (safe).
4. **Check the guards** on every untrusted path: does an adequate, sink-appropriate guard exist on EVERY path from source to this sink?
5. **Verdict per sink**: safe (guard verified), candidate finding (guard missing/broken), or uncertain (→ Phase 5 research or "Could NOT verify").
6. **Record the trace** for every candidate: `source → transforms → sink` with file:line at each hop. This trace IS your evidence.

For second-order flows, trace through the store: `source → database/file → later read → sink`.

## Confidence Assignment

| Confidence | Meaning | Action |
|------------|---------|--------|
| Confirmed | Full source→sink trace verified in code; no adequate guard on any path | Report as finding |
| High | Trace verified; guard exists but is demonstrably inadequate for this sink | Report as finding |
| Medium | Trace likely but a hop is unclear (dynamic dispatch, framework magic) | Phase 5 research if impact is High+; else report with caveat |
| Low | Suspicion without a complete trace | Phase 5 research if potential impact is High/Critical; otherwise "Could NOT verify" section |

**Never upgrade confidence by intuition. Upgrade it by evidence or research.**

## Worked Example (language-agnostic)

Pseudo-code — the shapes exist in every language:

```
function getOrder(request):
    orderId = request.params["id"]                        # SOURCE (untrusted)
    query  = "SELECT * FROM orders WHERE id = " + orderId # transform: string concat (NO GUARD)
    rows   = db.execute(query)                            # SINK: query interpreter
    return rows

function getOrderSafe(request):
    orderId = request.params["id"]                        # SOURCE
    rows   = db.execute("SELECT ... WHERE id = ?", [orderId])  # SINK with GUARD: parameterization
```

Trace for the first: `request.params["id"] (source) → string concatenation (no guard) → db.execute (sink)` = **candidate finding: SQL injection**, severity High/Critical depending on reachability, confidence Confirmed if reachable.

For the second: parameterization is the sink-appropriate guard → safe, no finding.

## Common Tracing Failures

| Failure | Consequence | Counter |
|---------|-------------|---------|
| Stopping at framework boundaries ("the framework handles it") | Missed classes (frameworks protect specific sinks, not all) | Verify WHICH sinks the framework guards; trace the rest |
| Ignoring second-order sources | Missed stored XSS / second-order injection | Treat DB reads of user-origin data as sources |
| Assuming middleware covers every route | Missed authorization (CWE-862) | Verify coverage per route/handler |
| Tracing only the happy path | Missed flows via error handlers, alternate endpoints, batch paths | Enumerate ALL paths to the sink |
| Giving up on dynamic dispatch | "Could NOT verify" sections stay empty and wrong | Research the framework's dispatch (Phase 5) or mark explicitly unverifiable |
| Treating validation as sanitization | Format checks don't neutralize payloads | Match guard type to sink type |
