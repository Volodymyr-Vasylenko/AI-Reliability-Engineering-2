# Lab-4: A2A, Inventory, Qdrant

**Environment:** GitHub Codespace, abox, agentregistry v0.3.3, Qdrant v1.18.0

## Що зроблено

1. **A2A Agent Card** — отримана через Well-Known URI:
```
curl http://localhost:8080/.well-known/agent-card.json
→ name: my_first_k8s_agent, protocolVersion: 0.3.0, streaming: true
```

2. **Inventory (agentregistry)** — встановлено arctl CLI + daemon, зареєстровано AI ресурси кластера:
```
arctl mcp list
io.kagent/grafana-mcp           0.7.23
io.kagent/tool-server           0.7.23
io.vasylenko/security-checker   1.0.0
```

3. **MCPG** — agentgateway v2.2.1 вже працює як MCP Gateway (Gateway API, 2 routes, 2 backends)

4. **Qdrant** — задеплоєно через Helm (`helm install qdrant qdrant/qdrant`), Running

## AI ресурси кластера (kubectl inventory)

| Тип | Кількість | Приклади |
|---|---|---|
| Agents | 7 | k8s-agent, helm-agent, my-first-k8s-agent, promql-agent, observability-agent, kgateway-agent, argo-rollouts-conversion-agent |
| MCPServers | 1 | security-checker |
| RemoteMCPServers | 3 | kagent-tool-server, kagent-grafana-mcp, security-checker-remote |
| ModelConfigs | 2 | anthropic (claude-sonnet-4-5), openai (gpt-4.1-mini) |
| Gateway | 1 | agentgateway-external |
| Vector DB | 1 | Qdrant v1.18.0 |
