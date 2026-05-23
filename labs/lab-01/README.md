# Lab-1: Basic Agentic Infrastructure

**Environment:** GitHub Codespace, agentgateway v1.2.1 standalone  
**LLM Provider:** Anthropic (claude-haiku-4-5-20251001)

## Що зроблено

1. Встановлено agentgateway v1.2.1 як standalone binary
2. Підключено Anthropic як LLM backend 
3. Перевірено маршрутизацію запитів через gateway (curl - gateway:4000 - Anthropic API)
4. Налаштовано та протестовано localRateLimit policy (3 req/60s, token bucket)
5. Результат: requests 1-3 - HTTP 200, request 4 - HTTP 429

## Security notes

- API ключ передається через `$ENV_VAR` — не хардкодиться в конфіг
- `localRateLimit` — in-memory, не шариться між репліками. Для production потрібен `remoteRateLimit`
- Поточний конфіг не має per-client auth - будь-хто з мережевим доступом може слати запити та вичерпати rate limit для всіх
- Gateway централізує управління ключами аналогічно до Istio Ingress Gateway, але для LLM/MCP/A2A трафіку

## Файли

- `config.yaml` — конфігурація gateway
- `test-result.json` — відповідь LLM через gateway
