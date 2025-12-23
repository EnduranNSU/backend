
import torch
from qdrant_client import QdrantClient
from retriever.config import config


class BatchQuadrantRetriever:
    def __init__(self, collection_name: str,  top_n: int = 5):
        self.collection_name = collection_name
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
        self.top_n = top_n
    
    def __call__(self, embedded_queries: list[torch.Tensor], **kwargs):
        results = []
        for embedding in embedded_queries:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector= embedding.tolist(),
                limit=self.top_n,
            )
            results.extend(hits)
        return results

