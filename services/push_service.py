from pywebpush import webpush, WebPushException
import json
import logging
import os
from core.configs import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_CLAIM_EMAIL
from repositories.push_subscription_repository import PushSubscriptionRepository
from sqlmodel import Session

# Códigos HTTP que indicam que a assinatura foi revogada/expirada pelo browser
_EXPIRED_CODES = {404, 410}

def send_web_push(subscription_info: dict, message_body: str):
    """Envia uma notificação push. Retorna o status code HTTP ou None em caso de falha."""
    if os.getenv("MOCK_WEBPUSH") == "1":
        logging.info("MOCK_WEBPUSH=1 enabled — skipping real webpush call")
        return 200
    try:
        response = webpush(
            subscription_info=subscription_info,
            data=message_body,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{VAPID_CLAIM_EMAIL}"}
        )
        return response.status_code if hasattr(response, "status_code") else 201
    except WebPushException as ex:
        logging.warning(f"WebPushException ao enviar para {subscription_info.get('endpoint','?')[:60]}: {ex}")
        if ex.response is not None:
            return ex.response.status_code
        return None
    except (ValueError, Exception) as ex:
        logging.error(
            f"Erro irrecuperável ao enviar push para {subscription_info.get('endpoint','?')[:60]}: "
            f"{type(ex).__name__}: {ex}"
        )
        return None


class PushNotificationService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PushSubscriptionRepository(session)

    def _dispatch(self, subscriptions, payload: str) -> dict:
        """Envia para uma lista de assinaturas, removendo as inválidas. Retorna estatísticas."""
        stats = {"sent": 0, "failed": 0, "removed": 0}
        for sub in subscriptions:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            }
            try:
                status = send_web_push(sub_info, payload)
            except Exception as ex:
                logging.error(f"Exceção inesperada no dispatch: {ex}")
                status = None

            if status in _EXPIRED_CODES or status is None:
                self.repo.delete_subscription_by_endpoint(sub.endpoint)
                stats["removed"] += 1
                stats["failed"] += 1
            else:
                stats["sent"] += 1

        return stats

    def send_to_user(self, user_id: int, title: str, body: str):
        subscriptions = self.repo.get_subscriptions_by_user(user_id)
        payload = json.dumps({"title": title, "body": body})
        stats = self._dispatch(subscriptions, payload)
        logging.info(f"send_to_user uid={user_id}: {stats}")

    def send_to_all(self, title: str, body: str):
        subscriptions = self.repo.get_all_subscriptions()
        payload = json.dumps({"title": title, "body": body})
        stats = self._dispatch(subscriptions, payload)
        logging.info(f"send_to_all: {stats}")
