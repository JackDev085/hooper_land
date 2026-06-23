from sqlmodel import SQLModel, Field, Relationship

class Exercises(SQLModel, table=True):
    __tablename__ = "exercises"
    id: int | None = Field(default=None,primary_key=True)
    
    name: str
    desc: str | None = None
    reps: str
    link_video: str
    
    created_at: str | None = None
    updated_at: str | None = None
    
    workouts_id: int = Field(foreign_key="workouts.id")
    workouts: "Workouts" = Relationship(back_populates="exercises")

