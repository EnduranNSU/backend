from retriever.core.pipelines import RAGPipeline
from retriever.core.pipelines.requests import MiniLMEmbedder
from retriever.core.pipelines.retrievers import TagFirstRetriever
from retriever.core.pipelines.rerankers import MMMLMReranker

class CoolRag():
    def __init__(self, collection_name: str):
        self.pipeline = RAGPipeline(MiniLMEmbedder(), TagFirstRetriever(collection_name), MMMLMReranker(top_n=5))

    def request(self, request:str, tags: list[str], **kwargs):
        return self.pipeline.run(request, query=request, tags=tags)
