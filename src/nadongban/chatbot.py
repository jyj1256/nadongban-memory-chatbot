from datetime import datetime, timezone
from typing import Protocol

from .memory_store import PineconeMemoryStore


class AIGateway(Protocol):
    def embed(self, text: str) -> list[float]: ...
    def answer(self, question: str, memories: list[str]) -> str: ...


class MemoryChatbot:
    def __init__(
        self,
        gateway: AIGateway,
        store: PineconeMemoryStore,
        top_k: int = 5,
        min_score: float = 0.2,
    ) -> None:
        self.gateway = gateway
        self.store = store
        self.top_k = top_k
        self.min_score = min_score

    def chat(self, user_text: str) -> dict:
        clean_text = user_text.strip()
        if not clean_text:
            raise ValueError("메시지를 입력해 주세요.")
        if len(clean_text) > 2_000:
            raise ValueError("메시지는 2,000자 이하여야 합니다.")

        now = datetime.now(timezone.utc)
        query_text = f"{now.isoformat()} | {clean_text}"
        query_embedding = self.gateway.embed(query_text)
        matches = self.store.search(
            query_embedding,
            top_k=self.top_k,
            min_score=self.min_score,
        )
        memory_texts = [
            f"{memory.created_at.isoformat()} | {memory.text}" for memory in matches
        ]
        answer = self.gateway.answer(clean_text, memory_texts)
        self.store.add(clean_text, query_embedding, created_at=now)

        return {
            "answer": answer,
            "retrieved": [
                {
                    "text": memory.text,
                    "created_at": memory.created_at.isoformat(),
                    "score": round(memory.score or 0.0, 4),
                }
                for memory in matches
            ],
            "memory_count": self.store.count(),
        }
