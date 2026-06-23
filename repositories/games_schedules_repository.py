from sqlmodel import Session, select
from models.games_schedules import GamesSchedules

class GamesSchedulesRepository:
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

    def get_schedules_by_game(self, games_id: int) -> list[GamesSchedules]:
        return self.session.exec(
            select(GamesSchedules).where(GamesSchedules.games_id == games_id)
        ).all()

    def save_all(self, schedules: list[GamesSchedules]) -> list[GamesSchedules]:
        try:
            for s in schedules:
                self.session.add(s)
            self.session.commit()
            for s in schedules:
                self.session.refresh(s)
            return schedules
        except Exception as e:
            self.session.rollback()
            raise e
