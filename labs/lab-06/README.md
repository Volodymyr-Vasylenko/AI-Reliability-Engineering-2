# Lab-6: RAG з Qdrant

**Environment:** GitHub Codespace, Qdrant v1.18.0, Gemini Embedding API

## Що зроблено

1. Створено knowledge base з 10 документів по Kubernetes security
2. Згенеровано embeddings через Gemini REST API (model: gemini-embedding-001, dimension: 3072)
3. Завантажено документи в Qdrant (collection: k8s_security, COSINE distance)
4. Виконано semantic search — агент знаходить релевантні документи по запиту

## Результат

```
Query: How to secure ServiceAccounts in Kubernetes?

Top 3 results:
  1. [score: 0.778] Default ServiceAccounts should not be used for workloads. Create dedicated ServiceAccounts with minimal RBAC permissions.
  2. [score: 0.688] RBAC roles should follow least privilege principle. Avoid ClusterRoleBindings with cluster-admin.
  3. [score: 0.666] Pod Security Standards (Baseline, Restricted) should be enforced at namespace level using admission controllers.
```

Semantic search правильно ранжує: найвищий score у документа який напряму відповідає на питання про ServiceAccounts.

## Файли

- `rag.py` — скрипт RAG pipeline (Gemini embeddings → Qdrant → semantic search)
