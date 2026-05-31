from .agent_tool import AgentTool
from agent.utils import user_save

async def tool(info: str, user_id: int):
    return await user_save(info, user_id)
    

openai_description = {
    "type": "function",
    "function": {
            "name": "user_rag_upload",
            "description": (
                "Сохранить информацию о пользователе в RAG. "
                "Вызывай после того, как пользователь сообщил свои цели, уровень или ограничения."
            ),
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


user_rag_upload_tool = AgentTool("user_rag_upload", tool, openai_description)


