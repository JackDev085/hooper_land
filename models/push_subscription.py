from sqlmodel import SQLModel, Field

class PushSubscriptions(SQLModel, table=True):
    __tablename__ = "push_subscriptions"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    endpoint: str = Field(unique=True, index=True)
    p256dh: str
    auth: str
