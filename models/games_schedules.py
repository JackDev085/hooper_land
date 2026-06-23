
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.games import Games

class GamesSchedules(SQLModel, table=True):
    __tablename__ = "gamesschedules"
    id: int | None = Field(default=None, primary_key=True)
    games_id: int = Field(foreign_key="games.id")
    weekday: int = Field(gt=0) # 0=Monday .. 6=Sunday
    start_time: str
    end_time: str
    games: "Games"= Relationship(back_populates="schedules")

    