from fastapi import APIRouter, Depends, Query
from core.database import get_session
from sqlmodel import Session
from models.users import User
from schemas.games import GamesReturn, GamesCreate, GamesPatch
from core.security import require_admin
from services.game_service import GameService

router = APIRouter(prefix="/games", tags=["Rachas"])

@router.get("/", response_model=list[GamesReturn])
async def list_games(
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros"),
    session: Session = Depends(get_session)
):
    game_service = GameService(session)
    return game_service.list_games(skip=skip, limit=limit)

@router.get("/{games_id}", response_model=GamesReturn)
async def list_games_by_id(games_id: int, session: Session = Depends(get_session)):
    game_service = GameService(session)
    return game_service.get_game_by_id(games_id)

@router.patch("/{games_id}", response_model=GamesPatch)
async def patch_games_data(
    games_id: int, 
    games_patch: GamesPatch, 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    game_service = GameService(session)
    return game_service.patch_game(games_id, games_patch)

@router.post("/", response_model=GamesReturn)
async def create_game(
    games: GamesCreate, 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    game_service = GameService(session)
    return game_service.create_game(games)