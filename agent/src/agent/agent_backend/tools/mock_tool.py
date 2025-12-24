from .agent_tool import AgentTool

async def tool():
    print("MOCK TOOL IS CALLED")

openai_description = {
    "type": "function",
    "function": {
            "name": "mock_tool",
            "description": "Выводит важное сообщение для пользователя",
            "parameters": {
                "type": "object",
                "properties": {}
            }
    }
}


mock_tool = AgentTool("mock_tool", tool, openai_description)

