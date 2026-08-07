# OpenCode Skills

Coleção pessoal de skills do OpenCode e o guia de setup do ambiente.

## Estrutura

Cada skill vive em sua própria pasta dentro de `skills/`, seguindo o formato
esperado pelo loader do OpenCode (`**/SKILL.md`):

```
opencode-skills/
├── README.md
├── OPENCODE_SETUP.md          # guia de instalação do zero do OpenCode
└── skills/
    ├── list-past-sessions/
    │   └── SKILL.md
    └── save-setup-instructions/
        └── SKILL.md
```

## Skills disponíveis

| Skill | Descrição |
| :--- | :--- |
| `list-past-sessions` | Lista sessões anteriores do OpenCode em tabela Markdown (ID, nome, datas). |
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
