# Agent Skills

Agent Skills are modular capabilities that extend an AI agent's functionality. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that the agent uses automatically when relevant.

---

## Why use Skills

Skills are reusable, filesystem-based resources that provide AI agents with domain-specific expertise: workflows, context, and best practices that transform general-purpose agents into specialists. Unlike prompts (conversation-level instructions for one-off tasks), Skills load on-demand and eliminate the need to repeatedly provide the same guidance across multiple conversations.

**Key benefits**:
- **Specialize agents**: Tailor capabilities for domain-specific tasks
- **Reduce repetition**: Create once, use automatically
- **Compose capabilities**: Combine Skills to build complex workflows

## Using Skills

Some platforms provide pre-built Agent Skills for common document tasks (PowerPoint, Excel, Word, PDF), and you can create your own custom Skills. Both work the same way. The agent automatically uses them when relevant to your request.

**Custom Skills** let you package domain expertise and organizational knowledge. Create them as directories with a `SKILL.md` file and optional supporting files.

## How Skills work

Skills leverage the agent's execution environment to provide capabilities beyond what's possible with prompts alone. The agent operates with filesystem access, allowing Skills to exist as directories containing instructions, executable code, and reference materials, organized like an onboarding guide you'd create for a new team member.

This filesystem-based architecture enables **progressive disclosure**: the agent loads information in stages as needed, rather than consuming context upfront.

### Three types of Skill content, three levels of loading

Skills can contain three types of content, each loaded at different times:

### Level 1: Metadata (always loaded)

**Content type: Instructions**. The Skill's YAML frontmatter provides discovery information:

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

The agent loads this metadata at startup and includes it in the system prompt. This lightweight approach means you can install many Skills without context penalty; the agent only knows each Skill exists and when to use it.

### Level 2: Instructions (loaded when triggered)

**Content type: Instructions**. The main body of SKILL.md contains procedural knowledge: workflows, best practices, and guidance:

````markdown
# PDF Processing

## Quick start

Use pdfplumber to extract text from PDFs:

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For advanced form filling, see [FORMS.md](FORMS.md).
````

When you request something that matches a Skill's description, the agent reads SKILL.md from the filesystem. Only then does this content enter the context window.

### Level 3: Resources and code (loaded as needed)

**Content types: Instructions, code, and resources**. Skills can bundle additional materials:

```text
pdf-skill/
├── SKILL.md (main instructions)
├── FORMS.md (form-filling guide)
├── REFERENCE.md (detailed API reference)
└── scripts/
    └── fill_form.py (utility script)
```

**Instructions**: Additional markdown files (FORMS.md, REFERENCE.md) containing specialized guidance and workflows

**Code**: Executable scripts (fill_form.py, validate.py) that the agent runs; scripts provide deterministic operations without consuming context

**Resources**: Reference materials like database schemas, API documentation, templates, or examples

The agent accesses these files only when referenced. The filesystem model means each content type has different strengths: instructions for flexible guidance, code for reliability, resources for factual lookup.

| Level | When Loaded | Token Cost | Content |
|-------|------------|------------|---------|
| **Level 1: Metadata** | Always (at startup) | ~100 tokens per Skill | `name` and `description` from YAML frontmatter |
| **Level 2: Instructions** | When Skill is triggered | Under 5k tokens | SKILL.md body with instructions and guidance |
| **Level 3+: Resources** | As needed | Effectively unlimited | Bundled files executed without loading contents into context |

Progressive disclosure ensures only relevant content occupies the context window at any given time.

### The Skills architecture

Skills run in the agent's execution environment with filesystem access and code execution capabilities. Think of it like this: Skills exist as directories on the filesystem, and the agent interacts with them like you'd navigate files on your computer.

**How the agent accesses Skill content:**

When a Skill is triggered, the agent reads SKILL.md from the filesystem, bringing its instructions into the context window. If those instructions reference other files (like FORMS.md or a database schema), the agent reads those files too. When instructions mention executable scripts, the agent runs them and receives only the output (the script code itself never enters context).

**What this architecture enables:**

**On-demand file access**: The agent reads only the files needed for each specific task. A Skill can include dozens of reference files, but if your task only needs the sales schema, the agent loads just that one file. The rest remain on the filesystem consuming zero tokens.

**Efficient script execution**: When the agent runs `validate_form.py`, the script's code never loads into the context window. Only the script's output (like "Validation passed" or specific error messages) consumes tokens. This makes scripts far more efficient than having the agent generate equivalent code on the fly.

**No practical limit on bundled content**: Because files don't consume context until accessed, Skills can include comprehensive API documentation, large datasets, extensive examples, or any reference materials you need. There's no context penalty for bundled content that isn't used.

This filesystem-based model is what makes progressive disclosure work. The agent navigates your Skill like you'd reference specific sections of an onboarding guide, accessing exactly what each task requires.

### Example: Loading a PDF processing skill

Here's how the agent loads and uses a PDF processing skill:

1. **Startup**: System prompt includes: `PDF Processing - Extract text and tables from PDF files, fill forms, merge documents`
2. **User request**: "Extract the text from this PDF and summarize it"
3. **Agent reads**: `pdf-skill/SKILL.md` → Instructions loaded into context
4. **Agent determines**: Form filling is not needed, so FORMS.md is not read
5. **Agent executes**: Uses instructions from SKILL.md to complete the task

This dynamic loading ensures only relevant skill content occupies the context window.

## Skill structure

Every Skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
[Clear, step-by-step guidance for the agent to follow]

## Examples
[Concrete examples of using this Skill]
```

**Required fields**: `name` and `description`

**Field requirements**:

`name`:
- Maximum 64 characters
- Must contain only lowercase letters, numbers, and hyphens
- Cannot contain XML tags

`description`:
- Must be non-empty
- Maximum 1024 characters
- Cannot contain XML tags

The `description` should include both what the Skill does and when the agent should use it. For complete authoring guidance, see the [best practices guide](./anthropic-best-practices.md).

## Security considerations

We strongly recommend using Skills only from trusted sources: those you created yourself or obtained from reputable providers. Skills provide the agent with new capabilities through instructions and code, and while this makes them powerful, it also means a malicious Skill can direct the agent to invoke tools or execute code in ways that don't match the Skill's stated purpose.

> **Warning:** If you must use a Skill from an untrusted or unknown source, exercise extreme caution and thoroughly audit it before use. Depending on what access the agent has when executing the Skill, malicious Skills could lead to data exfiltration, unauthorized system access, or other security risks.

**Key security considerations**:
- **Audit thoroughly**: Review all files bundled in the Skill: SKILL.md, scripts, images, and other resources. Look for unusual patterns like unexpected network calls, file access patterns, or operations that don't match the Skill's stated purpose
- **External sources are risky**: Skills that fetch data from external URLs pose particular risk, as fetched content may contain malicious instructions. Even trustworthy Skills can be compromised if their external dependencies change over time
- **Tool misuse**: Malicious Skills can invoke tools (file operations, bash commands, code execution) in harmful ways
- **Data exposure**: Skills with access to sensitive data could be designed to leak information to external systems
- **Treat like installing software**: Only use Skills from trusted sources. Be especially careful when integrating Skills into production systems with access to sensitive data or critical operations