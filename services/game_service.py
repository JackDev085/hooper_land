from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime
from models.games import Games
from schemas.games import GamesCreate, GamesPatch
from repositories.games_repository import GamesRepository

class GameService:
    def __init__(self, session: Session):
        self.session = session
        self.games_repository = GamesRepository(session)

    def list_games(self, skip: int = 0, limit: int = 50) -> list[Games]:
        return self.games_repository.get_all_games(skip=skip, limit=limit)

    def get_game_by_id(self, games_id: int) -> Games:
        game = self.games_repository.get_game_by_id(games_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum game encontrado"
            )
        return game

    def patch_game(self, games_id: int, games_patch: GamesPatch) -> Games:
        game = self.games_repository.get_game_raw(games_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum game encontrado"
            )

        try:
            games_data = games_patch.model_dump(exclude_unset=True)
            game.sqlmodel_update(games_data)
            game.updated_at = str(datetime.now())
            return self.games_repository.save(game)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar game"
            ) from e

    def create_game(self, games_data: GamesCreate) -> Games:
        try:
            return self.games_repository.create_game(games_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar game"
            ) from e
