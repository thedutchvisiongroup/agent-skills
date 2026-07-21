# LLM / GenAI Security

Read this during Phase 4, class 11 — whenever the codebase integrates LLMs or GenAI (chat features, agents, RAG, embeddings, model APIs). Anchored to the OWASP Top 10 for LLM Applications 2025 (LLM01–LLM10). Many LLM risks are runtime behaviors; this reference focuses on what is CODE-DETECTABLE. Anything not verifiable statically goes to "Could NOT verify" — say so explicitly.

## Contents

- What It Is
- Prompt Injection Surface (LLM01)
- Sensitive Information Disclosure (LLM02) & System Prompt Leakage (LLM07)
- Improper Output Handling (LLM05)
- Excessive Agency (LLM06)
- Vector and Embedding Weaknesses (LLM08)
- Supply Chain (LLM03) & Unbounded Consumption (LLM10)
- Data/Model Poisoning & Misinformation (LLM04/LLM09)
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

LLM-integrated code adds a new interpreter: the model. Untrusted data that steers the model is "injection"; model output that flows into your sinks is a new untrusted SOURCE. **The core review rule: treat model output as untrusted input everywhere downstream.**

## Prompt Injection Surface (LLM01)

Detection patterns:

1. **User input concatenated into prompts** — request data interpolated directly into system/user prompt strings. This is the SHAPE of prompt injection; the guard question is what the model can DO with a hijacked instruction (see agency below).
2. **Indirect injection paths** — third-party content (web pages, emails, documents, code, tickets) fetched and placed into prompts where the model also has tools. Trace: external content source → prompt assembly → tool-enabled model.
3. **No separation of instruction and data** — untrusted content not delimited/isolated (no clear demarcation, no "treat as data" handling, instructions mixed into the same field as user content).
4. **Jailbreak-fragile design** — security enforced BY the system prompt ("never reveal X") rather than by code controls. Prompt-based restrictions are not a control; note missing code-level enforcement.

Grade severity by consequence: a hijackable chatbot with no tools is lower severity than one that can send emails, run queries, or execute code.

## Sensitive Information Disclosure (LLM02) & System Prompt Leakage (LLM07)

1. **Secrets in prompts** — API keys, connection strings, credentials interpolated into prompts/context (the model can be coaxed to repeat them). Cross-reference secrets reference.
2. **PII/sensitive data in context** — full user records, other users' data, or internal docs placed into prompts beyond need (data minimization applies to prompts too).
3. **System prompts containing sensitive internals** — credentials, internal URLs, business logic worth protecting; assume prompts leak (they do).
4. **Model/provider keys hardcoded** — LLM API keys in source/config (high-frequency real-world finding; check env-var names, client initializations).
5. **Conversation data retention** — prompts/responses with PII logged or sent to providers without a visible basis (privacy reference).

## Improper Output Handling (LLM05)

**Treat every model output as an untrusted SOURCE and trace it to sinks** — this is the classic injection discipline applied downstream:

1. Model output → **HTML/DOM** (XSS via markdown/rendering of model text)
2. Model output → **SQL/shell/commands** (generated queries/commands executed; natural-language-to-SQL without constrained schemas/parameterization)
3. Model output → **code execution** (generated code eval'd/run; generated templates rendered)
4. Model output → **file paths/URLs** (writes, fetches, redirects — path traversal/SSRF via model)
5. Model output → **other users** (unreviewed autonomous publishing, emails, messages)

Each is reported under BOTH LLM05 and the underlying class (XSS/injection/etc.) — map both.

## Excessive Agency (LLM06)

When the model has tools/function-calling:

1. **High-impact tools without human confirmation** — send/delete/pay/execute/provision functions callable autonomously. Check for a human-in-the-loop gate on irreversible/high-impact actions.
2. **Over-broad tool permissions** — tools with wider scope than needed (DB access beyond read-only, broad filesystem/shell access, wildcard API permissions).
3. **Unconstrained tool parameters** — model-controlled arguments reaching sinks without validation (a `run_sql(query)` tool is a critical sink).
4. **Autonomous loops** — agent loops without iteration limits, cost caps, or kill-switches.
5. **Missing allow-lists** — the model able to invoke arbitrary functions rather than a vetted set.

## Vector and Embedding Weaknesses (LLM08)

1. **RAG retrieval across trust boundaries** — a user's query retrieving OTHER users'/tenants' documents (missing metadata/tenant filters in vector queries).
2. **Poisonable ingestion** — untrusted content embedded into the knowledge base without provenance/validation (indirect prompt injection via retrieval).
3. **Embedding inversion/sensitive embeddings** — embeddings of sensitive data exposed via similarity queries or logged.
4. **Access control on the vector store** — the vector DB treated as internal-safe while reachable by less-trusted services.

## Supply Chain (LLM03) & Unbounded Consumption (LLM10)

1. **Model/artifact provenance** — models/weights/adapters/datasets pulled from public hubs without verification (hashes, signatures, trusted sources); fine-tune artifacts unreviewed.
2. **Plugin/tool ecosystem trust** — third-party tools/plugins granted model access without review.
3. **Cost/DoS controls** — no request quotas, token limits, or spend caps around model calls (user-triggerable expensive calls; "denial of wallet"); missing timeouts on provider calls.
4. **Caching/retry storms** — retries without backoff on provider errors.

## Data/Model Poisoning (LLM04) & Misinformation (LLM09)

Mostly not code-detectable. What IS reviewable:

- Training/fine-tuning pipelines ingesting unvalidated external data (note it).
- **Unverified model output presented as fact** — no disclaimers/verification on high-stakes outputs (medical, legal, financial); note as observation.
- Grounding/citation absence where accuracy matters.

Anything deeper (weights, training data integrity) → "Could NOT verify" from static review.

## False-Positive Guidance

Do NOT report when:

- The model has NO tools and output is verifiably encoded before rendering (severity drops sharply — don't inflate a prompt-echo into Critical).
- Tool use is allow-listed AND high-impact actions require verified human confirmation in code.
- Context assembly demonstrably minimizes data (only required fields) and contains no secrets.
- Rate limits/quotas around model calls are visible in code/config.

## Mandatory Online Research Triggers

- The LLM SDK/provider's features for the detected version (tool-calling semantics, data retention defaults, streaming behaviors) — this ecosystem moves fast; ALWAYS research (protocol triggers #1/#2).
- Known advisories for model/embedding/framework packages (they're dependencies too — Phase 2 lookup applies).
- Current prompt-injection/output-handling guidance (OWASP GenAI project) — verify mitigations claimed in code comments.

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| User/external content into prompt with tools | CWE-74/1427 | LLM01:2025 Prompt Injection |
| Secrets/PII in prompts; prompt leakage | CWE-200/798/359 | LLM02:2025 / LLM07:2025 |
| Model output to XSS/SQL/cmd/path sinks | CWE-79/89/78/22 | LLM05:2025 Improper Output Handling |
| High-impact tools without confirmation; broad permissions | CWE-862/250/732 | LLM06:2025 Excessive Agency |
| Cross-tenant retrieval; poisonable ingestion | CWE-639/284 | LLM08:2025 Vector and Embedding Weaknesses |
| Unverified models/plugins | CWE-494/1357 | LLM03:2025 Supply Chain |
| No quotas/timeouts on model calls | CWE-770 | LLM10:2025 Unbounded Consumption |
| Unvalidated training ingestion | CWE-20 | LLM04:2025 / LLM09:2025 (mostly "Could NOT verify") |
