from fastapi import APIRouter, Depends
from core.database import get_session
from sqlmodel import Session
from models.photos import Photos
from models.users import User
from core.security import require_admin
from typing import List
from schemas.photos import PhotoCreateForGame
from services.game_photos_service import GamePhotosService

router = APIRouter(prefix="/games/photos", tags=["Fotos das quadras"])

@router.get("/{games_id}", response_model=List[Photos])
async def list_photos_by_game_id(games_id: int, session: Session = Depends(get_session)):
    game_photos_service = GamePhotosService(session)
    return game_photos_service.list_photos_by_game_id(games_id)

@router.post("/{games_id}", response_model=Photos)
async def create_photo_list_for_a_game(
    games_id: int, 
    photo_game: PhotoCreateForGame, 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    game_photos_service = GamePhotosService(session)
    return game_photos_service.create_photo_list_for_a_game(games_id, photo_game, admin.id)