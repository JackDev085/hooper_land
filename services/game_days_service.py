from fastapi import HTTPException, status
from sqlmodel import Session
from models.games_schedules import GamesSchedules
from schemas.games_schedules import GamesScheduleCreate
from repositories.games_repository import GamesRepository
from repositories.games_schedules_repository import GamesSchedulesRepository

class GameDaysService:
    def __init__(self, session: Session):
        self.session = session
        self.games_repository = GamesRepository(session)
        self.schedules_repository = GamesSchedulesRepository(session)

    def list_days_and_times_games(self, games_id: int) -> list[GamesSchedules]:
        game = self.games_repository.get_game_by_id(games_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum game encontrado com esse id"
            )
        
        time_games = game.schedules
        if len(time_games) < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum horário encontrado para esse game"
            )
        return time_games

    def create_times_game(self, games_id: int, times_game: list[GamesScheduleCreate]) -> list[GamesSchedules]:
        game = self.games_repository.get_game_raw(games_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum game encontrado com esse id"
            )

        try:
            new_time_game = []
            for time_game in times_game:
                time = GamesSchedules(**time_game.model_dump())
                time.games_id = game.id
                new_time_game.append(time)
                
            game.schedules = new_time_game
            self.games_repository.save(game)
            return game.schedules
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao adicionar horários de game"
            ) from e
