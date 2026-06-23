from sqlmodel import Session, select
from models.workouts import Workouts
from schemas.workouts import WorkoutsCreate, WorkoutUpdate
from datetime import datetime

class WorkoutRepository:
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

    def get_all_workouts(self, skip: int = 0, limit: int = 50) -> list[Workouts]:
        return self.session.exec(select(Workouts).offset(skip).limit(limit)).all()
    
    def get_workout_by_id(self, workout_id: int) -> Workouts | None:
        return self.session.get(Workouts, workout_id)
    
    def create_workout(self, workout_data: WorkoutsCreate) -> Workouts:
        try:
            new_workout = Workouts(**workout_data.model_dump())
            new_workout.created_at = datetime.now()
            new_workout.updated_at = datetime.now()
            new_workout.slug = datetime.now()
            self.session.add(new_workout)
            self.session.commit()
            self.session.refresh(new_workout)
            return new_workout
        except Exception as e:
            self.session.rollback()
            raise e

    def update_workout(self, db_workout: Workouts, workout_updated: WorkoutUpdate) -> Workouts:
        try:
            db_workout.sqlmodel_update(workout_updated.model_dump(exclude_unset=True))
            self.session.add(db_workout)
            self.session.commit()
            self.session.refresh(db_workout)
            return db_workout
        except Exception as e:
            self.session.rollback()
            raise e
        
    def delete_workout(self, db_workout: Workouts) -> None:
        try:
            self.session.delete(db_workout)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e