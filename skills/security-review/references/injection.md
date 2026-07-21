# Injection

Read this during Phase 4, class 1. Injection is the #2–#10 cluster of the CWE Top 25 (2025): SQLi (#2), OS command (#9), code injection (#10), command injection (#23) — plus deserialization (#15) and path traversal (#6).

## Contents

- What It Is
- Sink/Guard Table per Interpreter
- Detection Patterns (language-agnostic)
- Deserialization
- Path Traversal
- Second-Order Injection
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Injection occurs when untrusted data is interpreted as instructions by an interpreter (database, shell, template engine, expression language, file parser). The data crosses the trust boundary into the interpreter without a sink-appropriate guard.

**Universal detection shape:**

```
untrusted SOURCE → command/query/template STRING CONSTRUCTION → INTERPRETER (sink)
```

The guard that matters is almost never "validation" — it is **keeping data and instructions separated** (parameterization, prepared statements, structured APIs) or interpreter-specific escaping as a distant second choice.

## Sink/Guard Table per Interpreter

| Interpreter | Sink shapes (any language) | Correct guard | Insufficient guards |
|-------------|---------------------------|---------------|---------------------|
| SQL | query strings built with concatenation/interpolation; raw query APIs; stored-proc string building | parameterized queries / bound parameters for ALL values | escaping quotes, blocklists, "numeric check" on some params only |
| NoSQL | query objects built from request bodies; operator keys from user input; where-clauses from strings | strict schema/allow-list of fields+operators; never pass user objects as query fragments | type checks only; stripping `$` keys partially |
| ORM | raw-SQL escape hatches; dynamic ORDER BY/column names from user input; string-built filters | ORM query builder with bound values; allow-list for sortable columns | "ORMs are always safe" (false — raw fragments bypass) |
| OS shell | subprocess/exec/system/spawn with a command STRING; shell=True-style flags | exec with argument ARRAY, no shell; full paths; allow-listed commands | quoting/escaping args by hand; blocklisting metacharacters |
| Code eval | eval, exec, compile-then-run, dynamic class/function loading from names, expression-language evaluation | do not evaluate untrusted input; use data-driven dispatch (maps/allow-lists) | sandboxing by regex; "the input is trusted internally" |
| Template engines | rendering a template STRING that contains user input; server-side template injection (SSTI) | render user DATA inside fixed templates, never user input AS template | escaping HTML inside templates (wrong layer) |
| LDAP/XML/XPath | filter/query strings built by concatenation | parameterized/escaped APIs per interpreter; disable external entities for XML (XXE) | blocklisting special chars |
| Headers/logs | CRLF in headers, log forging via newlines | reject/encode CR/LF in values used in headers | length limits only |

## Detection Patterns (language-agnostic)

1. **Concatenation into interpreter calls** — any string-building operator (`+`, interpolation, format strings, template literals) inside an argument that reaches a query/shell/eval/render call. Trace the interpolated values to a source.
2. **User-controlled object keys/operators** — request bodies passed (deep-)unchecked into NoSQL queries, search filters, or update operators.
3. **Dynamic dispatch from user strings** — function/class/module/method selected by name from user input (`getattr`-style, `constantize`-style, reflection, plugin loaders).
4. **Shell flags** — process-spawn calls with shell interpretation enabled, or a single string containing the whole command line.
5. **Dangerous one-liners** — eval-like constructs, `Function(...)`-style constructors, expression evaluators (rule engines, SpEL/OGNL-style) receiving user data.
6. **Mass string building** — queries/commands assembled across helper functions (trace through helpers; the sink may be far from the source).

## Deserialization

Reconstructing objects from untrusted bytes is injection into the runtime's object graph.

- **Native/binary deserializers on untrusted data** (language object serialization, pickle-style, marshal-style, Java/.NET serialization) are Critical-class sinks when reachable from a source. Flag them even without a known gadget chain — research the ecosystem's gadget situation (Phase 5).
- **Data-only formats** (JSON) are safer, but watch: type-coercion quirks, constructor hooks, `__proto__`/prototype keys, polymorphic type fields (`$type`, `@class`) — these re-enable object-graph attacks.
- **YAML/XML parsers**: default-unsafe modes exist (arbitrary object construction in YAML; external entities in XML). Verify the parser is configured to the safe mode — the default is often wrong. This is version-specific: RESEARCH the parser + version (Phase 5).

## Path Traversal

Filesystem-path construction from untrusted input is injection into the filesystem namespace.

- **Sinks**: open/read/write/delete/append, file inclusion (`include`/`require`-style), archive extraction (zip/tar — "zip slip" entries with `../`), symlink following.
- **Guard that works**: canonicalize/resolve the final path AND verify containment within the intended base directory (prefix check on the RESOLVED path, handling symlinks). String-level `../` stripping fails (encoding, double-encoding, absolute paths, Windows/Unicode quirks).
- **Also check**: user-controlled file extensions for writes, null bytes (legacy runtimes), path normalization differences between validation and use.

## Second-Order Injection

Payloads stored first and interpreted later: user input → database/file → later read → query/HTML/shell sink. The guard must exist at the SECOND use, not (only) at input time. When you find a stored-value sink, trace where the value was WRITTEN to establish the source.

## False-Positive Guidance

Do NOT report when:

- Parameterization/binding is used for EVERY value (identifiers like table/column names are NOT parameterizable — those need allow-lists; check that instead).
- The "source" is a compile-time constant or config fully controlled by the deployer (note the assumption).
- The ORM/builder call is provably structured (no raw fragments).
- The spawn uses argv-array form with a fixed executable and no shell.

Downgrade, don't drop: if MOST values are bound but one interpolated identifier lacks an allow-list, report the identifier path specifically.

## Mandatory Online Research Triggers

- Parser/serializer default safety for the exact library+version (YAML, XML, JSON polymorphic typing) — per `online-research-protocol.md`.
- Deserialization gadget-chain status for the ecosystem (Java, .NET, PHP, Python, Ruby, Node) when native deserialization of untrusted data is found.
- Expression-language/template-engine SSTI techniques for the detected engine (each engine has distinct exploitation).
- Any interpreter API you do not fully recognize (trigger #1 of the protocol).

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| SQL injection | CWE-89 (Top 25 #2, 2025) | A05:2025 Injection |
| OS command injection | CWE-78 (#9) / CWE-77 (#23) | A05:2025 |
| Code injection / eval | CWE-94 (#10) | A05:2025 |
| Template injection (SSTI) | CWE-94 / CWE-1336 | A05:2025 |
| LDAP/XPath/XML injection, XXE | CWE-90/643/611 | A05:2025 |
| Deserialization of untrusted data | CWE-502 (#15) | A05:2025 / A08:2025 |
| Path traversal | CWE-22 (#6) | A05:2025 / A01:2025 |
| CRLF/header injection, log forging | CWE-93/113/117 | A05:2025 / A09:2025 |
| ASVS | V1 (Encoding and Sanitization), V5 (File Handling) | — |
