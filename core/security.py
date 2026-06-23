from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic.types import Annotated
from models.users import User
from schemas.users import UserCreate, TokenData
from core.configs import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import re
import logging
from core.database import get_session
from sqlmodel import Session, select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],session: Session= Depends(get_session)):
    logging.info(f"Token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == token_data.username)).first()
    if user is None:
        raise credentials_exception
    return user

# funcao para saber se o usuario esta ativo
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

# dependency para verificar se o usuário é admin
async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user

# função para criar o token de acesso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Função de hash da senha
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_user(user:UserCreate,session: Session)->bool:
    user.username = user.username.lower()

    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    existing_email = session.exec(select(User).where(User.email == user.email)).first()
    pattern_email = r"[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    pattern_password = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#.])[A-Za-z\d@$!%#.*?&]{8,}$"
    existing_blank_spaces = False
    if " " in user.username:
        existing_blank_spaces = True

    if existing_blank_spaces:
        raise HTTPException(status_code=400, detail="Camnpo usuário não pode ter espaços em branco")
    if existing_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado")
    if existing_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    if not re.match(pattern_email, user.email):
        raise HTTPException(status_code=400, detail="Email inválido")
    if not re.match(pattern_password, user.password):
        raise HTTPException(status_code=400, detail="Senha fora do padrão")
    print("Usuario validade")
    return True
    