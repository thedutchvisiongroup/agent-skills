# Nesting Policy

Sub-agents dispatching sub-agents (nesting, recursion). This skill's policy is deliberately strict, because nesting is where cost and error compound fastest.

## Contents

- The rule: depth ≤ 2, advisory handoffs only
- Why implementation nesting is forbidden
- The advisory handoff pattern
- What belongs in the work plan
- Harness depth limits
- When nesting is genuinely useful

## The rule: depth ≤ 2, advisory handoffs only

```
orchestrator (you)  →  sub-agent  →  specialist sub-agent
        depth 0            depth 1         depth 2 — MAXIMUM, advisory only
```

- **You, the orchestrator, dispatch ALL execution work.** Implementation and exploration are always flat — depth 1.
- **Depth 2 exists exclusively for advisory handoffs**: a reviewer encountering something outside its discipline hands it to a specialist reviewer (the canonical case: code-reviewer → security-reviewer).
- **Depth 2 requires explicit work-plan approval.** No plan approval, no nesting — the depth-1 agent reports handoff notes instead, and you dispatch the specialist yourself.
- **Leaves never nest.** A depth-2 agent never dispatches anything.

## Why implementation nesting is forbidden

- **Compounding error**: each layer summarizes the layer below; errors and omissions multiply through the chain (documented in hierarchical multi-agent research as inter-layer error propagation).
- **Compounding cost**: every nested dispatch re-pays a fresh system prompt and context prefix (+30–60% per level); wide trees multiply the bill several× over flat dispatch.
- **Lost control**: you approve one plan; nested orchestrators re-plan inside it, invisibly to you and the user.
- **Conflicting decisions**: parallel decision-makers with partial context produce valid parts that form an invalid whole. Decision authority must stay at exactly one level — yours.

If a sub-agent concludes "this needs sub-agents", the correct report is BLOCKED with that analysis. You decide.

## The advisory handoff pattern

The legitimate depth-2 flow:

1. The approved plan notes: "code review may hand off security suspicions to the security specialist".
2. The reviewer's delegation contract (see `templates/reviewer.md`) permits exactly that handoff — and nothing else.
3. The reviewer dispatches the specialist with a bounded question and the diff/report paths.
4. The specialist's verdict returns to the reviewer, who folds it into its own verdict to you.
5. You see ONE review verdict with the specialist's evidence attached.

**Fallback when nesting is unavailable or unapproved**: the reviewer lists suspicions as handoff notes (file:line, one line each, no analysis); you dispatch the specialist directly. The outcome is the same — only the routing differs. Prefer the fallback whenever in doubt.

## What belongs in the work plan

For every approved nest, the plan records:

- which depth-1 agent may hand off, to which specialist, and for what trigger
- the depth cap (2) and the leaf-may-not-nest rule
- the harness mechanism that allows it (see below) — or the explicit choice to use the fallback instead

## Harness depth limits

Harnesses gate nesting differently, and limits change between versions — verify against the live harness before planning a nest (see `references/harness-notes.md`):

- Some harnesses default to depth 1 (primary → sub-agent only) and need explicit configuration to allow depth 2; exceeding the configured depth fails the dispatch with an error.
- Some allow configurable maximums (e.g. up to 5 levels). **The harness maximum is a ceiling, not a target** — this skill's policy (2, advisory only) stays the operative limit regardless of what the harness permits.

A failed nested dispatch is not a crisis: the depth-1 agent falls back to handoff notes and you route it yourself.

## When nesting is genuinely useful

Rare, but real:

- **Reviewer → specialist handoffs** (the approved pattern above).
- **Tree-shaped read-only exploration**: a lead explorer fanning out scoped sub-explorers over independent areas (e.g. per-package in a monorepo), each leaf compressing before results roll up. Read-only means conflict-free; the tree shape means each leaf is genuinely bounded. Requires explicit plan approval like any nest.

The stop rule for any proposed nest: *if the leaf's output is under ~500 tokens, or the parent could produce it with two tool calls — don't nest.*
