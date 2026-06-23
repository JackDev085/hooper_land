from sqlmodel import SQLModel, Field, Relationship


class GamesScheduleCreate(SQLModel):
    weekday: int  # 0=Monday .. 6=Sunday
    start_time: str
    end_time: str
    
class GamesScheduleReturn(SQLModel):
    id: int
    weekday: int  # 0=Monday .. 6=Sunday
    start_time: str
    end_time: str
