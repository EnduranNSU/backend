
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchAny
from retriever.config import config


class BatchQuadrantRetriever:
    def __init__(self, collection_name: str, top_n: int = 5,
                 must_tags: list[str] | None = None,
                 score_threshold: float | None = None):
        self.collection_name = collection_name
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
        self.top_n = top_n
        self.must_tags = must_tags
        self.score_threshold = score_threshold

    def __call__(self, embedded_queries: list[torch.Tensor], limit: int | None = None, **kwargs):
        fetch_n = limit if limit is not None else self.top_n
        query_filter = (
            Filter(must=[FieldCondition(key="tags", match=MatchAny(any=self.must_tags))])
            if self.must_tags else None
        )
        results = []
        for embedding in embedded_queries:
            resp = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding.tolist(),
                using="dense",
                limit=fetch_n,
                query_filter=query_filter,
                score_threshold=self.score_threshold,
            )
            results.extend(resp.points)
        return results

