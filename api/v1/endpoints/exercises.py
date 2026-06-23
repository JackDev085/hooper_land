from fastapi import APIRouter, Depends
from core.database import get_session
from models.users import User
from models.exercises import Exercises
from sqlmodel import Session
from core.security import require_admin
from schemas.exercises import ExercisesCreate, ExercisesReturn, ExercisesUpdate
from services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.get("/{workout_id}")
async def list_exercises_by_workout(workout_id: int, session: Session = Depends(get_session)):
    exercise_service = ExerciseService(session)
    return exercise_service.list_exercises_by_workout(workout_id)

@router.post("/")
async def create_exercises_for_workout(
    workout_id: int, 
    exercises: list[ExercisesCreate], 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    exercise_service = ExerciseService(session)
    return exercise_service.create_exercises_for_workout(workout_id, exercises)

@router.post("/all_exercises")
async def create_all_exercises(
    exercises: list[Exercises], 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    exercise_service = ExerciseService(session)
    exercise_service.create_all_exercises(exercises)
    return {"detail": "Exercícios adicionados ao treino"}

@router.put("/{exercises_id}", response_model=ExercisesReturn)
async def update_exercise(
    exercises_id: int, 
    exercise_updated: ExercisesUpdate, 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    exercise_service = ExerciseService(session)
    return exercise_service.update_exercise(exercises_id, exercise_updated)
        
@router.delete("/{exercises_id}")
async def delete_exercise_by_id(
    exercises_id: int, 
    admin: User = Depends(require_admin), 
    session: Session = Depends(get_session)
):
    exercise_service = ExerciseService(session)
    return exercise_service.delete_exercise_by_id(exercises_id)