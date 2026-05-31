from .agent_tool import AgentTool
from agent.utils import user_get

async def tool(query: str, user_id: int):
    return await user_get(query, user_id)
    

openai_description = {
    "type": "function",
    "function": {
            "name": "user_rag_download",
            "description": (
                "Получить информацию о пользователе из RAG. "
                "Вызывай перед составлением тренировки, чтобы узнать цели, уровень и ограничения пользователя."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Запрос для РАГа"
                    },

                }
            },
            "required": ["query"]
    }
}


user_rag_download_tool = AgentTool("user_rag_download", tool, openai_description)


