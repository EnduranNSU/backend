from retriever.core.pipelines import RAGPipeline
from retriever.core.pipelines.requests import MiniLMEmbedder
from retriever.core.pipelines.retrievers import TagOnlyRetriever
from retriever.core.pipelines.rerankers import DryReranker

class CoolRagTagOnly():
    def __init__(self, collection_name: str):
        self.pipeline = RAGPipeline(MiniLMEmbedder(), TagOnlyRetriever(collection_name), DryReranker())

    def request(self, request:str, tags: list[str], **kwargs):
        return self.pipeline.run(request, query=request, tags=tags)
