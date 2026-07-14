
"""Users"""
from sqlmodel import SQLModel

class Token(SQLModel):
    """Classe modelo para token de autenticação"""
    access_token: str
    token_type: str
    

class TokenData(SQLModel):
    """Modelo para token com usuário"""
    username: str | None = None

    
class UserGetToken(SQLModel):
    """Modelo para autenticação de usuário que acessa uma rota"""
    username: str
    password: str


class UserInDB(SQLModel):
    """Modelo para usuário no banco de dados"""
    hashed_password: str
    

class UserBase(SQLModel):
    username: str


class UserCreate(UserBase):
    email: str | None = None
    name: str
    password: str

class UserLogin(UserBase):
    password: str

class UserUsername(SQLModel):
    username: str | None = None

class UserPublic(SQLModel):
    """Dados públicos do usuário (sem senha/hash)"""
    username: str
    name: str
    email: str
    role: str = "user"
    instagram: str | None = None
    description: str | None = None
    premium: bool = False
    streak_count: int = 0
    last_workout_at: str | None = None
    sex: str | None = None
    position: str | None = None
    birth_date: str | None = None
    phone: str | None = None
    weigth: float | None = None
    heigth: float | None = None

class UserSimple(SQLModel):
    """Dados simples de outros usuários (sem informações pessoais sensíveis como email, telefone, peso, altura)"""
    username: str
    name: str
    role: str = "user"
    instagram: str | None = None
    description: str | None = None
    premium: bool = False
    streak_count: int = 0
    last_workout_at: str | None = None
    sex: str | None = None
    position: str | None = None

class UserRanking(SQLModel):
    """Dados mínimos para ranking público (sem dados pessoais sensíveis)"""
    username: str
    name: str
    streak_count: int = 0

class UserUpdate(SQLModel):
    """Modelo para atualizar informações do usuário"""
    name: str | None = None
    description: str | None = None
    instagram: str | None = None
    sex: str | None = None
    position: str | None = None
    birth_date: str | None = None
    phone: str | None = None
    weigth: float | None = None
    heigth: float | None = None

class UserAdminUpdate(SQLModel):
    """Modelo para atualizar informações administrativas do usuário pelo admin"""
    premium: bool | None = None
    role: str | None = None