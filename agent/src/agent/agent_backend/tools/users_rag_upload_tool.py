from .agent_tool import AgentTool
from agent.utils import user_save

async def tool(info: str, user_id: int):
    return await user_save(info, user_id)
    

openai_description = {
    "type": "function",
    "function": {
            "name": "user_rag_download",
            "description": ("Инструмент для сохранение информации о пользователе в RAG",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, чтобы сохранить информацию о предпочтениях пользователя",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, чтобы сохранить информацию об ограничениях пользователя",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, чтобы сохранить информацию, которая поможет узнать пользователя получше",),
            "parameters": {
                "type": "object",
                "properties": {
                    "info": {
                        "type": "string",
                        "description": "Информация, которую требуется сохранить в RAG"
                    }
                }
            },
            "required": ["info"]
    }
}


user_rag_upload_tool = AgentTool("user_rag_download", tool, openai_description)


