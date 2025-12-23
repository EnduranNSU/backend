class DryReranker:
    def __call__(self, results, top_n: int = 5, **kwargs):
        return results[:5]
