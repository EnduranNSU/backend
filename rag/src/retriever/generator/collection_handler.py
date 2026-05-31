import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

from retriever.config import config


MODEL_EMBEDDINGS_SIZE = 384


class CollectionEntry:
    text: str
    payload: dict

    def __init__(self, text: str, payload: dict):
        self.text = text
        self.payload = payload


class CollectionHandler:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(f"http://{config.qdrant.host}:{config.qdrant.port}")
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.collection_name = collection_name

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={"dense": VectorParams(size=MODEL_EMBEDDINGS_SIZE, distance=Distance.COSINE)},
            )

    def write_data(self, entries: list[CollectionEntry]):
        for entry in entries:
            encoded_text = self.embedder.encode(entry.text, show_progress_bar=False).tolist()
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(
                    id=str(uuid.uuid4()),
                    vector={"dense": encoded_text},
                    payload=entry.payload,
                )],
            )
