import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models.users import User
from core.security import hash_password, create_access_token

def create_test_user(session: Session, username: str, is_premium: bool = True):
    user = User(
        username=username,
        name=username.capitalize(),
        email=f"{username}@example.com",
        password_hash=hash_password("password123"),
        premium=is_premium
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_auth_header(user: User):
    token = create_access_token({"sub": user.username})
    return {"Authorization": f"Bearer {token}"}

def test_premium_restriction(client: TestClient, session: Session):
    # Create a non-premium user
    non_prem_user = create_test_user(session, "regularjoey", is_premium=False)
    headers = get_auth_header(non_prem_user)

    # Try to access dashboard - should raise HTTP 403 Forbidden
    response = client.get("/athlete/dashboard", headers=headers)
    assert response.status_code == 403
    assert "Premium" in response.json()["detail"]

    # Try to post daily journal - should succeed (return 201), since only dashboard is restricted to premium
    journal_data = {
        "date": "2026-07-13",
        "sleep_hours": 7.5,
        "water_liters": 2.5,
        "stretched": True,
        "mobility": False,
        "trained_basketball": True,
        "gym": False,
        "cardio": False,
        "energy": 8,
        "muscle_pain": 3,
        "motivation": 9,
        "confidence": 8,
        "notes": "Good day"
    }
    response = client.post("/athlete/journal", json=journal_data, headers=headers)
    assert response.status_code == 201

def test_daily_journal_crud(client: TestClient, session: Session):
    # Create premium user
    prem_user = create_test_user(session, "premiumlebron", is_premium=True)
    headers = get_auth_header(prem_user)

    # 1. Post daily journal
    journal_data = {
        "date": "2026-07-13",
        "sleep_hours": 8.0,
        "water_liters": 3.2,
        "stretched": True,
        "mobility": True,
        "trained_basketball": True,
        "gym": True,
        "cardio": False,
        "energy": 9,
        "muscle_pain": 2,
        "motivation": 10,
        "confidence": 9,
        "notes": "Excellent performance today."
    }
    response = client.post("/athlete/journal", json=journal_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["sleep_hours"] == 8.0
    assert data["water_liters"] == 3.2
    assert data["notes"] == "Excellent performance today."

    # 2. Get daily journals
    response = client.get("/athlete/journal", headers=headers)
    assert response.status_code == 200
    journals = response.json()
    assert len(journals) == 1
    assert journals[0]["date"] == "2026-07-13"

def test_game_stats_crud(client: TestClient, session: Session):
    # Create premium user
    prem_user = create_test_user(session, "premiumsteph", is_premium=True)
    headers = get_auth_header(prem_user)

    # 1. Post game stats
    game_data = {
        "date": "2026-07-13",
        "opponent": "Lakers",
        "result": "Vitória",
        "points": 35,
        "ft_made": 5,
        "ft_attempted": 5,
        "fg2_made": 3,
        "fg2_attempted": 5,
        "fg3_made": 8,
        "fg3_attempted": 12,
        "assists": 8,
        "turnovers": 2,
        "offensive_rebounds": 1,
        "defensive_rebounds": 4,
        "steals": 2,
        "blocks": 0,
        "fouls_committed": 1,
        "fouls_drawn": 4
    }
    response = client.post("/athlete/game", json=game_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["opponent"] == "Lakers"
    assert data["points"] == 35

    # 2. Get game list
    response = client.get("/athlete/game", headers=headers)
    assert response.status_code == 200
    games = response.json()
    assert len(games) == 1
    assert games[0]["opponent"] == "Lakers"

    # 3. Delete game
    game_id = games[0]["id"]
    response = client.delete(f"/athlete/game/{game_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Partida removida com sucesso"

    # 4. Get game list again
    response = client.get("/athlete/game", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.skip(reason="Metas desabilitadas por enquanto")
def test_goals_crud(client: TestClient, session: Session):
    # Create premium user
    prem_user = create_test_user(session, "premiumkd", is_premium=True)
    headers = get_auth_header(prem_user)

    # 1. Post a goal
    goal_data = {
        "name": "Drink 3L water daily",
        "goal_type": "habit",
        "metric": "water_liters",
        "target_value": 3.0,
        "start_date": "2026-07-13",
        "end_date": "2026-08-13"
    }
    response = client.post("/athlete/goals", json=goal_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Drink 3L water daily"
    assert data["completed"] is False

    # 2. Get goals list
    response = client.get("/athlete/goals", headers=headers)
    assert response.status_code == 200
    goals = response.json()
    assert len(goals) == 1

    # 3. Toggle goal status
    goal_id = goals[0]["id"]
    response = client.patch(f"/athlete/goals/{goal_id}/toggle", headers=headers)
    assert response.status_code == 200
    assert response.json()["completed"] is True

    # 4. Toggle goal status back to False
    response = client.patch(f"/athlete/goals/{goal_id}/toggle", headers=headers)
    assert response.status_code == 200
    assert response.json()["completed"] is False

    # 5. Delete goal
    response = client.delete(f"/athlete/goals/{goal_id}", headers=headers)
    assert response.status_code == 200

    # 6. Check list again
    response = client.get("/athlete/goals", headers=headers)
    assert len(response.json()) == 0

def test_athlete_dashboard_aggregation(client: TestClient, session: Session):
    prem_user = create_test_user(session, "premiumgiannis", is_premium=True)
    headers = get_auth_header(prem_user)

    # Log some journals
    r1 = client.post("/athlete/journal", json={
        "date": "2026-07-12",
        "sleep_hours": 8.0,
        "water_liters": 3.0,
        "stretched": True,
        "mobility": True,
        "trained_basketball": True,
        "gym": False,
        "cardio": False,
        "energy": 8,
        "muscle_pain": 3,
        "motivation": 8,
        "confidence": 8,
        "notes": ""
    }, headers=headers)
    assert r1.status_code == 201

    r2 = client.post("/athlete/journal", json={
        "date": "2026-07-13",
        "sleep_hours": 7.0,
        "water_liters": 2.5,
        "stretched": False,
        "mobility": False,
        "trained_basketball": True,
        "gym": True,
        "cardio": False,
        "energy": 7,
        "muscle_pain": 5,
        "motivation": 7,
        "confidence": 7,
        "notes": ""
    }, headers=headers)
    assert r2.status_code == 201

    # Log game stats
    r3 = client.post("/athlete/game", json={
        "date": "2026-07-13",
        "opponent": "Bucks",
        "result": "Vitória",
        "points": 28,
        "ft_made": 8,
        "ft_attempted": 10,
        "fg2_made": 10,
        "fg2_attempted": 15,
        "fg3_made": 0,
        "fg3_attempted": 1,
        "assists": 6,
        "turnovers": 3,
        "offensive_rebounds": 3,
        "defensive_rebounds": 9,
        "steals": 1,
        "blocks": 2,
        "fouls_committed": 2,
        "fouls_drawn": 6
    }, headers=headers)
    assert r3.status_code == 201

    # Log a completed workout on the platform
    from models.users import WorkoutLog
    from datetime import datetime
    workout_log = WorkoutLog(
        user_id=prem_user.id,
        workout_id=999,
        completed_at=datetime.now()
    )
    session.add(workout_log)
    session.commit()

    # Get athlete dashboard
    response = client.get("/athlete/dashboard?days=30", headers=headers)
    assert response.status_code == 200
    data = response.json()



    # Verify consistency data
    assert data["consistency"]["streak"] == 2
    assert data["consistency"]["workouts_this_month"] == 1
    assert data["consistency"]["weekly_frequency"] == 2.0

    # Verify habits aggregation
    assert len(data["habits"]) == 2
    assert data["habits"][0]["sleep_hours"] == 8.0
    assert data["habits"][1]["water_liters"] == 2.5

    # Verify game stats aggregation
    assert len(data["game_stats"]) == 1
    assert data["game_stats"][0]["opponent"] == "Bucks"
    assert data["game_stats"][0]["points"] == 28
    assert data["game_stats"][0]["rebounds"] == 12
    assert data["game_stats"][0]["ft_pct"] == 80.0
    assert data["game_stats"][0]["fg3_pct"] == 0.0


def test_competition_crud_and_game_association(client: TestClient, session: Session):
    user = create_test_user(session, "competitoruser", is_premium=True)
    headers = get_auth_header(user)

    # 1. Create Competition
    comp_data = {
        "name": "Copa Metropolitana",
        "season": "2026"
    }
    response = client.post("/athlete/competitions", json=comp_data, headers=headers)
    assert response.status_code == 201
    comp = response.json()
    assert comp["name"] == "Copa Metropolitana"
    assert comp["season"] == "2026"
    assert comp["active"] is True

    # 2. List Competitions
    response = client.get("/athlete/competitions", headers=headers)
    assert response.status_code == 200
    competitions = response.json()
    assert len(competitions) == 1
    assert competitions[0]["name"] == "Copa Metropolitana"

    # 3. Create Game Stats with Competition ID and optional attempts (attempted = None)
    game_data = {
        "date": "2026-07-13",
        "opponent": "Nets",
        "result": "Vitória",
        "competition_id": comp["id"],
        "points": 20,
        "ft_made": 4,
        "ft_attempted": None,  # Opcional!
        "fg2_made": 5,
        "fg2_attempted": 8,
        "fg3_made": 2,
        "fg3_attempted": None,  # Opcional!
        "assists": 5,
        "turnovers": 1,
        "offensive_rebounds": 0,
        "defensive_rebounds": 3,
        "steals": 1,
        "blocks": 1,
        "fouls_committed": 2,
        "fouls_drawn": 3
    }
    response = client.post("/athlete/game", json=game_data, headers=headers)
    assert response.status_code == 201
    game = response.json()
    assert game["competition_id"] == comp["id"]
    assert game["ft_attempted"] is None
    assert game["fg3_attempted"] is None

    # Get games and assert competition info is returned
    response = client.get("/athlete/game", headers=headers)
    assert response.status_code == 200
    games = response.json()
    assert len(games) == 1
    assert games[0]["competition_id"] == comp["id"]

    # 4. Try to delete competition (should set active=False because it has a linked game)
    response = client.delete(f"/athlete/competitions/{comp['id']}", headers=headers)
    assert response.status_code == 200
    
    # Verify competition is now inactive
    response = client.get("/athlete/competitions", headers=headers)
    assert response.status_code == 200
    competitions = response.json()
    assert len(competitions) == 1
    assert competitions[0]["active"] is False

