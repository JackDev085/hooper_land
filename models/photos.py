from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Photos(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    games_id: int | None = Field(default=None, foreign_key="games.id")
    url: str
    uploaded_by_id: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    games: "Games"= Relationship(back_populates="photos")
