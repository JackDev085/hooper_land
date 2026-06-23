from sqlmodel import SQLModel, Relationship, Field
from typing import Optional, List
from models.photos import Photos
from models.games_schedules import GamesSchedules

class Games(SQLModel, table=True):
    __tablename__="games"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    maps_link: Optional[str] = None
    created_at: str | None = Field(default= None)
    updated_at: str | None = Field(default= None)
    photos: list["Photos"] = Relationship(back_populates="games")
    schedules: list["GamesSchedules"] = Relationship(back_populates="games")
