from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.users import User

class Groups(SQLModel, table=True):
    __tablename__ = "groups"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)

    members: List["GroupsAndUsers"] = Relationship(back_populates="group")


class GroupsAndUsers(SQLModel, table=True):
    __tablename__ = "groupsandusers"

    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id", index=True)
    group_id: int = Field(foreign_key="groups.id", index=True)

    group: Optional[Groups] = Relationship(back_populates="members")
    users: Optional[User] = Relationship(back_populates="groups")
