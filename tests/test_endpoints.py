import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models.users import User
from core.security import hash_password

def test_register_and_login_flow(client: TestClient):
    # 1. Register a user
    register_payload = {
        "username": "endpointuser",
        "email": "endpointuser@example.com",
        "name": "Endpoint User",
        "password": "Password123."
    }
    response = client.post("/register", json=register_payload)
    assert response.status_code == 200
    
    # 2. Login to get token
    login_data = {
        "username": "endpointuser",
        "password": "Password123."
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token_json = response.json()
    assert "access_token" in token_json
    token = token_json["access_token"]
    
    # 3. Get profile
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile["username"] == "endpointuser"
    assert profile["email"] == "endpointuser@example.com"

def test_workouts_endpoint_permissions(client: TestClient, session: Session):
    # 1. Register regular user and admin user in DB
    regular_user = User(
        username="reguser",
        email="reguser@example.com",
        name="Regular User",
        password_hash=hash_password("Password123."),
        role="user"
    )
    admin_user = User(
        username="adminuser",
        email="adminuser@example.com",
        name="Admin User",
        password_hash=hash_password("Password123."),
        role="admin"
    )
    session.add(regular_user)
    session.add(admin_user)
    session.commit()
    
    # 2. Get token for regular user
    login_regular = client.post("/token", data={"username": "reguser", "password": "Password123."})
    assert login_regular.status_code == 200
    reg_token = login_regular.json()["access_token"]
    
    # 3. Get token for admin user
    login_admin = client.post("/token", data={"username": "adminuser", "password": "Password123."})
    assert login_admin.status_code == 200
    admin_token = login_admin.json()["access_token"]
    
    # 4. Attempt to create workout as regular user (should be 403 Forbidden)
    workout_payload = {
        "name": "Treino Pro",
        "desc": "Treino Avançado",
        "duration": "90 min",
        "category": "Hipertrofia",
        "premium": True
    }
    headers_reg = {"Authorization": f"Bearer {reg_token}"}
    response = client.post("/workouts/", json=workout_payload, headers=headers_reg)
    assert response.status_code == 403
    
    # 5. Create workout as admin (should be 200 or 201)
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/workouts/", json=workout_payload, headers=headers_admin)
    assert response.status_code in [200, 201]
    
    # 6. List workouts as regular user (should be successful)
    response = client.get("/workouts/", headers=headers_reg)
    assert response.status_code == 200
    workouts = response.json()
    assert len(workouts) == 1
    assert workouts[0]["name"] == "Treino Pro"
