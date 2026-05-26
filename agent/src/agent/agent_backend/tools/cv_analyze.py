"""Tool: download a video from a URL and ask the cv_service to score the squat."""
from __future__ import annotations

import json

import httpx

from agent.config import get_config
from .agent_tool import AgentTool


config = get_config()


async def tool(video_url: str) -> str:
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
        # 1. Download the video the user uploaded somewhere reachable (minio link, etc.)
        try:
            video_resp = await client.get(video_url)
            video_resp.raise_for_status()
        except httpx.HTTPError as exc:
            return f"Не удалось скачать видео по ссылке: {exc}"

        # 2. POST it to cv_service /cv/analyze as multipart.
        files = {"video": ("squat.mp4", video_resp.content, "video/mp4")}
        try:
            cv_resp = await client.post(
                f"http://{config.cv.host}:{config.cv.port}/cv/analyze",
                files=files,
            )
            cv_resp.raise_for_status()
        except httpx.HTTPError as exc:
            return f"Ошибка CV-сервиса: {exc}"

        return json.dumps(cv_resp.json(), ensure_ascii=False)


openai_description = {
    "type": "function",
    "function": {
        "name": "cv_analyze_squat",
        "description": (
            "Анализирует видео приседаний пользователя через CV-сервис: "
            "считает количество повторений, глубину и заваливание коленей внутрь. "
            "Используй, когда пользователь скинул ссылку на видео своей тренировки."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "Прямая ссылка на видео файл (mp4/mov/webm)",
                }
            },
            "required": ["video_url"],
        },
    },
}


cv_analyze_tool = AgentTool("cv_analyze_squat", tool, openai_description)
