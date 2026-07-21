# XSS and Output Encoding

Read this during Phase 4, class 2. XSS is CWE-79 — #1 on the CWE Top 25 (2025). It is injection where the interpreter is the browser. The fix-class is always the same: the right encoding for the right output context, applied at output time.

## Contents

- What It Is
- Output Contexts (the core of correct review)
- Sink Table
- Detection Patterns
- Stored, Reflected, DOM-based
- CSP and Defense-in-Depth Signals
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

XSS occurs when untrusted data is written into an HTML/JS execution context without context-appropriate encoding. The browser cannot distinguish "data" from "markup/code" — encoding is what preserves the distinction.

**Universal detection shape:**

```
untrusted SOURCE → output/write into HTML, JS, attribute, URL, or CSS context → BROWSER (sink)
                  without context-appropriate encoding at output time
```

## Output Contexts (the core of correct review)

Encoding correctness is context-dependent. "Escaped" is meaningless until you name the context.

| Context | Example position | Required guard |
|---------|------------------|----------------|
| HTML body | `<div>HERE</div>` | HTML-entity encoding (`<`, `>`, `&`, quotes) |
| HTML attribute | `<div title="HERE">` | attribute encoding + ALWAYS quote attributes; unquoted attributes are findings |
| JavaScript string | `<script>var x = "HERE"</script>` | JS string encoding; better: never inline data into script — pass via JSON-serialized, safely-encoded data blocks |
| URL / href | `<a href="HERE">` | URL validation (scheme allow-list: `http`, `https`, `mailto`...) + encoding; `javascript:`/`data:` schemes are the payload |
| CSS | `style="...HERE..."` | CSS encoding; treat as high-risk context |
| Rich HTML (editor output) | user HTML rendered | dedicated allow-list HTML sanitizer library ONLY — never regex/blocklist |

## Sink Table

| Sink family | Shapes (any language/framework) |
|-------------|--------------------------------|
| Server-side templates | raw/unescaped output markers (every engine has one: `| safe`, `{!! !!}`, `<%= raw %>`, `dangerouslySet...`, `[innerHTML]` bindings, `v-html`-style directives) |
| DOM writes | `innerHTML`, `outerHTML`, `document.write`, `insertAdjacentHTML`, jQuery-style `.html()`, location/hash-driven DOM updates |
| Redirects | user-controlled redirect targets (open redirect — often phishing-critical) |
| Response construction | hand-built HTML strings, JSONP callbacks from user input, user-controlled `Content-Type` |
| Client frameworks | any "render raw HTML" escape hatch; markdown renderers with embedded-HTML enabled and no sanitizer |

## Detection Patterns

1. **Raw-output markers** in templates — grep for the engine's unescaped-output syntax; trace each usage's value to a source.
2. **Auto-escaping disabled** — escaping turned off globally or per-template ("autoescape off", safe-by-default strings).
3. **String-built HTML** — markup assembled by concatenation in code, emailed HTML, server-rendered fragments.
4. **DOM sink with user data** — client-side writes of values derived from URL, storage, messages (`postMessage`), or API responses containing user-generated content.
5. **Markdown/rich-text rendering** without a sanitizer (allow HTML passthrough + no allow-list sanitizer = XSS).
6. **User-controlled URLs in attributes/redirects** — missing scheme allow-list.
7. **Reflected values in responses** — error pages, search pages, and form re-rendering echoing request data.

## Stored, Reflected, DOM-based

- **Reflected**: request value → immediate response. Trace request sources to response sinks.
- **Stored**: user value → database/file → later rendered into pages (often for OTHER users/admins — higher severity). The guard must be at OUTPUT time; input-time-only encoding corrupts data and still fails other contexts. Check the render path, not the input path.
- **DOM-based**: source and sink both client-side (URL fragment → DOM write). Review client code with the same source→sink discipline.

## CSP and Defense-in-Depth Signals

Content-Security-Policy mitigates but never replaces encoding. Note in the report (not as findings by themselves):

- **Missing CSP** on HTML responses — a hardening gap (Low/Medium).
- **CSP with `unsafe-inline`/`unsafe-eval`** or wildcard sources — weak mitigation.
- Reliance on CSP to justify raw output — NOT acceptable; flag the underlying missing encoding.

## False-Positive Guidance

Do NOT report when:

- The framework's auto-escaping is verifiably active for that template/context AND the value passes through no raw marker.
- The value is serialized via the platform's safe JSON-embedding mechanism for script contexts.
- A vetted allow-list HTML sanitizer (current, maintained) processes the rich-text output. Verify it's actually invoked on the output path.
- The value is provably numeric/boolean typed (typed, not just validated-looking).

Watch for **double encoding** and **mutation XSS** (sanitized HTML mutated by the browser into payloads) — rare; if suspected, research (Phase 5).

## Mandatory Online Research Triggers

- The detected template engine/framework's raw-output syntax and auto-escaping defaults for its version (defaults differ; RESEARCH, don't assume).
- Sanitizer library currency: known bypasses for the detected sanitizer+version.
- Markdown parser HTML-passthrough defaults.
- Any unfamiliar raw-output marker or client-framework escape hatch (protocol trigger #1).

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| XSS (all forms) | CWE-79 (Top 25 #1, 2025) | A05:2025 Injection |
| Open redirect | CWE-601 | A01:2025 / API8:2023-adjacent |
| Improper neutralization in attributes/headers | CWE-83/113 | A05:2025 |
| Missing/weak CSP (hardening gap) | CWE-1021/693 | A02:2025 Security Misconfiguration |
| ASVS | V1 (Encoding and Sanitization), V3 (Web Frontend Security) | — |
