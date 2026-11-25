# OpenCode Skills

Coleção pessoal de skills do OpenCode e o guia de setup do ambiente.

## Estrutura

Cada skill vive em sua própria pasta dentro de `skills/`, seguindo o formato
esperado pelo loader do OpenCode (`**/SKILL.md`):

```
opencode-skills/
├── README.md
├── OPENCODE_SETUP.md          # guia de instalação do zero do OpenCode
├── plugin/
│   └── see-image.js           # vision bridge para modelos sem visão
└── skills/
    ├── audit-agent-context/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/
    ├── create-skill/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/writing-principles.md
    ├── discovery/
    │   ├── SKILL.md
    │   └── templates.md
    ├── evolution-api/
    │   ├── SKILL.md
    │   └── references/evolution-api-reference.md
    ├── flow-mattpocock/
    │   └── SKILL.md
    ├── gsheets-edit/
    │   ├── SKILL.md
    │   ├── charts.md
    │   ├── design.md
    │   └── locale.md
    ├── list-past-sessions/
    │   ├── SKILL.md
    │   └── scripts/
    ├── recontar-historia-infantil/
    │   ├── SKILL.md
    │   └── references/regras-literatura-infantil.md
    ├── sync-provider-models/
    │   ├── SKILL.md
    │   └── scripts/
    └── save-setup-instructions/
        └── SKILL.md
```

## Skills disponíveis

| Skill | Descrição |
| :--- | :--- |
| `audit-agent-context` | Audita e diagnostica Prompt Engineering e Context Engineering de agentes de IA cruzando traces reais com o código do loop, tools, schemas e memória multi-turno. |
| `create-skill` | Cria ou refatora skills enxutas para agentes combinando os princípios de escrita e poda do Matt Pocock (`writing-for-agents`) com validação e empacotamento autônomos. |
| `discovery` | Conduz o discovery de produto e arquitetura via entrevista implacável (`grill-with-docs`), Navalha de Occam, Deep Modules (`codebase-design`) e `writing-for-agents` para gerar `README.md`, `ARQUITETURA.md` e `AGENTS.md` sincronizados. |
| `evolution-api` | Guia da Evolution API para WhatsApp — webhooks, envio de mensagens e diagnóstico (com `references/evolution-api-reference.md`). |
| `flow-mattpocock` | Conduz demandas pelo pipeline Matt Pocock (classifica, roteia, preserva gates e invariantes). |
| `gsheets-edit` | Edita Google Sheets via API `USER_ENTERED` — fórmulas, decimais com vírgula, abas, design com filtros, gráficos e estatísticas. |
| `list-past-sessions` | Lista sessões anteriores do OpenCode em tabela Markdown (ID, nome, datas) — com `scope=current`/`all`. |
| `recontar-historia-infantil` | Reconta transcrições literais de histórias inventadas por crianças em histórias infantis com começo, meio e fim, preservando a voz original. |
| `sync-provider-models` | Verifica e sincroniza modelos de providers do opencode consultando a API remota `/models` e diff contra o cache local. |
| `save-setup-instructions` | Grava novas orientações no `OPENCODE_SETUP.md`, criando-o se necessário. |

## Instalação

Copie a pasta da skill para o diretório global de skills do OpenCode:

```bash
cp -r skills/<nome-da-skill> ~/.config/opencode/skills/
```

Valide o carregamento:

```bash
opencode debug skill
```

Reinicie o OpenCode após instalar ou alterar skills.

## Adicionando uma nova skill

1. Crie a pasta `skills/<nome-da-skill>/` com nome em minúsculas e hifens
   (o loader não aceita `_`).
2. Adicione o `SKILL.md` com frontmatter contendo pelo menos `name` (igual ao
   nome da pasta) e `description` (o que faz e quando usar).
3. Atualize a tabela deste README.
4. Commit e push neste repositório.
