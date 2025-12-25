import httpx

from agent.config import get_config

config = get_config()

import httpx

async def exercise_rag(query: str, tags:list[str]):

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"http://{config.rag.host}:{config.rag.port}/exercise/",
            json={
                "rag_name": "ex_cool",
                "query": query,
                "limit": 10,
                "tags": tags
            },
        )

    return resp


async def user_get(query: str, user_id: int):

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"http://{config.rag.host}:{config.rag.port}/user/",
            json={
                "rag_name": "tag_only",
                "query": query,
                "limit": 10,
                "tags": [str(user_id)]   
            },
        )

    return resp


async def user_save(info: str, user_id:int):

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"http://{config.rag.host}:{config.rag.port}/user/save",
            json={
                "info": info,
                "user": str(user_id)  
            },
        )

    return resp
