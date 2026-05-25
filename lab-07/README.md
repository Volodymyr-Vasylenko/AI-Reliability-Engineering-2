# Lab-7: Vin's Questions — оцінка AI-інфраструктури

**Stack:** abox (KinD + agentgateway v2.2.1 + kagent 0.7.23)

---

## 1. How could we handle 'agent got stuck' scenarios?

В Lab-3 я стикнувся з цим напряму — агент зависав з `httpx.ConnectTimeout` коли не міг підключитись до MCP сервера security-checker. Він просто чекав і не відповідав.
Три рівні захисту:
- **Timeout** — обмежити час очікування. В RemoteMCPServer я ставив `timeout: 120s` — якщо MCP не відповів за 2 хвилини, запит обривається.
- **Ліміт на tool calls** — обмежити скільки разів агент може викликати tools за один запит (наприклад 5 разів). Інакше агент може зациклитись: tool → LLM → tool → LLM → ...
- **Graceful degradation** — якщо tools недоступні, агент відповідає тим що знає, без реальних даних. Як в DevOps Bot з Research-1 де був "Claude-only" fallback mode.

## 2. Any automatic timeout/circuit breaker patterns coming from this framework?

Так. В Lab-1 протестував `localRateLimit` — token bucket алгоритм. Зробив 4 запити, перші 3 пройшли (HTTP 200), четвертий заблокований (HTTP 429). Це вбудований механізм agentgateway.
Також є:
- **Health checks** — gateway перевіряє чи backend живий перед відправкою запиту
- **Kubernetes readiness probes** — кожен kagent агент має probe на порту 8080 (`/.well-known/agent-card.json`). Якщо агент не відповідає — Kubernetes перезапускає під.

## 3. How does kgateway handle model failover?

Через priority groups. Кожна група — набір провайдерів з однаковим пріоритетом. Якщо перша група недоступна — gateway автоматично переходить на другу.
Приклад: перша група = GPT-4 (основна), друга = GPT-3.5 (fallback). Якщо GPT-4 повертає rate limit error — gateway переключається на GPT-3.5 без участі клієнта.
Де знадобилось б: в Lab-2 `claude-sonnet-4-20250514` не працював на створеному API key — довелось вручну міняти на `claude-sonnet-4-5-20250929`. З failover groups це було б автоматично.

## 4. Can we automatically switch from OpenAI to Claude to local model?

Так. В agentgateway конфігуруються кілька priority groups — OpenAI як primary, Anthropic як secondary, локальна модель як tertiary. Gateway сам переключається при помилках.

## 5. Could we seamlessly handle the response formats from these providers?

Так. В Lab-1 я відправляв запит до Anthropic через gateway, але відповідь прийшла в стандартному OpenAI форматі — `choices[].message.content`, а не в нативному Anthropic форматі з `content[].text`. Gateway зробив трансляцію автоматично.
Клієнт працює з одним API форматом незалежно від провайдера за gateway.

## 6. Can we version the agents built from kagent?

Так, через стандартні Kubernetes практики:
- **Docker image tags** — в Lab-3 білдив `security-checker:v1.0.0`. Наступна версія буде `v1.1.0`, `v2.0.0` тощо.
- **Agent CRD в Git** — зберігаєш YAML маніфест агента в репо, кожен commit — версія. Flux відстежує зміни і деплоїть автоматично.
- **ModelConfig окремо** — можна змінити модель (з sonnet на haiku) без зміни самого агента.

## 7. Any blue/green or canary deployment patterns for agents?

В abox є `argo-rollouts-conversion-agent` — він конвертує звичайні Deployments в Argo Rollouts для canary/blue-green.
Для canary: 90% трафіку на стабільну версію агента, 10% на нову. Поступово збільшуєш відсоток. Agentgateway підтримує traffic splitting між backends для цього.
Для blue/green: два deployments (v1 і v2) за одним Service. Переключення — зміна selector. Стандартний Kubernetes паттерн.

## 8. What's the fastmcp-python framework mentioned?

Я його використовував в Lab-3. FastMCP — Python framework для MCP серверів з decorator-based API:

```python
@mcp.tool()
def check_privileged_pods(namespace: str = "") -> str:
    """Check for pods running in privileged mode."""
    # kubectl get pods, parse JSON, find privileged
```

`@mcp.tool()` автоматично реєструє функцію як MCP tool. KMCP CLI (`kmcp init python`) генерує проєкт на базі FastMCP. Мій security-checker з двома tools — це і є FastMCP сервер.

## 9. Is it the easiest path to MCP?

З мого досвіду в Lab-3 — так. Від нуля до працюючого MCP сервера в кластері:

1. `kmcp init python security-checker` — scaffold (30 секунд)
2. Написати tool функцію з `@mcp.tool()` (5 хвилин)
3. `kmcp build --tag security-checker:v1.0.0` (2 хвилини)
4. `kmcp deploy --transport http` (1 хвилина)

Результат: MCP сервер Running, tools discovered (`check_privileged_pods`, `check_default_serviceaccounts`). Найпростіший шлях з тих що існують.

## 10. About finops: how much control can I have?

В Lab-1 я протестував базові rate limiting — 3 запити за 60 секунд. Але agentgateway має набагато більше:

- **Token rate limiting** — ліміт не на запити, а на токени. Можна поставити 100K токенів/день на одного агента.
- **Spend limits** — через API keys з бюджетом. Кожен ключ має свій ліміт.
- **Observability** — OpenTelemetry метрики показують token usage per request, per model, per provider.

## 11. Token level / per agent level

**Token level:** agentgateway рахує input + output токени. Рахування у дві фази — при запиті (input) і при відповіді (output). Коли бюджет вичерпано — 429.
**Per agent level:** кожен агент отримує свій API key на gateway. Ключ A (k8s-agent) = 100K tokens/day. Ключ B (security-agent) = 50K tokens/day. Gateway enforce'ить незалежно.

В Lab-1 налаштував `localRateLimit` для блокування четвертого запиту. В production це працює так само, тільки замість кількості запитів — кількість токенів.

## 12. Can I implement custom cost controls?

Так. Кілька підходів:

- **Webhook validation** — agentgateway може відправити запит на твій webhook перед тим як пустити до LLM. Webhook перевіряє бюджет і дозволяє або блокує.
- **CEL expressions** — кастомна логіка в конфігурації gateway (наприклад, різні ліміти для різних моделей — haiku більше, opus менше).
- **External rate limit service** — зовнішній сервіс через gRPC який вирішує пускати чи ні. Повна кастомізація.

## 13. Per-agent budgets or depth of Token limits

Обидва:
**Per-agent budgets:** API key → token budget per day/month. В Lab-1 занотував що потрібен per-client auth щоб один клієнт не вичерпав ліміт для всіх.
**Depth limits:** максимум tool calls за один запит. Якщо агент зробив 5 викликів tools і все ще не отримав відповідь — зупиняємо. Запобігає recursive loops.

## 14. vLLM suitable for agents with many back and forth tool calls, or is it better for single shot inference?

vLLM оптимізований під throughput — максимум запитів через GPU за одиницю часу. Для single-shot inference (один запит → одна відповідь) це ідеально.

## 15. llm-d's scheduler - helps when agents make 15 LLM calls?

llm-d — це Kubernetes-native inference platform. Його scheduler розумніший за звичайний round-robin:

- **KV-cache locality** — якщо агент вже зробив 5 запитів на под A і KV-cache там в пам'яті, scheduler направить шостий запит на той самий під. Не треба заново обробляти весь контекст.
- **LoRA affinity** — якщо агент використовує специфічний fine-tuned adapter, scheduler направляє на під де він вже завантажений.
- **Queue-aware** — враховує скільки запитів вже чекають на кожному поді.

Для агента з 15 LLM calls це допомагає — scheduler зберігає "sticky session" до одного GPU пода і зменшує latency за рахунок KV-cache reuse. Це те що InferencePool на діаграмі abox робить.
