from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from core.database import get_session
from core.security import require_admin
from models.users import User

from repositories.groups_repository import GroupsRepository
from repositories.dash_repository import DashRepository
from schemas.users import UserSimple
from schemas.groups import (
    GroupCreate, GroupUpdate, GroupRead,
    GroupMemberAdd, GroupMemberRemove, GroupAndUsersRead
)

router = APIRouter(prefix="/groups", tags=["Groups"])

# --------- CRUD ---------

@router.post("/create", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    return repo.create_group(payload)


@router.get("/", response_model=list[GroupRead], status_code=status.HTTP_200_OK)
async def list_groups(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    return repo.list_groups(skip=skip, limit=limit)


@router.get("/{group_id}", status_code=status.HTTP_200_OK)
async def get_group(
    group_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    group = repo.get_group(group_id)
    users = repo.get_group_members(group_id)
    
    return {"group": group, "users": users}


@router.put("/update/{group_id}", response_model=GroupRead, status_code=status.HTTP_200_OK)
async def update_group(
    group_id: int,
    payload: GroupUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    return repo.update_group(group_id, payload)


@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
async def delete_group(
    group_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    repo.delete_group(group_id)
    return {"detail": "Grupo deletado com sucesso"}


# --------- membros ---------

@router.post("/{group_id}/members/add", status_code=status.HTTP_201_CREATED)
async def add_member(
    group_id: int,
    payload: GroupMemberAdd,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    repo.add_member(group_id=group_id, user_id=payload.user_id)
    return {"detail": "Atleta adicionado ao grupo com sucesso"}


@router.post("/{group_id}/members/remove", status_code=status.HTTP_200_OK)
async def remove_member(
    group_id: int,
    payload: GroupMemberRemove,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    repo = GroupsRepository(session)
    repo.remove_member(group_id=group_id, user_id=payload.user_id)
    return {"detail": "Atleta removido do grupo com sucesso"}


@router.get("/{group_id}/evaluations", status_code=status.HTTP_200_OK)
async def get_reviews(
    group_id: int,
    months: int | None = 1,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    repo_dash_repository = DashRepository(session)
    avaliacao_return = repo_dash_repository.get_evaluation_by_group(group_id, months=months)
    return avaliacao_return


@router.get("/{group_id}/users", response_model=list[UserSimple], status_code=status.HTTP_200_OK)
async def get_group_users(
    group_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    groups_repository = GroupsRepository(session)
    users = groups_repository.get_group_members(group_id)
    return users


@router.get("/{group_id}/today-status", status_code=status.HTTP_200_OK)
async def get_today_status(
    group_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    from datetime import datetime
    import pytz
    from repositories.user_repository import UserRepository
    
    groups_repository = GroupsRepository(session)
    group = groups_repository.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
        
    members = group.members
    if not members:
        return {"submitted": [], "not_submitted": []}

    fuse_ce = pytz.timezone('America/Fortaleza')
    date_today = datetime.now(fuse_ce).strftime("%d/%m/%Y")

    submitted_users = []
    not_submitted_users = []

    user_repository = UserRepository(session)
    for member in members:
        user = user_repository.get_user_by_id(member.user_id)
        if not user:
            continue
        
        today_reviews = [r for r in (user.reviews or []) if r.send_date == date_today]
        
        pre_submitted = any(r.type == "pre" for r in today_reviews)
        pos_submitted = any(r.type == "pos" for r in today_reviews)

        user_info = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "position": user.position,
            "pre_submitted": pre_submitted,
            "pos_submitted": pos_submitted
        }

        if pre_submitted or pos_submitted:
            submitted_users.append(user_info)
        else:
            not_submitted_users.append(user_info)

    return {
        "submitted": submitted_users,
        "not_submitted": not_submitted_users
    }
