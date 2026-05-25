import os
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

documents = [
    "Privileged containers have full access to the host system. Always set securityContext.privileged to false in pod specs.",
    "Default ServiceAccounts should not be used for workloads. Create dedicated ServiceAccounts with minimal RBAC permissions.",
    "Network Policies should be applied to every namespace to restrict east-west traffic between pods.",
    "Pod Security Standards (Baseline, Restricted) should be enforced at namespace level using admission controllers.",
    "Secrets should be encrypted at rest using KMS provider. Never store secrets in plain text in etcd.",
    "Container images should be scanned for vulnerabilities before deployment. Use admission webhooks to block images with critical CVEs.",
    "RBAC roles should follow least privilege principle. Avoid ClusterRoleBindings with cluster-admin.",
    "Audit logging should be enabled on the API server to track all authentication and authorization decisions.",
    "Service mesh like Istio provides mTLS between pods, eliminating the need for application-level TLS.",
    "Runtime security tools like Falco can detect anomalous behavior inside containers in real time.",
]

def get_embedding(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GEMINI_API_KEY}"
    resp = requests.post(url, json={"model": "models/gemini-embedding-001", "content": {"parts": [{"text": text}]}})
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]

print("Generating embeddings with Gemini REST API...")
embeddings = [get_embedding(doc) for doc in documents]
print(f"Generated {len(embeddings)} embeddings, dimension: {len(embeddings[0])}")

print("Connecting to Qdrant...")
client = QdrantClient(host="localhost", port=6333)

collection_name = "k8s_security"
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE),
    )

points = [
    PointStruct(id=i, vector=emb, payload={"text": doc})
    for i, (emb, doc) in enumerate(zip(embeddings, documents))
]
client.upsert(collection_name=collection_name, points=points)
print(f"Uploaded {len(points)} documents to Qdrant collection '{collection_name}'")

query = "How to secure ServiceAccounts in Kubernetes?"
print(f"\nQuery: {query}")
query_embedding = get_embedding(query)

results = client.query_points(collection_name=collection_name, query=query_embedding, limit=3)
print("\nTop 3 results:")
for i, point in enumerate(results.points):
    print(f"  {i+1}. [score: {point.score:.3f}] {point.payload['text']}")
