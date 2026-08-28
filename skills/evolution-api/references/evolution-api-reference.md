# Evolution API — Referência Detalhada

Carregue este arquivo quando precisar de: lista completa de eventos, formatos exatos de payload, ou diagnóstico avançado além dos 5 casos do SKILL.md.

## Eventos Válidos (webhook.events)

Use apenas MAIÚSCULAS. Envio em minúsculas retorna `webhook.events[0] is not one of enum values`.

| Evento | Quando dispara | Payload chave |
|---|---|---|
| `MESSAGES_UPSERT` | Mensagem recebida/enviada | `data.messages[]` |
| `MESSAGES_UPDATE` | Mensagem editada/status | `data.messages[]` |
| `MESSAGES_SET` | Histórico carregado | `data.messages[]` |
| `CONNECTION_UPDATE` | `connectionStatus` muda | `data.state` |
| `CONTACTS_UPSERT` | Contato novo/atualizado | `data.contacts[]` |
| `CHATS_UPSERT` | Conversa nova | `data.chats[]` |
| `CALL` | Chamada recebida | `data.call` |

Mínimo recomendado para agente-whatsapp: `["MESSAGES_UPSERT", "CONNECTION_UPDATE"]`. Limite aos necessários (segurança).

## Formato de Número

- Enviar: `"number": "5511999999999"` — apenas dígitos com DDI/DDD, sem `@s.whatsapp.net`, sem `+`, sem espaços
- Recebido: `ownerJid: "5511999999999@s.whatsapp.net"` — com sufixo. Converta removendo sufixo antes de reenviar
- Erro típico: `{"exists": false}` → número com sufixo. Corrija removendo `@s.whatsapp.net`

## Payload Webhook (adapter espera)

```json
{
  "event": "MESSAGES_UPSERT",
  "instance": "nome-instancia",
  "data": {
    "messages": [
      {
        "key": {"remoteJid": "5511999999999@s.whatsapp.net", "id": "ABC123"},
        "message": {"conversation": "Olá"},
        "pushName": "João"
      }
    ]
  }
}
```

**Plural obrigatório:** `data.messages` não `data.message`. No adapter:
```python
for message in (payload.get("data") or {}).get("messages") or []:
    process(message)
```

## Headers

- Sempre `apikey: <EVOLUTION_API_KEY>` (minúsculas `apikey`, não `apikey` com caps nem `Authorization`)
- `Content-Type: application/json` para POST com body

## Fluxo Completo (detalhe)

```
WhatsApp → [Evolution API] —POST /webhook→ [Adapter :8081] → valida apikey, normaliza JID
→ [Core API :8000] → enfileira → [Worker] → LLM → [Outbound Queue] → Adapter polla → Evolution sendText/sendMedia → WhatsApp
```

## Matriz de Diagnóstico Estendida

| Sintoma | Checar | Comando |
|---|---|---|
| Webhook não recebe | Firewall/porta 8081, `enabled:true`, evento correto | `curl -s http://localhost:8081/` → 404 ok; `docker logs adapter --tail 20` |
| `invalid apikey` | Header ausente/errado | `curl -H "apikey: $KEY" $URL/instance/fetchInstances` |
| `Bad Request exists:false` | Número com sufixo | `jq .number` no payload |
| `webhook requires property "enabled"` | Body sem enabled | Incluir `webhook.enabled=true` |
| Mensagem 200 mas não processa | `data.message` singular | Checar plural |
| Instância `close` | QR não escaneado | `GET /instance/connectionState/{instance}` |

## Segurança

- Nunca logar `EVOLUTION_API_KEY`
- HTTPS em produção, `apikey` validado em todo webhook
- Eventos mínimos necessários
