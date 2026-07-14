from sqlmodel import Session, select
from repositories.user_repository import UserRepository
from models.users import User
from schemas.review import ReviewsReturnPos, ReviewsReturnPre
from fastapi import HTTPException, status
from repositories.groups_repository import GroupsRepository
from collections import Counter

class DashRepository:
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
        
    def one_dash_by_User(self, username: str, months: int | None = 1):
        user = self.session.exec(select(User).where(User.username == username)).first()
        if not user:
            self.not_found()
            
        data = user.reviews
        if not data:
            return []

        from datetime import datetime, timedelta
        cutoff_date = None
        if months is not None and months > 0:
            cutoff_date = datetime.now() - timedelta(days=30 * months)

        pre = []
        pos = []

        for i in data:
            if cutoff_date:
                try:
                    review_date = datetime.strptime(i.send_date, "%d/%m/%Y")
                    if review_date < cutoff_date:
                        continue
                except ValueError:
                    pass

            if i.type == "pre":
                pre.append(ReviewsReturnPre(**i.model_dump()))
            else:
                pos.append(ReviewsReturnPos(**i.model_dump()))
        return [pre, pos]
    
    def get_all(self):
        users_repository = UserRepository(self.session)
        users = users_repository.get_all_users()
        return self._process_users_data(users)
    
    def get_evaluation_by_group(self, group_id, months: int | None = 1):
        groups_repository = GroupsRepository(self.session)
        group = groups_repository.get_group(group_id)
        if not group:
            self.not_found()
            
        users_repository = UserRepository(self.session)
        members = group.members
        if not members:
            return []
            
        users = []
        for member in members:
            users.append(users_repository.get_user_by_id(member.user_id))
            
        return self._process_users_data(users, months=months)

    def _process_users_data(self, users, months: int | None = 1):
        from datetime import datetime, timedelta
        return_data = []

        cutoff_date = None
        if months is not None and months > 0:
            cutoff_date = datetime.now() - timedelta(days=30 * months)

        for user in users:
            if not user or getattr(user, "reviews", None) is None:
                continue
            
            pre = []
            pos = []

            for i in user.reviews:
                if cutoff_date:
                    try:
                        review_date = datetime.strptime(i.send_date, "%d/%m/%Y")
                        if review_date < cutoff_date:
                            continue
                    except ValueError:
                        pass

                if getattr(i, "type", None) == "pre":
                    pre.append(ReviewsReturnPre(**i.model_dump()))
                else:
                    pos.append(ReviewsReturnPos(**i.model_dump()))
            
            if not pre and not pos:
                continue
            
            pain = sum(t.pain for t in pre) / len(pre) if pre else 0
            
            sleep_items = [t.sleep for t in pre if getattr(t, 'sleep', None)]
            sleep = sum(sleep_items) / len(sleep_items) if sleep_items else 0
            
            food_items = [t.food for t in pre if getattr(t, 'food', None)]
            food = sum(food_items) / len(food_items) if food_items else 0
            
            pain_pos = sum(t.pain for t in pos) / len(pos) if pos else 0
            fadigue = sum(t.fadigue for t in pos) / len(pos) if pos else 0
            effort = sum(t.effort for t in pos) / len(pos) if pos else 0
            
            list_muscles = {}
            for i in pos:
                if i.severe_pain is not None and i.severe_pain != "":
                    if i.severe_pain not in list_muscles:
                        list_muscles[i.severe_pain] = 1
                    else:
                        list_muscles[i.severe_pain] += 1
                         
            return_data.append({
                "username": user.username,
                "pre": {
                    "pain": round(pain, 2),
                    "sleep": round(sleep, 2),
                    "food": round(food, 2)
                },
                "pos": {
                    "pain_pos": round(pain_pos, 2),
                    "fadigue": round(fadigue, 2),
                    "effort": round(effort, 2)
                },
                "muscle_in_risk": list_muscles
            })
            
        return return_data
    
    def not_found(self):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupo ou Usuário não encontrado")
