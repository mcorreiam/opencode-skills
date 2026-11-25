# Context & Memory Patterns Reference

Consult this reference during Step 4 of `audit-agent-context` when evaluating multi-turn memory, working memory persistence, tool-result pruning, or conversation compaction.

## 1. The 6 Memory Types in Agent Loops

| Memory Type | What it holds | Where it lives | Common Failure Mode (Smell) |
|---|---|---|---|
| **Short-term window** | Last N turns verbatim | `messages` array | Dropping structured `metadata` (drafts/decisions) when building `messages` from DB |
| **Working memory** | Active task state, open decisions, current draft | `<working_memory>` in last turn / `Conversation.metadata` | **Cross-Turn Amnesia**: agent cannot see its own previous proposal when user asks for edits |
| **Tool-result cache** | Verified file reads / API responses | In-turn `tool` messages + cross-turn `<prior_research>` | Overwriting prior turns' reads instead of merging by repo SHA; or replaying raw `list`/`grep` noise |
| **Episodic** | What happened per turn | Langfuse traces + DB turn metadata | No token/call/retry telemetry per turn to trigger pruning |
| **Semantic** | Domain glossary + repo architecture | `GLOSSARY.md` + `Project Map` (`<=4KB`) | **Domain Leak**: injecting host platform docs into client tenant conversations |
| **Procedural** | How the agent operates | `system` prompt + tool schemas + `<examples>` | **Prompt Sprawl**: repeating rules 5x instead of 1 rule + 2-3 few-shots |

## 2. Compression Cascade (Order of Application)

Apply context reduction from cheapest/lossless to most expensive:

1. **Deterministic Input Filtering (Pre-LLM):** exclude `.git`, `node_modules`, build dirs, agent dirs (`.opencode`, `.claude`, `.kiro`, `.playwright-mcp`, `.specs`), and secrets inside the tool executor before returning results.
2. **Tool-Result Clearing (`clear_tool_uses`):** when tool outputs dominate context (>80%), replace old raw `list`/`grep` outputs with compact placeholders while keeping the last 3-6 `read` snippets or offloading >20k token outputs to disk refs.
3. **Sliding Window + Working Memory:** keep last N messages verbatim plus a structured `<working_memory>` block carrying active `openDecisions`, latest `draft`, and merged `priorResearch` (capped at e.g. 8 snippets x 600 chars, keyed by repo SHA).
4. **Compaction / Hierarchical Summary:** trigger at 75-85% of context budget (never at 100%). Preserve session intent, architectural decisions, entity IDs, open constraints, and next steps; discard redundant failed tool attempts.

## 3. Multi-Turn Invariants

- **Append-only history:** never mutate mid-history messages (invalidates KV-cache). Inject summaries as a new boundary or append `<turn_context>` to the final `user` message.
- **Retry visibility:** when a schema or guardrail validation fails mid-turn, ensure the assistant's prior JSON slice in the retry prompt is large enough (e.g. `<=4000` chars) to include the exact field (`promptTecnico`, `perguntas`) the validator rejected.
- **Multi-tenant isolation:** scope all semantic maps (`repoMap`) and research caches (`priorResearch`) by `projectId` and `repoSha`.

## Primary Sources
- Anthropic Context Engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic Memory & Context Engineering Cookbooks: https://platform.claude.com/cookbook/tool-use-memory-cookbook · https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools
- LangChain Context Management for DeepAgents: https://www.langchain.com/blog/context-management-for-deepagents
