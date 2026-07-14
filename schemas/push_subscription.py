from pydantic import BaseModel

class PushKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: PushKeys

class PushNotificationSend(BaseModel):
    title: str
    body: str
    target_username: str | None = None  # None means send to all users
