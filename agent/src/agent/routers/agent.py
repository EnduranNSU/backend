from fastapi import APIRouter
from pydantic import BaseModel

from agent.agent_backend import Agent
from agent.agent_backend.tools import tools
from agent.utils import exercise

router = APIRouter(prefix="/agent", tags=['agent'])
agent = Agent(tools)


class ExerciseInquiry(BaseModel):
    message: str
    user_token: str
    user_id: int
    exercise_id: int
    chat_id: str
@router.post("/exercise")
async def exercise_endpoint(inquiry: ExerciseInquiry):
    res = await exercise(exercise_id=inquiry.exercise_id, token=inquiry.user_token)
    result = await agent.ainvoke(inquiry.message, inquiry.chat_id, f"Ты крутой тренер. Вообще очень круто разбираешься в спорте пользователь хочет разузнать про вот это упражнение. {res.json()['description']}")
    return result[-1].content


# @router.post("/tell_about")
# async def tell_about(inquiry: TellAboutInquiry):

#     await agent.ainvoke(inquiry.message, inquiry.chat_id, )
#     return

# @router.port("/prepare_trainning")
# async def prepare_trainning(inquiry: PrepareTrainningInquiry):

#     await agent.ainvoke(inquiry.message, inquiry.chat_id, )
#     return