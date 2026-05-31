
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchAny
from retriever.config import config


class TagFirstRetriever:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
    
    def __call__(self, embedded_queries: list[torch.Tensor], tags: list[str], limit: int | None = None, **kwargs):
        fetch_n = limit * 4 if limit is not None else 5
        query_filter = (
            Filter(should=[FieldCondition(key="tags", match=MatchAny(any=tags))])
            if tags else None
        )
        results = []
        for embedding in embedded_queries:
            resp = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding.tolist(),
                limit=fetch_n,
                query_filter=query_filter,
            )
            results.extend(resp.points)
        return results

