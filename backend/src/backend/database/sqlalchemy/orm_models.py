from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    hashed_password: Mapped[str]

    measurements: Mapped[List["Measurement"]] = relationship(
        "Measurement",
        cascade="all, delete-orphan"
    )

    performed_trainings: Mapped[List["UserPerformedTraining"]] = relationship(
        "UserPerformedTraining",
        cascade="all, delete-orphan"
    )

    trainings: Mapped[List["PlannedTrainnings"]] = relationship(
        "PlannedTrainnings",
        cascade="all, delete-orphan"
    )


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    type: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)



class Exercise(Base):
    __tablename__ = "exercises"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list  
    )
    hrefs: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list  
    )

class Set(Base):
    __tablename__ = "sets"
    

    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[int] = mapped_column(nullable=True)
    repetitions: Mapped[int] = mapped_column(nullable=True)
    rest_duration: Mapped[int] = mapped_column(nullable=True)

    perfomable_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("perfomable_exercises.id"),
        nullable=False,
        index=True
    )

class PerfomableExercise(Base):
    __tablename__ = "perfomable_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"),
        nullable=False,
    )
    exercise: Mapped["Exercise"] = relationship()
    sets: Mapped[List["Set"]] = relationship(
        cascade="all, delete-orphan"
    )
    training_id: Mapped[int] = mapped_column(
        ForeignKey("trainings.id"),
        nullable=False,
    )


class Training(Base):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    perfomable_exercises: Mapped[List["PerfomableExercise"]] = relationship(
        cascade="all, delete-orphan"
    )


class UserPerformedTraining(Base):
    __tablename__ = "user_performed_trainings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    training_id: Mapped[int] = mapped_column(
        ForeignKey("trainings.id"),
        nullable=False,
        index=True,
        unique=True
    )
    training: Mapped["Training"] = relationship(uselist=False)
    date: Mapped[str] = mapped_column(nullable=False)

class PlannedTrainnings(Base):
    __tablename__ = "planned_trainings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    training_id: Mapped[int] = mapped_column(
        ForeignKey("trainings.id"),
        nullable=False,
        index=True,
        unique=True
    )
    training:Mapped["Training"] = relationship(uselist=False)
    weekdays: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list  
    )
