from sqlmodel import SQLModel, Field

class ReviewsBase(SQLModel):
    type: str = Field(..., description="Tipo de avaliação: 'pre' ou 'pos'")

class ReviewsPreCreate(ReviewsBase):
    """Modelo para avaliação do usuário"""
    type: str = Field(default="pre")
    sleep: int = Field(..., ge=1, le=5)
    food: int = Field(..., ge=1, le=5)
    pain: int = Field(..., ge=1, le=5)
    
class ReviewsPosCreate(ReviewsBase):
    """Modelo para avaliação pós treino do usuário"""
    type: str = Field(default="pos")
    workout: str = Field(..., description="Treino realizado pelo usuário")
    fadigue: int = Field(..., ge=1, le=5)
    effort: int = Field(..., ge=1, le=5)
    pain: int = Field(..., ge=1, le=5, description="Nível da dor aguda do atleta")
    severe_pain: str | None = Field(default=None, description="Local da dor agúda")

class ReviewsReturnPos(SQLModel):
    """Modelo de resposta para avaliação"""
    type: str
    workout: str | None = None
    fadigue: int | None = None
    effort: int | None = None
    pain: int | None = None
    severe_pain: str | None = None
    send_date: str | None = None

class ReviewsReturnPre(SQLModel):
    """Modelo de resposta para avaliação"""
    type: str
    sleep: int | None = None
    food: int | None = None
    pain: int | None = None
    send_date: str | None = None
