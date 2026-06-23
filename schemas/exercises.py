from sqlmodel import SQLModel, Field

class ExercisesBase(SQLModel):
    name: str
    desc: str | None = None
    reps: str
    link_video: str

class ExercisesCreate(ExercisesBase):
    pass

class ExercisesReturn(ExercisesBase):
    pass

class ExercisesUpdate(ExercisesBase):
    pass