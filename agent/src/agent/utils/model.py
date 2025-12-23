from langchain_google_genai import ChatGoogleGenerativeAI

from config import get_config


_model = None

def get_model(model_name:str|None=None):
    config = get_config()

    global _model
    if _model is None:
        _model = ChatGoogleGenerativeAI(
            model=config.model.model,
            temperature=config.model.temperature,
            max_tokens=config.model.max_tokens,
        )

    return _model
