from sqlmodel import SQLModel, Field
from sqlalchemy import Index
from typing import Optional

class DailyJournal(SQLModel, table=True):
    __tablename__ = "daily_journals"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    date: str = Field(index=True)  # YYYY-MM-DD
    
    # Recuperação
    sleep_hours: float
    water_liters: float
    stretched: bool
    mobility: bool
    
    # Atividade Física
    trained_basketball: bool
    gym: bool
    cardio: bool
    
    # Estado Físico
    energy: int  # 1-10
    muscle_pain: int  # 1-10
    
    # Estado Mental
    motivation: int  # 1-10
    confidence: int  # 1-10
    
    # Observações
    notes: Optional[str] = Field(default=None)


class Competition(SQLModel, table=True):
    __tablename__ = "competitions"
    __table_args__ = (Index("ix_competitions_user_id_name", "user_id", "name", unique=True),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str
    season: Optional[str] = Field(default=None)
    active: bool = Field(default=True)


class GameStats(SQLModel, table=True):
    __tablename__ = "game_stats"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    competition_id: Optional[int] = Field(default=None, foreign_key="competitions.id", index=True)
    date: str = Field(index=True)  # YYYY-MM-DD
    opponent: str
    result: str  # Vitória / Derrota
    
    # Ofensivo
    points: int
    ft_made: int
    ft_attempted: Optional[int] = Field(default=None)
    fg2_made: int
    fg2_attempted: Optional[int] = Field(default=None)
    fg3_made: int
    fg3_attempted: Optional[int] = Field(default=None)
    
    # Criação de Jogadas
    assists: int
    turnovers: int
    
    # Defesa
    offensive_rebounds: int
    defensive_rebounds: int
    steals: int
    blocks: int
    
    # Faltas
    fouls_committed: int
    fouls_drawn: int


class Goal(SQLModel, table=True):
    __tablename__ = "goals"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    name: str
    goal_type: str  # habit / performance / custom
    metric: str  # e.g., water_liters, sleep_hours, points, assists, etc.
    target_value: float
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    completed: bool = Field(default=False)
