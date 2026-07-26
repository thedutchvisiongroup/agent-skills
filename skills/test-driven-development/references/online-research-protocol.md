# Online Research Protocol

Read this during Phase 2 (language deep-dive) and whenever a doubt trigger fires. Language-specific test idioms, framework defaults, and tool behavior evolve faster than your training data. **A guess reported as a fact is worse than no report.**

## When Research Is MANDATORY

Any of these triggers forces online research before you proceed:

- You use a test framework, assertion library, mocking library, or runner feature you do not fully recognize.
- A finding or recommendation depends on **version-specific behavior** (a flag, a default, a deprecation).
- You are about to recommend a coverage or mutation tool — verify it still exists, is maintained, and supports the project's stack/version.
- You catch yourself writing "probably", "should be fine", "I think this framework…", or "as far as I know".
- The project uses a language/stack whose idioms differ from the mainstream (e.g. Go's "fakes over mocks", Rust's "traits are the seam", Elixir's `ExUnit` async nuances).
- A test keeps failing for a reason that seems framework-specific (fixture lifecycle, async setup, parallelism model, snapshot serialization).
- You propose a pattern (property-based testing, fake clock, snapshot testing) in a language where you do not know the current canonical library.

## Authoritative Sources (in priority order)

1. **The framework's official docs** for the project's actual version (pytest, jest/vitest, JUnit, xUnit/NUnit, Go testing, Rust `std::test`, etc.). Pin the version — defaults change across majors.
2. **Canonical reference sites**: `martinfowler.com` (TestDouble, GivenWhenThen, TestDrivenDevelopment, Practical Test Pyramid), `xunitpatterns.com` (Meszaros patterns), `testsmells.org`, `kentcdodds.com` (Testing Trophy).
3. **The tool's own docs** for coverage/mutation tools (coverage.py, JaCoCo, Stryker, PITest, Hypothesis, etc.).
4. **Authoritative secondary**: OWASP (for security-adjacent fuzzing), language maintainers' blogs, well-regarded conference talks (Dave Farley, Sandro Mancuso, Kent Beck).
5. **Current changelogs / release notes** when behavior is version-dependent.
6. **GitHub issues / discussions** of the framework/tool — but treat as evidence of a report, not of a verdict.

Avoid: undated blog posts, AI-generated summary spam, anything that asserts a framework behavior without a version or date. Prefer sources updated within the last ~2 years for tooling, and canonical references (Fowler, Meszaros) for principles.

## Protocol

1. **State what you need to know** in one sentence before searching.
2. **Search authoritative sources first** (above). Prefer the official docs for the exact version.
3. **Verify against the project's actual versions** — read the manifest/lockfile (`package.json`/lock, `pyproject.toml`/lock, `Cargo.lock`, `go.mod`, `pom.xml`/`build.gradle`). Distrust your memory of version numbers; your training data has a cutoff.
4. **Cross-check** a non-obvious claim against a second source.
5. **Apply** the researched pattern to the code/tests in scope.
6. **Report back** (MANDATORY): what you researched, the source(s), the version you verified against, and how it changed your work — even if the answer is "no applicable pattern". Silence is not allowed.

## Triggers That Should Make You Stop

| Thought | Action |
|---------|--------|
| "I know jest, no need to check" | Your memory is stale. Verify the current API/defaults for the project's version. |
| "Mockito works like this" | Verify against the project's Mockito version; the API changed across majors. |
| "coverage.py reports branch by default" | Verify — the flag and default have changed; branch needs `--branch`. |
| "This is probably the right Stryker config" | Check Stryker's current config schema; it has changed. |
| "Go tests just use `testify`" | Go idiom favors hand-rolled fakes over mocks; verify the project's convention. |

## Report-Back Format

For every research action, include in your report (Phase 6 online research log):
- **What** you researched (the question).
- **Source(s)** with version/date.
- **What you found** — the answer.
- **How it changed your work** — confirmed / changed / downgraded / dropped a finding or approach.
- **Could NOT verify** — items that need runtime or project-specific evidence; never present as a fact.

## What Research Is NOT For

- General programming concepts (AAA, the pyramid) — these are stable; use the references.
- Refactoring business logic — out of scope (you never edit production code).
- Security review — hand off to the `security-review` skill.

Research validates language-specific specifics; the principles in the other references are the stable foundation.
