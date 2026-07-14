from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from models.users import User
from schemas.users import UserCreate, UserPublic, UserUsername, UserUpdate, UserAdminUpdate, UserRanking, UserSimple
from core.security import get_current_user, require_admin
from core.database import get_session
from sqlmodel import Session
from services.user_service import UserService
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Auth"])

# Rota de login — máximo 5 tentativas por minuto por IP
@router.post("/token")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user_service = UserService(session)
    return user_service.login_for_access_token(form_data)

# Rota de registro — máximo 3 por minuto por IP
@router.post("/register", response_model=UserPublic)
@limiter.limit("3/minute")
async def register_user(request: Request, user: UserCreate, session: Session = Depends(get_session)):
    user_service = UserService(session)
    new_user = user_service.register_user(user)
    return new_user

@router.post("/register_all_users", response_model=list[UserPublic])
async def register_all_users(users: list[UserCreate], admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    user_service = UserService(session)
    return user_service.register_all_users(users)
        
@router.post("/verify_token")
def verify_token(current_user: User = Depends(get_current_user)):
    return {"message": "Token is valid"}

@router.get("/me", response_model=UserPublic)
def about_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserPublic)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user_service = UserService(session)
    updated_user = user_service.update_my_profile(current_user, user_update)
    return updated_user

@router.get("/user_by_email/{email}", response_model=UserUsername)
def search_username_by_email(email: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    user_service = UserService(session)
    user_in_db = user_service.search_username_by_email(email)
    return user_in_db

@router.get("/ranking", response_model=list[UserRanking])
async def get_users_ranking(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user_service = UserService(session)
    return user_service.get_users_ranking(limit)

@router.get("/users", response_model=list[UserSimple])
async def list_all_users(
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    user_service = UserService(session)
    return user_service.list_all_users()

@router.put("/users/{username}/admin-update", response_model=UserPublic)
async def admin_update_user(
    username: str,
    user_admin_update: UserAdminUpdate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    user_service = UserService(session)
    return user_service.admin_update_user(username, user_admin_update)