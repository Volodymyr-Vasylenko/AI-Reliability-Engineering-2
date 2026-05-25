# Lab-5: Agent Sandbox та Tracing

**Environment:** GitHub Codespace (abox), Agent Sandbox v0.4.6, Google Colab (Phoenix + LangChain)

## Що зроблено

1. **Agent Sandbox** — встановлено controller v0.4.6, створено Sandbox з NetworkPolicy
2. **Colab LangChain tracing** — виконано notebook з Phoenix tracing та LLM evaluations

## Agent Sandbox + NetworkPolicy

Створено `security-sandbox` з мережевою ізоляцією:
- Ingress дозволено тільки з kagent namespace (агенти)
- Egress дозволено тільки DNS (port 53/UDP)
- Все інше заблоковано — принцип least privilege для AI sandbox

```
kubectl get sandbox -A
NAMESPACE   NAME               AGE
default     security-sandbox   5m

kubectl get networkpolicy
NAME                POD-SELECTOR                                AGE
sandbox-isolation   agents.x-k8s.io/sandbox=security-sandbox   5m
```

## Colab: LangChain Tracing з Phoenix

Виконано notebook по кроках:
1. Встановлено Phoenix, LangChain, OpenAI
2. Запущено Phoenix (`px.launch_app()`) — observability UI для AI
3. Побудовано RAG chain: OpenAI Embeddings → FAISS vector store → ChatGPT retrieval chain
4. Виконано 5 queries з tracing — кожен крок записаний як span (retrieval, LLM call, output parsing)
5. Evaluations: запущено faithfulness та correctness evaluators через gpt-3.5-turbo
6. Phoenix UI — постійно помилка 403. Не зміг виправити.

Проблеми:
- gpt-4-turbo-preview постыйно фейлився → замінено на gpt-3.5-turbo
- Phoenix UI сесію не зміг відкрити
