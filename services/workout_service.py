from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone, timedelta
from models.workouts import Workouts
from models.users import User, WorkoutLog
from schemas.workouts import WorkoutsCreate, WorkoutUpdate
from repositories.workout_repository import WorkoutRepository
from repositories.user_repository import UserRepository

class WorkoutService:
    def __init__(self, session: Session):
        self.session = session
        self.workout_repository = WorkoutRepository(session)
        self.user_repository = UserRepository(session)

    def list_workouts(self, skip: int = 0, limit: int = 50) -> list[Workouts]:
        return self.workout_repository.get_all_workouts(skip=skip, limit=limit)

    def create_workout(self, workout_data: WorkoutsCreate) -> Workouts:
        try:
            return self.workout_repository.create_workout(workout_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao adicionar treino no banco de dados"
            ) from e

    def get_workout_by_id(self, workout_id: int) -> Workouts:
        workout = self.workout_repository.get_workout_by_id(workout_id)
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        return workout

    def update_workout(self, workout_id: int, workout_updated: WorkoutUpdate) -> Workouts:
        workout = self.get_workout_by_id(workout_id)
        try:
            return self.workout_repository.update_workout(workout, workout_updated)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar treino"
            ) from e

    def delete_workout_by_id(self, workout_id: int) -> dict:
        workout = self.get_workout_by_id(workout_id)
        try:
            self.workout_repository.delete_workout(workout)
            return {"detail": "Treino deletado com sucesso"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao deletar treino"
            ) from e

    def complete_workout(self, workout_id: int, current_user: User) -> dict:
        workout = self.workout_repository.get_workout_by_id(workout_id)
        if not workout:
            if workout_id == 999:
                workout = Workouts(
                    id=999,
                    name="Treino de Tomada de Decisão Cognitiva",
                    desc="Treinamento neurocognitivo com comandos de voz.",
                    duration="Variável",
                    category="Neurocognitivo",
                    slug="treino-tomada-decisao-cognitiva",
                    premium=True,
                    created_at=str(datetime.now()),
                    updated_at=str(datetime.now())
                )
                self.session.add(workout)
                self.session.commit()
                self.session.refresh(workout)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treino não encontrado!")

        # Registra o log de conclusão
        log = WorkoutLog(user_id=current_user.id, workout_id=workout_id)
        self.session.add(log)

        # Lógica de cálculo do streak baseado em fuso horário de Fortaleza (UTC-3)
        tz_fortaleza = timezone(timedelta(hours=-3))
        today_str = datetime.now(tz_fortaleza).strftime("%Y-%m-%d")
        yesterday_str = (datetime.now(tz_fortaleza) - timedelta(days=1)).strftime("%Y-%m-%d")

        if current_user.last_workout_at == today_str:
            # Já concluiu um treino hoje, mantém a streak atual
            pass
        elif current_user.last_workout_at == yesterday_str:
            # Concluiu ontem, incrementa streak
            current_user.streak_count += 1
            current_user.last_workout_at = today_str
        else:
            # Reseta ou inicia em 1
            current_user.streak_count = 1
            current_user.last_workout_at = today_str

        try:
            self.session.add(current_user)
            self.session.commit()
            self.session.refresh(current_user)
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao registrar conclusão do treino"
            ) from e

        return {
            "message": "Treino concluído com sucesso!",
            "streak_count": current_user.streak_count,
            "last_workout_at": current_user.last_workout_at
        }
