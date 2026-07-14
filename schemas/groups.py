from sqlmodel import SQLModel, Field
from typing import Optional
from models.groups import GroupsAndUsers

class GroupCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)

class GroupUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)

class GroupRead(SQLModel):
    id: int
    name: str

class GroupAndUsersRead(SQLModel):
    id: int
    name: str
    members: list[GroupsAndUsers]
    
class GroupMemberAdd(SQLModel):
    user_id: int

class GroupMemberRemove(SQLModel):
    user_id: int
