from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from typing import Optional

class PhotoCreate(SQLModel):
    games_id: Optional[int] = Field(default=None)
    url: str
    uploaded_by_id: Optional[int] = Field(default=None)
    created_at: str | None = Field(default= None)


class PhotoCreateForGame(SQLModel):
    url: str

class PhotoReturn(SQLModel):
    id: int
    games_id: Optional[int] = None
    url: str
    uploaded_by_id: Optional[int] = None
    created_at: datetime
