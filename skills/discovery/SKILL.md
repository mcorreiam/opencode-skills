---
name: discovery
description: 'Product and architecture discovery via relentless grilling, Occam''s Razor, and Deep Modules to produce README.md, ARQUITETURA.md, and AGENTS.md. Use when starting a new project, reshaping product scope and architecture, or running discovery before specs and code (PT: Use para conduzir discovery de produto e arquitetura gerando README.md, ARQUITETURA.md e AGENTS.md).'
license: CC-BY-4.0
metadata:
  author: mcorreiam
  version: 1.0.0
---

# Discovery — Produto, Arquitetura (Occam + Deep Modules) e AGENTS.md

Conduza o discovery completo de um projeto até cristalizar três artefatos sincronizados na raiz do repositório:
1. **`README.md`** — Pedido de Produto, Pilares/Telas e UX (orientados a uma única pergunta-guia).
2. **`ARQUITETURA.md`** — Arquitetura em Alto Nível aplicando **Navalha de Occam** e **Deep Modules** (`codebase-design`), com mapa de fontes, Planos B (fallbacks) e portas prontas de entrega.
3. **`AGENTS.md`** — Guia operacional para agentes escrito com as alavancas de `writing-for-agents` (*context pointers*, *progressive disclosure*, *leading words*, invariantes de domínio e *completion criteria*).

Quando precisar da estrutura detalhada e seção por seção de cada um dos 3 arquivos, leia [`templates.md`](templates.md).

## Princípios Inegociáveis

- **Navalha de Occam (Produto e Arquitetura):** Entre duas formas de resolver o problema, escolha a que exige menos peças móveis, menos processos, menos fontes externas e menos trabalho no cliente. Corte qualquer dado, tela ou scraping que não ajude diretamente na decisão central do usuário.
- **Deep Modules (`codebase-design`):** Poucos módulos profundos (**Interface** minúscula + **Implementação** pesada escondida). Crie **Seams & Adapters** apenas onde houver variação externa real, mantendo o **Plano B (fallback)** dentro do próprio **Adapter**. Garanta **Locality** (*Single Source of Truth*: cada cálculo ou regra tem um único módulo dono).
- **Entrevista Implacável (`grill-with-docs`):** Descubra fatos no ambiente por conta própria; entreviste o usuário em rodadas sobre a **frontier** da árvore de decisões, sempre com recomendação opinativa (`➡️`) aplicando a Navalha de Occam, e capture termos e invariantes de domínio à medida que cristalizam.
- **Escrita para Agentes (`writing-for-agents`):** Proteja o *context load* no `AGENTS.md`. Use *context pointers* com *trigger branches* claros, empurre referência longa para `README.md` e `ARQUITETURA.md`, elimine *no-ops* e escreva regras na forma positiva e determinística.

## Steps

### 1. Reconhecimento do Ambiente e Referências

Antes de fazer perguntas ao usuário, explore o diretório atual e quaisquer projetos de referência ou homologação mencionados. Levante fatos que o código ou ambiente já respondem: APIs usadas, schemas, fórmulas validadas e armadilhas conhecidas.

Done when: fatos existentes no filesystem ou repositório de referência foram levantados sem perguntar ao usuário o que você mesmo podia inspecionar.

### 2. Grilling por Rodadas (Design Tree + Navalha de Occam)

Mapeie as decisões em uma **design tree** e conduza a entrevista em **rounds** cobrindo toda a **frontier** atual (questões cujos pré-requisitos já estão decididos). Formate cada questão da rodada assim:

```markdown
❓ **Q1** - **<título curto da decisão>**: <contexto direto + opções claras>

➡️ **Recomendação (Navalha de Occam):** <sua escolha recomendada cortando complexidade acidental e por quê>
```

Ao longo das rodadas, feche obrigatoriamente estas 5 dimensões:
1. **Pergunta-Guia Única e Pilares do Produto:** Qual é a única pergunta do usuário final que o produto responde? Quais são os pilares/telas essenciais e o que deve ser cortado por ser gordura?
2. **Fontes de Dados e Planos B (Fallbacks):** De onde vem cada dado essencial e qual é o cálculo interno ou fotografia de contingência se a fonte externa atrasar, zerar ou cair?
3. **Módulos Profundos (Deep Modules):** Quais são os módulos internos (tipicamente 3 a 4), qual é a responsabilidade única (*Single Source of Truth*) de cada um e qual a ordem de dependência entre eles?
4. **Portas de Entrega para o Cliente:** Quais são os pacotes prontos de leitura que o sistema serve para que o cliente/celular apenas exiba dados mastigados?
5. **Invariantes de Domínio (Gotchas Críticos):** Quais são as regras de negócio inegociáveis, janelas temporais exatas e armadilhas de dados externos que nunca podem ser violadas?

Done when: a frontier da design tree está vazia e o usuário confirmou o entendimento compartilhado das 5 dimensões.

### 3. Redigir `README.md` (Pedido de Produto)

Siga a estrutura de [`templates.md#1-readmemd`](templates.md) para criar ou atualizar o `README.md`.
- Destaque o **Objetivo Único** e a **Pergunta-Guia** logo na abertura.
- Descreva cada Pilar/Tela apenas com informações acionáveis que respondem à pergunta-guia.
- Use métricas e indicadores objetivos (ex.: frequência real, selo único de status) em vez de conceitos subjetivos.

Done when: `README.md` está salvo na raiz, cada bloco responde à pergunta-guia e aponta para `ARQUITETURA.md`.

### 4. Redigir `ARQUITETURA.md` (Navalha de Occam + Deep Modules)

Siga a estrutura de [`templates.md#2-arquiteturamd`](templates.md) para criar ou atualizar o `ARQUITETURA.md` em linguagem clara e de alto nível (sem código bruto):
- Explique a filosofia (**Navalha de Occam** + **Módulos Profundos** com diagrama ASCII da caixa-preta).
- Inclua o **Diagrama Geral em Mermaid** ligando Fontes Externas $\rightarrow$ Módulos Internos + Banco Único $\rightarrow$ Vitrine de Entrega (Portas Prontas) $\rightarrow$ Telas do Cliente.
- Monte a tabela **Mapa das Fontes e Planos B** (`O que precisamos saber | De onde vem o dado | Qual é o Plano B`).
- Detalhe cada **Módulo Profundo** deixando explícito quem é o dono único (*Single Source of Truth*) de cada cálculo e onde ocorrem snapshots/freezes imutáveis.
- Desenhe o diagrama das **Portas de Entrega** mapeadas 1:1 com as telas do `README.md`.

Done when: `ARQUITETURA.md` está salvo na raiz, todas as fontes têm Plano B determinístico e cada módulo tem responsabilidade única sem sobreposição.

### 5. Redigir `AGENTS.md` (Guia Operacional para Agentes)

Siga a estrutura de [`templates.md#3-agentsmd`](templates.md) aplicando `writing-for-agents`:
- **Context Pointers** no topo com *trigger branches* concisos para `README.md`, `ARQUITETURA.md` e referências externas.
- **Propósito** em 1 parágrafo denso ancorando as *leading words* do domínio.
- **Princípios de Design** (`codebase-design` + Navalha de Occam: Deep Modules, Seams & Adapters reais, Locality & Leverage, injeção explícita e retorno puro).
- **Invariantes de Domínio (Gotchas Críticos)** co-localizados com limiares exatos.
- **Critérios de Conclusão (Completion Criteria)** verificáveis (testes verdes na Seam sem rede externa, zero segredos no código, documentação sincronizada).

Done when: `AGENTS.md` está salvo na raiz, enxuto, sem duplicar tabelas longas dos outros documentos e sem instruções *no-op*.

### 6. Auditoria Cruzada (`README.md` × `ARQUITETURA.md` × `AGENTS.md`)

Faça um batimento linha a linha entre os 3 arquivos (se estiver em ambiente multi-pane como Herdr ou com sub-agentes disponíveis, você pode pedir revisão cruzada sob as lentes de *Produto/UX* e *Arquitetura/Dados*):

1. **Simetria Pilares $\leftrightarrow$ Portas:** Todo item prometido nas telas do `README.md` possui um módulo produtor e uma Porta de Entrega correspondente no `ARQUITETURA.md`?
2. **Corte de Fios Soltos (Occam):** Existe alguma fonte ou metadado citado num diagrama que não tem pipeline/Plano B ou não ajuda na decisão do usuário? Se sim, corte dos dois.
3. **Unicidade de Regras e Limiares:** As janelas temporais, fórmulas e regras dos invariantes são idênticas em `README.md`, `ARQUITETURA.md` e `AGENTS.md` (sem números órfãos)?
4. **Single Source of Truth e Imutabilidade:** Está claro qual módulo calcula cada indicador e como os snapshots evitam perda/sobrescrita de dados históricos?

Apresente a tabela de cruzamento ao usuário e aplique os ajustes finais nos 3 arquivos.

Done when: os 3 documentos (`README.md`, `ARQUITETURA.md` e `AGENTS.md`) estão 100% sincronizados, sem itens órfãos, sem gordura e aprovados pelo usuário.
