import os

from .chatbot import MemoryChatbot
from .memory_store import PineconeMemoryStore
from .openai_gateway import OpenAIGateway


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only")
    CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.5")
    EMBEDDING_MODEL = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    MEMORY_TOP_K = int(os.getenv("MEMORY_TOP_K", "5"))
    MEMORY_MIN_SCORE = float(os.getenv("MEMORY_MIN_SCORE", "0.20"))
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "nadongban-memory")
    PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST", "")
    PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

    @classmethod
    def build_memory_store(cls) -> PineconeMemoryStore:
        return PineconeMemoryStore(
            index_name=cls.PINECONE_INDEX_NAME,
            index_host=cls.PINECONE_INDEX_HOST or None,
            namespace=cls.PINECONE_NAMESPACE,
        )

    @classmethod
    def build_chatbot(cls, store: PineconeMemoryStore) -> MemoryChatbot:
        gateway = OpenAIGateway(
            chat_model=cls.CHAT_MODEL,
            embedding_model=cls.EMBEDDING_MODEL,
        )
        return MemoryChatbot(
            gateway=gateway,
            store=store,
            top_k=cls.MEMORY_TOP_K,
            min_score=cls.MEMORY_MIN_SCORE,
        )
