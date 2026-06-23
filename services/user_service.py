from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime
from models.users import User
from schemas.users import UserCreate, UserUpdate, UserAdminUpdate
from repositories.user_repository import UserRepository
from core.security import verify_user, hash_password, pwd_context, create_access_token
import logging

class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)

    def login_for_access_token(self, form_data) -> dict:
        user_in_db = self.user_repository.get_user_by_username(form_data.username)
        
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos!")
        if not pwd_context.verify(form_data.password, user_in_db.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos!")

        # Gerar o token JWT
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}

    def register_user(self, user_create: UserCreate) -> User:
        verify_user(user_create, self.session)
        
        new_user = User(
            id=None,
            username=user_create.username,
            name=user_create.name,
            email=user_create.email,
            created_at=str(datetime.now()),
            updated_at=str(datetime.now()),
            password_hash=hash_password(user_create.password)
        )
        
        try:
            return self.user_repository.create_user(new_user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro na criação de usuário"
            ) from e

    def register_all_users(self, users: list[UserCreate]) -> list[User]:
        created_users = []
        for user in users:
            new_user = self.register_user(user)
            created_users.append(new_user)
        return created_users

    def update_my_profile(self, current_user: User, user_update: UserUpdate) -> User:
        try:
            return self.user_repository.update_user(current_user, user_update)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar informações do usuário"
            ) from e

    def search_username_by_email(self, email: str) -> User:
        user_in_db = self.user_repository.get_user_by_email(email)
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return user_in_db

    def get_users_ranking(self, limit: int = 10) -> list[User]:
        return self.user_repository.get_ranking(limit)

    def list_all_users(self) -> list[User]:
        return self.user_repository.get_all_users()

    def admin_update_user(self, username: str, user_admin_update: UserAdminUpdate) -> User:
        user_in_db = self.user_repository.get_user_by_username(username)
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
        if user_admin_update.premium is not None:
            user_in_db.premium = user_admin_update.premium
        if user_admin_update.role is not None:
            if user_admin_update.role not in ["user", "admin"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role inválida. Escolha entre 'user' e 'admin'")
            user_in_db.role = user_admin_update.role
            
        user_in_db.updated_at = str(datetime.now())
        try:
            return self.user_repository.save(user_in_db)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar informações do usuário pelo administrador"
            ) from e
