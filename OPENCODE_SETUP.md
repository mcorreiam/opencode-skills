# Setup do OpenCode

Voce e o agente responsavel por configurar uma instalacao nova do OpenCode
neste ambiente. Execute cada secao na ordem, validando o resultado antes de
passar para a proxima. Se um item ja estiver instalado ou configurado, pule-o
informando que ja existia. Nunca encerre com passos pendentes sem avisar.

## 0. Pre-requisitos

Algumas etapas dependem de Node.js e git. Verifique:

```bash
git --version
node --version
npm --version
```

Se Node.js ou npm nao existirem, instale via nvm antes de prosseguir:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
source ~/.bashrc
nvm install --lts
```

## 1. Clipboard no terminal

Instale o `xclip` e o `wl-clipboard` para habilitar copy/paste no TUI do
OpenCode. O `wl-clipboard` e necessario em sessoes Wayland (GNOME, KDE):

```bash
sudo apt install xclip wl-clipboard
```

Sem eles, o TUI nao consegue copiar nem colar texto, e plugins que leem a
area de transferencia (como o `see-image`) tambem falham.

## 2. Context7 para documentacao atualizada

Configure o Context7 globalmente como servidor MCP do OpenCode. Edite
`~/.config/opencode/opencode.jsonc` (crie o arquivo se nao existir) e garanta
o bloco abaixo, preservando campos existentes:

```jsonc
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```

Valide a conexao com:

```bash
opencode mcp list
```

O resultado esperado e `context7 connected`. Uma API key gratuita e opcional,
mas recomendada para limites de uso maiores.

## 3. Skill para listar sessoes anteriores

Baixe e instale a skill a partir do repositorio publico:

```bash
git clone --depth 1 https://github.com/mcorreiam/opencode-skills.git /tmp/opencode-skills
mkdir -p ~/.config/opencode/skills
cp -r /tmp/opencode-skills/skills/list-past-sessions ~/.config/opencode/skills/
rm -rf /tmp/opencode-skills
```

O nome registrado e `list-past-sessions` (o OpenCode aceita apenas nomes em
minusculas separados por hifens). Confirme o carregamento:

```bash
opencode debug skill
```

O resultado deve conter `list-past-sessions`.

## 4. Playwright

Instale o Playwright globalmente e baixe os navegadores:

```bash
npm install -g playwright
npx playwright install
```

Instale tambem as dependencias do sistema. Como o Node.js e instalado via nvm,
o `sudo` precisa receber o caminho do Node explicitamente (resolva o caminho
dinamicamente, sem fixar versao):

```bash
NODE_BIN_DIR="$(dirname "$(which node)")"
sudo env PATH="$NODE_BIN_DIR:$PATH" "$NODE_BIN_DIR/npx" playwright install-deps
```

## 5. Skill tlc-spec-driven (Spec-Driven Development)

Instale a skill globalmente a partir do repositorio oficial:

```bash
git clone --depth 1 https://github.com/tech-leads-club/agent-skills.git /tmp/agent-skills
mkdir -p ~/.config/opencode/skills
cp -r "/tmp/agent-skills/packages/skills-catalog/skills/(development)/tlc-spec-driven" \
  ~/.config/opencode/skills/tlc-spec-driven
rm -rf /tmp/agent-skills
```

Confirme a instalacao:

```bash
opencode debug skill
```

O resultado deve conter `tlc-spec-driven`. Valide os scripts validadores
(dependem de `python3`):

```bash
for f in ~/.config/opencode/skills/tlc-spec-driven/scripts/*.py; do python3 "$f" --help; done
```

## 6. Plugin see-image (vision bridge para modelos sem visao)

Modelos de textoonly (como GLM-5.2) nao conseguem ler imagens coladas no
chat. Este plugin registra uma ferramenta `see_image` que intercepta o erro
"this model does not support image input", envia a imagem para um modelo com
visao nativa (qwen3.6-flash) e devolve a descricao como texto.

Crie o diretorio de plugins e instale as dependencias:

```bash
mkdir -p ~/.config/opencode/plugin
cd ~/.config/opencode
npm init -y
npm install zod
```

Garanta que o `package.json` tenha `"type": "module"` (plugins usam sintaxe
ESM). Copie o plugin a partir do repositorio:

```bash
git clone --depth 1 https://github.com/mcorreiam/opencode-skills.git /tmp/opencode-skills
cp /tmp/opencode-skills/plugin/see-image.js ~/.config/opencode/plugin/
rm -rf /tmp/opencode-skills
```

Adicione o plugin ao `~/.config/opencode/opencode.jsonc`, preservando campos
existentes:

```jsonc
{
  "plugin": [
    "./plugin/see-image.js"
  ]
}
```

O plugin usa estas variaveis de ambiente (opcional, com defaults):

```bash
export SEE_IMAGE_PROVIDER="alibaba-token-plan"
export SEE_IMAGE_MODEL="qwen3.6-flash"
export SEE_IMAGE_TIMEOUT="30000"
```

Valide o carregamento apos reiniciar o OpenCode. O modelo deve chamar
`see_image` automaticamente quando colar uma imagem e receber o erro
"this model does not support image input".

## 7. Skill save-setup-instructions (gravar setup)

Instale a skill que grava orientacoes de setup neste proprio arquivo:

```bash
git clone --depth 1 https://github.com/mcorreiam/opencode-skills.git /tmp/opencode-skills
mkdir -p ~/.config/opencode/skills
cp -r /tmp/opencode-skills/skills/save-setup-instructions ~/.config/opencode/skills/
rm -rf /tmp/opencode-skills
```

Confirme o carregamento:

```bash
opencode debug skill
```

O resultado deve conter `save-setup-instructions`.

## 8. Skill evolution-api (WhatsApp Evolution API)

Guia da Evolution API para webhooks, envio de mensagens e diagnostico. Inclui referencia detalhada em `references/evolution-api-reference.md`:

```bash
git clone --depth 1 https://github.com/mcorreiam/opencode-skills.git /tmp/opencode-skills
mkdir -p ~/.config/opencode/skills
cp -r /tmp/opencode-skills/skills/evolution-api ~/.config/opencode/skills/
rm -rf /tmp/opencode-skills
```

Confirme o carregamento:

```bash
opencode debug skill
```

O resultado deve conter `evolution-api`. Valide a skill:

```bash
python3 ~/.config/opencode/skills/skill-architect/scripts/validate_skill.py ~/.config/opencode/skills/evolution-api
```

## 9. Skill flow-mattpocock (pipeline Matt Pocock)

Conduz demandas pelo pipeline das skills de Matt Pocock — classifica origem, ambiguidade e tamanho e roteia para `triage`, `grill-me/grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `tdd` e `code-review`:

```bash
git clone --depth 1 https://github.com/mcorreiam/opencode-skills.git /tmp/opencode-skills
mkdir -p ~/.config/opencode/skills
cp -r /tmp/opencode-skills/skills/flow-mattpocock ~/.config/opencode/skills/
rm -rf /tmp/opencode-skills
```

Confirme o carregamento:

```bash
opencode debug skill
```

O resultado deve conter `flow-mattpocock`. Para o pipeline completo, instale tambem as skills `triage`, `to-spec`, `to-tickets`, `implement`, `code-review` via `npx skills@latest add mattpocock/skills/<skill>` — ver `skills/flow-mattpocock/SKILL.md` para tabela de URLs.

## 10. Laboratorio WhatsApp Cloud API (WABA com CNPJ MEI - Robotizeme)

Lab real de WABA para M05 (System User) e M06 (Graph API/Webhooks). Evita 3 armadilhas que quebram o envio mesmo com token aparentemente valido.

Contexto: cria Portfolio com dados da Receita, App tipo Empresa com produto WhatsApp, numero de teste e System User long-lived para `POST /v25.0/<PHONE_NUMBER_ID>/messages`. Sem isso o lab fica em token temporario de 24h e falha `190`/`131030`.

```bash
# 1) Portfolio: business.facebook.com/settings/info
#    Razao exata "66.334.562 MARCO CORREIA DE MAGALHAES", CNPJ 66.334.562/0001-80,
#    endereco QNM 42 Conjunto F 27 - Taguatinga Norte - Brasilia/DF 72146-206,
#    tel +55 61 98475-2323, site https://robotizeme.com.br, email admin@robotizeme.com.br
#    Ative 2FA para Todos e verifique dominio via TXT DNS

# 2) App: developers.facebook.com > Criar App > Empresa > adicionar WhatsApp
#    -> Casos de uso > Conectar no WhatsApp > Etapa 1 Experimente
#    Anote: WABA_ID, PHONE_NUMBER_ID (+1 555 659-0046 teste) e TOKEN_TEMP (24h)
#    Destinatario: adicione seu numero em "Gerenciar lista de numeros" (max 5) e confirme SMS

# 3) System User long-lived: business.facebook.com/settings > Usuarios do sistema
#    Criar Funcionario robotizeme-system
#    Atribuir ATIVOS: Contas do WhatsApp > Test WABA + Apps > Robotizeme app (Gerenciar app - Acesso total)
#    Sem os dois ativos, Gerar token falha "Nenhuma permissao disponivel"
#    Gerar token > App Robotizeme app > expiracao Nunca > scopes whatsapp_business_messaging, whatsapp_business_management, business_management
```

Instrucoes de validacao, quando aplicavel:

```bash
source /tmp/robotizeme.env  # PORTFOLIO_ID, WABA_ID, PHONE_NUMBER_ID, TENANT_TOKEN, TENANT_TOKEN_TEMP
# .env deve ter chaves sem espaco (PORTFOLIO_ID, nao "PORTFOLIO ID") e chmod 600
chmod 600 /tmp/robotizeme.env

# deve retornar 200 com template jaspers_market_order_confirmation_v1
curl -s "https://graph.facebook.com/v25.0/$WABA_ID/message_templates?limit=1" -H "Authorization: Bearer $TENANT_TOKEN" | jq .data[0].name

# deve retornar robotizeme-system e id
curl -s "https://graph.facebook.com/v25.0/me?access_token=$TENANT_TOKEN" | jq .

# deve retornar 200 com wamid e wa_id (ex: 556184752329)
curl -s -X POST "https://graph.facebook.com/v25.0/$PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer $TENANT_TOKEN" -H "Content-Type: application/json" \
  -d '{"messaging_product":"whatsapp","to":"5561984752329","type":"template","template":{"name":"hello_world","language":{"code":"en_US"}}}' | jq .
```

Resultado esperado da validacao: `message_templates` com `UTILITY APPROVED`, `me` com `name robotizeme-system`, `POST messages` com `message_status accepted` e `wamid.*`. Erros comuns: `(#131030) not in allowed list` = falta allowlist do destinatario; `190 Authentication Error` / `TOKEN len 0` = .env com espaco na chave ou token truncado; `Nenhuma permissao` = esqueceu de atribuir Apps > Gerenciar app ao System User.

## Finalizacao

Ao terminar, apresente um resumo do que foi instalado ou ja existia e avise o
usuario: **reiniciar o OpenCode e necessario para carregar as alteracoes**
(configuracao e skills sao lidas apenas na inicializacao). Essa reinicializacao
e uma acao manual do usuario.
