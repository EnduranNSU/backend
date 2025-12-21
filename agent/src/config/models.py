import os
from typing import Literal, Union

from pydantic import BaseModel, Field, ValidationError


class GeminiConfig(BaseModel):
    type: Literal["Gemini"]

    model: str
    temperature: float
    max_tokens: int
    API_KEY: str

class Config(BaseModel):
    model: GeminiConfig





