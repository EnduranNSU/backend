from retriever.core.pipelines import RAGPipeline
from retriever.core.pipelines.requests import MiniLMEmbedder
from retriever.core.pipelines.retrievers import BatchQuadrantRetriever
from retriever.core.pipelines.rerankers import DryReranker

class SimpleRag():
    def __init__(self, collection_name: str):
        self.pipeline = RAGPipeline(MiniLMEmbedder(), BatchQuadrantRetriever(collection_name), DryReranker())

    def request(self, request:str):
        return self.pipeline.run(request)
