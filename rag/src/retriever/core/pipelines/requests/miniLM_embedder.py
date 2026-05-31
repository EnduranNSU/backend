import torch
from sentence_transformers import SentenceTransformer

class MiniLMEmbedder:
    def __init__(self):
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def __call__(self, request:str, **kwargs) -> list[torch.Tensor]:
        return [self.embedder.encode(request)]
