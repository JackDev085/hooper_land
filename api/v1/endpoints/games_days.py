from fastapi import APIRouter, Depends
from core.database import get_session
from sqlmodel import Session
from models.games_schedules import GamesSchedules
from models.users import User
from core.security import require_admin
from typing import List
from schemas.games_schedules import GamesScheduleCreate, GamesScheduleReturn
from services.game_days_service import GameDaysService

router = APIRouter(prefix="/game/days", tags=["Dias de racha"])

@router.get("/{games_id}", response_model=List[GamesSchedules])
async def list_days_and_times_games(games_id: int, session: Session = Depends(get_session)):
    game_days_service = GameDaysService(session)
    return game_days_service.list_days_and_times_games(games_id)

@router.post("/{games_id}", response_model=List[GamesScheduleReturn])
async def create_times_game(
    games_id: int, 
    times_game: List[GamesScheduleCreate], 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    game_days_service = GameDaysService(session)
    return game_days_service.create_times_game(games_id, times_game)