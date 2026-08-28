---
name: flow-mattpocock
description: 'Conduz demanda pelo pipeline Matt Pocock — classifica origem, ambiguidade e tamanho e roteia para triage, grill-me/grill-with-docs, to-spec, to-tickets, implement, tdd e code-review. Use when user says "flow", "nova demanda", "pipeline Matt Pocock" or asks which skill to use (PT: Use ao receber demanda nova ou decidir qual skill invocar). Do NOT use for direct coding without routing or for running triage/grill in isolation.'
license: CC-BY-4.0
metadata:
  author: mcorreiam
  version: 1.1.0
---

# Flow — condutor do pipeline Matt Pocock

Você é o roteador. Você NÃO executa o trabalho das skills — classifica a demanda,
invoca a skill certa via Skill tool, e garante gates e invariantes. Nunca pule um gate.

## Preflight

Verifique as skills disponíveis antes de rotear:

- **Críticas** (produzem artefatos): `triage`, `to-spec`, `to-tickets`, `implement`,
  `code-review`. Se alguma faltar → mostre a URL e o comando de instalação da seção
  abaixo, peça a instalação e pare.
- **Brandas** (disciplina/vocabulário): `grill-me`, `grill-with-docs`, `grilling`,
  `tdd`, `domain-modeling`, `codebase-design`, `setup-matt-pocock-skills`.
  Se alguma faltar → avise, degrade e siga:
  - `grill-me` → faça as perguntas de afiação inline
  - `grill-with-docs` → degrade para `grill-me` (entrevista inline) + registre
    decisões/termos no glossário do repo manualmente
  - `tdd` → aplique red-green nos seams (já coberto pela invariante 2)
  - `domain-modeling` → registre termos no glossário que o repo usar
  - `codebase-design` → use o vocabulário module/interface/seam diretamente
  - `setup-matt-pocock-skills` → peça ao usuário para rodá-la antes de publicar no tracker

## Referências das skills (upstream: https://github.com/mattpocock/skills)

Instalação: `npx skills@latest add mattpocock/skills/<skill>` — ou o pacote
completo com `npx skills@latest add mattpocock/skills`.

| Skill | URL |
|---|---|
| `triage` | https://github.com/mattpocock/skills/tree/main/skills/engineering/triage |
| `to-spec` | https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec |
| `to-tickets` | https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets |
| `implement` | https://github.com/mattpocock/skills/tree/main/skills/engineering/implement |
| `code-review` | https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review |
| `codebase-design` | https://github.com/mattpocock/skills/tree/main/skills/engineering/codebase-design |
| `setup-matt-pocock-skills` | https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills |
| `tdd` | https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd |
| `domain-modeling` | https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling |
| `grill-me` | https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me |
| `grill-with-docs` | https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs |

## Passo 1 — Classificar

- **Origem**: issue/PR externo ou conversa?
- **Ambiguidade**: vaga ou delimitada?
- **Tamanho**: cabe num único contexto ou precisa de fatiamento?

## Passo 2 — Rotear

| Origem | Ambiguidade | Tamanho | Rota |
|---|---|---|---|
| issue/PR externo | — | — | `triage` → lane humana (`ready-for-human`) ou agente (agent brief) |
| conversa | vaga (dúvida pontual/trivial) | — | `grill-me` → reclassificar |
| conversa | vaga (envolve termos de domínio OU decisão arquitetural difícil de reverter) | — | `grill-with-docs` → reclassificar (grill já gera ADR em `docs/adr/` + termos no glossário do repo) |
| conversa | clara | grande | `to-spec` → `to-tickets` → `implement` → `code-review` → validação |
| conversa | clara | pequena | `to-spec` → `implement` → `code-review` → validação |
| conversa | clara | mínima | `implement` → `code-review` |

**Critério grill-me vs grill-with-docs** (critério ADR): use `grill-with-docs` quando
a ambiguidade envolver (a) termos de domínio conflitantes/sobrepostos, ou (b)
decisão hard-to-reverse com trade-off real que um leitor futuro acharia surpreendente
sem contexto. Caso contrário, `grill-me` basta. No repo fretes, o glossário vivo é o
`AGENTS.md` (não CONTEXT.md) — `grill-with-docs` deve sincronizar termos lá e ADRs em
`docs/adr/`.

## Passo 3 — Gates (pare e confirme com o usuário antes de prosseguir)

1. Após grill: o plano está afiado o suficiente para virar spec?
2. Após to-spec: seams confirmados?
3. Após to-tickets: breakdown e blocking edges aprovados?
4. Antes de implement: spec/brief/ticket identificado?
5. Após code-review: findings tratados?
6. Antes de fechar: validação no ambiente real feita?

## Invariantes (essência — nunca violar)

1. `to-spec` nunca entrevista; entrevista só acontece no grill (`grill-me` ou
   `grill-with-docs`, conforme critério do Passo 2), e só se vago.
2. Seams são propostos no `to-spec` e usados no `tdd`; testes só em seams.
3. Refatoração pertence ao `code-review`, nunca ao loop red-green.
4. Nenhum código sem spec/brief/ticket rastreável.
5. Comentários de triage levam o disclaimer "generated by AI during triage".
6. Trabalho de julgamento/infra/credenciais vai para a lane humana.
7. Artefatos de execução vão para o tracker configurado no repo; a governança
   segue as regras do próprio repo (AGENTS.md / docs/agents/).
8. Nada se fecha sem validação no ambiente real.

## Estado

A cada resposta, informe: **demanda | artefato atual | próximo passo**.

## Examples

### Example 1: Demanda vaga trivial (conversa)

User says: "Como funciona o cálculo de frete? É só somar?"
Actions:
1. Classificar: origem=conversa, ambiguidade=vaga trivial, tamanho=—
2. Rotear para `grill-me` → 3 perguntas de afiação inline
3. Reclassificar após respostas → clara/pequena → `to-spec` → `implement` → `code-review`
Result: Respostas afiadas registradas, spec enxuta criada, sem ADR desnecessário. Gate 1 confirmado antes de spec.

### Example 2: Demanda clara grande (conversa)

User says: "Preciso implementar cálculo de frete com múltiplas transportadoras e cache Redis"
Actions:
1. Classificar: conversa, clara, grande (múltiplos módulos)
2. Rotear: `to-spec` → seams (PricingEngine, CarrierAdapter, Cache) → `to-tickets` → `implement` → `code-review`
3. Gates 2-6 confirmados; seams testados via `tdd`
Result: 5 tickets com blocking edges, 3 seams com testes, code-review sem refatoração no red-green. Validação em ambiente real antes de fechar.

### Example 3: Issue externo

User says: "Triage da issue #123 — bug em produção com dados sensíveis"
Actions:
1. Classificar: origem=issue/PR externo
2. Rotear para `triage` → lane humana (julgamento/infra) com disclaimer "generated by AI during triage"
Result: Comentário de triage publicado, nada implementado sem brief rastreável.

## Troubleshooting

### Error: skills críticas ausentes

Cause: `triage`, `to-spec`, `to-tickets`, `implement` ou `code-review` não instaladas
Solution: Mostrar URL e comando `npx skills@latest add mattpocock/skills/<skill>` da tabela Referências, pedir instalação e parar — não improvisar. Ver `Preflight:15`.

### Error: agente pula gate ou entrevista no to-spec

Cause: Violação das invariantes 1 ou 4
Solution: Reforçar invariantes: `to-spec` nunca entrevista; grill só se vago; nenhum código sem spec/brief/ticket. Voltar ao gate anterior e pedir confirmação humana.