from os import getenv

from pydantic import ValidationError

from .models import Config



manual_config = {
        "model": {
            "type": "Gemini",
            "model": "gemini-2.5-flash",
            "temperature": 0.7,
            "max_tokens": 100000,
        }
    }



_config = None
def get_config() -> Config:
    global _config
    if _config is not None:
        return _config


    google_api_key = getenv("GOOGLE_API_KEY")
    if google_api_key is None:
        raise Exception("GOOGLE_API_KEY is not set")
    else:
        try:
            manual_config["model"]["API_KEY"] = google_api_key
        except KeyError as e:
            raise Exception("Failed config validation: {e}")

    try:
        _config = Config.model_validate(manual_config)
    except ValidationError as e:
        raise Exception(f"Invalid config: {e}")

    return _config
