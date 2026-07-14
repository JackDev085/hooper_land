from fastapi import APIRouter, status, HTTPException, Depends
from models.users import User
from core.security import get_current_user, require_admin
from repositories.dash_repository import DashRepository
from sqlmodel import Session
from core.database import get_session

router = APIRouter(tags=["dashboard"])

@router.get("/dash")
async def get_one_dash(username: str, months: int | None = 1, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    repo_dash_repository = DashRepository(session)
    data = repo_dash_repository.one_dash_by_User(username, months=months)
    return data

@router.get("/evaluations", status_code=status.HTTP_200_OK)
async def get_reviews(current_user: User = Depends(require_admin), session: Session = Depends(get_session)):
    repo_dash_repository = DashRepository(session)
    avaliacao_return = repo_dash_repository.get_all()
    return avaliacao_return
