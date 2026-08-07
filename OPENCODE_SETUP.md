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

Instale o `xclip` para habilitar copy/paste no TUI do OpenCode:

```bash
sudo apt install xclip
```

Sem ele, o TUI nao consegue copiar nem colar texto.

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

## Finalizacao

Ao terminar, apresente um resumo do que foi instalado ou ja existia e avise o
usuario: **reiniciar o OpenCode e necessario para carregar as alteracoes**
(configuracao e skills sao lidas apenas na inicializacao). Essa reinicializacao
e uma acao manual do usuario.
