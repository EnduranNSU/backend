import httpx

from agent.config import get_config

config = get_config()

import httpx

async def exercise(exercise_id: int, token: str):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://{config.backend.host}:{config.backend.port}/exercise/{exercise_id}",
            headers=headers,
        )

    return resp

async def exercise_list(token: str):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://{config.backend.host}:{config.backend.port}/exercise",
            headers=headers,
        )

    return resp
