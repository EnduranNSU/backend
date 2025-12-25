class RAGPipeline:
    def __init__(self, request, retriever, reranker):
        self.request = request
        self.retriever = retriever
        self.reranker = reranker

    def run(self, request_text: str, **kwargs):
        request = self.request(request_text, **kwargs)
        print(request)
        retrieved = self.retriever(request, **kwargs)
        print(retrieved)
        reranked = self.reranker(retrieved, **kwargs)
        print(reranked)

        return reranked

