---
name: create-skill
description: 'Cria ou refatora skills para agentes (SKILL.md, references/, scripts/, agents/openai.yaml) combinando a disciplina enxuta do Matt Pocock (writing-for-agents) com empacotamento validado. Use when user asks to create a new skill, turn a workflow into a skill, or refactor an existing SKILL.md (PT: criar skill, transformar em skill, refatorar skill). Do NOT use for creating plugins/MCP tools or subagents (use opencode-extension).'
license: CC-BY-4.0
metadata:
  author: mcorreiam
  version: 1.0.0
---

# Create Skill

Build small, sharp, composable skills for coding agents. Self-contained (zero external skill dependencies). Every skill must pass the pruning and hierarchy rules in [references/writing-principles.md](references/writing-principles.md) before writing files to disk.

## Steps

### 1. Discovery & Split Test

If the user says "turn what we did into a skill", extract the workflow, inputs, tools, and outputs from the conversation history first; ask only what is still missing. Otherwise, run one frontier round to settle:

1. **Sequence Split test**: does the request combine two phases where the second tempts the agent to rush the first (e.g., *diagnosing* + *greenfield creation*)? If yes, split into two skills or scope to the primary phase.
2. **Invocation choice** (trading **context load** vs. **cognitive load**):
   - **Model-invoked** (default when the agent should auto-discover it): requires a sharp `description` with `[What it does] + [Use when ...] + [Do NOT use for ...]`.
   - **User-invoked** (`disable-model-invocation: true`): zero context load; only runs when the human types `/skill-name`. Use for heavy orchestrators or infrequent workflows.

**Done when** scope (single vs. split), invocation mode, and 2–3 concrete trigger phrases (EN/PT) are settled.

### 2. Plan the Information Hierarchy

Read [references/writing-principles.md](references/writing-principles.md) and map every piece of content to the three-tier ladder:

```text
<skill-name>/
├── SKILL.md                 # Target: 30–80 lines (In-file steps + flat smell/rule baseline)
├── agents/openai.yaml       # UI metadata sidecar (display_name + short_description)
├── references/              # Disclosed reference (>80 lines, tables, provider specs)
└── scripts/                 # Deterministic validation or automation (code > prose)
```

- **Mechanical vs. Judgement**: if a check is deterministic (syntax, file structure, CLI call), put it in `scripts/` or a command — never write prose rules for what code can check.
- **Branching disclosure test**: inline in `SKILL.md` only what *every* run needs; push branch-specific docs into `references/*.md` with an explicit condition stating **when** to read each file.

**Done when** the folder tree and the role of each file are decided.

### 3. Craft & Pruning Pass

Write `SKILL.md` and supporting files obeying these hard rules:

1. **Frontmatter**:
   - `name`: `kebab-case` matching the folder name (never use `claude` or `anthropic`; no `_` underscores).
   - `description`: **single inline line** (never YAML `>` or `|`, never `< >` angle brackets, under 1024 chars). Front-load the leading trigger word, list one trigger per branch (EN + PT), and end with `Do NOT use for ...`.
2. **Steps with Completion Criteria**: end every step with an explicit `Done when ...` condition that is both **clear** (binary done vs. not-done) and **high-demand** (forces thorough legwork, e.g. *"every block mapped to `file:line`"*, never *"understanding reached"*).
3. **Flat Reference as `Name: what it is → how to fix`**: group heuristics/smells into one-line co-located entries using strong **leading words**.
4. **The Pruning Pass** (mandatory before saving):
   - **Delete no-ops**: cut whole sentences the model already obeys by default (e.g. "You are a senior expert...", "Be careful and thorough").
   - **Positive over negation**: replace banned-behaviour lists ("Don't do X") with the affirmative target behaviour.
   - **Single source of truth**: never repeat the same rule in both `SKILL.md` and `references/`.
   - **No hard line-wrapping**: write prose paragraphs on single lines (no 80-col wraps). Never create a `README.md` inside the skill folder.

### 4. Validate & Deliver

Verify the checklist before finishing:

- [ ] Folder and `name` are `kebab-case` (hyphens only, no underscores)
- [ ] `description` is a single line with `[What] + [Use when (EN/PT)] + [Do NOT use for]` and no `< >`
- [ ] `SKILL.md` is compact (ideally 30–80 lines), every step has a checkable completion criterion, and every `references/` link states **when** to load it
- [ ] `agents/openai.yaml` sidecar created (`interface.display_name` and `interface.short_description`)
- [ ] Saved in `~/.config/opencode/skills/<skill-name>/` (active immediately) AND synced to `/home/marco/projects/opencode-skills/skills/<skill-name>/` with `/home/marco/projects/opencode-skills/README.md` updated (when that repo exists on disk)
