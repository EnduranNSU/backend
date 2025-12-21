from pydantic import BaseModel
from pydantic import ConfigDict

class MeasurementBase(BaseModel):
    type: str
    value: int
    date: str

class MeasurementRead(MeasurementBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MeasurementCreate(MeasurementBase):
    user_id: int
    model_config = ConfigDict(from_attributes=True)
