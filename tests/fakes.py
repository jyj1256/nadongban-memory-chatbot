class FakePineconeIndex:
    def __init__(self):
        self.vectors = {}

    def upsert(self, vectors, namespace):
        for vector in vectors:
            self.vectors[(namespace, vector["id"])] = vector

    def query(self, vector, top_k, include_metadata, namespace):
        matches = []
        for (stored_namespace, vector_id), stored in self.vectors.items():
            if stored_namespace != namespace:
                continue
            score = sum(a * b for a, b in zip(vector, stored["values"]))
            matches.append(
                {
                    "id": vector_id,
                    "score": score,
                    "metadata": stored["metadata"],
                }
            )
        matches.sort(key=lambda item: item["score"], reverse=True)
        return {"matches": matches[:top_k]}

    def describe_index_stats(self):
        counts = {}
        for namespace, _ in self.vectors:
            counts[namespace] = counts.get(namespace, 0) + 1
        return {
            "namespaces": {
                namespace: {"vector_count": count}
                for namespace, count in counts.items()
            }
        }

    def delete(self, delete_all, namespace):
        if delete_all:
            self.vectors = {
                key: value
                for key, value in self.vectors.items()
                if key[0] != namespace
            }
