from datetime import datetime, timezone
import unittest

from fakes import FakePineconeIndex
from nadongban.memory_store import PineconeMemoryStore


class PineconeMemoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.index = FakePineconeIndex()
        self.store = PineconeMemoryStore(
            index_name="test-index",
            namespace="test-user",
            index=self.index,
        )

    def test_add_search_count_and_clear(self):
        now = datetime.now(timezone.utc)
        self.store.add("졸업 작품 회의", [1.0, 0.0], now)
        self.store.add("저녁 메뉴", [0.0, 1.0], now)

        results = self.store.search([0.9, 0.1], top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "졸업 작품 회의")
        self.assertEqual(self.store.count(), 2)
        self.store.clear()
        self.assertEqual(self.store.count(), 0)


if __name__ == "__main__":
    unittest.main()
