---
name: audit-agent-context
description: 'Audita e diagnostica Prompt Engineering e Context Engineering de agentes de IA cruzando traces reais (Langfuse/logs) com o codigo do loop, tools, schemas e memoria multi-turno. Use when user asks to audit, analyze, or critique an agent prompt or context, debug wasted tokens/tool calls in a trace, or review prompt caching and multi-turn memory (PT: analisar/criticar prompt e contexto de agente, auditar trace). Do NOT use for creating greenfield prompts without an existing agent or trace.'
license: CC-BY-4.0
metadata:
  author: mcorreiam
  version: 1.1.0
---

# Audit Agent Context

Evidence-driven audit of an AI agent's prompt and context pipeline. Self-contained (zero external skill dependencies). Every finding must tie a **symptom observed in a real trace** to its **generator in code (`file:line`)**.

## Steps

1. **Dissect the trace**: read the captured trace (file or trace dump) and tabulate every call in the turn (`step | role/phase | chars/tokens | tool in/out | outcome`). Done when every discarded output, validation retry, unrequested payload field, and gap between user input and final response is accounted for.
2. **Trace every byte to code**: locate the files that build and run the turn (`system prompt`, `tool definitions`, `tool executors`, `output schema`, `agent loop`, `history loader`, `state persistence`). Done when every block visible in the trace is mapped to its `file:line` generator and every cross-turn state read/write (`DB`/`metadata` → next turn's `messages`) is accounted for.
3. **Classify findings against the Smell Baseline**: check the trace and pipeline against every smell below. Read [references/prompt-best-practices.md](references/prompt-best-practices.md) when evaluating provider prompt caching, variable placement, long-context vs. RAG, or prompt pruning rules; read [references/context-memory-patterns.md](references/context-memory-patterns.md) when evaluating multi-turn memory, tool-result clearing, or compaction. First classify each violation as **mechanical** or **judgement call**:
   - **Mechanical** (invalid field combinations, unfiltered dotfiles, truncated retry context, overwritten state, removed `tools` array) → fix in **deterministic code/schema**, and delete the prose rule trying to police it.
   - **Judgement call** (frontier slicing, tone, when to investigate vs. ask) → fix in the **prompt** using positive instructions, single source of truth, and 2–3 canonical `<examples>`.

### Smell Baseline (`what it is → how to fix`)

- **Domain Leak**: host/platform internal docs, infra runbooks, or other-tenant facts injected as client-project context, or mid-sentence `.slice()` truncation. → strip to a pure glossary; load client domain from the client repo.
- **Broken Cache Prefix**: volatile data (timestamps, conditional turn rules, working memory) placed before stable history, trailing `system` messages, or `tools` definitions removed on the final emit call. → order strictly `stable → volatile`, keep `tools` byte-identical with `tool_choice: "none"`, and pack volatile state into the final `user` message.
- **Shadowed User Input**: a trailing `user` or `system` guardrail message placed after the user's message, eclipsing the actual question. → merge `<user_input>` and `<turn_context>` into one final `user` message.
- **Noisy Tool Surface**: `seed`/`list`/`grep` returning dotfiles (`.opencode`, `.claude`, `.kiro`), build artifacts, or ASCII-sorted noise that hides real source code. → filter exclusions deterministically in the tool executor and sort source code first.
- **Wasted Loop Exit**: a tool-loop call returning `toolCalls: []` whose generated text is discarded before a separate structured-output call, or dual investigation mechanisms (`tool_calls` + `INVESTIGAR` action). → keep the prefix cached across both calls or unify the loop exit.
- **Unbounded Schema Variant**: nullable sub-objects (`draft`, `evidencias`) allowed on actions where they must be `null`, burning completion tokens and firing false guardrails. → reject in Zod/schema and gate SSE/API emission by action.
- **Cross-Turn Amnesia**: history loader dropping prior `draft` or `openDecisions` when the user asks for adjustments, new tool reads overwriting accumulated `priorResearch`, or `.slice(500)` cutting off the broken field during a retry. → merge research reads by SHA, surface active draft in history/working memory, and keep retry targets intact.
- **Prompt Sprawl & Negation**: mechanical rules policed in prose, rules repeated across system prompt and schema, long banned-phrase lists, contradictory rules (Map vs. `read_repo`), or zero few-shots. → move mechanical rules to code/schema, state positive targets once, resolve contradictions, and add 2–3 canonical `<examples>`.

4. **Prune the target prompt**: when rewriting the agent's prompt, delete **no-op** sentences (instructions the model already obeys by default), replace **negations** ("Proibido: ...") with positive targets, keep **one source of truth** per rule (field constraints in schema `description`, judgement rules in `<instructions>`), and anchor concepts with consistent **leading words**.
5. **Deliver the redesign and evaluation gate**: rank findings by severity (`P0/P1/P2 | Smell | file:line | trace evidence | code vs. prompt fix`), write the pruned target prompt/topology, and include a before/after verification table tied to replaying the original trace.
