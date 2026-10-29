from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .models import Memory


def _read(value: Any, key: str, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


class PineconeMemoryStore:
    """Long-term memory store backed by a Pinecone dense-vector index."""

    def __init__(
        self,
        index_name: str,
        namespace: str = "default",
        index_host: str | None = None,
        index=None,
    ) -> None:
        self.namespace = namespace
        if index is not None:
            self.index = index
            return

        from pinecone import Pinecone

        client = Pinecone()
        self.index = (
            client.Index(host=index_host)
            if index_host
            else client.Index(index_name)
        )

    def add(
        self,
        text: str,
        embedding: list[float],
        created_at: datetime | None = None,
    ) -> Memory:
        created_at = created_at or datetime.now(timezone.utc)
        memory = Memory(id=str(uuid4()), text=text, created_at=created_at)
        self.index.upsert(
            vectors=[
                {
                    "id": memory.id,
                    "values": embedding,
                    "metadata": {
                        "text": memory.text,
                        "created_at": memory.created_at.isoformat(),
                    },
                }
            ],
            namespace=self.namespace,
        )
        return memory

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[Memory]:
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace,
        )
        memories: list[Memory] = []
        for match in _read(response, "matches", []):
            score = float(_read(match, "score", 0.0))
            metadata = _read(match, "metadata", {}) or {}
            text = _read(metadata, "text", "")
            created_at = _read(metadata, "created_at")
            if score < min_score or not text or not created_at:
                continue
            memories.append(
                Memory(
                    id=str(_read(match, "id", "")),
                    text=str(text),
                    created_at=datetime.fromisoformat(str(created_at)),
                    score=score,
                )
            )
        return memories

    def count(self) -> int:
        stats = self.index.describe_index_stats()
        namespaces = _read(stats, "namespaces", {}) or {}
        namespace_stats = _read(namespaces, self.namespace)
        return int(_read(namespace_stats, "vector_count", 0)) if namespace_stats else 0

    def clear(self) -> None:
        self.index.delete(delete_all=True, namespace=self.namespace)
