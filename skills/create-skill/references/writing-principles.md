# Writing Principles for Agent Skills (Self-Contained Reference)

Distilled from Matt Pocock's `writing-for-agents` + `SKILL-MECHANICS` and validated skill packaging rules. Read this file during Step 2 and Step 3 of `create-skill`.

## 1. The Two Loads & Invocation Choice

Every skill and pointer spends one of two budgets:
- **Context load**: cost of always-loaded text on the agent's window (`description` of model-invoked skills, `AGENTS.md` lines). Paid on *every* turn whether or not the skill fires.
- **Cognitive load**: cost on the human to remember a command exists (`/skill-name`).

| Mode | Frontmatter | Context Load | When to choose |
|---|---|---|---|
| **Model-invoked** | Omit `disable-model-invocation` | Permanent (`description` always loaded) | Agent or another skill must reach it autonomously |
| **User-invoked** | `disable-model-invocation: true` (+ `policy.allow_implicit_invocation: false` in `openai.yaml`) | **Zero** | Human explicitly triggers workflow (`/retro`, `/implement-spec`) |

## 2. Context Pointers (Writing the `description`)

A skill's `description` is its top-level context pointer. Its wording decides when the agent loads the skill:
- **Single-line YAML rule**: always write `description: '...'` on a single line. Never use `>`, `|`, `>-`, or `< >` XML brackets.
- **Front-load the leading word**: start with the concrete action and domain.
- **One trigger per branch**: list genuinely distinct situations (include PT-BR and EN triggers when the user works in Portuguese). Collapse synonyms.
- **Explicit negative boundary**: end with `Do NOT use for X (use Y instead)` to prevent misfires against neighboring skills.

## 3. Information Hierarchy & Progressive Disclosure

Rank every piece of material on a three-rung ladder:
1. **In-file steps (`SKILL.md`)**: ordered actions the agent performs on *every* run (target 30–80 lines total).
2. **In-file flat reference (`SKILL.md`)**: compact one-line rules or smell baselines (`**Name**: what it is → how to fix`) consulted on every run.
3. **Disclosed reference (`references/*.md`)**: material needed only by specific branches or deep dives (>80 lines, tables, API/provider specs).

**Co-location**: keep a concept's definition, rule, and fix under one heading rather than scattered across the file.
**Branching test**: inline what *every* branch needs; push behind a pointer in `references/` what only *some* branches reach, and state the exact condition (`Read references/X.md when...`).

## 4. Steps, Completion Criteria & Sequence Splitting

Every step needs a **completion criterion** (`Done when ...`) with two properties:
- **Clarity**: binary checkable state (can the agent tell done from not-done?). Vague bounds ("understanding reached") cause **premature completion** because visible later steps pull attention forward.
- **Demand**: exhaustiveness bar that forces legwork without listing 20 sub-bullets (e.g., *"every modified file accounted for"*, *"every trace block mapped to `file:line`"*).

**When to split by sequence**: if later steps (e.g. *write a new prompt from scratch*) tempt the agent to rush earlier steps (e.g. *audit existing code for bugs*), split them into separate skills.

## 5. Leading Words, Positivity & Pruning

- **Leading words**: recruit concepts already in the model's pretraining (*seam*, *tight loop*, *smell baseline*, *frontier*, *working memory*, *context rot*). Repeat the token, never the explanation.
- **Positivity over negation**: steering by prohibition (*"Don't write verbose comments"*, *"Proibido X"*) activates the forbidden concept in attention. State the positive target (*"Write one-line comments"*).
- **Delete no-ops**: ask of every sentence: *does this change behaviour compared to the model's default?* Persona fluff (*"You are a world-class senior architect..."*) and generic pep talks (*"Be thorough and careful"*) are no-ops. Delete the entire sentence.
- **Single source of truth**: each rule lives in one place. If a check is **mechanical**, enforce it in a script (`scripts/`) or schema and delete the prose rule.
- **Environment as source of truth**: never restate in a skill what a one-command lookup in the repo (`package.json`, directory tree) already tells the agent.
