from sqlmodel import SQLModel, Field

class WorkoutsBase(SQLModel):
    name: str
    desc: str
    duration: str
    category: str
    premium: bool

class WorkoutsCreate(SQLModel):
    name: str
    desc: str | None = None
    duration: str
    category: str
    
class WorkoutReturn(WorkoutsBase):
    pass

class WorkoutUpdate(SQLModel):
    name: str | None = None
    desc: str | None = None
    duration: str | None = None
    category: str | None = None
    premium: bool | None = None
