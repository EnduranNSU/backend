from .agent_tool import AgentTool
from agent.utils import exercise_rag

async def tool(query: str):
    return await exercise_rag(query)
    

openai_description = {
    "type": "function",
    "function": {
            "name": "mock_tool",
            "description": "Эндпоинт для RAG по базе знаний об упражнениях. ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, когда пользователю нужен совет по технике, ограничениям, альтернативам, типичным ошибкам и так далее связанными с упражнениями.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Запрос для РАГа"
                    }
                }
            }
    }
}


mock_tool = AgentTool("mock_tool", tool, openai_description)


