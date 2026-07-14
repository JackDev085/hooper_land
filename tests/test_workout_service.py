import pytest
from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import datetime, timezone, timedelta
from schemas.workouts import WorkoutsCreate, WorkoutUpdate
from services.workout_service import WorkoutService
from models.workouts import Workouts
from models.users import User, WorkoutLog

def test_crud_workout(session: Session):
    workout_service = WorkoutService(session)
    
    # 1. Create Workout
    workout_data = WorkoutsCreate(
        name="Treino de Quadríceps",
        desc="Foco em força",
        duration="45 min",
        category="Perna",
        premium=False
    )
    new_workout = workout_service.create_workout(workout_data)
    assert new_workout.id is not None
    assert new_workout.name == "Treino de Quadríceps"
    
    # 2. Get Workout
    workout = workout_service.get_workout_by_id(new_workout.id)
    assert workout.name == "Treino de Quadríceps"
    
    # 3. Update Workout
    update_data = WorkoutUpdate(name="Treino de Perna Completo")
    updated_workout = workout_service.update_workout(new_workout.id, update_data)
    assert updated_workout.name == "Treino de Perna Completo"
    
    # 4. List Workouts
    workouts = workout_service.list_workouts()
    assert len(workouts) == 1
    
    # 5. Delete Workout
    res = workout_service.delete_workout_by_id(new_workout.id)
    assert res["detail"] == "Treino deletado com sucesso"
    
    with pytest.raises(HTTPException) as excinfo:
        workout_service.get_workout_by_id(new_workout.id)
    assert excinfo.value.status_code == 404

def test_complete_workout_first_time(session: Session):
    workout_service = WorkoutService(session)
    
    # Setup User and Workout
    user = User(username="user1", name="User One", email="user1@example.com", password_hash="hash")
    session.add(user)
    
    workout = Workouts(name="Treino A", desc="Treino A desc", duration="60 min", category="A", slug="treino-a")
    session.add(workout)
    session.commit()
    session.refresh(user)
    session.refresh(workout)
    
    # Complete Workout
    res = workout_service.complete_workout(workout.id, user)
    assert res["streak_count"] == 1
    
    # Verify log was created
    logs = session.exec(select(WorkoutLog).where(WorkoutLog.user_id == user.id)).all()
    assert len(logs) == 1
    assert logs[0].workout_id == workout.id

def test_complete_workout_streak_logic(session: Session):
    workout_service = WorkoutService(session)
    
    # Setup User and Workout
    tz_fortaleza = timezone(timedelta(hours=-3))
    today_str = datetime.now(tz_fortaleza).strftime("%Y-%m-%d")
    yesterday_str = (datetime.now(tz_fortaleza) - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # User completed workout yesterday
    user = User(
        username="user1", 
        name="User One", 
        email="user1@example.com", 
        password_hash="hash",
        last_workout_at=yesterday_str,
        streak_count=5
    )
    session.add(user)
    
    workout = Workouts(name="Treino A", desc="Treino A desc", duration="60 min", category="A", slug="treino-a")
    session.add(workout)
    session.commit()
    session.refresh(user)
    session.refresh(workout)
    
    # Complete Workout today -> streak should increment to 6
    res = workout_service.complete_workout(workout.id, user)
    assert res["streak_count"] == 6
    assert res["last_workout_at"] == today_str
    
    # Complete Workout again today -> streak should remain 6
    res2 = workout_service.complete_workout(workout.id, user)
    assert res2["streak_count"] == 6
    assert res2["last_workout_at"] == today_str

def test_complete_workout_neuro_cognition_dynamic_creation(session: Session):
    workout_service = WorkoutService(session)
    user = User(username="usernc", name="User NC", email="usernc@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Workout 999 does not exist in DB yet
    res = workout_service.complete_workout(999, user)
    assert res["streak_count"] == 1
    
    # Verify it was created dynamically
    workout = workout_service.get_workout_by_id(999)
    assert workout is not None
    assert workout.name == "Treino de Tomada de Decisão Cognitiva"
