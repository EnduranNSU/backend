class DryReranker:
    def __call__(self, results, limit: int = 5, **kwargs):
        return results[:limit]
