from retriever.core.pipelines import RAGPipeline
from retriever.core.pipelines.requests import MiniLMEmbedder
from retriever.core.pipelines.retrievers import BatchQuadrantRetriever
from retriever.core.pipelines.rerankers import DryReranker

class SimpleRag():
    def __init__(self, collection_name: str):
        self.pipeline = RAGPipeline(
            MiniLMEmbedder(),
            BatchQuadrantRetriever(collection_name, top_n=20, must_tags=["muscles"], score_threshold=0.60),
            DryReranker(),
        )

    def request(self, request: str, **kwargs):
        return self.pipeline.run(request, **kwargs)
