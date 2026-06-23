from sqlmodel import SQLModel, Field
from datetime import date, datetime

class Attendance(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    games_id: int = Field(foreign_key="games.id")
    date: date  # date of the games the user confirmed for
    created_at: str | None = Field(default= None)