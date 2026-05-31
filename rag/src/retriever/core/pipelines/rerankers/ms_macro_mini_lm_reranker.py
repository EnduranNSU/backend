from sentence_transformers import CrossEncoder

class MMMLMReranker:
    def __init__(self, top_n: int = 5):
        self.reranker = CrossEncoder(
            "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
            device="cpu"
        )
        self.top_n=top_n

    def __call__(self, results, query: str | None = None, limit: int | None = None, **kwargs):
        if query is None:
            raise ValueError("query is required")

        pairs = [
            (query, doc.payload["text"])
            for doc in results
        ]

        scores = self.reranker.predict(pairs)

        reranked = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        top_n = limit if limit is not None else self.top_n
        return [sp for sp, _ in reranked[:top_n]]
