"""HyDE embedder: ask the LLM proxy for a hypothetical answer, then embed it."""
from __future__ import annotations

import os

import httpx
from sentence_transformers import SentenceTransformer


LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://llm:9000/v1")
LLM_CHAT_MODEL = os.environ.get("LLM_CHAT_MODEL", "default")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "proxy")


SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Ты используешься в HyDE для RAG-системы. "
        "Отвечай ТОЛЬКО на русском языке. "
        "Сгенерируй реалистичный, информативный текст, "
        "который мог бы быть ответом на вопрос пользователя. "
        "Не упоминай, что это гипотеза. "
        "Не задавай вопросов. "
        "Без воды и вступлений."
    ),
}


def _hyde(request: str, system_prompt_on: bool) -> str:
    messages = []
    if system_prompt_on:
        messages.append(SYSTEM_PROMPT)
    messages.append({"role": "user", "content": request})

    payload = {
        "model": LLM_CHAT_MODEL,
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.7,
    }
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{LLM_BASE_URL}/chat/completions",
                           json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    return str(data["choices"][0]["message"]["content"])


class HydeEmbedder:
    def __init__(self, system_prompt_on: bool = True):
        self.system_prompt_on = system_prompt_on
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def __call__(self, request: str, **kwargs):
        hyde_text = _hyde(request, self.system_prompt_on)
        return [self.embedder.encode(hyde_text)]
