import pytest
from fastapi import HTTPException
from sqlmodel import Session
from schemas.exercises import ExercisesCreate, ExercisesUpdate
from services.exercise_service import ExerciseService
from models.workouts import Workouts
from models.exercises import Exercises

def test_exercise_operations(session: Session):
    exercise_service = ExerciseService(session)
    
    # Setup Workout
    workout = Workouts(name="Treino A", desc="Treino A desc", duration="60 min", category="A", slug="treino-a")
    session.add(workout)
    session.commit()
    session.refresh(workout)
    
    # 1. Create Exercises
    exercises_data = [
        ExercisesCreate(name="Flexão", reps="10", link_video="http://example.com/video1", desc="Peito"),
        ExercisesCreate(name="Agachamento", reps="15", link_video="http://example.com/video2", desc="Pernas")
    ]
    
    res = exercise_service.create_exercises_for_workout(workout.id, exercises_data)
    assert len(res.exercises) == 2
    assert res.exercises[0].name == "Flexão"
    
    # 2. List Exercises
    list_res = exercise_service.list_exercises_by_workout(workout.id)
    assert list_res["workout_name"] == "Treino A"
    assert len(list_res["exercises"]) == 2
    
    # 3. Update Exercise
    exercise_id = res.exercises[0].id
    update_data = ExercisesUpdate(name="Flexão Inclinada", reps="12", link_video="http://example.com/video1", desc="Peito")
    updated_exercise = exercise_service.update_exercise(exercise_id, update_data)
    assert updated_exercise.name == "Flexão Inclinada"
    assert updated_exercise.reps == "12"
    
    # 4. Delete Exercise
    del_res = exercise_service.delete_exercise_by_id(exercise_id)
    assert del_res["detail"] == "Exercício deletado com sucesso"
    
    # Verify deletion
    list_res2 = exercise_service.list_exercises_by_workout(workout.id)
    assert len(list_res2["exercises"]) == 1
