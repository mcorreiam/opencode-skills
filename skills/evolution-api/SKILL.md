---
name: evolution-api
description: Guia completo de uso da Evolution API para integração com WhatsApp. Configure webhooks, envie mensagens, resolva problemas comuns. Use quando o usuário precisar configurar, testar ou solucionar problemas com Evolution API e WhatsApp.
compatibility: Requer acesso à Evolution API (self-hosted ou cloud) e ao projeto agente-whatsapp.
metadata:
  provider: evolution-api
  protocol: webhook
---

# Evolution API — Guia de Uso e Integração

Guia completo para configurar e usar a Evolution API com o projeto agente-whatsapp.
Esta skill documenta padrões, armadilhas conhecidas e operações comuns.

## Quando Usar

- Configurar integração WhatsApp via Evolution API
- Enviar mensagens de texto ou mídia via API
- Configurar webhooks para receber mensagens
- Diagnosticar erros comuns (apikey, formato de número, eventos)
- Testar conexão com a instância Evolution

## Configuração Inicial

### Variáveis de Ambiente

```bash
# .env do agente-whatsapp
EVOLUTION_API_URL=https://sua-instancia.evolution-api.com
EVOLUTION_API_KEY=sua-chave-api
INSTANCE_NAME=nome-da-instancia
```

### Estrutura do Webhook

O adapter do agente-whatsapp espera:

```
POST http://ip-publico:8081/webhook
Header: apikey: <sua-chave-api>
Body: {
  "event": "MESSAGES_UPSERT",
  "instance": "nome-instancia",
  "data": {
    "messages": [...]  // ATENÇÃO: "messages" (plural), não "message"
  }
}
```

## Operações Comuns

### 1. Verificar Status da Instância

```bash
curl -s "https://evolution-api.com/instance/fetchInstances" \
  -H "apikey: SUA_CHAVE" | python3 -m json.tool
```

Resposta esperada:
```json
[{
  "name": "nome-instancia",
  "connectionStatus": "open",
  "ownerJid": "5511999999999@s.whatsapp.net",
  "number": "5511999999999"
}]
```

### 2. Enviar Mensagem de Texto

```bash
curl -s -X POST "https://evolution-api.com/message/sendText/NOME_INSTANCIA" \
  -H "apikey: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Olá! Esta é uma mensagem de teste."
  }'
```

**IMPORTANTE:** O campo `number` deve conter APENAS o número sem `@s.whatsapp.net`.

### 3. Enviar Mídia (Imagem)

```bash
curl -s -X POST "https://evolution-api.com/message/sendMedia/NOME_INSTANCIA" \
  -H "apikey: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "mediatype": "image",
    "media": "https://url-da-imagem.com/foto.jpg",
    "caption": "Legenda da imagem"
  }'
```

### 4. Configurar Webhook

```bash
curl -s -X POST "https://evolution-api.com/webhook/set/NOME_INSTANCIA" \
  -H "apikey: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "http://seu-ip:8081/webhook",
      "events": [
        "MESSAGES_UPSERT",
        "CONNECTION_UPDATE"
      ]
    }
  }'
```

### 5. Listar Eventos Disponíveis

Eventos válidos para webhook:
- `MESSAGES_UPSERT` — Mensagens recebidas/enviadas
- `CONNECTION_UPDATE` — Status da conexão
- `MESSAGES_SET` — Mensagens definidas
- `MESSAGES_UPDATE` — Mensagens atualizadas
- `CONTACTS_UPSERT` — Contatos recebidos
- `CHATS_UPSERT` — Conversas recebidas
- `CALL` — Chamadas recebidas

## Armadilhas Conhecidas

### 1. ❌ Formato de Número Incorreto

**Erro:** `{"error": "Bad Request", "response": {"message": [{"exists": false}]}}`

**Causa:** Enviar número com `@s.whatsapp.net`:
```json
{"number": "5511999999999@s.whatsapp.net"}  // ERRADO
```

**Solução:** Enviar apenas o número:
```json
{"number": "5511999999999"}  // CORRETO
```

### 2. ❌ Evento em Minúsculas

**Erro:** `webhook.events[0] is not one of enum values`

**Causa:** Usar `messages.upsert` em minúsculas.

**Solução:** Usar MAIÚSCULAS:
```json
{"events": ["MESSAGES_UPSERT"]}  // CORRETO
```

### 3. ❌ Campo "enabled" Ausente

**Erro:** `webhook requires property "enabled"`

**Solução:** Incluir sempre:
```json
{"webhook": {"enabled": true, ...}}
```

### 4. ❌ Formato "data.message" Singular

**Problema:** Webhook retorna 200 mas mensagem não é processada.

**Causa:** Evolution envia em `data.messages` (plural), não `data.message`.

**Solução:** No adapter, verificar:
```python
for message in (payload.get("data") or {}).get("messages") or []:
```

### 5. ❌ Apikey no Header

**Erro:** `{"error": "invalid apikey"}`

**Causa:** Header `apikey` não enviado ou incorreto.

**Solução:** Sempre incluir:
```bash
-H "apikey: SUA_CHAVE"
```

## Fluxo Completo de Mensagem

```
WhatsApp (Cliente)
    ↓
[Evolution API] ← Webhook POST
    ↓
[Adapter agente-whatsapp] (porta 8081)
    ↓ Valida apikey, converte formato
[Core API] (porta 8000)
    ↓ Enfileira mensagem
[Worker]
    ↓ Processa com LLM, gera resposta
[Outbound Queue]
    ↓ Adapter polla e envia
[Evolution API]
    ↓ sendText/sendMedia
WhatsApp (Cliente)
```

## Troubleshooting Rápido

| Problema | Verificar |
|----------|-----------|
| Webhook não recebe | Porta 8081 aberta no firewall? |
| `invalid apikey` | Header `apikey` enviado? Chave correta? |
| Mensagem não processada | Evento `MESSAGES_UPSERT` configurado? |
| Resposta não enviada | Número no formato correto (sem @s.whatsapp.net)? |
| Instância desconectada | Status `connectionStatus` = `open`? |

## Comandos de Diagnóstico

```bash
# Verificar se adapter está rodando
curl -s http://localhost:8081/  # Deve retornar 404 (não 502/503)

# Verificar status da instância
curl -s "https://evolution-api.com/instance/fetchInstances" \
  -H "apikey: SUA_CHAVE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['connectionStatus'])"

# Verificar outbound queue
curl -s -H "Authorization: Bearer dev-token-local" \
  http://localhost:8000/api/queue

# Logs do adapter
docker logs agente-whatsapp-adapter-1 --tail 20

# Logs do worker
docker logs agente-whatsapp-worker-1 --tail 20
```

## Segurança

- Nunca exiba a `EVOLUTION_API_KEY` em logs ou mensagens
- Use HTTPS sempre que possível em produção
- Valide o header `apikey` em todos os webhooks
- Limite os eventos do webhook apenas aos necessários

## Referência Rápida

| Operação | Endpoint |
|----------|----------|
| Enviar texto | `POST /message/sendText/{instance}` |
| Enviar mídia | `POST /message/sendMedia/{instance}` |
| Listar instâncias | `GET /instance/fetchInstances` |
| Configurar webhook | `POST /webhook/set/{instance}` |
| Status conexão | `GET /instance/connectionState/{instance}` |
