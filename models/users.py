from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True,unique=True)
    email: str | None = Field(default=None, unique=True)
    name: str
    disabled: bool | None = Field(default=None)
    role: str = Field(default="user")  # "user" | "admin"
    instagram: str | None = Field(default=None)
    description: str | None = Field(default=None)
    streak_count: int = Field(default=0)
    last_workout_at: str | None = Field(default=None)
    created_at: str|None = Field(default=None)
    updated_at: str|None= Field(default=None)
    premium: bool | None = Field(default=False)
    password_hash: str

class WorkoutLog(SQLModel, table=True):
    __tablename__ = "workout_logs"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    workout_id: int = Field(foreign_key="workouts.id")
    completed_at: datetime = Field(default_factory=datetime.now)
