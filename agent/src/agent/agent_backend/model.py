import os

from openai import OpenAI

# All LLM traffic goes through the in-cluster llm proxy
# (which knows how to authenticate against Yandex / OpenAI / Ollama).
client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL", "http://llm:9000/v1"),
    api_key=os.environ.get("LLM_API_KEY", "proxy"),
)

# Use "default" so the proxy substitutes whatever model is configured in env.
CHAT_MODEL = os.environ.get("LLM_CHAT_MODEL", "default")
