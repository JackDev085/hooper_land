from fastapi import HTTPException, status
from sqlmodel import Session
from models.photos import Photos
from schemas.photos import PhotoCreateForGame
from repositories.games_repository import GamesRepository
from repositories.photos_repository import PhotosRepository

class GamePhotosService:
    def __init__(self, session: Session):
        self.session = session
        self.games_repository = GamesRepository(session)
        self.photos_repository = PhotosRepository(session)

    def list_photos_by_game_id(self, games_id: int) -> list[Photos]:
        game = self.games_repository.get_game_by_id(games_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum games encontrado com esse id"
            )
        
        photos_game = game.photos
        if len(photos_game) < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma foto encontrada para esse games"
            )
        return photos_game

    def create_photo_list_for_a_game(self, games_id: int, photo_game: PhotoCreateForGame, uploader_id: int) -> Photos:
        game = self.games_repository.get_game_raw(games_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum games encontrado com esse id"
            )
        
        try:
            photo_obj = Photos(**photo_game.model_dump())
            photo_obj.games_id = game.id
            photo_obj.uploaded_by_id = uploader_id
            return self.photos_repository.create_photo(photo_obj)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao adicionar foto ao game"
            ) from e
