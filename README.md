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
    ├── evolution-api/
    │   └── SKILL.md
    ├── flow-mattpocock/
    │   └── SKILL.md
    ├── list-past-sessions/
    │   └── SKILL.md
    └── save-setup-instructions/
        └── SKILL.md
```

## Skills disponíveis

| Skill | Descrição |
| :--- | :--- |
| `evolution-api` | Guia da Evolution API para WhatsApp — webhooks, envio de mensagens e diagnóstico (com `references/evolution-api-reference.md`). |
| `flow-mattpocock` | Conduz demandas pelo pipeline Matt Pocock (classifica, roteia, preserva gates e invariantes). |
| `list-past-sessions` | Lista sessões anteriores do OpenCode em tabela Markdown (ID, nome, datas) — com `scope=current`/`all`. |
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
