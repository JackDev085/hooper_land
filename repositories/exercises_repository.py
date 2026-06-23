from sqlmodel import Session
from models.exercises import Exercises
from models.workouts import Workouts
from schemas.exercises import ExercisesCreate, ExercisesUpdate
from datetime import datetime

class ExercisesRepository:
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

    def get_workout_with_exercises(self, workouts_id: int) -> Workouts | None:
        if not isinstance(workouts_id, int):
            raise TypeError("O workouts_id deve ser do tipo inteiro")
        return self.session.get(Workouts, workouts_id)

    def get_exercise_by_id(self, exercise_id: int) -> Exercises | None:
        return self.session.get(Exercises, exercise_id)
    
    def save_workout(self, workout: Workouts) -> Workouts:
        try:
            self.session.add(workout)
            self.session.commit()
            self.session.refresh(workout)
            return workout
        except Exception as e:
            self.session.rollback()
            raise e
            
    def save_exercise(self, exercise: Exercises) -> Exercises:
        try:
            self.session.add(exercise)
            self.session.commit()
            self.session.refresh(exercise)
            return exercise
        except Exception as e:
            self.session.rollback()
            raise e

    def delete_exercise(self, exercise: Exercises) -> None:
        try:
            self.session.delete(exercise)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e