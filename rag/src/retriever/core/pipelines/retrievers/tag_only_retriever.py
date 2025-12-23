
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchAny
from retriever.config import config


class TagOnlyRetriever:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
    
    def __call__(self, embedded_queries: list[torch.Tensor], tags: list[str], **kwargs):
        results = []
        for embedding in embedded_queries:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector= embedding.tolist(),
                limit=5,

                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="tags",
                            match=MatchAny(any=tags)
                        )
                    ]
                )
            )
            results.extend(hits)
        return results

