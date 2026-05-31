import json
import httpx

from agent.config import get_config
from .agent_tool import AgentTool

config = get_config()


async def tool() -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"http://{config.backend.host}:{config.backend.port}/exercise/"
        )
    exercises = resp.json()
    catalog = [{"id": e["id"], "title": e["title"]} for e in exercises]
    return json.dumps(catalog, ensure_ascii=False)


openai_description = {
    "type": "function",
    "function": {
        "name": "get_exercise_catalog",
        "description": (
            "Получить полный список упражнений из базы данных с их ID и названиями. "
            "ОБЯЗАТЕЛЬНО вызывай перед составлением тренировки — нужны точные ID упражнений для JSON."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

exercise_catalog_tool = AgentTool("get_exercise_catalog", tool, openai_description)
