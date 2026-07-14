from fastapi import HTTPException, status
from sqlmodel import Session, select
from models.review import Reviews
from schemas.review import ReviewsPosCreate, ReviewsPreCreate
from datetime import datetime
import logging
from models.users import User
import pytz
from tools.muscles import muscles

class ReviewsRepository:
    def __init__(self, session: Session):
        self.session = session
        
        # Definindo o fuso horário de Fortaleza (Ceará)
        self.fuse_ce = pytz.timezone('America/Fortaleza')

        # Pegando a data e hora atual no fuso horário do Ceará
        self.date_today = datetime.now(self.fuse_ce).strftime("%d/%m/%Y")
        self.time_now = datetime.now(self.fuse_ce).strftime("%d/%m/%Y %H:%M:%S")
        
    @property
    def session(self):
        return self.__session
    
    @session.setter
    def session(self, session):
        if not isinstance(session, Session):
            raise TypeError("Session deve ser do tipo Session(sqlmodel)")
        self.__session = session

    def get_all_reviews(self, type: str, user_id: int) -> list[Reviews]:
        if type != "pre" and type != "pos":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Tipo de avaliação inválido")
        
        user_in_db = self.session.get(User, user_id)
        if not user_in_db:
            self.not_found()

        reviews_in_db = self.session.exec(select(Reviews).where(Reviews.user_id == user_in_db.id).limit(10))
        return reviews_in_db

    def create_pre_review(self, review: ReviewsPreCreate, user_id: int):
        try:
            user_in_db = self.session.get(User, user_id)
            if not user_in_db:
                self.not_found()

            # Verifica se já existe uma avaliação para o usuário na data atual
            exist_review = self.session.exec(
                select(Reviews).
                where(Reviews.user_id == user_in_db.id, 
                      Reviews.send_date == self.date_today, 
                      Reviews.type == review.type)
            ).first()
            
            # Se já existir, retorna um erro
            if exist_review:
                logging.error(f"{self.date_today} | {self.time_now}: Avaliação já existe para o usuário {user_in_db.username} na data {self.date_today} do tipo: {review.type}")
                return {"detail": f"Avaliação do tipo '{review.type}' já existe para o usuário na data atual"}
            
            review_db = Reviews(**review.model_dump(), send_date=self.date_today, user_id=user_in_db.id)
            
            self.session.add(review_db)
            self.session.commit()
            self.session.refresh(review_db)
            
            return True
        except Exception as e:
            logging.error(f"{datetime.now()}: Erro ao criar avaliação {e}")
            return {"detail": str(e)}
    
    def create_pos_review(self, review: ReviewsPosCreate, user_id: int):
        try:
            if review.workout != "" and review.severe_pain and review.severe_pain not in muscles:
                return {"detail": "Escolha um local de dor a partir das opções da lista"}
            
            user_in_db = self.session.get(User, user_id)
            if not user_in_db:
                self.not_found()
            
            exist_review = self.session.exec(
                select(Reviews).
                where(Reviews.user_id == user_in_db.id, 
                      Reviews.send_date == self.date_today, 
                      Reviews.type == review.type)
            ).first()
            
            # Se já existir, retorna um erro
            if exist_review:
                logging.error(f"{self.date_today} | {self.time_now}: Avaliação já existe para o usuário {user_in_db.username} na data {self.date_today} do tipo: {review.type}")
                return {"detail": f"Avaliação do tipo '{review.type}' já existe para o usuário na data atual"}
            
            review_db = Reviews(**review.model_dump(), send_date=self.date_today, user_id=user_in_db.id)
            
            self.session.add(review_db)
            self.session.commit()
            self.session.refresh(review_db)

            return True
        except Exception as e:
            logging.error(f"{datetime.now()}: Erro ao criar avaliação {e}")
            return {"detail": str(e)}
    
    def create(self, review: Reviews):
        try:
            self.session.add(review)
            self.session.commit()
            self.session.refresh(review)
            return True
        except Exception as e:
            logging.error(f"{datetime.now()}: Erro ao criar avaliação {e}")
            return {"detail": str(e)}
    
    def not_found(self):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
