from pydantic import BaseModel
from ..routers.exercise import ExerciseRead


class SetBase(BaseModel):
    weight: int
    repetitions: int
    rest_duration: int

class SetRead(BaseModel):
    id: int
    weight: int
    repetitions: int
    rest_duration: int



class PerfomableExerciseBase(BaseModel):
    sets: list[SetBase]

class PerfomableExerciseRead(PerfomableExerciseBase):
    exercise: ExerciseRead

class PerfomableExerciseCreate(PerfomableExerciseBase):
    exercise_id: int



class TrainingBase(BaseModel):
    title: str

class TrainingRead(TrainingBase):
    perfomable_exercises: list[PerfomableExerciseRead]

class TrainingCreate(TrainingBase):
    perfomable_exercises: list[PerfomableExerciseCreate]



class PlannedTrainningBase(BaseModel):
    weekdays: list[str]

class PlannedTrainningCreate(PlannedTrainningBase):
    training: TrainingCreate

class PlannedTrainingCreateUser(PlannedTrainningCreate):
    user_id: int

class PlannedTrainingRead(PlannedTrainningBase):
    id: int
    user_id: int
    training: TrainingRead



class UserPerformedTrainingBase(BaseModel):
    date: str

class UserPerformedTrainingCreate(UserPerformedTrainingBase):
    training: TrainingCreate

class UserPerformedTrainingCreateUser(UserPerformedTrainingCreate):
    user_id: int

class UserPerformedTrainingRead(UserPerformedTrainingBase):
    id: int
    user_id: int
    training: TrainingRead
