from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime
from models.exercises import Exercises
from models.workouts import Workouts
from schemas.exercises import ExercisesCreate, ExercisesUpdate
from repositories.exercises_repository import ExercisesRepository

class ExerciseService:
    def __init__(self, session: Session):
        self.session = session
        self.exercises_repository = ExercisesRepository(session)

    def list_exercises_by_workout(self, workout_id: int) -> dict:
        workout = self.exercises_repository.get_workout_with_exercises(workout_id)
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        return {"workout_name": workout.name, "exercises": workout.exercises}

    def create_exercises_for_workout(self, workout_id: int, list_exercises: list[ExercisesCreate]) -> Workouts:
        workout = self.exercises_repository.get_workout_with_exercises(workout_id)
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        
        if len(list_exercises) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lista de exercícios precisa ser maior que 1"
            )
        
        try:
            db_exercises = []
            for item in list_exercises:
                exercise = Exercises(**item.model_dump())
                exercise.created_at = datetime.now()
                exercise.updated_at = datetime.now()
                db_exercises.append(exercise)
                
            workout.exercises.extend(db_exercises)
            return self.exercises_repository.save_workout(workout)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao adicionar exercícios ao treino"
            ) from e

    def create_all_exercises(self, exercises: list[Exercises]) -> bool:
        try:
            for exercise in exercises:
                self.exercises_repository.save_exercise(exercise)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar exercícios"
            ) from e

    def update_exercise(self, exercise_id: int, exercise_updated: ExercisesUpdate) -> Exercises:
        exercise_in_db = self.exercises_repository.get_exercise_by_id(exercise_id)
        if not exercise_in_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercício não encontrado"
            )
            
        try:
            exercise_in_db.sqlmodel_update(exercise_updated.model_dump(exclude_unset=True))
            return self.exercises_repository.save_exercise(exercise_in_db)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar exercício"
            ) from e

    def delete_exercise_by_id(self, exercise_id: int) -> dict:
        exercise_in_db = self.exercises_repository.get_exercise_by_id(exercise_id)
        if not exercise_in_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercício não encontrado"
            )
            
        try:
            self.exercises_repository.delete_exercise(exercise_in_db)
            return {"detail": "Exercício deletado com sucesso"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao deletar exercício"
            ) from e
