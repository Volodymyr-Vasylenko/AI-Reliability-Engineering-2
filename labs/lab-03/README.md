# Lab-3: KMCP — власний MCP сервер

**Environment:** GitHub Codespace, abox, KMCP CLI v0.3.0  
**MCP Server:** security-checker (Python/FastMCP)

## Що зроблено

1. Встановлено KMCP CLI v0.3.0 (`~/kmcp`)
2. Створено MCP сервер `security-checker` через `kmcp init python`
3. Розроблено два security tools:
   - `check_privileged_pods` — шукає поди в privileged mode
   - `check_default_serviceaccounts` — шукає поди з default ServiceAccount
4. Збілджено Docker image (`kmcp build --tag security-checker:v1.0.0`)
5. Завантажено image на всі ноди KinD (`docker save | ctr images import`)
6. Задеплоєно в кластер (`kmcp deploy --transport http`) — під Running, tools loaded
7. Створено RemoteMCPServer CRD — tools `check_privileged_pods` та `check_default_serviceaccounts` виявлені автоматично
8. Мережевий доступ підтверджено: `curl http://security-checker:3000/mcp` повертає JSON-RPC відповідь

## Проблеми

Підключення MCP сервера до агента: kagent runtime таймаутить при встановленні MCP сесії (`httpx.ConnectTimeout`). Причина — нестабільна cross-node мережа KinD після рестартів Codespace. Навіть з nodeSelector (обидва поди на одній ноді) проблема зберігається. Tools відображаються в UI агента, але виклик не проходить.

## Ключові команди

```bash
# Scaffold
~/kmcp init python security-checker --author "Volodymyr Vasylenko" --non-interactive

# Build
~/kmcp build --tag security-checker:v1.0.0

# Load to KinD
for node in abox-control-plane abox-worker abox-worker2; do
  docker save security-checker:v1.0.0 | docker exec -i $node ctr --namespace k8s.io images import -
done

# Deploy
~/kmcp deploy --image security-checker:v1.0.0 --namespace kagent --port 3000 --transport http --no-inspector

# RemoteMCPServer для інтеграції з агентом
kubectl apply -f - <<EOF
apiVersion: kagent.dev/v1alpha2
kind: RemoteMCPServer
metadata:
  name: security-checker-remote
  namespace: kagent
spec:
  protocol: STREAMABLE_HTTP
  url: http://security-checker.kagent:3000/mcp
  timeout: 120s
EOF
```

## Файли

- `k8s_security.py` — код security tools
