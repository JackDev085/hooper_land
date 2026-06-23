import pytest
from fastapi import HTTPException
from sqlmodel import Session, select
from schemas.users import UserCreate, UserUpdate, UserAdminUpdate
from services.user_service import UserService
from models.users import User
from core.security import pwd_context

class MockFormData:
    def __init__(self, username, password):
        self.username = username
        self.password = password

def test_register_user_success(session: Session):
    user_service = UserService(session)
    user_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        name="Test User",
        password="Password123."
    )
    
    new_user = user_service.register_user(user_data)
    assert new_user.username == "testuser"
    assert new_user.name == "Test User"
    assert new_user.email == "testuser@example.com"
    
    # Verify in DB
    db_user = session.exec(select(User).where(User.username == "testuser")).first()
    assert db_user is not None
    assert pwd_context.verify("Password123.", db_user.password_hash)

def test_register_user_duplicate_username(session: Session):
    user_service = UserService(session)
    user_data = UserCreate(
        username="testuser",
        email="testuser1@example.com",
        name="Test User",
        password="Password123."
    )
    user_service.register_user(user_data)
    
    # Try again with same username but different email
    user_data2 = UserCreate(
        username="testuser",
        email="testuser2@example.com",
        name="Test User 2",
        password="Password123."
    )
    
    with pytest.raises(HTTPException) as excinfo:
        user_service.register_user(user_data2)
    assert excinfo.value.status_code == 400
    assert "Nome de usuário já cadastrado" in excinfo.value.detail

def test_login_success(session: Session):
    user_service = UserService(session)
    user_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        name="Test User",
        password="Password123."
    )
    user_service.register_user(user_data)
    
    form_data = MockFormData(username="testuser", password="Password123.")
    response = user_service.login_for_access_token(form_data)
    
    assert "access_token" in response
    assert response["token_type"] == "bearer"

def test_login_invalid_password(session: Session):
    user_service = UserService(session)
    user_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        name="Test User",
        password="Password123."
    )
    user_service.register_user(user_data)
    
    form_data = MockFormData(username="testuser", password="WrongPassword!")
    with pytest.raises(HTTPException) as excinfo:
        user_service.login_for_access_token(form_data)
    assert excinfo.value.status_code == 401
    assert "Usuário ou senha incorretos" in excinfo.value.detail

def test_update_profile(session: Session):
    user_service = UserService(session)
    user_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        name="Original Name",
        password="Password123."
    )
    user_service.register_user(user_data)
    
    db_user = session.exec(select(User).where(User.username == "testuser")).first()
    update_data = UserUpdate(
        name="Updated Name",
        instagram="updated_insta",
        description="Updated Description"
    )
    
    updated_user = user_service.update_my_profile(db_user, update_data)
    assert updated_user.name == "Updated Name"
    assert updated_user.instagram == "updated_insta"
    assert updated_user.description == "Updated Description"

def test_admin_update_user(session: Session):
    user_service = UserService(session)
    user_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        name="Test User",
        password="Password123."
    )
    user_service.register_user(user_data)
    
    admin_update = UserAdminUpdate(
        premium=True,
        role="admin"
    )
    
    updated_user = user_service.admin_update_user("testuser", admin_update)
    assert updated_user.premium is True
    assert updated_user.role == "admin"
