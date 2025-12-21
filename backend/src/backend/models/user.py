from pydantic import BaseModel
from pydantic import ConfigDict

class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserAuth(UserBase):
    id: int
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
