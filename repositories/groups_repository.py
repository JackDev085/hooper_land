from fastapi import HTTPException, status
from sqlmodel import Session, select
from models.groups import Groups, GroupsAndUsers
from models.users import User
from schemas.groups import GroupCreate, GroupUpdate
from .user_repository import UserRepository
from schemas.users import UserSimple

class GroupsRepository:
    def __init__(self, session: Session):
        self.session = session

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, session):
        if not isinstance(session, Session):
            raise TypeError("Session deve ser do tipo Session(sqlmodel)")
        self.__session = session

    # --------- CRUD de Groups ---------

    def create_group(self, payload: GroupCreate) -> Groups:
        exist = self.session.exec(
            select(Groups).where(Groups.name == payload.name)
        ).first()
        if exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um grupo com esse nome"
            )

        group_db = Groups(name=payload.name)
        self.session.add(group_db)
        self.session.commit()
        self.session.refresh(group_db)
        return group_db

    def list_groups(self, skip: int = 0, limit: int = 50) -> list[Groups]:
        groups = self.session.exec(
            select(Groups).offset(skip).limit(limit).order_by(Groups.id.desc())
        ).all()
        return groups

    def get_group(self, group_id: int) -> Groups:
        group = self.session.get(Groups, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado"
            )
        return group

    def update_group(self, group_id: int, payload: GroupUpdate) -> Groups:
        group = self.get_group(group_id)

        if payload.name is not None:
            exist = self.session.exec(
                select(Groups).where(Groups.name == payload.name, Groups.id != group_id)
            ).first()
            if exist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um grupo com esse nome"
                )
            group.name = payload.name

        self.session.add(group)
        self.session.commit()
        self.session.refresh(group)
        return group

    def delete_group(self, group_id: int) -> bool:
        group = self.get_group(group_id)

        links = self.session.exec(
            select(GroupsAndUsers).where(GroupsAndUsers.group_id == group_id)
        ).all()
        for link in links:
            self.session.delete(link)

        self.session.delete(group)
        self.session.commit()
        return True

    # --------- Membros do grupo ---------

    def add_member(self, group_id: int, user_id: int) -> bool:
        group = self.get_group(group_id)

        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        exist_link = self.session.exec(
            select(GroupsAndUsers).where(
                GroupsAndUsers.group_id == group.id,
                GroupsAndUsers.user_id == user.id
            )
        ).first()
        if exist_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já está no grupo"
            )

        link = GroupsAndUsers(group_id=group.id, user_id=user.id)
        self.session.add(link)
        self.session.commit()
        return True

    def remove_member(self, group_id: int, user_id: int) -> bool:
        self.get_group(group_id)

        link = self.session.exec(
            select(GroupsAndUsers).where(
                GroupsAndUsers.group_id == group_id,
                GroupsAndUsers.user_id == user_id
            )
        ).first()

        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não está nesse grupo"
            )

        self.session.delete(link)
        self.session.commit()
        return True
    
    def get_group_members(self, group_id: int):
        users_repository = UserRepository(self.session)
        group = self.session.get(Groups, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado"
            )
            
        members = group.members
        users = []
        
        for member in members:
            users.append(UserSimple(**users_repository.get_user_by_id(member.user_id).model_dump()))
        if not members:
            return []
        return users
