from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from models.games import Games
from schemas.games import GamesCreate
from datetime import datetime

class GamesRepository:
    def __init__(self, session: Session):
        self.session = session

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, session):
        if not isinstance(session, Session):
            raise TypeError("Session deve ser do tipo Session(sqlmodel)")
        self.__session = session

    def get_all_games(self, skip: int = 0, limit: int = 50) -> list[Games]:
        return self.session.exec(
            select(Games).offset(skip).limit(limit)
        ).all()

    def get_game_by_id(self, games_id: int) -> Games | None:
        return self.session.exec(
            select(Games)
            .where(Games.id == games_id)
            .options(selectinload(Games.photos), selectinload(Games.schedules))
        ).first()

    def get_game_raw(self, games_id: int) -> Games | None:
        return self.session.get(Games, games_id)

    def create_game(self, games_data: GamesCreate) -> Games:
        try:
            new_game = Games(**games_data.model_dump())
            new_game.created_at = str(datetime.now())
            self.session.add(new_game)
            self.session.commit()
            self.session.refresh(new_game)
            return new_game
        except Exception as e:
            self.session.rollback()
            raise e

    def save(self, game: Games) -> Games:
        try:
            self.session.add(game)
            self.session.commit()
            self.session.refresh(game)
            return game
        except Exception as e:
            self.session.rollback()
            raise e
