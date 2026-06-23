from sqlmodel import SQLModel, Field, Relationship
from models.exercises import Exercises
from schemas.workouts import WorkoutsBase

class Workouts(WorkoutsBase, table=True):
    __tablename__ = "workouts"
    id: int | None = Field(default=None, primary_key=True)
    
    name: str
    desc: str
    duration: str
    category: str
    slug: str |None = Field(index=True)
    created_at: str | None = Field(default=None)
    updated_at: str | None= Field(default=None)
    
    exercises: list[Exercises] = Relationship(back_populates="workouts", cascade_delete=True)
    premium: bool | None = Field(default=False)