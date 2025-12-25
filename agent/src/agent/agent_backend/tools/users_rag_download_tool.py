from .agent_tool import AgentTool
from agent.utils import user_get

async def tool(query: str, user_id: int):
    return await user_get(query, user_id)
    

openai_description = {
    "type": "function",
    "function": {
            "name": "user_rag_download",
            "description": ("Инструмент для ПОЛУЧЕНИЯ информации о пользователе из RAG",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, чтобы получить информацию о предпочтениях пользователя",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, чтобы получить информацию об ограничениях пользователя",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, чтобы узнать пользователя получше",),
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


