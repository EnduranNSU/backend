import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer


from airflow.hooks.base import BaseHook

MODEL_EMBEDDINGS_SIZE = 384


def save_to_qdrant(id: int, ex_title: str, clean_llm_response: str):
    conn = BaseHook.get_connection("qdrant")
    extra = conn.extra_dejson
    client = QdrantClient(f"http://{extra['host']}:{extra['port']}")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    collection_name = "exercises"
    if not client.collection_exists(collection_name):
        MODEL_EMBEDDINGS_SIZE = 384
        client.create_collection(
               collection_name=collection_name,
               vectors_config=VectorParams(size=MODEL_EMBEDDINGS_SIZE, distance=Distance.COSINE),
            )

    splitted_text = clean_llm_response.split("\n\n\n")
    tagged_parts = [
        ('general', splitted_text[0]),
        ('technique', splitted_text[1]),
        ('muscles', splitted_text[2]),
        ('limitations', splitted_text[3]),
        ('mistakes', splitted_text[4]),
        ('alternatives', splitted_text[5])
    ]

    points = []
    for part in tagged_parts:
        encoded_text = embedder.encode(part[1], show_progress_bar=True).tolist()
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=encoded_text,
            payload = {
                "text": part[1],
                "source": id,
                "tags": [
                    ex_title,
                    part[0]
                ]
            }
        ))


    client.upsert(
        collection_name = collection_name,
        points = points
    )
