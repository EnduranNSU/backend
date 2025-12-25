from .agent_tool import AgentTool
from agent.utils import exercise_rag

async def tool(query: str, exercise_name: str, info_category:str):
    return await exercise_rag(query, [exercise_name, info_category])
    



openai_description = {
    "type": "function",
    "function": {
            "name": "exrcise_rag_get",
            "description": ("Эндпоинт для RAG по базе знаний об упражнениях",
                            "ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ, когда пользователю нужен совет по технике, ограничениям, альтернативам, типичным ошибкам и так далее связанными с упражнениями."),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Запрос для РАГа"
                    },
                    "exercise_name": {
                        "type": "string",
                        "enum": ["Тяга штанги в наклоне", "Приседания со штангой", "Жим лёжа",
                                    "Болгарский сплит-присед", "Становая тяга", "Ягодичный мост",
                                    "Подъём ног с наклоном корпуса", "Тяга верхнего блока к груди", "Выпады вперёд / назад",
                                    "Подъём ног лёжа", "Горизонтальная тяга в блоке", "Тяга гантели одной рукой",
                                    "Планка", "Подтягивания", "Румынская становая тяга",
                                    "Русские скручивания", "Боковая планка"],
                        "description": "Название упражнения"
                    },
                    "info_category": {
                        "type": "string",
                        "enum": ["technique", "limitations", "alternatives", "mistakes", "muscles"],
                        "description": "Категория информации"
                    }
                },
                "required": ["query", "exercise_name", "info_category"]
            }
    }
}


exercise_rag_get_tool = AgentTool("exercise_rag_get", tool, openai_description)


