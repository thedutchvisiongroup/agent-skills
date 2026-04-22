# Progressive Disclosure Patterns

## Overview

Progressive disclosure is the principle of loading only the information needed for the current task. In skill design, this means structuring content so the agent doesn't consume context tokens on material it doesn't need right now.

**Core principle:** Load the minimum context required. Everything else stays on the filesystem until needed.

## The Three Levels

| Level | When Loaded | Token Cost | Content |
|-------|------------|------------|---------|
| **Level 1: Metadata** | Always (at startup) | ~100 tokens | `name` and `description` from YAML frontmatter |
| **Level 2: Instructions** | When skill is triggered | <5k tokens | SKILL.md body with guidance and workflows |
| **Level 3: Resources** | As needed | Effectively unlimited | Reference files, scripts, templates |

**Level 1** is the only content that's always in context. This is why the `description` field matters so much — it's the agent's only signal for deciding whether to load the rest.

**Level 2** loads when the agent determines the skill is relevant. Keep this focused and scannable.

**Level 3** loads only when SKILL.md explicitly references it. You can bundle extensive documentation, large datasets, or complex scripts with zero context penalty until they're actually accessed.

## Structure Patterns

### Pattern 1: High-level guide with deep references

Best for skills with distinct sub-domains or extensive reference material.

```
skill-name/
├── SKILL.md              # Overview + navigation (~200 lines)
├── references/
│   ├── api-reference.md  # Detailed API docs (loaded as needed)
│   ├── examples.md       # Usage examples (loaded as needed)
│   └── troubleshooting.md
```

SKILL.md contains the core workflow and links to references:

```markdown
## Advanced Features

**API reference**: See [references/api-reference.md](references/api-reference.md)
**Examples**: See [references/examples.md](references/examples.md)
**Troubleshooting**: See [references/troubleshooting.md](references/troubleshooting.md)
```

### Pattern 2: Domain-specific organization

Best for skills covering multiple domains where only one is relevant at a time.

```
data-analysis/
├── SKILL.md
└── reference/
    ├── finance.md
    ├── sales.md
    ├── product.md
    └── marketing.md
```

When the user asks about sales metrics, only `reference/sales.md` gets loaded.

### Pattern 3: Conditional details

Best for skills where advanced features are rarely needed.

```markdown
## Creating Documents

Use the standard library for new documents.

## Editing Documents

For simple edits, modify directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For advanced XML operations**: See [OOXML.md](OOXML.md)
```

The agent reads REDLINING.md or OOXML.md only when the user's task requires those features.

## Token Budget Guidelines

| Content Type | Target Size | Rationale |
|-------------|-------------|-----------|
| **SKILL.md body** | <500 lines | Keeps Level 2 loading cost manageable |
| **Individual references** | No hard limit | Only loaded when needed, but structure with ToC |
| **Total skill directory** | No hard limit | Files not accessed consume zero tokens |

**When SKILL.md exceeds 500 lines:**
1. Identify sections that aren't needed for every task
2. Move them to separate reference files
3. Add clear links from SKILL.md

**When a reference file exceeds 100 lines:**

Include a table of contents at the top so the agent can see what's available:

```markdown
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
...
```

## Reference Depth Rules

**Keep references one level deep from SKILL.md.**

The agent may partially read files when they're referenced from other referenced files. Nested references lead to incomplete information.

```markdown
- Bad: SKILL.md → advanced.md → details.md → actual info
- Good: SKILL.md → advanced.md (contains actual info)
         SKILL.md → details.md (contains actual info)
```

All reference files should link directly from SKILL.md.

## Anti-Patterns

### Everything in SKILL.md

```markdown
- Bad: 800-line SKILL.md with all API docs inline
- Good: 200-line SKILL.md + separate api-reference.md
```

**Why it matters:** A large SKILL.md loads entirely every time the skill triggers, even if the user only needs a small part.

### Deeply nested references

```markdown
- Bad: SKILL.md → guide.md → advanced.md → the actual information
- Good: SKILL.md → guide.md (complete info for that topic)
```

**Why it matters:** The agent may use partial reads on deeply nested files, missing critical information.

### Unstructured large files

```markdown
- Bad: 600-line reference file with no headings or table of contents
- Good: Same file with ## headings and a ToC at top
```

**Why it matters:** Without structure, the agent can't efficiently navigate to the relevant section.

### Missing cross-references

```markdown
- Bad: Reference file exists but SKILL.md doesn't mention it
- Good: SKILL.md explicitly links to every reference with context on when to use it
```

**Why it matters:** The agent won't know to look for files it hasn't been told about.

## File Organization Quick Reference

| Content | Keep Inline | Separate File |
|---------|-------------|---------------|
| Core workflow (<50 lines) | Yes | No |
| Principles and concepts | Yes | No |
| Code patterns (<50 lines) | Yes | No |
| API reference (>100 lines) | No | Yes |
| Extensive examples | No | Yes |
| Reusable scripts | No | Yes (scripts/) |
| Domain-specific data | No | Yes (reference/) |
| Troubleshooting guides | No | Yes |
