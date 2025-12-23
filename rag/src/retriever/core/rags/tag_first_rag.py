from retriever.core.pipelines import RAGPipeline
from retriever.core.pipelines.requests import MiniLMEmbedder
from retriever.core.pipelines.retrievers import TagFirstRetriever
from retriever.core.pipelines.rerankers import DryReranker

class TagFirstRag():
    def __init__(self, collection_name: str):
        self.pipeline = RAGPipeline(MiniLMEmbedder(), TagFirstRetriever(collection_name), DryReranker())

    def request(self, request:str, tags: list[str], **kwargs):
        return self.pipeline.run(request, tags=tags)
