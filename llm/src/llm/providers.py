"""Per-provider config: where to forward and how to authenticate.

All clients send OpenAI-compatible JSON to this service. We:
  1. pick a provider via env (LLM_PROVIDER)
  2. rewrite the auth header (Yandex needs `Api-Key`, OpenAI needs `Bearer`)
  3. optionally substitute the `model` field if the client sent "default"
  4. forward upstream and stream the response back
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    base_url: str
    auth_scheme: str          # "Api-Key" or "Bearer"
    api_key: str
    chat_model: str           # default model to substitute when client sends "default"


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def load_config() -> ProviderConfig:
    provider = _env("LLM_PROVIDER", "yandex").lower()

    if provider == "yandex":
        folder = _env("YANDEX_FOLDER_ID", "")
        return ProviderConfig(
            base_url=_env("LLM_BASE_URL", "https://llm.api.cloud.yandex.net/v1"),
            auth_scheme="Api-Key",
            api_key=_env("YANDEX_API_KEY", ""),
            chat_model=_env(
                "LLM_CHAT_MODEL",
                f"gpt://{folder}/qwen3-235b-a22b-fp8/latest" if folder else "",
            ),
        )

    if provider == "openai":
        return ProviderConfig(
            base_url=_env("LLM_BASE_URL", "https://api.openai.com/v1"),
            auth_scheme="Bearer",
            api_key=_env("OPENAI_API_KEY", ""),
            chat_model=_env("LLM_CHAT_MODEL", "gpt-4o-mini"),
        )

    if provider == "ollama":
        return ProviderConfig(
            base_url=_env("LLM_BASE_URL", "http://ollama:11434/v1"),
            auth_scheme="Bearer",
            api_key=_env("OPENAI_API_KEY", "ollama"),
            chat_model=_env("LLM_CHAT_MODEL", "qwen2.5:3b"),
        )

    raise RuntimeError(f"Unknown LLM_PROVIDER={provider!r}. Use yandex|openai|ollama.")
