from pydantic import BaseModel
from pydantic import ConfigDict

class ExerciseBase(BaseModel):
    title: str
    tags: list[str]
    hrefs: list[str]

class ExerciseRead(ExerciseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ExerciseReadVerbose(ExerciseRead):
    id: int
    description: str

    model_config = ConfigDict(from_attributes=True)

class ExerciseCreate(ExerciseBase):
    description: str
