from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from core.database import get_session
from core.security import get_current_user, require_admin
from models.users import User
from schemas.push_subscription import PushSubscriptionCreate, PushNotificationSend
from repositories.push_subscription_repository import PushSubscriptionRepository
from repositories.user_repository import UserRepository
from services.push_service import PushNotificationService
from core.configs import VAPID_PUBLIC_KEY

router = APIRouter(tags=["Notifications"])

@router.get("/notifications/vapid-public-key")
def get_vapid_public_key():
    return {"public_key": VAPID_PUBLIC_KEY}

@router.post("/notifications/subscribe")
def subscribe(
    subscription: PushSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = PushSubscriptionRepository(session)
    repo.add_subscription(
        user_id=current_user.id,
        endpoint=subscription.endpoint,
        p256dh=subscription.keys.p256dh,
        auth=subscription.keys.auth
    )
    return {"message": "Inscrição realizada com sucesso"}

@router.post("/notifications/send")
def send_notification(
    notification: PushNotificationSend,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    push_service = PushNotificationService(session)
    if notification.target_username:
        user_repo = UserRepository(session)
        target_user = user_repo.get_user_by_username(notification.target_username.lower())
        if not target_user:
            raise HTTPException(status_code=404, detail="Usuário alvo não encontrado")
        push_service.send_to_user(target_user.id, notification.title, notification.body)
        return {"message": f"Notificação enviada para @{notification.target_username}"}
    else:
        push_service.send_to_all(notification.title, notification.body)
        return {"message": "Notificação enviada para todos os usuários"}
