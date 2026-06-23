from sqlmodel import Session, select
from models.users import User
from schemas.users import UserUpdate
from datetime import datetime
import logging

class UserRepository:
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

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.exec(select(User).where(User.username == username)).first()
    
    def get_user_by_email(self, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)
        
    def create_user(self, new_user: User) -> User:
        try:
            self.session.add(new_user)
            self.session.commit()
            self.session.refresh(new_user)
            return new_user
        except Exception as e:
            self.session.rollback()
            logging.error(f"{datetime.now()}: Erro na criação do usuário {new_user.username}, Erro({e})")
            raise e

    def update_user(self, db_user: User, user_update: UserUpdate) -> User:
        if user_update.name is not None:
            db_user.name = user_update.name
        if user_update.description is not None:
            db_user.description = user_update.description
        if user_update.instagram is not None:
            db_user.instagram = user_update.instagram
        
        db_user.updated_at = str(datetime.now())
        try:
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        except Exception as e:
            self.session.rollback()
            logging.error(f"{datetime.now()}: Erro ao atualizar o usuário {db_user.username}, Erro({e})")
            raise e

    def save(self, user: User) -> User:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            self.session.rollback()
            raise e

    def get_ranking(self, limit: int = 10) -> list[User]:
        statement = select(User).where(User.streak_count > 0).order_by(User.streak_count.desc()).limit(limit)
        return self.session.exec(statement).all()

    def get_all_users(self) -> list[User]:
        statement = select(User).order_by(User.name)
        return self.session.exec(statement).all()