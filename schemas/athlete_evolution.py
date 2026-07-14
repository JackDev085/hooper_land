from pydantic import BaseModel, Field, model_validator
from typing import Optional

class DailyJournalCreate(BaseModel):
    date: str  # YYYY-MM-DD
    sleep_hours: float = Field(..., ge=0, le=24)
    water_liters: float = Field(..., ge=0)
    stretched: bool
    mobility: bool
    trained_basketball: bool
    gym: bool
    cardio: bool
    energy: int = Field(..., ge=1, le=10)
    muscle_pain: int = Field(..., ge=1, le=10)
    motivation: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None

class GameStatsCreate(BaseModel):
    competition_id: Optional[int] = None
    date: str  # YYYY-MM-DD
    opponent: str
    result: str  # Vitória / Derrota
    points: int = Field(..., ge=0)
    ft_made: int = Field(..., ge=0)
    ft_attempted: Optional[int] = Field(default=None, ge=0)
    fg2_made: int = Field(..., ge=0)
    fg2_attempted: Optional[int] = Field(default=None, ge=0)
    fg3_made: int = Field(..., ge=0)
    fg3_attempted: Optional[int] = Field(default=None, ge=0)
    assists: int = Field(..., ge=0)
    turnovers: int = Field(..., ge=0)
    offensive_rebounds: int = Field(..., ge=0)
    defensive_rebounds: int = Field(..., ge=0)
    steals: int = Field(..., ge=0)
    blocks: int = Field(..., ge=0)
    fouls_committed: int = Field(..., ge=0)
    fouls_drawn: int = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_made_vs_attempted(self):
        if self.ft_attempted is not None and self.ft_made > self.ft_attempted:
            raise ValueError("ft_made não pode ser maior que ft_attempted.")
        if self.fg2_attempted is not None and self.fg2_made > self.fg2_attempted:
            raise ValueError("fg2_made não pode ser maior que fg2_attempted.")
        if self.fg3_attempted is not None and self.fg3_made > self.fg3_attempted:
            raise ValueError("fg3_made não pode ser maior que fg3_attempted.")
        return self

class CompetitionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    season: Optional[str] = Field(default=None, max_length=50)

class CompetitionOut(BaseModel):
    id: int
    user_id: int
    name: str
    season: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True

class GoalCreate(BaseModel):
    name: str
    goal_type: str  # habit / performance / custom
    metric: str
    target_value: float
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
