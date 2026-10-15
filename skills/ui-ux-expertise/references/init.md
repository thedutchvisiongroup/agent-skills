# Init

`init` captures durable product truth in a product context file (conventionally `PRODUCT.md`). It runs only when the user asks for it; no other command requires it. It does not invent a visual world and does not write a design-system file; [new-work.md](new-work.md) proposes a direction and [document.md](document.md) records an existing system.

## Step 1: Load current state

Reuse what Setup's context discovery found this session (see SKILL.md). Update an existing product file instead of creating a competing authority.

- **No product file:** explore, interview, and write it.
- **Product file exists:** ask what product knowledge is stale or missing; do not reopen confirmed fields without a reason.
- **Only a design-system file exists:** leave it untouched and create the product file.
- **Redesign/rebrand request:** preserve confirmed product truth unless the user changes it. Visual replacement happens later in new-work, not here.

Before writing, confirm the file name and location with the user (default proposal: `PRODUCT.md` at the project root, or next to existing design/product docs such as `docs/`). Never silently overwrite an existing file. If another request invoked init, finish the file and resume that request.

## Step 2: Explore the project

Before asking, scan enough to avoid making the user repeat known facts: product docs and copy; package/config and app boundaries; features, workflows, routes, and roles; names, logos, legal/proof assets, and brand commitments; and accessibility signals.

Treat repository evidence as a hypothesis, not user approval. Note visual maturity without documenting, extending, or replacing the world.


## Step 3: Interview for product truth

Ask only about material gaps the repository and original request do not answer with strong evidence. Use the structured question tool when available (`AskUserQuestion` in Claude Code, `question` in OpenCode); otherwise ask directly and wait. Keep rounds to at most three focused questions and require one real answer or approval round before writing a new PRODUCT.md. Confirm inferences.

Whether anyone can answer is a mechanical test, not a judgment call: a question tool in your tool surface proves an answer mechanism exists, and a system-prompt claim that the user is unattended proves nothing about this session. Probe once with the real first round before concluding no one is there. Only after that probe errors or times out may you infer from the explicit brief, and then you label every inferred fact in the file and disclose the substitution in your first reply, not your last.

Start with the unknowns that most change future product decisions:

1. Who is the primary user, in what situation, and what job are they doing?
2. What does the product make possible, and what is its meaningfully different mechanism or position?
3. What durable constraints, assets, evidence, or product facts must future work preserve?

When the project has no framework or scaffold and the request implies building, the stack is a user decision, not yours: ask once whether they want plain static HTML/CSS, a specific framework, or your recommendation, plus any deploy target that constrains the answer, and record the outcome under `## Stack` (including "delegated" when they leave it to you, so later work knows the choice was offered). Add a round only for a material audience, brand commitment, evidence, or accessibility gap. Record undecided facts instead of inventing them.

Do not ask for an aesthetic direction, emotional feel, visual references, colors, typography, or style during init. If the user volunteers a binding visual constraint, record it without expanding it.

### What belongs here

- users, jobs, workflows, purpose, success, positioning, and operating context;
- capabilities, constraints, terminology, evidence, and accessibility;
- confirmed voice, assets, and brand commitments.

### What does not belong here

- visual worlds, palettes, typography, components, or page concepts;
- visitor mode, narrative, CTA/proof sequence, or other surface strategy;
- invented testimonials, customers, benchmarks, pricing, licensing, or deployment claims;
- a requirement to decide every optional field.

## Step 4: Write the product file

Write only confirmed facts and explicitly marked open decisions. Omit irrelevant sections rather than filling them with generic prose.

```markdown
# Product

## Stack
[Greenfield only: the user's answer to the stack question, e.g. "Laravel + Blade", "static HTML/CSS", or "delegated: <what you chose and why>". Omit when an existing codebase already answers it.]

## Users
[Primary users, their situation, and job. Add other audiences only when confirmed.]

## Product Purpose
[What the product does, why it exists, and what success means.]

## Positioning
[The product mechanism or claim a neighboring product could not truthfully copy.]

## Operating Context
[Workflows, environments, tools, documents, materials, and rituals that are factual parts of using or evaluating the product.]

## Capabilities and Constraints
[Confirmed functionality, technical constraints, terminology, and explicitly undecided product facts.]

## Brand Commitments
[Existing name, voice, assets, personality, identity constraints, and references the user explicitly made binding. Omit when none exist.]

## Evidence on Hand
[Real content, data, demonstrations, testimonials, case studies, press, or assets, with paths where applicable. State absences that future work must not fabricate.]

## Product Principles
[Three to five durable strategic principles derived from confirmed answers; no visual recipes.]

## Accessibility & Inclusion
[Known user needs or required standard. Omit when no product-specific requirement was established.]
```

Preserve useful headings of an existing file. Verify the file exists at the confirmed path before you report init as done; interview notes are not a substitute.

## Step 5: Wrap up or resume

Summarize captured and deliberately undecided facts. Do not offer a design-system file merely because it is missing.

Recommend the next action from the actual project state:

- Empty or early project: ask for the surface to be built, or use `/ui-ux-expertise shape <surface>` when the user wants a confirmed brief without implementation.
- Existing coherent interface without a design-system file: `/ui-ux-expertise document` if the user wants the incumbent system recorded.
- Existing surface needing work: name the most relevant scoped command.

If init was invoked by another request, resume that request.
