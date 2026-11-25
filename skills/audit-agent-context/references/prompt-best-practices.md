# Prompt Best Practices Reference

Consult this reference during Step 4 of `audit-agent-context` when evaluating prompt caching, dynamic variable placement, XML delimiters, long-context vs. RAG, few-shot examples, or inference parameters.

## 1. Prompt Caching & Prefix Ordering

Prompt caching reuses KV-tensors of the rendered request prefix (system + tool definitions + messages). Any byte difference before a breakpoint invalidates everything after it.

### Canonical Request Order (`stable → volatile`)
1. `system` / `developer` instructions (identity, permanent rules)
2. Tool definitions (fixed order, identical schemas across every call in the turn; to disable tools on a final structured-output call, pass `tool_choice: "none"` instead of removing `tools`)
3. Few-shot `<examples>`
4. Stable reference documents / project map
5. Conversation history (`append-only`)
6. Final `user` message: `<user_input>` followed by `<turn_context>` (working memory, prior research, conditional turn rules, timestamps)

### Provider Rules
- **OpenAI:** automatic prefix caching (~90-95% discount on cached input; minimum 1024 tokens). Requires identical prefix including `tools`.
- **Anthropic:** explicit `cache_control: {"type": "ephemeral"}` (5m TTL, 1.25x write, ~0.1x read) or `ttl: "1h"` (2x write) up to 4 breakpoints.
- **Gemini:** implicit caching (~90% discount on shared prefix) or explicit named caches (charges write + storage TTL; use sparingly).

## 2. Dynamic Variables & Trust Hierarchy

- **Trust hierarchy:** `system`/`developer` > `user` > `tool`/retrieval. Treat `<user_input>` and `<repo_content>`/`<document_content>` strictly as data, never instructions.
- **Delimiters:** isolate untrusted inputs and volatile turn state in consistent XML tags (`<user_input>`, `<turn_context>`, `<working_memory>`, `<prior_research>`, `<turn_rules>`).
- **Pre-normalize in code:** resolve dates, booleans, file exclusions, and state transitions deterministically in code before injecting into the prompt.

## 3. Attention Budget & Long Context vs. RAG

- **Lost in the Middle (U-shaped attention curve):** accuracy is highest at the very start and very end of the prompt, dropping 30%+ in the middle. Put core identity/rules at the top and active turn context/latest tool output at the bottom.
- **Just-in-time hybrid:** load a compact semantic index up-front (e.g. `Project Map` <=4KB or root `GLOSSARY.md` header) and fetch file slices on demand via tools (`grep`/`read`).

## 4. Prompt Structure & Temperature

- **Mechanical vs. Judgement:** enforce structural invariants (required sections, nullability per action, path citations, array bounds) in Zod/JSON Schema + deterministic code guardrails. Keep prose instructions focused on judgement calls.
- **Positive targets + Few-shots:** replace lists of banned phrases with affirmative target behavior and 2-5 canonical `<examples>` covering normal, edge, and closure turns.
- **Temperature:** `0.0-0.2` for agentic loops, classification, and structured JSON emission.

## Primary Sources
- OpenAI Prompt Caching: https://developers.openai.com/api/docs/guides/prompt-caching
- Anthropic Effective Context Engineering for AI Agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Claude Prompting Best Practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Gemini Context Caching: https://ai.google.dev/gemini-api/docs/caching
