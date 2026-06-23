import pytest
from fastapi import HTTPException
from sqlmodel import Session
from schemas.games import GamesCreate, GamesPatch
from schemas.games_schedules import GamesScheduleCreate
from schemas.photos import PhotoCreateForGame
from services.game_service import GameService
from services.game_days_service import GameDaysService
from services.game_photos_service import GamePhotosService
from models.users import User
from models.games import Games

def test_game_crud(session: Session):
    game_service = GameService(session)
    
    # 1. Create Game
    game_data = GamesCreate(
        title="Racha da Quarta",
        description="Futebol society",
        address="Av. Santos Dumont",
        city="Fortaleza",
        state="CE",
        country="Brasil",
        maps_link="http://maps.google.com"
    )
    new_game = game_service.create_game(game_data)
    assert new_game.id is not None
    assert new_game.title == "Racha da Quarta"
    
    # 2. Get Game
    game = game_service.get_game_by_id(new_game.id)
    assert game.title == "Racha da Quarta"
    
    # 3. Patch Game
    patch_data = GamesPatch(title="Racha de Futsal da Quarta")
    patched_game = game_service.patch_game(new_game.id, patch_data)
    assert patched_game.title == "Racha de Futsal da Quarta"
    
    # 4. List Games
    games = game_service.list_games()
    assert len(games) == 1

def test_game_schedules(session: Session):
    game_service = GameService(session)
    game_days_service = GameDaysService(session)
    
    # Setup Game
    game_data = GamesCreate(
        title="Racha da Quarta",
        description="Futebol society",
        address="Av. Santos Dumont",
        city="Fortaleza",
        state="CE",
        country="Brasil",
        maps_link="http://maps.google.com"
    )
    game = game_service.create_game(game_data)
    
    # 1. Create Schedules
    schedules_data = [
        GamesScheduleCreate(weekday=3, start_time="19:00", end_time="21:00"),
        GamesScheduleCreate(weekday=5, start_time="18:00", end_time="20:00")
    ]
    schedules = game_days_service.create_times_game(game.id, schedules_data)
    assert len(schedules) == 2
    assert schedules[0].weekday == 3
    
    # 2. List Schedules
    list_schedules = game_days_service.list_days_and_times_games(game.id)
    assert len(list_schedules) == 2

def test_game_photos(session: Session):
    game_service = GameService(session)
    game_photos_service = GamePhotosService(session)
    
    # Setup Game and User
    game_data = GamesCreate(
        title="Racha da Quarta",
        description="Futebol society",
        address="Av. Santos Dumont",
        city="Fortaleza",
        state="CE",
        country="Brasil",
        maps_link="http://maps.google.com"
    )
    game = game_service.create_game(game_data)
    user = User(username="admin", name="Admin", email="admin@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # 1. Create Photo
    photo_data = PhotoCreateForGame(url="http://example.com/photo.jpg")
    photo = game_photos_service.create_photo_list_for_a_game(game.id, photo_data, user.id)
    assert photo.id is not None
    assert photo.url == "http://example.com/photo.jpg"
    assert photo.uploaded_by_id == user.id
    
    # 2. List Photos
    photos = game_photos_service.list_photos_by_game_id(game.id)
    assert len(photos) == 1
    assert photos[0].url == "http://example.com/photo.jpg"
