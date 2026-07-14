from sqlmodel import Session, select
from models.push_subscription import PushSubscriptions

class PushSubscriptionRepository:
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
        
    def add_subscription(self, user_id: int, endpoint: str, p256dh: str, auth: str):
        existing = self.session.exec(
            select(PushSubscriptions).where(PushSubscriptions.endpoint == endpoint)
        ).first()
        
        if existing:
            existing.user_id = user_id
            existing.p256dh = p256dh
            existing.auth = auth
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing
            
        new_sub = PushSubscriptions(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth
        )
        self.session.add(new_sub)
        self.session.commit()
        self.session.refresh(new_sub)
        return new_sub
        
    def get_subscriptions_by_user(self, user_id: int):
        return self.session.exec(
            select(PushSubscriptions).where(PushSubscriptions.user_id == user_id)
        ).all()
        
    def get_all_subscriptions(self):
        return self.session.exec(select(PushSubscriptions)).all()
        
    def delete_subscription_by_endpoint(self, endpoint: str):
        existing = self.session.exec(
            select(PushSubscriptions).where(PushSubscriptions.endpoint == endpoint)
        ).first()
        if existing:
            self.session.delete(existing)
            self.session.commit()
            return True
        return False
