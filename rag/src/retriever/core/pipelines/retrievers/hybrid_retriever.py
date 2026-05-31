import torch
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

from retriever.config import config


def _sparse_dot(q_indices, q_values, d_indices, d_values) -> float:
    d_map = dict(zip(d_indices.tolist(), d_values.tolist()))
    return sum(float(qv) * d_map.get(int(qi), 0.0)
               for qi, qv in zip(q_indices.tolist(), q_values.tolist()))


_MUSCLES_FILTER = Filter(must=[FieldCondition(key="tags", match=MatchAny(any=["muscles"]))])
_TECHNIQUE_FILTER = Filter(must=[FieldCondition(key="tags", match=MatchAny(any=["technique"]))])


class HybridRetriever:
    def __init__(self, collection_name: str, top_n: int = 20):
        self.collection_name = collection_name
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
        self.sparse_embedder = SparseTextEmbedding(model_name="Qdrant/bm25")
        self.top_n = top_n

    def __call__(self, embedded_queries: list[torch.Tensor],
                 limit: int | None = None, query: str = "", **kwargs):
        top_n = limit or self.top_n
        fetch_n = top_n * 4

        all_results = []
        seen_ids: set = set()

        for embedding in embedded_queries:
            vec = embedding.tolist()
            for chunk_filter in (_MUSCLES_FILTER, _TECHNIQUE_FILTER):
                resp = self.client.query_points(
                    collection_name=self.collection_name,
                    query=vec,
                    limit=fetch_n,
                    query_filter=chunk_filter,
                )
                for point in resp.points:
                    if point.id not in seen_ids:
                        seen_ids.add(point.id)
                        all_results.append(point)

        if not all_results:
            return []

        # BM25 scoring via fastembed (handles Russian stemming)
        texts = [r.payload.get("text", "") for r in all_results]
        query_sparse = list(self.sparse_embedder.embed([query]))[0]
        doc_sparses = list(self.sparse_embedder.embed(texts))

        bm25_scores = [
            _sparse_dot(query_sparse.indices, query_sparse.values,
                        ds.indices, ds.values)
            for ds in doc_sparses
        ]

        # Linear combination: 75% BM25 (primary signal) + 25% dense (tiebreaker)
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        combined = [
            (0.75 * (bs / max_bm25) + 0.25 * r.score, r)
            for bs, r in zip(bm25_scores, all_results)
        ]
        combined.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in combined[:top_n]]
