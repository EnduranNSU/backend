from pydantic import BaseModel

class BackendConfig(BaseModel):
    host: str
    port: str

class RAGConfig(BaseModel):
    host: str
    port: str

class Config(BaseModel):
    backend: BackendConfig
    rag: RAGConfig



_config = {
    "backend": {
        "host": "backend",
        "port": "8000",
    },
    "rag": {
        "host": "rag",
        "port": "8888",
    }
}

def get_config():
    return Config.model_validate(_config)
