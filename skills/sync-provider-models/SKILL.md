---
name: sync-provider-models
description: 'Verifica e sincroniza modelos de providers do opencode (alibaba-token-plan, opencode-go, etc.) consultando a API remota `/models` e diff contra o cache local. Use when user asks to check for new models, update model list, sync providers, or "verificar modelos novos" (PT: Use quando precisar checar modelos novos em providers do opencode ou atualizar a lista de modelos). Do NOT use for adding custom user-defined models, debugging provider auth, or listing past sessions.'
license: CC-BY-4.0
compatibility: "Requer python3 (stdlib apenas) + ~/.local/share/opencode/auth.json + ~/.cache/opencode/models.json. Sem curl/sqlite3/binários externos."
metadata:
  author: mcorreiam
  version: 1.0.0
  requested_name: sync_provider_models
  storage: json-cache
  scope: single|all
  mode: report|apply
---

# Sync Provider Models

Verifica e sincroniza a lista de modelos de um provider do opencode (ex:
`alibaba-token-plan`, `opencode-go`) contra a API remota do próprio provider.
Detecta **modelos novos** (disponíveis na API mas ausentes no cache) e
**modelos no cache não anunciados** pela API, podendo adicionar os novos ao
`~/.cache/opencode/models.json`.

## Atalho — script bundleado (recomendado)

Um comando único substitui a sequência manual (auth → cache → curl → diff →
patch). Use sempre que possível.

```bash
# dentro do diretório da skill instalada (~/.config/opencode/skills/sync-provider-models)
# ou do repo (skills/sync-provider-models)

# 1. Apenas relatório (read-only, não toca no cache)
scripts/sync_models.sh --provider alibaba-token-plan
scripts/sync_models.sh --provider opencode-go
scripts/sync_models.sh --provider all            # todos os providers com auth

# 2. Aplicar: adiciona modelos novos ao cache (com backup automático)
scripts/sync_models.sh --provider alibaba-token-plan --apply
scripts/sync_models.sh --provider opencode-go --apply
scripts/sync_models.sh --provider all --apply

# 3. Listar providers conhecidos
scripts/sync_models.sh --list-providers

# 4. Ajustar timeout HTTP (default 30s) e suprimir backup
scripts/sync_models.sh --provider opencode-go --apply --timeout 60 --no-backup

scripts/sync_models.sh --help
```

O que o script faz por você:

1. **Carrega credenciais com segurança:** lê a API key de
   `~/.local/share/opencode/auth.json` (chave `key` do bloco do provider).
   **Nunca** exibe a chave nem a grava em arquivo temporário.
2. **Descobre baseUrl do provider:** lê `~/.cache/opencode/models.json`
   (`<provider>.api`) — ex: `alibaba-token-plan` →
   `https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`;
   `opencode-go` → `https://opencode.ai/zen/go/v1`.
3. **Consulta a API remota:** `GET {baseUrl}/models` (compatível OpenAI) com
   header `Authorization: Bearer <key>`, via `urllib` (stdlib, sem curl).
4. **Diff bidirecional:**
   - `NOVOS` = remoto ∖ cache → candidatos a adicionar.
   - `NO CACHE SEM REMOTO` = cache ∖ remoto → **NUNCA removidos** (podem ser
     `status: "deprecated"` mas ainda utilizáveis, ou multimodais não
     enumerados pelo `/models` — ex: `wan2.7-image`, `happyhorse-*` no
     `alibaba-token-plan`, `ox-alpha-free` no `opencode-go`).
5. **Com `--apply`:** backup do cache (`models.json.bak{N}`), escolhe um
   **template** para cada modelo novo (mesma `family` > mesmo prefixo antes do
   primeiro `-` > primeiro disponível), sobrescreve `id`/`name`/datas e grava.
   Se a API retornar `created` (timestamp), usa a data convertida em vez de
   hoje (heurística de magnitude s/ms/µs, fuso local via
   `datetime.date.fromtimestamp`).

## Procedimento Manual (fallback detalhado)

Siga apenas se o script bundleado não estiver disponível ou precisar depurar.

1. **Localize provider e baseUrl no cache:**
   ```python
   import json
   cache = json.load(open("~/.cache/opencode/models.json"))
   p = cache["alibaba-token-plan"]
   print(p["api"])          # baseUrl
   print(list(p["models"]))  # modelos em cache
   ```

2. **Obtenha a API key (segurança):**
   ```python
   auth = json.load(open("~/.local/share/opencode/auth.json"))
   key = auth["alibaba-token-plan"]["key"]  # nunca imprima a chave
   ```

3. **Consulte a API remota:**
   ```bash
   curl -s --max-time 30 "{baseUrl}/models" -H "Authorization: Bearer ${KEY}" \
     -o /tmp/models.json -w "HTTP %{http_code}\n"
   ```
   Formato esperado (compatível OpenAI): `{"data": [{"id": "...", "created": ..., "object": "model"}, ...]}`.

4. **Calcule o diff:**
   ```python
   cached = set(cache[provider]["models"].keys())
   remote = {m["id"] for m in json.load(open("/tmp/models.json"))["data"]}
   print("NOVOS:", sorted(remote - cached))
   print("REMOVIDOS:", sorted(cached - remote))  # não remover — ver regra abaixo
   ```

5. **Adicione novos (com backup):** copie uma entrada existente da mesma
   `family` como template, sobrescreva `id`/`name`/`release_date`/
   `last_updated`, e grave o JSON de volta. Use
   `datetime.date.fromtimestamp(created)` se a API retornar `created`.

## Regras Fundamentais

1. **Read-only por padrão.** Sem `--apply`, o script apenas reporta. O cache
   só é modificado com `--apply` explícito.
2. **Backup obrigatório antes de aplicar.** `--no-backup` é opt-in, nunca
   default. Backups incrementais: `models.json.bak`, `.bak2`, `.bak3`...
3. **Nunca remover modelos do cache.** Modelos ausentes no `/models` remoto
   podem estar `deprecated` (ex: `ox-alpha-free`) ou ser multimodais não
   enumerados pelo endpoint (ex: `wan2.7-image`, `happyhorse-*`). Remover do
   cache quebraria referências em `model.json` (variantes/favoritos) e
   historico. Apenas reportar como "no cache sem remoto".
4. **Template conservador.** Ao adicionar, herdar shallow-copy de modelo da
   mesma `family` para preservar `reasoning_options`, `modalities`, `limit`,
   `cost`, `compat`. Campos `id`/`name`/datas sempre sobrescritos.
5. **Datas via `created` quando disponível.** Se a API retornar `created`
   (unix timestamp), converter com heurística de magnitude (s/ms/µs) e fuso
   local; senão usar `today`.
6. **Segurança de credenciais.** Nunca exibir, logar ou gravar a API key em
   arquivo temporário. Ler de `auth.json` apenas em memória.

## Providers Conhecidos

| Provider | baseUrl | Notas |
| :--- | :--- | :--- |
| `alibaba-token-plan` | `https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` | Alibaba Token Plan (MaaS). `/models` enumera apenas texto/áudio; multimodais (wan, happyhorse, qwen-image) não aparecem mas funcionam. |
| `opencode-go` | `https://opencode.ai/zen/go/v1` | OpenCode Go/Zen. Modelos `status: "deprecated"` (ex: `ox-alpha-free`) permanecem no cache. |
| `opencode` | `https://opencode.ai/zen/v1` | OpenCode default Zen. |
| `alibaba-coding-plan` | (do cache) | Alibaba Coding Plan. |

> Outros providers presentes em `auth.json` também podem funcionar via
> `--provider <id>` se tiverem bloco no `models.json` com `api` + `models`.

## Formato da Resposta

Para cada provider processado, emita um bloco:

```
=== <provider> ===
base_url: <url>
cache: <N> modelos | remoto: <M> | comum: <K>
NOVOS (<n>):
  + <id1>
  + <id2>
NO CACHE SEM REMOTO (<m>) — não removidos (podem ser deprecated/multimodais):
  - <id1>
```

Em `--apply`, adicionalmente em `stderr`:
```
backup criado: ~/.cache/opencode/models.json.bak
[<provider>] adicionados ao cache: <id1>, <id2>
cache atualizado: <n> modelo(s) adicionado(s) em ~/.cache/opencode/models.json
```

Sem introdução, explicação ou texto livre além dos blocos acima. Erros em
`stderr` com prefixo `[<provider>] ERRO:`.

## Examples

### Example 1: checar alibaba-token-plan (report only)

User says: "verifique se no token plan alibaba tem algum modelo novo"
Actions: `scripts/sync_models.sh --provider alibaba-token-plan`
Result:
```
=== alibaba-token-plan ===
base_url: https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
cache: 27 modelos | remoto: 12 | comum: 10
NOVOS (2):
  + qwen-audio-3.0-realtime-plus
  + qwen-audio-3.0-tts-plus
NO CACHE SEM REMOTO (17) — não removidos (podem ser deprecated/multimodais):
  - MiniMax-M2.5
  - happyhorse-1.1-i2v
  - wan2.7-image
  ...
```

### Example 2: aplicar novos ao opencode-go

User says: "atualiza a lista do opencode-go"
Actions: `scripts/sync_models.sh --provider opencode-go --apply`
Result (stderr): `backup criado: ...bak2` + `[opencode-go] adicionados ao cache: hy3-preview` + `cache atualizado: 1 modelo(s) adicionado(s) em ~/.cache/opencode/models.json`

### Example 3: sincronizar todos de uma vez

User says: "sincroniza todos os providers"
Actions: `scripts/sync_models.sh --provider all --apply`
Result: bloco por provider com diff + aplicação incremental dos novos.

## Troubleshooting

### Error: `provider '<id>' não encontrado no cache`

Cause: o ID do provider não existe em `~/.cache/opencode/models.json`.
Solution: liste com `--list-providers`; confirme o ID exato (case-sensitive,
hífen vs underscore). Se o provider nunca teve modelos cacheados, ele não
aparece — o cache é populado pelo opencode na primeira consulta.

### Error: `sem credencial para '<id>' em auth.json`

Cause: não há bloco `<id>.key` em `~/.local/share/opencode/auth.json`.
Solution: autentique o provider via opencode UI/CLI primeiro, ou confirme que
o ID em `auth.json` é o mesmo do `models.json` (ex:
`alibaba-token-plan` vs `alibaba-coding-plan`).

### Error: `HTTP/fetch falhou: URLError(...)`

Cause: rede, SSL, ou baseUrl incorreta; ou o provider exige header não-`Bearer`.
Solution: valide a URL com `curl -v "{baseUrl}/models" -H "Authorization: Bearer $KEY"`.
Confira se o `api` no `models.json` está correto (não é o `doc`/homepage).

### Error: modelo adicionado não aparece no seletor do opencode

Cause: o opencode carrega o cache no startup e pode sobrescrevê-lo no próximo
sync. As adições via skill são **efêmeras** — persistem até o opencode
re-sincronizar.
Solution: para persistência definitiva, adicione o bloco do modelo no
`opencode.jsonc` sob `provider.<id>.models` (config imutável pelo sync). A
skill não faz isso automaticamente para evitar quebrar o config do usuário —
pergunte antes.

### Error: datas estranhas (ex: 1970 ou ano 50000)

Cause: `created` retornado pela API em unidade inesperada, ou `None`.
Solution: a heurística de magnitude (s/ms/µs) cobre os 3 casos comuns. Se vier
`None`, cai para `today.isoformat()`. Valide com
`python3 -c "import datetime; print(datetime.date.fromtimestamp(<ts>))"`.
