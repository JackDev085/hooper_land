from sqlmodel import SQLModel, Relationship, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from schemas.photos import PhotoReturn
from schemas.games_schedules import GamesScheduleReturn
class GamesCreate(SQLModel):
    title: str
    description: str
    address: str
    city: str
    state: str
    country: str
    maps_link: str
    """photos: Optional[List["Photos"]] = Relationship(back_populates="games")
    schedules: Optional[List["GamesSchedule"]] = Relationship(back_populates="games")"""
    
class GamesReturn(SQLModel):
    id: int
    title: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    maps_link: Optional[str] = None
    created_at: str | None = Field(default= None)
    photos: list[PhotoReturn] = []
    schedules: list[GamesScheduleReturn] = []  
    
class GamesPatch(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    maps_link: Optional[str] = None



