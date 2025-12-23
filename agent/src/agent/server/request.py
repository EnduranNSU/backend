from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

from langchain_core.prompts import PromptTemplate

from utils.model import get_model

request_router = APIRouter()

class MessageRequest(BaseModel):
    request_id: str
    request_text: str


async def basic(req: MessageRequest):
    model = get_model()

    template = PromptTemplate.from_template("" \
    "You are helpful assistant who is really good at sport and fitness." \
    "The user has such request in his message: {request_text}")
    req.request_text = template.format(request_text=req.request_text)

    async for part in model.astream(req.request_text):
        yield part.content


@request_router.post("/request")
async def stream_response(req: MessageRequest):
    return StreamingResponse(
        basic(req),
        media_type="text/plain"
    )
