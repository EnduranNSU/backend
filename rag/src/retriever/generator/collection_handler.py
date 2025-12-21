import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import Distance, VectorParams

from retriever.config import config


MODEL_EMBEDDINGS_SIZE = 384


class CollectionEntry:
    text: str
    payload: dict

    def __init__(self, text:str, payload:dict):
        self.text = text
        self.payload = payload

class CollectionHandler:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = collection_name

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
               collection_name=collection_name,
               vectors_config=VectorParams(size=MODEL_EMBEDDINGS_SIZE, distance=Distance.COSINE),
            )

    def write_data(self, entries: list[CollectionEntry]):
        for entry in entries:
            print([entry.text])
            encoded_text = self.embedder.encode(entry.text, show_progress_bar=True).tolist()
            payload = entry.payload

            self.client.upsert(
                collection_name=self.collection_name,
                points = [
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=encoded_text,
                        payload = payload
                    )
                ]
            )
