from retriever.core.pipelines import RAGPipeline
from retriever.core.pipelines.requests import HydeEmbedder
from retriever.core.pipelines.retrievers import BatchQuadrantRetriever
from retriever.core.pipelines.rerankers import DryReranker

class HydeRag():
    def __init__(self, collection_name: str):
        self.pipeline = RAGPipeline(HydeEmbedder(), BatchQuadrantRetriever(collection_name), DryReranker())

    def request(self, request:str, **kwargs):
        return self.pipeline.run(request)
