# Lab-2: Розгортання abox

**Environment:** GitHub Codespace, abox (KinD + Flux CD + agentgateway v2.2.1 + kagent)  
**LLM Provider:** Anthropic (claude-sonnet-4-5-20250929)

## Що зроблено

1. Розгорнуто abox через `make run` — KinD кластер, Flux CD, agentgateway, kagent з готовими агентами
2. Отримано доступ до UI: Kagent (port-forward 3000:8080), Agentgateway (port-forward deploy/agentgateway-external 15000:15000)
3. Створено агента `my-first-k8s-agent` через wizard з tools `k8s_get_resources` та `k8s_get_available_api_resources`
4. Агент успішно виконав запит - використав tool і повернув реальні дані з кластера (8 namespaces)

## Тест агента

```
User: List all namespaces in this cluster
Tool: k8s_get_resources
Result: 8 namespaces — all Active
```

## Notes

- Agentgateway v2.2.1 керується через Gateway API (xDS), не config.yaml як в Lab-1
- Haiku модель недоступна на Console free tier — використано claude-sonnet-4-5-20250929
- Готові агенти (helm, k8s, promql, observability) використовують дефолтний OpenAI конфіг — потребують заміни для інших ЛЛМ
