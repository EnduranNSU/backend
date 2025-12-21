from pydantic import BaseModel, Field


class Qdrant(BaseModel):
    host: str
    port: int = Field(..., ge=0, le=65535)

class EmbedderModel(BaseModel):
    name : str
    embedding_size: int


class Config(BaseModel):
    qdrant: Qdrant
    llm_model: EmbedderModel



_config = {
    "qdrant": {
        "host": "localhost",
        "port": 6333,
    },
    "llm_model": {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_size": 384
    }
}

config = Config.model_validate(_config)
