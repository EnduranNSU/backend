from pydantic import BaseModel


class BackendConfig(BaseModel):
    host: str
    port: str


class RAGConfig(BaseModel):
    host: str
    port: str


class CVConfig(BaseModel):
    host: str
    port: str


class Config(BaseModel):
    backend: BackendConfig
    rag: RAGConfig
    cv: CVConfig


_config = {
    "backend": {
        "host": "backend",
        "port": "8000",
    },
    "rag": {
        "host": "retriever",
        "port": "8888",
    },
    "cv": {
        "host": "cv_service",
        "port": "9090",
    },
}


def get_config():
    return Config.model_validate(_config)
