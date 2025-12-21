class RAGPipeline:
    def __init__(self, request, retriever, reranker):
        self.request = request
        self.retriever = retriever
        self.reranker = reranker

    def run(self, request_text: str, **kwargs):
        request = self.request(request_text, **kwargs)
        retrieved = self.retriever(request, **kwargs)
        reranked = self.reranker(retrieved, **kwargs)

        return reranked

