import unittest

from fakes import FakePineconeIndex
from nadongban.chatbot import MemoryChatbot
from nadongban.memory_store import PineconeMemoryStore


class FakeGateway:
    def embed(self, text):
        return [1.0, 0.0] if "교수" in text else [0.0, 1.0]

    def answer(self, question, memories):
        return f"검색된 기억: {len(memories)}개"


class ChatbotTests(unittest.TestCase):
    def test_chat_saves_and_retrieves_memory(self):
        store = PineconeMemoryStore(
            index_name="test-index",
            namespace="test-user",
            index=FakePineconeIndex(),
        )
        chatbot = MemoryChatbot(FakeGateway(), store, min_score=0.5)
        first = chatbot.chat("내일 교수님과 회의가 있어")
        second = chatbot.chat("교수님과 무슨 일정이 있었지?")
        self.assertEqual(first["memory_count"], 1)
        self.assertEqual(second["memory_count"], 2)
        self.assertEqual(len(second["retrieved"]), 1)
        self.assertIn("교수님과 회의", second["retrieved"][0]["text"])


if __name__ == "__main__":
    unittest.main()
