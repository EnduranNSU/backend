from sentence_transformers import CrossEncoder

class MMMLMReranker:
    def __init__(self, top_n: int = 5):
        self.reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            device="cpu"
        )
        self.top_n=top_n

    def __call__(self, results, query:str|None = None, **kwargs):
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
            reverse=True
        )

        result = [sp for sp, _ in reranked[:self.top_n]]

        return result
