from sqlmodel import SQLModel, Field, Relationship
from models.users import User


class Reviews(SQLModel, table=True):
    __tablename__ = "reviews"
    id: int | None = Field(default=None, primary_key=True)
    sleep: int | None = Field(default=None)
    food: int | None = Field(default=None)
    pain: int | None = Field(default=None)
    workout: str | None = Field(default=None)
    fadigue: int | None = Field(default=None)
    effort: int | None = Field(default=None)
    severe_pain: str | None = Field(default=None)
    send_date: str = Field(..., description="Data da avaliação no formato dd/mm/yyyy")
    user_id: int = Field(foreign_key="users.id")
    type: str = Field(..., description="Tipo de avaliação: 'pre' ou 'pos'")
    
    user_obj: User | None = Relationship(back_populates="reviews")
