from fastapi import status, Depends, APIRouter, Query
from core.database import get_session
from sqlmodel import Session
from models.users import User
from models.workouts import Workouts
from schemas.workouts import WorkoutReturn, WorkoutsCreate, WorkoutUpdate
from core.security import get_current_user, require_admin
from services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.get("/", response_model=list[Workouts])
async def list_workouts(
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros"),
    session: Session = Depends(get_session)
):
    workout_service = WorkoutService(session)
    return workout_service.list_workouts(skip=skip, limit=limit)
    
@router.post("/", response_model=Workouts)
async def create_workout(
    workout: WorkoutsCreate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    workout_service = WorkoutService(session)
    return workout_service.create_workout(workout)

@router.get("/{workout_id}", response_model=Workouts)
async def get_workout_by_id(
    workout_id: int,
    session: Session = Depends(get_session)
):
    workout_service = WorkoutService(session)
    return workout_service.get_workout_by_id(workout_id)

@router.put("/{workout_id}", response_model=WorkoutReturn)
async def update_workout(
    workout_id: int,
    workout_updated: WorkoutUpdate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    workout_service = WorkoutService(session)
    return workout_service.update_workout(workout_id, workout_updated)
        
@router.delete("/{workout_id}")
async def delete_workout_by_id(
    workout_id: int,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    workout_service = WorkoutService(session)
    return workout_service.delete_workout_by_id(workout_id)

@router.post("/{workout_id}/complete")
async def complete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    workout_service = WorkoutService(session)
    return workout_service.complete_workout(workout_id, current_user)