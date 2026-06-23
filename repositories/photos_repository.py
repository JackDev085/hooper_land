from sqlmodel import Session, select
from models.photos import Photos

class PhotosRepository:
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

    def get_photos_by_game(self, games_id: int) -> list[Photos]:
        return self.session.exec(
            select(Photos).where(Photos.games_id == games_id)
        ).all()

    def create_photo(self, photo: Photos) -> Photos:
        try:
            self.session.add(photo)
            self.session.commit()
            self.session.refresh(photo)
            return photo
        except Exception as e:
            self.session.rollback()
            raise e
