import json
import re

from fastapi import APIRouter
from pydantic import BaseModel

from agent.agent_backend import Agent
from agent.agent_backend.tools import tools
from agent.utils import exercise
from agent.agent_backend.prompts import user_inquire_system_prompt, create_training_prompt, exercise_prompt

router = APIRouter(prefix="/agent", tags=['agent'])
agent = Agent(tools)

_TRAINING_RE = re.compile(r'<TRAINING_JSON>\s*(.*?)\s*</TRAINING_JSON>', re.DOTALL)


def _extract_training(content: str) -> tuple[str, dict | None]:
    """Return (clean_text, training_dict_or_None)."""
    m = _TRAINING_RE.search(content)
    if not m:
        return content, None
    try:
        training = json.loads(m.group(1))
    except (json.JSONDecodeError, ValueError):
        return content, None
    clean = _TRAINING_RE.sub('', content).strip()
    return clean, training


class ExerciseInquiry(BaseModel):
    message: str
    user_token: str
    user_id: int
    exercise_id: int
    chat_id: str

@router.post("/exercise")
async def exercise_endpoint(inquiry: ExerciseInquiry):
    res = (await exercise(exercise_id=inquiry.exercise_id, token=inquiry.user_token)).json()
    result = await agent.ainvoke(inquiry.message, inquiry.chat_id, inquiry.user_id, inquiry.user_token,
                                 exercise_prompt.format(exercise_title=res['title'], exercise_description=res['description']))
    return result[-1]['content']


class TellAboutInquiry(BaseModel):
    message: str
    chat_id: str
    user_id: int
    user_token: str

@router.post("/tell_about")
async def tell_about_endpoint(inquiry: TellAboutInquiry):
    result = await agent.ainvoke(inquiry.message, inquiry.chat_id, inquiry.user_id, inquiry.user_token,
                                 user_inquire_system_prompt)
    return result[-1]['content']


class PrepareTrainningInquiry(BaseModel):
    message: str
    user_id: int
    chat_id: str
    user_token: str

@router.post("/prepare_trainning")
async def prepare_trainning(inquiry: PrepareTrainningInquiry):
    result = await agent.ainvoke(inquiry.message, inquiry.chat_id, inquiry.user_id, inquiry.user_token,
                                 create_training_prompt)
    content = result[-1]['content']
    text, training = _extract_training(content)
    return {"text": text, "training": training}
